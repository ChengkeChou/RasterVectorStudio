@echo off
REM 设置 Visual Studio 编译环境并编译 DiffVG

echo 正在设置 Visual Studio 编译环境...

REM 尝试找到 Visual Studio 安装
set "VS_INSTALL_DIR="
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_INSTALL_DIR=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\"
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_INSTALL_DIR=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\"
) else if exist "C:\Program Files\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_INSTALL_DIR=C:\Program Files\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\"
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_INSTALL_DIR=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\"
) else (
    echo 错误: 找不到 Visual Studio 安装
    echo 请确保安装了 Visual Studio 或 Visual Studio Build Tools
    pause
    exit /b 1
)

echo 找到 Visual Studio: %VS_INSTALL_DIR%

REM 设置编译环境
call "%VS_INSTALL_DIR%vcvarsall.bat" x64

REM 添加 CMake 到 PATH
set "PATH=%PATH%;D:\Program Files\CMake\bin"

REM 进入 DiffVG 目录
cd /d "F:\mylab\SVG\RasterVectorStudio\third_party\diffvg"

echo 开始编译 DiffVG...

REM 清理之前的构建
if exist build rmdir /s /q build

REM 编译
python setup.py build_ext --inplace

if %ERRORLEVEL% NEQ 0 (
    echo 编译失败!
    pause
    exit /b 1
)

echo 安装到 Python...
python setup.py develop

if %ERRORLEVEL% NEQ 0 (
    echo 安装失败!
    pause
    exit /b 1
)

echo DiffVG 编译完成!

REM 测试
echo 测试 DiffVG...
python -c "import pydiffvg; print('DiffVG 测试成功!')"

if %ERRORLEVEL% NEQ 0 (
    echo DiffVG 测试失败!
    pause
    exit /b 1
)

echo 所有操作完成!
pause
