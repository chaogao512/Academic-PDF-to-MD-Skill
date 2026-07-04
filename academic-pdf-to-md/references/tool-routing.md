# Tool Routing

Use this reference after diagnosis, especially when the first route fails.

## Local-First Policy

Start with local tools. Use online/API tools only after the user confirms that uploading the PDF or rendered pages is acceptable.

## Tool Matrix

| Situation | Preferred tools | Notes |
|---|---|---|
| Fast metadata and text check | `pdfinfo`, `pdftotext`, PyMuPDF | Best first pass. |
| Text-layer academic PDF | Poppler, PyMuPDF, pdfminer.six, pypdf | Use PyMuPDF or pdfminer.six when Poppler output is messy. |
| Tables and coordinates | pdfplumber, PyMuPDF | Good for checking table regions and layout. |
| Complex academic layout | MinerU, OpenDataLoader | Prefer when formulas, figures, tables, and sections matter. |
| Scanned/image-heavy PDF | MinerU local, OpenDataLoader local, baidu/Unlimited-OCR | Render pages first if the OCR tool expects images. |
| Long-document OCR on local machine | baidu/Unlimited-OCR | Consider when installed and the machine has suitable GPU/resources. |
| Online fallback | MinerU API, OpenDataLoader hybrid/remote, Baidu AI Studio PaddleOCR | Ask before upload. |

## Decision Rules

1. If diagnosis shows a dense text layer and ordinary layout, start with Poppler or PyMuPDF.
2. If headings, tables, figures, formulas, or references are badly structured, try MinerU or OpenDataLoader.
3. If text density is very low or pages are image-heavy, use OCR. For local OCR, consider MinerU/OpenDataLoader local modes or baidu/Unlimited-OCR.
4. If local routes fail and the paper is not sensitive, ask whether online processing is allowed.
5. Record every attempted route in `metadata.json` and `quality-report.md`.

## Tool Notes

### Poppler

Use `pdfinfo` for page count and metadata, `pdftotext` for quick text extraction, and `pdftoppm` for sampled page rendering.

### PyMuPDF

Use when fast page text, block extraction, image extraction, or rendered page previews are needed. It is a strong local fallback if Poppler is not installed.

### pdfplumber

Use when tables, character coordinates, or layout-sensitive checks matter. It is useful for verifying whether table content exists before trying a heavier parser.

### MinerU

Use for academic PDFs with formulas, tables, OCR needs, and complex layout. Prefer local or token-free options when they satisfy the task. Treat API modes as upload-based and ask first.

### OpenDataLoader

Use when Markdown/JSON/HTML output, bbox-style structure, accessibility/tagged PDF information, or RAG-ready output is important. Treat hybrid or remote modes as upload-based and ask first.

### baidu/Unlimited-OCR

Use as a local OCR candidate for long documents or image-heavy PDFs when installed. If it expects page images, render PDF pages into `samples/` or `assets/pages/` first, then run the tool according to its current README. Record model, runtime, and page range.

Project: https://github.com/baidu/Unlimited-OCR

### Baidu AI Studio PaddleOCR

Use as an online/service fallback for OCR or document parsing when the user approves upload. It can be considered when local OCR quality is poor or local resources are insufficient. Record that an online service was used.

Service: https://aistudio.baidu.com/paddleocr
Project: https://github.com/PaddlePaddle/PaddleOCR

## Failure Handling

If one route fails:

- keep partial artifacts;
- record the command/tool and failure mode;
- try a route with different assumptions, such as text-layer extraction versus OCR;
- do not silently replace `raw.md` without preserving the failed route in metadata or notes.
