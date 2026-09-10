@echo off
chcp 65001 >nul
python "%~dp0agentmemory_i18n_patch.py" apply
pause
