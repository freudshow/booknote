@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 微信作业自动下载机器人
echo ========================================

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖
echo [信息] 检查依赖包...
pip show wxauto pyyaml apscheduler >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络或手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

:: 检查微信是否运行
tasklist | findstr /i "WeChat.exe" >nul
if %errorlevel% neq 0 (
    echo [警告] 微信客户端未运行，请先登录微信PC版
    echo 启动微信后按任意键继续...
    pause >nul
)

:: 创建日志目录
if not exist logs mkdir logs

echo [信息] 启动机器人...
echo [提示] 按 Ctrl+C 可停止程序
echo ========================================

python main.py

echo.
echo 程序已退出
pause