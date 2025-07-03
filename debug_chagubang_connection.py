#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试茶股帮连接和数据接收
"""

import socket
import time
from datetime import datetime

# 茶股帮配置
CHAGUBANG_HOST = 'l1.chagubang.com'
CHAGUBANG_PORT = 6380
TOKEN = "QT_wat5QfcJ6N9pDZM5"

def debug_chagubang_connection():
    """调试茶股帮连接"""
    print("🔍 茶股帮连接调试")
    print("=" * 50)
    
    # 检查当前时间
    now = datetime.now()
    print(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
    
    # 判断是否在交易时间
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    hour = now.hour
    minute = now.minute
    
    is_trading_day = weekday < 5  # Monday to Friday
    is_morning_session = (9 <= hour < 11) or (hour == 11 and minute <= 30)
    is_afternoon_session = (13 <= hour < 15)
    is_trading_time = is_trading_day and (is_morning_session or is_afternoon_session)
    
    print(f"📊 交易时间检查:")
    print(f"   工作日: {'是' if is_trading_day else '否'}")
    print(f"   上午时段 (9:00-11:30): {'是' if is_morning_session else '否'}")
    print(f"   下午时段 (13:00-15:00): {'是' if is_afternoon_session else '否'}")
    print(f"   当前是交易时间: {'是' if is_trading_time else '否'}")
    
    if not is_trading_time:
        print("⚠️  当前不在交易时间，可能没有实时数据推送")
    
    print(f"\n🔗 尝试连接茶股帮服务器...")
    
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print(f"📡 连接到 {CHAGUBANG_HOST}:{CHAGUBANG_PORT}")
        sock.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
        print("✅ TCP连接成功")
        
        # 发送token
        print(f"📤 发送认证Token: {TOKEN}")
        sock.send(TOKEN.encode('utf-8'))
        print("✅ Token发送成功")
        
        # 尝试接收数据
        print(f"\n📥 等待数据接收 (30秒)...")
        sock.settimeout(2)
        
        received_count = 0
        raw_data_samples = []
        
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                data = sock.recv(4096)
                if data:
                    received_count += 1
                    decoded_data = data.decode('utf-8', errors='ignore')
                    
                    print(f"📦 接收数据包 #{received_count} (长度: {len(data)} 字节)")
                    
                    # 保存前几个数据样本
                    if len(raw_data_samples) < 5:
                        raw_data_samples.append(decoded_data[:200])  # 只保存前200个字符
                    
                    # 显示数据内容预览
                    preview = decoded_data[:100].replace('\n', '\\n').replace('\r', '\\r')
                    print(f"   内容预览: {preview}")
                    
                    # 检查是否包含股票数据特征
                    if any(marker in decoded_data for marker in ['SH', 'SZ', ',', '.']):
                        print("   ✅ 疑似包含股票数据")
                    else:
                        print("   ⚠️  数据格式不明")
                    
                else:
                    print("📭 接收到空数据")
                    
            except socket.timeout:
                print("⏱️  等待数据中...")
                continue
            except Exception as e:
                print(f"❌ 接收数据错误: {e}")
                break
        
        sock.close()
        
        # 总结结果
        print(f"\n📊 接收测试结果:")
        print(f"   接收数据包: {received_count} 个")
        print(f"   测试时长: 30 秒")
        
        if received_count > 0:
            print("✅ 成功接收到数据!")
            print(f"\n📄 数据样本:")
            for i, sample in enumerate(raw_data_samples, 1):
                print(f"   样本 {i}: {sample}")
        else:
            print("❌ 没有接收到任何数据")
            
            if not is_trading_time:
                print("💡 可能原因: 当前不在交易时间")
            else:
                print("💡 可能原因: Token无效或服务器问题")
        
        return received_count > 0
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_simple_socket():
    """测试简单socket连接"""
    print(f"\n🔧 测试基础Socket连接...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
        
        print("✅ 基础Socket连接成功")
        
        # 发送不同的测试数据
        test_messages = [
            TOKEN.encode('utf-8'),
            b'test',
            b'hello',
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"📤 发送测试消息 {i}: {msg}")
            sock.send(msg)
            
            try:
                response = sock.recv(1024)
                if response:
                    print(f"📥 收到响应: {response[:100]}")
                else:
                    print("📭 无响应")
            except socket.timeout:
                print("⏱️  响应超时")
            
            time.sleep(1)
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ 基础连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 茶股帮连接和数据接收调试工具")
    print("=" * 60)
    
    # 调试连接和数据接收
    success1 = debug_chagubang_connection()
    
    # 测试基础连接
    success2 = test_simple_socket()
    
    print(f"\n🎯 调试总结:")
    if success1:
        print("✅ Agent可以接收到茶股帮实时数据")
        print("✅ 数据推送正常工作")
    elif success2:
        print("✅ 网络连接正常")
        print("❌ 但没有接收到数据推送")
        print("💡 可能是交易时间或Token问题")
    else:
        print("❌ 网络连接存在问题")
        print("💡 请检查网络设置和服务器状态")

if __name__ == "__main__":
    main()
