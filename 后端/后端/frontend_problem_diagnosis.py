#!/usr/bin/env python3
"""
前端问题诊断脚本
使用MCP分析发现的前端问题进行深度诊断
"""
import os
import json
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class FrontendProblemDiagnoser:
    """前端问题诊断器"""
    
    def __init__(self):
        self.frontend_projects = [
            "frontend/gupiao1",
            "frontend/stock5", 
            "炒股养家",
            "vercel-frontend"
        ]
        
        self.api_endpoints = {
            "main": "https://api.aigupiao.me",
            "local": "http://localhost:8000",
            "backup": "http://localhost:8001"
        }
        
        self.diagnosis_results = {}
        
    def print_banner(self):
        """打印诊断横幅"""
        print("=" * 80)
        print("🔍 前端问题深度诊断")
        print("=" * 80)
        print(f"📅 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 基于MCP分析结果进行问题诊断")
        print("=" * 80)
        
    def diagnose_project_structure(self):
        """诊断项目结构"""
        print("\n📁 诊断项目结构...")
        print("-" * 60)
        
        structure_issues = []
        
        for project in self.frontend_projects:
            print(f"检查项目: {project}")
            
            if not os.path.exists(project):
                structure_issues.append(f"❌ 项目目录不存在: {project}")
                continue
                
            # 检查关键文件
            key_files = {
                "package.json": "包配置文件",
                "main.js": "主入口文件",
                "App.vue": "主应用组件",
                "pages.json": "页面配置",
                "manifest.json": "应用清单"
            }
            
            missing_files = []
            for file, desc in key_files.items():
                file_path = os.path.join(project, file)
                if not os.path.exists(file_path):
                    missing_files.append(f"  ⚠️ 缺少{desc}: {file}")
                    
            if missing_files:
                structure_issues.extend(missing_files)
            else:
                print(f"  ✅ 项目结构完整")
                
        self.diagnosis_results['structure'] = structure_issues
        
    def diagnose_dependencies(self):
        """诊断依赖问题"""
        print("\n📦 诊断依赖问题...")
        print("-" * 60)
        
        dependency_issues = []
        
        for project in self.frontend_projects:
            package_json = os.path.join(project, "package.json")
            
            if not os.path.exists(package_json):
                continue
                
            print(f"检查依赖: {project}")
            
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                # 检查关键依赖
                deps = package_data.get('dependencies', {})
                dev_deps = package_data.get('devDependencies', {})
                
                # uni-app项目特殊检查
                if '@dcloudio/uni-app' in deps:
                    uni_version = deps['@dcloudio/uni-app']
                    if uni_version.startswith('^2.'):
                        dependency_issues.append(f"⚠️ {project}: uni-app版本过旧 ({uni_version})")
                        
                # Vue版本检查
                if 'vue' in deps:
                    vue_version = deps['vue']
                    if vue_version.startswith('^2.') and '@dcloudio/uni-app' in deps:
                        # uni-app项目使用Vue2是正常的
                        pass
                    elif vue_version.startswith('^2.'):
                        dependency_issues.append(f"⚠️ {project}: Vue版本可能需要升级 ({vue_version})")
                        
                # 检查node_modules
                node_modules = os.path.join(project, "node_modules")
                if not os.path.exists(node_modules):
                    dependency_issues.append(f"❌ {project}: 依赖未安装 (缺少node_modules)")
                    
                print(f"  ✅ 依赖配置检查完成")
                
            except Exception as e:
                dependency_issues.append(f"❌ {project}: package.json解析失败 - {str(e)}")
                
        self.diagnosis_results['dependencies'] = dependency_issues
        
    def diagnose_api_configuration(self):
        """诊断API配置"""
        print("\n🌐 诊断API配置...")
        print("-" * 60)
        
        api_issues = []
        
        for project in self.frontend_projects:
            print(f"检查API配置: {project}")
            
            # 检查环境配置文件
            env_files = ["env.js", "config.js", ".env"]
            config_found = False
            
            for env_file in env_files:
                env_path = os.path.join(project, env_file)
                if os.path.exists(env_path):
                    config_found = True
                    try:
                        with open(env_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 检查API地址配置
                        if 'localhost' in content:
                            api_issues.append(f"⚠️ {project}: 仍使用localhost地址")
                        elif 'api.aigupiao.me' not in content:
                            api_issues.append(f"⚠️ {project}: API地址可能不正确")
                        else:
                            print(f"  ✅ API地址配置正确")
                            
                        # 检查模拟数据配置
                        if 'useMockData: true' in content or 'mock: true' in content:
                            api_issues.append(f"⚠️ {project}: 模拟数据仍然启用")
                            
                    except Exception as e:
                        api_issues.append(f"❌ {project}: 配置文件读取失败 - {str(e)}")
                        
            if not config_found:
                api_issues.append(f"❌ {project}: 未找到环境配置文件")
                
        self.diagnosis_results['api_config'] = api_issues
        
    def diagnose_build_issues(self):
        """诊断构建问题"""
        print("\n🔨 诊断构建问题...")
        print("-" * 60)
        
        build_issues = []
        
        for project in self.frontend_projects:
            if not os.path.exists(project):
                continue
                
            print(f"检查构建配置: {project}")
            
            # 检查构建脚本
            package_json = os.path.join(project, "package.json")
            if os.path.exists(package_json):
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        package_data = json.load(f)
                        
                    scripts = package_data.get('scripts', {})
                    
                    # 检查必要的脚本
                    required_scripts = ['dev', 'build']
                    for script in required_scripts:
                        if script not in scripts:
                            build_issues.append(f"⚠️ {project}: 缺少{script}脚本")
                            
                    # 检查构建输出目录
                    if 'build' in scripts:
                        build_cmd = scripts['build']
                        if 'dist' not in build_cmd and 'build' not in build_cmd:
                            build_issues.append(f"⚠️ {project}: 构建脚本可能有问题")
                            
                    print(f"  ✅ 构建配置检查完成")
                    
                except Exception as e:
                    build_issues.append(f"❌ {project}: 构建配置检查失败 - {str(e)}")
                    
        self.diagnosis_results['build'] = build_issues
        
    def diagnose_runtime_connectivity(self):
        """诊断运行时连接性"""
        print("\n🔗 诊断运行时连接性...")
        print("-" * 60)
        
        connectivity_issues = []
        
        # 测试API端点连接
        for name, url in self.api_endpoints.items():
            print(f"测试连接: {name} ({url})")
            
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {name} API连接正常")
                else:
                    connectivity_issues.append(f"⚠️ {name} API返回状态码: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                connectivity_issues.append(f"❌ {name} API连接失败 - 服务不可达")
            except requests.exceptions.Timeout:
                connectivity_issues.append(f"⚠️ {name} API连接超时")
            except Exception as e:
                connectivity_issues.append(f"❌ {name} API测试失败 - {str(e)}")
                
        self.diagnosis_results['connectivity'] = connectivity_issues
        
    def diagnose_common_errors(self):
        """诊断常见错误"""
        print("\n🐛 诊断常见错误...")
        print("-" * 60)
        
        common_errors = []
        
        # 检查常见的错误模式
        error_patterns = {
            "CORS错误": ["Access-Control-Allow-Origin", "CORS policy"],
            "模块导入错误": ["Cannot resolve module", "Module not found"],
            "API调用错误": ["404", "500", "Network Error"],
            "构建错误": ["Build failed", "Compilation error"],
            "路由错误": ["Cannot match route", "Page not found"]
        }
        
        for project in self.frontend_projects:
            if not os.path.exists(project):
                continue
                
            print(f"检查常见错误: {project}")
            
            # 检查日志文件
            log_files = ["error.log", "build.log", "console.log"]
            for log_file in log_files:
                log_path = os.path.join(project, log_file)
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                            
                        for error_type, patterns in error_patterns.items():
                            for pattern in patterns:
                                if pattern in log_content:
                                    common_errors.append(f"⚠️ {project}: 发现{error_type}")
                                    break
                                    
                    except Exception as e:
                        common_errors.append(f"❌ {project}: 日志文件读取失败 - {str(e)}")
                        
        self.diagnosis_results['common_errors'] = common_errors
        
    def generate_diagnosis_report(self):
        """生成诊断报告"""
        print("\n" + "=" * 80)
        print("📊 前端问题诊断报告")
        print("=" * 80)
        
        total_issues = 0
        
        for category, issues in self.diagnosis_results.items():
            if issues:
                total_issues += len(issues)
                print(f"\n🔍 {category.upper()}问题 ({len(issues)}个):")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"\n✅ {category.upper()}: 无问题发现")
                
        print(f"\n📈 问题统计:")
        print(f"  • 总问题数: {total_issues}")
        print(f"  • 检查类别: {len(self.diagnosis_results)}")
        
        # 生成修复建议
        print(f"\n💡 修复建议:")
        
        if self.diagnosis_results.get('structure'):
            print("  🏗️ 项目结构问题:")
            print("    - 检查缺失的关键文件")
            print("    - 确保项目目录结构正确")
            
        if self.diagnosis_results.get('dependencies'):
            print("  📦 依赖问题:")
            print("    - 运行 npm install 安装依赖")
            print("    - 检查package.json中的版本冲突")
            print("    - 考虑升级过时的依赖包")
            
        if self.diagnosis_results.get('api_config'):
            print("  🌐 API配置问题:")
            print("    - 统一API地址为 https://api.aigupiao.me")
            print("    - 禁用所有模拟数据配置")
            print("    - 检查环境变量配置")
            
        if self.diagnosis_results.get('build'):
            print("  🔨 构建问题:")
            print("    - 检查构建脚本配置")
            print("    - 清理构建缓存")
            print("    - 重新安装依赖")
            
        if self.diagnosis_results.get('connectivity'):
            print("  🔗 连接问题:")
            print("    - 检查网络连接")
            print("    - 验证API服务状态")
            print("    - 检查防火墙设置")
            
        if total_issues == 0:
            print("  🎉 恭喜!未发现明显问题")
            print("  💡 如果仍有问题,建议:")
            print("    - 清除浏览器缓存")
            print("    - 重启开发服务器")
            print("    - 检查控制台错误信息")
            
        print("=" * 80)
        
    def run_diagnosis(self):
        """运行完整诊断"""
        self.print_banner()
        
        # 执行各项诊断
        self.diagnose_project_structure()
        self.diagnose_dependencies()
        self.diagnose_api_configuration()
        self.diagnose_build_issues()
        self.diagnose_runtime_connectivity()
        self.diagnose_common_errors()
        
        # 生成报告
        self.generate_diagnosis_report()

def main():
    """主函数"""
    diagnoser = FrontendProblemDiagnoser()
    diagnoser.run_diagnosis()

if __name__ == "__main__":
    main()
