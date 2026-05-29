---
name: paper-spine
description: Orchestrates the PaperSpine suite for motivation-driven paper/report rewriting or building from materials.
---

# PaperSpine Orchestrator

Use this skill as the suite entrypoint. It routes the user to intake, research,
rewrite, build, LaTeX, and audit skills.

## Operating Principle

PaperSpine is a research-writing workflow, not a prose patcher. Its job is to
learn the target scene and strong examples first, force a user-confirmed
motivation, design the paper row by row, and only then write or rebuild the
manuscript.

Never fabricate data, metrics, p-values, datasets, citations, figures, or
experimental claims. User materials are authoritative for this paper's results.
External examples teach structure and rhetoric only.

## Required Configuration

Prefer reading `paper_rewriting_output/paper_spine_config.json`. If it is
missing, route to `paper-spine-intake` or ask the same fields directly.

Required fields:

| Field | Allowed Values |
|---|---|
| `workflow` | `rewrite_existing`, `build_from_materials` |
| `scene` | `journal`, `conference`, `report_review`, `competition` |
| `tier` | `flash`, `pro` |
| `output_language` | `en`, `zh` |
| `target_name` | free text |
| `materials_dir` | path or empty |
| `draft_path` | path or empty |
| `user_motivation` | free text or empty |
| `official_urls` | list |
| `special_requirements` | list |
| `word_output` | `none`, `docx` |
| `translation_package` | `none`, `zh` |

## Non-Negotiable Route

1. If configuration is missing or incomplete, run the terminal wizard from
   `paper-spine-intake`; do not ask the user to hand-write JSON or answer a
   long plain chat checklist when the terminal is available. The wizard is the
   supported Claude Code/Codex command-line UI. In Claude Code, `/paperspine`
   is the preferred entry: it launches intake automatically when configuration
   is missing. Use `scripts/launch_paperspine_ui.ps1` only as the underlying
   launcher when implementing that command.
2. Always create or verify `source_map.md`.
3. Always use `paper-spine-research` before choosing the final motivation.
4. Research must create `reference_materials/`, `research_dossier.md`,
   `exemplar_learning_dossier.md`, `style_profile.md`, `sota_gap_map.md`, and
   `motivation_options_after_research.md`.
5. Stop for user confirmation of the controlling motivation. Do not write or
   rewrite until `confirmed_motivation.md` records the user's chosen motivation.
   The final motivation should be concise and specific. Do not inflate one
   narrow contribution into a multi-claim motivation.
6. If `workflow` is `rewrite_existing`, use `paper-spine-rewrite`.
7. If `workflow` is `build_from_materials`, use `paper-spine-build`.
8. Before drafting, both workflows must create `section_blueprints.md` and
   `writing_rationale_matrix.md`. The matrix is the execution plan, not a
   post-hoc summary.
9. Use `paper-spine-latex` for final LaTeX structure, figure placement,
   citation safety, and compile-oriented cleanup.
10. Always produce final LaTeX source. Compile PDF when a TeX engine is
    available. Markdown alone is not a final PaperSpine output.
11. If `word_output` is `docx`, produce and check a Word version.
12. If `output_language` is `en` and `translation_package` is `zh`, translate every required intermediate Markdown artifact, every final result Markdown artifact, and the complete final paper text into `translation_zh/`, with a detailed coverage report. Large files such as `writing_rationale_matrix.md` must be translated row by row; summaries are not acceptable.
13. Use `paper-spine-audit` before declaring the work complete.

If another skill is unavailable, follow the referenced workflow locally and
produce the same artifacts.

## Standard Artifacts

Write workflow artifacts under `paper_rewriting_output/` unless the user asks
otherwise.

Common required artifacts:

- `paper_spine_config.json`
- `paper_spine_config.md`
- `source_map.md`
- `reference_materials/source_index.md`
- `research_dossier.md`
- `exemplar_learning_dossier.md`
- `style_profile.md`
- `sota_gap_map.md`
- `motivation_options_after_research.md`
- `confirmed_motivation.md`
- `section_blueprints.md`
- `writing_rationale_matrix.md`

Rewrite existing:

- `original_logic_map.md`
- `evidence_bank.md`
- `rewrite_matrix.md`
- `logic_transfer_audit.md`
- revised manuscript

Build from materials:

- `source_inventory.md`
- `evidence_bank.md`
- `figure_asset_map.md`
- `claim_register.md`
- manuscript draft as an intermediate artifact

Final artifacts:

- `latex_report.md`
- `final_artifact_manifest.md`
- `final_paper/main.tex`
- `final_paper/paper.pdf` when a TeX compiler is available
- `final_paper/paper.docx` and `word_report.md` when Word output is requested
- `translation_zh/` when English output requests a Chinese translation package

## Writing Rationale Matrix Requirement

`writing_rationale_matrix.md` must be created before final writing in both
`rewrite_existing` and `build_from_materials`. It must be a Markdown table used
as the execution plan:

| Row ID | Manuscript Unit | Current/Planned Function | Motivation Link | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Change | Final Text Check |
|---|---|---|---|---|---|---|---|---|

The first data row must justify the whole-work framework, structure, or main
throughline in depth: why this controlling structure is chosen, how SOTA/target
examples informed it, how it follows the confirmed motivation, which user
evidence anchors it, and how the final manuscript will be checked against it.
Subsequent rows must follow the target document in order and split it into the
smallest useful writing units: paragraph-level moves, paragraph
groups, model steps, assumptions, result/claim units, review synthesis units,
competition solution blocks, headings, captions, and other argument-bearing
fragments.

This is flexible by scene. A journal paper may naturally use abstract,
introduction, methods, results, and discussion units. A competition paper may
use problem restatement, assumptions, model construction, solving process,
validation, sensitivity, strengths/weaknesses, and recommendations. A report or
review may use executive summary, background, taxonomy, comparison, synthesis,
and recommendation units. Do not force all tasks into a fixed IMRaD template.

Each row must explain concrete anchors across multiple dimensions: it advances
or narrows the confirmed motivation, transfers a structural pattern learned from
SOTA/example work, matches a target-scene norm, uses a user-provided evidence
item, creates a front/back echo, fixes an original logic failure, and/or
constrains a claim to available evidence. For important rows, write enough
reasoning that the user can learn why this writing move is better.

A shallow matrix is a failure. If most rows say only "improve clarity" or
"polish wording", stop and redo the research/blueprint stage.

## Command-Line UI

Claude Code and Codex do not guarantee a native graphical picker for skills.
The supported UI is the bundled terminal wizard. When configuration is missing,
run `paper-spine-intake`. In Claude Code, `/paperspine` must launch the intake
UI automatically; do not ask the user to call a separate UI command. The legacy
`/paperspine-ui` command may be used only as a manual fallback. The launcher
opens the bundled terminal TUI, which supports Up/Down for option values,
Left/Right for fields, Enter for edit or confirm, and `S` to save. Claude Code
does not currently provide third-party skills with an API for embedding a custom
keyboard UI directly inside the chat input box, so the real terminal TUI is the
supported interactive path. Use native structured questions only when the host
exposes them reliably in the current session. Use chat fallback only when
terminal execution is impossible.

