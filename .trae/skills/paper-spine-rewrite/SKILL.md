---
name: paper-spine-rewrite
description: Rewrites an existing manuscript from confirmed motivation, research, paragraph-level rationale, and evidence.
---

# PaperSpine Rewrite

Use this skill when the user already has a draft and wants a substantive
manuscript improvement.

## Required Inputs

- `paper_rewriting_output/paper_spine_config.json`
- user draft from `draft_path` or the conversation
- `paper_rewriting_output/reference_materials/source_index.md`
- `paper_rewriting_output/research_dossier.md`
- `paper_rewriting_output/exemplar_learning_dossier.md`
- `paper_rewriting_output/style_profile.md`
- `paper_rewriting_output/sota_gap_map.md`
- `paper_rewriting_output/confirmed_motivation.md` with user confirmation
- evidence from the user's draft, figures, tables, data, or notes

If research or confirmed motivation is missing, do not rewrite. Return to
`paper-spine-research` and ask the user to confirm the motivation after seeing
research-grounded options.

## Required Outputs

- `paper_rewriting_output/original_logic_map.md`
- `paper_rewriting_output/evidence_bank.md`
- `paper_rewriting_output/section_blueprints.md`
- `paper_rewriting_output/writing_rationale_matrix.md`
- `paper_rewriting_output/rewrite_matrix.md`
- `paper_rewriting_output/logic_transfer_audit.md`
- revised manuscript or revised sections

## Original Logic Map

Before rewriting, map the existing manuscript in order:

| Original Unit | Current Text Role | Evidence Used | Motivation Link | Problem | Keep / Move / Rewrite / Delete |
|---|---|---|---|---|---|

This is required so the rewrite can be compared against the original logic, not
only against surface wording.

## Writing Rationale Matrix

Before final prose, create `writing_rationale_matrix.md` and read
`references/writing-rationale-matrix.md`. The matrix is the rewrite plan. It
must be ordered by the manuscript's actual writing units, not by a fixed IMRaD
or journal-paper template.

Use this table:

| Row ID | Manuscript Unit | Original Problem or Planned Function | Motivation Link | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Change | Final Text Check |
|---|---|---|---|---|---|---|---|---|

The first data row must deeply justify the whole-work framework or throughline:
why this controlling structure is chosen, how SOTA/target examples informed it,
how it follows the confirmed motivation, which user evidence anchors it, and how
the final manuscript will be checked against it. After that, split the draft
into the smallest useful units for this target scene:
paragraphs, paragraph groups, result/claim units, model steps, assumptions,
review synthesis blocks, competition solution blocks, headings, captions, or
other argument-bearing fragments. Do not force reports, reviews, or competition
papers into Abstract/Introduction/Methods/Results/Discussion if that is not the
right structure.

Each row must explain concrete anchors across multiple dimensions. Acceptable
reasons include: confirms or narrows the central motivation, transfers a
structural move from a strong example without copying wording, matches
target-scene expectation, moves evidence next to the claim, fixes a weak
transition, creates a front/back echo, or constrains a claim to available
evidence. If a row cannot teach the user why this writing move is better, it is
too shallow.

## Rewrite Rules

- Rewrite from `writing_rationale_matrix.md`, not by appending sentences to old
  paragraphs.
- A paragraph should survive unchanged only if the matrix explicitly says why it
  already serves the confirmed motivation.
- Preserve user claims only when supported by user evidence.
- Preserve LaTeX commands, labels, citations, equations, figures, and tables
  unless the user asks to change structure.
- Use `output_language` from config: `en` for English, `zh` for Chinese.
- Keep target-scene style subordinate to the confirmed motivation.
- `rewrite_matrix.md` must map original units to final units and state whether
  each change is structural, rhetorical, evidence-related, or only language.

Read `references/writing-rationale-matrix.md`,
`references/motivation-thread-writing.md`, `references/deep-imitation-protocol.md`,
and `references/rewrite-matrix.md` when doing substantive rewriting.

