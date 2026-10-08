"""Region-independent metre projections with declared areas of use."""

from math import isfinite

from pyproj import CRS, Transformer


def metric_projection(crs: str) -> CRS:
    parsed = CRS.from_user_input(crs)
    if not parsed.is_projected or len(parsed.axis_info) != 2:
        raise ValueError("distance calculations require a projected two-dimensional CRS")
    if any(axis.unit_name != "metre" for axis in parsed.axis_info):
        raise ValueError("metric CRS axes must be metres")
    if parsed.area_of_use is None:
        raise ValueError("metric CRS must declare an area of use")
    if parsed.to_epsg() == 3857:
        raise ValueError("Web Mercator is a display CRS; select a local metric analysis CRS")
    return parsed


def projection(crs: str) -> Transformer:
    return Transformer.from_crs(4326, metric_projection(crs), always_xy=True, allow_ballpark=False)


def inside_area(longitude, latitude, area):
    if not isfinite(longitude) or not isfinite(latitude):
        return False
    if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        return False
    # EPSG areas may straddle the antimeridian.
    in_longitude = (
        area.west <= longitude <= area.east
        if area.west <= area.east
        else longitude >= area.west or longitude <= area.east
    )
    return in_longitude and area.south <= latitude <= area.north
