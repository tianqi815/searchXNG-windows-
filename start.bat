@echo off
chcp 65001 >nul
echo ========================================
echo    SearXNG 开发服务器启动脚本
echo ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %CD%
echo.

echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 无法激活虚拟环境
    pause
    exit /b 1
)
echo ✓ 虚拟环境已激活
echo.

echo [2/3] 设置环境变量...
set SEARXNG_SETTINGS_PATH=config\settings.yml
echo ✓ 环境变量已设置
echo.

echo [3/3] 启动SearXNG服务器...
echo.
echo ========================================
echo   服务器正在启动...
echo   访问地址: http://127.0.0.1:8888
echo   按 Ctrl+C 停止服务器
echo ========================================
echo.

python searx\webapp.py

pause

