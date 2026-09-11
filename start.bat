@echo off
title Telegram Assistant Bot
cd /d "%~dp0"
echo Starting Telegram Assistant Bot...
echo Logs are also saved to logs\bot.log
echo Close this window to stop the bot.
echo.
python main.py
echo.
echo Bot stopped. Press any key to close.
pause >nul
