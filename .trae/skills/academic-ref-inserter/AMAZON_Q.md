# Academic Ref Inserter — Amazon Q Developer Configuration

## Project
Academic Reference Inserter — insert, format, and cross-reference academic citations in .docx.

## CLI Commands (all support --json)
```bash
python scripts/insert_refs.py analyze   --input paper.docx --json
python scripts/insert_refs.py fix       --input paper.docx --format gbt7714
python scripts/insert_refs.py reformat  --input paper.docx --format ieee
python scripts/insert_refs.py reorder   --input paper.docx
python scripts/insert_refs.py hyperlink --input paper.docx
python scripts/insert_refs.py validate  --input paper.docx --format gbt7714 --json
```

## Supported Formats
- `gbt7714`: GB/T 7714-2015 (Chinese)
- `ieee`: IEEE (Engineering/CS)
- `apa7`: APA 7th (Social Sciences)

## Requirements
```bash
pip install python-docx
```
Python 3.8+ required.
