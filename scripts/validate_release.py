#!/usr/bin/env python3
"""Validate the source pet and, optionally, a built release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "pet" / "lilac-chibi" / "spritesheet.webp"
MANIFEST = ROOT / "pet" / "lilac-chibi" / "pet.json"
EXPECTED_SIZE = (1536, 2288)
MAX_BYTES = 20 * 1024 * 1024
EXPECTED_ARCHIVE_ENTRIES = {
    "ASSET-LICENSE.md",
    "LICENSE.txt",
    "README.md",
    "lilac-chibi/pet.json",
    "lilac-chibi/spritesheet.webp",
    "preview.html",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def text_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def webp_size(data: bytes) -> tuple[int, int]:
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a RIFF WebP file")

    offset = 12
    while offset + 8 <= len(data):
        chunk = data[offset : offset + 4]
        length = struct.unpack_from("<I", data, offset + 4)[0]
        payload = data[offset + 8 : offset + 8 + length]

        if chunk == b"VP8X" and len(payload) >= 10:
            width = 1 + int.from_bytes(payload[4:7], "little")
            height = 1 + int.from_bytes(payload[7:10], "little")
            return width, height

        if chunk == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
            width = int.from_bytes(payload[6:8], "little") & 0x3FFF
            height = int.from_bytes(payload[8:10], "little") & 0x3FFF
            return width, height

        if chunk == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
            bits = int.from_bytes(payload[1:5], "little")
            width = 1 + (bits & 0x3FFF)
            height = 1 + ((bits >> 14) & 0x3FFF)
            return width, height

        offset += 8 + length + (length & 1)

    raise ValueError("WebP dimensions not found")


def validate_manifest(data: bytes) -> dict[str, object]:
    try:
        manifest = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"pet.json is not valid UTF-8 JSON: {exc}") from exc

    required = {
        "id": "lilac-chibi",
        "displayName": "紫团",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    for key, expected in required.items():
        if manifest.get(key) != expected:
            raise ValueError(f"pet.json {key!r} must be {expected!r}")
    if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
        raise ValueError("pet.json description must be a non-empty string")
    return manifest


def validate_source() -> None:
    if not MANIFEST.is_file() or not ATLAS.is_file():
        raise ValueError("pet/lilac-chibi must contain pet.json and spritesheet.webp")

    validate_manifest(MANIFEST.read_bytes())
    atlas = ATLAS.read_bytes()
    dimensions = webp_size(atlas)
    if dimensions != EXPECTED_SIZE:
        raise ValueError(f"spritesheet dimensions are {dimensions}, expected {EXPECTED_SIZE}")
    if len(atlas) > MAX_BYTES:
        raise ValueError(f"spritesheet is larger than {MAX_BYTES} bytes")

    expected_hashes = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))
    expected_hash = expected_hashes.get("pet/lilac-chibi/spritesheet.webp")
    actual_hash = sha256_bytes(atlas)
    if actual_hash != expected_hash:
        raise ValueError(f"spritesheet SHA-256 mismatch: {actual_hash}")

    preview = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
    if "../pet/lilac-chibi/spritesheet.webp" not in preview:
        raise ValueError("repository preview must load ../pet/lilac-chibi/spritesheet.webp")

    print("source=ok")
    print(f"atlas_dimensions={dimensions[0]}x{dimensions[1]}")
    print(f"atlas_sha256={actual_hash}")


def validate_archive(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"archive not found: {path}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    expected_name = f"zituan-codex-pet-v{version}.zip"
    if path.name != expected_name:
        raise ValueError(f"archive name must be {expected_name}")

    with ZipFile(path) as bundle:
        names = set(bundle.namelist())
        if names != EXPECTED_ARCHIVE_ENTRIES:
            missing = sorted(EXPECTED_ARCHIVE_ENTRIES - names)
            extra = sorted(names - EXPECTED_ARCHIVE_ENTRIES)
            raise ValueError(f"archive entries mismatch; missing={missing}, extra={extra}")

        for name in names:
            parts = PurePosixPath(name).parts
            if not parts or name.startswith("/") or ".." in parts:
                raise ValueError(f"unsafe archive path: {name}")

        manifest = bundle.read("lilac-chibi/pet.json")
        atlas = bundle.read("lilac-chibi/spritesheet.webp")
        validate_manifest(manifest)
        if webp_size(atlas) != EXPECTED_SIZE:
            raise ValueError("archive spritesheet dimensions are invalid")
        if manifest != text_bytes(MANIFEST):
            raise ValueError("archive pet.json differs from source")
        if atlas != ATLAS.read_bytes():
            raise ValueError("archive spritesheet differs from source")

        preview = bundle.read("preview.html").decode("utf-8")
        if "lilac-chibi/spritesheet.webp" not in preview:
            raise ValueError("archive preview does not load the packaged spritesheet")
        if "../pet/lilac-chibi/spritesheet.webp" in preview:
            raise ValueError("archive preview still contains the repository-only path")

        bad = bundle.testzip()
        if bad is not None:
            raise ValueError(f"archive CRC failure: {bad}")

    print("archive=ok")
    print(f"archive_sha256={sha256_file(path)}")
    print(f"archive_bytes={path.stat().st_size}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, help="also validate a built ZIP archive")
    args = parser.parse_args()

    try:
        validate_source()
        if args.archive:
            validate_archive(args.archive.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"validation failed: {exc}") from exc


if __name__ == "__main__":
    main()
