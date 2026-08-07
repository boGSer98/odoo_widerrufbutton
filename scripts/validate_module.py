#!/usr/bin/env python3
"""Lightweight validation for the Odoo Widerrufbutton add-ons.

This intentionally avoids requiring a running Odoo server. It checks the repository
shape, manifest metadata, app-store description hygiene, syntax, XML well-formedness,
packaged asset references and obvious secret/private-IP patterns.
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDONS = [
    "odoo_widerrufbutton",
    "odoo_widerrufbutton_sale",
    "odoo_widerrufbutton_account",
]

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"fernet:gAAAAA[0-9A-Za-z_-]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    re.compile(r"192\.168\.\d+\.\d+"),
]
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pyc", ".zip"}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_manifest(addon: Path) -> dict:
    manifest_path = addon / "__manifest__.py"
    if not manifest_path.is_file():
        fail(f"Missing manifest: {manifest_path.relative_to(REPO_ROOT)}")
    try:
        return ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(f"Cannot parse {manifest_path.relative_to(REPO_ROOT)}: {exc}")


def validate_repo_shape() -> None:
    if (REPO_ROOT / "__manifest__.py").exists():
        fail("Repository root must contain addon directories, not a root-level __manifest__.py")
    for addon_name in ADDONS:
        addon = REPO_ROOT / addon_name
        if not addon.is_dir():
            fail(f"Missing addon directory: {addon_name}")
        if not (addon / "__init__.py").is_file():
            fail(f"Missing __init__.py in {addon_name}")
        if not (addon / "__manifest__.py").is_file():
            fail(f"Missing __manifest__.py in {addon_name}")


def validate_manifest(addon_name: str) -> dict:
    addon = REPO_ROOT / addon_name
    manifest = load_manifest(addon)
    required = ["name", "summary", "version", "category", "author", "license", "support", "depends"]
    for key in required:
        if not manifest.get(key):
            fail(f"{addon_name}: missing manifest key {key!r}")
    if not manifest.get("installable"):
        fail(f"{addon_name}: manifest must be installable")
    for rel in manifest.get("data", []):
        if not (addon / rel).is_file():
            fail(f"{addon_name}: missing data file {rel}")
    for bundle, assets in manifest.get("assets", {}).items():
        for asset in assets:
            asset_path = REPO_ROOT / asset
            if not asset_path.is_file():
                fail(f"{addon_name}: missing asset {asset} in bundle {bundle}")
    for rel in manifest.get("images", []):
        image = addon / rel
        if not image.is_file():
            fail(f"{addon_name}: missing image {rel}")
        if image.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
            fail(f"{addon_name}: unsupported image type {rel}")
    return manifest


def validate_appstore_description(addon_name: str) -> None:
    addon = REPO_ROOT / addon_name
    index = addon / "static" / "description" / "index.html"
    icon = addon / "static" / "description" / "icon.png"
    if not index.is_file():
        fail(f"{addon_name}: missing static/description/index.html")
    if not icon.is_file():
        fail(f"{addon_name}: missing static/description/icon.png")
    html = index.read_text(encoding="utf-8")
    lowered = html.lower()
    for bad in ["<script", "javascript:", "<iframe", "modal", "style=", "https://", "http://"]:
        if bad in lowered:
            fail(f"{addon_name}: forbidden app-store description content: {bad}")
    ET.fromstring(f"<root>{html}</root>")


def validate_syntax() -> None:
    for path in REPO_ROOT.rglob("*.py"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            fail(f"Python syntax error in {path.relative_to(REPO_ROOT)}: {exc}")
    for path in REPO_ROOT.rglob("*.xml"):
        if ".git" in path.parts:
            continue
        ET.parse(path)


def validate_no_generated_or_secrets() -> None:
    forbidden_parts = {"__pycache__"}
    for path in REPO_ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if any(part in forbidden_parts for part in path.parts) or path.suffix == ".pyc":
            fail(f"Generated Python cache is packaged: {path.relative_to(REPO_ROOT)}")
        if not path.is_file() or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"Possible packaged token/secret/private IP in {path.relative_to(REPO_ROOT)}")


def build_zip(addon_name: str, version: str) -> Path:
    addon = REPO_ROOT / addon_name
    asset = Path("/tmp") / f"{addon_name}-{version}.zip"
    if asset.exists():
        asset.unlink()
    with zipfile.ZipFile(asset, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(addon.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            archive.write(path, path.relative_to(REPO_ROOT).as_posix())
    with zipfile.ZipFile(asset) as archive:
        names = set(archive.namelist())
        expected = f"{addon_name}/__manifest__.py"
        if expected not in names:
            fail(f"ZIP missing {expected}")
    return asset


def main() -> None:
    validate_repo_shape()
    manifests = {addon: validate_manifest(addon) for addon in ADDONS}
    validate_appstore_description("odoo_widerrufbutton")
    base_manifest = manifests["odoo_widerrufbutton"]
    if base_manifest.get("price") != 10.00 or base_manifest.get("currency") != "EUR":
        fail("odoo_widerrufbutton: expected price 10.00 EUR")
    validate_syntax()
    validate_no_generated_or_secrets()
    asset = build_zip("odoo_widerrufbutton", base_manifest["version"])
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    print("Validation OK")
    print(f"Base module ZIP: {asset} ({asset.stat().st_size} bytes, sha256={digest})")


if __name__ == "__main__":
    main()
