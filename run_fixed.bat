@echo off
REM AI Novel Generator 启动脚本 (Windows)

echo AI Novel Generator 启动器
echo ================================

REM 检查 uv 是否可用
where uv >nul 2>nul
if %errorlevel% == 0 (
    echo 发现 uv 包管理器
) else (
    echo 未找到 uv 包管理器，将使用 pip
    goto use_pip
)

REM 使用 uv 安装依赖
echo 正在使用 uv 安装依赖...
uv pip install -r requirements-uv.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，继续尝试运行程序...
)

REM 使用 uv 运行主程序
echo 正在启动 AI Novel Generator...
uv run python main.py
goto end

:use_pip
echo 使用 pip 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，继续尝试运行程序...
)

echo 正在启动 AI Novel Generator...
python main.py

:end
pause