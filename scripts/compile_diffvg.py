#!/usr/bin/env python3
"""
简化的 DiffVG 编译脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """编译 DiffVG"""
    print("🚀 开始编译 DiffVG...")
    print("=" * 50)
    
    # 获取路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    diffvg_dir = project_root / "third_party" / "diffvg"
    
    if not diffvg_dir.exists():
        print(f"❌ DiffVG 源代码目录不存在: {diffvg_dir}")
        return False
    
    print(f"📁 DiffVG 目录: {diffvg_dir}")
    
    # 切换到 DiffVG 目录
    original_dir = os.getcwd()
    os.chdir(diffvg_dir)
    
    try:
        print("🔨 开始编译...")
        
        # 方法1: 尝试开发模式安装
        print("尝试开发模式安装...")
        result = subprocess.run([
            sys.executable, 'setup.py', 'develop'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 开发模式安装成功!")
            print(result.stdout)
        else:
            print("⚠️  开发模式安装失败，尝试常规安装...")
            print("stderr:", result.stderr)
            
            # 方法2: 常规安装
            result = subprocess.run([
                sys.executable, 'setup.py', 'install'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ 常规安装成功!")
                print(result.stdout)
            else:
                print("❌ 编译失败")
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
                return False
        
        # 测试安装
        print("🧪 测试安装...")
        test_result = subprocess.run([
            sys.executable, '-c', 'import pydiffvg; print("DiffVG 导入成功!")'
        ], capture_output=True, text=True)
        
        if test_result.returncode == 0:
            print("✅ DiffVG 测试成功!")
            print(test_result.stdout)
            return True
        else:
            print("❌ DiffVG 测试失败")
            print("stderr:", test_result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 编译超时 (5分钟)")
        return False
    except Exception as e:
        print(f"❌ 编译过程中出错: {e}")
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 DiffVG 编译完成! 现在可以使用真实的 DiffVG 功能了。")
    else:
        print("\n💡 编译失败的可能原因:")
        print("   1. 缺少 CMake: 请安装 CMake")
        print("   2. 缺少编译器: Windows 需要 Visual Studio Build Tools")
        print("   3. 缺少 PyTorch: pip install torch")
        print("   4. Python 版本过低: 需要 Python 3.7+")
    
    sys.exit(0 if success else 1)
