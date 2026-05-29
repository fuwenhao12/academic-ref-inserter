# Academic Ref Inserter — Aider Conventions

## Project Context
This project provides tools to insert, format, and cross-reference academic citations in Word (.docx) documents. It supports Chinese (GB/T 7714-2015) and international (IEEE, APA 7th) citation styles.

## Key Files
- `scripts/insert_refs.py` — Main CLI entry point
- `scripts/formats/` — Citation format implementations
- `scripts/utils/` — Document utilities and validation
- `tests/test_formats.py` — Test suite

## Commands
Use `python scripts/insert_refs.py <command> --input <file.docx> [--format <name>] [--json]`
- `fix` — Full pipeline (always prefer this)
- `analyze` — Examine document structure
- `check-refs` — Auto-detect references and verify citation status (cited / not cited)
  Options: `--report FILE` (export detailed report to .txt or .md)
- `auto-find` — Auto-search CrossRef and insert relevant references into the document
  Options: `--query TITLE`, `--max-results N`, `--no-interactive`
- `reformat` — Change citation format
- `validate` — Check consistency

## Format Names
`gbt7714` (Chinese), `ieee` (Engineering), `apa7` (Social Sciences)

## Testing
`python tests/test_formats.py` — Run unit tests
