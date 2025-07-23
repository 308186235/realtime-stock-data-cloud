import re
from typing import Union, Optional, List, Dict, Any
from decimal import Decimal, InvalidOperation

class ValidationError(Exception):
    """验证错误异常"""
    pass

class InputValidator:
    """输入验证器"""
    
    # 股票代码正则表达式
    STOCK_CODE_PATTERN = re.compile(r'^[0-9]{6}$')
    
    # 价格范围限制
    MIN_PRICE = Decimal('0.01')
    MAX_PRICE = Decimal('9999.99')
    
    # 数量范围限制
    MIN_QUANTITY = 1
    MAX_QUANTITY = 1000000
    
    @staticmethod
    def validate_stock_code(code: str) -> str:
        """验证股票代码"""
        if not code:
            raise ValidationError("股票代码不能为空")
        
        code = str(code).strip()
        
        if not InputValidator.STOCK_CODE_PATTERN.match(code):
            raise ValidationError(f"无效的股票代码格式: {code}")
        
        # 验证交易所代码
        if code.startswith('0') or code.startswith('3'):
            # 深圳交易所
            pass
        elif code.startswith('6'):
            # 上海交易所
            pass
        elif code.startswith('8') or code.startswith('4'):
            # 北京交易所
            pass
        else:
            raise ValidationError(f"不支持的股票代码: {code}")
        
        return code
    
    @staticmethod
    def validate_price(price: Union[str, float, int, Decimal]) -> Decimal:
        """验证价格"""
        if price is None:
            raise ValidationError("价格不能为空")
        
        try:
            price_decimal = Decimal(str(price))
        except (InvalidOperation, ValueError):
            raise ValidationError(f"无效的价格格式: {price}")
        
        if price_decimal <= 0:
            raise ValidationError("价格必须大于0")
        
        if price_decimal < InputValidator.MIN_PRICE:
            raise ValidationError(f"价格不能低于 {InputValidator.MIN_PRICE}")
        
        if price_decimal > InputValidator.MAX_PRICE:
            raise ValidationError(f"价格不能高于 {InputValidator.MAX_PRICE}")
        
        # 检查小数位数（股票价格最多2位小数）
        if price_decimal.as_tuple().exponent < -2:
            raise ValidationError("价格最多保留2位小数")
        
        return price_decimal
    
    @staticmethod
    def validate_quantity(quantity: Union[str, int]) -> int:
        """验证数量"""
        if quantity is None:
            raise ValidationError("数量不能为空")
        
        try:
            quantity_int = int(quantity)
        except (ValueError, TypeError):
            raise ValidationError(f"无效的数量格式: {quantity}")
        
        if quantity_int <= 0:
            raise ValidationError("数量必须大于0")
        
        if quantity_int < InputValidator.MIN_QUANTITY:
            raise ValidationError(f"数量不能少于 {InputValidator.MIN_QUANTITY}")
        
        if quantity_int > InputValidator.MAX_QUANTITY:
            raise ValidationError(f"数量不能超过 {InputValidator.MAX_QUANTITY}")
        
        # 检查是否为100的倍数（A股交易规则）
        if quantity_int % 100 != 0:
            raise ValidationError("A股交易数量必须为100股的倍数")
        
        return quantity_int
    
    @staticmethod
    def validate_trade_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证交易请求"""
        if not isinstance(data, dict):
            raise ValidationError("请求数据必须为字典格式")
        
        # 验证必需字段
        required_fields = ['code', 'quantity']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"缺少必需字段: {field}")
        
        validated_data = {}
        
        # 验证股票代码
        validated_data['code'] = InputValidator.validate_stock_code(data['code'])
        
        # 验证数量
        validated_data['quantity'] = InputValidator.validate_quantity(data['quantity'])
        
        # 验证价格（可选）
        if 'price' in data and data['price'] is not None:
            validated_data['price'] = InputValidator.validate_price(data['price'])
        
        return validated_data
    
    @staticmethod
    def validate_export_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证导出请求"""
        if not isinstance(data, dict):
            raise ValidationError("请求数据必须为字典格式")
        
        validated_data = {}
        
        # 验证导出类型
        export_type = data.get('type', 'all')
        valid_types = ['holdings', 'transactions', 'orders', 'all']
        
        if export_type not in valid_types:
            raise ValidationError(f"无效的导出类型: {export_type}，支持的类型: {valid_types}")
        
        validated_data['type'] = export_type
        
        return validated_data
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 100) -> str:
        """清理字符串输入"""
        if not isinstance(value, str):
            value = str(value)
        
        # 移除危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        # 限制长度
        if len(value) > max_length:
            value = value[:max_length]
        
        return value.strip()

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证API密钥格式"""
        if not api_key:
            return False
        
        # API密钥应该是字母数字组合，长度在10-50之间
        if not re.match(r'^[A-Za-z0-9_-]{10,50}$', api_key):
            return False
        
        return True
    
    @staticmethod
    def validate_jwt_token(token: str) -> bool:
        """验证JWT令牌格式"""
        if not token:
            return False
        
        # JWT令牌应该有3个部分，用.分隔
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        return True
    
    @staticmethod
    def check_rate_limit(client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """检查请求频率限制"""
        # 这里可以实现基于Redis的频率限制
        # 暂时返回True，实际使用时需要实现
        return True

# 便捷函数
def validate_trade_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证交易数据的便捷函数"""
    return InputValidator.validate_trade_request(data)

def validate_export_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证导出数据的便捷函数"""
    return InputValidator.validate_export_request(data)
