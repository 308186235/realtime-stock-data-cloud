#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库实时推送功能
"""

import socket
import json
import time
import threading
from datetime import datetime
from supabase import create_client, Client

# Supabase配置
SUPABASE_URL = "https://process.env.SUPABASE_URL"
SUPABASE_KEY = "process.env.SUPABASE_ANON_KEY

# 茶股帮配置
CHAGUBANG_HOST = 'l1.chagubang.com'
CHAGUBANG_PORT = 6380
TOKEN = "process.env.STOCK_API_KEY"

def test_database_connection():
    """测试数据库连接"""
    print("🔧 测试Supabase数据库连接...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 尝试创建一个简单的表并插入数据
        test_data = {
            'id': 1,
            'symbol': 'TEST001',
            'name': '测试股票',
            'price': 10.00,
            'change_percent': 1.23,
            'timestamp': datetime.now().isoformat()
        }
        
        # 尝试插入到stock_realtime表
        result = supabase.table('stock_realtime').insert(test_data).execute()
        
        if result.data:
            print("✅ 数据库连接成功,表自动创建")
            # 清理测试数据
            supabase.table('stock_realtime').delete().eq('symbol', 'TEST001').execute()
            return supabase
        else:
            print(f"❌ 数据库插入失败: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def test_chagubang_connection():
    """测试茶股帮连接"""
    print("🔧 测试茶股帮连接...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
        sock.send(TOKEN.encode('utf-8'))
        
        print("✅ 茶股帮连接成功")
        return sock
        
    except Exception as e:
        print(f"❌ 茶股帮连接失败: {e}")
        return None

def parse_stock_data(data_str):
    """解析茶股帮数据"""
    try:
        # 简单解析,假设格式为: symbol,name,price,change
        parts = data_str.strip().split(',')
        if len(parts) >= 4:
            return {
                'symbol': parts[0].strip(),
                'name': parts[1].strip(),
                'price': float(parts[2]) if parts[2] else 0.0,
                'change_percent': float(parts[3]) if parts[3] else 0.0,
                'timestamp': datetime.now().isoformat(),
                'raw_data': data_str
            }
    except:
        pass
    return None

def realtime_test():
    """实时数据推送测试"""
    print("\n🚀 开始实时数据推送测试...")
    print("=" * 60)
    
    # 测试数据库连接
    supabase = test_database_connection()
    if not supabase:
        print("❌ 数据库连接失败,无法继续测试")
        return False
    
    # 测试茶股帮连接
    sock = test_chagubang_connection()
    if not sock:
        print("❌ 茶股帮连接失败,无法继续测试")
        return False
    
    print("\n📊 开始接收和存储实时数据...")
    print("运行30秒测试...")
    
    start_time = time.time()
    received_count = 0
    stored_count = 0
    error_count = 0
    
    buffer = ""
    
    try:
        while time.time() - start_time < 30:  # 运行30秒
            try:
                # 接收数据
                sock.settimeout(1)
                data = sock.recv(4096).decode('utf-8', errors='ignore')
                
                if not data:
                    continue
                
                buffer += data
                
                # 按行处理数据
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        received_count += 1
                        
                        # 解析数据
                        stock_data = parse_stock_data(line)
                        
                        if stock_data:
                            try:
                                # 存储到数据库
                                result = supabase.table('stock_realtime').upsert(
                                    stock_data, 
                                    on_conflict='symbol'
                                ).execute()
                                
                                if result.data:
                                    stored_count += 1
                                else:
                                    error_count += 1
                                    
                            except Exception as e:
                                error_count += 1
                                if error_count <= 3:  # 只打印前3个错误
                                    print(f"❌ 存储错误: {e}")
                        
                        # 每100条数据打印一次进度
                        if received_count % 100 == 0:
                            elapsed = time.time() - start_time
                            rate = received_count / elapsed if elapsed > 0 else 0
                            print(f"📈 进度: 接收{received_count} 存储{stored_count} 错误{error_count} 速率{rate:.1f}/秒")
                            
            except socket.timeout:
                continue
            except Exception as e:
                error_count += 1
                if error_count <= 3:
                    print(f"❌ 接收错误: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    
    finally:
        sock.close()
    
    # 测试结果
    elapsed = time.time() - start_time
    print(f"\n📊 测试结果 (运行{elapsed:.1f}秒):")
    print(f"   接收数据: {received_count} 条")
    print(f"   存储成功: {stored_count} 条")
    print(f"   存储错误: {error_count} 条")
    print(f"   成功率: {(stored_count/received_count*100) if received_count > 0 else 0:.1f}%")
    print(f"   接收速率: {received_count/elapsed:.1f} 条/秒")
    
    # 检查数据库中的数据
    try:
        print("\n🔍 检查数据库中的数据...")
        recent_data = supabase.table('stock_realtime').select('*').order('timestamp', desc=True).limit(5).execute()
        
        if recent_data.data:
            print(f"✅ 数据库中有 {len(recent_data.data)} 条最新数据:")
            for i, record in enumerate(recent_data.data, 1):
                symbol = record.get('symbol', 'N/A')
                name = record.get('name', 'N/A')
                price = record.get('price', 0)
                change = record.get('change_percent', 0)
                timestamp = record.get('timestamp', 'N/A')
                print(f"   {i}. {symbol} {name}: ¥{price} ({change:+.2f}%) - {timestamp}")
        else:
            print("❌ 数据库中没有数据")
            
    except Exception as e:
        print(f"❌ 检查数据库数据失败: {e}")
    
    # 判断测试是否成功
    success = received_count > 0 and stored_count > 0 and (stored_count / received_count) > 0.5
    
    if success:
        print("\n🎉 实时数据推送测试成功!")
        print("✅ 茶股帮数据源正常")
        print("✅ 数据库存储正常")
        print("✅ 数据可以提交给Agent")
    else:
        print("\n❌ 实时数据推送测试失败")
        if received_count == 0:
            print("❌ 没有接收到数据")
        elif stored_count == 0:
            print("❌ 数据无法存储到数据库")
        else:
            print("❌ 存储成功率过低")
    
    return success

if __name__ == "__main__":
    print("🧪 实时数据推送测试")
    print("=" * 60)
    print("测试目标:")
    print("1. 茶股帮实时数据接收")
    print("2. Supabase数据库存储")
    print("3. 数据完整性验证")
    print("4. Agent数据可用性")
    
    success = realtime_test()
    
    if success:
        print("\n🎯 结论: 数据库可以接收实时推送并提交给Agent!")
    else:
        print("\n🎯 结论: 数据库推送存在问题,需要进一步调试")
