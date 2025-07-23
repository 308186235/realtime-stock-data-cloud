"""
演示交易软件导出系统
展示导出文件格式和自动清理功能
"""

import os
import glob
import time
from datetime import datetime, time as dt_time, timedelta
import csv

def create_sample_export_files():
    """创建示例导出文件"""
    print("📁 创建示例导出文件...")
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    
    # 1. 创建持仓数据文件
    holdings_file = f"持仓数据_{timestamp}.csv"
    holdings_data = [
        ["证券代码", "证券名称", "股票余额", "可用余额", "冻结数量", "盈亏", "市值", "成本价", "现价"],
        ["000001", "平安银行", "1000", "1000", "0", "+150.00", "12500.00", "12.35", "12.50"],
        ["000002", "万科A", "500", "500", "0", "-25.00", "5475.00", "11.00", "10.95"],
        ["600036", "招商银行", "800", "800", "0", "+320.00", "28800.00", "35.60", "36.00"]
    ]
    
    with open(holdings_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(holdings_data)
    print(f"   ✅ 创建持仓数据: {holdings_file}")
    
    # 2. 创建成交数据文件
    transactions_file = f"成交数据_{timestamp}.csv"
    transactions_data = [
        ["成交时间", "证券代码", "证券名称", "买卖方向", "成交价格", "成交数量", "成交金额", "手续费"],
        ["09:30:15", "000001", "平安银行", "买入", "12.35", "1000", "12350.00", "12.35"],
        ["10:15:30", "000002", "万科A", "买入", "11.00", "500", "5500.00", "5.50"],
        ["14:30:45", "600036", "招商银行", "买入", "35.60", "800", "28480.00", "28.48"]
    ]
    
    with open(transactions_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(transactions_data)
    print(f"   ✅ 创建成交数据: {transactions_file}")
    
    # 3. 创建委托数据文件
    orders_file = f"委托数据_{timestamp}.csv"
    orders_data = [
        ["委托时间", "证券代码", "证券名称", "买卖方向", "委托价格", "委托数量", "成交数量", "撤单数量", "委托状态"],
        ["09:25:00", "000001", "平安银行", "买入", "12.35", "1000", "1000", "0", "已成交"],
        ["10:10:00", "000002", "万科A", "买入", "11.00", "500", "500", "0", "已成交"],
        ["14:25:00", "600036", "招商银行", "买入", "35.60", "800", "800", "0", "已成交"],
        ["14:55:00", "000858", "五粮液", "买入", "180.00", "100", "0", "100", "已撤单"]
    ]
    
    with open(orders_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(orders_data)
    print(f"   ✅ 创建委托数据: {orders_file}")
    
    return [holdings_file, transactions_file, orders_file]

def show_export_files():
    """显示当前导出文件"""
    print("\n📋 当前导出文件:")
    
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
            print(f"  📄 {file}")
            print(f"     时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     大小: {file_size} 字节")
        total_files += len(files)
    
    print(f"\n总计: {total_files} 个导出文件")

def show_file_content(filename):
    """显示文件内容"""
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return
    
    print(f"\n📖 文件内容: {filename}")
    print("-" * 50)
    
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def demo_cleanup_system():
    """演示清理系统"""
    print("\n🧹 演示自动清理系统")
    print("=" * 40)
    
    # 获取当前时间
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断过期时间:今天15点
    today_3pm = datetime.combine(now.date(), dt_time(15, 0))
    
    # 如果现在还没到15点,则以昨天15点为过期时间
    if now < today_3pm:
        yesterday_3pm = today_3pm - timedelta(days=1)
        cutoff_time = yesterday_3pm
        print(f"过期标准: 昨天15:00后的文件")
        print(f"过期时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        cutoff_time = today_3pm
        print(f"过期标准: 今天15:00后的文件")
        print(f"过期时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查文件是否过期
    patterns = [
        "持仓数据_*.csv",
        "成交数据_*.csv", 
        "委托数据_*.csv"
    ]
    
    print(f"\n检查过期文件:")
    expired_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                is_expired = file_time < cutoff_time
                status = "🗑️ 过期" if is_expired else "✅ 有效"
                print(f"  {status} {file_path} (修改时间: {file_time.strftime('%H:%M:%S')})")
                if is_expired:
                    expired_files.append(file_path)
            except Exception as e:
                print(f"  ❌ 检查文件失败 {file_path}: {e}")
    
    if expired_files:
        print(f"\n发现 {len(expired_files)} 个过期文件")
        print("注意: 在实际系统中,这些文件会被自动删除")
    else:
        print(f"\n✅ 没有过期文件")

def main():
    """主函数"""
    print("🎯 交易软件导出系统演示")
    print("=" * 50)
    
    # 1. 显示当前文件状态
    show_export_files()
    
    # 2. 创建示例文件
    print(f"\n" + "=" * 50)
    created_files = create_sample_export_files()
    
    # 3. 再次显示文件状态
    print(f"\n" + "=" * 50)
    show_export_files()
    
    # 4. 显示文件内容示例
    if created_files:
        print(f"\n" + "=" * 50)
        print("📖 文件内容示例:")
        show_file_content(created_files[0])  # 显示持仓数据
    
    # 5. 演示清理系统
    print(f"\n" + "=" * 50)
    demo_cleanup_system()
    
    print(f"\n" + "=" * 50)
    print("✅ 演示完成!")
    print("\n说明:")
    print("- 交易软件会自动导出持仓,成交,委托数据为CSV文件")
    print("- 文件名格式: [数据类型]_[月日_时分秒].csv")
    print("- 系统会在每天15:00后自动清理过期文件")
    print("- 文件采用UTF-8-BOM编码,确保中文正确显示")

if __name__ == "__main__":
    main()
