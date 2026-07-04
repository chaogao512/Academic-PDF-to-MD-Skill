#!/usr/bin/env python3
"""Diagnose an academic PDF and recommend a conversion route."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


TOOLS = [
    "pdfinfo",
    "pdftotext",
    "pdftoppm",
    "python3",
    "mineru",
    "mineru-open-api",
    "opendataloader-pdf",
    "unlimited-ocr",
]


def run_command(args: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as exc:  # noqa: BLE001 - diagnostics should not crash.
        return 1, "", str(exc)


def installed_tools() -> dict[str, bool]:
    return {tool: shutil.which(tool) is not None for tool in TOOLS}


def pdfinfo_pages(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    code, out, _err = run_command(["pdfinfo", str(pdf)])
    if code != 0:
        return None
    for line in out.splitlines():
        if line.lower().startswith("pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def pypdf_pages(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore

        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return None


def pymupdf_sample_text(pdf: Path, max_pages: int = 5) -> tuple[int, list[int]]:
    try:
        import fitz  # type: ignore

        doc = fitz.open(str(pdf))
        counts: list[int] = []
        for index in range(min(max_pages, doc.page_count)):
            text = doc.load_page(index).get_text("text")
            counts.append(len(text.strip()))
        return sum(counts), counts
    except Exception:
        return 0, []


def poppler_sample_text(pdf: Path, max_pages: int = 5) -> tuple[int, list[int]]:
    if not shutil.which("pdftotext"):
        return 0, []
    code, out, _err = run_command(
        ["pdftotext", "-f", "1", "-l", str(max_pages), str(pdf), "-"],
        timeout=60,
    )
    if code != 0:
        return 0, []
    pages = out.split("\f")
    counts = [len(page.strip()) for page in pages if page.strip()]
    return sum(counts), counts


def recommend_route(page_count: int | None, text_chars: int, sampled_pages: int) -> dict[str, str]:
    pages = max(sampled_pages, 1)
    chars_per_page = text_chars / pages
    likely_scanned = chars_per_page < 120

    if likely_scanned:
        route = "local-ocr"
        reason = "sampled pages have very little extractable text"
        tools = "MinerU local/OpenDataLoader local/baidu Unlimited-OCR; ask before online OCR"
    elif page_count and page_count > 40:
        route = "complex-or-long-paper"
        reason = "long paper with a usable text layer; structure may need a stronger parser"
        tools = "PyMuPDF or Poppler first; retry with MinerU/OpenDataLoader for layout"
    else:
        route = "text-layer"
        reason = "sampled pages have a usable text layer"
        tools = "Poppler/PyMuPDF/pdfplumber/pdfminer.six"

    return {
        "route": route,
        "reason": reason,
        "preferred_tools": tools,
        "chars_per_sampled_page": f"{chars_per_page:.1f}",
    }


def diagnose(pdf: Path) -> dict[str, object]:
    if not pdf.exists():
        raise FileNotFoundError(pdf)
    if pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file: {pdf}")

    page_count = pdfinfo_pages(pdf) or pypdf_pages(pdf)
    sample_limit = min(page_count or 5, 5)
    poppler_chars, poppler_counts = poppler_sample_text(pdf, sample_limit)
    pymupdf_chars, pymupdf_counts = pymupdf_sample_text(pdf, sample_limit)

    if poppler_chars >= pymupdf_chars:
        text_chars = poppler_chars
        page_counts = poppler_counts
        text_probe = "pdftotext"
    else:
        text_chars = pymupdf_chars
        page_counts = pymupdf_counts
        text_probe = "PyMuPDF"

    sampled_pages = len(page_counts)
    recommendation = recommend_route(page_count, text_chars, sampled_pages)
    size_bytes = pdf.stat().st_size

    return {
        "source_pdf": str(pdf.resolve()),
        "file_size_bytes": size_bytes,
        "file_size_mb": round(size_bytes / 1024 / 1024, 2),
        "page_count": page_count,
        "text_probe": text_probe,
        "sampled_pages": sampled_pages,
        "sample_text_chars": text_chars,
        "sample_text_chars_by_page": page_counts,
        "has_text_layer": text_chars >= 120,
        "likely_scanned_or_image_heavy": recommendation["route"] == "local-ocr",
        "recommended_route": recommendation,
        "installed_tools": installed_tools(),
        "privacy_policy": "local-first; ask before uploading to online/API services",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Academic PDF to diagnose")
    parser.add_argument("-o", "--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    try:
        result = diagnose(args.pdf)
    except Exception as exc:  # noqa: BLE001 - user-facing CLI.
        print(f"diagnose_pdf.py: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + os.linesep, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
