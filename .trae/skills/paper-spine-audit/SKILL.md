---
name: paper-spine-audit
description: Audits PaperSpine outputs for missing artifacts, shallow revisions, logic transfer, unsupported claims, and translation coverage.
---

# PaperSpine Audit

Use this skill before calling a PaperSpine rewrite or build complete.

## Required Checks

1. Artifact completeness.
2. Reference material workspace exists and has a source index.
3. Motivation was confirmed by the user after research, not invented before
   research.
4. `writing_rationale_matrix.md` exists, is ordered, and covers the whole-work
   framework plus the task-specific writing units for the selected scene. It
   should split the paper/report into paragraph-sized, claim-sized, evidence,
   model, synthesis, heading, caption, or competition-solution units as needed;
   it must not be a fixed IMRaD checklist when the task is not an IMRaD paper.
   The first row must deeply justify the whole-work framework, and each row must
   include concrete motivation, reference/SOTA, target-scene, evidence, and
   planned text-move anchors rather than short labels.
5. No append-only or shallow revision for substantive rewrite tasks.
6. Logic transfer from original draft or materials to final manuscript.
7. Claim support from user evidence.
8. LaTeX citation, label, and figure safety when a LaTeX project exists.
9. Final LaTeX source exists; compiled PDF exists when a TeX engine is
   available.
10. Word output is structurally valid when a `.docx` is requested or generated.
11. Translation coverage is complete when `translation_package` is `zh`,
    including `full_paper_translation.zh.md` for the complete final paper text
    and row-by-row translation of large intermediate artifacts such as
    `writing_rationale_matrix.md`.

## Scripts

Run when available:

```bash
python scripts/artifact_check.py paper_rewriting_output --markdown --write
python scripts/revision_audit.py <original> <revised> --markdown
python scripts/latex_guard.py <main.tex> --bib <references.bib> --markdown
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx --markdown --output paper_rewriting_output/word_report.md
```

## Required Outputs

- `paper_rewriting_output/artifact_check.md`
- `paper_rewriting_output/revision_audit.md` for rewrite tasks
- `paper_rewriting_output/logic_transfer_audit.md`
- unresolved risks and user decisions

Do not mark the task complete if required artifacts are missing, if the final
manuscript contains unsupported claims, if translation is partial, or if the
rationale matrix is generic.

