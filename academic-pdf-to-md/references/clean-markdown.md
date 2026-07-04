# Clean Markdown Rules

Use these rules when creating `clean.md` from `raw.md` and converter artifacts.

## Required Structure

```markdown
---
title: ""
authors: []
year:
venue: ""
doi: ""
source_pdf: ""
conversion_route: ""
quality_status: ""
---

# Title

## Metadata

## Abstract

## Keywords

## Table of Contents

## Main Text

## Figures And Tables

## Formula Notes

## References

## Conversion Notes
```

Keep unknown metadata fields empty or mark them as `unknown`; do not fabricate them.

## Cleanup Rules

- Preserve academic claims, citations, numbers, and technical terms.
- Fix heading levels so paper title is `#`, major sections are `##`, and subsections are `###` or below.
- Remove repeated page headers, footers, page numbers, and running titles.
- Merge broken line wraps inside ordinary paragraphs.
- Keep references as a list even when formatting is imperfect.
- Keep tables in Markdown if faithful; otherwise keep a placeholder linking to extracted HTML/CSV/image artifacts.
- Keep formulas as LaTeX when available. If formulas are garbled, mark them with `[formula conversion uncertain]`.
- Keep figure and table captions near the relevant section when possible.
- Add page references only when the source route provides reliable page mapping.

## Figure And Table Index

Create a concise index when figures or tables are detected:

```markdown
## Figures And Tables

- Figure 1: caption or short description. Source: assets/...
- Table 1: caption or short description. Source: assets/...
```

If a figure/table is visible in sampled pages but missing from Markdown, report it in `quality-report.md`.

## Conversion Notes

End `clean.md` with notes such as:

```markdown
## Conversion Notes

- Raw converter: MinerU / PyMuPDF / ...
- Cleanup: removed repeated headers and repaired paragraph wraps.
- Unresolved: table 2 may need manual verification.
```

## Forbidden

- Do not summarize away content when the user asked for conversion.
- Do not invent missing references, DOI, author names, numbers, formulas, or tables.
- Do not hide low-quality extraction; flag it clearly.
