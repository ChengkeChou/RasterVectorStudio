#!/usr/bin/env python3
"""
DiffVG 编译脚本 - 专为 CUDA 12.8 优化
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_cuda_128():
    """检查 CUDA 12.8 环境"""
    print("🔍 检查 CUDA 12.8 环境...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CUDA 编译器可用:")
            print(result.stdout)
            
            # 检查是否是 12.8 版本
            if "release 12.8" in result.stdout:
                print("✅ 确认 CUDA 12.8 版本")
                return True
            else:
                print("⚠️  检测到的不是 CUDA 12.8")
                print("当前版本可能仍然兼容")
                return True
        else:
            print("❌ CUDA 编译器不可用")
            return False
    except FileNotFoundError:
        print("❌ nvcc 命令未找到")
        return False

def check_visual_studio():
    """检查 Visual Studio 2022"""
    print("🔍 检查 Visual Studio 2022...")
    
    try:
        result = subprocess.run(['cl'], capture_output=True, text=True)
        if 'Microsoft' in result.stderr and 'Visual Studio' in result.stderr:
            print("✅ Visual Studio 编译器可用")
            # 提取版本信息
            for line in result.stderr.split('\n'):
                if '版本' in line or 'Version' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Visual Studio 编译器不可用")
            print("需要设置 Visual Studio 环境")
            return False
    except FileNotFoundError:
        print("❌ cl 编译器未找到")
        return False

def setup_vs_environment():
    """设置 Visual Studio 环境"""
    print("🔧 设置 Visual Studio 环境...")
    
    vs_paths = [
        "D:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat",
        "D:\\Program Files\\Microsoft Visual Studio\\2022\\Professional\\VC\\Auxiliary\\Build\\vcvarsall.bat",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional\\VC\\Auxiliary\\Build\\vcvarsall.bat"
    ]
    
    for vs_path in vs_paths:
        if Path(vs_path).exists():
            print(f"✅ 找到 Visual Studio: {vs_path}")
            return vs_path
    
    print("❌ 未找到 Visual Studio 安装")
    return None

def check_pytorch_cuda():
    """检查 PyTorch CUDA 支持"""
    print("🔍 检查 PyTorch CUDA 支持...")
    
    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA 可用: {torch.version.cuda}")
            print(f"✅ GPU 设备: {torch.cuda.get_device_name(0)}")
            print(f"✅ GPU 数量: {torch.cuda.device_count()}")
            return True
        else:
            print("⚠️  PyTorch 未检测到 CUDA 支持")
            print("可能需要重新安装兼容 CUDA 12.8 的 PyTorch")
            return False
    except ImportError:
        print("❌ PyTorch 未安装")
        return False

def update_pytorch_for_cuda128():
    """为 CUDA 12.8 更新 PyTorch"""
    print("🔄 为 CUDA 12.8 更新 PyTorch...")
    
    try:
        # 卸载现有版本
        print("卸载现有 PyTorch...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'uninstall', 
            'torch', 'torchvision', 'torchaudio', '-y'
        ], check=False)
        
        # 安装兼容 CUDA 12.8 的版本
        print("安装兼容 CUDA 12.8 的 PyTorch...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'torch', 'torchvision', 'torchaudio', 
            '--index-url', 'https://download.pytorch.org/whl/cu121'
        ], check=True)
        
        print("✅ PyTorch 更新完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyTorch 更新失败: {e}")
        return False

def clean_diffvg_build():
    """清理 DiffVG 构建目录"""
    print("🧹 清理 DiffVG 构建目录...")
    
    diffvg_path = Path("F:/mylab/SVG/RasterVectorStudio/third_party/diffvg")
    
    # 要清理的目录和文件
    cleanup_targets = [
        'build',
        '_skbuild', 
        'dist',
        '*.egg-info',
        'CMakeCache.txt',
        'CMakeFiles'
    ]
    
    for target in cleanup_targets:
        for path in diffvg_path.glob(target):
            if path.exists():
                print(f"删除: {path}")
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

def update_cmake_for_cuda128():
    """更新 CMakeLists.txt 支持 CUDA 12.8"""
    print("📝 更新 CMakeLists.txt...")
    
    cmake_file = Path("F:/mylab/SVG/RasterVectorStudio/third_party/diffvg/CMakeLists.txt")
    
    if not cmake_file.exists():
        print(f"❌ CMakeLists.txt 不存在: {cmake_file}")
        return False
    
    # 备份原文件
    backup_file = cmake_file.with_suffix('.txt.backup')
    if not backup_file.exists():
        shutil.copy2(cmake_file, backup_file)
        print(f"✅ 备份原文件: {backup_file}")
    
    # 读取文件内容
    with open(cmake_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 CUDA 配置
    if "CUDA 12.8" not in content:
        # 添加 CUDA 12.8 特定配置
        cuda_config = '''
# CUDA 12.8 特定配置
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CXX_STANDARD 17)

# CUDA 架构支持 (包括最新的 Ada Lovelace 和 Hopper)
set(CMAKE_CUDA_ARCHITECTURES "60;61;70;75;80;86;89;90")

# CUDA 12.8 编译选项
if(WIN32)
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -Xcompiler /MD")
    set(CMAKE_CUDA_FLAGS_RELEASE "${CMAKE_CUDA_FLAGS_RELEASE} -O3")
endif()
'''
        
        # 在适当位置插入配置
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if 'cmake_minimum_required' in line.lower():
                insert_index = i + 1
                break
        
        lines.insert(insert_index, cuda_config)
        content = '\n'.join(lines)
        
        # 写回文件
        with open(cmake_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ CMakeLists.txt 已更新支持 CUDA 12.8")
    else:
        print("✅ CMakeLists.txt 已包含 CUDA 12.8 配置")
    
    return True

def update_setup_py_for_cuda128():
    """更新 setup.py 支持 CUDA 12.8"""
    print("📝 更新 setup.py...")
    
    setup_file = Path("F:/mylab/SVG/RasterVectorStudio/third_party/diffvg/setup.py")
    
    if not setup_file.exists():
        print(f"❌ setup.py 不存在: {setup_file}")
        return False
    
    # 备份原文件
    backup_file = setup_file.with_suffix('.py.backup')
    if not backup_file.exists():
        shutil.copy2(setup_file, backup_file)
        print(f"✅ 备份原文件: {backup_file}")
    
    # 读取文件内容
    with open(setup_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 强制启用 CUDA 并指定版本
    if "# CUDA 12.8 配置" not in content:
        cuda_setup_config = '''
# CUDA 12.8 配置
import os
os.environ['CUDA_HOME'] = os.environ.get('CUDA_PATH', 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.8')
os.environ['CUDA_PATH'] = os.environ.get('CUDA_PATH', 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.8')

# 强制启用 CUDA
build_with_cuda = True
print(f"强制启用 CUDA 编译: {build_with_cuda}")
'''
        
        # 在导入部分之后插入
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if 'import' in line and ('torch' in line or 'sys' in line):
                insert_index = i + 1
                break
        
        lines.insert(insert_index, cuda_setup_config)
        content = '\n'.join(lines)
        
        # 写回文件
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ setup.py 已更新支持 CUDA 12.8")
    else:
        print("✅ setup.py 已包含 CUDA 12.8 配置")
    
    return True

def create_compile_batch():
    """创建编译批处理脚本"""
    print("📝 创建编译批处理脚本...")
    
    vs_path = setup_vs_environment()
    if not vs_path:
        print("❌ 无法找到 Visual Studio 安装")
        return None
    
    batch_content = f'''@echo off
echo ================================================
echo DiffVG 编译脚本 - CUDA 12.8
echo ================================================

echo 设置 Visual Studio 2022 环境...
call "{vs_path}" x64
if %ERRORLEVEL% NEQ 0 (
    echo Visual Studio 环境设置失败!
    pause
    exit /b 1
)

echo 设置 CUDA 环境变量...
set "CUDA_PATH=C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.8"
set "CUDA_HOME=%CUDA_PATH%"
set "PATH=%CUDA_PATH%\\bin;%PATH%"

echo 切换到 DiffVG 目录...
cd /d "F:\\mylab\\SVG\\RasterVectorStudio\\third_party\\diffvg"

echo 验证编译工具...
nvcc --version
echo.
cl
echo.

echo 开始编译 DiffVG...
python -m pip install -e . --verbose --force-reinstall

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DiffVG 编译成功!
    echo 测试 DiffVG 导入...
    python -c "import pydiffvg; print('DiffVG 导入成功!')"
) else (
    echo.
    echo ❌ DiffVG 编译失败!
)

echo.
echo 编译完成! 
pause
'''
    
    batch_file = Path("F:/mylab/SVG/RasterVectorStudio/scripts/compile_diffvg_cuda128.bat")
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ 编译脚本已创建: {batch_file}")
    return batch_file

def compile_diffvg_python():
    """使用 Python 直接编译 DiffVG"""
    print("🔨 使用 Python 编译 DiffVG...")
    
    diffvg_path = Path("F:/mylab/SVG/RasterVectorStudio/third_party/diffvg")
    original_dir = os.getcwd()
    
    try:
        os.chdir(diffvg_path)
        
        # 设置环境变量
        os.environ['CUDA_PATH'] = 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.8'
        os.environ['CUDA_HOME'] = os.environ['CUDA_PATH']
        
        print("运行: python -m pip install -e . --verbose")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-e', '.', '--verbose'
        ], capture_output=True, text=True, timeout=1800)  # 30分钟超时
        
        if result.returncode == 0:
            print("✅ DiffVG 编译成功!")
            print("编译输出 (最后500字符):")
            print(result.stdout[-500:])
            return True
        else:
            print("❌ DiffVG 编译失败!")
            print("错误输出:")
            print(result.stderr[-1000:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 编译超时 (30分钟)")
        return False
    except Exception as e:
        print(f"❌ 编译过程中出错: {e}")
        return False
    finally:
        os.chdir(original_dir)

def test_diffvg():
    """测试 DiffVG 安装"""
    print("🧪 测试 DiffVG 安装...")
    
    try:
        # 基本导入测试
        import pydiffvg
        print("✅ pydiffvg 导入成功")
        
        # 检查 CUDA 支持
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"✅ 计算设备: {device}")
        
        # 尝试设置 DiffVG
        pydiffvg.set_use_gpu(torch.cuda.is_available())
        pydiffvg.set_print_timing(False)
        
        print("✅ DiffVG 基本功能测试成功!")
        print("🎉 可以在应用程序中使用 DiffVG 了!")
        return True
        
    except Exception as e:
        print(f"❌ DiffVG 测试失败: {e}")
        print("💡 可能的问题:")
        print("   1. 编译未完全成功")
        print("   2. 缺少依赖库")
        print("   3. CUDA 版本不匹配")
        return False

def main():
    """主函数"""
    print("🚀 DiffVG 编译脚本 (CUDA 12.8)")
    print("=" * 60)
    print("针对 CUDA 12.8 和 Visual Studio 2022 优化")
    print("=" * 60)
    
    # 1. 检查 CUDA 12.8
    if not check_cuda_128():
        print("❌ CUDA 12.8 环境检查失败")
        return
    
    # 2. 检查 Visual Studio
    if not check_visual_studio():
        print("⚠️  Visual Studio 环境未激活")
        print("将创建批处理脚本来设置环境")
    
    # 3. 检查 PyTorch CUDA 支持
    pytorch_cuda_ok = check_pytorch_cuda()
    if not pytorch_cuda_ok:
        response = input("是否更新 PyTorch 以支持 CUDA 12.8? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            update_pytorch_for_cuda128()
    
    # 4. 清理构建目录
    clean_diffvg_build()
    
    # 5. 更新配置文件
    if not update_cmake_for_cuda128():
        print("❌ CMake 配置更新失败")
        return
    
    if not update_setup_py_for_cuda128():
        print("❌ setup.py 配置更新失败")
        return
    
    # 6. 选择编译方式
    print("\n🎯 选择编译方式:")
    print("1. Python 自动编译 (推荐)")
    print("2. 批处理脚本编译 (手动)")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == '1':
        # Python 编译
        if compile_diffvg_python():
            if test_diffvg():
                print("\n🎉 DiffVG 编译和测试成功!")
                print("现在可以在 RasterVectorStudio 中使用 DiffVG 功能了!")
            else:
                print("\n⚠️  DiffVG 编译成功但测试失败")
                print("请手动测试 'import pydiffvg'")
        else:
            print("\n❌ DiffVG 编译失败")
            print("请尝试使用批处理脚本编译")
    
    elif choice == '2':
        # 批处理脚本
        batch_file = create_compile_batch()
        if batch_file:
            print(f"\n📋 请运行编译脚本: {batch_file}")
            print("脚本将自动设置环境并编译 DiffVG")
            
            response = input("是否现在运行批处理脚本? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                subprocess.run([str(batch_file)], shell=True)
    
    else:
        print("无效选择")
    
    print("\n📋 编译完成后的下一步:")
    print("1. 重启应用程序")
    print("2. 在 DiffVG 工具中测试功能")
    print("3. 尝试深度学习矢量化")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
