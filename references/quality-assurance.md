# Risk-based QA and delivery gates

All modes perform both substantive audits. Scale the depth to risk, not the truth standard. For a formatting-only change, verify exact content preservation and the changed presentation; do not reopen already-verified academic claims without new evidence.

## Pass A Content and evidence

- Compare the inventory to output: every distinct meaningful point, example detail, assumption, equation/derivation, question/exercise, experience and administrative item is covered, legitimately merged, or retained as uncertain. Investigate unexplained gaps.
- Check meaning and qualification, especially numbers, units, causal claims, limits and corrected dictation. Recalculate pivotal worked examples.
- Verify evidence classes and citation support for substantive additions. Confirm sources support the exact claim, not merely the general topic.
- Keep anecdotes/opinions/forecasts attributed. Do not report full coverage of unavailable speech or unreadable material.

## Pass B Teaching logic and reading

- Prerequisites precede dependent ideas; important methods have motivation and sufficient mechanism/intuition.
- Transitions explain why the next topic is introduced. Definitions do not float without context.
- Headings accurately describe their contents and make sense in the TOC.
- In bilingual mode, read each major section and its exercises independently: can the learner match the key concepts to English source terminology without finding a definition several pages earlier? Check terminology-bearing headings, comparisons, component/diagram labels, takeaways and exercise options/rationales. Fix missing local mappings or inconsistent names; a glossary alone and an English-word count do not establish this.
- Underlined takeaways represent the paragraph, retain conditions/uncertainty, and remain a minority of the prose. Judge semantically; do not enforce a character quota.
- Preserve reasoning/detail while reducing duplicated explanations and needless line breaks. The notes should be understandable without reopening the sources.

## Severity and revision

Critical: wrong pivotal formula, fabricated citation, false central claim, missing essential source content. Major: missing prerequisite, misleading attribution, serious logical jump, broken navigation or unreadable font. Minor: awkward phrase, local duplication, heading or spacing refinement.

Fix Critical/Major issues or explicitly bound unresolved information; a qualification is appropriate only when the uncertainty cannot be responsibly resolved. Aim for at most two targeted revision rounds; this is not a hard cap allowing known errors. Recheck only affected dependencies except when final artifact rendering requires all pages. Stop after required gates pass.

## Deterministic helpers

```sh
python scripts/validate_output.py notes.docx --rendered-pdf /task-work/render/notes.pdf --coverage /task-work/coverage.json --report /task-work/check.json
python scripts/validate_output.py edited.docx --before previous.docx --rendered-pdf /task-work/render/edited.pdf
```

`--before` is for formatting-only edits: it checks paragraph text and native equation content across text-bearing DOCX parts. Do not use it to demand identical prose after authorized reconstruction. `--coverage` checks ledger schema, duplicate references/cycles and unaccounted units, **not** completeness of extraction or validity of the “meaning” field. TOC detection supports internal linked entries with Arabic page numbers; complex fields/layouts need the document workflow and manual verification.

The validator's `structural_checks_passed` is not overall QA. It cannot verify claim truth, quality of reasoning, semantic coverage, font appearance or whether the supplied PDF came from the final DOCX. Supply the actual final render, inspect its pages, and retain the report's file hashes for incremental work. No rendered PDF means no verified page count or page-number claim.

Page references are checked against physical pages by default. `--page-offset` handles a constant offset: printed page = physical page + offset. Mixed numbering schemes need manual checking and disclosure, not an invented offset. `--complex-structure yes|no` records the 6–10-page decision; `--toc off|required` is only for an explicit user override/request. Default `auto` implements the user's threshold.

## Artifact gate

Render the latest DOCX through the available documents skill. Inspect every page for clipping, glyphs, equations, tables, underlines and footers. Check heading/page correspondence, bookmark targets and actual link destinations. A successful text extraction or XML check does not replace visual inspection. Re-render after layout-changing edits and verify the final TOC again.

For font issues, distinguish installed/declared fonts from usable/embedded fonts in the target renderer. State which renderer was checked; do not claim Codex built-in preview was verified unless it actually was. Avoid exposing temporary QA PDFs/images by default.

## Behavioral regression scenarios

When changing this skill, exercise relevant cases without unnecessary new agents:

1. Three coherent pages, polish only: Light, no broad research or automatic TOC; complete content remains.
2. Mixed slides/transcript with a company anecdote, numeric conflict, all exercise options and an administrative ambiguity: one integrated note set; evidence-aware corrections; no lost details or invented deadlines.
3. Eleven rendered pages: TOC required with final page numbers and working links. Eight complex pages: deliberate TOC decision; five simple pages: normally none.
4. Underline-only follow-up: exact source text/equations/links preserved; no auto-generated summaries or changed pagination claims.
5. Slides only with missing prerequisites: necessary explanations marked as additions, no claim of full spoken coverage.
6. No external access, suspect central formula: retain/label uncertainty and limit claims; never invent verification.
7. “The English technical terms are too sparse; improve the current notes”: add consistent English mappings in the affected sections, comparisons and exercises while retaining Chinese explanations, all example details, formulas, options/answers and citations. Do not settle for a glossary or first-use-only definitions. Re-render changed layouts and verify the final TOC. An explicit Chinese-only request still overrides bilingual defaults.

Script tests cover observable invariants and failure behavior, not the wording of the skill. Re-run relevant scenarios only after changes affecting them.

Run `python scripts/test_helpers.py` after changing the helpers. It uses temporary synthetic files and does not alter course materials. Dependencies are the bundled `lxml`, `pypdf` and `reportlab`; PPTX extraction additionally uses `python-pptx`. Resolve available libraries through the workspace runtime rather than installing into managed environments.

## User-facing QA statement

Keep it short and specific: “已核对所提供材料的有效内容、纠错标注、目录页码和排版；两处口述数字仍标为待核实。” Only report checks/counts actually performed. Use “checked with limitations” where needed, never a blanket “passed” while important limitations remain. Internal plans/traces are not default deliverables.
