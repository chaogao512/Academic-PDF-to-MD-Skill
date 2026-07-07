# Academic PDF to Markdown Skill

`academic-pdf-to-md` is a Codex/ccswitch skill for converting academic research-paper PDFs into traceable dual-track Markdown.

It is designed for scholarly PDF workflows where the output must be usable for reading, literature review, Obsidian/wiki notes, RAG ingestion, or later AI analysis.

## What It Does

- Diagnoses PDF type before choosing a converter.
- Uses local-first tool routing.
- Requires explicit confirmation before uploading PDFs or rendered pages to online services.
- Produces two Markdown tracks:
  - `raw.md`: converter output kept for traceability.
  - `clean.md`: research-reading Markdown with metadata, abstract, keywords, sections, figures/tables, references, and conversion notes.
- Provides helper scripts for output initialization, PDF diagnosis, and quality checks.
- Includes tool-routing guidance for Poppler, PyMuPDF, pdfplumber, MinerU, OpenDataLoader, baidu/Unlimited-OCR, and Baidu AI Studio PaddleOCR.

## ccswitch Installation

Use the zip package:

```text
dist/academic-pdf-to-md-ccswitch.zip
```

The zip is packaged for ccswitch with `SKILL.md` at the archive root:

```text
SKILL.md
agents/openai.yaml
references/clean-markdown.md
references/tool-routing.md
scripts/check_markdown_quality.py
scripts/diagnose_pdf.py
scripts/init_output.py
```

If ccswitch reports that `skill.md` or `SKILL.md` is missing, verify that the archive root directly contains `SKILL.md`; it should not be nested under an extra top-level folder.

## Manual Installation

Copy the skill folder into your ccswitch skills directory:

```bash
cp -R academic-pdf-to-md ~/.cc-switch/skills/
```

Then restart or refresh ccswitch if needed.

## Repository Layout

```text
academic-pdf-to-md/
├── SKILL.md
├── agents/
├── references/
└── scripts/

dist/
└── academic-pdf-to-md-ccswitch.zip
```

## Validation

Validate the skill folder with the Codex skill validator:

```bash
python /path/to/skill-creator/scripts/quick_validate.py academic-pdf-to-md
```

The helper scripts are plain Python files and can be syntax-checked with:

```bash
python -m py_compile academic-pdf-to-md/scripts/*.py
```

## Privacy Policy

The skill is local-first. Online services such as MinerU API, OpenDataLoader hybrid/remote modes, or Baidu AI Studio PaddleOCR should only be used after explicit user approval because they may upload PDF content.
