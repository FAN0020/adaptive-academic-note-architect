# Output, navigation and typography

## Select the output

Honor the requested format and latest accepted artifact. Short notes can be Markdown; long complete lecture notes default to DOCX. Do not create a Markdown file merely because prose was drafted internally; use the appropriate saving workflow when needed. Preserve original sources and prior deliverables unless overwrite is explicitly requested. Use clear output names and deliver only final requested artifacts.

Use the available documents/PDF skills for actual file creation/rendering. Resolve bundled dependencies through the environment instead of hardcoding versioned installation paths into this skill. If unavailable, use supported equivalents and disclose unperformed checks.

## Underline implementation

DOCX: native `w:u` single black underline on selected runs, preserving fonts, bold/italic, superscripts, links, bookmarks and native equations. Split runs only at exact semantic boundaries. Do not replace equations with flattened text to apply emphasis.

For existing DOCX files, select spans manually after reading paragraphs; the helper does not decide what is a conclusion. Locate paragraphs with `extract_sources.py` (zero-based **all** `word/document.xml` paragraph order, including tables). Example selection file:

```json
[
  {
    "paragraph_index": 12,
    "expected_text": "A complete paragraph copied exactly from extraction.",
    "spans": [{"text": "complete paragraph", "occurrence": 1}]
  }
]
```

`expected_text` is optional but recommended to prevent applying stale indices. `occurrence` is one-based and needed only for intentionally repeated exact text. Unsupported/ambiguous spans fail without writing output; do not use fuzzy matching.

```sh
python scripts/apply_underlines.py existing.docx selections.json --output underlined.docx
```

The helper does not overwrite its input, edit prose, choose spans or remove existing emphasis. It rejects headings, field/hyperlink/math/drawing overlaps instead of damaging them. Use a carefully scoped document workflow for unsupported structures. Afterward validate exact content, render and inspect. Existing underlines need not be duplicated.

Markdown: use `<u>summary sentence</u>` only if the intended renderer supports inline HTML underlining; `__text__` is bold, not underline. Never simulate with combining Unicode underline characters. If underlining is essential but unavailable, prefer DOCX when format is flexible; with an explicit Markdown-only constraint disclose the rendering limit and retain portable HTML markup. Do not silently substitute bold.

## Table of contents

Use final rendered page count (not words, PDF slide count, or XML `lastRenderedPageBreak`). Count all pages in the delivered document, including front matter and references; recheck after adding a TOC.

| Actual pages | Default |
|---|---|
| 1–5 | Usually no TOC; include if explicitly requested |
| 6–10 | Include if structure is complex enough to aid repeated lookup |
| 11+ | Must include TOC unless the user explicitly opts out |

Complexity indicators include multiple independent parts (knowledge, experience, exercises, administration), several major sections, a dense two-level hierarchy or frequent cross-reference use. These are judgment criteria, not a score the user must choose. Document the decision internally. For an unpaginated output use heading anchors if useful; never fabricate page numbers. If page-indexed navigation is requested, use a paginated deliverable.

Practical workflow:

1. Establish meaningful Heading 1/2 styles and unique bookmarks; avoid indexing every minor paragraph.
2. Render the body draft to determine the TOC requirement. Reserve a compact contents page when clearly long.
3. Build a native TOC and materialize fields through a renderer that updates them, or a static TOC with verified bookmark links and page numbers. A static TOC is acceptable; do not call it auto-updating.
4. Render with the TOC, obtain actual heading positions, update numbers, and render again if changed. Do not assume adding a page shifts all headings by exactly one.
5. Check each entry against the final heading page, printed footer numbering and bookmark/link destination. PDF annotation arrays may be in reverse visual order; match by coordinates/label, not array order.
6. Any later layout/content change invalidates old pagination until rechecked. Formatting-only edits may preserve pagination, but verify rather than assume.

For 6–10-page simple structure omit a TOC if it adds more friction than value. For 11+ pages retain all valid content and add navigation; do not delete content to fall below the threshold. A TOC need not be squeezed into a single page at the expense of readability.

## Typography and fonts

Use the optional `assets/academic-notes-style.json` profile as a starting point, not an immutable template. Preserve existing good user-approved styling. A4, roughly 20 mm margins, 11 pt body, modest paragraph spacing, clear black headings and comfortable line spacing are reasonable defaults. Use tables only for comparisons, metrics, repeated records and structured mappings; avoid equal-width columns that cramp explanation text.

Choose attractive CJK-capable fonts supported by the actual environment. Preferred candidates include Source Han Serif/Sans or Noto Serif/Sans CJK, with locally verified macOS alternatives such as Songti SC or PingFang SC. Names can vary by internal font family name; inspect installed font metadata. Configure both Latin and East Asian font slots. Do not assume a font displayed in one Mac app will work in Codex's built-in preview.

If a target preview fails to load fonts, test a short bilingual probe, choose a working family or embed redistributable fonts with permitted embedding rights, then render the complete document. Embedding is optional and format-dependent; declaring a font is not embedding it. Avoid hardcoded paths to temporary fonts or silently downloading/bundling proprietary fonts. Use only fonts whose licensing permits the intended use. Verify CJK, Latin, mathematical symbols, superscripts, tables and bold text. Do not claim target-preview compatibility based solely on another renderer; report the actual scope of verification if relevant.

Keep equations native/editable when practical, with defined notation and readable size. Do not trade technical fidelity for compactness. Apply “keep with next” to headings, repeat table headers where needed, and avoid stranded headings or clipped table rows.

## Delivery

Final message: link/attach the requested notes, state what changed, and give a short verified QA/limitations statement. Do not attach extraction manifests, coverage ledgers, execution traces, font probes, QA PDFs or PNGs unless requested. A summary of completeness is bounded by supplied materials, not all words ever spoken in class.
