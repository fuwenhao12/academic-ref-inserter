# Contributing to Academic Ref Inserter

Thanks for your interest in contributing! This guide covers how to get started.

## Setup

```bash
git clone https://github.com/linfewngfeng/academic-ref-inserter.git
cd academic-ref-inserter
pip install -r requirements.txt -r requirements-dev.txt
```

## Running Tests

```bash
python tests/test_formats.py
python tests/test_validator.py
```

All 14 tests must pass before submitting a PR.

## Adding a New Citation Format

1. Create a new file in `scripts/formats/` (e.g., `vancouver.py`)
2. Extend `BaseFormat` and implement `format_journal`, `format_conference`, `format_book` at minimum
3. Add the format to `FORMATS` dict in `scripts/insert_refs.py`
4. Add tests in `tests/` verifying journal, book, and author formatting

## Code Style

- Python 3.8+ with type hints where practical
- 4-space indentation, max line length 110 (config in `pyproject.toml`)
- Use `_emit()` and `--json` for all CLI output

## Pull Request Checklist

- [ ] All tests pass (`python tests/test_formats.py && python tests/test_validator.py`)
- [ ] New format has tests covering journal, book, and author output
- [ ] CLI `--json` output is properly structured
- [ ] Updated `FORMATS` dict and `--format` choices in the parser

## Questions?

Open an issue on GitHub or refer to `AGENTS.md` for multi-agent usage.
