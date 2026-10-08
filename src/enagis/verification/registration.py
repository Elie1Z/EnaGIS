"""Bind exact ranking/sample bytes to an annotated Git tag and its remote object."""

import hashlib
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from enagis.data_io import file_hash, write_json
from enagis.verification.bundle import BUNDLE_FILES, read_json, verify_bundle


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=60)
    if result.returncode:
        # Do not echo a credential-bearing command or arbitrary stderr into public artifacts.
        raise ValueError(f"Git {args[0]} failed; check repository, tag and remote availability")
    return result.stdout


def git_text(root, *args):
    return git(root, *args).decode("utf-8").strip()


def repository(root, bundle):
    root = Path(root).resolve()
    actual = Path(git_text(root, "rev-parse", "--show-toplevel")).resolve()
    if root != actual:
        raise ValueError("repository argument must identify its root")
    bundle = Path(bundle).resolve()
    if not bundle.is_relative_to(root):
        raise ValueError("freeze package must be inside the committed repository")
    return root, bundle.relative_to(root).as_posix()


def tag_binding(root, bundle, manifest):
    root, relative = repository(root, bundle)
    tag = manifest["freeze_tag"]
    ref = f"refs/tags/{tag}"
    if git_text(root, "cat-file", "-t", ref) != "tag":
        raise ValueError("freeze requires an annotated tag with a recorded tagger time")
    obj = git_text(root, "rev-parse", ref)
    commit = git_text(root, "rev-parse", f"{ref}^{{commit}}")
    stamp = git_text(root, "for-each-ref", "--format=%(taggerdate:iso-strict)", ref)
    if datetime.fromisoformat(stamp).tzinfo is None:
        raise ValueError("tagger timestamp must include its timezone")
    tree = {}
    for row in git(root, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if row:
            descriptor, name = row.split(b"\t", 1)
            mode, kind, digest = descriptor.decode().split()
            tree[name.decode("utf-8")] = (mode, kind, digest)
    algorithm = git_text(root, "rev-parse", "--show-object-format")

    def agrees(name):
        blob = (root / name).read_bytes()
        checksum = hashlib.new(algorithm, f"blob {len(blob)}\0".encode() + blob).hexdigest()
        entry = tree.get(name)
        if not entry or entry[0] not in {"100644", "100755"} or entry[1:] != ("blob", checksum):
            raise ValueError(f"tag does not contain the exact reviewed file: {name}")

    expected_bundle = {f"{relative}/{p}" for p in BUNDLE_FILES | {"manifest.json"}}
    if {n for n in tree if n.startswith(relative + "/")} != expected_bundle:
        raise ValueError("tagged freeze package has unexpected or missing files")
    source_paths = {p.relative_to(root).as_posix() for p in (root / "src/enagis").rglob("*.py")}
    if (
        not source_paths
        or {n for n in tree if n.startswith("src/enagis/") and n.endswith(".py")} != source_paths
    ):
        raise ValueError("tagged source file set does not match the executing package")
    source_digest = hashlib.sha256()
    for name in sorted(source_paths):
        source_digest.update(
            name.removeprefix("src/enagis/").encode() + b"\0" + (root / name).read_bytes()
        )
    if (
        source_digest.hexdigest() != manifest["source_code_sha256"]
        or file_hash(root / "uv.lock") != manifest["lockfile_sha256"]
    ):
        raise ValueError("tagged repository code/lockfile differs from the prepared scientific run")
    for name in sorted(expected_bundle | source_paths | {"uv.lock"}):
        agrees(name)
    return root, relative, obj, commit, stamp


def remote_url(root, name, purpose):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("invalid remote name")
    url = git_text(root, "config", "--get", f"remote.{name}.url")
    if not url or url.startswith("-") or ("://" in url and urlsplit(url).password):
        raise ValueError("unsafe or credential-bearing remote URL")
    if url.startswith(("http://", "https://")) and urlsplit(url).username:
        raise ValueError("remote URL must not embed credentials")
    if purpose != "synthetic_fixture" and not url.startswith(("https://", "ssh://", "git@")):
        raise ValueError("real freeze needs a configured HTTPS or SSH remote")
    return url


def remote_matches(root, url, tag, obj, commit):
    rows = git_text(
        root, "ls-remote", "--exit-code", url, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"
    )
    refs = dict(line.split()[::-1] for line in rows.splitlines())
    if refs.get(f"refs/tags/{tag}") != obj or refs.get(f"refs/tags/{tag}^{{}}") != commit:
        raise ValueError("freeze tag and commit are not both present on the remote")


def bound_receipt(root, bundle, manifest, remote, *, check_remote):
    root, relative, obj, commit, stamp = tag_binding(root, bundle, manifest)
    url = remote_url(root, remote, manifest["purpose"])
    if check_remote:
        remote_matches(root, url, manifest["freeze_tag"], obj, commit)
    return {
        "schema_version": "phase7-seal-v1",
        "freeze_id": manifest["freeze_id"],
        "purpose": manifest["purpose"],
        "bundle_path": relative,
        "manifest_sha256": file_hash(Path(bundle) / "manifest.json"),
        "tag": manifest["freeze_tag"],
        "tag_object": obj,
        "commit": commit,
        "remote_name": remote,
        "remote_url": url,
        "sealed_at": stamp,
        "timestamp_basis": "Git annotated-tag time; reported observation dates are human evidence",
        "remote_status_at_seal": "tag_and_commit_verified",
    }


def seal(bundle, receipt_path, root, lockfile, *, remote="origin", allow_fixture=False):
    receipt_path = Path(receipt_path).resolve()
    if receipt_path.exists() or receipt_path.is_relative_to(Path(bundle).resolve()):
        raise ValueError("seal receipt must be new and outside the frozen package")
    manifest, _, _ = verify_bundle(bundle, lockfile, allow_fixture=allow_fixture)
    receipt = bound_receipt(root, bundle, manifest, remote, check_remote=True)
    write_json(receipt_path, receipt)
    return receipt


def verify_seal(bundle, receipt_path, root, lockfile, *, allow_fixture=False, check_remote=False):
    manifest, protocol, sample = verify_bundle(bundle, lockfile, allow_fixture=allow_fixture)
    receipt = read_json(receipt_path)
    expected = bound_receipt(
        root, bundle, manifest, receipt["remote_name"], check_remote=check_remote
    )
    if receipt != expected:
        raise ValueError("seal receipt does not match the immutable tagged package")
    return manifest, protocol, sample, receipt
