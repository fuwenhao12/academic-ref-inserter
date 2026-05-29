# Academic Ref Inserter — Cursor Project Rules

This project provides tools for inserting, formatting, and cross-referencing academic citations in Word (.docx) documents.

## Core CLI

```bash
# Full pipeline (analyze -> reformat -> reorder -> hyperlink -> validate)
python scripts/insert_refs.py fix --input paper.docx --format gbt7714 --json

# Individual steps (all support --json for machine-readable output)
python scripts/insert_refs.py analyze   --input paper.docx --json
python scripts/insert_refs.py reformat  --input paper.docx --format ieee
python scripts/insert_refs.py reorder   --input paper.docx
python scripts/insert_refs.py hyperlink --input paper.docx
python scripts/insert_refs.py validate  --input paper.docx --format gbt7714
```

## Supported Formats

| Flag | Style | Region | Ordering |
|------|-------|--------|----------|
| `gbt7714` | GB/T 7714-2015 | China | Sequential [1][2] |
| `ieee` | IEEE | International (CS/Eng) | Sequential [1][2] |
| `apa7` | APA 7th | International (Social Sci) | Alphabetical |

## Key Files

- `scripts/insert_refs.py` — Main CLI (primary entry point)
- `scripts/formats/` — Citation format implementations
- `scripts/utils/docx_utils.py` — Word document manipulation
- `.trae/skills/academic-ref-inserter/SKILL.md` — Full documentation

## Workflow for AI Agents

1. Always run `analyze --json` first to understand the document state
2. Choose format based on user's target journal
3. Run `fix --format <name>` for the full pipeline
4. Validate with `validate --json`
5. Provide summary to user

## Installation

```bash
pip install python-docx
```
