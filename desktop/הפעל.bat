@echo off
chcp 65001 >nul
cd /d "%~dp0"
title זוכר שמות תלמידים - גרסה מקומית
python server.py
pause
