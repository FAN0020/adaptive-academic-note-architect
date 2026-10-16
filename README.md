# Adaptive Academic Note Architect v2.0

A Codex skill for turning lecture slides, transcripts, handwritten notes, and mixed academic materials into comprehensive, coherent, source-grounded study notes.

自适应学术笔记架构：保留材料中的全部可恢复有效信息，重建知识之间的逻辑联系，以紧凑、易读的形式形成能够独立理解的学习笔记。

## What it does

- **Preserves meaningful details:** explanations, equations, derivations, assumptions, examples, caveats, questions, exercises, and course information.
- **Builds conceptual connections:** explains What, Why, How, When, and relationships where needed, without forcing a repetitive template.
- **Separates information:** core knowledge, practical/company experience, course administration, and significant corrections or uncertainties.
- **Keeps evidence traceable:** distinguishes source material, corrections, grounded explanations, verified external additions, and unresolved claims.
- **Makes notes easy to scan:** underlines conclusion clauses and uses descriptive headings. A page-numbered table of contents is required by default above 10 rendered pages, conditional at 6–10 pages, and usually omitted at 5 pages or fewer.
- **Adapts effort:** Light, Standard, and Deep modes control processing depth independently of output length. References and research load only when needed.

Default output uses Chinese explanations with English technical terminology, comprehensive coverage, and compact layout. Language, format, and other preferences can be overridden in the request. Long notes normally use DOCX; font and layout checks must reflect the actual rendering environment.

## Install in Codex

Clone into your personal skills directory. Choose an unused destination; do not overwrite an existing installation.

```sh
git clone https://github.com/FAN0020/adaptive-academic-note-architect.git "${CODEX_HOME:-$HOME/.codex}/skills/adaptive-academic-note-architect"
```

The repository root contains the skill entry point, [SKILL.md](SKILL.md). The skill supports automatic selection as well as explicit invocation.

## Use

Attach or identify your course files, then ask:

```text
$adaptive-academic-note-architect
请根据这些课件与课堂转写整理完整学习笔记。使用中文解释和英文术语，
保留全部有效课堂信息，分开知识、行业经验与课程事项，并给结论句加下划线。
```

For a later formatting change, identify the latest accepted document. The skill preserves its content and checks only the affected formatting and navigation.

## Helper scripts

The skill's instructions work independently of the optional Python helpers. For helpers, use the environment's configured dependencies or install them into a virtual environment. They were tested with Python 3.12.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/test_helpers.py
```

| File | Purpose |
|---|---|
| `scripts/extract_sources.py` | Extract located text from PDF, DOCX, PPTX, and text files; reuse unchanged sources by hash |
| `scripts/apply_underlines.py` | Apply exact, manually selected DOCX underline spans while checking content preservation |
| `scripts/validate_output.py` | Check structural properties, coverage-ledger consistency, and TOC pages/links against a rendered PDF |
| `scripts/test_helpers.py` | Run regression checks using synthetic fixtures |
| `references/` | Load detailed source-processing, writing, research, architecture, QA, and output guidance as needed |
| `assets/academic-notes-style.json` | Adaptable typography and layout defaults |

Run a helper with `--help` for its interface. See [output guidance](references/output-formats.md) for underline selections and [quality assurance](references/quality-assurance.md) for validation examples.

## Verification boundaries

The automated tests cover helper behavior, including content preservation, unsafe span rejection, extraction, caching, and TOC thresholds/navigation. They do not certify semantic completeness, citation truth, teaching quality, or visual rendering. Those require source review and the skill's content/evidence and pedagogical audits. DOCX/PDF rendering requires suitable tools in the execution environment; no rendering engine or fonts are bundled. Scanned or handwritten content requires visual interpretation or OCR outside the text extraction helper.
