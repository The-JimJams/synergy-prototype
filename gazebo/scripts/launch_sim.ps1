# ==============================================================================
# Multi-AMR Warehouse Simulation - Windows PowerShell Launcher
# ==============================================================================

param (
    [switch]$Server,
    [switch]$GUI
)

$ProjectRoot = (Get-Item "$PSScriptRoot\..").FullName
$env:GZ_IP = "127.0.0.1"

if ($env:GZ_SIM_RESOURCE_PATH) {
    $env:GZ_SIM_RESOURCE_PATH = "$ProjectRoot\simulation\models;" + $env:GZ_SIM_RESOURCE_PATH
} else {
    $env:GZ_SIM_RESOURCE_PATH = "$ProjectRoot\simulation\models"
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " 🤖 Starting AMR Warehouse Simulation Environment" -ForegroundColor Green
Write-Host " Project Directory : $ProjectRoot"
Write-Host " GZ_IP             : $env:GZ_IP"
Write-Host " GZ_SIM_RESOURCE_PATH : $env:GZ_SIM_RESOURCE_PATH"
Write-Host "==================================================" -ForegroundColor Cyan

if ($Server) {
    Write-Host "[+] Launching in Headless (Server) Mode..." -ForegroundColor Yellow
    gz sim -s -r "$ProjectRoot\simulation\worlds\warehouse.sdf"
} elseif ($GUI) {
    Write-Host "[+] Launching GUI Client only..." -ForegroundColor Yellow
    gz sim -g
} else {
    Write-Host "[+] Launching Full Simulation (Server + GUI)..." -ForegroundColor Yellow
    gz sim -r "$ProjectRoot\simulation\worlds\warehouse.sdf"
}
