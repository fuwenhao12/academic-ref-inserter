# Academic Ref Inserter — GitHub Copilot Instructions

This project helps format, reorder, and cross-reference academic citations in Word (.docx) documents.

## Core Commands

- `python scripts/insert_refs.py analyze --input <file.docx> --json` — Analyze citation structure
- `python scripts/insert_refs.py fix --input <file.docx> --format gbt7714` — Full pipeline
- `python scripts/insert_refs.py fix --input <file.docx> --format ieee` — IEEE format
- `python scripts/insert_refs.py reformat --input <file.docx> --format apa7` — APA format
- `python scripts/insert_refs.py validate --input <file.docx> --format gbt7714 --json` — Validate

## Formats

- `gbt7714`: Chinese standard, sequential [1] numbering
- `ieee`: Engineering/CS, sequential [1] numbering
- `apa7`: Social sciences, author-year, alphabetical order

Always use `--json` for structured output that Copilot can parse.
