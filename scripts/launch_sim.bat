@echo off
REM ==============================================================================
REM Multi-AMR Warehouse Simulation - Windows Command Prompt Launcher
REM ==============================================================================

set "PROJECT_ROOT=%~dp0.."
set "GZ_IP=127.0.0.1"
set "GZ_SIM_RESOURCE_PATH=%PROJECT_ROOT%\simulation\models;%GZ_SIM_RESOURCE_PATH%"

echo ==================================================
echo  Starting AMR Warehouse Simulation Environment
echo  Project Directory : %PROJECT_ROOT%
echo  GZ_IP             : %GZ_IP%
echo  GZ_SIM_RESOURCE_PATH : %GZ_SIM_RESOURCE_PATH%
echo ==================================================

if "%1"=="--server" (
    echo [+] Launching in Headless (Server) Mode...
    gz sim -s -r "%PROJECT_ROOT%\simulation\worlds\warehouse.sdf"
    goto :eof
)
if "%1"=="-s" (
    echo [+] Launching in Headless (Server) Mode...
    gz sim -s -r "%PROJECT_ROOT%\simulation\worlds\warehouse.sdf"
    goto :eof
)
if "%1"=="--gui" (
    echo [+] Launching GUI Client only...
    gz sim -g
    goto :eof
)
if "%1"=="-g" (
    echo [+] Launching GUI Client only...
    gz sim -g
    goto :eof
)

echo [+] Launching Full Simulation (Server + GUI)...
gz sim -r "%PROJECT_ROOT%\simulation\worlds\warehouse.sdf"
