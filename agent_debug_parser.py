#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent数据解析调试器
"""

import socket
import time
from datetime import datetime

# 茶股帮配置
HOST = 'l1.chagubang.com'
PORT = 6380
TOKEN = "QT_wat5QfcJ6N9pDZM5"

def debug_data_parsing():
    """调试数据解析"""
    print("🔍 Agent数据解析调试器")
    print("=" * 50)
    
    try:
        print(f"🔗 连接到 {HOST}:{PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, PORT))
        print("✅ TCP连接成功")
        
        print(f"📤 发送Token: {TOKEN}")
        sock.send(TOKEN.encode('utf-8'))
        print("✅ Token发送成功")
        
        print(f"\n📥 开始接收和分析数据 (20秒)...")
        sock.settimeout(2)
        
        received_count = 0
        parsed_count = 0
        error_count = 0
        buffer = ""
        sample_lines = []
        
        start_time = time.time()
        
        while time.time() - start_time < 20:
            try:
                data = sock.recv(4096)
                if data:
                    received_count += 1
                    
                    # 解码数据
                    decoded_data = data.decode('utf-8', errors='ignore')
                    buffer += decoded_data
                    
                    # 按行处理数据
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            # 保存前10个样本
                            if len(sample_lines) < 10:
                                sample_lines.append(line)
                            
                            # 尝试解析
                            result = try_parse_line(line)
                            if result['success']:
                                parsed_count += 1
                                
                                # 显示前几个成功解析的结果
                                if parsed_count <= 5:
                                    print(f"✅ 解析成功 #{parsed_count}: {result['stock']['name']} ({result['stock']['symbol']}) ¥{result['stock']['price']:.2f}")
                            else:
                                error_count += 1
                                
                                # 显示前几个解析失败的原因
                                if error_count <= 5:
                                    print(f"❌ 解析失败 #{error_count}: {result['error']}")
                                    print(f"   原始数据: {line[:100]}...")
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ 接收错误: {e}")
                break
        
        sock.close()
        
        print(f"\n📊 调试统计:")
        print(f"   接收数据包: {received_count}")
        print(f"   解析成功: {parsed_count}")
        print(f"   解析失败: {error_count}")
        print(f"   成功率: {parsed_count/(parsed_count+error_count)*100:.1f}%" if (parsed_count+error_count) > 0 else "0%")
        
        print(f"\n📄 原始数据样本:")
        for i, line in enumerate(sample_lines, 1):
            print(f"样本 {i}: {line[:150]}...")
            
            # 分析数据结构
            parts = line.split('$')
            print(f"   字段数量: {len(parts)}")
            if len(parts) >= 3:
                print(f"   字段0 (股票代码): {parts[0]}")
                print(f"   字段1 (股票名称): {parts[1]}")
                print(f"   字段2 (时间戳): {parts[2]}")
                if len(parts) >= 7:
                    print(f"   字段6 (当前价): {parts[6]}")
            print()
        
        return parsed_count > 0
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def try_parse_line(raw_data: str):
    """尝试解析单行数据"""
    try:
        # 茶股帮数据格式: symbol$name$timestamp$open$high$low$current$volume$amount$...
        parts = raw_data.strip().split('$')
        
        if len(parts) < 10:
            return {'success': False, 'error': f'字段不足，只有{len(parts)}个字段'}
            
        symbol = parts[0].strip()
        name = parts[1].strip()
        
        # 检查股票代码格式
        if not symbol or len(symbol) < 6:
            return {'success': False, 'error': f'股票代码格式错误: {symbol}'}
        
        # 检查股票名称
        if not name or len(name) < 2:
            return {'success': False, 'error': f'股票名称格式错误: {name}'}
        
        # 跳过指数数据
        if symbol.startswith('SH0000') or symbol.startswith('SZ0000'):
            return {'success': False, 'error': f'跳过指数数据: {symbol}'}
        
        try:
            # 解析价格数据
            current_price = float(parts[6]) if len(parts) > 6 and parts[6] else 0.0
            volume = float(parts[7]) if len(parts) > 7 and parts[7] else 0.0
            amount = float(parts[8]) if len(parts) > 8 and parts[8] else 0.0
            
            # 获取涨跌幅
            change_percent = 0.0
            if len(parts) > 29 and parts[29]:
                try:
                    change_percent = float(parts[29])
                except:
                    pass
            
        except (ValueError, IndexError) as e:
            return {'success': False, 'error': f'价格数据解析错误: {e}'}
        
        # 检查价格有效性
        if current_price <= 0:
            return {'success': False, 'error': f'价格无效: {current_price}'}
        
        stock_info = {
            'symbol': symbol,
            'name': name,
            'price': current_price,
            'change_percent': change_percent,
            'volume': volume,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
        
        return {'success': True, 'stock': stock_info}
        
    except Exception as e:
        return {'success': False, 'error': f'解析异常: {e}'}

if __name__ == "__main__":
    success = debug_data_parsing()
    if success:
        print(f"\n🎉 数据解析调试成功！")
    else:
        print(f"\n💔 数据解析调试失败")
