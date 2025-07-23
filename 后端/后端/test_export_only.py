"""
简单测试导出功能
"""

import time
from trader_export import export_holdings

def main():
    print("🧪 测试导出功能")
    print("=" * 50)
    
    # 测试持仓导出
    print("\n📊 测试持仓导出...")
    success = export_holdings()
    
    if success:
        print("✅ 导出操作完成")
        
        # 检查文件是否存在
        import glob
        import os
        
        print("\n🔍 检查导出文件...")
        
        # 检查当前目录
        current_files = glob.glob("*.csv")
        print(f"当前目录CSV文件: {current_files}")
        
        # 检查可能的保存路径
        possible_paths = [
            ".",
            "C:\\Users\\%USERNAME%\\Documents",
            "C:\\Users\\%USERNAME%\\Desktop",
            "C:\\Program Files\\东吴证券",
            "C:\\Program Files (x86)\\东吴证券"
        ]
        
        for path in possible_paths:
            try:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    files = glob.glob(os.path.join(expanded_path, "*持仓数据*.csv"))
                    if files:
                        print(f"✅ 在 {expanded_path} 找到文件: {files}")
                        break
                    else:
                        print(f"❌ 在 {expanded_path} 未找到文件")
            except Exception as e:
                print(f"❌ 检查路径 {path} 失败: {e}")
    else:
        print("❌ 导出操作失败")

if __name__ == "__main__":
    main()
