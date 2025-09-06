#!/usr/bin/env python3
"""
CUDA 升级脚本 - 从 CUDA 11.8 升级到 CUDA 12.6
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path
import tempfile
import time

def check_current_cuda():
    """检查当前 CUDA 版本"""
    print("🔍 检查当前 CUDA 版本...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("当前 CUDA 版本:")
            print(result.stdout)
            return True
        else:
            print("❌ 无法检测到 CUDA")
            return False
    except FileNotFoundError:
        print("❌ nvcc 命令未找到，CUDA 可能未安装")
        return False

def download_cuda_installer():
    """下载 CUDA 12.6 安装程序到 D 盘"""
    print("📥 下载 CUDA 12.6 安装程序到 D 盘...")
    
    # CUDA 12.6 下载链接
    cuda_url = "https://developer.download.nvidia.com/compute/cuda/12.6.0/network_installers/cuda_12.6.0_windows_network.exe"
    
    # 在 D 盘创建下载目录
    download_dir = Path("D:/Downloads/CUDA")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    installer_path = download_dir / "cuda_12.6.0_windows_network.exe"
    
    # 如果文件已存在，询问是否重新下载
    if installer_path.exists():
        print(f"文件已存在: {installer_path}")
        response = input("是否重新下载? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("使用现有文件")
            return installer_path
        else:
            print("删除现有文件，重新下载...")
            installer_path.unlink()
    
    try:
        print(f"正在下载到: {installer_path}")
        print("文件大小: 约 3MB (网络安装器)")
        
        # 下载并显示进度
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                print(f"\r下载进度: {percent}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)", end="")
        
        urllib.request.urlretrieve(cuda_url, installer_path, reporthook=show_progress)
        print("\n✅ CUDA 安装程序下载完成!")
        print(f"保存位置: {installer_path}")
        return installer_path
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("💡 备选方案:")
        print("1. 手动访问: https://developer.nvidia.com/cuda-downloads")
        print("2. 下载 CUDA 12.6 for Windows")
        print("3. 保存到 D:/Downloads/CUDA/ 目录")
        return None

def uninstall_old_cuda():
    """卸载旧版本 CUDA"""
    print("🗑️  卸载旧版本 CUDA...")
    
    # 查找已安装的 CUDA 版本
    cuda_programs = []
    
    try:
        # 使用 wmic 查找 CUDA 相关程序
        result = subprocess.run([
            'wmic', 'product', 'where', 
            'name like "%CUDA%"', 
            'get', 'name,version'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # 跳过标题行
                if line.strip() and 'CUDA' in line:
                    cuda_programs.append(line.strip())
        
        if cuda_programs:
            print("找到以下 CUDA 程序:")
            for program in cuda_programs:
                print(f"  - {program}")
            
            # 询问是否卸载
            response = input("是否卸载这些程序? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                print("正在卸载旧版本 CUDA...")
                print("⚠️  请通过控制面板 -> 程序和功能 手动卸载 CUDA 11.8")
                print("⚠️  或者使用 NVIDIA 卸载工具")
                input("卸载完成后按 Enter 继续...")
            else:
                print("跳过卸载，直接安装新版本")
                print("⚠️  建议先卸载旧版本以避免冲突")
        else:
            print("没有找到已安装的 CUDA 程序")
            
    except Exception as e:
        print(f"❌ 检查已安装程序失败: {e}")
        print("请手动检查并卸载旧版本 CUDA")

def install_cuda(installer_path):
    """安装新版本 CUDA"""
    print("📦 安装 CUDA 12.6...")
    
    if not installer_path.exists():
        print(f"❌ 安装程序不存在: {installer_path}")
        return False
    
    try:
        print("🚀 启动 CUDA 安装程序...")
        print("\n📋 安装指南:")
        print("   1. 选择 '自定义安装'")
        print("   2. 勾选 'CUDA Toolkit'")
        print("   3. 如果显卡驱动已是最新，可跳过驱动程序")
        print("   4. 选择安装位置 (建议默认: C:\\Program Files\\NVIDIA GPU Computing Toolkit)")
        print("   5. 等待安装完成")
        print("\n⚠️  安装程序需要管理员权限")
        
        input("按 Enter 启动安装程序...")
        
        # 启动安装程序
        subprocess.run([str(installer_path)], check=False)
        
        print("\n安装程序已启动")
        print("请按照上述指南完成安装")
        input("安装完成后按 Enter 继续...")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动安装程序失败: {e}")
        return False

def verify_cuda_installation():
    """验证 CUDA 安装"""
    print("✅ 验证 CUDA 安装...")
    
    # 等待一下让系统更新环境变量
    print("等待环境变量更新...")
    time.sleep(3)
    
    try:
        # 检查 nvcc
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CUDA 编译器验证成功:")
            print(result.stdout)
            
            # 提取版本号
            for line in result.stdout.split('\n'):
                if 'release' in line.lower():
                    print(f"🎉 安装的 CUDA 版本: {line.strip()}")
                    
        else:
            print("❌ CUDA 编译器验证失败")
            return False
        
        # 检查 PyTorch CUDA 支持
        try:
            import torch
            if torch.cuda.is_available():
                print(f"✅ PyTorch CUDA 支持: {torch.version.cuda}")
                print(f"✅ 检测到 GPU: {torch.cuda.get_device_name(0)}")
                print(f"✅ GPU 数量: {torch.cuda.device_count()}")
            else:
                print("⚠️  PyTorch 检测不到 CUDA 支持")
                print("💡 可能需要重新安装 PyTorch")
        except ImportError:
            print("⚠️  PyTorch 未安装")
        
        return True
        
    except FileNotFoundError:
        print("❌ nvcc 仍然未找到")
        print("\n💡 故障排除:")
        print("1. 重启计算机")
        print("2. 检查环境变量 PATH 中是否包含:")
        print("   C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6\\bin")
        print("3. 手动添加 CUDA bin 目录到 PATH")
        return False

def update_environment_variables():
    """更新环境变量"""
    print("🔧 更新当前会话的环境变量...")
    
    # 检查可能的 CUDA 12.x 安装路径
    possible_cuda_versions = ['v12.6', 'v12.5', 'v12.4', 'v12.3', 'v12.2', 'v12.1', 'v12.0']
    cuda_found = False
    
    for version in possible_cuda_versions:
        cuda_base = f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\{version}"
        if Path(cuda_base).exists():
            print(f"✅ 找到 CUDA {version}: {cuda_base}")
            
            cuda_paths = [
                cuda_base,
                cuda_base + "\\bin",
                cuda_base + "\\libnvvp",
            ]
            
            current_path = os.environ.get('PATH', '')
            
            for cuda_path in cuda_paths:
                if Path(cuda_path).exists() and cuda_path not in current_path:
                    print(f"添加到 PATH: {cuda_path}")
                    os.environ['PATH'] = f"{cuda_path};{current_path}"
                    current_path = os.environ['PATH']
            
            # 设置 CUDA_HOME
            os.environ['CUDA_HOME'] = cuda_base
            os.environ['CUDA_PATH'] = cuda_base
            print(f"设置 CUDA_HOME: {cuda_base}")
            cuda_found = True
            break
    
    if not cuda_found:
        print("⚠️  未找到 CUDA 12.x 安装，请检查安装是否成功")

def reinstall_pytorch():
    """重新安装 PyTorch 以支持新的 CUDA 版本"""
    print("🔄 重新安装 PyTorch for CUDA 12.x...")
    
    try:
        print("卸载现有的 PyTorch...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'uninstall', 
            'torch', 'torchvision', 'torchaudio', '-y'
        ], check=False)
        
        print("安装支持 CUDA 12.x 的 PyTorch...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'torch', 'torchvision', 'torchaudio', 
            '--index-url', 'https://download.pytorch.org/whl/cu121'
        ], check=True)
        
        print("✅ PyTorch 重新安装完成")
        
        # 验证 PyTorch CUDA 支持
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 支持: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyTorch 重新安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 CUDA 升级脚本")
    print("=" * 60)
    print("从 CUDA 11.8 升级到 CUDA 12.6")
    print("下载位置: D:/Downloads/CUDA/")
    print("=" * 60)
    
    # 1. 检查当前版本
    current_cuda_exists = check_current_cuda()
    
    # 2. 询问是否继续
    if current_cuda_exists:
        print("\n⚠️  检测到现有 CUDA 版本")
        response = input("是否继续升级到 CUDA 12.6? (y/N): ").lower().strip()
    else:
        response = input("\n是否安装 CUDA 12.6? (y/N): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print("取消操作")
        return
    
    # 3. 下载安装程序到 D 盘
    installer_path = download_cuda_installer()
    if not installer_path:
        print("❌ 无法下载 CUDA 安装程序")
        print("请手动下载并重新运行脚本")
        return
    
    # 4. 卸载旧版本 (可选)
    if current_cuda_exists:
        uninstall_old_cuda()
    
    # 5. 安装新版本
    if not install_cuda(installer_path):
        print("❌ CUDA 安装失败")
        return
    
    # 6. 更新环境变量
    update_environment_variables()
    
    # 7. 验证安装
    if verify_cuda_installation():
        print("\n✅ CUDA 验证成功!")
        
        # 8. 重新安装 PyTorch
        pytorch_success = reinstall_pytorch()
        
        print("\n🎉 CUDA 升级完成!")
        print("\n📋 下一步:")
        print("1. 重启计算机以确保环境变量永久生效")
        print("2. 重新打开终端/PowerShell")
        print("3. 运行 DiffVG 编译脚本")
        print("4. 测试 DiffVG 功能")
        
        if pytorch_success:
            print("\n✅ PyTorch 也已更新为 CUDA 12.x 版本")
        
    else:
        print("\n❌ CUDA 验证失败")
        print("\n💡 故障排除步骤:")
        print("1. 检查安装是否真正完成")
        print("2. 重启计算机")
        print("3. 手动添加 CUDA 到系统 PATH")
        print("4. 检查显卡驱动程序兼容性")
        print("5. 重新运行此脚本验证")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 请将错误信息报告给开发者")