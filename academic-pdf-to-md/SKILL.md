---
name: academic-pdf-to-md
description: Convert academic research-paper PDFs into traceable dual-track Markdown. Use when Codex needs to parse single or batch scholarly PDFs into raw.md and research-reading clean.md, choose between local PDF/OCR tools and approved online services, preserve titles/abstracts/keywords/sections/figures/tables/formulas/references, create metadata and quality reports, or prepare papers for literature review, Obsidian, wiki, RAG, or AI reading workflows.
---

# Academic PDF To Markdown

Convert academic papers from PDF to Markdown with a local-first, quality-checked workflow. Produce two Markdown tracks:

- `raw.md`: closest converter output for traceability.
- `clean.md`: research-reading Markdown for literature review and AI use.

## Core Rules

1. Diagnose the PDF before choosing a converter.
2. Prefer local tools. Ask the user before uploading any PDF or page image to online/API services.
3. Do not invent missing content. Mark uncertainty in `clean.md` and `quality-report.md`.
4. Keep `raw.md` traceable to the converter output; do substantial cleanup only in `clean.md`.
5. Run quality checks before reporting completion.

## Quick Start

Use the bundled scripts from this skill directory:

```bash
python scripts/diagnose_pdf.py paper.pdf
python scripts/init_output.py paper.pdf -o ./converted
python scripts/check_markdown_quality.py ./converted/paper --pdf paper.pdf
```

Then run the selected external converter and place outputs into the folder contract.

## Workflow

### 1. Diagnose

Run `scripts/diagnose_pdf.py` on each PDF. Use its JSON result to identify:

- page count and file size;
- whether a text layer is present;
- estimated text density;
- likely scanned/image-heavy status;
- available local tools;
- recommended route.

If the user provides many PDFs, diagnose a small representative sample first unless they explicitly want all files processed.

### 2. Select Tool Route

Use `references/tool-routing.md` when choosing tools or when a preferred tool is unavailable.

Default routes:

- Text-layer paper: use Poppler, PyMuPDF, pdfplumber, pdfminer.six, or pypdf for text extraction; use pdfplumber/PyMuPDF when tables or coordinates matter.
- Complex academic layout: prefer MinerU or OpenDataLoader if installed.
- Scanned or image-heavy paper: prefer local OCR-capable tools first, including MinerU local modes, OpenDataLoader local modes, or baidu/Unlimited-OCR.
- Online fallback: ask the user before using MinerU API, OpenDataLoader hybrid/remote, Baidu AI Studio PaddleOCR, or similar upload-based services.

State the chosen route in one or two sentences before running it.

### 3. Create Output Folder

Run `scripts/init_output.py` to create one independent folder per paper:

```text
<paper-slug>/
├── raw.md
├── clean.md
├── metadata.json
├── quality-report.md
├── assets/
└── samples/
```

Use `assets/` for extracted figures, tables, images, HTML, JSON, LaTeX, or converter artifacts. Use `samples/` for sampled page text, rendered pages, or comparison snippets.

### 4. Produce `raw.md`

Save the converter's Markdown output as `raw.md`. If the converter produces HTML, JSON, LaTeX, or extracted images, keep those files under `assets/` and reference them in `metadata.json`.

For weak conversions, keep the partial `raw.md` rather than overwriting it with guesses. Then try a second route and record both attempts.

### 5. Produce `clean.md`

Read `references/clean-markdown.md` before cleaning. The clean version should include:

- YAML frontmatter;
- title, authors, venue/year if available;
- abstract and keywords;
- table of contents;
- cleaned section hierarchy;
- figure and table index;
- formula notes when formulas are detected but not faithfully converted;
- references section;
- cleanup notes and unresolved issues.

Remove obvious page headers, footers, page numbers, broken line wrapping, duplicated running titles, and OCR artifacts. Preserve the authors' claims and wording.

### 6. Quality Check

Run:

```bash
python scripts/check_markdown_quality.py <paper-output-dir> --pdf <source.pdf>
```

The script checks file presence, rough structure, common OCR problems, frontmatter, references, and sampled source text when local extraction tools are available.

If the report flags high-risk issues, either retry with a better route or clearly report the remaining risk.

### 7. Report Back

End with:

- output folder path;
- converter route used;
- whether online/API services were used;
- quality result and remaining risks;
- next useful action, such as rerunning with MinerU, Unlimited-OCR, or PaddleOCR if needed.

## Online Upload Gate

Before using any service that may upload PDF content, ask clearly:

```text
This route may upload the PDF or rendered pages to <service>. Do you approve using it for <file>?
```

Proceed only after approval. If approval is not granted, continue with local-only routes and document the limitation.

## Bundled Resources

- `scripts/diagnose_pdf.py`: local PDF diagnosis and route recommendation.
- `scripts/init_output.py`: output folder creation and metadata skeleton.
- `scripts/check_markdown_quality.py`: Markdown and sampled PDF quality checks.
- `references/tool-routing.md`: tool-selection details, including MinerU, OpenDataLoader, baidu/Unlimited-OCR, and PaddleOCR.
- `references/clean-markdown.md`: clean Markdown structure and cleanup rules.
