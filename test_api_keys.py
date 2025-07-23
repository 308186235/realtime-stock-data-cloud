#!/usr/bin/env python3
"""
测试API密钥和茶股帮token是否能正常获取股票数据
"""

import os
import socket
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class APIKeyTester:
    """API密钥测试器"""
    
    def __init__(self):
        self.stock_api_key = os.getenv("STOCK_API_KEY")
        self.chagubang_token = os.getenv("CHAGUBANG_TOKEN")
        self.chagubang_host = os.getenv("CHAGUBANG_HOST", "l1.chagubang.com")
        self.chagubang_port = int(os.getenv("CHAGUBANG_PORT", "6380"))
        
        print("🔑 API密钥配置:")
        print(f"  股票API密钥: {self.stock_api_key[:10]}..." if self.stock_api_key else "  股票API密钥: 未配置")
        print(f"  茶股帮Token: {self.chagubang_token[:10]}..." if self.chagubang_token else "  茶股帮Token: 未配置")
        print(f"  茶股帮服务器: {self.chagubang_host}:{self.chagubang_port}")
        print()
    
    def test_chagubang_connection(self):
        """测试茶股帮连接"""
        print("🔗 测试茶股帮连接...")
        
        if not self.chagubang_token:
            print("❌ 茶股帮Token未配置")
            return False
        
        try:
            # 创建TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            print(f"📡 连接到 {self.chagubang_host}:{self.chagubang_port}...")
            sock.connect((self.chagubang_host, self.chagubang_port))
            print("✅ TCP连接成功")
            
            # 发送Token进行认证
            print(f"🔐 发送Token认证: {self.chagubang_token}")
            sock.send(self.chagubang_token.encode('utf-8'))
            
            # 等待响应
            print("⏳ 等待服务器响应...")
            sock.settimeout(5)
            response = sock.recv(1024)
            
            if response:
                response_text = response.decode('utf-8', errors='ignore')
                print(f"📨 服务器响应: {response_text}")
                
                # 分析响应
                if "成功" in response_text or "success" in response_text.lower():
                    print("✅ 茶股帮Token认证成功")
                    return True
                elif "失败" in response_text or "error" in response_text.lower():
                    print("❌ 茶股帮Token认证失败")
                    return False
                else:
                    print("⚠️ 服务器响应未知，可能需要进一步处理")
                    return True
            else:
                print("⚠️ 服务器无响应")
                return False
                
        except socket.timeout:
            print("❌ 连接超时")
            return False
        except socket.error as e:
            print(f"❌ 连接错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False
        finally:
            try:
                sock.close()
            except:
                pass
    
    def test_stock_api_with_different_endpoints(self):
        """测试不同的股票API端点"""
        print("📊 测试股票API...")
        
        if not self.stock_api_key:
            print("❌ 股票API密钥未配置")
            return False
        
        # 可能的API端点
        test_endpoints = [
            # 通用股票API格式
            f"https://api.example.com/stock/quote?symbol=000001&key={self.stock_api_key}",
            f"https://api.example.com/v1/stock?code=000001&token={self.stock_api_key}",
            
            # 如果是茶股帮的HTTP API
            f"https://api.chagubang.com/stock?symbol=000001&token={self.stock_api_key}",
            f"https://l1.chagubang.com/api/stock?code=000001&key={self.stock_api_key}",
            
            # 其他可能的格式
            f"https://stock-api.com/quote?stock=000001&apikey={self.stock_api_key}",
        ]
        
        print(f"🔑 使用API密钥: {self.stock_api_key}")
        
        for i, endpoint in enumerate(test_endpoints, 1):
            print(f"\n📡 测试端点 {i}: {endpoint.split('?')[0]}...")
            
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ 成功获取数据: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                        return True
                    except:
                        print(f"   📄 响应内容: {response.text[:200]}...")
                        if "股票" in response.text or "price" in response.text.lower():
                            print("   ✅ 可能包含股票数据")
                            return True
                elif response.status_code == 401:
                    print("   ❌ 认证失败 - API密钥可能无效")
                elif response.status_code == 403:
                    print("   ❌ 访问被拒绝 - 权限不足")
                elif response.status_code == 404:
                    print("   ⚠️ 端点不存在")
                else:
                    print(f"   ⚠️ 其他状态: {response.text[:100]}...")
                    
            except requests.exceptions.Timeout:
                print("   ❌ 请求超时")
            except requests.exceptions.ConnectionError:
                print("   ❌ 连接错误")
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
        
        return False
    
    def test_api_key_as_chagubang_format(self):
        """测试API密钥是否为茶股帮格式的数据"""
        print("\n🔍 分析API密钥格式...")
        
        if not self.stock_api_key:
            print("❌ API密钥未配置")
            return False
        
        print(f"🔑 API密钥: {self.stock_api_key}")
        print(f"📏 长度: {len(self.stock_api_key)}")
        
        # 分析密钥格式
        if self.stock_api_key.startswith("QT_"):
            print("✅ 符合茶股帮Token格式 (QT_开头)")
            
            # 如果API密钥就是茶股帮Token，那么应该用TCP连接
            if self.stock_api_key == self.chagubang_token:
                print("✅ API密钥与茶股帮Token相同，这是正确的配置")
                return True
        
        return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始API密钥测试")
        print("=" * 60)
        
        results = {
            "chagubang_connection": False,
            "stock_api": False,
            "key_format": False
        }
        
        # 测试1: 茶股帮连接
        results["chagubang_connection"] = self.test_chagubang_connection()
        
        print("\n" + "-" * 60)
        
        # 测试2: 股票API
        results["stock_api"] = self.test_stock_api_with_different_endpoints()
        
        print("\n" + "-" * 60)
        
        # 测试3: 密钥格式分析
        results["key_format"] = self.test_api_key_as_chagubang_format()
        
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print(f"  茶股帮连接: {'✅ 成功' if results['chagubang_connection'] else '❌ 失败'}")
        print(f"  股票API: {'✅ 成功' if results['stock_api'] else '❌ 失败'}")
        print(f"  密钥格式: {'✅ 正确' if results['key_format'] else '⚠️ 需确认'}")
        
        # 总结
        if results["chagubang_connection"]:
            print("\n🎉 好消息: 茶股帮连接成功！")
            print("💡 建议: 使用茶股帮TCP连接获取实时股票数据")
        elif results["stock_api"]:
            print("\n🎉 好消息: 股票API可用！")
            print("💡 建议: 使用HTTP API获取股票数据")
        else:
            print("\n⚠️ 需要进一步配置:")
            print("1. 确认API密钥是否正确")
            print("2. 确认API服务端点")
            print("3. 检查网络连接")
        
        return results

if __name__ == "__main__":
    tester = APIKeyTester()
    results = tester.run_all_tests()
