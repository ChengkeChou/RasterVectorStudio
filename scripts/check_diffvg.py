#!/usr/bin/env python3
"""
DiffVG 状态检查脚本
"""

import sys
from pathlib import Path

def check_diffvg_status():
    """检查 DiffVG 状态"""
    print("🔍 检查 DiffVG 状态...")
    print("=" * 50)
    
    # 检查 PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA 可用: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch 未安装")
        print("   解决: pip install torch")
        return False
    
    # 检查 DiffVG 源代码
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    diffvg_dir = project_root / "third_party" / "diffvg"
    
    if diffvg_dir.exists():
        print(f"✅ DiffVG 源代码存在: {diffvg_dir}")
        setup_py = diffvg_dir / "setup.py"
        if setup_py.exists():
            print("✅ setup.py 存在")
        else:
            print("❌ setup.py 不存在")
    else:
        print(f"❌ DiffVG 源代码不存在: {diffvg_dir}")
        return False
    
    # 检查是否已编译
    try:
        import pydiffvg
        print("✅ pydiffvg 可以导入")
        
        # 测试基本功能
        try:
            pydiffvg.set_use_gpu(torch.cuda.is_available())
            device = pydiffvg.get_device()
            print(f"✅ DiffVG 设备: {device}")
            print("🎉 DiffVG 完全可用!")
            return True
        except Exception as e:
            print(f"⚠️  DiffVG 导入成功但初始化失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ pydiffvg 无法导入: {e}")
        print("   解决: python scripts/compile_diffvg.py")
        return False
    
    # 检查可选依赖
    try:
        import lpips
        print("✅ LPIPS 可用 (感知损失)")
    except ImportError:
        print("⚠️  LPIPS 不可用 (可选)")
        print("   安装: pip install lpips")
    
    try:
        import skimage
        print("✅ scikit-image 可用")
    except ImportError:
        print("❌ scikit-image 不可用")
        print("   安装: pip install scikit-image")

def main():
    """主函数"""
    available = check_diffvg_status()
    
    print("\n" + "=" * 50)
    if available:
        print("🎉 DiffVG 状态: 完全可用")
        print("现在可以在应用中使用深度学习矢量化功能!")
    else:
        print("⚠️  DiffVG 状态: 不可用")
        print("\n📋 建议的解决步骤:")
        print("1. 确保安装了 PyTorch: pip install torch")
        print("2. 编译 DiffVG: python scripts/compile_diffvg.py")
        print("3. 安装依赖: pip install scikit-image lpips")
        print("4. 重新检查: python scripts/check_diffvg.py")
    
    return available

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
