import os
import re
import time
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class ThsCrawler:
    """
    同花顺数据爬取工具
    用于从同花顺网站和数据接口获取股票数据
    """
    
    def __init__(self):
        """
        初始化同花顺数据爬取工具
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://www.10jqka.com.cn/'
        }
        self.stock_basics = None
        
    def get_stock_list(self):
        """
        获取股票列表
        
        Returns:
            pd.DataFrame: 股票基本信息
        """
        try:
            # 从同花顺网站获取股票列表
            url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/1/ajax/1/'
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取页面数
            page_info = soup.find('span', class_='page_info')
            if page_info:
                total_pages = int(page_info.text.split('/')[-1])
            else:
                total_pages = 20  # 默认值
                
            stock_data = []
            
            # 遍历所有页面
            for page in range(1, min(total_pages + 1, 50)):  # 最多获取50页
                page_url = f'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/{page}/ajax/1/'
                page_response = requests.get(page_url, headers=self.headers)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # 解析表格
                table = page_soup.find('table', class_='m-table')
                if not table:
                    continue
                    
                rows = table.find_all('tr')[1:]  # 跳过表头
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        code = cells[1].text.strip()
                        name = cells[2].text.strip()
                        # 判断市场(沪市为6开头,深市为0或3开头)
                        market = 'SH' if code.startswith('6') else 'SZ'
                        
                        stock_data.append({
                            'code': code,
                            'name': name,
                            'market': market,
                            'industry': '',  # 行业数据需要单独获取
                            'area': ''       # 地区数据需要单独获取
                        })
                
                # 休眠0.5秒,避免请求过于频繁
                time.sleep(0.5)
                
            # 如果列表为空,尝试使用备用接口
            if not stock_data:
                return self._get_stock_list_backup()
                
            return pd.DataFrame(stock_data)
        except Exception as e:
            logger.error(f"同花顺获取股票列表失败: {e}")
            # 尝试备用接口
            return self._get_stock_list_backup()
    
    def _get_stock_list_backup(self):
        """
        使用备用接口获取股票列表
        """
        try:
            # 使用东方财富网接口作为备用
            url = 'http://87.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5000&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23'
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            if 'data' not in data or 'diff' not in data['data']:
                return pd.DataFrame(columns=['code', 'name', 'market', 'industry', 'area'])
                
            stock_data = []
            for item in data['data']['diff'].values():
                code = item.get('f12', '')
                name = item.get('f14', '')
                market_code = item.get('f13', 0)
                market = 'SH' if market_code == 1 else 'SZ'
                
                stock_data.append({
                    'code': code,
                    'name': name,
                    'market': market,
                    'industry': '',
                    'area': ''
                })
                
            return pd.DataFrame(stock_data)
        except Exception as e:
            logger.error(f"备用接口获取股票列表失败: {e}")
            return pd.DataFrame(columns=['code', 'name', 'market', 'industry', 'area'])
    
    def get_k_data(self, code, start_date=None, end_date=None, freq='daily'):
        """
        获取股票K线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期,格式:'YYYY-MM-DD'
            end_date: 结束日期,格式:'YYYY-MM-DD'
            freq: 数据频率,支持 'daily', 'weekly', 'monthly'
            
        Returns:
            pd.DataFrame: K线数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # 将日期转换为秒时间戳
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        # 确定k线类型
        period_map = {
            'daily': 'day',
            'weekly': 'week',
            'monthly': 'month'
        }
        period = period_map.get(freq, 'day')
        
        try:
            # 同花顺数据接口
            market = '1' if code.startswith('6') else '0'
            url = f'http://d.10jqka.com.cn/v6/line/hs_{code}/{period}/last.js'
            headers = {
                **self.headers,
                'Referer': f'http://stockpage.10jqka.com.cn/{code}/'
            }
            
            response = requests.get(url, headers=headers)
            # 提取JSON数据
            json_data = response.text
            json_data = json_data.split('=')[1].strip(';')
            data = json.loads(json_data)
            
            if 'data' not in data:
                # 备用方案
                return self._get_k_data_backup(code, start_date, end_date, freq)
                
            k_data = []
            for date_str, values in data['data'].items():
                # 格式化日期 (YYYYMMDD -> YYYY-MM-DD)
                if len(date_str) == 8:
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                    
                date_ts = datetime.strptime(formatted_date, '%Y-%m-%d').timestamp()
                if date_ts < start_ts or date_ts > end_ts:
                    continue
                    
                # 解析数据,格式为: 开盘,最高,最低,收盘,成交量,成交额
                vals = values.split(',')
                if len(vals) >= 6:
                    k_data.append({
                        'date': formatted_date,
                        'open': float(vals[0]),
                        'high': float(vals[1]),
                        'low': float(vals[2]),
                        'close': float(vals[3]),
                        'volume': float(vals[4]),
                        'amount': float(vals[5]) / 10000.0  # 转换为元
                    })
            
            df = pd.DataFrame(k_data)
            if df.empty:
                # 备用方案
                return self._get_k_data_backup(code, start_date, end_date, freq)
                
            return df
        except Exception as e:
            logger.error(f"同花顺获取K线数据失败 - 股票: {code}, 错误: {e}")
            # 备用方案
            return self._get_k_data_backup(code, start_date, end_date, freq)
    
    def _get_k_data_backup(self, code, start_date, end_date, freq):
        """
        使用备用接口获取K线数据
        """
        try:
            # 东方财富网接口
            market = 'SH' if code.startswith('6') else 'SZ'
            market_code = 1 if market == 'SH' else 0
            
            freq_map = {
                'daily': 101,   # 日线
                'weekly': 102,  # 周线
                'monthly': 103  # 月线
            }
            klt = freq_map.get(freq, 101)
            
            url = (f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market_code}.{code}"
                  f"&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
                  f"&klt={klt}&fqt=0&beg={start_date.replace('-', '')}&end={end_date.replace('-', '')}")
            
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            if data['data'] is None:
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
                
            k_data = []
            for item in data['data']['klines']:
                values = item.split(',')
                k_data.append({
                    'date': values[0],
                    'open': float(values[1]),
                    'close': float(values[2]),
                    'high': float(values[3]),
                    'low': float(values[4]),
                    'volume': float(values[5]),
                    'amount': float(values[6])
                })
                
            return pd.DataFrame(k_data)
        except Exception as e:
            logger.error(f"备用接口获取K线数据失败 - 股票: {code}, 错误: {e}")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
    
    def get_realtime_quotes(self, codes):
        """
        获取实时行情数据
        
        Args:
            codes: 股票代码列表,如 ['000001', '600000']
            
        Returns:
            pd.DataFrame: 实时行情数据
        """
        if not isinstance(codes, list):
            codes = [codes]
            
        try:
            # 构建股票编码列表
            stock_list = []
            for code in codes:
                if code.startswith('6'):
                    stock_list.append(f"1_{code}")
                else:
                    stock_list.append(f"0_{code}")
                    
            code_str = ",".join(stock_list)
            url = f"http://d.10jqka.com.cn/v6/realhead/hs/{code_str}/last.js"
            headers = {
                **self.headers,
                'Referer': 'http://stockpage.10jqka.com.cn/'
            }
            
            response = requests.get(url, headers=headers)
            # 提取JSON数据
            try:
                json_data = response.text
                json_data = json_data.split('=')[1].strip(';')
                data = json.loads(json_data)
            except:
                # 如果解析失败,使用备用接口
                return self._get_realtime_quotes_backup(codes)
                
            quotes = []
            for code in codes:
                key = f"hs_{code}"
                if key in data and data[key]:
                    item = data[key]
                    quotes.append({
                        'code': code,
                        'name': item.get('name', ''),
                        'price': float(item.get('10', 0)),  # 当前价
                        'change': float(item.get('264', 0)),  # 涨跌额
                        'change_pct': float(item.get('199', 0)),  # 涨跌幅
                        'high': float(item.get('33', 0)),  # 最高
                        'low': float(item.get('34', 0)),  # 最低
                        'open': float(item.get('7', 0)),  # 开盘
                        'prev_close': float(item.get('6', 0)),  # 昨收
                        'volume': float(item.get('13', 0)),  # 成交量
                        'amount': float(item.get('19', 0)),  # 成交额
                        'time': item.get('time', '')  # 时间
                    })
                    
            df = pd.DataFrame(quotes)
            if df.empty:
                # 备用方案
                return self._get_realtime_quotes_backup(codes)
                
            return df
        except Exception as e:
            logger.error(f"同花顺获取实时行情失败: {e}")
            # 备用方案
            return self._get_realtime_quotes_backup(codes)
    
    def _get_realtime_quotes_backup(self, codes):
        """
        使用备用接口获取实时行情
        """
        try:
            # 东方财富网接口
            code_str = ','.join([f"{'sh' if c.startswith('6') else 'sz'}{c}" for c in codes])
            url = f"http://api.money.126.net/data/feed/{code_str}?callback=a"
            
            response = requests.get(url, headers=self.headers)
            text = response.text[2:-2]  # 移除回调函数名称和括号
            data = eval(text)  # 解析JSON
            
            quotes = []
            for code in codes:
                market_code = f"{'sh' if code.startswith('6') else 'sz'}{code}"
                if market_code in data:
                    item = data[market_code]
                    quotes.append({
                        'code': code,
                        'name': item.get('name', ''),
                        'price': item.get('price', 0),
                        'change': item.get('updown', 0),
                        'change_pct': item.get('percent', 0) * 100,
                        'high': item.get('high', 0),
                        'low': item.get('low', 0),
                        'open': item.get('open', 0),
                        'prev_close': item.get('yestclose', 0),
                        'volume': item.get('volume', 0),
                        'amount': item.get('turnover', 0),
                        'time': item.get('update', '')
                    })
                    
            return pd.DataFrame(quotes)
        except Exception as e:
            logger.error(f"备用接口获取实时行情失败: {e}")
            return pd.DataFrame(columns=['code', 'name', 'price', 'change', 'change_pct', 'high', 'low', 'open', 'prev_close', 'volume', 'amount', 'time'])
    
    def get_index_data(self, index_code, start_date=None, end_date=None):
        """
        获取指数数据
        
        Args:
            index_code: 指数代码,如 '000001' (上证指数)
            start_date: 开始日期,格式:'YYYY-MM-DD'
            end_date: 结束日期,格式:'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: 指数数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # 转换为同花顺的指数代码
        ths_index_map = {
            '000001': '1A0001',  # 上证指数
            '399001': '1A0001',  # 深证成指 (同花顺使用不同编码)
            '399006': '1A0001'   # 创业板指
        }
        
        ths_index = ths_index_map.get(index_code, index_code)
            
        try:
            # 同花顺的指数接口
            url = f'http://d.10jqka.com.cn/v6/line/hs_{ths_index}/day/last.js'
            headers = {
                **self.headers,
                'Referer': 'http://q.10jqka.com.cn/'
            }
            
            response = requests.get(url, headers=headers)
            
            # 提取JSON数据
            try:
                json_data = response.text
                json_data = json_data.split('=')[1].strip(';')
                data = json.loads(json_data)
            except:
                # 如果解析失败,使用备用接口
                return self._get_index_data_backup(index_code, start_date, end_date)
                
            if 'data' not in data:
                return self._get_index_data_backup(index_code, start_date, end_date)
                
            # 将日期转换为秒时间戳
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
                
            index_data = []
            for date_str, values in data['data'].items():
                # 格式化日期 (YYYYMMDD -> YYYY-MM-DD)
                if len(date_str) == 8:
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                    
                date_ts = datetime.strptime(formatted_date, '%Y-%m-%d').timestamp()
                if date_ts < start_ts or date_ts > end_ts:
                    continue
                    
                # 解析数据,格式为: 开盘,最高,最低,收盘,成交量,成交额
                vals = values.split(',')
                if len(vals) >= 6:
                    index_data.append({
                        'date': formatted_date,
                        'open': float(vals[0]),
                        'high': float(vals[1]),
                        'low': float(vals[2]),
                        'close': float(vals[3]),
                        'volume': float(vals[4]),
                        'amount': float(vals[5]) / 10000.0  # 转换为元
                    })
                    
            df = pd.DataFrame(index_data)
            if df.empty:
                # 备用方案
                return self._get_index_data_backup(index_code, start_date, end_date)
                
            return df
        except Exception as e:
            logger.error(f"同花顺获取指数数据失败 - 指数: {index_code}, 错误: {e}")
            # 备用方案
            return self._get_index_data_backup(index_code, start_date, end_date)
    
    def _get_index_data_backup(self, index_code, start_date, end_date):
        """
        使用备用接口获取指数数据
        """
        try:
            # 处理常见指数代码
            if index_code == '000001':
                market = 1  # 上证指数
            elif index_code == '399001':
                market = 0  # 深证成指
            elif index_code == '399006':
                market = 0  # 创业板指
            else:
                market = 1 if index_code.startswith('0') else 0
                
            url = (f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market}.{index_code}"
                   f"&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
                   f"&klt=101&fqt=0&beg={start_date.replace('-', '')}&end={end_date.replace('-', '')}")
                   
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            if data['data'] is None:
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
                
            index_data = []
            for item in data['data']['klines']:
                values = item.split(',')
                index_data.append({
                    'date': values[0],
                    'open': float(values[1]),
                    'close': float(values[2]),
                    'high': float(values[3]),
                    'low': float(values[4]),
                    'volume': float(values[5]),
                    'amount': float(values[6])
                })
                
            return pd.DataFrame(index_data)
        except Exception as e:
            logger.error(f"备用接口获取指数数据失败 - 指数: {index_code}, 错误: {e}")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount']) 
