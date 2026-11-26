# Helper for the Cowork CW1 runbook (work/TaskContractCoworkRunbook.md). Messages are ASCII on purpose (works on Windows PowerShell 5.1 and PowerShell 7).
# Usage (from any folder):
#   .\cowork.ps1 init                      create run-01..run-06 folders (default root C:\CoworkRuns\CW1)
#   .\cowork.ps1 copy B                    copy the B prompt to the clipboard (also: P1 = TC+ phase 1)
#   .\cowork.ps1 answers run-02 tz tax     write run-02\answers.txt for the asked topics (cancelled, tz, tax, months)
#   .\cowork.ps1 phase2 run-02             build run-02\phase2_prompt.txt from phase1_output.txt + answers.txt and copy it
#                                          (add -NewTask when phase 2 must go into a NEW Cowork task: the data block is put in front)
#   .\cowork.ps1 status                    show which files exist per run
#   .\cowork.ps1 pack                      write manifest.sha256.txt and CW1_results.zip
param(
    [Parameter(Position = 0)][string]$Cmd = "help",
    [Parameter(Position = 1)][string]$Arg1,
    [Parameter(Position = 2, ValueFromRemainingArguments = $true)][string[]]$Rest,
    [string]$Root = "C:\CoworkRuns\CW1",
    [switch]$NewTask
)
$ErrorActionPreference = "Stop"
$Exp = Split-Path $PSScriptRoot -Parent
$Arms = [ordered]@{ "run-01" = "B"; "run-02" = "TCP"; "run-03" = "B"; "run-04" = "TCP"; "run-05" = "B"; "run-06" = "TCP" }

function Read-Utf8([string]$Path) { return [System.IO.File]::ReadAllText($Path, (New-Object System.Text.UTF8Encoding($false))) }

# The answer sentences are read from the pre-registered protocol (single source of truth), not typed here.
function Get-AnswerTable {
    $proto = Read-Utf8 (Join-Path $Exp "data\preregistration_cowork_cw1.md")
    $t = @{}
    foreach ($line in ($proto -split "`n")) {
        if ($line -match '^\| `(cancelled|tz|tax|months|default)`[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$') { $t[$Matches[1]] = $Matches[2] }
    }
    if ($t.Count -ne 5) { throw "answer table not found in protocol" }
    return $t
}

function Get-Hash([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    return ([BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Text))) -replace "-", "")
}

switch ($Cmd) {
    "init" {
        New-Item -ItemType Directory -Force $Root | Out-Null
        foreach ($r in $Arms.Keys) {
            $d = Join-Path $Root $r
            New-Item -ItemType Directory -Force $d | Out-Null
            $meta = Join-Path $d "meta.txt"
            if (-not (Test-Path $meta)) {
                $text = @"
run: $r
arm: $($Arms[$r])
start_time (hh:mm:ss, local):
end_time (hh:mm:ss, local):
cowork_executed_code (yes / no / unknown):
cowork_asked_questions (count, 0 if none):
topics_answered (cancelled / tz / tax / months / none):
stopped_after_phase1 (yes / no / NA for B):
phase2_same_task (yes / no / NA):
approval_prompts_shown (describe, or none):
external_effect_requested (none, or describe and say you refused):
files_created_by_cowork (names, or none):
deviations (anything not following the runbook, or none):
"@
                [System.IO.File]::WriteAllText($meta, $text, (New-Object System.Text.UTF8Encoding($false)))
            }
        }
        Write-Host "Created run folders under $Root"
        Write-Host "Order: run-01 B, run-02 TC+, run-03 B, run-04 TC+, run-05 B, run-06 TC+ (use a NEW Cowork task for each run)"
    }
    "copy" {
        $map = @{ "B" = "prompts\E12_B.txt"; "P1" = "prompts\E12_TCP_phase1.txt" }
        if (-not $map.ContainsKey($Arg1)) { throw "usage: copy B | copy P1" }
        $text = Read-Utf8 (Join-Path $Exp $map[$Arg1])
        Set-Clipboard -Value $text
        Write-Host ("Copied {0} ({1} chars, SHA-256 {2}). Paste it into Cowork without any change." -f $map[$Arg1], $text.Length, (Get-Hash $text))
    }
    "answers" {
        $run = $Arg1
        if (-not $Arms.Contains($run)) { throw "usage: answers run-0N [cancelled] [tz] [tax] [months]" }
        $tbl = Get-AnswerTable
        $asked = @($Rest | Where-Object { $_ })
        foreach ($a in $asked) { if (-not $tbl.ContainsKey($a) -or $a -eq "default") { throw "unknown topic: $a (use cancelled, tz, tax, months)" } }
        $lines = @()
        foreach ($a in $asked) { $lines += ("- [{0}] {1}" -f $a, $tbl[$a]) }
        $lines += ("- [other] {0}" -f $tbl["default"])
        $out = Join-Path (Join-Path $Root $run) "answers.txt"
        [System.IO.File]::WriteAllText($out, (($lines -join "`r`n") + "`r`n"), (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "Wrote $out"
        Get-Content $out -Encoding UTF8
    }
    "phase2" {
        $run = $Arg1
        $d = Join-Path $Root $run
        $p1 = Join-Path $d "phase1_output.txt"
        $an = Join-Path $d "answers.txt"
        if (-not (Test-Path $p1)) { throw "save Cowork's whole phase 1 reply as $p1 first" }
        if (-not (Test-Path $an)) { throw "run 'answers $run ...' first" }
        $tpl = Read-Utf8 (Join-Path $Exp "prompts\E12_TCP_phase2.txt")
        $text = $tpl.Replace("{CONTRACT}", (Read-Utf8 $p1).Trim()).Replace("{ANSWERS}", (Read-Utf8 $an).Trim())
        if ($Rest -contains "-NewTask" -or $NewTask) {
            # fallback when phase 2 cannot continue in the same task: put the unchanged data block in front (protocol: reported separately)
            $b = Read-Utf8 (Join-Path $Exp "prompts\E12_B.txt")
            $m = [regex]::Match($b, '(?s)sales\.csv .{0,40}:\r?\n```.*?```')
            if (-not $m.Success) { throw "data block not found in E12_B.txt" }
            $text = $m.Value + "`r`n`r`n" + $text
        }
        $out = Join-Path $d "phase2_prompt.txt"
        [System.IO.File]::WriteAllText($out, $text, (New-Object System.Text.UTF8Encoding($false)))
        Set-Clipboard -Value $text
        Write-Host "Wrote $out and copied it to the clipboard. Send it in Cowork (same task if possible)."
    }
    "status" {
        foreach ($r in $Arms.Keys) {
            $d = Join-Path $Root $r
            $files = @("meta.txt", "conversation.txt", "final_dict.json", "phase1_output.txt", "answers.txt", "phase2_prompt.txt")
            $have = ($files | ForEach-Object { if (Test-Path (Join-Path $d $_)) { "[x] $_" } else { "[ ] $_" } }) -join "  "
            Write-Host ("{0} ({1}): {2}" -f $r, $Arms[$r], $have)
        }
    }
    "pack" {
        $manifest = Join-Path $Root "manifest.sha256.txt"
        $lines = Get-ChildItem $Root -Recurse -File | Where-Object { $_.Name -ne "manifest.sha256.txt" } | Sort-Object FullName | ForEach-Object {
            "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash, $_.FullName.Substring($Root.Length + 1)
        }
        [System.IO.File]::WriteAllText($manifest, (($lines -join "`r`n") + "`r`n"), (New-Object System.Text.UTF8Encoding($false)))
        $zip = Join-Path (Split-Path $Root -Parent) "CW1_results.zip"
        if (Test-Path $zip) { Remove-Item $zip -Force }
        Compress-Archive -Path (Join-Path $Root "*") -DestinationPath $zip
        Write-Host "Wrote $manifest"
        Write-Host "Wrote $zip"
        Write-Host ("zip SHA-256: " + (Get-FileHash $zip -Algorithm SHA256).Hash)
        Write-Host "Send the zip path and the zip SHA-256 above in your next message."
    }
    default {
        Get-Content $PSCommandPath -Encoding UTF8 | Select-Object -First 11
    }
}
