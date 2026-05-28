# Academic Ref Inserter — Cline Rules

Cline (VS Code extension) reads `.clinerules` files for project-level AI instructions.

## Project Overview
Academic Reference Inserter: Insert, format, and cross-reference academic citations
in Word (.docx) documents. Supports GB/T 7714-2015, IEEE, and APA 7th.

## CLI Reference
```
python scripts/insert_refs.py analyze   --input paper.docx --json
python scripts/insert_refs.py fix       --input paper.docx --format gbt7714
python scripts/insert_refs.py reformat  --input paper.docx --format ieee
python scripts/insert_refs.py validate  --input paper.docx --format gbt7714 --json
```

## Formats
- `gbt7714`: GB/T 7714-2015 (Chinese standard, sequential [1])
- `ieee`: IEEE (engineering/CS, sequential [1])
- `apa7`: APA 7th (social sciences, author-year alphabetical)

## Key Files
- `scripts/insert_refs.py`: Main CLI entry point
- `scripts/formats/`: Citation format implementations
- `scripts/utils/docx_utils.py`: Word document utilities

## Requirements
```bash
pip install python-docx
```

Python 3.8+. See AGENTS.md for all platform details.
