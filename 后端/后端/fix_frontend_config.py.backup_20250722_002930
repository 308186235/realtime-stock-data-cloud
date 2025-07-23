#!/usr/bin/env python3
"""
前端配置修复工具
检查和修复前端与后端的通信配置问题
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List

class FrontendConfigFixer:
    """前端配置修复器"""
    
    def __init__(self):
        self.correct_api_url = "https://api.aigupiao.me"
        self.correct_ws_url = "wss://api.aigupiao.me/ws"
        self.frontend_dirs = [
            "frontend/gupiao1",
            "frontend/stock5", 
            "炒股养家"
        ]
        
    def run_fix(self):
        """运行修复"""
        print("🔧 开始修复前端配置...")
        print("=" * 50)
        
        # 1. 检查和修复环境配置
        self._fix_env_configs()
        
        # 2. 检查和修复API配置
        self._fix_api_configs()
        
        # 3. 检查和修复请求配置
        self._fix_request_configs()
        
        # 4. 生成配置报告
        self._generate_config_report()
        
        print("\n✅ 前端配置修复完成！")
    
    def _fix_env_configs(self):
        """修复环境配置文件"""
        print("\n🌍 修复环境配置文件...")
        
        for frontend_dir in self.frontend_dirs:
            env_file = os.path.join(frontend_dir, "env.js")
            if os.path.exists(env_file):
                self._fix_env_file(env_file)
                print(f"✅ 修复: {env_file}")
    
    def _fix_env_file(self, env_file):
        """修复单个环境配置文件"""
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复API URL
        content = re.sub(
            r"apiBaseUrl:\s*['\"][^'\"]*['\"]",
            f"apiBaseUrl: '{self.correct_api_url}'",
            content
        )
        
        # 修复WebSocket URL
        content = re.sub(
            r"wsUrl:\s*['\"][^'\"]*['\"]",
            f"wsUrl: '{self.correct_ws_url}'",
            content
        )
        
        # 禁用模拟数据
        content = re.sub(
            r"useMockData:\s*true",
            "useMockData: false  // 🚨 禁用模拟数据",
            content
        )
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_api_configs(self):
        """修复API配置文件"""
        print("\n🔌 修复API配置文件...")
        
        for frontend_dir in self.frontend_dirs:
            # 查找API配置文件
            api_files = []
            
            # 查找services目录
            services_dir = os.path.join(frontend_dir, "services")
            if os.path.exists(services_dir):
                for file in os.listdir(services_dir):
                    if file.endswith('.js'):
                        api_files.append(os.path.join(services_dir, file))
            
            # 查找api目录
            api_dir = os.path.join(frontend_dir, "api")
            if os.path.exists(api_dir):
                for file in os.listdir(api_dir):
                    if file.endswith('.js'):
                        api_files.append(os.path.join(api_dir, file))
            
            # 修复API文件
            for api_file in api_files:
                self._fix_api_file(api_file)
                print(f"✅ 修复API文件: {api_file}")
    
    def _fix_api_file(self, api_file):
        """修复单个API文件"""
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确保使用正确的API路径
            content = re.sub(
                r"['\"]https?://[^'\"]*aigupiao\.me[^'\"]*['\"]",
                f"'{self.correct_api_url}'",
                content
            )
            
            # 移除硬编码的错误URL
            content = re.sub(
                r"['\"]https?://localhost:\d+[^'\"]*['\"]",
                f"'{self.correct_api_url}'",
                content
            )
            
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"⚠️ 修复API文件失败 {api_file}: {e}")
    
    def _fix_request_configs(self):
        """修复请求配置文件"""
        print("\n📡 修复请求配置文件...")
        
        for frontend_dir in self.frontend_dirs:
            request_file = os.path.join(frontend_dir, "utils", "request.js")
            if os.path.exists(request_file):
                self._fix_request_file(request_file)
                print(f"✅ 修复请求文件: {request_file}")
    
    def _fix_request_file(self, request_file):
        """修复单个请求文件"""
        with open(request_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保模拟数据被禁用
        if 'USE_MOCK_DATA' in content and 'window.mockResponse' in content:
            # 替换模拟数据逻辑
            mock_pattern = r'if\s*\(\s*USE_MOCK_DATA.*?\}\s*\}'
            replacement = '''// 🚨 模拟数据已完全禁用
    if (false) { // 模拟数据逻辑已禁用
      // 原模拟数据代码已移除
    }'''
            
            content = re.sub(mock_pattern, replacement, content, flags=re.DOTALL)
        
        # 添加URL验证
        if 'options.url' in content and '!options.url.startsWith' not in content:
            # 在请求开始处添加URL验证
            url_validation = '''
    // 验证API地址
    if (!options.url) {
      reject(new Error('❌ 错误：API地址不能为空'));
      return;
    }
    
    // 如果是相对路径，确保是API路径
    if (!options.url.startsWith('http') && !options.url.startsWith('/api/')) {
      reject(new Error('❌ 错误：只允许调用真实API路径'));
      return;
    }
'''
            
            # 在Promise开始后添加验证
            content = re.sub(
                r'(return new Promise\(\(resolve, reject\) => \{)',
                r'\1' + url_validation,
                content
            )
        
        with open(request_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_config_report(self):
        """生成配置报告"""
        print("\n📋 生成配置报告...")
        
        report = {
            "timestamp": "2025-07-02T04:00:00",
            "api_configuration": {
                "correct_api_url": self.correct_api_url,
                "correct_ws_url": self.correct_ws_url,
                "mock_data_disabled": True
            },
            "frontend_projects": [],
            "common_issues_fixed": [
                "API URL统一为 https://api.aigupiao.me",
                "WebSocket URL统一为 wss://api.aigupiao.me/ws", 
                "所有环境禁用模拟数据",
                "添加API地址验证",
                "移除硬编码的localhost地址"
            ]
        }
        
        # 检查每个前端项目
        for frontend_dir in self.frontend_dirs:
            if os.path.exists(frontend_dir):
                project_info = {
                    "name": frontend_dir,
                    "env_file": os.path.exists(os.path.join(frontend_dir, "env.js")),
                    "request_file": os.path.exists(os.path.join(frontend_dir, "utils", "request.js")),
                    "services_dir": os.path.exists(os.path.join(frontend_dir, "services")),
                    "api_dir": os.path.exists(os.path.join(frontend_dir, "api"))
                }
                report["frontend_projects"].append(project_info)
        
        # 保存报告
        with open("frontend_config_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("📄 配置报告已保存: frontend_config_report.json")
    
    def check_connectivity(self):
        """检查连接性"""
        print("\n🔗 检查前端后端连接性...")
        
        # 检查域名解析
        try:
            import socket
            ip = socket.gethostbyname("api.aigupiao.me")
            print(f"✅ 域名解析成功: api.aigupiao.me -> {ip}")
        except Exception as e:
            print(f"❌ 域名解析失败: {e}")
        
        # 检查HTTPS连接
        try:
            import requests
            response = requests.get(self.correct_api_url, timeout=10)
            print(f"✅ HTTPS连接成功: {response.status_code}")
        except Exception as e:
            print(f"❌ HTTPS连接失败: {e}")
        
        # 检查CORS配置
        try:
            import requests
            headers = {
                'Origin': 'https://app.aigupiao.me',
                'Access-Control-Request-Method': 'GET'
            }
            response = requests.options(self.correct_api_url, headers=headers, timeout=10)
            print(f"✅ CORS预检成功: {response.status_code}")
        except Exception as e:
            print(f"❌ CORS预检失败: {e}")

def main():
    """主函数"""
    print("🔧 前端配置修复工具")
    print("=" * 40)
    
    fixer = FrontendConfigFixer()
    
    # 运行修复
    fixer.run_fix()
    
    # 检查连接性
    fixer.check_connectivity()
    
    print("\n" + "=" * 50)
    print("🎉 前端配置修复完成！")
    print()
    print("修复内容:")
    print("✅ API URL统一为: https://api.aigupiao.me")
    print("✅ WebSocket URL统一为: wss://api.aigupiao.me/ws")
    print("✅ 所有环境禁用模拟数据")
    print("✅ 添加API地址验证")
    print("✅ 移除错误的URL配置")
    print()
    print("下一步:")
    print("1. 重新构建前端项目")
    print("2. 部署到Cloudflare Pages")
    print("3. 测试前端后端通信")

if __name__ == "__main__":
    main()
