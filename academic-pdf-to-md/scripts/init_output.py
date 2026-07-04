#!/usr/bin/env python3
"""Create the standard output folder for academic PDF to Markdown conversion."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(path: Path) -> str:
    stem = path.stem.strip().lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", stem, flags=re.IGNORECASE).strip("-")
    digest = hashlib.md5(str(path.resolve()).encode("utf-8")).hexdigest()[:8]
    return f"{slug[:80] or 'paper'}-{digest}"


def init_one(pdf: Path, output_root: Path) -> Path:
    if pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file: {pdf}")

    folder = output_root / slugify(pdf)
    (folder / "assets").mkdir(parents=True, exist_ok=True)
    (folder / "samples").mkdir(parents=True, exist_ok=True)

    raw = folder / "raw.md"
    clean = folder / "clean.md"
    report = folder / "quality-report.md"
    metadata = folder / "metadata.json"

    raw.touch(exist_ok=True)
    clean.touch(exist_ok=True)
    if not report.exists():
        report.write_text("# Quality Report\n\nStatus: not checked\n", encoding="utf-8")

    if not metadata.exists():
        data = {
            "source_pdf": str(pdf.resolve()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "conversion_route": "",
            "online_services_used": [],
            "attempts": [],
            "outputs": {
                "raw_md": str(raw.resolve()),
                "clean_md": str(clean.resolve()),
                "quality_report": str(report.resolve()),
                "assets_dir": str((folder / "assets").resolve()),
                "samples_dir": str((folder / "samples").resolve()),
            },
            "quality_status": "not checked",
        }
        metadata.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return folder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="+", type=Path, help="One or more PDF files")
    parser.add_argument("-o", "--output-root", type=Path, default=Path("pdf-md-output"))
    args = parser.parse_args()

    args.output_root.mkdir(parents=True, exist_ok=True)
    folders = []
    for pdf in args.pdfs:
        folders.append(init_one(pdf, args.output_root))

    for folder in folders:
        print(folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
