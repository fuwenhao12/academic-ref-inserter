# Academic Ref Inserter — Gemini CLI Configuration

## Project
Academic Reference Inserter — format, reorder, and hyperlink citations in .docx documents.

## Tool Commands
```bash
python scripts/insert_refs.py analyze   --input paper.docx --json
python scripts/insert_refs.py fix       --input paper.docx --format gbt7714
python scripts/insert_refs.py reformat  --input paper.docx --format ieee
python scripts/insert_refs.py validate  --input paper.docx --format gbt7714 --json
python scripts/insert_refs.py reorder   --input paper.docx
python scripts/insert_refs.py hyperlink --input paper.docx
```

## Formats
- `gbt7714`: GB/T 7714-2015 (Chinese standard, sequential [1])
- `ieee`: IEEE (engineering/CS, sequential [1])
- `apa7`: APA 7th (social sciences, author-year alphabetical)

## Dependencies
```bash
pip install python-docx
```

Python 3.8+ required. See AGENTS.md for full documentation.
