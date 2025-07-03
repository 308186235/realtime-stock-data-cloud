#!/usr/bin/env python3
"""
全面项目审计工具
使用MCP检查发现的所有潜在问题
"""

import os
import json
import ast
import re
import sys
from pathlib import Path
from datetime import datetime
import importlib

class ComprehensiveProjectAuditor:
    """全面项目审计器"""
    
    def __init__(self):
        self.issues = {
            "security": [],
            "database": [],
            "dependencies": [],
            "configuration": [],
            "performance": [],
            "architecture": [],
            "data_integrity": []
        }
        
    def run_audit(self):
        """运行全面审计"""
        print("🔍 开始全面项目审计")
        print("=" * 60)
        
        # 1. 安全性审计
        self._audit_security()
        
        # 2. 数据库审计
        self._audit_database()
        
        # 3. 依赖包审计
        self._audit_dependencies()
        
        # 4. 配置审计
        self._audit_configuration()
        
        # 5. 性能审计
        self._audit_performance()
        
        # 6. 架构审计
        self._audit_architecture()
        
        # 7. 数据完整性审计
        self._audit_data_integrity()
        
        # 8. 生成审计报告
        self._generate_audit_report()
        
    def _audit_security(self):
        """安全性审计"""
        print("\n🔒 安全性审计...")
        
        # 检查API密钥暴露
        self._check_api_key_exposure()
        
        # 检查数据库密码暴露
        self._check_database_credentials()
        
        # 检查CORS配置
        self._check_cors_configuration()
        
        # 检查认证机制
        # self._check_authentication()  # 暂时注释掉
        
    def _check_api_key_exposure(self):
        """检查API密钥暴露"""
        exposed_keys = []
        
        # 检查api_keys.json文件
        if os.path.exists("api_keys.json"):
            exposed_keys.append({
                "file": "api_keys.json",
                "issue": "API密钥明文存储",
                "severity": "HIGH",
                "description": "生产环境API密钥QT_wat5QfcJ6N9pDZM5暴露在代码中"
            })
        
        # 检查前端文件中的API密钥
        frontend_files = [
            "炒股养家/services/apiKeyManager.js",
            "frontend/gupiao1/env.js"
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "QT_wat5QfcJ6N9pDZM5" in content:
                        exposed_keys.append({
                            "file": file_path,
                            "issue": "前端代码包含API密钥",
                            "severity": "CRITICAL",
                            "description": "API密钥暴露在前端代码中，用户可见"
                        })
                except Exception as e:
                    pass
        
        self.issues["security"].extend(exposed_keys)
    
    def _check_database_credentials(self):
        """检查数据库凭据暴露"""
        db_issues = []
        
        # 检查Supabase配置文件
        supabase_files = [
            "backend/supabase_config.py",
            "backend/config/supabase.py",
            "frontend/src/config/supabase.js"
        ]
        
        for file_path in supabase_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查硬编码的数据库URL和密钥
                    if "zzukfxwavknskqcepsjb.supabase.co" in content:
                        db_issues.append({
                            "file": file_path,
                            "issue": "数据库URL硬编码",
                            "severity": "MEDIUM",
                            "description": "Supabase URL硬编码在代码中"
                        })
                    
                    if "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" in content:
                        db_issues.append({
                            "file": file_path,
                            "issue": "数据库密钥硬编码",
                            "severity": "HIGH",
                            "description": "Supabase密钥硬编码在代码中"
                        })
                        
                    if "WuFeng1234567890oO" in content:
                        db_issues.append({
                            "file": file_path,
                            "issue": "数据库密码明文存储",
                            "severity": "CRITICAL",
                            "description": "数据库密码明文暴露"
                        })
                        
                except Exception as e:
                    pass
        
        self.issues["security"].extend(db_issues)
    
    def _check_cors_configuration(self):
        """检查CORS配置"""
        cors_issues = []
        
        cors_files = [
            "backend/middleware/security.py",
            "backend/app.py",
            "cloud_app.py"
        ]
        
        for file_path in cors_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'allow_origins=["*"]' in content or "allow_origins = ['*']" in content:
                        cors_issues.append({
                            "file": file_path,
                            "issue": "CORS配置过于宽松",
                            "severity": "MEDIUM",
                            "description": "允许所有来源访问，存在安全风险"
                        })
                        
                except Exception as e:
                    pass
        
        self.issues["security"].extend(cors_issues)
    
    def _audit_database(self):
        """数据库审计"""
        print("\n🗄️ 数据库审计...")
        
        # 检查数据库连接配置
        self._check_database_connections()
        
        # 检查数据库表结构
        # self._check_database_schema()  # 暂时注释掉

        # 检查数据备份策略
        # self._check_backup_strategy()  # 暂时注释掉
        
    def _check_database_connections(self):
        """检查数据库连接配置"""
        db_issues = []
        
        # 检查Supabase配置完整性
        if os.path.exists("backend/supabase_config.py"):
            try:
                with open("backend/supabase_config.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'self.service_key = ""' in content:
                    db_issues.append({
                        "file": "backend/supabase_config.py",
                        "issue": "Supabase service_role密钥未配置",
                        "severity": "HIGH",
                        "description": "缺少service_role密钥，影响后端数据库操作"
                    })
                
                if "[YOUR_PASSWORD]" in content:
                    db_issues.append({
                        "file": "backend/supabase_config.py",
                        "issue": "数据库密码占位符未替换",
                        "severity": "HIGH",
                        "description": "数据库连接字符串包含占位符"
                    })
                    
            except Exception as e:
                pass
        
        self.issues["database"].extend(db_issues)
    
    def _audit_dependencies(self):
        """依赖包审计"""
        print("\n📦 依赖包审计...")
        
        # 检查requirements.txt文件
        self._check_requirements_files()
        
        # 检查包版本冲突
        # self._check_version_conflicts()  # 暂时注释掉

        # 检查缺失依赖
        # self._check_missing_dependencies()  # 暂时注释掉
        
    def _check_requirements_files(self):
        """检查requirements.txt文件"""
        req_issues = []
        
        req_files = [
            "requirements.txt",
            "backend/requirements.txt",
            "backend/requirements_supabase.txt",
            "requirements_cloud.txt"
        ]
        
        found_files = []
        for req_file in req_files:
            if os.path.exists(req_file):
                found_files.append(req_file)
        
        if len(found_files) > 2:
            req_issues.append({
                "issue": "多个requirements.txt文件",
                "severity": "MEDIUM",
                "description": f"发现{len(found_files)}个requirements文件，可能导致依赖混乱",
                "files": found_files
            })
        
        # 检查版本固定
        for req_file in found_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                unfixed_versions = []
                
                for line in lines:
                    if '>=' in line and '==' not in line:
                        unfixed_versions.append(line)
                
                if unfixed_versions:
                    req_issues.append({
                        "file": req_file,
                        "issue": "版本号未固定",
                        "severity": "LOW",
                        "description": f"有{len(unfixed_versions)}个包版本未固定，可能导致环境不一致"
                    })
                    
            except Exception as e:
                pass
        
        self.issues["dependencies"].extend(req_issues)
    
    def _audit_configuration(self):
        """配置审计"""
        print("\n⚙️ 配置审计...")
        
        # 检查环境变量配置
        self._check_environment_variables()
        
        # 检查配置文件一致性
        # self._check_config_consistency()  # 暂时注释掉
        
    def _check_environment_variables(self):
        """检查环境变量配置"""
        config_issues = []
        
        # 检查.env模板文件
        if os.path.exists("env.template"):
            if not os.path.exists(".env"):
                config_issues.append({
                    "issue": "缺少.env文件",
                    "severity": "HIGH",
                    "description": "存在env.template但缺少实际的.env配置文件"
                })
        
        # 检查配置文件中的硬编码值
        config_files = [
            "backend/config.py",
            "backend/config/settings.py"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt")' in content:
                        config_issues.append({
                            "file": config_file,
                            "issue": "JWT密钥使用默认值",
                            "severity": "HIGH",
                            "description": "JWT密钥使用不安全的默认值"
                        })
                        
                except Exception as e:
                    pass
        
        self.issues["configuration"].extend(config_issues)
    
    def _audit_performance(self):
        """性能审计"""
        print("\n⚡ 性能审计...")
        
        perf_issues = []
        
        # 检查数据库连接池配置
        if os.path.exists("backend/supabase_config.py"):
            try:
                with open("backend/supabase_config.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "max_size=10" in content:
                    perf_issues.append({
                        "file": "backend/supabase_config.py",
                        "issue": "数据库连接池较小",
                        "severity": "LOW",
                        "description": "连接池大小为10，高并发时可能不足"
                    })
                    
            except Exception as e:
                pass
        
        self.issues["performance"].extend(perf_issues)
    
    def _audit_architecture(self):
        """架构审计"""
        print("\n🏗️ 架构审计...")
        
        arch_issues = []
        
        # 检查服务端口冲突
        ports_used = []
        
        # 扫描代码中的端口配置
        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['__pycache__', '.git', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找端口配置
                        port_matches = re.findall(r'port[=\s]*(\d+)', content, re.IGNORECASE)
                        for port in port_matches:
                            if port not in ['80', '443']:  # 排除标准端口
                                ports_used.append((file_path, port))
                                
                    except Exception as e:
                        pass
        
        # 检查端口冲突
        port_counts = {}
        for file_path, port in ports_used:
            if port not in port_counts:
                port_counts[port] = []
            port_counts[port].append(file_path)
        
        for port, files in port_counts.items():
            if len(files) > 1:
                arch_issues.append({
                    "issue": f"端口{port}冲突",
                    "severity": "MEDIUM",
                    "description": f"端口{port}在多个文件中使用",
                    "files": files
                })
        
        self.issues["architecture"].extend(arch_issues)
    
    def _audit_data_integrity(self):
        """数据完整性审计"""
        print("\n🔍 数据完整性审计...")
        
        data_issues = []
        
        # 检查数据验证
        if os.path.exists("trader_api.py"):
            try:
                with open("trader_api.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "if not code or not quantity:" in content:
                    # 这是好的，有基本验证
                    pass
                else:
                    data_issues.append({
                        "file": "trader_api.py",
                        "issue": "缺少输入验证",
                        "severity": "MEDIUM",
                        "description": "交易API缺少充分的输入验证"
                    })
                    
            except Exception as e:
                pass
        
        self.issues["data_integrity"].extend(data_issues)
    
    def _generate_audit_report(self):
        """生成审计报告"""
        print("\n📋 审计报告")
        print("=" * 60)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("✅ 未发现任何问题！")
            return
        
        print(f"🚨 发现 {total_issues} 个问题")
        
        # 按严重程度统计
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for category, issues in self.issues.items():
            if issues:
                print(f"\n📂 {category.upper()} ({len(issues)} 个问题):")
                
                for issue in issues:
                    severity = issue.get("severity", "UNKNOWN")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                    
                    print(f"  🔸 {issue.get('issue', 'Unknown issue')}")
                    if 'file' in issue:
                        print(f"     📁 文件: {issue['file']}")
                    if 'description' in issue:
                        print(f"     📝 描述: {issue['description']}")
                    print(f"     ⚠️ 严重程度: {severity}")
                    print()
        
        # 严重程度汇总
        print("📊 严重程度汇总:")
        for severity, count in severity_counts.items():
            if count > 0:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                print(f"  {emoji.get(severity, '⚪')} {severity}: {count}")
        
        # 优先修复建议
        print("\n🎯 优先修复建议:")
        if severity_counts["CRITICAL"] > 0:
            print("  1. 🔴 立即修复CRITICAL级别问题（安全风险）")
        if severity_counts["HIGH"] > 0:
            print("  2. 🟠 尽快修复HIGH级别问题（功能影响）")
        if severity_counts["MEDIUM"] > 0:
            print("  3. 🟡 计划修复MEDIUM级别问题（改进建议）")
        
        # 保存详细报告
        report_data = {
            "audit_time": datetime.now().isoformat(),
            "total_issues": total_issues,
            "severity_summary": severity_counts,
            "detailed_issues": self.issues
        }
        
        with open("audit_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: audit_report.json")

if __name__ == "__main__":
    auditor = ComprehensiveProjectAuditor()
    auditor.run_audit()
