#!/usr/bin/env python3
"""Build the deterministic GitHub release archive for Zituan."""

from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def version() -> str:
    value = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not value or any(part == "" for part in value.split(".")):
        raise SystemExit("VERSION is empty or malformed")
    return value


def zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, FIXED_TIMESTAMP)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def text_bytes(path: Path) -> bytes:
    """Return UTF-8 text with stable LF line endings on every platform."""
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def source_entries() -> list[tuple[str, bytes]]:
    preview = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
    preview = preview.replace(
        "../pet/lilac-chibi/spritesheet.webp",
        "lilac-chibi/spritesheet.webp",
    )

    entries = [
        ("ASSET-LICENSE.md", text_bytes(ROOT / "ASSET-LICENSE.md")),
        ("LICENSE.txt", text_bytes(ROOT / "LICENSE")),
        ("README.md", text_bytes(ROOT / "docs" / "INSTALL.md")),
        (
            "lilac-chibi/pet.json",
            text_bytes(ROOT / "pet" / "lilac-chibi" / "pet.json"),
        ),
        (
            "lilac-chibi/spritesheet.webp",
            (ROOT / "pet" / "lilac-chibi" / "spritesheet.webp").read_bytes(),
        ),
        ("preview.html", preview.encode("utf-8")),
    ]
    return sorted(entries, key=lambda item: item[0])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    release_version = version()
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"zituan-codex-pet-v{release_version}.zip"

    with ZipFile(archive, "w", compression=ZIP_STORED) as bundle:
        for name, data in source_entries():
            bundle.writestr(zip_info(name), data, compress_type=ZIP_STORED)

    atlas = ROOT / "pet" / "lilac-chibi" / "spritesheet.webp"
    sums = (
        f"{sha256(archive)}  {archive.name}\n"
        f"{sha256(atlas)}  pet/lilac-chibi/spritesheet.webp\n"
    )
    (DIST / "SHA256SUMS.txt").write_text(sums, encoding="ascii", newline="\n")

    print(f"built={archive.relative_to(ROOT)}")
    print(f"sha256={sha256(archive)}")
    print(f"bytes={archive.stat().st_size}")


if __name__ == "__main__":
    main()
