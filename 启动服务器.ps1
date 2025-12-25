# SearXNG 开发服务器启动脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SearXNG 开发服务器启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "当前目录: $PWD" -ForegroundColor Gray
Write-Host ""

Write-Host "[1/3] 激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 无法激活虚拟环境" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host "✓ 虚拟环境已激活" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] 设置环境变量..." -ForegroundColor Yellow
$env:SEARXNG_SETTINGS_PATH = "config\settings.yml"
Write-Host "✓ 环境变量已设置" -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] 启动SearXNG服务器..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务器正在启动..." -ForegroundColor Green
Write-Host "  访问地址: http://127.0.0.1:8888" -ForegroundColor Cyan
Write-Host "  按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python searx\webapp.py

