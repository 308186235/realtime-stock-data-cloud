#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent原始数据调试器
"""

import socket
import time

# 茶股帮配置
HOST = 'l1.chagubang.com'
PORT = 6380
TOKEN = "process.env.STOCK_API_KEY"

def debug_raw_data():
    """调试原始数据格式"""
    print("🔍 Agent原始数据调试器")
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
        
        print(f"\n📥 开始接收原始数据 (15秒)...")
        sock.settimeout(2)
        
        received_count = 0
        total_data = ""
        raw_samples = []
        
        start_time = time.time()
        
        while time.time() - start_time < 15:
            try:
                data = sock.recv(4096)
                if data:
                    received_count += 1
                    
                    # 解码数据
                    decoded_data = data.decode('utf-8', errors='ignore')
                    total_data += decoded_data
                    
                    # 保存前5个原始数据包样本
                    if len(raw_samples) < 5:
                        raw_samples.append(decoded_data)
                    
                    # 每100个包显示一次进度
                    if received_count % 100 == 0:
                        print(f"📦 已接收 {received_count} 个数据包,总数据量: {len(total_data)} 字符")
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ 接收错误: {e}")
                break
        
        sock.close()
        
        print(f"\n📊 原始数据统计:")
        print(f"   接收数据包: {received_count}")
        print(f"   总数据量: {len(total_data)} 字符")
        
        # 分析数据分隔符
        print(f"\n🔍 数据分隔符分析:")
        print(f"   换行符 \\n 数量: {total_data.count(chr(10))}")
        print(f"   回车符 \\r 数量: {total_data.count(chr(13))}")
        print(f"   $ 分隔符数量: {total_data.count('$')}")
        print(f"   , 分隔符数量: {total_data.count(',')}")
        print(f"   ; 分隔符数量: {total_data.count(';')}")
        print(f"   | 分隔符数量: {total_data.count('|')}")
        
        # 显示原始数据样本
        print(f"\n📄 原始数据包样本:")
        for i, sample in enumerate(raw_samples, 1):
            print(f"\n样本 {i} (前300字符):")
            print("-" * 40)
            preview = sample[:300].replace('\n', '\\n').replace('\r', '\\r')
            print(preview)
            print("-" * 40)
        
        # 尝试不同的分隔方式
        print(f"\n🧪 尝试不同的数据分割方式:")
        
        # 方式1: 按换行符分割
        lines_by_newline = total_data.split('\n')
        valid_lines_newline = [line.strip() for line in lines_by_newline if line.strip() and '$' in line]
        print(f"   按\\n分割: {len(lines_by_newline)} 行,有效行: {len(valid_lines_newline)}")
        
        # 方式2: 按回车换行分割
        lines_by_crlf = total_data.split('\r\n')
        valid_lines_crlf = [line.strip() for line in lines_by_crlf if line.strip() and '$' in line]
        print(f"   按\\r\\n分割: {len(lines_by_crlf)} 行,有效行: {len(valid_lines_crlf)}")
        
        # 方式3: 按股票代码模式分割
        import re
        stock_pattern = r'(SH\d{6}|SZ\d{6})\$'
        matches = re.findall(stock_pattern, total_data)
        print(f"   股票代码匹配: {len(matches)} 个")
        
        # 显示有效行样本
        valid_lines = valid_lines_newline if valid_lines_newline else valid_lines_crlf
        if valid_lines:
            print(f"\n📋 有效数据行样本 (前3行):")
            for i, line in enumerate(valid_lines[:3], 1):
                print(f"\n行 {i}: {line[:200]}...")
                parts = line.split('$')
                print(f"   字段数: {len(parts)}")
                if len(parts) >= 3:
                    print(f"   股票代码: {parts[0]}")
                    print(f"   股票名称: {parts[1]}")
                    print(f"   时间戳: {parts[2]}")
                    if len(parts) >= 7:
                        print(f"   当前价: {parts[6]}")
        
        # 尝试解析一行数据
        if valid_lines:
            print(f"\n🎯 尝试解析第一行数据:")
            first_line = valid_lines[0]
            result = try_parse_stock_data(first_line)
            if result['success']:
                stock = result['stock']
                print(f"   ✅ 解析成功!")
                print(f"   股票: {stock['name']} ({stock['symbol']})")
                print(f"   价格: ¥{stock['price']:.2f}")
                print(f"   涨跌: {stock['change_percent']:+.2f}%")
                print(f"   成交量: {stock['volume']:.0f}")
                return True
            else:
                print(f"   ❌ 解析失败: {result['error']}")
                return False
        else:
            print(f"\n❌ 没有找到有效的股票数据行")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def try_parse_stock_data(raw_data: str):
    """尝试解析股票数据"""
    try:
        parts = raw_data.strip().split('$')
        
        if len(parts) < 10:
            return {'success': False, 'error': f'字段不足,只有{len(parts)}个字段'}
            
        symbol = parts[0].strip()
        name = parts[1].strip()
        
        # 检查股票代码格式
        if not symbol or len(symbol) < 6:
            return {'success': False, 'error': f'股票代码格式错误: {symbol}'}
        
        # 检查股票名称
        if not name or len(name) < 1:
            return {'success': False, 'error': f'股票名称格式错误: {name}'}
        
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
            'amount': amount
        }
        
        return {'success': True, 'stock': stock_info}
        
    except Exception as e:
        return {'success': False, 'error': f'解析异常: {e}'}

if __name__ == "__main__":
    success = debug_raw_data()
    if success:
        print(f"\n🎉 原始数据调试成功!Agent可以正确解析茶股帮数据!")
    else:
        print(f"\n💔 原始数据调试失败,需要进一步分析数据格式")
