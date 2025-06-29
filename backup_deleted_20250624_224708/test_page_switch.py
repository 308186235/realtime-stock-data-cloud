import win32gui
import win32api
import win32con
import time

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    print(f"当前Caps Lock状态: {caps_state}")
    
    if caps_state == 0:
        print("开启Caps Lock...")
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        new_state = win32api.GetKeyState(win32con.VK_CAPITAL)
        print(f"开启后Caps Lock状态: {new_state}")
        return new_state != 0
    else:
        print("Caps Lock已开启")
        return True

def switch_to_trading_software():
    """切换到交易软件"""
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # 验证是否成功
            current_hwnd = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_hwnd)
            print(f"当前前台窗口: {current_title}")
            
            return hwnd == current_hwnd
        else:
            print("❌ 没找到交易软件窗口")
            return False
    except Exception as e:
        print(f"❌ 切换窗口失败: {e}")
        return False

def test_single_key(key_name, vk_code):
    """测试单个按键"""
    print(f"\n{'='*50}")
    print(f"测试 {key_name} 键...")
    print(f"{'='*50}")
    
    # 确保Caps Lock开启
    if not ensure_caps_lock_on():
        print("❌ 无法开启Caps Lock")
        return
    
    # 切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件")
        return
    
    print(f"准备发送 {key_name} 键...")
    print("请观察交易软件是否切换页面...")
    time.sleep(2)
    
    # 发送按键
    print(f"发送 {key_name} 键...")
    win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    
    print(f"{key_name} 键发送完成！")
    print("等待5秒观察效果...")
    time.sleep(5)
    
    # 询问用户结果
    result = input(f"{key_name} 键是否切换了页面？(y/n): ").strip().lower()
    return result == 'y'

def main():
    print("🔍 测试W/E/R键页面切换功能")
    print("请确保交易软件已经打开并可见")
    input("按回车开始测试...")
    
    results = {}
    
    # 测试W键
    results['W'] = test_single_key("W", 0x57)
    
    # 测试E键
    results['E'] = test_single_key("E", 0x45)
    
    # 测试R键
    results['R'] = test_single_key("R", 0x52)
    
    # 显示结果
    print(f"\n{'='*50}")
    print("测试结果汇总:")
    print(f"{'='*50}")
    for key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{key} 键: {status}")
    
    # 如果都失败，给出建议
    if not any(results.values()):
        print("\n🤔 所有按键都没有切换页面，可能的原因：")
        print("1. 交易软件版本不支持W/E/R快捷键")
        print("2. 需要特殊的窗口状态或焦点")
        print("3. 需要先点击特定区域")
        print("4. 快捷键被禁用或重新映射")
        print("\n💡 建议：")
        print("1. 手动测试W/E/R键是否能切换页面")
        print("2. 查看交易软件的快捷键设置")
        print("3. 尝试其他切换方式（如点击标签页）")

if __name__ == "__main__":
    main()
