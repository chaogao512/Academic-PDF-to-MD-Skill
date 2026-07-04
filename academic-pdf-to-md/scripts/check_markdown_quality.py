#!/usr/bin/env python3
"""Check raw.md and clean.md quality for an academic PDF conversion folder."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


STRUCTURE_PATTERNS = {
    "title_heading": re.compile(r"^#\s+\S+", re.MULTILINE),
    "frontmatter": re.compile(r"\A---\n.*?\n---\n", re.DOTALL),
    "abstract": re.compile(r"(^|\n)#{1,3}\s*(abstract|摘要)\b", re.IGNORECASE),
    "keywords": re.compile(r"(keywords|key words|关键词)", re.IGNORECASE),
    "references": re.compile(r"(^|\n)#{1,3}\s*(references|bibliography|参考文献)\b", re.IGNORECASE),
    "figures_or_tables": re.compile(r"\b(fig\.?|figure|table|图|表)\s*\d*", re.IGNORECASE),
}

GARBAGE_PATTERNS = {
    "replacement_chars": re.compile("\ufffd"),
    "mojibake": re.compile(r"(Ã|Â|�|â€|å|æ|ç){3,}"),
    "excessive_whitespace": re.compile(r"\n{5,}"),
    "hyphen_linebreaks": re.compile(r"[A-Za-z]-\n[A-Za-z]"),
}


@dataclass
class Finding:
    severity: str
    item: str
    detail: str


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_pdf_sample(pdf: Path, max_pages: int = 3) -> str:
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-f", "1", "-l", str(max_pages), str(pdf), "-"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0:
            return proc.stdout

    try:
        import fitz  # type: ignore

        doc = fitz.open(str(pdf))
        chunks = []
        for index in range(min(max_pages, doc.page_count)):
            chunks.append(doc.load_page(index).get_text("text"))
        return "\n".join(chunks)
    except Exception:
        return ""


def check_file_presence(folder: Path, findings: list[Finding]) -> None:
    for name in ["raw.md", "clean.md", "metadata.json"]:
        path = folder / name
        if not path.exists():
            findings.append(Finding("high", name, "missing"))
        elif path.stat().st_size == 0:
            findings.append(Finding("medium", name, "exists but is empty"))


def check_structure(clean_text: str, findings: list[Finding]) -> None:
    for item, pattern in STRUCTURE_PATTERNS.items():
        if not pattern.search(clean_text):
            severity = "medium" if item in {"figures_or_tables", "keywords"} else "high"
            findings.append(Finding(severity, item, "not detected in clean.md"))


def check_garbage(text: str, findings: list[Finding]) -> None:
    for item, pattern in GARBAGE_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings.append(Finding("medium", item, f"detected {len(matches)} possible issue(s)"))


def check_sample_overlap(pdf: Path | None, clean_text: str, findings: list[Finding]) -> None:
    if not pdf:
        findings.append(Finding("low", "pdf_sample", "no source PDF provided for sampled comparison"))
        return
    sample = extract_pdf_sample(pdf)
    if not sample.strip():
        findings.append(Finding("medium", "pdf_sample", "could not extract sampled PDF text locally"))
        return

    words = re.findall(r"[\w\u4e00-\u9fff]{4,}", sample.lower())
    if not words:
        findings.append(Finding("medium", "pdf_sample", "sampled PDF text contains too few comparable tokens"))
        return

    unique_words = list(dict.fromkeys(words[:120]))
    clean_lower = clean_text.lower()
    hits = sum(1 for word in unique_words if word in clean_lower)
    ratio = hits / max(len(unique_words), 1)
    if ratio < 0.08:
        findings.append(
            Finding("high", "sample_overlap", f"low overlap with first sampled pages ({ratio:.1%})")
        )
    elif ratio < 0.18:
        findings.append(
            Finding("medium", "sample_overlap", f"weak overlap with first sampled pages ({ratio:.1%})")
        )


def quality_status(findings: list[Finding]) -> str:
    if any(f.severity == "high" for f in findings):
        return "needs review"
    if any(f.severity == "medium" for f in findings):
        return "usable with cautions"
    return "passed"


def write_report(folder: Path, findings: list[Finding], status: str) -> None:
    lines = [
        "# Quality Report",
        "",
        f"Checked at: {datetime.now(timezone.utc).isoformat()}",
        f"Status: {status}",
        "",
        "## Findings",
        "",
    ]
    if findings:
        for finding in findings:
            lines.append(f"- [{finding.severity}] {finding.item}: {finding.detail}")
    else:
        lines.append("- No structural issues detected by the scripted checks.")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This report is a scripted quality screen, not a guarantee of perfect conversion. Manually inspect formulas, tables, and sampled pages when the paper is important.",
        ]
    )
    (folder / "quality-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_metadata(folder: Path, status: str, findings: list[Finding]) -> None:
    metadata = folder / "metadata.json"
    if not metadata.exists():
        return
    try:
        data = json.loads(metadata.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    data["quality_status"] = status
    data["quality_checked_at"] = datetime.now(timezone.utc).isoformat()
    data["quality_findings"] = [finding.__dict__ for finding in findings]
    metadata.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Paper output folder")
    parser.add_argument("--pdf", type=Path, help="Optional source PDF for sampled comparison")
    args = parser.parse_args()

    folder = args.folder
    findings: list[Finding] = []
    check_file_presence(folder, findings)

    raw_text = read_text(folder / "raw.md")
    clean_text = read_text(folder / "clean.md")
    check_structure(clean_text, findings)
    check_garbage(raw_text + "\n" + clean_text, findings)
    check_sample_overlap(args.pdf, clean_text, findings)

    status = quality_status(findings)
    write_report(folder, findings, status)
    update_metadata(folder, status, findings)

    print(f"Status: {status}")
    print(f"Report: {folder / 'quality-report.md'}")
    return 1 if status == "needs review" else 0


if __name__ == "__main__":
    raise SystemExit(main())
