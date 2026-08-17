#!/usr/bin/env python3
import hashlib
import json
import os
import plistlib
import re
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "yodaluca23/Fusion-AltStore"
API_URL = f"https://api.github.com/repos/{REPO}/releases"
SOURCE_PATH = Path(__file__).resolve().parent.parent / "fusion.json"
BUNDLE_IDENTIFIER = "dev.fusionapp.Fusion"
ICON_URL = "https://avatars.githubusercontent.com/u/67206487?s=400&v=4"
ASSET_SUFFIX = "-ios.ipa"
SCREENSHOT_URLS = [
    "https://raw.githubusercontent.com/sti000en/fusion-altstore-source/main/screenshots/screenshot-1.jpg",
    "https://raw.githubusercontent.com/sti000en/fusion-altstore-source/main/screenshots/screenshot-2.jpg",
    "https://raw.githubusercontent.com/sti000en/fusion-altstore-source/main/screenshots/screenshot-3.jpg",
]


def api_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "fusion-altstore-source",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_json(url):
    req = Request(url, headers=api_headers())
    with urlopen(req) as resp:
        return json.load(resp)


def fetch_releases():
    releases = []
    page = 1
    while True:
        batch = fetch_json(f"{API_URL}?per_page=100&page={page}")
        if not batch:
            break
        releases.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return releases


def find_ios_asset(release):
    for asset in release.get("assets", []):
        if asset["name"].endswith(ASSET_SUFFIX):
            return asset
    return None


def download_ipa(url, dest):
    req = Request(url, headers=api_headers())
    with urlopen(req) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def read_info_plist(ipa_path):
    with zipfile.ZipFile(ipa_path) as zf:
        info_plist_name = next(
            (n for n in zf.namelist() if re.match(r"^Payload/[^/]+\.app/Info\.plist$", n)),
            None,
        )
        if info_plist_name is None:
            raise ValueError(f"No Info.plist found in {ipa_path}")
        with zf.open(info_plist_name) as f:
            return plistlib.load(f)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cached_versions():
    if not SOURCE_PATH.exists():
        return {}
    with open(SOURCE_PATH) as f:
        data = json.load(f)
    cached = {}
    for app in data.get("apps", []):
        if app.get("bundleIdentifier") == BUNDLE_IDENTIFIER:
            for version in app.get("versions", []):
                cached[version["downloadURL"]] = version
    return cached


def build_version_entry(release, asset, cached):
    download_url = asset["browser_download_url"]
    if download_url in cached:
        return cached[download_url]

    tmp_path = Path("/tmp") / asset["name"]
    try:
        download_ipa(download_url, tmp_path)
        plist = read_info_plist(tmp_path)
        size = tmp_path.stat().st_size
        sha256 = sha256_of(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    description = (release.get("body") or "").strip() or release.get("name") or release["tag_name"]

    return {
        "version": plist["CFBundleShortVersionString"],
        "buildVersion": str(plist["CFBundleVersion"]),
        "date": release["published_at"],
        "localizedDescription": description,
        "downloadURL": download_url,
        "size": size,
        "sha256": sha256,
        "minOSVersion": plist.get("MinimumOSVersion", "26.0"),
    }


def default_source():
    return {
        "name": "Fusion (Unofficial)",
        "subtitle": "Fusion builds for AltStore and SideStore.",
        "description": "Automatisch generierte Update-Quelle für Fusion von yodaluca23.",
        "website": "https://github.com/yodaluca23/Fusion-AltStore",
        "tintColor": "1E90FF",
        "news": [],
        "apps": [
            {
                "name": "Fusion",
                "bundleIdentifier": BUNDLE_IDENTIFIER,
                "developerName": "yodaluca23",
                "subtitle": "Fusion für iOS",
                "localizedDescription": "Fusion, unsigned IPA aus den GitHub-Releases.",
                "iconURL": ICON_URL,
                "tintColor": "1E90FF",
                "category": "entertainment",
                "screenshotURLs": SCREENSHOT_URLS,
                "versions": [],
            }
        ],
    }


def build_source():
    releases = fetch_releases()
    cached = load_cached_versions()

    versions = []
    for release in releases:
        if release.get("draft"):
            continue
        asset = find_ios_asset(release)
        if asset is None:
            continue
        versions.append(build_version_entry(release, asset, cached))

    versions.sort(key=lambda v: v["date"], reverse=True)

    data = default_source()
    if SOURCE_PATH.exists():
        with open(SOURCE_PATH) as f:
            data = json.load(f)

    for app in data["apps"]:
        if app.get("bundleIdentifier") == BUNDLE_IDENTIFIER:
            app["versions"] = versions

    with open(SOURCE_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    build_source()
