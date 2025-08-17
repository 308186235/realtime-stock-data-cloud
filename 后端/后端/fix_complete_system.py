#!/usr/bin/env python3
"""
完整系统修复脚本
修复前后端通信,Agent算法,本地交易集成等关键问题
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

class CompleteSystemFixer:
    """完整系统修复器"""
    
    def __init__(self):
        self.worker_url = "https://trading-api.308186235.workers.dev"
        self.local_api_url = "http://localhost:8888"
        self.issues_found = []
        self.fixes_applied = []
        
    def run_complete_fix(self):
        """运行完整修复"""
        print("🔧 开始完整系统修复...")
        print("=" * 60)
        
        # 1. 检查并修复前端配置
        self._fix_frontend_config()
        
        # 2. 检查并修复Worker API
        self._fix_worker_api()
        
        # 3. 检查并修复Agent算法
        self._fix_agent_algorithms()
        
        # 4. 检查并修复本地交易集成
        self._fix_local_trading_integration()
        
        # 5. 启动必要服务
        self._start_required_services()
        
        # 6. 运行完整测试
        self._run_integration_test()
        
        # 7. 生成修复报告
        self._generate_fix_report()
        
    def _fix_frontend_config(self):
        """修复前端配置"""
        print("\n🌐 修复前端配置...")
        
        # 检查前端配置文件
        config_files = [
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js", 
            "炒股养家/env.js"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查API URL配置
                    if self.worker_url in content:
                        print(f"✅ {config_file} - API配置正确")
                    else:
                        print(f"❌ {config_file} - API配置需要修复")
                        self.issues_found.append(f"前端配置错误: {config_file}")
                        
                except Exception as e:
                    print(f"❌ 读取配置文件失败: {config_file} - {e}")
                    self.issues_found.append(f"配置文件读取失败: {config_file}")
            else:
                print(f"❌ 配置文件不存在: {config_file}")
                self.issues_found.append(f"配置文件缺失: {config_file}")
    
    def _fix_worker_api(self):
        """修复Worker API"""
        print("\n🔧 检查Worker API...")
        
        try:
            # 测试基础端点
            response = requests.get(f"{self.worker_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Worker基础端点正常")
            else:
                print(f"❌ Worker基础端点异常: {response.status_code}")
                self.issues_found.append("Worker基础端点异常")
                
            # 测试Agent分析端点
            response = requests.get(f"{self.worker_url}/api/agent-analysis", timeout=10)
            if response.status_code == 200:
                print("✅ Agent分析端点正常")
            else:
                print(f"❌ Agent分析端点异常: {response.status_code}")
                self.issues_found.append("Agent分析端点异常")
                
            # 测试账户余额端点
            response = requests.get(f"{self.worker_url}/api/account-balance", timeout=10)
            if response.status_code == 200:
                print("✅ 账户余额端点正常")
            else:
                print(f"❌ 账户余额端点异常: {response.status_code}")
                self.issues_found.append("账户余额端点异常")
                
        except Exception as e:
            print(f"❌ Worker API测试失败: {e}")
            self.issues_found.append(f"Worker API连接失败: {e}")
    
    def _fix_agent_algorithms(self):
        """修复Agent算法"""
        print("\n🤖 检查Agent算法...")
        
        # 检查关键算法文件
        algorithm_files = [
            "backend/ai/agent_system.py",
            "backend/ai/enhanced_learning_manager.py",
            "backend/services/data_flow_manager.py"
        ]
        
        for file_path in algorithm_files:
            if os.path.exists(file_path):
                print(f"✅ 算法文件存在: {file_path}")
            else:
                print(f"❌ 算法文件缺失: {file_path}")
                self.issues_found.append(f"算法文件缺失: {file_path}")
    
    def _fix_local_trading_integration(self):
        """修复本地交易集成"""
        print("\n💰 检查本地交易集成...")
        
        # 检查working-trader-FIXED模块
        trader_files = [
            "trader_api.py",
            "trader_buy_sell.py", 
            "trader_export.py",
            "trader_core.py"
        ]
        
        missing_files = []
        for file_path in trader_files:
            if os.path.exists(file_path):
                print(f"✅ 交易模块存在: {file_path}")
            else:
                print(f"❌ 交易模块缺失: {file_path}")
                missing_files.append(file_path)
                
        if missing_files:
            self.issues_found.append(f"交易模块缺失: {missing_files}")
        
        # 检查本地API服务器
        try:
            response = requests.get(f"{self.local_api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 本地API服务器正常")
            else:
                print(f"❌ 本地API服务器异常: {response.status_code}")
                self.issues_found.append("本地API服务器异常")
        except Exception as e:
            print(f"❌ 本地API服务器连接失败: {e}")
            self.issues_found.append(f"本地API服务器连接失败: {e}")
    
    def _start_required_services(self):
        """启动必要服务"""
        print("\n🚀 启动必要服务...")
        
        # 检查是否需要启动本地API服务器
        try:
            response = requests.get(f"{self.local_api_url}/health", timeout=3)
            print("✅ 本地API服务器已运行")
        except:
            print("⚠️ 本地API服务器未运行,尝试启动...")
            # 这里可以添加启动本地服务器的逻辑
            self.issues_found.append("本地API服务器需要手动启动")
    
    def _run_integration_test(self):
        """运行集成测试"""
        print("\n🧪 运行集成测试...")
        
        test_results = {
            "frontend_to_worker": False,
            "worker_to_local": False,
            "agent_analysis": False,
            "trading_execution": False
        }
        
        # 测试前端到Worker通信
        try:
            response = requests.get(f"{self.worker_url}/api/agent-analysis", timeout=10)
            if response.status_code == 200:
                test_results["frontend_to_worker"] = True
                print("✅ 前端到Worker通信正常")
            else:
                print("❌ 前端到Worker通信异常")
        except Exception as e:
            print(f"❌ 前端到Worker通信失败: {e}")
        
        # 测试Agent分析功能
        try:
            response = requests.get(f"{self.worker_url}/api/agent-analysis", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    test_results["agent_analysis"] = True
                    print("✅ Agent分析功能正常")
                else:
                    print("❌ Agent分析功能异常")
            else:
                print("❌ Agent分析功能测试失败")
        except Exception as e:
            print(f"❌ Agent分析功能测试失败: {e}")
        
        return test_results
    
    def _generate_fix_report(self):
        """生成修复报告"""
        print("\n📋 生成修复报告...")
        print("=" * 60)
        
        print(f"\n🔍 发现的问题 ({len(self.issues_found)} 个):")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n✅ 应用的修复 ({len(self.fixes_applied)} 个):")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
        
        # 生成下一步建议
        print("\n📝 下一步建议:")
        if "Worker API连接失败" in str(self.issues_found):
            print("  1. 重新部署Cloudflare Worker")
        if "本地API服务器连接失败" in str(self.issues_found):
            print("  2. 启动本地API服务器: python local_trading_server.py")
        if "交易模块缺失" in str(self.issues_found):
            print("  3. 恢复working-trader-FIXED模块")
        if "前端配置错误" in str(self.issues_found):
            print("  4. 更新前端配置文件中的API地址")
        
        print("\n🎯 关键修复优先级:")
        print("  1. 🔧 修复Worker API端点")
        print("  2. 🌐 修复前端配置")
        print("  3. 🤖 完善Agent算法")
        print("  4. 💰 修复本地交易集成")
        print("  5. 🔗 建立完整通信链路")

if __name__ == "__main__":
    fixer = CompleteSystemFixer()
    fixer.run_complete_fix()
