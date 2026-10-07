"""Read snapshot OSM PBF nodes/ways using the published OSM-binary wire schema.

Unknown required features and unsupported compression fail explicitly. Relations
remain in the immutable raw PBF. No native reader or global worker pool is needed.
Reference: https://github.com/openstreetmap/OSM-binary/tree/master/osmpbf
"""

import struct
import zlib
from datetime import UTC, datetime
from pathlib import Path


def varint(data, position=0):
    value = 0
    for shift in range(0, 70, 7):
        if position >= len(data):
            raise ValueError("truncated protobuf varint")
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            if value >= 1 << 64:
                raise ValueError("protobuf varint exceeds uint64")
            return value, position
    raise ValueError("overlong protobuf varint")


def fields(data):
    position = 0
    while position < len(data):
        tag, position = varint(data, position)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError("protobuf field number zero")
        if wire == 0:
            value, position = varint(data, position)
        elif wire == 2:
            size, position = varint(data, position)
            end = position + size
            if end > len(data):
                raise ValueError("truncated protobuf byte field")
            value = data[position:end]
            position = end
        elif wire in (1, 5):
            end = position + (8 if wire == 1 else 4)
            if end > len(data):
                raise ValueError("truncated fixed-width protobuf field")
            value = data[position:end]
            position = end
        else:
            raise ValueError("unsupported protobuf wire type")
        yield number, wire, value


def zigzag(number):
    return (number >> 1) ^ -(number & 1)


def signed(number):
    return number if number < 1 << 63 else number - (1 << 64)


def packed(data, delta=False):
    position, total = 0, 0
    while position < len(data):
        value, position = varint(data, position)
        if delta:
            total += zigzag(value)
            yield total
        else:
            yield value


def one(message, number, default=None):
    values = [value for field, wire, value in fields(message) if field == number]
    if len(values) > 1:
        raise ValueError("duplicate singular protobuf field")
    return values[0] if values else default


def repeated(message, number):
    values = []
    for field, wire, value in fields(message):
        if field == number:
            values.extend(packed(value) if wire == 2 else [value])
    return values


def deltas(message, number):
    total, values = 0, []
    for raw in repeated(message, number):
        total += zigzag(raw)
        values.append(total)
    return values


def read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("truncated PBF block")
    return data


def blocks(path: Path):
    with path.open("rb") as stream:
        while prefix := stream.read(4):
            if len(prefix) != 4:
                raise ValueError("truncated PBF block header length")
            header_size = struct.unpack(">I", prefix)[0]
            if not 0 < header_size <= 64 * 1024:
                raise ValueError("invalid PBF header size")
            header = read_exact(stream, header_size)
            kind, size = one(header, 1), one(header, 3)
            if kind not in (b"OSMHeader", b"OSMData") or not size or size > 64 * 1024 * 1024:
                raise ValueError("unsupported PBF block type/size")
            blob = read_exact(stream, size)
            raw, compressed, expected_size = one(blob, 1), one(blob, 3), one(blob, 2)
            if any(number in (4, 5, 6, 7) for number, wire, value in fields(blob)):
                raise ValueError("unsupported PBF compression")
            if (raw is None) == (compressed is None):
                raise ValueError("PBF blob must have one supported payload")
            if raw is None:
                if expected_size is None or not 0 < expected_size <= 64 * 1024 * 1024:
                    raise ValueError("invalid PBF uncompressed size")
                decoder = zlib.decompressobj()
                raw = decoder.decompress(compressed, expected_size + 1)
                if len(raw) != expected_size or not decoder.eof or decoder.unused_data:
                    raise ValueError("PBF decompression size/stream mismatch")
            yield kind, raw


def header_timestamp(message):
    required = [value.decode() for number, wire, value in fields(message) if number == 4]
    if set(required) - {"OsmSchema-V0.6", "DenseNodes"}:
        raise ValueError(f"unsupported PBF required features: {required}")
    if "OsmSchema-V0.6" not in required:
        raise ValueError("PBF lacks supported schema declaration")
    timestamp = one(message, 32)
    return (
        datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z")
        if timestamp is not None
        else "not_reported"
    )


def primitive_groups(message):
    strings_blob = one(message, 1)
    if strings_blob is None:
        raise ValueError("PBF lacks string table")
    strings = [value.decode("utf-8") for number, wire, value in fields(strings_blob) if number == 1]
    if not strings or strings[0] != "":
        raise ValueError("invalid PBF string table")
    granularity = one(message, 17, 100)
    lat_offset, lon_offset = signed(one(message, 19, 0)), signed(one(message, 20, 0))
    if granularity <= 0:
        raise ValueError("invalid PBF coordinate granularity")
    for number, _wire, group in fields(message):
        if number == 2:
            yield group, strings, granularity, lat_offset, lon_offset


def nodes(group, granularity, lat_offset, lon_offset):
    for number, _wire, message in fields(group):
        if number == 1:
            identity, lat, lon = (one(message, field) for field in (1, 8, 9))
            if identity is None or lat is None or lon is None:
                raise ValueError("PBF node lacks required fields")
            yield (
                zigzag(identity),
                lon_offset + granularity * zigzag(lon),
                lat_offset + granularity * zigzag(lat),
            )
        elif number == 2:
            arrays = [deltas(message, field) for field in (1, 8, 9)]
            if not len(arrays[0]) == len(arrays[1]) == len(arrays[2]):
                raise ValueError("PBF dense node array lengths differ")
            for identity, lat, lon in zip(*arrays, strict=True):
                yield identity, lon_offset + granularity * lon, lat_offset + granularity * lat


def ways(group, strings):
    for number, _wire, message in fields(group):
        if number != 3:
            continue
        keys, values = repeated(message, 2), repeated(message, 3)
        if len(keys) != len(values):
            raise ValueError("PBF way tag arrays differ")
        try:
            tags = {strings[key]: strings[value] for key, value in zip(keys, values, strict=True)}
        except IndexError as error:
            raise ValueError("PBF way string-table reference invalid") from error
        if len(tags) != len(keys):
            raise ValueError("PBF way repeats a tag key")
        if "highway" not in tags:
            continue
        identity, info = one(message, 1), one(message, 4)
        version = one(info, 1) if info is not None else None
        if identity is None or identity <= 0 or version is None or version <= 0:
            raise ValueError("road way lacks positive ID/version")
        refs = deltas(message, 8)
        yield identity, version, refs, tags
