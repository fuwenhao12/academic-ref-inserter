# AI Coding Assistant Compatibility Guide

Academic Ref Inserter is designed to work with **all major AI coding assistants**.
Below is a quick reference for each platform.

---

## Compatibility Matrix

| Assistant | Config File | Auto-Detected | Since |
|-----------|------------|---------------|-------|
| **Cursor** | `.cursorrules` + `.cursor/rules/*.mdc` | ✅ | 0.45+ |
| **Claude Code** | `CLAUDE.md` | ✅ | v1.0 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | ✅ | 2025 |
| **Windsurf** | `.windsurfrules` | ✅ | Always |
| **Aider** | `CONVENTIONS.md` | ✅ | v0.73+ |
| **Continue.dev** | `.continue/config.json` | ✅ | VS Code ext |
| **OpenAI Codex CLI** | `AGENTS.md` | ✅ | v1.0 |
| **Kimi Code CLI** | `.kimi/skills/*/SKILL.md` + `AGENTS.md` | ✅ | v1.0 |
| **Qwen Code** | `.qwen/skills/*/SKILL.md` | ✅ | v0.16+ |
| **OpenCode** | `opencode.json` + `AGENTS.md` | ✅ | v1.0 |
| **OpenClaw (小龙虾)** | `~/.openclaw/workspace/` files | Manual setup | v2026 |
| **Gemini CLI** | `GEMINI.md` | Manual setup | v1.0 |
| **Amazon Q Developer** | `AMAZON_Q.md` | Auto (VS Code) | 2025 |
| **Cline (VS Code)** | `.clinerules` | Auto | v1.0 |
| **Trae** | `.trae/skills/*/SKILL.md` | ✅ | Built-in |

---

## Quick Start for Any AI Assistant

When you ask your AI coding assistant to "insert references" or "format citations",
the assistant will automatically detect this project and use the Academic Ref Inserter tool.

### Example Prompts

```
# Analyze citations in my paper
python scripts/insert_refs.py analyze --input paper.docx --json

# Full pipeline (recommended)
python scripts/insert_refs.py fix --input paper.docx --format gbt7714

# IEEE format
python scripts/insert_refs.py fix --input paper.docx --format ieee

# Validate only
python scripts/insert_refs.py validate --input paper.docx --format gbt7714 --json

# Reformat only (skip hyperlinks and reorder)
python scripts/insert_refs.py reformat --input paper.docx --format apa7
```

### JSON Output Mode

All commands support `--json` for structured output. AI assistants should always
use this flag for reliable parsing:

```bash
python scripts/insert_refs.py analyze --input paper.docx --json
```

Returns structured data like:
```json
{
  "command": "analyze",
  "total_refs": 25,
  "citation_order": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "sequential_ok": true,
  "orphan_refs": [],
  "missing_refs": [],
  "file_ok": true
}
```

---

## Platform-Specific Details

### Cursor

Two files control behavior:
- `.cursorrules` — Project-level instructions  
- `.cursor/rules/academic-ref-inserter.mdc` — Rule-based trigger for .docx files

Cursor automatically loads these when opening the project directory.

### Claude Code (Anthropic)

`CLAUDE.md` is read by the `claude` CLI when working in this project.  
Claude will know to use the `scripts/insert_refs.py` tool when asked about citations.

### GitHub Copilot

`.github/copilot-instructions.md` is read by Copilot in VS Code and
GitHub.com. Copilot will suggest the correct CLI commands for reference tasks.

### Windsurf (Codeium)

`.windsurfrules` is loaded automatically by Windsurf IDE.  
The AI will understand the tool's capabilities and commands.

### Aider

`CONVENTIONS.md` is auto-detected by Aider (v0.73+).  
Aider will respect the project conventions and use the scripts correctly.

### Continue.dev

`.continue/config.json` provides pre-configured commands that appear as
buttons in the Continue.dev VS Code extension sidebar.

### OpenAI Codex CLI

Codex CLI reads `AGENTS.md` from the project root (and nested directories
via its hierarchical discovery system). It also supports `~/.codex/AGENTS.md`
for global instructions.

Codex automatically finds this file when running `codex` in the project
directory. The `--json` flag is especially useful for Codex's structured
output parsing.

### Kimi Code CLI (Kimi Agent / 月之暗面)

Kimi Code CLI supports two discovery mechanisms:

**Project Skill (recommended):**
The skill at `.kimi/skills/academic-ref-inserter/SKILL.md` is auto-discovered
when running `kimi` in this project. The AI will know to use the tool when
citation tasks arise.

**AGENTS.md fallback:**
Kimi also reads `AGENTS.md` from the project root and merges it into the
system prompt via `${KIMI_AGENTS_MD}`.

Kimi also supports merging skills from `.claude/skills/` and `.codex/skills/`
when `merge_all_available_skills` is enabled (default: `true`).

### Qwen Code (QCoder / 通义千问编程智能体)

Qwen Code discovers project-level skills from `.qwen/skills/`:

```bash
# The skill is auto-discovered at:
.qwen/skills/academic-ref-inserter/SKILL.md
```

When the user mentions citations, references, or document formatting,
Qwen Code will automatically read this skill and use the CLI tool.

Personal installation (for all projects):
```bash
cp -r .qwen/skills/academic-ref-inserter ~/.qwen/skills/
```

### OpenCode

OpenCode loads `opencode.json` from the project root. This config:
- Registers 5 pre-configured commands (`analyze`, `fix-gbt7714`, `fix-ieee`, `fix-apa7`, `validate`)
- Defines an `academic-ref-inserter` agent with full tool access
- References `AGENTS.md`, `CONVENTIONS.md`, and `CLAUDE.md` as instruction sources

OpenCode also supports `.opencode/agents/` for custom agent definitions.

### OpenClaw (小龙虾)

OpenClaw is a general-purpose AI agent framework (not a coding CLI).  
To add Academic Ref Inserter capabilities to your OpenClaw instance:

1. **Add a custom skill** via ClawHub or create a skill file:
   ```
   ~/.openclaw/workspace/skills/academic-ref-inserter/SKILL.md
   ```

2. **Or update your SOUL.md** to include reference insertion as a capability:
   ```markdown
   ## Skills & Tools
   - Academic citation formatting: python scripts/insert_refs.py
   - Supports GB/T 7714, IEEE, APA 7th
   - Located at /path/to/academic-ref-inserter/
   ```

3. **Or use the AGENTS.md** file as a reference in your USER.md:
   ```
   When working with academic papers, reference the AGENTS.md
   file in the academic-ref-inserter project for citation formatting.
   ```

### Trae

`.trae/skills/academic-ref-inserter/SKILL.md` contains the full skill definition.
Trae invokes this skill when the user asks about reference insertion.

### Gemini CLI (Google)

`GEMINI.md` provides project-specific instructions accessible to the Gemini CLI
tool. Place this file in the project root or reference it in your session:

```bash
gemini "Read GEMINI.md and use the academic-ref-inserter tool to fix citations in paper.docx"
```

### Amazon Q Developer (AWS)

`AMAZON_Q.md` is detected by the Amazon Q Developer VS Code extension. Q will
automatically read project-level configuration files to understand tool usage.

### Cline (VS Code Extension)

`.clinerules` is auto-loaded by the Cline VS Code extension. The file defines
project-specific instructions including CLI commands and format options.

---

## Cross-Platform Skill Sharing

Thanks to the open Agent Skills format, many platforms can share the same
`SKILL.md` file. Kimi Code, Qwen Code, and Claude Code can all discover
skills from each other's directories when `merge_all_available_skills` is
enabled.

| Source Skill Dir | Discoverable By |
|-----------------|-----------------|
| `.kimi/skills/` | Kimi Code, Claude Code (merge), Codex CLI (merge) |
| `.qwen/skills/` | Qwen Code |
| `.claude/skills/` | Claude Code, Kimi Code (merge) |
| `.codex/skills/` | Codex CLI, Kimi Code (merge) |
| `.trae/skills/` | Trae |
| `.agents/skills/` | Kimi Code, Claude Code (generic group) |

---

## Installation

```bash
pip install python-docx
```

Python 3.8+ required.

---

## Project Structure

```
academic-ref-inserter/
├── .cursorrules                    # Cursor
├── .cursor/rules/*.mdc            # Cursor rules
├── CLAUDE.md                       # Claude Code
├── .github/copilot-instructions.md # GitHub Copilot
├── .windsurfrules                  # Windsurf
├── CONVENTIONS.md                  # Aider
├── .continue/config.json           # Continue.dev
├── opencode.json                   # OpenCode
├── GEMINI.md                       # Gemini CLI
├── AMAZON_Q.md                     # Amazon Q Developer
├── .clinerules                     # Cline
├── AGENTS.md                       # Codex CLI + unified guide (this file)
├── .kimi/skills/*/SKILL.md         # Kimi Code CLI
├── .qwen/skills/*/SKILL.md         # Qwen Code
├── .trae/skills/academic-ref-inserter/  # Trae (full skill definition)
├── README.md                       # GitHub documentation
├── LICENSE                         # MIT
├── scripts/
│   ├── insert_refs.py              # Main CLI (all agents)
│   ├── formats/                    # Citation style implementations
│   └── utils/                      # Document utilities
├── tests/
│   └── test_formats.py
└── examples/
```
