#!/usr/bin/env python3
"""
OneDrive存储管理器
用于将交易数据上传到OneDrive,供Cloudflare Worker访问
"""

import requests
import json
import time
from datetime import datetime
import os

class OneDriveStorage:
    """OneDrive存储管理器"""
    
    def __init__(self):
        # OneDrive API配置
        self.client_id = "your_client_id"  # 需要在Azure注册应用获取
        self.client_secret = "your_client_secret"
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = "https://graph.microsoft.com/Files.ReadWrite"
        
        # API端点
        self.auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # 访问令牌
        self.access_token = None
        self.refresh_token = None
        
        # 加载保存的令牌
        self.load_tokens()
    
    def get_auth_url(self):
        """获取授权URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_mode': 'query'
        }
        
        auth_url = f"{self.auth_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return auth_url
    
    def get_access_token(self, auth_code):
        """使用授权码获取访问令牌"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            
            # 保存令牌
            self.save_tokens()
            return True
        else:
            print(f"获取访问令牌失败: {response.text}")
            return False
    
    def refresh_access_token(self):
        """刷新访问令牌"""
        if not self.refresh_token:
            return False
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            self.save_tokens()
            return True
        else:
            print(f"刷新访问令牌失败: {response.text}")
            return False
    
    def save_tokens(self):
        """保存令牌到文件"""
        tokens = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'timestamp': time.time()
        }
        
        with open('onedrive_tokens.json', 'w') as f:
            json.dump(tokens, f)
    
    def load_tokens(self):
        """从文件加载令牌"""
        try:
            with open('onedrive_tokens.json', 'r') as f:
                tokens = json.load(f)
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
        except FileNotFoundError:
            pass
    
    def upload_file(self, file_path, content, folder_path="TradingData"):
        """上传文件到OneDrive"""
        if not self.access_token:
            print("没有访问令牌,请先授权")
            return False
        
        # 构建上传URL
        upload_url = f"{self.graph_url}/me/drive/root:/{folder_path}/{file_path}:/content"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # 如果content是字典,转换为JSON字符串
        if isinstance(content, dict):
            content = json.dumps(content, indent=2, ensure_ascii=False)
        
        response = requests.put(upload_url, data=content.encode('utf-8'), headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ 文件上传成功: {file_path}")
            return True
        elif response.status_code == 401:
            # 令牌过期,尝试刷新
            if self.refresh_access_token():
                return self.upload_file(file_path, content, folder_path)
            else:
                print("访问令牌过期且刷新失败")
                return False
        else:
            print(f"❌ 文件上传失败: {response.status_code} - {response.text}")
            return False
    
    def get_file_download_url(self, file_path, folder_path="TradingData"):
        """获取文件的公共下载链接"""
        if not self.access_token:
            return None
        
        # 获取文件信息
        file_url = f"{self.graph_url}/me/drive/root:/{folder_path}/{file_path}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(file_url, headers=headers)
        
        if response.status_code == 200:
            file_info = response.json()
            # 获取下载URL
            download_url = file_info.get('@microsoft.graph.downloadUrl')
            return download_url
        elif response.status_code == 401:
            # 令牌过期,尝试刷新
            if self.refresh_access_token():
                return self.get_file_download_url(file_path, folder_path)
        
        return None
    
    def upload_trading_data(self, data_type, data):
        """上传交易数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{data_type}_{timestamp}.json"
        
        # 添加时间戳到数据
        data_with_timestamp = {
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        return self.upload_file(file_name, data_with_timestamp)
    
    def upload_latest_data(self, data_type, data):
        """上传最新数据(覆盖同名文件)"""
        file_name = f"latest_{data_type}.json"
        
        data_with_timestamp = {
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "source": "local_trading_server"
        }
        
        return self.upload_file(file_name, data_with_timestamp)

# 全局OneDrive管理器实例
onedrive_storage = OneDriveStorage()

def setup_onedrive_auth():
    """设置OneDrive授权"""
    print("🔧 设置OneDrive授权")
    print("=" * 50)
    
    # 获取授权URL
    auth_url = onedrive_storage.get_auth_url()
    print(f"请访问以下URL进行授权:")
    print(auth_url)
    print()
    print("授权后,请复制回调URL中的code参数值")
    
    # 等待用户输入授权码
    auth_code = input("请输入授权码: ").strip()
    
    if onedrive_storage.get_access_token(auth_code):
        print("✅ OneDrive授权成功!")
        return True
    else:
        print("❌ OneDrive授权失败!")
        return False

if __name__ == "__main__":
    # 测试OneDrive集成
    print("🔧 测试OneDrive集成")
    
    # 如果没有访问令牌,进行授权
    if not onedrive_storage.access_token:
        setup_onedrive_auth()
    
    # 测试上传数据
    test_data = {
        "positions": [
            {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "quantity": 1000,
                "current_price": 13.50
            }
        ]
    }
    
    if onedrive_storage.upload_latest_data("positions", test_data):
        print("✅ 测试数据上传成功")
        
        # 获取下载链接
        download_url = onedrive_storage.get_file_download_url("latest_positions.json")
        if download_url:
            print(f"📥 下载链接: {download_url}")
        else:
            print("❌ 获取下载链接失败")
    else:
        print("❌ 测试数据上传失败")
