# Academic PDF to Markdown Skill Design

## Goal

Create a reusable Codex skill for converting academic PDF papers into Markdown. The skill must prioritize scholarly reading quality, traceability, and safe tool selection rather than acting as a single fixed converter.

## Scope

The skill handles single-paper and batch academic PDF conversion. Its first-priority use case is research papers, including Chinese and English papers with titles, abstracts, keywords, sections, figures, tables, formulas, and references.

The first version is a hybrid skill:

- `SKILL.md` defines the workflow, tool-selection rules, privacy policy, output contract, and quality gates.
- `scripts/` provides deterministic helpers for PDF diagnosis, output folder creation, and Markdown quality checks.
- `references/` stores tool routing notes and Markdown cleaning rules.
- External engines such as Poppler, PyMuPDF, pdfplumber, MinerU, OpenDataLoader, baidu/Unlimited-OCR, and PaddleOCR remain external dependencies; the skill does not reimplement conversion engines.

## Privacy And Tool Policy

The default policy is local-first. The agent must diagnose and try suitable local tools before using any network or API service.

Online processing is allowed only after explicit user confirmation, because it may upload PDF content. This applies to MinerU API, OpenDataLoader hybrid or remote backends, Baidu AI Studio PaddleOCR, or any similar service.

## Tool Routing

The skill uses intelligent routing:

- Text-layer PDFs: prefer lightweight local tools such as Poppler, PyMuPDF, pdfplumber, pypdf, or pdfminer.six.
- Complex academic layout: prefer MinerU or OpenDataLoader when available.
- Scanned or image-heavy PDFs: prefer local OCR-capable tools first, including MinerU local modes, OpenDataLoader local modes, or baidu/Unlimited-OCR.
- Difficult long-document OCR: consider baidu/Unlimited-OCR as a local candidate when installed and the machine has suitable resources.
- Online fallback: after user approval, consider MinerU API, OpenDataLoader hybrid, or Baidu AI Studio PaddleOCR.

## Output Contract

Each source PDF gets one independent output folder. The expected structure is:

```text
<paper-slug>/
├── raw.md
├── clean.md
├── metadata.json
├── quality-report.md
├── assets/
└── samples/
```

`raw.md` preserves the converter's closest Markdown representation. `clean.md` is a research-reading version with frontmatter, title, abstract, keywords, table of contents, cleaned section hierarchy, figure/table index, formula notes where possible, references, and a cleaning log. `metadata.json` records source path, tool decisions, page count, detected PDF type, output paths, and quality summary. `quality-report.md` records structural and sampled page checks.

## Cleaning Standard

The clean Markdown should be suitable for scholarly reading and later literature review. It should remove obvious page headers, footers, repeated page numbers, broken line wraps, and duplicated running titles while preserving author claims and wording.

The agent must not invent missing paper content. When formulas, tables, figures, references, or pages appear incomplete, it should mark the issue in `clean.md` and `quality-report.md`.

## Quality Standard

Quality checking uses sampled comparison. The skill should check that:

- output files exist and are non-empty;
- title, abstract, keywords, section headings, figures, tables, formulas, and references are visible when present in the PDF;
- Markdown does not contain obvious OCR garbage, excessive mojibake, broken hyphenation, repeated headers, or repeated footers;
- sampled first, last, and middle pages are compared against extracted or rendered PDF text where tools allow;
- unresolved risks are documented in `quality-report.md`.

## User Experience

The agent should be concise and decisive:

1. Diagnose the PDF.
2. Explain the selected tool path briefly.
3. Ask before any online/API upload.
4. Produce the folder contract.
5. Run quality checks.
6. Report output paths and remaining risks.

## Non-Goals

The skill does not provide a full citation manager, full paper-summary pipeline, or complete literature-review system. It may produce reading-friendly metadata and indexes, but deeper paper interpretation belongs to separate literature reading or academic writing skills.
