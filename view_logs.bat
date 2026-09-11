@echo off
cd /d "%~dp0"
powershell -Command "Get-Content logs\bot.log -Tail 50 -Wait"
