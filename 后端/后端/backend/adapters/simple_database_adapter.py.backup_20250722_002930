"""
简化数据库适配器 - 避免外键约束问题，用于演示和测试
"""
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.supabase import SupabaseManager

logger = logging.getLogger(__name__)

class SimpleDatabaseAdapter:
    """简化数据库适配器 - 使用系统配置表存储所有数据，避免外键约束"""
    
    def __init__(self):
        self.supabase = SupabaseManager()
    
    def _get_config_key(self, data_type: str, entity_id: str = None) -> str:
        """生成配置键"""
        if entity_id:
            return f"{data_type}_{entity_id}"
        return data_type
    
    def _save_entity(self, data_type: str, entity_data: Dict[str, Any], description: str = None) -> Dict[str, Any]:
        """保存实体到系统配置表"""
        try:
            entity_id = entity_data.get('id', str(uuid.uuid4()))
            entity_data['id'] = entity_id
            entity_data['created_at'] = entity_data.get('created_at', datetime.now().isoformat())
            entity_data['updated_at'] = datetime.now().isoformat()
            
            config_key = self._get_config_key(data_type, entity_id)
            
            result = self.supabase.client.table('system_config').upsert({
                'key': config_key,
                'value': entity_data,
                'description': description or f'{data_type}: {entity_data.get("name", entity_id)}'
            }).execute()
            
            if result.data:
                return {"success": True, "data": entity_data}
            else:
                raise Exception(f"保存{data_type}失败")
                
        except Exception as e:
            logger.error(f"保存{data_type}失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_entities(self, data_type: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取实体列表"""
        try:
            all_configs = self.supabase.get_record('system_config')
            entities = []
            
            for config in all_configs:
                if config['key'].startswith(f'{data_type}_') and isinstance(config.get('value'), dict):
                    entity_data = config['value']
                    
                    # 应用过滤器
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if entity_data.get(key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    entities.append(entity_data)
            
            return entities
            
        except Exception as e:
            logger.error(f"获取{data_type}列表失败: {str(e)}")
            return []
    
    def _get_entity(self, data_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取单个实体"""
        try:
            config_key = self._get_config_key(data_type, entity_id)
            result = self.supabase.get_record('system_config', {'key': config_key})
            
            if result:
                return result[0].get('value')
            return None
            
        except Exception as e:
            logger.error(f"获取{data_type}失败: {str(e)}")
            return None
    
    # ==================== 用户管理 ====================
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        return self._save_entity('user', user_data, f'用户: {user_data.get("username")}')
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """获取用户"""
        user = self._get_entity('user', user_id)
        return {"success": True, "data": user}
    
    def get_users(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取用户列表"""
        users = self._get_entities('user', filters)
        return {"success": True, "data": users}
    
    # ==================== 股票管理 ====================
    
    def create_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建股票"""
        # 使用股票代码作为ID
        stock_data['id'] = stock_data['code']
        return self._save_entity('stock', stock_data, f'股票: {stock_data.get("name")}')
    
    def get_stock(self, stock_code: str) -> Dict[str, Any]:
        """获取股票"""
        stock = self._get_entity('stock', stock_code)
        return {"success": True, "data": stock}
    
    def get_stocks(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取股票列表"""
        stocks = self._get_entities('stock', filters)
        return {"success": True, "data": stocks}
    
    # ==================== 投资组合管理 ====================
    
    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建投资组合"""
        return self._save_entity('portfolio', portfolio_data, f'投资组合: {portfolio_data.get("name")}')
    
    def get_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """获取投资组合"""
        portfolio = self._get_entity('portfolio', portfolio_id)
        return {"success": True, "data": portfolio}
    
    def get_portfolios(self, user_id: str = None) -> Dict[str, Any]:
        """获取投资组合列表"""
        filters = {'user_id': user_id} if user_id else None
        portfolios = self._get_entities('portfolio', filters)
        return {"success": True, "data": portfolios}
    
    def update_portfolio(self, portfolio_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新投资组合"""
        portfolio = self._get_entity('portfolio', portfolio_id)
        if not portfolio:
            return {"success": False, "error": "投资组合不存在"}
        
        portfolio.update(update_data)
        return self._save_entity('portfolio', portfolio, f'投资组合: {portfolio.get("name")}')
    
    # ==================== 持仓管理 ====================
    
    def create_holding(self, holding_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建持仓"""
        # 生成持仓ID
        holding_id = f"{holding_data['portfolio_id']}_{holding_data['stock_code']}"
        holding_data['id'] = holding_id
        return self._save_entity('holding', holding_data, f'持仓: {holding_data.get("stock_code")}')
    
    def get_holding(self, holding_id: str) -> Dict[str, Any]:
        """获取持仓"""
        holding = self._get_entity('holding', holding_id)
        return {"success": True, "data": holding}
    
    def get_holdings(self, portfolio_id: str = None) -> Dict[str, Any]:
        """获取持仓列表"""
        filters = {'portfolio_id': portfolio_id} if portfolio_id else None
        holdings = self._get_entities('holding', filters)
        return {"success": True, "data": holdings}
    
    def update_holding(self, holding_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新持仓"""
        holding = self._get_entity('holding', holding_id)
        if not holding:
            return {"success": False, "error": "持仓不存在"}
        
        holding.update(update_data)
        return self._save_entity('holding', holding, f'持仓: {holding.get("stock_code")}')
    
    # ==================== 交易记录管理 ====================
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建交易记录"""
        return self._save_entity('transaction', transaction_data, f'交易: {transaction_data.get("stock_code")}')
    
    def get_transactions(self, portfolio_id: str = None, stock_code: str = None) -> Dict[str, Any]:
        """获取交易记录"""
        filters = {}
        if portfolio_id:
            filters['portfolio_id'] = portfolio_id
        if stock_code:
            filters['stock_code'] = stock_code
        
        transactions = self._get_entities('transaction', filters)
        return {"success": True, "data": transactions}
    
    # ==================== 系统配置管理 ====================
    
    def get_system_config(self, key: str = None) -> Dict[str, Any]:
        """获取系统配置"""
        try:
            if key:
                result = self.supabase.get_record('system_config', {'key': key})
            else:
                result = self.supabase.get_record('system_config')
            
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"获取系统配置失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_system_config(self, key: str, value: Any, description: str = None) -> Dict[str, Any]:
        """更新系统配置"""
        try:
            data = {
                'key': key,
                'value': value,
                'description': description,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.client.table('system_config').upsert(data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"更新系统配置失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==================== 数据清理 ====================
    
    def cleanup_test_data(self, data_types: List[str] = None) -> Dict[str, Any]:
        """清理测试数据"""
        try:
            if not data_types:
                data_types = ['user', 'stock', 'portfolio', 'holding', 'transaction']
            
            cleaned_count = 0
            for data_type in data_types:
                # 删除所有该类型的数据
                all_configs = self.supabase.get_record('system_config')
                for config in all_configs:
                    if config['key'].startswith(f'{data_type}_'):
                        self.supabase.client.table('system_config').delete().eq('key', config['key']).execute()
                        cleaned_count += 1
            
            return {"success": True, "data": {"cleaned_count": cleaned_count}}
        except Exception as e:
            logger.error(f"清理测试数据失败: {str(e)}")
            return {"success": False, "error": str(e)}

# 全局简化数据库适配器实例
simple_db_adapter = SimpleDatabaseAdapter()
