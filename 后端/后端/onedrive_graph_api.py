#!/usr/bin/env python3
"""
OneDrive Microsoft Graph API集成
用于本地交易服务器上传数据到OneDrive
"""

import requests
import json
import time
from datetime import datetime
import os
import base64

class OneDriveGraphAPI:
    """OneDrive Microsoft Graph API管理器"""
    
    def __init__(self):
        # Microsoft Graph API配置
        # 您需要在Azure AD中注册应用获取这些值
        self.tenant_id = os.getenv('AZURE_TENANT_ID', 'common')
        self.client_id = os.getenv('AZURE_CLIENT_ID', '')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET', '')
        
        # API端点
        self.auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # 访问令牌
        self.access_token = None
        self.token_expires_at = 0
        
        # 加载保存的令牌
        self.load_token()
    
    def get_access_token_client_credentials(self):
        """使用客户端凭证模式获取访问令牌(适用于服务器应用)"""
        if not self.client_id or not self.client_secret:
            print("❌ 缺少Azure应用凭证,请设置环境变量")
            return False
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        try:
            response = requests.post(self.auth_url, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = time.time() + expires_in - 60  # 提前1分钟刷新
                
                self.save_token()
                print("✅ 获取访问令牌成功")
                return True
            else:
                print(f"❌ 获取访问令牌失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取访问令牌异常: {e}")
            return False
    
    def is_token_valid(self):
        """检查令牌是否有效"""
        return self.access_token and time.time() < self.token_expires_at
    
    def ensure_valid_token(self):
        """确保有有效的访问令牌"""
        if not self.is_token_valid():
            return self.get_access_token_client_credentials()
        return True
    
    def save_token(self):
        """保存令牌到文件"""
        token_data = {
            'access_token': self.access_token,
            'expires_at': self.token_expires_at,
            'timestamp': time.time()
        }
        
        try:
            with open('onedrive_token.json', 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"⚠️ 保存令牌失败: {e}")
    
    def load_token(self):
        """从文件加载令牌"""
        try:
            with open('onedrive_token.json', 'r') as f:
                token_data = json.load(f)
                self.access_token = token_data.get('access_token')
                self.token_expires_at = token_data.get('expires_at', 0)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ 加载令牌失败: {e}")
    
    def upload_file(self, file_path, content, folder_path="TradingData"):
        """上传文件到OneDrive"""
        if not self.ensure_valid_token():
            return False
        
        # 构建上传URL - 使用应用的OneDrive
        upload_url = f"{self.graph_url}/me/drive/root:/{folder_path}/{file_path}:/content"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        # 如果content是字典,转换为JSON字符串
        if isinstance(content, dict):
            content = json.dumps(content, indent=2, ensure_ascii=False)
        
        # 转换为字节
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        try:
            response = requests.put(upload_url, data=content, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                file_info = response.json()
                print(f"✅ 文件上传成功: {file_path}")
                return {
                    'success': True,
                    'file_id': file_info.get('id'),
                    'download_url': file_info.get('@microsoft.graph.downloadUrl'),
                    'web_url': file_info.get('webUrl')
                }
            else:
                print(f"❌ 文件上传失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 文件上传异常: {e}")
            return False
    
    def get_file_download_url(self, file_path, folder_path="TradingData"):
        """获取文件的下载链接"""
        if not self.ensure_valid_token():
            return None
        
        file_url = f"{self.graph_url}/me/drive/root:/{folder_path}/{file_path}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(file_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                file_info = response.json()
                return file_info.get('@microsoft.graph.downloadUrl')
            else:
                print(f"❌ 获取文件信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 获取文件信息异常: {e}")
            return None
    
    def create_public_share_link(self, file_path, folder_path="TradingData"):
        """创建公共分享链接"""
        if not self.ensure_valid_token():
            return None
        
        file_url = f"{self.graph_url}/me/drive/root:/{folder_path}/{file_path}:/createLink"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'type': 'view',  # 只读访问
            'scope': 'anonymous'  # 匿名访问
        }
        
        try:
            response = requests.post(file_url, json=data, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                link_info = response.json()
                return link_info.get('link', {}).get('webUrl')
            else:
                print(f"❌ 创建分享链接失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 创建分享链接异常: {e}")
            return None
    
    def upload_trading_data(self, data_type, data):
        """上传交易数据"""
        file_name = f"latest_{data_type}.json"
        
        trading_data = {
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "source": "local_trading_server",
            "data": data
        }
        
        result = self.upload_file(file_name, trading_data)
        
        if result and result.get('success'):
            # 尝试创建公共分享链接
            share_link = self.create_public_share_link(file_name)
            if share_link:
                result['share_link'] = share_link
                print(f"📤 公共分享链接: {share_link}")
        
        return result

# 全局OneDrive API实例
onedrive_api = OneDriveGraphAPI()

def setup_onedrive_credentials():
    """设置OneDrive凭证"""
    print("🔧 设置OneDrive凭证")
    print("=" * 50)
    print()
    print("请按照以下步骤设置Azure应用:")
    print("1. 访问 https://portal.azure.com")
    print("2. 进入 Azure Active Directory > 应用注册")
    print("3. 点击 '新注册' 创建应用")
    print("4. 设置应用名称,选择 '任何组织目录中的帐户'")
    print("5. 在 'API权限' 中添加 Microsoft Graph > 应用程序权限 > Files.ReadWrite.All")
    print("6. 点击 '授予管理员同意'")
    print("7. 在 '证书和密码' 中创建客户端密码")
    print("8. 复制应用程序(客户端)ID和客户端密码")
    print()
    
    # 设置环境变量
    client_id = input("请输入客户端ID: ").strip()
    client_secret = input("请输入客户端密码: ").strip()
    
    if client_id and client_secret:
        os.environ['AZURE_CLIENT_ID'] = client_id
        os.environ['AZURE_CLIENT_SECRET'] = client_secret
        
        # 保存到文件
        with open('.env_onedrive', 'w') as f:
            f.write(f"AZURE_CLIENT_ID={client_id}\n")
            f.write(f"AZURE_CLIENT_SECRET={client_secret}\n")
            f.write(f"AZURE_TENANT_ID=common\n")
        
        print("✅ 凭证已保存到 .env_onedrive 文件")
        
        # 测试连接
        onedrive_api.client_id = client_id
        onedrive_api.client_secret = client_secret
        
        if onedrive_api.get_access_token_client_credentials():
            print("🎉 OneDrive连接测试成功!")
            return True
        else:
            print("❌ OneDrive连接测试失败!")
            return False
    else:
        print("❌ 凭证不完整")
        return False

if __name__ == "__main__":
    # 测试OneDrive API
    print("🔧 测试OneDrive Graph API")
    
    # 如果没有凭证,进行设置
    if not onedrive_api.client_id or not onedrive_api.client_secret:
        if not setup_onedrive_credentials():
            exit(1)
    
    # 测试上传数据
    test_data = {
        "positions": [
            {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "quantity": 1000,
                "current_price": 13.50,
                "market_value": 13500
            }
        ],
        "summary": {
            "total_market_value": 13500
        }
    }
    
    result = onedrive_api.upload_trading_data("positions", test_data)
    if result:
        print("✅ 测试数据上传成功")
        print(f"📊 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 测试数据上传失败")
