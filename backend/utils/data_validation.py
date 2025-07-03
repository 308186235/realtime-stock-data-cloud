#!/usr/bin/env python3
"""
数据验证工具
确保系统只使用真实数据，完全禁止模拟数据
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    """数据验证错误"""
    pass

class MockDataDetectedError(DataValidationError):
    """检测到模拟数据错误"""
    pass

class RealDataRequiredError(DataValidationError):
    """需要真实数据错误"""
    pass

def validate_real_data(data: Any, data_type: str = "unknown") -> bool:
    """
    验证数据真实性
    
    Args:
        data: 要验证的数据
        data_type: 数据类型描述
        
    Returns:
        bool: 数据有效返回True
        
    Raises:
        MockDataDetectedError: 检测到模拟数据
        DataValidationError: 数据验证失败
    """
    if not data:
        raise DataValidationError(f"❌ {data_type}数据为空，需要真实数据")
    
    # 检查模拟数据标识
    mock_indicators = [
        'mock', 'test', 'demo', 'sample', 'fake', 'simulated', 
        'generated', 'random', 'artificial', 'synthetic'
    ]
    
    # 检查数据源字段
    if hasattr(data, 'source') or hasattr(data, 'data_source'):
        source = str(getattr(data, 'source', '') or getattr(data, 'data_source', '')).lower()
        for indicator in mock_indicators:
            if indicator in source:
                raise MockDataDetectedError(f"❌ 检测到{data_type}模拟数据源: {source}")
    
    # 检查字典类型数据
    if isinstance(data, dict):
        for key, value in data.items():
            key_str = str(key).lower()
            value_str = str(value).lower()
            
            for indicator in mock_indicators:
                if indicator in key_str or indicator in value_str:
                    raise MockDataDetectedError(f"❌ 检测到{data_type}模拟数据字段: {key}={value}")
    
    # 检查列表类型数据
    if isinstance(data, list) and data:
        for item in data[:5]:  # 检查前5个元素
            try:
                validate_real_data(item, f"{data_type}列表项")
            except MockDataDetectedError:
                raise
    
    # 检查DataFrame类型数据
    try:
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            # 检查列名
            for col in data.columns:
                col_str = str(col).lower()
                for indicator in mock_indicators:
                    if indicator in col_str:
                        raise MockDataDetectedError(f"❌ 检测到{data_type}模拟数据列: {col}")
            
            # 检查是否有source列
            if 'source' in data.columns or 'data_source' in data.columns:
                source_col = 'source' if 'source' in data.columns else 'data_source'
                sources = data[source_col].astype(str).str.lower()
                for indicator in mock_indicators:
                    if sources.str.contains(indicator).any():
                        raise MockDataDetectedError(f"❌ 检测到{data_type}模拟数据源列")
    except ImportError:
        pass  # pandas未安装，跳过DataFrame检查
    
    return True

def validate_stock_data(data: Dict[str, Any]) -> bool:
    """
    验证股票数据真实性
    
    Args:
        data: 股票数据字典
        
    Returns:
        bool: 数据有效返回True
        
    Raises:
        MockDataDetectedError: 检测到模拟数据
        DataValidationError: 数据验证失败
    """
    if not data:
        raise DataValidationError("❌ 股票数据为空")
    
    # 基础验证
    validate_real_data(data, "股票")
    
    # 检查必要字段
    required_fields = ['timestamp', 'stock_code', 'price']
    for field in required_fields:
        if field not in data:
            raise DataValidationError(f"❌ 缺少必要字段: {field}")
    
    # 检查数据时效性
    if 'timestamp' in data:
        try:
            data_time = float(data['timestamp'])
            current_time = time.time()
            
            # 数据不能超过5分钟
            if current_time - data_time > 300:
                raise DataValidationError("❌ 股票数据过期，需要实时数据")
                
            # 数据不能来自未来
            if data_time > current_time + 60:
                raise DataValidationError("❌ 股票数据时间异常，疑似模拟数据")
                
        except (ValueError, TypeError):
            raise DataValidationError("❌ 股票数据时间戳格式错误")
    
    # 检查价格合理性
    if 'price' in data:
        try:
            price = float(data['price'])
            if price <= 0 or price > 10000:  # A股价格范围检查
                raise DataValidationError(f"❌ 股票价格异常: {price}")
        except (ValueError, TypeError):
            raise DataValidationError("❌ 股票价格格式错误")
    
    return True

def validate_market_data(data: Any) -> bool:
    """
    验证市场数据真实性
    
    Args:
        data: 市场数据
        
    Returns:
        bool: 数据有效返回True
        
    Raises:
        MockDataDetectedError: 检测到模拟数据
        DataValidationError: 数据验证失败
    """
    validate_real_data(data, "市场")
    
    # 如果是股票列表，验证每只股票
    if isinstance(data, list):
        for i, stock_data in enumerate(data):
            try:
                validate_stock_data(stock_data)
            except (MockDataDetectedError, DataValidationError) as e:
                raise DataValidationError(f"❌ 第{i+1}只股票数据验证失败: {e}")
    
    return True

def require_real_data_source(service_name: str = "未知服务"):
    """
    要求配置真实数据源
    
    Args:
        service_name: 服务名称
        
    Raises:
        RealDataRequiredError: 需要真实数据源
    """
    error_msg = f"""
    ❌ 错误：{service_name}未配置真实数据源
    
    请配置以下真实数据源之一：
    1. 淘宝股票数据推送服务
       - API_KEY: QT_wat5QfcJ6N9pDZM5
       - 连接信息: 需要从淘宝卖家获取
    
    2. 同花顺实时数据API
       - 需要申请API密钥
       - 支持实时行情推送
    
    3. 通达信数据接口
       - 本地通达信软件接口
       - 支持历史和实时数据
    
    系统拒绝使用任何模拟数据！
    """
    
    logger.error(error_msg)
    raise RealDataRequiredError(error_msg)

def check_data_freshness(timestamp: float, max_age_seconds: int = 300) -> bool:
    """
    检查数据新鲜度
    
    Args:
        timestamp: 数据时间戳
        max_age_seconds: 最大允许年龄（秒）
        
    Returns:
        bool: 数据新鲜返回True
        
    Raises:
        DataValidationError: 数据过期
    """
    current_time = time.time()
    age = current_time - timestamp
    
    if age > max_age_seconds:
        raise DataValidationError(f"❌ 数据过期: {age:.1f}秒前的数据，最大允许{max_age_seconds}秒")
    
    if timestamp > current_time + 60:
        raise DataValidationError("❌ 数据时间异常，疑似模拟数据")
    
    return True

def validate_api_response(response: Dict[str, Any], api_name: str = "API") -> bool:
    """
    验证API响应真实性
    
    Args:
        response: API响应数据
        api_name: API名称
        
    Returns:
        bool: 响应有效返回True
        
    Raises:
        MockDataDetectedError: 检测到模拟响应
        DataValidationError: 响应验证失败
    """
    if not response:
        raise DataValidationError(f"❌ {api_name}响应为空")
    
    # 基础验证
    validate_real_data(response, f"{api_name}响应")
    
    # 检查响应状态
    if 'status' in response and response['status'] == 'mock':
        raise MockDataDetectedError(f"❌ {api_name}返回模拟状态")
    
    # 检查数据字段
    if 'data' in response:
        validate_real_data(response['data'], f"{api_name}数据")
    
    return True

def log_data_validation_success(data_type: str, count: int = 1):
    """
    记录数据验证成功
    
    Args:
        data_type: 数据类型
        count: 数据数量
    """
    logger.info(f"✅ {data_type}数据验证成功: {count}条真实数据")

def create_real_data_error_response(error_msg: str) -> Dict[str, Any]:
    """
    创建真实数据错误响应
    
    Args:
        error_msg: 错误消息
        
    Returns:
        Dict: 错误响应
    """
    return {
        "success": False,
        "error": "REAL_DATA_REQUIRED",
        "message": error_msg,
        "timestamp": datetime.now().isoformat(),
        "data_policy": "系统只接受真实数据，拒绝任何模拟数据"
    }

# 装饰器：确保函数只处理真实数据
def real_data_only(data_type: str = "数据"):
    """
    装饰器：确保函数只处理真实数据
    
    Args:
        data_type: 数据类型描述
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 检查参数中的数据
            for arg in args:
                if arg is not None:
                    try:
                        validate_real_data(arg, data_type)
                    except (MockDataDetectedError, DataValidationError) as e:
                        logger.error(f"❌ {func.__name__}函数检测到模拟数据: {e}")
                        raise
            
            for key, value in kwargs.items():
                if value is not None:
                    try:
                        validate_real_data(value, f"{data_type}({key})")
                    except (MockDataDetectedError, DataValidationError) as e:
                        logger.error(f"❌ {func.__name__}函数参数{key}检测到模拟数据: {e}")
                        raise
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 检查返回结果
            if result is not None:
                try:
                    validate_real_data(result, f"{data_type}返回值")
                except (MockDataDetectedError, DataValidationError) as e:
                    logger.error(f"❌ {func.__name__}函数返回模拟数据: {e}")
                    raise
            
            return result
        return wrapper
    return decorator
