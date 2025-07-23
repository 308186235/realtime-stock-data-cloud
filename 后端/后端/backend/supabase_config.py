
# 增强数据库错误处理
import logging
from backend.services.unified_error_handler import unified_error_handler, ErrorSeverity, async_error_handler

logger = logging.getLogger(__name__)

@async_error_handler(severity=ErrorSeverity.HIGH)
async def safe_database_operation(func, *args, **kwargs):
    """安全的数据库操作包装器"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"数据库操作异常: {e}")
        # 这里可以添加数据库重连逻辑
        raise

"""
Supabase配置和连接管理
"""
import os
import logging
from typing import Dict, Any, Optional
from supabase import create_client, Client
import asyncio
import asyncpg

logger = logging.getLogger(__name__)

class SupabaseConfig:
    """Supabase配置管理"""
    
    def __init__(self):
        # 从环境变量或直接配置获取Supabase信息
        self.url = os.getenv('SUPABASE_URL', '')
        self.key = os.getenv('SUPABASE_ANON_KEY', '')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
        self.db_url = os.getenv('SUPABASE_DB_URL', '')
        
        # 如果环境变量为空,使用配置文件
        if not self.url:
            self._load_from_config()
        
        self.client: Optional[Client] = None
        self.db_pool: Optional[asyncpg.Pool] = None
    
    def _load_from_config(self):
        """从配置文件加载(项目创建后填写)"""
        # 实际的Supabase项目连接信息
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.db_url = os.getenv("DATABASE_URL")
    
    def get_client(self) -> Client:
        """获取Supabase客户端"""
        if not self.client:
            if not self.url or not self.key:
                raise ValueError("Supabase URL和Key未配置")
            
            self.client = create_client(self.url, self.key)
            logger.info("Supabase客户端初始化成功")
        
        return self.client
    
    async def get_db_pool(self) -> asyncpg.Pool:
        """获取数据库连接池"""
        if not self.db_pool:
            if not self.db_url:
                raise ValueError("数据库URL未配置")
            
            self.db_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )
            logger.info("数据库连接池创建成功")
        
        return self.db_pool
    
    async def close_db_pool(self):
        """关闭数据库连接池"""
        if self.db_pool:
            await self.db_pool.close()
            self.db_pool = None
            logger.info("数据库连接池已关闭")

# 全局配置实例
supabase_config = SupabaseConfig()

class SupabaseService:
    """Supabase服务封装"""
    
    def __init__(self):
        self.config = supabase_config
    
    async def get_portfolios(self, user_id: str) -> Dict[str, Any]:
        """获取用户投资组合"""
        try:
            client = self.config.get_client()
            
            response = client.table('portfolios').select(
                '*, holdings(*, stocks(name))'
            ).eq('user_id', user_id).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            logger.error(f"获取投资组合失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_stock_prices(self, stock_codes: list) -> Dict[str, Any]:
        """获取股票价格"""
        try:
            client = self.config.get_client()
            
            response = client.table('stock_prices').select(
                '*'
            ).in_('stock_code', stock_codes).order(
                'timestamp', desc=True
            ).limit(len(stock_codes)).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            logger.error(f"获取股票价格失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建交易记录"""
        try:
            client = self.config.get_client()
            
            response = client.table('transactions').insert(
                transaction_data
            ).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            logger.error(f"创建交易记录失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ai_analysis(self, stock_code: str = None) -> Dict[str, Any]:
        """获取AI分析结果"""
        try:
            client = self.config.get_client()
            
            query = client.table('ai_analysis').select('*')
            
            if stock_code:
                query = query.eq('stock_code', stock_code)
            
            response = query.order('created_at', desc=True).limit(10).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            logger.error(f"获取AI分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_strategies(self, user_id: str) -> Dict[str, Any]:
        """获取用户策略"""
        try:
            client = self.config.get_client()
            
            response = client.table('strategies').select(
                '*'
            ).eq('user_id', user_id).execute()
            
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            logger.error(f"获取策略失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_stock_price(self, stock_code: str, price_data: Dict[str, Any]) -> bool:
        """更新股票价格"""
        try:
            client = self.config.get_client()
            
            # 插入新的价格记录
            response = client.table('stock_prices').insert({
                'stock_code': stock_code,
                **price_data
            }).execute()
            
            return True
        except Exception as e:
            logger.error(f"更新股票价格失败: {str(e)}")
            return False
    
    async def batch_update_stock_prices(self, price_data_list: list) -> bool:
        """批量更新股票价格"""
        try:
            client = self.config.get_client()
            
            # 批量插入价格记录
            response = client.table('stock_prices').insert(
                price_data_list
            ).execute()
            
            logger.info(f"批量更新了 {len(price_data_list)} 条股票价格")
            return True
        except Exception as e:
            logger.error(f"批量更新股票价格失败: {str(e)}")
            return False

# 全局服务实例
supabase_service = SupabaseService()

async def test_connection():
    """测试Supabase连接"""
    try:
        client = supabase_config.get_client()
        
        # 测试查询系统配置表
        response = client.table('system_config').select('*').limit(1).execute()
        
        print("✅ Supabase连接测试成功!")
        print(f"📊 查询结果: {response.data}")
        return True
    except Exception as e:
        print(f"❌ Supabase连接测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试连接
    asyncio.run(test_connection())
