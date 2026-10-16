# Compact, independently understandable notes

Write connected paragraphs explaining causes, mechanisms and dependencies. Merge repeated material while retaining unique detail/qualifications. Keep teaching examples by their concepts; separate company/research experience with cross-references to its technical lesson. Keep administration separate. Omit absent sections, not meaningful content.

Introduce context before advice: “在考虑模型微调之前，应优先排查 Prompt、Tool Schema 或其他推理时工程能否解决性能问题，以避免不必要的训练成本” is clearer than “先排查便宜且直接的修复”. Use precise subjects and conditions; avoid vague comparisons and mechanical translation.

Use prose for explanations, lists for parallel points/steps, tables for comparisons/repeated records. Do not line-break every sentence or put prose in tables for decoration. Definitions can be inline; difficult concepts need adequate explanation. Compact layout is not a page cap.

## Bilingual terminology

Default bilingual mode supports reading Chinese explanations while recognizing the terminology in English slides, papers and questions. Honor explicit language and terminology-density preferences; this mode does not require duplicating every sentence in two languages.

- Introduce a technical concept with its Chinese name, English name and useful acronym. Prefer the source's English spelling and distinctions; do not invent an expansion for an ambiguous acronym. A translation added by the notes is not a verbatim source quotation.
- Keep English available locally: reintroduce the English term at the first substantive use in each relevant section, and retain it where a later comparison or takeaway depends on recognizing that term. Once the local mapping is clear, either Chinese–English pairs or the established English term within Chinese prose can be used naturally. A single definition early in a long document is insufficient.
- Give terminology-bearing headings, comparison axes, component names, diagram labels and exercise terms/options an English counterpart where it helps match the source. Preserve source identifiers, method names and option wording; explanations and answer rationales should use the same terms. Ordinary prose headings and everyday words do not need mechanical translation.
- For example, after introducing 状态（State）、观察（Observation）and 反馈（Feedback）, a later explanation can say “Observation 更新 State，再作为 Feedback 影响下一步决策.” Avoid a later all-Chinese comparison that makes the reader search earlier pages for these mappings.
- An optional glossary can aid lookup but does not replace English in the relevant explanations and exercises. Judge coverage by whether the reader can match the concepts locally, not by an English-word quota. Avoid annotating every occurrence, long repeated expansions or an unchanged full sentence translated twice.

For a request to add more English terminology, enrich the current notes rather than replacing explanations with a glossary or shortening them. Preserve substantive content and source boundaries, then recheck affected tables, line wrapping, page numbers and TOC links.

## Underlined takeaways

For each substantive paragraph or coherent fragment, select an **existing** conclusion/generalization/summary conveying its point. Prefer one concise span; two only for distinct central ideas. Include conditions/caveats so scanning does not overstate evidence. Do not automatically underline the final sentence or only already-bold text.

- Theory: mechanism, defining distinction, condition or conclusion.
- Examples: what the result teaches, retaining calculations and assumptions in full.
- Company experience: transferable lesson or attributed/qualified judgment; not uncertain numbers presented as facts.
- Exercises: answer **reason**, not merely its letter; preserve prompts/options/answers/caveats. Repeated answer-key lines need no extra underline.
- Administration: meaningful arrangement with date/source uncertainty; no invented deadlines.
- Corrections: corrected distinction or uncertainty boundary.
- Equations, references, code, headings and structured tables need no underline in every item; a decisive table interpretation can be marked.

Do not underline whole paragraphs, isolated keywords or every important statement. Retain useful original bold but do not automatically bold all underlined passages. There is no numerical quota.

For format-only edits choose exact spans and change run formatting only. Do not add takeaway prose, revise claims or remove original emphasis. If no summary sentence exists, select the most informative supported clause. During an authorized rewrite a concise explanation may be added, but avoid a duplicate recap for every paragraph.

## Navigation and scanability

Use accurate titles naming topic plus mechanism/comparison/purpose, real heading hierarchy and defined acronyms. Avoid slogans, conversational headings and titles relying on prior-page context.

Read the sequence of headings and underlined statements: it should convey the framework without stripping qualifications. Then check that the full prose supplies reasoning/details. This is a scanability audit, not permission to reduce the document to highlighted text.

If a later user says “too long” while preserving a full-coverage requirement, first improve navigation, duplicates, sentences and spacing. Do not infer permission to delete valid information. An explicitly requested shorter summary must be labelled as such, without claiming every detail; preserve the complete version unless asked otherwise.
