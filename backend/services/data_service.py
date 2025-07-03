import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

# 数据缓存
data_cache = {}

def get_historical_data(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    获取历史数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        
    Returns:
        DataFrame: 包含日期,开盘价,最高价,最低价,收盘价,成交量的数据框
    """
    # 检查缓存
    cache_key = f"{symbol}_{start_date}_{end_date}"
    if cache_key in data_cache:
        return data_cache[cache_key]
    
    try:
        # 尝试从本地文件读取
        data = _load_from_local(symbol, start_date, end_date)
        
        if data is None:
            # 如果本地没有,从远程API获取
            data = _fetch_from_remote(symbol, start_date, end_date)
            
            # 保存到本地
            if data is not None:
                _save_to_local(symbol, data)
        
        # 缓存数据
        if data is not None:
            data_cache[cache_key] = data
            
        return data
        
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        
        # 创建示例数据用于开发和测试
        return _create_sample_data(symbol, start_date, end_date)

def _load_from_local(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """从本地文件加载数据"""
    # 构建文件路径
    file_path = Path(f"backend/data/historical/{symbol}.csv")
    
    if not file_path.exists():
        return None
    
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 确保日期列是日期类型并设为索引
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # 过滤日期范围
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df.index >= start) & (df.index <= end)]
        
        if df.empty:
            return None
            
        return df
        
    except Exception as e:
        logger.error(f"从本地加载数据失败: {e}")
        return None

def _fetch_from_remote(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """从远程API获取数据"""
    # 这里应当实现与实际数据API的集成
    # 例如: 调用Yahoo Finance,Alpha Vantage等
    
    # 示例: 使用Yahoo Finance API
    try:
        # 转换日期格式 (YYYY-MM-DD -> UNIX时间戳)
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        # 构造API请求URL (示例)
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}"
        params = {
            "period1": start_timestamp,
            "period2": end_timestamp,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true"
        }
        
        # 发送请求
        # response = requests.get(url, params=params)
        
        # 如果API请求成功
        # if response.status_code == 200:
        #     # 解析CSV数据
        #     data = pd.read_csv(StringIO(response.text))
        #     data['Date'] = pd.to_datetime(data['Date'])
        #     data.set_index('Date', inplace=True)
        #     
        #     # 重命名列名以匹配我们的标准
        #     data.rename(columns={
        #         'Open': 'open',
        #         'High': 'high',
        #         'Low': 'low',
        #         'Close': 'close',
        #         'Volume': 'volume'
        #     }, inplace=True)
        #     
        #     return data
        
        # 开发阶段返回模拟数据
        return _create_sample_data(symbol, start_date, end_date)
        
    except Exception as e:
        logger.error(f"从远程获取数据失败: {e}")
        return None

def _save_to_local(symbol: str, data: pd.DataFrame) -> bool:
    """保存数据到本地文件"""
    try:
        # 创建目录
        os.makedirs("backend/data/historical", exist_ok=True)
        
        # 保存到CSV
        file_path = f"backend/data/historical/{symbol}.csv"
        data.reset_index().to_csv(file_path, index=False)
        
        return True
        
    except Exception as e:
        logger.error(f"保存数据到本地失败: {e}")
        return False

def _create_sample_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    🚨 禁用示例数据创建 - 只允许真实数据
    """
    error_msg = f"""
    ❌ 错误：系统禁止创建示例数据

    请求的股票: {symbol}
    日期范围: {start_date} 到 {end_date}

    请配置真实数据源：
    1. 淘宝股票数据推送服务 (API_KEY: QT_wat5QfcJ6N9pDZM5)
    2. 同花顺实时数据API
    3. 通达信数据接口

    系统拒绝提供任何模拟或示例数据！
    """

    logger.error(error_msg)
    raise ValueError(error_msg)

def get_available_symbols() -> List[Dict[str, str]]:
    """获取可用的股票列表"""
    # 示例列表
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "market": "美国"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "market": "美国"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "market": "美国"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "market": "美国"},
        {"symbol": "TSLA", "name": "Tesla, Inc.", "market": "美国"},
        {"symbol": "600519.SS", "name": "贵州茅台", "market": "中国"},
        {"symbol": "000651.SZ", "name": "格力电器", "market": "中国"},
        {"symbol": "000333.SZ", "name": "美的集团", "market": "中国"},
        {"symbol": "601318.SS", "name": "中国平安", "market": "中国"},
        {"symbol": "600036.SS", "name": "招商银行", "market": "中国"}
    ]
    
    return symbols 
