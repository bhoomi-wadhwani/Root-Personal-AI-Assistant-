@echo off
schtasks /end /tn TelegramAssistant >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
echo Bot stopped.
timeout /t 2 >nul
