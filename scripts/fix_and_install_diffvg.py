#!/usr/bin/env python3
"""
修复的 DiffVG 安装脚本 - 解决 Python 3.12 兼容性问题
"""

import os
import sys
import subprocess
from pathlib import Path

def fix_setup_py():
    """修复 setup.py 中的 Python 3.12 兼容性问题"""
    setup_py_path = Path("setup.py")
    
    if not setup_py_path.exists():
        print("❌ setup.py 不存在")
        return False
    
    print("🔧 修复 setup.py 的 Python 3.12 兼容性问题...")
    
    # 读取原始文件
    with open(setup_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复 LIBDIR 问题
    old_line = "'-DPYTHON_LIBRARY=' + get_config_var('LIBDIR'),"
    new_line = "'-DPYTHON_LIBRARY=' + (get_config_var('LIBDIR') or ''),"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ 修复了 LIBDIR 问题")
    
    # 写回文件
    with open(setup_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def install_with_build():
    """使用现代 build 工具安装"""
    print("🔨 使用现代 build 工具安装...")
    
    try:
        # 安装 build 工具
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'build'], check=True)
        
        # 构建包
        subprocess.run([sys.executable, '-m', 'build'], check=True)
        
        # 安装
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 现代安装方法失败: {e}")
        return False

def install_with_setuptools():
    """使用 setuptools 安装"""
    print("🔨 使用 setuptools develop 模式安装...")
    
    try:
        result = subprocess.run([
            sys.executable, 'setup.py', 'develop'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ develop 模式安装成功!")
            return True
        else:
            print("❌ develop 模式安装失败")
            print("stderr:", result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ setuptools 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 修复并安装 DiffVG")
    print("=" * 50)
    
    # 确保在正确的目录
    diffvg_dir = Path("F:/mylab/SVG/RasterVectorStudio/third_party/diffvg")
    if not diffvg_dir.exists():
        print(f"❌ DiffVG 目录不存在: {diffvg_dir}")
        return False
    
    original_dir = os.getcwd()
    os.chdir(diffvg_dir)
    
    try:
        # 修复 setup.py
        if not fix_setup_py():
            return False
        
        # 尝试不同的安装方法
        print("\n📦 尝试安装方法...")
        
        # 方法 1: 现代 build 工具
        if install_with_build():
            print("✅ 使用现代 build 工具安装成功!")
            return True
        
        # 方法 2: setuptools develop
        if install_with_setuptools():
            print("✅ 使用 setuptools develop 安装成功!")
            return True
        
        print("❌ 所有安装方法都失败了")
        return False
        
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 DiffVG 安装成功!")
        
        # 测试安装
        try:
            import pydiffvg
            print("✅ pydiffvg 导入测试成功!")
        except ImportError as e:
            print(f"⚠️  pydiffvg 导入失败: {e}")
    else:
        print("\n❌ DiffVG 安装失败")
        print("\n💡 可能的解决方案:")
        print("1. 确保安装了 Visual Studio Build Tools")
        print("2. 尝试使用 conda 环境")
        print("3. 检查 PyTorch 版本兼容性")
    
    sys.exit(0 if success else 1)
