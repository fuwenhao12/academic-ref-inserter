---
allowed-tools: Bash(powershell:*), Bash(powershell.exe:*), Bash(pwsh:*), Bash(cmd:*)
description: Legacy alias for launching the PaperSpine intake wizard
---

Launch the PaperSpine intake UI for the current project.

Prefer `/paperspine` for normal work. It starts the full PaperSpine workflow and
launches this UI automatically when configuration is missing. This command is a
compatibility/manual launcher.

Important: do not run `python scripts/intake_wizard.py` directly inside Claude
Code's hidden Bash/tool execution surface. It waits for stdin and can hang.

On Windows, run this command from the current project directory:

```powershell
$launcher = Join-Path $env:USERPROFILE ".claude\skills\paper-spine-intake\scripts\launch_paperspine_ui.ps1"
if (-not (Test-Path -LiteralPath $launcher)) {
  throw "PaperSpine UI launcher not found at $launcher. Reinstall or resync PaperSpine."
}
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $launcher -OutputDir "paper_rewriting_output"
```

This opens a separate PowerShell window with numbered menus. After the user
finishes, read `paper_rewriting_output/paper_spine_config.json` and continue the
PaperSpine workflow.
