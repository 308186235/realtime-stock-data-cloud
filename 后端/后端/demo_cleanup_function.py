"""
演示交易软件自动清理功能
创建模拟的过期文件并演示清理过程
"""

import os
import glob
import time
from datetime import datetime, time as dt_time, timedelta
import csv

def create_old_export_files():
    """创建模拟的过期导出文件"""
    print("📁 创建模拟过期文件...")
    
    # 创建昨天的时间戳 (模拟过期文件)
    yesterday = datetime.now() - timedelta(days=1)
    old_timestamp = yesterday.strftime("%m%d_%H%M%S")
    
    # 创建过期文件
    old_files = []
    
    # 1. 过期持仓数据
    old_holdings = f"持仓数据_{old_timestamp}.csv"
    with open(old_holdings, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ["证券代码", "证券名称", "股票余额", "可用余额", "冻结数量", "盈亏", "市值", "成本价", "现价"],
            ["000001", "平安银行", "500", "500", "0", "+75.00", "6250.00", "12.35", "12.50"]
        ])
    old_files.append(old_holdings)
    
    # 2. 过期成交数据
    old_transactions = f"成交数据_{old_timestamp}.csv"
    with open(old_transactions, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ["成交时间", "证券代码", "证券名称", "买卖方向", "成交价格", "成交数量", "成交金额", "手续费"],
            ["09:30:15", "000001", "平安银行", "买入", "12.35", "500", "6175.00", "6.18"]
        ])
    old_files.append(old_transactions)
    
    # 3. 过期委托数据
    old_orders = f"委托数据_{old_timestamp}.csv"
    with open(old_orders, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ["委托时间", "证券代码", "证券名称", "买卖方向", "委托价格", "委托数量", "成交数量", "撤单数量", "委托状态"],
            ["09:25:00", "000001", "平安银行", "买入", "12.35", "500", "500", "0", "已成交"]
        ])
    old_files.append(old_orders)
    
    # 修改文件时间为昨天 (模拟过期)
    yesterday_timestamp = yesterday.timestamp()
    for file_path in old_files:
        os.utime(file_path, (yesterday_timestamp, yesterday_timestamp))
        print(f"   📄 创建过期文件: {file_path}")
    
    return old_files

def cleanup_old_export_files():
    """清理过期的导出文件(15点后为过期) - 从trader_core.py复制"""
    try:
        print("🧹 清理过期导出文件...")
        
        # 获取当前时间
        now = datetime.now()
        
        # 判断过期时间:今天15点
        today_3pm = datetime.combine(now.date(), dt_time(15, 0))
        
        # 如果现在还没到15点,则以昨天15点为过期时间
        if now < today_3pm:
            yesterday_3pm = today_3pm - timedelta(days=1)
            cutoff_time = yesterday_3pm
            print(f"   当前时间: {now.strftime('%H:%M')}")
            print(f"   过期标准: 昨天15:00后的文件")
        else:
            cutoff_time = today_3pm
            print(f"   当前时间: {now.strftime('%H:%M')}")
            print(f"   过期标准: 今天15:00后的文件")
        
        # 查找所有导出文件
        patterns = [
            "持仓数据_*.csv",
            "成交数据_*.csv", 
            "委托数据_*.csv",
            "测试过期文件_*.csv"
        ]
        
        deleted_count = 0
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    # 获取文件修改时间
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 如果文件在15点后,删除它
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        print(f"   🗑️ 删除过期文件: {file_path}")
                        deleted_count += 1
                        
                except Exception as e:
                    print(f"   ❌ 删除文件失败 {file_path}: {e}")
        
        if deleted_count > 0:
            print(f"   ✅ 清理完成,删除了 {deleted_count} 个过期文件")
        else:
            print(f"   ✅ 没有过期文件需要清理")
            
    except Exception as e:
        print(f"   ❌ 清理过期文件失败: {e}")

def show_all_export_files():
    """显示所有导出文件"""
    print("\n📋 当前所有导出文件:")
    
    patterns = [
        ("持仓数据", "持仓数据_*.csv"),
        ("成交数据", "成交数据_*.csv"),
        ("委托数据", "委托数据_*.csv")
    ]
    
    total_files = 0
    for name, pattern in patterns:
        files = glob.glob(pattern)
        print(f"\n{name}: {len(files)} 个文件")
        for file in files:
            file_time = datetime.fromtimestamp(os.path.getmtime(file))
            file_size = os.path.getsize(file)
            
            # 判断是否过期
            now = datetime.now()
            today_3pm = datetime.combine(now.date(), dt_time(15, 0))
            if now < today_3pm:
                cutoff_time = today_3pm - timedelta(days=1)
            else:
                cutoff_time = today_3pm
            
            is_expired = file_time < cutoff_time
            status = "🗑️ 过期" if is_expired else "✅ 有效"
            
            print(f"  📄 {file} {status}")
            print(f"     时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     大小: {file_size} 字节")
        total_files += len(files)
    
    print(f"\n总计: {total_files} 个导出文件")

def main():
    """主函数"""
    print("🎯 交易软件自动清理功能演示")
    print("=" * 50)
    
    # 1. 显示当前文件状态
    show_all_export_files()
    
    # 2. 创建模拟过期文件
    print(f"\n" + "=" * 50)
    old_files = create_old_export_files()
    
    # 3. 显示包含过期文件的状态
    print(f"\n" + "=" * 50)
    show_all_export_files()
    
    # 4. 执行清理
    print(f"\n" + "=" * 50)
    cleanup_old_export_files()
    
    # 5. 显示清理后的状态
    print(f"\n" + "=" * 50)
    show_all_export_files()
    
    print(f"\n" + "=" * 50)
    print("✅ 清理演示完成!")
    print("\n说明:")
    print("- 系统会自动检查所有导出文件的修改时间")
    print("- 在15:00之前,会删除昨天15:00之前的文件")
    print("- 在15:00之后,会删除今天15:00之前的文件")
    print("- 这确保了导出文件不会无限累积,节省磁盘空间")
    print("- 用户可以在交易日内随时查看当天的导出数据")

if __name__ == "__main__":
    main()
