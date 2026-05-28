# Academic Reference Inserter (academic-ref-inserter)

Insert, format, and cross-reference academic citations in Word (.docx) documents.
Supports GB/T 7714-2015 (Chinese), IEEE, and APA 7th citation styles.

## Quick Start

```bash
cd academic-ref-inserter
pip install python-docx

# Full pipeline
python scripts/insert_refs.py fix --input paper.docx --format gbt7714 --json

# Or step by step
python scripts/insert_refs.py analyze   --input paper.docx --json
python scripts/insert_refs.py reformat  --input paper.docx --format ieee
python scripts/insert_refs.py reorder   --input paper.docx
python scripts/insert_refs.py hyperlink --input paper.docx
python scripts/insert_refs.py validate  --input paper.docx --format apa7 --json
```

## Supported Formats

| Flag | Style | Ordering |
|------|-------|----------|
| `gbt7714` | GB/T 7714-2015 (Chinese) | Sequential [1] |
| `ieee` | IEEE (Engineering/CS) | Sequential [1] |
| `apa7` | APA 7th (Social Sciences) | Alphabetical (Author, Year) |

## CLI Reference

All commands accept `--json` for machine-readable JSON output.

### `analyze`
Analyzes the document structure — extracts citations, references, and detects issues.
Output: total refs, citation order, sequential check, orphan/missing refs.

### `reformat --format <name>`
Reformats all references to the target citation style.

### `reorder`
Renumbers references to match first-citation order in text.

### `hyperlink`
Adds bookmarks to bibliography entries and converts all [N] citations to clickable hyperlinks.

### `validate --format <name>`
Validates: orphan/missing refs, sequential numbering, type tags, recency, duplicates.

### `fix --format <name>`
Full pipeline: analyze → reformat → reorder → hyperlink → validate.

## Architecture

```
scripts/
├── insert_refs.py    Main CLI entry point
├── formats/
│   ├── base.py       Abstract base class
│   ├── gbt7714.py    GB/T 7714-2015
│   ├── ieee.py       IEEE
│   └── apa7.py       APA 7th
└── utils/
    ├── docx_utils.py Word document utilities
    ├── parser.py     Reference text parser
    └── validator.py  Validation logic
```
