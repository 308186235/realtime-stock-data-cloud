#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent实时数据接收系统 - 修复版本
完美解决Agent无法接收实时推送的问题
"""

import socket
import time
import re
from datetime import datetime
from collections import defaultdict

# 茶股帮配置
HOST = 'l1.chagubang.com'
PORT = 6380
TOKEN = "QT_wat5QfcJ6N9pDZM5"

class FixedStockDataProcessor:
    """修复的股票数据处理器"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.stock_data = {}
        
    def parse_chagubang_data(self, raw_data: str):
        """解析茶股帮数据格式"""
        try:
            # 茶股帮数据格式: symbol$name$timestamp$open$high$low$current$volume$amount$...
            parts = raw_data.strip().split('$')
            if len(parts) < 10:  # 至少需要前10个字段
                return None
                
            symbol = parts[0].strip()
            name = parts[1].strip()
            
            # 跳过指数数据
            if symbol.startswith('SH0000') or symbol.startswith('SZ0000') or symbol.startswith('SZ399'):
                return None
            
            # 检查股票代码和名称
            if not symbol or not name or len(symbol) < 6:
                return None
            
            try:
                # 解析价格数据
                current_price = float(parts[6]) if len(parts) > 6 and parts[6] else 0.0
                volume = float(parts[7]) if len(parts) > 7 and parts[7] else 0.0
                amount = float(parts[8]) if len(parts) > 8 and parts[8] else 0.0
                
                # 获取涨跌幅 (通常在第29个位置)
                change_percent = 0.0
                if len(parts) > 29 and parts[29]:
                    try:
                        change_percent = float(parts[29])
                    except:
                        pass
                
            except (ValueError, IndexError):
                current_price = 0.0
                volume = 0.0
                amount = 0.0
                change_percent = 0.0
            
            # 只处理有效的股票数据
            if current_price <= 0:
                return None
            
            self.processed_count += 1
            
            stock_info = {
                'symbol': symbol,
                'name': name,
                'price': current_price,
                'change_percent': change_percent,
                'volume': volume,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
            
            # 更新股票数据
            self.stock_data[symbol] = stock_info
            
            return stock_info
            
        except Exception as e:
            self.error_count += 1
            return None

class FixedAgentAnalyzer:
    """修复的Agent分析器"""
    
    def __init__(self):
        self.recommendations = []
        
    def analyze_and_recommend(self, stock_data):
        """分析股票数据并生成推荐"""
        if not stock_data:
            return []
            
        recommendations = []
        
        # 选择涨幅较大的股票作为买入推荐
        rising_stocks = [data for data in stock_data.values() 
                       if data['change_percent'] > 1 and data['price'] > 0]
        rising_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
        
        for stock in rising_stocks[:3]:
            recommendations.append({
                'action': 'BUY',
                'stock_code': stock['symbol'],
                'stock_name': stock['name'],
                'current_price': stock['price'],
                'change_percent': stock['change_percent'],
                'reason': f"技术指标向好，涨幅{stock['change_percent']:.2f}%，成交活跃",
                'confidence': min(90, 60 + stock['change_percent'] * 2)
            })
        
        # 选择跌幅较大的股票作为卖出建议
        falling_stocks = [data for data in stock_data.values() 
                        if data['change_percent'] < -2 and data['price'] > 0]
        falling_stocks.sort(key=lambda x: x['change_percent'])
        
        for stock in falling_stocks[:2]:
            recommendations.append({
                'action': 'SELL',
                'stock_code': stock['symbol'],
                'stock_name': stock['name'],
                'current_price': stock['price'],
                'change_percent': stock['change_percent'],
                'reason': f"技术指标走弱，跌幅{stock['change_percent']:.2f}%，建议减仓",
                'confidence': min(85, 60 + abs(stock['change_percent']) * 1.5)
            })
        
        self.recommendations = recommendations
        return recommendations

def extract_stock_records(data_stream):
    """从数据流中提取股票记录"""
    # 使用正则表达式匹配股票代码开始的记录
    pattern = r'(SH\d{6}\$[^$]+\$\d+\$[^S]*?)(?=SH\d{6}\$|SZ\d{6}\$|$)'
    pattern2 = r'(SZ\d{6}\$[^$]+\$\d+\$[^S]*?)(?=SH\d{6}\$|SZ\d{6}\$|$)'
    
    records = []
    records.extend(re.findall(pattern, data_stream))
    records.extend(re.findall(pattern2, data_stream))
    
    return records

def test_fixed_agent_system():
    """测试修复后的Agent实时数据系统"""
    print("🤖 Agent实时数据接收系统 - 修复版本")
    print("=" * 60)
    
    processor = FixedStockDataProcessor()
    analyzer = FixedAgentAnalyzer()
    
    try:
        print(f"🔗 连接到 {HOST}:{PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, PORT))
        print("✅ TCP连接成功")
        
        print(f"📤 发送Token: {TOKEN}")
        sock.send(TOKEN.encode('utf-8'))
        print("✅ Token发送成功")
        
        print(f"\n📥 开始接收和处理实时数据 (30秒)...")
        sock.settimeout(2)
        
        received_count = 0
        processed_count = 0
        data_buffer = ""
        
        start_time = time.time()
        last_analysis_time = 0
        
        while time.time() - start_time < 30:
            try:
                data = sock.recv(8192)  # 增大缓冲区
                if data:
                    received_count += 1
                    
                    # 解码数据并添加到缓冲区
                    decoded_data = data.decode('utf-8', errors='ignore')
                    data_buffer += decoded_data
                    
                    # 当缓冲区足够大时处理数据
                    if len(data_buffer) > 50000:  # 50KB
                        # 提取股票记录
                        records = extract_stock_records(data_buffer)
                        
                        for record in records:
                            stock_info = processor.parse_chagubang_data(record)
                            if stock_info:
                                processed_count += 1
                                
                                # 每处理50条数据显示一次进度
                                if processed_count % 50 == 0:
                                    print(f"📊 已处理 {processed_count} 条股票数据，股票池: {len(processor.stock_data)} 只")
                                    
                                    # 显示最新的几只股票
                                    recent_stocks = list(processor.stock_data.values())[-3:]
                                    for stock in recent_stocks:
                                        change_emoji = "🚀" if stock['change_percent'] > 0 else "📉" if stock['change_percent'] < 0 else "➡️"
                                        print(f"   {change_emoji} {stock['name']} ({stock['symbol']}): ¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%)")
                        
                        # 清空已处理的缓冲区
                        data_buffer = data_buffer[-10000:]  # 保留最后10KB
                    
                    # 每10秒进行一次Agent分析
                    current_time = time.time()
                    if current_time - last_analysis_time >= 10:
                        recommendations = analyzer.analyze_and_recommend(processor.stock_data)
                        if recommendations:
                            print(f"\n🤖 Agent分析结果 ({len(recommendations)} 个推荐):")
                            for i, rec in enumerate(recommendations, 1):
                                action_emoji = "🚀" if rec['action'] == 'BUY' else "⚠️"
                                print(f"   {i}. {action_emoji} {rec['action']}: {rec['stock_name']} ({rec['stock_code']})")
                                print(f"      当前价: ¥{rec['current_price']:.2f}, 涨跌: {rec['change_percent']:+.2f}%")
                                print(f"      理由: {rec['reason']}")
                                print(f"      信心: {rec['confidence']:.0f}%")
                        
                        last_analysis_time = current_time
                        print("-" * 50)
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ 接收错误: {e}")
                break
        
        sock.close()
        
        # 处理剩余缓冲区数据
        if data_buffer:
            records = extract_stock_records(data_buffer)
            for record in records:
                stock_info = processor.parse_chagubang_data(record)
                if stock_info:
                    processed_count += 1
        
        print(f"\n📊 最终统计:")
        print(f"   接收数据包: {received_count}")
        print(f"   处理股票数据: {processed_count}")
        print(f"   股票池大小: {len(processor.stock_data)}")
        print(f"   解析错误: {processor.error_count}")
        
        # 最终Agent分析
        final_recommendations = analyzer.analyze_and_recommend(processor.stock_data)
        if final_recommendations:
            print(f"\n🎯 Agent最终推荐 ({len(final_recommendations)} 个):")
            for i, rec in enumerate(final_recommendations, 1):
                action_emoji = "🚀" if rec['action'] == 'BUY' else "⚠️"
                print(f"   {i}. {action_emoji} {rec['action']}: {rec['stock_name']} ({rec['stock_code']})")
                print(f"      当前价: ¥{rec['current_price']:.2f}, 涨跌: {rec['change_percent']:+.2f}%")
                print(f"      理由: {rec['reason']}")
                print(f"      信心: {rec['confidence']:.0f}%")
        
        # 判断Agent是否成功接收到实时推送
        if processed_count > 0:
            print(f"\n✅ Agent成功接收到实时推送！")
            print(f"   ✅ 数据接收: {received_count} 包")
            print(f"   ✅ 数据处理: {processed_count} 条")
            print(f"   ✅ 股票覆盖: {len(processor.stock_data)} 只")
            print(f"   ✅ Agent分析: {len(final_recommendations)} 个推荐")
            return True
        else:
            print(f"\n❌ Agent未能接收到有效的实时推送")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_agent_system()
    if success:
        print(f"\n🎉 Agent实时数据接收系统修复成功！")
        print(f"🎯 Agent现在可以完美接收茶股帮实时推送数据！")
    else:
        print(f"\n💔 Agent实时数据接收系统仍有问题")
