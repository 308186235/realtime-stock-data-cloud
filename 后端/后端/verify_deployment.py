#!/usr/bin/env python3
"""
验证Cloudflare Worker部署是否成功
检查OneDrive数据读取是否修复
"""

import json
import time
import requests
from datetime import datetime

class DeploymentVerifier:
    """部署验证器"""
    
    def __init__(self):
        self.api_base = "https://api.aigupiao.me"
        
    def check_api_version(self):
        """检查API版本"""
        print("🔍 检查API版本...")
        
        try:
            response = requests.get(f"{self.api_base}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    api_data = data['data']
                    version = api_data.get('version', '未知')
                    message = api_data.get('message', '未知')
                    fix_note = api_data.get('fix_note', '')
                    
                    print(f"✅ API响应正常")
                    print(f"   版本: {version}")
                    print(f"   消息: {message}")
                    
                    if 'OneDrive支持' in message or fix_note:
                        print(f"✅ 检测到OneDrive支持: {fix_note}")
                        return True
                    else:
                        print(f"❌ 未检测到OneDrive支持")
                        return False
                else:
                    print(f"❌ API响应格式异常")
                    return False
            else:
                print(f"❌ API响应失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API检查异常: {e}")
            return False
    
    def check_onedrive_data_access(self):
        """检查OneDrive数据访问"""
        print("\n📁 检查OneDrive数据访问...")
        
        endpoints = [
            ("持仓数据", "/api/local-trading/positions"),
            ("余额数据", "/api/local-trading/balance")
        ]
        
        onedrive_access_count = 0
        
        for name, path in endpoints:
            print(f"\n🔥 测试: {name}")
            
            try:
                response = requests.get(f"{self.api_base}{path}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data:
                        response_data = data['data']
                        api_source = response_data.get('api_source', '')
                        fix_note = response_data.get('fix_note', '')
                        timestamp = response_data.get('timestamp', '')
                        
                        print(f"✅ 响应成功")
                        print(f"   API来源: {api_source}")
                        print(f"   修复状态: {fix_note}")
                        print(f"   数据时间: {timestamp}")
                        
                        if 'onedrive' in api_source.lower():
                            print(f"✅ 检测到OneDrive数据源")
                            onedrive_access_count += 1
                        else:
                            print(f"⚠️ 未检测到OneDrive数据源")
                    else:
                        print(f"❌ 响应数据格式异常")
                else:
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 测试异常: {e}")
        
        print(f"\n📊 OneDrive访问统计: {onedrive_access_count}/{len(endpoints)}")
        return onedrive_access_count > 0
    
    def test_agent_complete_data(self):
        """测试Agent完整数据"""
        print("\n🤖 测试Agent完整数据...")
        
        try:
            response = requests.get(f"{self.api_base}/api/agent/complete-data", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    response_data = data['data']
                    
                    # 检查数据源
                    data_sources = response_data.get('data_sources', {})
                    trading_data = response_data.get('trading_data', {})
                    analysis_context = response_data.get('analysis_context', {})
                    
                    print(f"✅ Agent数据响应成功")
                    print(f"   数据源状态: {data_sources}")
                    
                    # 检查交易数据
                    if 'positions' in trading_data and 'balance' in trading_data:
                        print(f"✅ 包含完整交易数据")
                        
                        positions = trading_data['positions']
                        balance = trading_data['balance']
                        
                        # 检查数据来源
                        pos_source = positions.get('api_source', positions.get('source', ''))
                        bal_source = balance.get('api_source', balance.get('source', ''))
                        
                        print(f"   持仓数据来源: {pos_source}")
                        print(f"   余额数据来源: {bal_source}")
                        
                        if 'onedrive' in pos_source.lower() or 'onedrive' in bal_source.lower():
                            print(f"✅ Agent能够获取OneDrive数据")
                            return True
                        else:
                            print(f"⚠️ Agent未获取到OneDrive数据")
                            return False
                    else:
                        print(f"❌ 交易数据不完整")
                        return False
                else:
                    print(f"❌ 响应数据格式异常")
                    return False
            else:
                print(f"❌ 响应失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    def run_verification(self):
        """运行完整验证"""
        print("🚀 Cloudflare Worker部署验证")
        print("=" * 60)
        print(f"⏰ 验证时间: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # 1. 检查API版本
        print("📋 步骤1: 检查API版本和OneDrive支持")
        version_ok = self.check_api_version()
        
        # 2. 检查OneDrive数据访问
        print("\n📋 步骤2: 检查OneDrive数据访问")
        onedrive_ok = self.check_onedrive_data_access()
        
        # 3. 测试Agent完整数据
        print("\n📋 步骤3: 测试Agent完整数据")
        agent_ok = self.test_agent_complete_data()
        
        # 4. 生成验证报告
        print("\n" + "=" * 60)
        print("📊 部署验证报告")
        print("=" * 60)
        
        print(f"🔍 验证项目:")
        print(f"   {'✅' if version_ok else '❌'} API版本和OneDrive支持")
        print(f"   {'✅' if onedrive_ok else '❌'} OneDrive数据访问")
        print(f"   {'✅' if agent_ok else '❌'} Agent完整数据获取")
        
        success_count = sum([version_ok, onedrive_ok, agent_ok])
        success_rate = (success_count / 3) * 100
        
        print(f"\n📊 验证统计:")
        print(f"   成功率: {success_rate:.1f}% ({success_count}/3)")
        
        print(f"\n💡 验证结论:")
        if success_rate >= 100:
            print("🎉 部署验证完全成功!")
            print("✅ OneDrive数据读取问题已完全修复")
            print("✅ 云端Agent现在可以获取本地导出的真实数据")
            print("✅ 系统已准备就绪,可以正常使用")
        elif success_rate >= 66:
            print("⚠️ 部署验证大部分成功")
            print("📝 OneDrive数据读取基本正常,可能需要微调")
            print("🔧 建议检查OneDrive分享链接和权限设置")
        else:
            print("❌ 部署验证失败")
            print("💥 OneDrive数据读取问题未解决")
            print("🔧 需要重新检查Worker代码部署")
        
        print("\n📋 下一步操作:")
        if success_rate >= 66:
            print("1. 运行真实数据测试验证端到端流程")
            print("2. 监控API性能和稳定性")
            print("3. 开始使用真实交易软件导出数据")
        else:
            print("1. 检查Cloudflare Worker代码是否正确部署")
            print("2. 验证OneDrive分享链接是否有效")
            print("3. 查看Worker日志排查问题")
        
        print("=" * 60)
        
        return success_rate >= 66

def main():
    """主函数"""
    print("🔍 Cloudflare Worker部署验证工具")
    print("验证OneDrive数据读取是否修复")
    print()
    
    verifier = DeploymentVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🎯 验证成功!部署已完成")
        print("现在可以测试真实的数据导出流程")
    else:
        print("\n💥 验证失败!需要检查部署")
        print("请参考部署指南重新部署Worker")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
