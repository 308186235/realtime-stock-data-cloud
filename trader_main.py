"""
交易程序主界面
提供用户交互菜单,整合所有功能模块
"""

from trader_api import api

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("🎯 股票交易自动化程序 v2.0 (模块化版本)")
    print("=" * 50)
    print("📈 交易功能:")
    print("  1. 买入股票")
    print("  2. 卖出股票")
    print("")
    print("📊 导出功能:")
    print("  3. 导出持仓数据")
    print("  4. 导出成交数据")
    print("  5. 导出委托数据")
    print("  6. 导出所有数据")
    print("")
    print("🔧 管理功能:")
    print("  7. 查看文件列表")
    print("  8. 清理过期文件")
    print("  9. 查看系统状态")
    print("")
    print("  0. 退出程序")
    print("-" * 50)

def handle_buy():
    """处理买入操作"""
    print("\n📈 买入股票")
    print("-" * 30)
    
    code = input("股票代码 (如 000001): ").strip()
    if not code:
        print("❌ 股票代码不能为空")
        return
    
    quantity = input("买入数量 (如 100): ").strip()
    if not quantity:
        print("❌ 买入数量不能为空")
        return
    
    price = input("买入价格 (如 10.50,回车=市价): ").strip()
    if not price:
        price = "市价"
    
    print(f"\n确认买入: {code} {quantity}股 @ {price}")
    confirm = input("确认执行? (y/N): ").strip().lower()
    
    if confirm == 'y':
        result = api.buy(code, quantity, price)
        if result:
            print("✅ 买入操作完成")
        else:
            print("❌ 买入操作失败")
    else:
        print("❌ 操作已取消")

def handle_sell():
    """处理卖出操作"""
    print("\n📉 卖出股票")
    print("-" * 30)
    
    code = input("股票代码 (如 000001): ").strip()
    if not code:
        print("❌ 股票代码不能为空")
        return
    
    quantity = input("卖出数量 (如 100): ").strip()
    if not quantity:
        print("❌ 卖出数量不能为空")
        return
    
    price = input("卖出价格 (如 10.60,回车=市价): ").strip()
    if not price:
        price = "市价"
    
    print(f"\n确认卖出: {code} {quantity}股 @ {price}")
    confirm = input("确认执行? (y/N): ").strip().lower()
    
    if confirm == 'y':
        result = api.sell(code, quantity, price)
        if result:
            print("✅ 卖出操作完成")
        else:
            print("❌ 卖出操作失败")
    else:
        print("❌ 操作已取消")

def handle_export_single(export_type):
    """处理单项导出"""
    export_map = {
        "holdings": ("持仓数据", api.export_positions),
        "transactions": ("成交数据", api.export_trades),
        "orders": ("委托数据", api.export_orders)
    }
    
    if export_type not in export_map:
        print("❌ 未知的导出类型")
        return
    
    name, func = export_map[export_type]
    print(f"\n📊 导出{name}")
    
    result = func()
    if result:
        print(f"✅ {name}导出完成")
    else:
        print(f"❌ {name}导出失败")

def handle_export_all():
    """处理导出所有数据"""
    print("\n📊 导出所有数据")
    print("这将导出持仓,成交,委托三类数据...")
    
    confirm = input("确认执行? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    results = api.export_all()
    
    print("\n导出结果:")
    success_count = 0
    for data_type, success in results.items():
        status = "✅" if success else "❌"
        type_name = {"holdings": "持仓", "transactions": "成交", "orders": "委托"}[data_type]
        print(f"  {status} {type_name}数据")
        if success:
            success_count += 1
    
    print(f"\n总结: {success_count}/3 项导出成功")

def handle_file_list():
    """处理文件列表查看"""
    print("\n📁 导出文件列表")
    print("-" * 30)
    
    files = api.get_files()
    
    for file_type, file_list in files.items():
        type_name = {"holdings": "持仓数据", "transactions": "成交数据", "orders": "委托数据"}[file_type]
        print(f"\n{type_name} ({len(file_list)} 个文件):")
        
        if not file_list:
            print("  (无文件)")
        else:
            for i, file in enumerate(file_list[-5:], 1):  # 只显示最新5个
                print(f"  {i}. {file}")
            
            if len(file_list) > 5:
                print(f"  ... (还有 {len(file_list) - 5} 个文件)")

def handle_cleanup():
    """处理清理过期文件"""
    print("\n🧹 清理过期文件")
    print("将删除15点前的过期导出文件...")
    
    confirm = input("确认执行? (y/N): ").strip().lower()
    if confirm == 'y':
        api.cleanup_files()
        print("✅ 清理完成")
    else:
        print("❌ 操作已取消")

def handle_status():
    """处理状态查看"""
    print("\n🔍 系统状态")
    print("-" * 30)
    
    status = api.get_status()
    
    print(f"当前窗口: {status['current_window']}")
    print(f"交易软件激活: {'✅' if status['trading_software_active'] else '❌'}")
    
    print(f"\n导出文件统计:")
    files = status['export_files']
    print(f"  持仓数据: {files['holdings_count']} 个文件")
    print(f"  成交数据: {files['transactions_count']} 个文件")
    print(f"  委托数据: {files['orders_count']} 个文件")
    print(f"  总计: {sum(files.values())} 个文件")

def main():
    """主程序"""
    print("🚀 启动交易程序...")
    
    while True:
        try:
            show_menu()
            choice = input("请选择 (0-9): ").strip()
            
            if choice == "0":
                print("\n👋 退出程序")
                break
            elif choice == "1":
                handle_buy()
            elif choice == "2":
                handle_sell()
            elif choice == "3":
                handle_export_single("holdings")
            elif choice == "4":
                handle_export_single("transactions")
            elif choice == "5":
                handle_export_single("orders")
            elif choice == "6":
                handle_export_all()
            elif choice == "7":
                handle_file_list()
            elif choice == "8":
                handle_cleanup()
            elif choice == "9":
                handle_status()
            else:
                print("❌ 无效选择,请重新输入")
            
            # 等待用户按键继续
            if choice != "0":
                input("\n按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断,退出")
            break
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
