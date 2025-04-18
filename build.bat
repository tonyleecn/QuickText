@echo off
chcp 65001 > nul
echo ===== 开始构建QuickText可执行文件 =====
echo.

REM 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python, 请先安装Python
    pause
    exit /b 1
)

REM 检查并安装必要的依赖包
echo 正在检查并安装依赖...
python -m pip install --upgrade pip
python -m pip install pyinstaller pyperclip keyboard pillow -q

REM 检查图标文件
if not exist tool.png (
    echo 错误: 未找到tool.png图标文件, 请确保图标文件存在于当前目录
    pause
    exit /b 1
)

REM 检查预设文件
if not exist presets.json (
    echo 创建默认预设文件...
    echo {"常用": {"欢迎使用": "欢迎使用QuickText!\n\n这是您的第一个预设文本。\n您可以在设置中添加更多预设。"}} > presets.json
)

REM 转换图标为ICO格式
echo 正在转换图标...
python convert_icon.py
if not exist tool.ico (
    echo 警告: 图标转换失败, 将使用原始PNG图标
    set ICON_FILE=tool.png
) else (
    set ICON_FILE=tool.ico
)

echo.
echo 构建选项:
echo 1. 构建标准版本 (更小体积)
echo 2. 构建调试版本 (更易于排错)
echo.

choice /c 12 /m "请选择构建版本"
if %ERRORLEVEL% EQU 1 (
    echo.
    echo 开始构建标准版本...
    
    REM 调用PyInstaller进行打包 - 标准版本
    pyinstaller --name=QuickText ^
                --onefile ^
                --windowed ^
                --icon=%ICON_FILE% ^
                --add-data="presets.json;." ^
                --add-data="tool.png;." ^
                quick_text.py
) else (
    echo.
    echo 开始构建调试版本...
    
    REM 调用PyInstaller进行打包 - 调试版本
    pyinstaller --name=QuickText_debug ^
                --onedir ^
                --icon=%ICON_FILE% ^
                --add-data="presets.json;." ^
                --add-data="tool.png;." ^
                --console ^
                quick_text.py
)

REM 打包完成
if exist dist\QuickText.exe (
    echo.
    echo ===== 标准版本构建成功 =====
    echo 可执行文件位于: %CD%\dist\QuickText.exe
) else if exist dist\QuickText_debug\QuickText_debug.exe (
    echo.
    echo ===== 调试版本构建成功 =====
    echo 可执行文件位于: %CD%\dist\QuickText_debug\QuickText_debug.exe
) else (
    echo.
    echo ===== 构建失败 =====
    echo 请检查错误信息
)
echo.
pause 