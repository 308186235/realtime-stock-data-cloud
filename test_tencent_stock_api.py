#!/usr/bin/env python3
"""
测试使用token从腾讯获取股价数据
"""

import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class TencentStockTester:
    """腾讯股票API测试器"""
    
    def __init__(self):
        self.token = os.getenv("STOCK_API_KEY", "QT_wat5QfcJ6N9pDZM5")
        self.chagubang_token = os.getenv("CHAGUBANG_TOKEN", "QT_wat5QfcJ6N9pDZM5")
        
        # 腾讯股票API的各种可能端点
        self.tencent_endpoints = [
            # 腾讯财经API
            "https://qt.gtimg.cn/q=",
            "https://web.sqt.gtimg.cn/q=",
            "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get",
            
            # 腾讯证券API
            "https://stock.gtimg.cn/data/index.php",
            "https://qt.gtimg.cn/r=",
            
            # 可能的认证端点
            "https://api.finance.qq.com/stock/",
            "https://stockapp.finance.qq.com/mstats/",
        ]
        
        # 测试股票代码
        self.test_stocks = [
            "sh000001",  # 上证指数
            "sz399001",  # 深证成指
            "sh600519",  # 贵州茅台
            "sz000001",  # 平安银行
            "sh600036",  # 招商银行
        ]
        
        print(f"🔑 使用Token: {self.token}")
        print(f"📊 测试股票: {', '.join(self.test_stocks)}")
        print()
    
    def test_tencent_qt_api(self):
        """测试腾讯qt.gtimg.cn API"""
        print("📈 测试腾讯qt.gtimg.cn股票API...")
        
        for stock in self.test_stocks:
            print(f"\n📊 测试股票: {stock}")
            
            # 方法1: 直接查询（无需token）
            url1 = f"https://qt.gtimg.cn/q={stock}"
            try:
                response = requests.get(url1, timeout=10)
                if response.status_code == 200:
                    data = response.text
                    print(f"   ✅ 方法1成功: {data[:100]}...")
                    if self._parse_tencent_data(data, stock):
                        return True
                else:
                    print(f"   ❌ 方法1失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 方法1异常: {e}")
            
            # 方法2: 带token参数
            url2 = f"https://qt.gtimg.cn/q={stock}&token={self.token}"
            try:
                response = requests.get(url2, timeout=10)
                if response.status_code == 200:
                    data = response.text
                    print(f"   ✅ 方法2成功: {data[:100]}...")
                    if self._parse_tencent_data(data, stock):
                        return True
                else:
                    print(f"   ❌ 方法2失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 方法2异常: {e}")
            
            # 方法3: 在请求头中使用token
            headers = {
                'Authorization': f'Bearer {self.token}',
                'X-API-Key': self.token,
                'Token': self.token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                response = requests.get(url1, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.text
                    print(f"   ✅ 方法3成功: {data[:100]}...")
                    if self._parse_tencent_data(data, stock):
                        return True
                else:
                    print(f"   ❌ 方法3失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 方法3异常: {e}")
        
        return False
    
    def test_tencent_web_api(self):
        """测试腾讯web股票API"""
        print("\n🌐 测试腾讯web股票API...")
        
        # 测试不同的web API端点
        web_apis = [
            "https://web.sqt.gtimg.cn/q={stock}",
            "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/kline/kline?param={stock},day,,,320,qfq",
            "https://stock.gtimg.cn/data/index.php?appn=detail&action=data&c={stock}",
        ]
        
        for api_template in web_apis:
            print(f"\n🔗 测试API: {api_template.split('?')[0]}...")
            
            for stock in self.test_stocks[:2]:  # 只测试前两个股票
                url = api_template.format(stock=stock)
                
                # 尝试不同的参数组合
                test_params = [
                    {},
                    {'token': self.token},
                    {'key': self.token},
                    {'apikey': self.token},
                    {'access_token': self.token},
                ]
                
                for i, params in enumerate(test_params):
                    try:
                        response = requests.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            data = response.text
                            print(f"     ✅ 参数组合{i+1}成功: {data[:80]}...")
                            
                            # 检查是否包含股票数据
                            if self._contains_stock_data(data):
                                print(f"     🎉 发现股票数据！")
                                return True
                        else:
                            print(f"     ❌ 参数组合{i+1}失败: {response.status_code}")
                    except Exception as e:
                        print(f"     ❌ 参数组合{i+1}异常: {str(e)[:50]}...")
        
        return False
    
    def test_chagubang_http_api(self):
        """测试茶股帮可能的HTTP API"""
        print("\n🍃 测试茶股帮HTTP API...")
        
        # 可能的茶股帮HTTP端点
        chagubang_apis = [
            "https://api.chagubang.com/stock",
            "https://l1.chagubang.com/api/stock",
            "https://chagubang.com/api/quote",
            "http://l1.chagubang.com:8080/stock",
            "https://qt.chagubang.com/q=",
        ]
        
        for api_url in chagubang_apis:
            print(f"\n🔗 测试: {api_url}")
            
            for stock in self.test_stocks[:2]:
                # 尝试不同的请求方式
                test_requests = [
                    # GET请求
                    {'method': 'GET', 'params': {'symbol': stock, 'token': self.token}},
                    {'method': 'GET', 'params': {'code': stock, 'key': self.token}},
                    {'method': 'GET', 'url': f"{api_url}?q={stock}&token={self.token}"},
                    
                    # POST请求
                    {'method': 'POST', 'json': {'symbol': stock, 'token': self.token}},
                    {'method': 'POST', 'data': {'code': stock, 'token': self.token}},
                ]
                
                for req_config in test_requests:
                    try:
                        if req_config['method'] == 'GET':
                            if 'url' in req_config:
                                response = requests.get(req_config['url'], timeout=5)
                            else:
                                response = requests.get(api_url, params=req_config.get('params'), timeout=5)
                        else:  # POST
                            if 'json' in req_config:
                                response = requests.post(api_url, json=req_config['json'], timeout=5)
                            else:
                                response = requests.post(api_url, data=req_config['data'], timeout=5)
                        
                        if response.status_code == 200:
                            data = response.text
                            print(f"     ✅ {req_config['method']}成功: {data[:60]}...")
                            
                            if self._contains_stock_data(data):
                                print(f"     🎉 发现股票数据！")
                                return True
                        else:
                            print(f"     ❌ {req_config['method']}失败: {response.status_code}")
                            
                    except requests.exceptions.Timeout:
                        print(f"     ⏰ {req_config['method']}超时")
                    except requests.exceptions.ConnectionError:
                        print(f"     🔌 {req_config['method']}连接失败")
                    except Exception as e:
                        print(f"     ❌ {req_config['method']}异常: {str(e)[:30]}...")
        
        return False
    
    def _parse_tencent_data(self, data, stock_code):
        """解析腾讯股票数据"""
        try:
            # 腾讯API返回格式通常是: v_股票代码="数据字段1~数据字段2~...";
            if '="' in data and '~' in data:
                # 提取数据部分
                start = data.find('="') + 2
                end = data.find('";', start)
                if end == -1:
                    end = len(data)
                
                stock_data = data[start:end]
                fields = stock_data.split('~')
                
                if len(fields) >= 10:
                    print(f"     📊 解析成功:")
                    print(f"       股票名称: {fields[1] if len(fields) > 1 else 'N/A'}")
                    print(f"       当前价格: {fields[3] if len(fields) > 3 else 'N/A'}")
                    print(f"       涨跌幅: {fields[32] if len(fields) > 32 else fields[5] if len(fields) > 5 else 'N/A'}")
                    print(f"       成交量: {fields[6] if len(fields) > 6 else 'N/A'}")
                    return True
        except Exception as e:
            print(f"     ❌ 数据解析失败: {e}")
        
        return False
    
    def _contains_stock_data(self, data):
        """检查数据是否包含股票信息"""
        stock_indicators = [
            '价格', 'price', '涨跌', 'change', '成交量', 'volume',
            '开盘', 'open', '收盘', 'close', '最高', 'high', '最低', 'low',
            '股票', 'stock', '证券', 'security', '~', 'v_'
        ]
        
        data_lower = data.lower()
        for indicator in stock_indicators:
            if indicator.lower() in data_lower:
                return True
        return False
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 腾讯股票API综合测试")
        print("=" * 60)
        print(f"🔑 Token: {self.token}")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {}
        
        # 测试1: 腾讯qt API
        print("🔍 测试1: 腾讯qt.gtimg.cn API")
        results['tencent_qt'] = self.test_tencent_qt_api()
        
        # 测试2: 腾讯web API
        print("\n🔍 测试2: 腾讯web股票API")
        results['tencent_web'] = self.test_tencent_web_api()
        
        # 测试3: 茶股帮HTTP API
        print("\n🔍 测试3: 茶股帮HTTP API")
        results['chagubang_http'] = self.test_chagubang_http_api()
        
        # 结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print(f"  腾讯qt API: {'✅ 成功' if results['tencent_qt'] else '❌ 失败'}")
        print(f"  腾讯web API: {'✅ 成功' if results['tencent_web'] else '❌ 失败'}")
        print(f"  茶股帮HTTP API: {'✅ 成功' if results['chagubang_http'] else '❌ 失败'}")
        
        # 总结
        success_count = sum(results.values())
        if success_count > 0:
            print(f"\n🎉 成功！找到了 {success_count} 个可用的API接口")
            print("💡 建议: 使用成功的接口获取股票数据")
        else:
            print("\n⚠️ 所有HTTP API测试都失败了")
            print("💡 可能的原因:")
            print("  1. Token主要用于TCP连接，不适用于HTTP API")
            print("  2. 需要在交易时间内测试")
            print("  3. 腾讯API可能不需要token认证")
            print("  4. 茶股帮主要使用TCP协议而非HTTP")
        
        return results

if __name__ == "__main__":
    tester = TencentStockTester()
    results = tester.run_comprehensive_test()
