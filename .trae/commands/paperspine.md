---
allowed-tools: Bash(powershell:*), Bash(powershell.exe:*), Bash(pwsh:*), Bash(cmd:*)
description: Start PaperSpine with automatic intake UI when configuration is missing
---

Start the PaperSpine workflow for the current project.

If `paper_rewriting_output/paper_spine_config.json` is missing or incomplete,
launch the PaperSpine intake UI automatically. Do not ask the user to run
`/paperspine-ui` or hand-write the configuration.

On Windows, run this command from the current project directory:

```powershell
$config = Join-Path (Get-Location) "paper_rewriting_output\paper_spine_config.json"
$launcher = Join-Path $env:USERPROFILE ".claude\skills\paper-spine-intake\scripts\launch_paperspine_ui.ps1"
if (-not (Test-Path -LiteralPath $launcher)) {
  throw "PaperSpine UI launcher not found at $launcher. Reinstall or resync PaperSpine."
}
if (-not (Test-Path -LiteralPath $config)) {
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File $launcher -OutputDir "paper_rewriting_output"
}
for ($i = 0; $i -lt 120 -and -not (Test-Path -LiteralPath $config); $i++) {
  Start-Sleep -Seconds 5
}
if (-not (Test-Path -LiteralPath $config)) {
  throw "PaperSpine intake config was not created yet. Finish the opened PowerShell UI window, then rerun /paperspine."
}
Get-Content -LiteralPath $config -Raw
```

The launcher opens a separate interactive PowerShell window with numbered menus.
Wait for `paper_rewriting_output/paper_spine_config.json`, read it, and continue
through the `paper-spine` orchestrator workflow.

When the config already exists, read it directly and continue the PaperSpine
workflow without relaunching intake unless required fields are missing.
