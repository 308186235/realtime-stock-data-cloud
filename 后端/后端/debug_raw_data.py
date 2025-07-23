#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试茶股帮原始数据接收
"""

import socket
import time
from datetime import datetime

# 茶股帮配置
HOST = 'l1.chagubang.com'
PORT = 6380
TOKEN = "process.env.STOCK_API_KEY"

def debug_raw_data():
    """调试原始数据接收"""
    print("🔍 茶股帮原始数据调试")
    print("=" * 50)
    
    # 检查当前时间
    now = datetime.now()
    print(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
    
    # 判断交易时间
    weekday = now.weekday()
    hour = now.hour
    minute = now.minute
    
    is_trading_day = weekday < 5
    is_morning = (9 <= hour < 11) or (hour == 11 and minute <= 30)
    is_afternoon = (13 <= hour < 15)
    is_trading_time = is_trading_day and (is_morning or is_afternoon)
    
    print(f"📊 交易时间状态: {'✅ 是' if is_trading_time else '❌ 否'}")
    
    try:
        print(f"\n🔗 连接到 {HOST}:{PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, PORT))
        print("✅ TCP连接成功")
        
        print(f"📤 发送Token: {TOKEN}")
        sock.send(TOKEN.encode('utf-8'))
        print("✅ Token发送成功")
        
        print(f"\n📥 开始接收原始数据 (30秒)...")
        sock.settimeout(2)
        
        received_count = 0
        total_bytes = 0
        raw_samples = []
        
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                data = sock.recv(4096)
                if data:
                    received_count += 1
                    total_bytes += len(data)
                    
                    # 尝试解码
                    try:
                        decoded = data.decode('utf-8', errors='ignore')
                        print(f"📦 数据包 #{received_count} ({len(data)} 字节)")
                        
                        # 显示原始数据的前200个字符
                        preview = decoded[:200].replace('\n', '\\n').replace('\r', '\\r')
                        print(f"   原始内容: {preview}")
                        
                        # 保存样本
                        if len(raw_samples) < 5:
                            raw_samples.append(decoded)
                        
                        # 分析数据特征
                        if '$' in decoded:
                            print("   ✅ 包含$分隔符 (可能是沪深A股数据)")
                        elif '{' in decoded and '}' in decoded:
                            print("   ✅ 包含JSON格式 (可能是北交所数据)")
                        elif ',' in decoded:
                            print("   ✅ 包含逗号分隔")
                        else:
                            print("   ⚠️  数据格式未知")
                            
                        # 检查是否包含股票代码特征
                        if any(code in decoded for code in ['SH', 'SZ', '00', '30', '60']):
                            print("   ✅ 疑似包含股票代码")
                            
                        print()
                        
                    except Exception as e:
                        print(f"   ❌ 解码失败: {e}")
                        
                else:
                    print("📭 接收到空数据")
                    
            except socket.timeout:
                print("⏱️  等待数据...")
                continue
            except Exception as e:
                print(f"❌ 接收错误: {e}")
                break
        
        sock.close()
        
        print(f"\n📊 接收统计:")
        print(f"   数据包数量: {received_count}")
        print(f"   总字节数: {total_bytes}")
        print(f"   平均包大小: {total_bytes/received_count if received_count > 0 else 0:.1f} 字节")
        
        if raw_samples:
            print(f"\n📄 原始数据样本分析:")
            for i, sample in enumerate(raw_samples, 1):
                print(f"\n样本 {i} (前500字符):")
                print("-" * 40)
                print(sample[:500])
                print("-" * 40)
                
                # 尝试按不同分隔符分析
                if '$' in sample:
                    parts = sample.split('$')
                    print(f"按$分割: {len(parts)} 部分")
                    if len(parts) >= 3:
                        print(f"   可能的股票代码: {parts[0]}")
                        print(f"   可能的股票名称: {parts[1]}")
                        
                if ',' in sample:
                    parts = sample.split(',')
                    print(f"按,分割: {len(parts)} 部分")
                    
                if '\n' in sample:
                    lines = sample.split('\n')
                    print(f"行数: {len(lines)}")
                    
        else:
            print("❌ 没有接收到任何数据")
            
        return received_count > 0
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_different_parsing():
    """测试不同的数据解析方法"""
    print("\n🧪 测试数据解析方法")
    print("=" * 50)
    
    # 模拟一些可能的数据格式
    test_data = [
        "SH600519$贵州茅台$1751436005$1408.51$1410.00$1405.00$1408.51$1234567$1234567890$1408.51$1409.00",
        "SZ000001,平安银行,13.20,0.15,1000000,13200000",
        '{"symbol":"BJ430047","name":"诺思兰德","price":15.67,"change":0.23}',
        "600519,贵州茅台,1408.51,0.12,1234567"
    ]
    
    for i, data in enumerate(test_data, 1):
        print(f"\n测试数据 {i}: {data}")
        
        # 测试$分隔
        if '$' in data:
            parts = data.split('$')
            print(f"  $分隔解析: 股票代码={parts[0]}, 名称={parts[1] if len(parts)>1 else 'N/A'}")
            
        # 测试,分隔
        if ',' in data:
            parts = data.split(',')
            print(f"  ,分隔解析: 股票代码={parts[0]}, 名称={parts[1] if len(parts)>1 else 'N/A'}")
            
        # 测试JSON
        if data.startswith('{'):
            try:
                import json
                parsed = json.loads(data)
                print(f"  JSON解析: {parsed}")
            except:
                print("  JSON解析失败")

def main():
    """主函数"""
    print("🧪 茶股帮原始数据调试工具")
    print("=" * 60)
    
    # 调试原始数据接收
    success = debug_raw_data()
    
    # 测试解析方法
    test_different_parsing()
    
    print(f"\n🎯 调试结论:")
    if success:
        print("✅ 可以接收到茶股帮数据")
        print("💡 需要分析数据格式并调整解析逻辑")
    else:
        print("❌ 无法接收到茶股帮数据")
        print("💡 可能是网络问题或Token失效")

if __name__ == "__main__":
    main()
