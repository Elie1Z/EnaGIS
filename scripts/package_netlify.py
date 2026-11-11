"""Package EnaGIS Live as a ready-to-upload static Netlify Drop site."""

import argparse
import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "img"} and attrs.get("src"):
            self.urls.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.urls.append(attrs["href"])


def package(output):
    output = output.resolve()
    if not output.is_relative_to(ROOT / "outputs") or output == ROOT / "outputs":
        raise ValueError("Choose a package directory beneath outputs/")
    source = ROOT / "live"
    files = {name: source / name for name in ("index.html", "style.css")}
    for folder in ("assets", "vendor", "js", "hero"):
        for path in sorted((source / folder).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink cannot enter public package: {path}")
            if path.is_file():
                files[path.relative_to(source).as_posix()] = path
    for name in ("LICENSE", "LICENSE-DATA.md", "THIRD_PARTY_NOTICES.md"):
        files[name] = ROOT / name
    contents = {name: path.read_bytes() for name, path in files.items()}
    parser = Resources()
    parser.feed(contents["index.html"].decode("utf-8"))
    urls = parser.urls + re.findall(r"url\(['\"]?([^)'\"]+)", contents["style.css"].decode("utf-8"))
    for url in urls:
        parsed = urlsplit(url)
        if not parsed.scheme and not parsed.netloc:
            name = unquote(parsed.path)
            if name not in contents:
                raise ValueError(f"Missing local page resource: {name}")
    site = output / "site"
    if site.exists():
        existing = {p.relative_to(site).as_posix() for p in site.rglob("*") if p.is_file()}
        if extra := existing - contents.keys():
            raise ValueError(f"Unexpected files in public output; use a new directory: {extra}")
    for name, data in contents.items():
        target = site / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    archive = output / "EnaGIS-Netlify-Drop.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for name, data in sorted(contents.items()):
            entry = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            entry.external_attr = 0o644 << 16
            bundle.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None or "index.html" not in bundle.namelist():
            raise ValueError("Archive integrity check failed")
        for name, data in contents.items():
            if bundle.read(name) != data:
                raise ValueError(f"Archive differs from source: {name}")
    audit = {
        "entry_point": "index.html",
        "source": "live/",
        "files": len(contents),
        "uncompressed_bytes": sum(map(len, contents.values())),
        "zip_bytes": archive.stat().st_size,
        "zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "artifacts": [
            {"path": name, "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in sorted(contents.items())
        ],
    }
    (output / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n", "utf-8")
    (output / "DEPLOY.md").write_text(
        "# Publish EnaGIS Live\n\n"
        "1. Open https://app.netlify.com/drop in your browser.\n"
        "2. Drop EnaGIS-Netlify-Drop.zip there, or drop the site folder.\n"
        "3. Open the URL Netlify gives you. "
        "No build command or environment variables are needed.\n\n"
        "The ZIP contains index.html directly at its root. Drop site/, not this parent folder.\n"
        "The saved Nyabihu analysis is included. Fresh searches and online basemaps need internet\n"
        "and depend on the availability of external open-data services.\n",
        "utf-8",
    )
    return {
        "site": str(site),
        "zip": str(archive),
        **{k: v for k, v in audit.items() if k != "artifacts"},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/netlify-drop")
    args = parser.parse_args()
    print(json.dumps(package(args.output), indent=2))


if __name__ == "__main__":
    main()
