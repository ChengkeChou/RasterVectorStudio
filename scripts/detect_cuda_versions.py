#!/usr/bin/env python3
"""
多 CUDA 版本检测和管理脚本
"""

import os
import sys
import subprocess
from pathlib import Path
import json

def detect_cuda_installations():
    """检测系统中所有的 CUDA 安装"""
    print("🔍 检测系统中的 CUDA 安装...")
    
    cuda_installations = []
    
    # 检查常见的 CUDA 安装路径
    possible_paths = [
        "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
        "D:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
        "C:\\Program Files\\NVIDIA Corporation\\CUDA",
        "D:\\Program Files\\NVIDIA Corporation\\CUDA",
        "C:\\cuda",
        "D:\\cuda",
        "C:\\NVIDIA\\CUDA",
        "D:\\NVIDIA\\CUDA"
    ]
    
    for base_path in possible_paths:
        base_dir = Path(base_path)
        if base_dir.exists():
            print(f"📁 检查目录: {base_path}")
            
            # 查找版本目录 (v11.8, v12.0, v12.6, v12.9 等)
            for version_dir in base_dir.iterdir():
                if version_dir.is_dir() and version_dir.name.startswith('v'):
                    nvcc_path = version_dir / "bin" / "nvcc.exe"
                    if nvcc_path.exists():
                        # 获取版本信息
                        try:
                            result = subprocess.run([str(nvcc_path), '--version'], 
                                                  capture_output=True, text=True)
                            if result.returncode == 0:
                                version_info = extract_cuda_version(result.stdout)
                                cuda_info = {
                                    'path': str(version_dir),
                                    'version': version_info,
                                    'nvcc_path': str(nvcc_path),
                                    'bin_path': str(version_dir / "bin"),
                                    'lib_path': str(version_dir / "lib" / "x64"),
                                    'include_path': str(version_dir / "include"),
                                    'active': is_cuda_in_path(str(version_dir / "bin"))
                                }
                                cuda_installations.append(cuda_info)
                                print(f"✅ 找到 CUDA {version_info}: {version_dir}")
                        except Exception as e:
                            print(f"⚠️  检查 {version_dir} 时出错: {e}")
    
    return cuda_installations

def extract_cuda_version(nvcc_output):
    """从 nvcc --version 输出中提取版本号"""
    for line in nvcc_output.split('\n'):
        if 'release' in line.lower():
            # 例如: "Cuda compilation tools, release 12.6, V12.6.20"
            try:
                version = line.split('release')[1].split(',')[0].strip()
                return version
            except:
                pass
    return "Unknown"

def is_cuda_in_path(cuda_bin_path):
    """检查指定的 CUDA bin 路径是否在系统 PATH 中"""
    current_path = os.environ.get('PATH', '')
    return cuda_bin_path.lower() in current_path.lower()

def show_cuda_installations(installations):
    """显示所有 CUDA 安装"""
    if not installations:
        print("❌ 没有找到任何 CUDA 安装")
        return
    
    print(f"\n📊 找到 {len(installations)} 个 CUDA 安装:")
    print("=" * 80)
    
    for i, cuda in enumerate(installations, 1):
        status = "🟢 活跃" if cuda['active'] else "⚪ 非活跃"
        print(f"{i}. CUDA {cuda['version']} {status}")
        print(f"   📍 路径: {cuda['path']}")
        print(f"   🔧 nvcc: {cuda['nvcc_path']}")
        print(f"   📁 bin: {cuda['bin_path']}")
        print(f"   📚 lib: {cuda['lib_path']}")
        print(f"   📄 include: {cuda['include_path']}")
        print()

def check_current_active_cuda():
    """检查当前活跃的 CUDA 版本"""
    print("🔍 检查当前活跃的 CUDA 版本...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = extract_cuda_version(result.stdout)
            which_result = subprocess.run(['where', 'nvcc'], capture_output=True, text=True)
            nvcc_path = which_result.stdout.strip() if which_result.returncode == 0 else "Unknown"
            
            print(f"✅ 当前活跃的 CUDA 版本: {version}")
            print(f"📍 nvcc 路径: {nvcc_path}")
            return version, nvcc_path
        else:
            print("❌ nvcc 命令不可用")
            return None, None
    except FileNotFoundError:
        print("❌ nvcc 命令未找到")
        return None, None

def switch_cuda_version(installations, target_version):
    """切换到指定的 CUDA 版本"""
    print(f"🔄 切换到 CUDA {target_version}...")
    
    # 找到目标版本
    target_cuda = None
    for cuda in installations:
        if cuda['version'] == target_version:
            target_cuda = cuda
            break
    
    if not target_cuda:
        print(f"❌ 未找到 CUDA {target_version}")
        return False
    
    # 移除所有 CUDA 路径从 PATH
    current_path = os.environ.get('PATH', '')
    path_parts = current_path.split(';')
    
    # 过滤掉所有 CUDA 路径
    filtered_parts = []
    for part in path_parts:
        if 'cuda' not in part.lower() or 'nvidia gpu computing toolkit' not in part.lower():
            filtered_parts.append(part)
    
    # 添加目标 CUDA 路径
    new_paths = [
        target_cuda['bin_path'],
        target_cuda['lib_path']
    ]
    
    new_path = ';'.join(new_paths + filtered_parts)
    
    # 更新环境变量
    os.environ['PATH'] = new_path
    os.environ['CUDA_HOME'] = target_cuda['path']
    os.environ['CUDA_PATH'] = target_cuda['path']
    
    print(f"✅ 已切换到 CUDA {target_version}")
    print(f"📍 CUDA_HOME: {target_cuda['path']}")
    
    # 验证切换
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            current_version = extract_cuda_version(result.stdout)
            if current_version == target_version:
                print(f"✅ 验证成功: 当前活跃版本为 {current_version}")
                return True
            else:
                print(f"⚠️  切换可能失败: 检测到版本 {current_version}")
                return False
        else:
            print("❌ nvcc 验证失败")
            return False
    except:
        print("❌ 无法验证 CUDA 切换")
        return False

def create_cuda_switch_script(installations):
    """创建 CUDA 版本切换脚本"""
    print("📝 创建 CUDA 版本切换脚本...")
    
    script_content = '''@echo off
setlocal enabledelayedexpansion

echo 🚀 CUDA 版本切换工具
echo ========================

'''
    
    # 添加每个 CUDA 版本的切换命令
    for i, cuda in enumerate(installations, 1):
        script_content += f'''
if "%1"=="{cuda['version']}" (
    echo 切换到 CUDA {cuda['version']}...
    set "CUDA_HOME={cuda['path']}"
    set "CUDA_PATH={cuda['path']}"
    set "PATH={cuda['bin_path']};%PATH%"
    echo ✅ 已切换到 CUDA {cuda['version']}
    nvcc --version
    goto :end
)
'''
    
    script_content += '''
echo 用法: switch_cuda.bat [版本号]
echo 可用版本:
'''
    
    for cuda in installations:
        script_content += f'echo   - {cuda["version"]}\n'
    
    script_content += '''
:end
'''
    
    script_path = Path("F:/mylab/SVG/RasterVectorStudio/scripts/switch_cuda.bat")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ 切换脚本已创建: {script_path}")
    return script_path

def recommend_cuda_for_diffvg():
    """为 DiffVG 推荐最佳的 CUDA 版本"""
    print("💡 为 DiffVG 推荐 CUDA 版本...")
    
    recommendations = {
        '12.9': {'score': 100, 'reason': '最新版本，完全支持 VS2022，最佳性能'},
        '12.6': {'score': 95, 'reason': '稳定版本，完全支持 VS2022，推荐使用'},
        '12.5': {'score': 90, 'reason': '稳定版本，支持 VS2022'},
        '12.4': {'score': 85, 'reason': '较新版本，支持 VS2022'},
        '12.3': {'score': 80, 'reason': '支持 VS2022'},
        '12.2': {'score': 75, 'reason': '支持 VS2022'},
        '12.1': {'score': 70, 'reason': '支持 VS2022'},
        '12.0': {'score': 65, 'reason': '支持 VS2022'},
        '11.8': {'score': 30, 'reason': '与 VS2022 兼容性问题'},
        '11.7': {'score': 25, 'reason': '较旧版本，不推荐'},
    }
    
    return recommendations

def save_cuda_config(installations):
    """保存 CUDA 配置信息"""
    config_file = Path("F:/mylab/SVG/RasterVectorStudio/config/cuda_config.json")
    config_file.parent.mkdir(exist_ok=True)
    
    config = {
        'last_scan': str(Path.cwd()),
        'installations': installations,
        'scan_time': str(Path.stat),
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已保存: {config_file}")
    except Exception as e:
        print(f"⚠️  保存配置失败: {e}")

def main():
    """主函数"""
    print("🚀 多 CUDA 版本检测和管理工具")
    print("=" * 60)
    
    # 1. 检测所有 CUDA 安装
    installations = detect_cuda_installations()
    
    # 2. 显示安装信息
    show_cuda_installations(installations)
    
    # 3. 检查当前活跃版本
    current_version, current_path = check_current_active_cuda()
    
    # 4. 获取推荐信息
    recommendations = recommend_cuda_for_diffvg()
    
    if installations:
        print("\n💡 DiffVG 编译推荐:")
        print("=" * 40)
        
        for cuda in installations:
            version = cuda['version']
            if version in recommendations:
                rec = recommendations[version]
                print(f"CUDA {version}: {rec['score']}/100 - {rec['reason']}")
        
        # 5. 提供选择
        print("\n🎯 选择操作:")
        print("1. 切换 CUDA 版本")
        print("2. 创建版本切换脚本")
        print("3. 使用当前版本编译 DiffVG")
        print("4. 保存配置并退出")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            print("\n可用的 CUDA 版本:")
            for i, cuda in enumerate(installations, 1):
                status = "🟢" if cuda['active'] else "⚪"
                print(f"{i}. {status} CUDA {cuda['version']}")
            
            try:
                index = int(input("选择版本 (输入序号): ")) - 1
                if 0 <= index < len(installations):
                    target_cuda = installations[index]
                    switch_cuda_version(installations, target_cuda['version'])
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效数字")
        
        elif choice == '2':
            create_cuda_switch_script(installations)
        
        elif choice == '3':
            print("🔨 准备使用当前 CUDA 版本编译 DiffVG...")
            print(f"当前版本: {current_version}")
            if current_version and current_version in recommendations:
                rec = recommendations[current_version]
                print(f"推荐指数: {rec['score']}/100")
                print(f"说明: {rec['reason']}")
                
                if rec['score'] >= 70:
                    print("✅ 当前版本适合编译 DiffVG")
                    response = input("是否继续编译? (y/N): ")
                    if response.lower() in ['y', 'yes']:
                        print("请运行: python scripts/compile_diffvg_cuda12.py")
                else:
                    print("⚠️  当前版本可能不是最佳选择")
                    print("建议切换到 CUDA 12.6 或更新版本")
        
        elif choice == '4':
            save_cuda_config(installations)
    
    else:
        print("❌ 没有找到任何 CUDA 安装")
        print("💡 请安装 CUDA 12.6 或更新版本")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
