# Academic Reference Inserter

> **Insert, format, and cross-reference academic citations in Word documents.**  
> Supports Chinese (GB/T 7714-2015) and international (IEEE, APA 7th, Chicago, MLA, Harvard) standards.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXX-blue)](https://doi.org/10.5281/zenodo.XXXXXX)

---

## Features

- **Format detection** - Auto-detects citation style from existing references
- **Multi-format support** - GB/T 7714-2015 (Chinese), IEEE, APA 7th, Chicago, MLA, Harvard
- **DOI auto-fetch** - Generate formatted references from DOI via CrossRef API
- **BibTeX import/export** - Convert between .docx references and .bib files
- **Interactive console** - Interactive CLI mode for quick operations
- **Cross-reference hyperlinks** - All `[N]` citations become clickable links to bibliography
- **Validation** - Checks orphan/missing refs, sequential ordering, recency, duplicates
- **Full pipeline** - One command to analyze, reformat, reorder, hyperlink, and validate
- **Safe** - Automatic backup before any modification

## Supported Formats

| Format | Region | Common In | Citation Style | Ordering |
|--------|--------|-----------|---------------|----------|
| **GB/T 7714-2015** | China | 计算机工程与应用, 自动化学报 | `[1]` | Sequential |
| **IEEE** | International | Engineering, CS journals | `[1]` | Sequential |
| **APA 7th** | International | Psychology, Education, Business | `(Author, Year)` | Alphabetical |
| **Chicago 17th** | International | Humanities, History | Footnotes/Bib | Alphabetical |
| **MLA 9th** | International | Literature, Arts | `(Author Pg)` | Alphabetical |
| **Harvard** | International | UK/Australia, Social Sci | `(Author, Year)` | Alphabetical |

## Installation

```bash
# Clone the repository
git clone https://github.com/linfewngfeng/academic-ref-inserter.git
cd academic-ref-inserter

# Install dependencies
pip install python-docx
```

## Usage

### Quick Start (Full Pipeline)

```bash
# One command to do everything
python scripts/insert_refs.py fix --input paper.docx --format gbt7714
```

### Step-by-Step

```bash
# 1. Analyze current state
python scripts/insert_refs.py analyze --input paper.docx

# 2. Reformat to target style
python scripts/insert_refs.py reformat --input paper.docx --format ieee

# 3. Reorder references to match citation order
python scripts/insert_refs.py reorder --input paper.docx

# 4. Add cross-reference hyperlinks (Ctrl+Click to jump)
python scripts/insert_refs.py hyperlink --input paper.docx

# 5. Validate
python scripts/insert_refs.py validate --input paper.docx --format gbt7714
```

### Format Options

```bash
# Chinese national standard
python scripts/insert_refs.py fix --input paper.docx --format gbt7714

# IEEE (engineering / CS)
python scripts/insert_refs.py fix --input paper.docx --format ieee

# APA 7th (social sciences)
python scripts/insert_refs.py fix --input paper.docx --format apa7
```

## Example

**Before** (raw docx with unformatted citations):

```
PM2.5 has been studied extensively [4]. Recent work [1][2] shows...
```

**After** (GB/T 7714 formatted with hyperlinks):

```
PM2.5 has been studied extensively [4]. Recent work [1][2] shows...

References:
[1] Wang Y, Wu H, Dong J, et al. TimeXer: Empowering transformers...[J]. NeurIPS, 2024.
[2] Liu Y, Hu T, Zhang H, et al. iTransformer: Inverted transformers...[J]. arXiv, 2023.
...
```

Each `[N]` in the text becomes a **blue clickable hyperlink** that jumps to the bibliography entry (Ctrl+Click in Word).

## Project Structure

```
academic-ref-inserter/
├── SKILL.md                    # AI assistant skill definition (Trae)
├── .cursorrules                # Cursor project rules
├── .cursor/rules/*.mdc         # Cursor 0.45+ rules
├── CLAUDE.md                   # Claude Code config
├── .github/copilot-instructions.md # GitHub Copilot config
├── .windsurfrules              # Windsurf config
├── CONVENTIONS.md              # Aider config
├── .continue/config.json       # Continue.dev config
├── AGENTS.md                   # Unified AI compatibility guide
├── opencode.json                # OpenCode config
├── GEMINI.md                     # Gemini CLI config
├── AMAZON_Q.md                   # Amazon Q Developer config
├── .clinerules                   # Cline rules
├── .kimi/skills/*/SKILL.md     # Kimi Code CLI skill
├── .qwen/skills/*/SKILL.md     # Qwen Code skill
├── README.md                   # This file
├── pyproject.toml               # Python packaging config
├── requirements.txt             # Runtime dependencies
├── requirements-dev.txt         # Dev dependencies
├── LICENSE                     # MIT License
├── scripts/
│   ├── insert_refs.py          # Main CLI entry point
│   ├── formats/
│   │   ├── base.py             # Abstract base format class
│   │   ├── gbt7714.py          # GB/T 7714-2015 implementation
│   │   ├── ieee.py             # IEEE implementation
│   │   ├── apa7.py             # APA 7th implementation
│   │   ├── chicago.py          # Chicago 17th implementation
│   │   ├── mla.py              # MLA 9th implementation
│   │   └── harvard.py          # Harvard implementation
│   └── utils/
│       ├── docx_utils.py       # Word document manipulation
│       ├── parser.py           # Reference parser
│       ├── validator.py        # Reference validator
│       ├── doi_lookup.py       # CrossRef DOI/title lookup
│       └── bibtex.py           # BibTeX import/export
├── examples/                   # Usage examples
└── tests/                      # Test suite
    ├── test_formats.py
    ├── test_validator.py
    ├── test_bibtex.py
    └── test_new_formats.py
```

## Validation Checks

After running, the tool verifies:

- [x] All citations in text have matching bibliography entries
- [x] All bibliography entries are cited in text
- [x] Sequential numbering has no gaps/duplicates
- [x] At least 15 references (journal paper minimum)
- [x] At least 50% from last 5 years
- [x] Each entry has proper type tag [J]/[M]/[C]/[D]
- [x] Author names formatted correctly for target style
- [x] Cross-reference hyperlinks work

## Running Tests

```bash
cd tests
python test_formats.py
```

## Integration with AI Code Assistants

This project supports **all major AI coding assistants** with automatic configuration detection:

| Assistant | Config File | Auto-Detected |
|-----------|------------|---------------|
| **Cursor** | `.cursorrules` + `.cursor/rules/*.mdc` | ✅ |
| **Claude Code** | `CLAUDE.md` | ✅ |
| **GitHub Copilot** | `.github/copilot-instructions.md` | ✅ |
| **Windsurf** | `.windsurfrules` | ✅ |
| **Aider** (v0.73+) | `CONVENTIONS.md` | ✅ |
| **Continue.dev** | `.continue/config.json` | ✅ (VS Code) |
| **OpenAI Codex CLI** | `AGENTS.md` | ✅ |
| **Kimi Code CLI** (月之暗面) | `.kimi/skills/*/SKILL.md` + `AGENTS.md` | ✅ |
| **Qwen Code** (通义千问) | `.qwen/skills/*/SKILL.md` | ✅ |
| **OpenCode** | `opencode.json` + `AGENTS.md` | ✅ |
| **OpenClaw** (小龙虾) | `~/.openclaw/workspace/` | 需手动配置 |
| **Gemini CLI** | `GEMINI.md` | 手动指定 |
| **Amazon Q Developer** | `AMAZON_Q.md` | VS Code 扩展 |
| **Cline** | `.clinerules` | VS Code 扩展 |
| **Trae** | `SKILL.md` | ✅ |

All CLI commands support `--json` for structured JSON output that AI agents can parse reliably.

See [AGENTS.md](AGENTS.md) for detailed compatibility information.

## Contributing

Contributions are welcome! Areas for improvement:

- Add more citation formats (Chicago, Harvard, Vancouver)
- Support for `.bib` / LaTeX interop
- Support for `.tex` files
- GUI / web interface
- More reference validation rules

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{academic_ref_inserter_2026,
  author = {Academic Ref Inserter Contributors},
  title = {Academic Reference Inserter},
  year = {2026},
  url = {https://github.com/linfewngfeng/academic-ref-inserter}
}
```
