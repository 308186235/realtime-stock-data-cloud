#!/usr/bin/env python3
"""
验证Cloudflare配置工具
确保所有配置都正确切换到Cloudflare
"""

import os
import re
import json
from pathlib import Path

class CloudflareConfigVerifier:
    """Cloudflare配置验证器"""
    
    def __init__(self):
        self.expected_domains = {
            "api": "api.aigupiao.me",
            "app": "app.aigupiao.me", 
            "mobile": "mobile.aigupiao.me",
            "admin": "admin.aigupiao.me"
        }
        
        self.verification_results = []
    
    def run_verification(self):
        """运行验证"""
        print("🔍 验证Cloudflare配置...")
        print("=" * 50)
        
        # 1. 验证前端配置
        self._verify_frontend_configs()
        
        # 2. 验证API配置
        self._verify_api_configs()
        
        # 3. 验证后端配置
        self._verify_backend_configs()
        
        # 4. 验证Cloudflare文件
        self._verify_cloudflare_files()
        
        # 5. 检查Netlify残留
        self._check_netlify_remnants()
        
        # 6. 生成验证报告
        self._generate_verification_report()
        
        print("\n✅ 配置验证完成！")
    
    def _add_result(self, category: str, item: str, status: bool, message: str):
        """添加验证结果"""
        result = {
            "category": category,
            "item": item,
            "status": status,
            "message": message
        }
        self.verification_results.append(result)
        
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {category} - {item}: {message}")
    
    def _verify_frontend_configs(self):
        """验证前端配置"""
        print("\n🎨 验证前端配置...")
        
        frontend_configs = [
            "炒股养家/env.js",
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js"
        ]
        
        for config_file in frontend_configs:
            if os.path.exists(config_file):
                self._verify_env_file(config_file)
            else:
                self._add_result("前端配置", config_file, False, "文件不存在")
    
    def _verify_env_file(self, file_path):
        """验证环境配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查API地址
            if "api.aigupiao.me" in content:
                self._add_result("前端配置", file_path, True, "API地址正确")
            else:
                self._add_result("前端配置", file_path, False, "API地址不正确")
            
            # 检查WebSocket地址
            if "wss://api.aigupiao.me/ws" in content:
                self._add_result("前端配置", f"{file_path} (WebSocket)", True, "WebSocket地址正确")
            else:
                self._add_result("前端配置", f"{file_path} (WebSocket)", False, "WebSocket地址不正确")
            
            # 检查模拟数据禁用
            if "useMockData: false" in content:
                self._add_result("前端配置", f"{file_path} (Mock Data)", True, "模拟数据已禁用")
            else:
                self._add_result("前端配置", f"{file_path} (Mock Data)", False, "模拟数据未禁用")
            
            # 检查Netlify残留
            netlify_patterns = ['netlify', 'Netlify', 'NTF888888']
            has_netlify = any(pattern in content for pattern in netlify_patterns)
            
            if not has_netlify:
                self._add_result("前端配置", f"{file_path} (Netlify清理)", True, "无Netlify残留")
            else:
                self._add_result("前端配置", f"{file_path} (Netlify清理)", False, "发现Netlify残留")
                
        except Exception as e:
            self._add_result("前端配置", file_path, False, f"读取失败: {e}")
    
    def _verify_api_configs(self):
        """验证API配置"""
        print("\n🔌 验证API配置...")
        
        api_files = [
            "炒股养家/services/config.js",
            "frontend/gupiao1/services/config.js",
            "frontend/stock5/services/config.js"
        ]
        
        for api_file in api_files:
            if os.path.exists(api_file):
                self._verify_api_file(api_file)
            else:
                self._add_result("API配置", api_file, False, "文件不存在")
    
    def _verify_api_file(self, file_path):
        """验证API配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查基础URL
            if "api.aigupiao.me" in content:
                self._add_result("API配置", file_path, True, "基础URL正确")
            else:
                self._add_result("API配置", file_path, False, "基础URL不正确")
                
        except Exception as e:
            self._add_result("API配置", file_path, False, f"读取失败: {e}")
    
    def _verify_backend_configs(self):
        """验证后端配置"""
        print("\n🌐 验证后端配置...")
        
        backend_files = [
            "backend/app.py",
            "cloud_app.py"
        ]
        
        for backend_file in backend_files:
            if os.path.exists(backend_file):
                self._verify_backend_file(backend_file)
            else:
                self._add_result("后端配置", backend_file, False, "文件不存在")
    
    def _verify_backend_file(self, file_path):
        """验证后端配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查CORS配置
            expected_domains = [
                "app.aigupiao.me",
                "mobile.aigupiao.me", 
                "admin.aigupiao.me",
                "api.aigupiao.me"
            ]
            
            cors_correct = all(domain in content for domain in expected_domains)
            
            if cors_correct:
                self._add_result("后端配置", f"{file_path} (CORS)", True, "CORS配置正确")
            else:
                self._add_result("后端配置", f"{file_path} (CORS)", False, "CORS配置不完整")
                
        except Exception as e:
            self._add_result("后端配置", file_path, False, f"读取失败: {e}")
    
    def _verify_cloudflare_files(self):
        """验证Cloudflare文件"""
        print("\n☁️ 验证Cloudflare文件...")
        
        required_files = [
            "wrangler.toml",
            "_redirects",
            "cloudflare-pages-config.md",
            "CLOUDFLARE_DEPLOYMENT_GUIDE.md"
        ]
        
        for file_name in required_files:
            if os.path.exists(file_name):
                self._add_result("Cloudflare文件", file_name, True, "文件存在")
                
                # 验证文件内容
                if file_name == "wrangler.toml":
                    self._verify_wrangler_toml()
                elif file_name == "_redirects":
                    self._verify_redirects_file()
            else:
                self._add_result("Cloudflare文件", file_name, False, "文件不存在")
    
    def _verify_wrangler_toml(self):
        """验证wrangler.toml文件"""
        try:
            with open("wrangler.toml", 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "api.aigupiao.me" in content:
                self._add_result("Cloudflare文件", "wrangler.toml (域名)", True, "域名配置正确")
            else:
                self._add_result("Cloudflare文件", "wrangler.toml (域名)", False, "域名配置错误")
                
        except Exception as e:
            self._add_result("Cloudflare文件", "wrangler.toml", False, f"验证失败: {e}")
    
    def _verify_redirects_file(self):
        """验证_redirects文件"""
        try:
            with open("_redirects", 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "api.aigupiao.me" in content:
                self._add_result("Cloudflare文件", "_redirects (重定向)", True, "重定向配置正确")
            else:
                self._add_result("Cloudflare文件", "_redirects (重定向)", False, "重定向配置错误")
                
        except Exception as e:
            self._add_result("Cloudflare文件", "_redirects", False, f"验证失败: {e}")
    
    def _check_netlify_remnants(self):
        """检查Netlify残留"""
        print("\n🔍 检查Netlify残留...")
        
        # 检查文件和目录
        netlify_items = [
            "netlify.toml",
            "_netlify",
            "netlify-final",
            "netlify-trading",
            "netlify-trading-fixed"
        ]
        
        for item in netlify_items:
            if os.path.exists(item):
                self._add_result("Netlify清理", item, False, "发现Netlify残留")
            else:
                self._add_result("Netlify清理", item, True, "已清理")
        
        # 检查代码中的Netlify引用
        self._scan_for_netlify_references()
    
    def _scan_for_netlify_references(self):
        """扫描代码中的Netlify引用"""
        netlify_patterns = [
            r'netlify',
            r'\.netlify\.app',
            r'Netlify交易账户',
            r'NTF888888'
        ]
        
        scan_dirs = ["炒股养家", "frontend", "backend"]
        
        for scan_dir in scan_dirs:
            if os.path.exists(scan_dir):
                netlify_found = False
                
                for root, dirs, files in os.walk(scan_dir):
                    for file in files:
                        if file.endswith(('.js', '.vue', '.py', '.json')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                for pattern in netlify_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        netlify_found = True
                                        break
                                
                                if netlify_found:
                                    break
                            except:
                                continue
                    
                    if netlify_found:
                        break
                
                if netlify_found:
                    self._add_result("代码扫描", scan_dir, False, "发现Netlify引用")
                else:
                    self._add_result("代码扫描", scan_dir, True, "无Netlify引用")
    
    def _generate_verification_report(self):
        """生成验证报告"""
        print("\n📋 生成验证报告...")
        
        total_checks = len(self.verification_results)
        passed_checks = len([r for r in self.verification_results if r["status"]])
        failed_checks = total_checks - passed_checks
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            "timestamp": "2025-07-02T05:00:00",
            "verification_type": "Cloudflare配置验证",
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "success_rate": f"{success_rate:.1f}%"
            },
            "expected_domains": self.expected_domains,
            "verification_results": self.verification_results,
            "recommendations": self._generate_recommendations()
        }
        
        with open("cloudflare_verification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 显示摘要
        print(f"\n📊 验证摘要:")
        print(f"  总检查项: {total_checks}")
        print(f"  通过: {passed_checks}")
        print(f"  失败: {failed_checks}")
        print(f"  成功率: {success_rate:.1f}%")
        
        # 显示失败的检查
        failed_results = [r for r in self.verification_results if not r["status"]]
        if failed_results:
            print(f"\n❌ 失败的检查:")
            for result in failed_results:
                print(f"  {result['category']} - {result['item']}: {result['message']}")
        
        print(f"\n📄 详细报告: cloudflare_verification_report.json")
        
        # 总体评估
        if failed_checks == 0:
            print(f"\n🎉 所有检查通过！Cloudflare配置完全正确！")
        elif success_rate >= 90:
            print(f"\n✅ 大部分检查通过，配置基本正确")
        else:
            print(f"\n⚠️ 多项检查失败，需要修复配置")
    
    def _generate_recommendations(self):
        """生成建议"""
        recommendations = []
        
        failed_results = [r for r in self.verification_results if not r["status"]]
        
        if not failed_results:
            recommendations.extend([
                "Cloudflare配置完全正确",
                "可以开始部署到Cloudflare",
                "建议测试所有域名访问"
            ])
        else:
            for result in failed_results:
                category = result["category"]
                
                if "前端配置" in category:
                    recommendations.append("检查前端环境配置文件")
                elif "API配置" in category:
                    recommendations.append("检查API服务配置文件")
                elif "后端配置" in category:
                    recommendations.append("检查后端CORS配置")
                elif "Cloudflare文件" in category:
                    recommendations.append("检查Cloudflare部署文件")
                elif "Netlify" in category:
                    recommendations.append("清理剩余的Netlify配置")
        
        return list(set(recommendations))

def main():
    """主函数"""
    print("🔍 Cloudflare配置验证工具")
    print("=" * 40)
    
    verifier = CloudflareConfigVerifier()
    verifier.run_verification()

if __name__ == "__main__":
    main()
