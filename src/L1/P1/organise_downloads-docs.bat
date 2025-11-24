@echo off
echo ===== Preview Mode =====
file_organizer_agent_3.exe --path "%USERPROFILE%\Downloads\docs" --dry-run
echo.
echo Press Any Button Start Organising...
pause >nul
file_organizer_agent_3.exe --path "%USERPROFILE%\Downloads\docs"
pause