"""
清理无用的交易相关文件，保留核心工作代码
"""

import os
import shutil
from datetime import datetime

def create_backup_folder():
    """创建备份文件夹"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"backup_unused_{timestamp}"
    os.makedirs(backup_folder, exist_ok=True)
    return backup_folder

def move_file_to_backup(file_path, backup_folder):
    """移动文件到备份文件夹"""
    if os.path.exists(file_path):
        try:
            shutil.move(file_path, os.path.join(backup_folder, os.path.basename(file_path)))
            print(f"✅ 移动: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 移动失败 {file_path}: {e}")
            return False
    return False

def cleanup_unused_files():
    """清理无用文件"""
    print("🧹 开始清理无用的交易相关文件")
    print("=" * 60)
    
    # 创建备份文件夹
    backup_folder = create_backup_folder()
    print(f"📁 备份文件夹: {backup_folder}")
    
    # 需要移出的无用余额获取器（保留fixed_balance_reader.py）
    unused_balance_files = [
        "winapi_balance_reader.py",
        "final_balance_reader.py", 
        "improved_balance_reader.py"
    ]
    
    # 需要移出的无用导出模块（保留trader_export.py）
    unused_export_files = [
        "trader_export_original.py",
        "trader_export_real.py"
    ]
    
    # 需要移出的旧核心模块（保留trader_core_original.py）
    unused_core_files = [
        "trader_core.py"  # 已被trader_core_original.py替代
    ]
    
    # 需要移出的其他无用交易文件
    unused_trader_files = [
        "working_trader.py",  # 保留backup中的working_trader_FIXED.py
        "trader_api.py",
        "trader_api_real.py",
        "trader_buy_sell.py",
        "trader_main.py"
    ]
    
    # 统计
    moved_count = 0
    total_files = len(unused_balance_files) + len(unused_export_files) + len(unused_core_files) + len(unused_trader_files)
    
    print(f"\n📊 计划移动 {total_files} 个文件")
    print("-" * 40)
    
    # 移动无用余额获取器
    print("\n🔄 移动无用余额获取器...")
    for file in unused_balance_files:
        if move_file_to_backup(file, backup_folder):
            moved_count += 1
    
    # 移动无用导出模块
    print("\n🔄 移动无用导出模块...")
    for file in unused_export_files:
        if move_file_to_backup(file, backup_folder):
            moved_count += 1
    
    # 移动旧核心模块
    print("\n🔄 移动旧核心模块...")
    for file in unused_core_files:
        if move_file_to_backup(file, backup_folder):
            moved_count += 1
    
    # 移动其他无用交易文件
    print("\n🔄 移动其他无用交易文件...")
    for file in unused_trader_files:
        if move_file_to_backup(file, backup_folder):
            moved_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 清理完成! 移动了 {moved_count}/{total_files} 个文件")
    print(f"📁 备份位置: {backup_folder}")
    
    # 显示保留的核心文件
    print("\n📋 保留的核心工作文件:")
    core_files = [
        "backup_deleted_20250624_224708/working_trader_FIXED.py",  # 原版源代码
        "trader_core_original.py",  # 模块化核心
        "trader_export.py",  # 模块化导出
        "fixed_balance_reader.py",  # 余额获取
        "test_*.py",  # 测试文件
        "*.csv"  # 导出的数据文件
    ]
    
    for file in core_files:
        print(f"  ✅ {file}")
    
    return moved_count

if __name__ == "__main__":
    cleanup_unused_files()
