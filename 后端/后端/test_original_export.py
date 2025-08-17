"""
测试原版导出功能
"""

import sys
import os

# 添加backup目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'backup_deleted_20250624_224708'))

def main():
    print("🧪 测试原版导出功能")
    print("=" * 50)
    
    try:
        # 导入原版模块
        from working_trader_FIXED import export_holdings
        
        print("\n📊 测试原版持仓导出...")
        success = export_holdings()
        
        if success:
            print("✅ 原版导出操作完成")
            
            # 检查文件是否存在
            import glob
            import os
            
            print("\n🔍 检查导出文件...")
            
            # 检查可能的保存路径
            possible_paths = [
                ".",
                "C:\\Users\\%USERNAME%\\Documents",
                "C:\\Users\\%USERNAME%\\Desktop",
            ]
            
            found_files = []
            for path in possible_paths:
                try:
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        files = glob.glob(os.path.join(expanded_path, "*持仓数据*.csv"))
                        if files:
                            # 按修改时间排序,获取最新的
                            latest_files = sorted(files, key=os.path.getmtime, reverse=True)[:3]
                            print(f"✅ 在 {expanded_path} 找到最新文件:")
                            for f in latest_files:
                                mtime = os.path.getmtime(f)
                                import datetime
                                time_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                                print(f"   - {os.path.basename(f)} ({time_str})")
                            found_files.extend(latest_files)
                        else:
                            print(f"❌ 在 {expanded_path} 未找到文件")
                except Exception as e:
                    print(f"❌ 检查路径 {path} 失败: {e}")
            
            if found_files:
                print(f"\n✅ 总共找到 {len(found_files)} 个文件")
            else:
                print("\n❌ 没有找到任何导出文件")
                
        else:
            print("❌ 原版导出操作失败")
            
    except Exception as e:
        print(f"❌ 导入原版模块失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
