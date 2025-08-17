#!/usr/bin/env python3
"""
项目修复验证工具
验证配置修复后的项目状态
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any

class ProjectFixVerifier:
    """项目修复验证器"""
    
    def __init__(self):
        self.verification_results = []
        self.expected_config = {
            "api_base_url": "https://api.aigupiao.me",
            "ws_url": "wss://api.aigupiao.me/ws"
        }
        
    def run_verification(self):
        """运行验证"""
        print("🔍 开始验证项目修复结果...")
        print("=" * 50)
        
        # 1. 验证前端配置统一性
        self._verify_frontend_configs()
        
        # 2. 验证Agent策略配置
        self._verify_agent_configs()
        
        # 3. 验证部署配置
        self._verify_deployment_configs()
        
        # 4. 验证文件结构
        self._verify_file_structure()
        
        # 5. 生成验证报告
        self._generate_verification_report()
    
    def _verify_frontend_configs(self):
        """验证前端配置"""
        print("🎨 验证前端配置统一性...")
        
        frontend_files = [
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js",
            "炒股养家/env.js"
        ]
        
        config_consistency = True
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                result = self._check_frontend_config(file_path)
                self.verification_results.append(result)
                
                if not result["passed"]:
                    config_consistency = False
                    print(f"❌ {file_path}: {result['issue']}")
                else:
                    print(f"✅ {file_path}: 配置正确")
            else:
                print(f"⚠️ {file_path}: 文件不存在")
        
        if config_consistency:
            print("✅ 前端配置统一性验证通过")
        else:
            print("❌ 前端配置存在不一致")
    
    def _check_frontend_config(self, file_path: str) -> Dict[str, Any]:
        """检查单个前端配置文件"""
        result = {
            "file": file_path,
            "type": "frontend_config",
            "passed": True,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查开发环境API地址 (支持中英文注释)
            dev_api_pattern = r"(// 开发环境|// Development environment)[\s\S]*?apiBaseUrl:\s*['\"]([^'\"]*)"
            dev_match = re.search(dev_api_pattern, content)
            
            if dev_match:
                dev_api = dev_match.group(2)  # 修改为group(2)因为现在有两个捕获组
                if dev_api != self.expected_config["api_base_url"]:
                    result["issues"].append(f"开发环境API地址不正确: {dev_api}")
                    result["passed"] = False
            else:
                result["issues"].append("未找到开发环境API配置")
                result["passed"] = False
            
            # 检查生产环境API地址 (支持中英文注释)
            prod_api_pattern = r"(// 生产环境|// Production environment)[\s\S]*?apiBaseUrl:\s*['\"]([^'\"]*)"
            prod_match = re.search(prod_api_pattern, content)

            if prod_match:
                prod_api = prod_match.group(2)  # 修改为group(2)
                if prod_api != self.expected_config["api_base_url"]:
                    result["issues"].append(f"生产环境API地址不正确: {prod_api}")
                    result["passed"] = False
            else:
                result["issues"].append("未找到生产环境API配置")
                result["passed"] = False
            
            # 检查WebSocket地址
            ws_pattern = r"wsUrl:\s*['\"]([^'\"]*)"
            ws_matches = re.findall(ws_pattern, content)
            
            for ws_url in ws_matches:
                if ws_url != self.expected_config["ws_url"]:
                    result["issues"].append(f"WebSocket地址不正确: {ws_url}")
                    result["passed"] = False
            
            if result["passed"]:
                result["message"] = "配置正确"
            else:
                result["issue"] = "; ".join(result["issues"])
                
        except Exception as e:
            result["passed"] = False
            result["issue"] = f"文件读取失败: {e}"
        
        return result
    
    def _verify_agent_configs(self):
        """验证Agent配置"""
        print("\n🤖 验证Agent策略配置...")
        
        # 检查统一策略配置文件
        strategy_config_path = "config/trading_strategy.json"
        
        if os.path.exists(strategy_config_path):
            result = self._check_strategy_config(strategy_config_path)
            self.verification_results.append(result)
            
            if result["passed"]:
                print(f"✅ {strategy_config_path}: 策略配置完整")
            else:
                print(f"❌ {strategy_config_path}: {result['issue']}")
        else:
            print(f"❌ {strategy_config_path}: 统一策略配置文件不存在")
            self.verification_results.append({
                "file": strategy_config_path,
                "type": "strategy_config",
                "passed": False,
                "issue": "文件不存在"
            })
        
        # 检查Agent文件是否存在
        agent_files = [
            "auto_cleanup_trading_agent.py",
            "backend/ai/agent_system.py",
            "backend/services/auto_trader_service.py"
        ]
        
        for file_path in agent_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}: 文件存在")
            else:
                print(f"⚠️ {file_path}: 文件不存在")
    
    def _check_strategy_config(self, file_path: str) -> Dict[str, Any]:
        """检查策略配置文件"""
        result = {
            "file": file_path,
            "type": "strategy_config",
            "passed": True,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必要的配置项
            required_sections = ["risk_management", "trading_rules", "strategies"]
            
            for section in required_sections:
                if section not in config:
                    result["issues"].append(f"缺少配置节: {section}")
                    result["passed"] = False
            
            # 检查风险管理配置
            if "risk_management" in config:
                risk_config = config["risk_management"]
                required_risk_params = ["max_position_size", "stop_loss_pct", "take_profit_pct"]
                
                for param in required_risk_params:
                    if param not in risk_config:
                        result["issues"].append(f"缺少风险参数: {param}")
                        result["passed"] = False
            
            if result["passed"]:
                result["message"] = "策略配置完整"
            else:
                result["issue"] = "; ".join(result["issues"])
                
        except Exception as e:
            result["passed"] = False
            result["issue"] = f"配置文件解析失败: {e}"
        
        return result
    
    def _verify_deployment_configs(self):
        """验证部署配置"""
        print("\n🚀 验证部署配置...")
        
        # 检查Cloudflare配置文件
        cloudflare_files = ["_redirects", "wrangler.toml"]
        
        for file_path in cloudflare_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}: 文件存在")
                result = {
                    "file": file_path,
                    "type": "deployment_config",
                    "passed": True,
                    "message": "文件存在"
                }
            else:
                print(f"❌ {file_path}: 文件不存在")
                result = {
                    "file": file_path,
                    "type": "deployment_config",
                    "passed": False,
                    "issue": "文件不存在"
                }
            
            self.verification_results.append(result)
        
        # 检查部署脚本
        deploy_script = "deploy.sh"
        if os.path.exists(deploy_script):
            print(f"✅ {deploy_script}: 部署脚本存在")
        else:
            print(f"❌ {deploy_script}: 部署脚本不存在")
        
        # 检查后端CORS配置
        self._verify_cors_config()
    
    def _verify_cors_config(self):
        """验证CORS配置"""
        print("\n🔒 验证CORS配置...")
        
        cors_files = ["backend/app.py", "cloud_app.py"]
        
        for file_path in cors_files:
            if os.path.exists(file_path):
                result = self._check_cors_config(file_path)
                self.verification_results.append(result)
                
                if result["passed"]:
                    print(f"✅ {file_path}: CORS配置正确")
                else:
                    print(f"❌ {file_path}: {result['issue']}")
            else:
                print(f"⚠️ {file_path}: 文件不存在")
    
    def _check_cors_config(self, file_path: str) -> Dict[str, Any]:
        """检查CORS配置"""
        result = {
            "file": file_path,
            "type": "cors_config",
            "passed": True,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含必要的域名
            required_domains = [
                "app.aigupiao.me",
                "aigupiao.me",
                "localhost"
            ]
            
            for domain in required_domains:
                if domain not in content:
                    result["issues"].append(f"缺少域名: {domain}")
                    result["passed"] = False
            
            # 检查CORS中间件配置
            if "CORSMiddleware" not in content:
                result["issues"].append("缺少CORS中间件配置")
                result["passed"] = False
            
            if result["passed"]:
                result["message"] = "CORS配置正确"
            else:
                result["issue"] = "; ".join(result["issues"])
                
        except Exception as e:
            result["passed"] = False
            result["issue"] = f"文件读取失败: {e}"
        
        return result
    
    def _verify_file_structure(self):
        """验证文件结构"""
        print("\n📁 验证文件结构...")
        
        # 检查关键目录
        important_dirs = [
            "frontend/gupiao1",
            "炒股养家",
            "backend",
            "config"
        ]
        
        for dir_path in important_dirs:
            if os.path.exists(dir_path):
                size = self._get_dir_size(dir_path)
                print(f"✅ {dir_path}: 存在 ({size:.1f}MB)")
            else:
                print(f"❌ {dir_path}: 不存在")
        
        # 检查关键文件
        important_files = [
            "index.html",
            "README.md",
            "requirements.txt"
        ]
        
        for file_path in important_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}: 存在")
            else:
                print(f"⚠️ {file_path}: 不存在")
    
    def _get_dir_size(self, dir_path: str) -> float:
        """获取目录大小(MB)"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
        return total_size / (1024 * 1024)
    
    def _generate_verification_report(self):
        """生成验证报告"""
        print("\n📊 生成验证报告...")
        
        # 统计结果
        total_checks = len(self.verification_results)
        passed_checks = len([r for r in self.verification_results if r["passed"]])
        failed_checks = total_checks - passed_checks
        
        # 按类型分组
        by_type = {}
        for result in self.verification_results:
            result_type = result["type"]
            if result_type not in by_type:
                by_type[result_type] = {"passed": 0, "failed": 0}
            
            if result["passed"]:
                by_type[result_type]["passed"] += 1
            else:
                by_type[result_type]["failed"] += 1
        
        # 生成报告
        report = {
            "timestamp": "2025-07-02 03:45:00",
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "success_rate": f"{(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "0%"
            },
            "by_type": by_type,
            "detailed_results": self.verification_results,
            "recommendations": self._generate_recommendations()
        }
        
        # 保存报告
        report_file = "verification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 显示摘要
        print(f"\n📋 验证摘要:")
        print(f"  总检查项: {total_checks}")
        print(f"  通过: {passed_checks}")
        print(f"  失败: {failed_checks}")
        print(f"  成功率: {report['summary']['success_rate']}")
        
        print(f"\n📊 按类型统计:")
        for result_type, stats in by_type.items():
            print(f"  {result_type}: ✅{stats['passed']} ❌{stats['failed']}")
        
        # 显示失败的检查
        failed_results = [r for r in self.verification_results if not r["passed"]]
        if failed_results:
            print(f"\n❌ 失败的检查:")
            for result in failed_results:
                print(f"  {result['file']}: {result.get('issue', '未知错误')}")
        
        print(f"\n📄 详细报告: {report_file}")
        
        # 总体评估
        if failed_checks == 0:
            print(f"\n🎉 项目配置修复验证完全通过！")
        elif failed_checks <= 2:
            print(f"\n✅ 项目配置修复基本成功，有少量问题需要处理")
        else:
            print(f"\n⚠️ 项目配置修复部分成功，需要进一步处理问题")
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于验证结果生成建议
        failed_results = [r for r in self.verification_results if not r["passed"]]
        
        if any(r["type"] == "frontend_config" for r in failed_results):
            recommendations.append("检查并修复前端配置文件中的API地址")
        
        if any(r["type"] == "strategy_config" for r in failed_results):
            recommendations.append("完善Agent策略配置文件")
        
        if any(r["type"] == "deployment_config" for r in failed_results):
            recommendations.append("创建缺失的部署配置文件")
        
        if any(r["type"] == "cors_config" for r in failed_results):
            recommendations.append("更新后端CORS配置")
        
        # 通用建议
        recommendations.extend([
            "测试前端与后端的连接",
            "验证Cloudflare Pages部署",
            "检查移动端访问",
            "运行完整的功能测试"
        ])
        
        return recommendations

def main():
    """主函数"""
    verifier = ProjectFixVerifier()
    
    print("🔍 项目修复验证工具")
    print("=" * 30)
    print("验证项目配置修复后的状态")
    print()
    
    verifier.run_verification()

if __name__ == "__main__":
    main()
