"""
Supabase配置和客户端管理
"""
import os
import logging
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseConfig:
    """Supabase配置管理"""

    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.database_url = os.getenv('DATABASE_URL')

        # 如果环境变量未设置，使用默认值
        if not self.url:
            self.url = 'https://zzukfxwavknskqcepsjb.supabase.co'
        if not self.anon_key:
            self.anon_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'
        if not self.service_role_key:
            self.service_role_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g'
        if not self.database_url:
            self.database_url = 'postgresql://postgres:WuFeng1234567890oO@db.zzukfxwavknskqcepsjb.supabase.co:5432/postgres'

        # 验证必要的配置
        if not all([self.url, self.anon_key, self.service_role_key]):
            raise ValueError(f"缺少必要的Supabase配置信息: URL={bool(self.url)}, ANON={bool(self.anon_key)}, SERVICE={bool(self.service_role_key)}")
    
    def get_client(self, use_service_role: bool = False) -> Client:
        """
        获取Supabase客户端
        
        Args:
            use_service_role: 是否使用service_role密钥（用于后端管理操作）
        
        Returns:
            Supabase客户端实例
        """
        key = self.service_role_key if use_service_role else self.anon_key
        return create_client(self.url, key)

# 全局配置实例
supabase_config = SupabaseConfig()

# 便捷函数
def get_supabase_client(use_service_role: bool = False) -> Client:
    """获取Supabase客户端的便捷函数"""
    return supabase_config.get_client(use_service_role)

def get_anon_client() -> Client:
    """获取匿名客户端（用于前端）"""
    return supabase_config.get_client(use_service_role=False)

def get_admin_client() -> Client:
    """获取管理员客户端（用于后端）"""
    return supabase_config.get_client(use_service_role=True)

# 测试连接函数
async def test_connection() -> bool:
    """测试Supabase连接"""
    try:
        client = get_admin_client()
        
        # 测试基本查询
        result = client.table('user_profiles').select('*').limit(1).execute()
        
        logger.info("Supabase连接测试成功")
        return True
        
    except Exception as e:
        logger.error(f"Supabase连接测试失败: {str(e)}")
        return False

# 数据库操作基类
class SupabaseManager:
    """Supabase数据库操作管理器"""
    
    def __init__(self, use_service_role: bool = True):
        self.client = get_supabase_client(use_service_role)
    
    def create_record(self, table: str, data: dict) -> dict:
        """创建记录"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"创建记录失败 - 表: {table}, 错误: {str(e)}")
            raise
    
    def get_record(self, table: str, filters: dict = None) -> list:
        """查询记录"""
        try:
            query = self.client.table(table).select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"查询记录失败 - 表: {table}, 错误: {str(e)}")
            raise
    
    def update_record(self, table: str, record_id: str, data: dict) -> dict:
        """更新记录"""
        try:
            result = self.client.table(table).update(data).eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"更新记录失败 - 表: {table}, ID: {record_id}, 错误: {str(e)}")
            raise
    
    def delete_record(self, table: str, record_id: str) -> bool:
        """删除记录"""
        try:
            result = self.client.table(table).delete().eq('id', record_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"删除记录失败 - 表: {table}, ID: {record_id}, 错误: {str(e)}")
            raise

# 导出主要组件
__all__ = [
    'SupabaseConfig',
    'supabase_config',
    'get_supabase_client',
    'get_anon_client',
    'get_admin_client',
    'test_connection',
    'SupabaseManager'
]
