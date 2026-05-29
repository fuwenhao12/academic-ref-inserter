---
name: paper-spine-research
description: Researches target requirements, downloads reference materials, learns strong examples, and prepares motivation options.
---

# PaperSpine Research

Use this skill before motivation confirmation and before any scene-specific
writing. No target-scene research means no venue-specific writing advice.

## Inputs

Read `paper_rewriting_output/paper_spine_config.json` when available. The
important fields are `scene`, `tier`, `target_name`, `official_urls`,
`materials_dir`, `draft_path`, and `output_language`.

## Reference Materials Workspace

Create and use this folder before writing:

```text
paper_rewriting_output/reference_materials/
  source_index.md
  official_requirements/
  target_examples/
  field_sota/
  templates/
  figures_images/
  extracted_notes/
```

Store downloaded or extracted materials here, including target journal papers,
conference papers, competition reference papers, official rules/guidelines,
LaTeX or Word templates, reference figures/images, and extracted notes. Do not
mix these external examples with user evidence. External examples teach writing
logic only.

`source_index.md` must record every reference item:

| Source ID | Type | Title/Name | Origin/URL/Path | Why Included | Local File/Note | Used For |
|---|---|---|---|---|---|---|

## Tier Rules

- `flash`: collect 3 target-scene examples and 3 recent high-quality field/SOTA
  examples.
- `pro`: collect 6 target-scene examples and 6 recent high-quality field/SOTA
  examples.

Users may override counts explicitly, but do not invent that override.

## Scene Routes

- `journal`: read `references/scenario-journal.md`.
- `conference`: read `references/scenario-conference.md`.
- `report_review`: read `references/scenario-report-review.md`.
- `competition`: read `references/scenario-competition.md`.

For current official requirements, use current web sources when available:
author guidelines, CFPs, rubrics, school or department pages, competition
rules, templates, and official announcements.

## Motivation Comes After Research

Do not finalize the motivation before learning SOTA and target-scene examples.
If the user provides a motivation early, treat it as a hypothesis.

Create `sota_gap_map.md`:

| Candidate Contribution | What SOTA/Examples Already Do | User Evidence | Real Gap | Claim Strength | Risk of Overclaim |
|---|---|---|---|---|---|

Then create `motivation_options_after_research.md`:

| Option | One-Sentence Motivation | Core Innovation | Why It Is Not Overbroad | Required Evidence | Best-Fit Paper Arc |
|---|---|---|---|---|---|

Rules:

- Each option must be concise. Prefer one controlling contribution over a list
  of generic benefits.
- If the real novelty is narrow, say so. For example, if the contribution is a
  conservation score, do not inflate the motivation into long-range context,
  profile jitter, and many unrelated claims unless user evidence proves them.
- Stop and ask the user to choose, revise, or write their own motivation.
- Only after the user confirms, write `confirmed_motivation.md` with:
  - exact confirmed motivation,
  - user confirmation status,
  - rejected options and why,
  - scope limits and forbidden overclaims.

## Required Outputs

Create:

- `paper_rewriting_output/reference_materials/source_index.md`
- `paper_rewriting_output/research_dossier.md`
- `paper_rewriting_output/exemplar_learning_dossier.md`
- `paper_rewriting_output/style_profile.md`
- `paper_rewriting_output/sota_gap_map.md`
- `paper_rewriting_output/motivation_options_after_research.md`
- `paper_rewriting_output/confirmed_motivation.md` only after user confirmation

The dossier must separate official requirements, target-scene examples, field
SOTA examples, reusable rhetorical moves, and constraints that affect the user's
manuscript. Do not borrow claims, data, or results from examples into the user's
paper.