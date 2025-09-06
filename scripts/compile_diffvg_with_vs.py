#!/usr/bin/env python3
"""
DiffVG 编译脚本 - 使用发现的 Visual Studio 2022
优化版本，专门针对已确认的环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 DiffVG 快速编译 (已发现 VS2022)")
    print("=" * 60)
    
    # 确认的 Visual Studio 路径
    vs_path = r"D:\Program Files\Microsoft Visual Studio\2022\Community"
    vcvars_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvars64.bat")
    
    print(f"✅ 使用 Visual Studio: {vs_path}")
    print(f"✅ vcvars64.bat: {vcvars_path}")
    
    # DiffVG 目录
    current_dir = Path(__file__).parent.parent
    diffvg_dir = current_dir / "third_party" / "diffvg"
    
    print(f"📁 DiffVG 目录: {diffvg_dir}")
    
    if not diffvg_dir.exists():
        print("❌ DiffVG 目录不存在")
        return False
    
    # 清理旧的构建
    print("🧹 清理构建目录...")
    build_dirs = [
        diffvg_dir / "build",
        diffvg_dir / "dist", 
        diffvg_dir / "diffvg.egg-info"
    ]
    
    for build_dir in build_dirs:
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"   删除: {build_dir}")
    
    # 创建编译批处理脚本
    compile_script = diffvg_dir / "compile_with_vs.bat"
    
    script_content = f'''@echo off
echo 激活 Visual Studio 2022 环境...
call "{vcvars_path}"

echo 检查编译器...
cl
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 编译器激活失败
    exit /b 1
)

echo 检查 CUDA...
nvcc --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ CUDA 不可用
    exit /b 1
)

echo 开始编译 DiffVG...
cd /d "{diffvg_dir}"
python -m pip install -e . --verbose

echo 编译完成
'''
    
    print("📝 创建编译脚本...")
    with open(compile_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ 编译脚本: {compile_script}")
    
    # 执行编译
    print("🔨 开始编译...")
    os.chdir(diffvg_dir)
    
    try:
        result = subprocess.run([str(compile_script)], 
                              shell=True, 
                              capture_output=True, 
                              text=True,
                              timeout=600)  # 10分钟超时
        
        print("📋 编译输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  编译警告/错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 编译成功!")
            
            # 测试导入
            print("🧪 测试 DiffVG...")
            test_result = subprocess.run([
                sys.executable, '-c', 
                'import diffvg; print("✅ DiffVG 导入成功"); print("功能:", len(dir(diffvg)), "个")'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                print(test_result.stdout)
                print("🎉 DiffVG 安装完成且可用!")
                return True
            else:
                print("❌ DiffVG 导入测试失败:")
                print(test_result.stderr)
                return False
        else:
            print("❌ 编译失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 编译超时 (10分钟)")
        return False
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 下一步:")
        print("1. 重启应用程序")  
        print("2. 选择 DiffVG 引擎")
        print("3. 享受 AI 矢量化!")
    else:
        print("\n❌ 编译失败，请检查错误信息")
    
    input("\n按回车键继续...")
