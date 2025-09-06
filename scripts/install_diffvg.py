#!/usr/bin/env python3
"""
DiffVG 安装脚本
按照 diffvg.txt 中的说明安装 DiffVG
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_prerequisites():
    """检查先决条件"""
    print("检查先决条件...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    print(f"✅ Python {sys.version}")
    
    # 检查 CMake
    try:
        result = subprocess.run(['cmake', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CMake 已安装")
        else:
            print("❌ CMake 未找到")
            return False
    except FileNotFoundError:
        print("❌ CMake 未安装")
        print("请安装 CMake: https://cmake.org/download/")
        return False
    
    # 检查 PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA 可用: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch 未安装")
        print("请安装 PyTorch: pip install torch torchvision")
        return False
    
    return True

def install_dependencies():
    """安装依赖项"""
    print("\n安装 Python 依赖项...")
    
    dependencies = [
        'torch',
        'torchvision', 
        'scikit-image',
        'numpy',
        'Pillow',
        'svglib',
        'svgpathtools',
        'freetype-py',
        'opencv-python'
    ]
    
    # 可选依赖
    optional_deps = [
        'lpips',  # 感知损失
        'cairosvg'  # SVG 渲染
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 安装失败: {e}")
            return False
    
    # 安装可选依赖（失败不影响主流程）
    for dep in optional_deps:
        print(f"安装可选依赖 {dep}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError:
            print(f"⚠️  {dep} 安装失败 (可选)")
    
    return True

def compile_diffvg():
    """编译 DiffVG"""
    print("\n编译 DiffVG...")
    
    # 获取 DiffVG 路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    diffvg_dir = project_root / "third_party" / "diffvg"
    
    if not diffvg_dir.exists():
        print(f"❌ DiffVG 源代码目录不存在: {diffvg_dir}")
        return False
    
    print(f"DiffVG 源代码目录: {diffvg_dir}")
    
    # 切换到 DiffVG 目录
    original_dir = os.getcwd()
    os.chdir(diffvg_dir)
    
    try:
        # 清理之前的构建
        build_dir = diffvg_dir / "build"
        if build_dir.exists():
            print("清理之前的构建...")
            import shutil
            shutil.rmtree(build_dir)
        
        # 运行 setup.py
        print("运行 python setup.py install...")
        result = subprocess.run([
            sys.executable, 'setup.py', 'install'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ DiffVG 编译成功")
            print(result.stdout)
            return True
        else:
            print("❌ DiffVG 编译失败")
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 编译过程中出错: {e}")
        return False
    finally:
        os.chdir(original_dir)

def test_installation():
    """测试安装"""
    print("\n测试 DiffVG 安装...")
    
    try:
        import pydiffvg
        print("✅ pydiffvg 导入成功")
        
        # 测试基本功能
        import torch
        pydiffvg.set_use_gpu(torch.cuda.is_available())
        device = pydiffvg.get_device()
        print(f"✅ DiffVG 设备: {device}")
        
        return True
        
    except ImportError as e:
        print(f"❌ pydiffvg 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ DiffVG 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("DiffVG 安装脚本")
    print("=" * 50)
    
    # 检查先决条件
    if not check_prerequisites():
        print("\n❌ 先决条件检查失败")
        return False
    
    # 安装依赖项
    if not install_dependencies():
        print("\n❌ 依赖项安装失败")
        return False
    
    # 编译 DiffVG
    if not compile_diffvg():
        print("\n❌ DiffVG 编译失败")
        return False
    
    # 测试安装
    if not test_installation():
        print("\n❌ DiffVG 安装测试失败")
        return False
    
    print("\n🎉 DiffVG 安装成功！")
    print("\n现在您可以使用 DiffVG 进行深度学习矢量化了。")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
