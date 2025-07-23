#!/usr/bin/env python3
"""
Token同步服务
将本地Token更新同步到云端服务器
"""

import requests
import json
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Optional
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenSyncService:
    """Token同步服务"""
    
    def __init__(self):
        self.cloud_api_base = "https://agent.aigupiao.me"
        self.local_api_base = "http://localhost:8001"
        self.sync_interval = 30  # 30秒同步一次
        self.running = False
        
    async def sync_token_to_cloud(self, token: str, token_name: str = None) -> Dict:
        """将Token同步到云端"""
        try:
            if not token_name:
                token_name = f"local_token_{int(time.time())}"
            
            # 1. 先添加Token到云端
            add_response = await self._add_token_to_cloud(token, token_name)
            if not add_response.get('success'):
                logger.warning(f"添加Token到云端失败: {add_response.get('message')}")
            
            # 2. 切换到新Token
            switch_response = await self._switch_cloud_token(token_name)
            if switch_response.get('success'):
                logger.info(f"✅ Token同步到云端成功: {token_name}")
                return {
                    'success': True,
                    'message': f'Token同步成功: {token_name}',
                    'token_name': token_name
                }
            else:
                logger.error(f"切换云端Token失败: {switch_response.get('message')}")
                return {
                    'success': False,
                    'message': f'切换云端Token失败: {switch_response.get("message")}'
                }
                
        except Exception as e:
            logger.error(f"同步Token到云端失败: {e}")
            return {
                'success': False,
                'message': f'同步失败: {str(e)}'
            }
    
    async def _add_token_to_cloud(self, token: str, token_name: str) -> Dict:
        """添加Token到云端"""
        try:
            response = requests.post(
                f"{self.cloud_api_base}/tokens",
                json={
                    "token": token,
                    "name": token_name,
                    "priority": 8  # 本地同步的Token优先级较高
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
    
    async def _switch_cloud_token(self, token_name: str) -> Dict:
        """切换云端Token"""
        try:
            response = requests.post(
                f"{self.cloud_api_base}/switch-token",
                json={
                    "token_name": token_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
    
    async def get_cloud_token_status(self) -> Dict:
        """获取云端Token状态"""
        try:
            response = requests.get(f"{self.cloud_api_base}/tokens", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
    
    async def get_local_token_status(self) -> Dict:
        """获取本地Token状态"""
        try:
            response = requests.get(f"{self.local_api_base}/token/current", timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
    
    async def update_local_token(self, token: str) -> Dict:
        """更新本地Token"""
        try:
            response = requests.post(
                f"{self.local_api_base}/token/update",
                json={"token": token},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
    
    async def sync_from_cloud_to_local(self) -> Dict:
        """从云端同步Token到本地"""
        try:
            # 获取云端当前活跃Token
            cloud_status = await self.get_cloud_token_status()
            if not cloud_status.get('success'):
                return {
                    'success': False,
                    'message': f'获取云端状态失败: {cloud_status.get("message")}'
                }
            
            cloud_token = cloud_status.get('current_token_full')  # 假设云端返回完整Token
            if not cloud_token:
                return {
                    'success': False,
                    'message': '云端没有活跃Token'
                }
            
            # 获取本地当前Token
            local_status = await self.get_local_token_status()
            if local_status.get('success'):
                local_token = local_status.get('full_token')
                
                # 如果Token相同，无需同步
                if local_token == cloud_token:
                    return {
                        'success': True,
                        'message': 'Token已同步，无需更新'
                    }
            
            # 更新本地Token
            update_result = await self.update_local_token(cloud_token)
            if update_result.get('success'):
                logger.info("✅ 从云端同步Token到本地成功")
                return {
                    'success': True,
                    'message': '从云端同步Token成功'
                }
            else:
                return {
                    'success': False,
                    'message': f'更新本地Token失败: {update_result.get("message")}'
                }
                
        except Exception as e:
            logger.error(f"从云端同步Token失败: {e}")
            return {
                'success': False,
                'message': f'同步失败: {str(e)}'
            }
    
    async def start_auto_sync(self):
        """启动自动同步"""
        self.running = True
        logger.info("🔄 启动Token自动同步服务...")
        
        while self.running:
            try:
                # 检查云端和本地Token状态
                cloud_status = await self.get_cloud_token_status()
                local_status = await self.get_local_token_status()
                
                if cloud_status.get('success') and local_status.get('success'):
                    logger.info(f"Token状态检查 - 云端: {cloud_status.get('current_token', 'N/A')[:15]}..., "
                              f"本地: {local_status.get('current_token', 'N/A')}")
                
                # 等待下次同步
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"自动同步过程出错: {e}")
                await asyncio.sleep(self.sync_interval)
    
    def stop_auto_sync(self):
        """停止自动同步"""
        self.running = False
        logger.info("🛑 Token自动同步服务已停止")

# 使用示例
async def demo_sync():
    """同步演示"""
    sync_service = TokenSyncService()
    
    print("🔄 Token同步服务演示")
    print("=" * 50)
    
    # 获取当前状态
    print("📊 获取当前Token状态...")
    cloud_status = await sync_service.get_cloud_token_status()
    local_status = await sync_service.get_local_token_status()
    
    print(f"云端状态: {cloud_status}")
    print(f"本地状态: {local_status}")
    
    # 测试同步功能
    current_token = os.getenv("CHAGUBANG_TOKEN")
    if current_token:
        print(f"\n🔄 测试同步Token到云端: {current_token[:15]}...")
        sync_result = await sync_service.sync_token_to_cloud(current_token, "demo_sync_token")
        print(f"同步结果: {sync_result}")

if __name__ == "__main__":
    asyncio.run(demo_sync())
