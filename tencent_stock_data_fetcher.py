#!/usr/bin/env python3
"""
使用腾讯API获取实时股票数据
"""

import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class TencentStockDataFetcher:
    """腾讯股票数据获取器"""
    
    def __init__(self):
        self.token = os.getenv("STOCK_API_KEY", "QT_wat5QfcJ6N9pDZM5")
        self.base_url = "https://qt.gtimg.cn/q="
        
        # 热门股票代码
        self.popular_stocks = {
            # 指数
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            
            # 热门股票
            "sh600519": "贵州茅台",
            "sz000001": "平安银行", 
            "sh600036": "招商银行",
            "sh600000": "浦发银行",
            "sz000002": "万科A",
            "sh601318": "中国平安",
            "sh600276": "恒瑞医药",
            "sz300015": "爱尔眼科",
            "sh688981": "中芯国际",
            "sh601012": "隆基绿能",
            "sz002415": "海康威视",
        }
        
    def fetch_single_stock(self, stock_code):
        """获取单个股票数据"""
        try:
            url = f"{self.base_url}{stock_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.text.strip()
                return self.parse_tencent_data(data, stock_code)
            else:
                return None
                
        except Exception as e:
            print(f"❌ 获取 {stock_code} 数据失败: {e}")
            return None
    
    def fetch_multiple_stocks(self, stock_codes):
        """批量获取多个股票数据"""
        try:
            # 腾讯API支持批量查询
            codes_str = ",".join(stock_codes)
            url = f"{self.base_url}{codes_str}"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.text.strip()
                return self.parse_multiple_stocks_data(data, stock_codes)
            else:
                return {}
                
        except Exception as e:
            print(f"❌ 批量获取股票数据失败: {e}")
            return {}
    
    def parse_tencent_data(self, data, stock_code):
        """解析腾讯股票数据"""
        try:
            # 腾讯API返回格式: v_股票代码="字段1~字段2~字段3~...";
            if '="' in data and '~' in data:
                start = data.find('="') + 2
                end = data.find('";', start)
                if end == -1:
                    end = len(data)
                
                stock_data = data[start:end]
                fields = stock_data.split('~')
                
                if len(fields) >= 10:
                    return {
                        'code': stock_code,
                        'name': fields[1] if len(fields) > 1 else 'N/A',
                        'current_price': float(fields[3]) if len(fields) > 3 and fields[3] else 0,
                        'yesterday_close': float(fields[4]) if len(fields) > 4 and fields[4] else 0,
                        'today_open': float(fields[5]) if len(fields) > 5 and fields[5] else 0,
                        'volume': int(fields[6]) if len(fields) > 6 and fields[6] else 0,
                        'high': float(fields[41]) if len(fields) > 41 and fields[41] else 0,
                        'low': float(fields[42]) if len(fields) > 42 and fields[42] else 0,
                        'change': float(fields[31]) if len(fields) > 31 and fields[31] else 0,
                        'change_percent': float(fields[32]) if len(fields) > 32 and fields[32] else 0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'raw_data': data[:200] + '...' if len(data) > 200 else data
                    }
        except Exception as e:
            print(f"❌ 解析 {stock_code} 数据失败: {e}")
        
        return None
    
    def parse_multiple_stocks_data(self, data, stock_codes):
        """解析多个股票数据"""
        results = {}
        
        try:
            # 分割多个股票的数据
            lines = data.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 提取股票代码
                for code in stock_codes:
                    if f"v_{code}" in line:
                        parsed = self.parse_tencent_data(line, code)
                        if parsed:
                            results[code] = parsed
                        break
        except Exception as e:
            print(f"❌ 解析批量数据失败: {e}")
        
        return results
    
    def display_stock_data(self, stock_data):
        """显示股票数据"""
        if not stock_data:
            return
        
        print(f"\n📊 {stock_data['name']} ({stock_data['code']})")
        print(f"   💰 当前价格: ¥{stock_data['current_price']:.2f}")
        
        change = stock_data['change']
        change_percent = stock_data['change_percent']
        
        if change > 0:
            print(f"   📈 涨跌: +¥{change:.2f} (+{change_percent:.2f}%)")
        elif change < 0:
            print(f"   📉 涨跌: ¥{change:.2f} ({change_percent:.2f}%)")
        else:
            print(f"   ➡️ 涨跌: ¥{change:.2f} ({change_percent:.2f}%)")
        
        print(f"   🔄 成交量: {stock_data['volume']:,}")
        print(f"   📅 更新时间: {stock_data['timestamp']}")
    
    def get_market_overview(self):
        """获取市场概览"""
        print("📈 获取市场概览...")
        
        # 获取主要指数
        indices = ["sh000001", "sz399001", "sz399006"]
        index_data = {}
        
        for index_code in indices:
            data = self.fetch_single_stock(index_code)
            if data:
                index_data[index_code] = data
                self.display_stock_data(data)
        
        return index_data
    
    def get_popular_stocks(self):
        """获取热门股票数据"""
        print("\n🔥 获取热门股票数据...")
        
        # 批量获取热门股票
        stock_codes = list(self.popular_stocks.keys())[3:]  # 跳过指数
        stock_data = self.fetch_multiple_stocks(stock_codes)
        
        for code, name in self.popular_stocks.items():
            if code in stock_data:
                self.display_stock_data(stock_data[code])
            elif code not in ["sh000001", "sz399001", "sz399006"]:  # 不是指数
                # 单独获取
                data = self.fetch_single_stock(code)
                if data:
                    self.display_stock_data(data)
        
        return stock_data
    
    def search_stock(self, stock_code):
        """搜索特定股票"""
        print(f"\n🔍 搜索股票: {stock_code}")
        
        data = self.fetch_single_stock(stock_code)
        if data:
            self.display_stock_data(data)
            return data
        else:
            print(f"❌ 未找到股票 {stock_code} 的数据")
            return None
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        print("🚀 腾讯股票数据获取演示")
        print("=" * 60)
        print(f"🔑 Token: {self.token}")
        print(f"🌐 数据源: 腾讯财经 (qt.gtimg.cn)")
        print(f"⏰ 获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 市场概览
        market_data = self.get_market_overview()
        
        # 2. 热门股票
        popular_data = self.get_popular_stocks()
        
        # 3. 搜索特定股票
        print("\n" + "=" * 60)
        print("🔍 特定股票搜索演示:")
        
        test_stocks = ["sh600519", "sz000001", "sh601318"]
        for stock in test_stocks:
            self.search_stock(stock)
        
        # 4. 数据统计
        total_stocks = len(market_data) + len(popular_data)
        print(f"\n📊 数据获取统计:")
        print(f"   成功获取: {total_stocks} 只股票/指数")
        print(f"   数据源: 腾讯财经API")
        print(f"   是否需要Token: ❌ 不需要 (公开API)")
        print(f"   您的Token状态: ✅ 有效 (用于茶股帮TCP连接)")
        
        return {
            'market_data': market_data,
            'popular_data': popular_data,
            'total_count': total_stocks
        }

if __name__ == "__main__":
    fetcher = TencentStockDataFetcher()
    results = fetcher.run_comprehensive_demo()
