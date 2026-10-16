# Source diagnosis and preservation

| Input | Main work | Boundary |
|---|---|---|
| Slides only | Inspect figures/equations; supply missing prerequisites and links | Do not claim additions were spoken in class |
| Transcript only | Repair evidenced dictation errors; retain explanations, examples, Q&A and administration | A plausible term is not proof of the intended word |
| Handwritten fragments | Inspect visually; expand supported abbreviations; recover dependencies | Handwritten emphasis signals user interest, not low quality |
| Typed notes | Preserve sound structure; repair local gaps | Polished sources can still contain incorrect formulas |
| Mixed | One integrated content inventory; reconcile overlap/conflict | Neither slides nor speech is automatically correct |
| Minimal | Bounded thematic learning notes from reliable sources | Distinguish from reconstruction of a particular lecture |

Assess completeness, structure, reliability and explanatory depth alongside difficulty and user scope. Record decisions that change work. Chunking long sources is compatible with single-pass extraction; never rely on truncated tool output.

## Extraction

```sh
python scripts/extract_sources.py slides.pdf transcript.md --output /task-work/sources.json
```

The helper emits hashes and units located by PDF page, text line, DOCX paragraph (including table cells), or PPTX slide/speaker notes. `--reuse` accepts cached extraction only when source hash and extractor version match. It does not OCR or interpret images. Missing/unsupported inputs and extraction errors produce a nonzero exit, not silent omission.

Text extraction is an index, not the complete source of truth. Inspect diagrams, plots, handwritten symbols, equations, footnotes, headers and visual emphasis whenever text is insufficient. Distinguish PDF page index from printed numbering. Keep relative dates unless the lecture date establishes their meaning; do not resolve “last year” using today.

## Coverage ledger

Keep a small ledger in context; persist it for long/full-coverage or mixed-source tasks. Group by meaningful teaching unit, not every sentence/token:

```json
{"scope":"All supplied materials","units":[
  {"id":"u01","source":"slides.pdf","location":"PDF page 12","kind":"knowledge","meaning":"Claim including its assumption","status":"covered","destination":"3.2 Conditional success probabilities"},
  {"id":"u02","source":"transcript.md","location":"lines 71–75","kind":"experience","meaning":"Teacher-reported uncertain cost","status":"uncertain_retained","destination":"Company experience","reason":"Currency is not established"}
]}
```

Statuses: `covered`; `merged_duplicate` (give `merged_into` unit ID); `uncertain_retained` (destination/reason); `excluded_noncontent` (reason); `out_of_scope` (explicit scope justification); `missing` (delivery blocker). Kinds may include knowledge, formula, derivation, example, experience, opinion, exercise, question_answer, administration, noncontent. Merged duplicates must preserve the union of unique details/conditions.

Audit source → output for omissions and output → evidence for unsupported additions. Do not relabel omitted meaningful material as filler. Ledger consistency does not prove initial extraction completeness.

Preserve:

- Every distinct technical claim, variable meaning, equation, derivation, assumption, limitation and counterexample.
- Teaching examples, parameters, steps, results and purpose.
- Substantive student/teacher questions and answers; every exercise, option, answer and explanation. Attribute suspect classroom answers and add supported corrections.
- Company/research details, hardware counts, times, costs and uncertainty; anecdotes and forecasts stay attributed.
- Course sequence, projects, dates, durations, CA/exam connections and meaningful contact details. Keep ambiguous administration as unresolved, not inferred requirements.

## Correction and conflicts

Separate typographical repair from interpretation. Cross-check slides, speech, context and primary sources as needed. Fix high-confidence terms consistently. Preserve uncertain names, acronyms, versions, units and dates. Avoid global replacements of ambiguous words such as “world”, “room” or “Zoom”.

For material errors, record original claim/location → correction → evidence → effect on understanding. Keep the valid underlying teaching point. Verification of a related algorithm does not resolve an uncertain spoken model name.

Show source conflicts with locations; choose a version only with a reason. Do not average conflicting numbers, combine distinct worked examples, or privilege formal-looking slides automatically. Reconstructed omitted proof steps are supplements, not lecture content.

For full coverage retain unresolved meaningful source information with qualification. Omit only unsupported **new external** claims, genuine filler or explicitly out-of-scope content. If illegibility materially blocks completion, identify the exact passage and ask a focused question while continuing independent work.
