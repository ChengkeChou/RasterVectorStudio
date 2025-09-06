@echo off
setlocal

echo 设置 Visual Studio 2022 编译环境...
call "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

echo 添加 CMake 到 PATH...
set "PATH=%PATH%;D:\Program Files\CMake\bin"

echo 进入 DiffVG 目录...
cd /d "F:\mylab\SVG\RasterVectorStudio\third_party\diffvg"

echo 清理之前的构建...
if exist build (
    rmdir /s /q build
    echo 已删除 build 目录
)
if exist CMakeCache.txt (
    del CMakeCache.txt
    echo 已删除 CMakeCache.txt
)
if exist CMakeFiles (
    rmdir /s /q CMakeFiles
    echo 已删除 CMakeFiles 目录
)

echo 开始编译 DiffVG...
python setup.py build_ext --inplace

if %ERRORLEVEL% NEQ 0 (
    echo 编译失败! 错误代码: %ERRORLEVEL%
    pause
    exit /b 1
)

echo 安装到 Python 环境...
python setup.py develop

if %ERRORLEVEL% NEQ 0 (
    echo 安装失败! 错误代码: %ERRORLEVEL%
    pause
    exit /b 1
)

echo 测试 DiffVG 导入...
python -c "import pydiffvg; print('✅ DiffVG 编译和安装成功!')"

if %ERRORLEVEL% NEQ 0 (
    echo DiffVG 导入测试失败!
    pause
    exit /b 1
)

echo.
echo 🎉 DiffVG 编译完成！现在可以使用深度学习矢量化功能了。
pause
