# Run this ONCE to register the bot as a Windows auto-start task.
# Right-click this file → "Run with PowerShell"

$projectDir = "C:\Users\bhoom\telegram-assistant"
$pythonw    = "C:\Users\bhoom\AppData\Local\Programs\Python\Python312\pythonw.exe"
$taskName   = "TelegramAssistant"

if (-not (Test-Path $pythonw)) {
    Write-Host "ERROR: pythonw.exe not found at $pythonw" -ForegroundColor Red
    Write-Host "Find it with: where pythonw" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$action   = New-ScheduledTaskAction -Execute $pythonw -Argument "main.py" -WorkingDirectory $projectDir
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable $true

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force | Out-Null

Write-Host ""
Write-Host "Done! '$taskName' registered." -ForegroundColor Green
Write-Host "The bot will now start automatically every time you log into Windows." -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  Start now  : schtasks /run /tn TelegramAssistant"
Write-Host "  Stop now   : schtasks /end /tn TelegramAssistant"
Write-Host "  Remove task: schtasks /delete /tn TelegramAssistant /f"
Write-Host "  View logs  : notepad $projectDir\logs\bot.log"
Write-Host ""
Read-Host "Press Enter to exit"
