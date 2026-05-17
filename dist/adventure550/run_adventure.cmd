@echo off
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%"
"%SCRIPT_DIR%adventure.exe"
set RC=%ERRORLEVEL%
popd
exit /b %RC%
