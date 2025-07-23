#!/usr/bin/env python3
"""
项目配置修复工具
自动修复Agent策略、前端配置和部署配置的不一致问题
"""

import os
import json
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any

class ProjectConfigurationFixer:
    """项目配置修复器"""
    
    def __init__(self):
        self.root_dir = Path(".")
        self.backup_dir = Path(f"config_backup_{int(time.time())}")
        self.issues_found = []
        self.fixes_applied = []
        
        # 统一配置
        self.unified_config = {
            "api_base_url": "https://api.aigupiao.me",
            "ws_url": "wss://api.aigupiao.me/ws",
            "main_domain": "aigupiao.me",
            "app_domain": "app.aigupiao.me"
        }
        
    def run_comprehensive_fix(self):
        """运行综合修复"""
        print("🔧 开始项目配置综合修复...")
        print("=" * 50)
        
        try:
            # 1. 创建备份
            self._create_backup()
            
            # 2. 修复前端配置
            self._fix_frontend_configurations()
            
            # 3. 修复Agent策略配置
            self._fix_agent_configurations()
            
            # 4. 修复部署配置
            self._fix_deployment_configurations()
            
            # 5. 清理重复文件
            self._cleanup_duplicate_files()
            
            # 6. 生成修复报告
            self._generate_fix_report()
            
            print("\n🎉 项目配置修复完成！")
            
        except Exception as e:
            print(f"\n❌ 修复过程出错: {e}")
            self._restore_backup()
    
    def _create_backup(self):
        """创建配置备份"""
        print("📄 创建配置文件备份...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # 备份关键配置文件
        config_files = [
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js", 
            "炒股养家/env.js",
            "frontend/gupiao1/services/config.js",
            "炒股养家/services/config.js",
            "backend/app.py",
            "cloud_app.py"
        ]
        
        for file_path in config_files:
            if os.path.exists(file_path):
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                print(f"✅ 备份: {file_path}")
        
        print(f"📁 备份目录: {self.backup_dir}")
    
    def _fix_frontend_configurations(self):
        """修复前端配置"""
        print("\n🎨 修复前端配置...")
        
        # 前端配置文件列表
        frontend_configs = [
            {
                "path": "frontend/gupiao1/env.js",
                "name": "股票1前端"
            },
            {
                "path": "frontend/stock5/env.js", 
                "name": "股票5前端"
            },
            {
                "path": "炒股养家/env.js",
                "name": "炒股养家前端"
            }
        ]
        
        for config in frontend_configs:
            self._fix_single_frontend_config(config["path"], config["name"])
        
        # 修复服务配置文件
        service_configs = [
            "frontend/gupiao1/services/config.js",
            "炒股养家/services/config.js"
        ]
        
        for config_path in service_configs:
            self._fix_service_config(config_path)
    
    def _fix_single_frontend_config(self, file_path: str, name: str):
        """修复单个前端配置文件"""
        if not os.path.exists(file_path):
            print(f"⚠️ 文件不存在: {file_path}")
            return
        
        print(f"🔧 修复 {name}: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 记录原始配置
            original_dev_api = self._extract_api_url(content, 'DEV')
            original_prod_api = self._extract_api_url(content, 'PROD')
            
            if original_dev_api != self.unified_config["api_base_url"] or \
               original_prod_api != self.unified_config["api_base_url"]:
                
                self.issues_found.append({
                    "file": file_path,
                    "issue": f"API地址不统一",
                    "original_dev": original_dev_api,
                    "original_prod": original_prod_api
                })
            
            # 替换开发环境API地址
            content = re.sub(
                r"(// 开发环境[\s\S]*?apiBaseUrl:\s*['\"])([^'\"]*)",
                f"\\1{self.unified_config['api_base_url']}",
                content
            )
            
            # 替换生产环境API地址
            content = re.sub(
                r"(// 生产环境[\s\S]*?apiBaseUrl:\s*['\"])([^'\"]*)",
                f"\\1{self.unified_config['api_base_url']}",
                content
            )
            
            # 替换WebSocket地址
            content = re.sub(
                r"(wsUrl:\s*['\"])([^'\"]*)",
                f"\\1{self.unified_config['ws_url']}",
                content
            )
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixes_applied.append({
                "file": file_path,
                "action": "统一API地址配置",
                "new_api": self.unified_config["api_base_url"]
            })
            
            print(f"✅ {name} 配置已修复")
            
        except Exception as e:
            print(f"❌ 修复 {name} 失败: {e}")
    
    def _extract_api_url(self, content: str, env_type: str) -> str:
        """提取API URL"""
        pattern = f"// {env_type.lower()}环境[\\s\\S]*?apiBaseUrl:\\s*['\"]([^'\"]*)"
        match = re.search(pattern, content)
        return match.group(1) if match else "未找到"
    
    def _fix_service_config(self, file_path: str):
        """修复服务配置文件"""
        if not os.path.exists(file_path):
            return
        
        print(f"🔧 修复服务配置: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一API基础URL配置
            new_content = f'''/**
 * 服务配置文件 - 统一配置
 */

// API基础URL,根据环境设置
const baseUrl = process.env.NODE_ENV === 'development'
  ? '{self.unified_config["api_base_url"]}'  // 开发环境
  : '{self.unified_config["api_base_url"]}';  // 生产环境

// 超时设置(毫秒)
const timeout = 30000;

// 重试次数
const retryCount = 3;

// 导出配置
export {{
  baseUrl,
  timeout,
  retryCount
}};'''
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixes_applied.append({
                "file": file_path,
                "action": "重写服务配置",
                "new_config": "统一API地址"
            })
            
            print(f"✅ 服务配置已修复")
            
        except Exception as e:
            print(f"❌ 修复服务配置失败: {e}")
    
    def _fix_agent_configurations(self):
        """修复Agent配置"""
        print("\n🤖 修复Agent配置...")
        
        # 检查Agent策略文件
        agent_files = [
            "auto_cleanup_trading_agent.py",
            "backend/ai/agent_system.py",
            "backend/services/auto_trader_service.py"
        ]
        
        strategy_issues = []
        
        for file_path in agent_files:
            if os.path.exists(file_path):
                issues = self._analyze_agent_file(file_path)
                strategy_issues.extend(issues)
        
        if strategy_issues:
            self.issues_found.extend(strategy_issues)
            print(f"⚠️ 发现 {len(strategy_issues)} 个Agent策略问题")
            
            # 创建统一策略配置
            self._create_unified_strategy_config()
        else:
            print("✅ Agent配置检查通过")
    
    def _analyze_agent_file(self, file_path: str) -> List[Dict]:
        """分析Agent文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查策略参数硬编码
            if "profit_pct > 10" in content:
                issues.append({
                    "file": file_path,
                    "issue": "止盈参数硬编码",
                    "suggestion": "使用配置文件管理策略参数"
                })
            
            # 检查风险控制
            if "stop_loss" not in content.lower():
                issues.append({
                    "file": file_path,
                    "issue": "缺少止损机制",
                    "suggestion": "添加统一的风险控制"
                })
            
        except Exception as e:
            issues.append({
                "file": file_path,
                "issue": f"文件分析失败: {e}",
                "suggestion": "检查文件格式和编码"
            })
        
        return issues
    
    def _create_unified_strategy_config(self):
        """创建统一策略配置"""
        print("📋 创建统一策略配置...")
        
        strategy_config = {
            "risk_management": {
                "max_position_size": 0.1,
                "max_daily_loss": 0.02,
                "stop_loss_pct": 0.08,
                "take_profit_pct": 0.10
            },
            "trading_rules": {
                "min_volume": 1000000,
                "max_price": 100,
                "trading_hours": {
                    "start": "09:30",
                    "end": "15:00"
                }
            },
            "strategies": {
                "momentum": {
                    "enabled": True,
                    "buy_threshold": -0.05,
                    "sell_threshold": 0.10
                },
                "mean_reversion": {
                    "enabled": True,
                    "oversold_rsi": 30,
                    "overbought_rsi": 70
                }
            }
        }
        
        config_path = "config/trading_strategy.json"
        os.makedirs("config", exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(strategy_config, f, ensure_ascii=False, indent=2)
        
        self.fixes_applied.append({
            "file": config_path,
            "action": "创建统一策略配置",
            "description": "集中管理所有交易策略参数"
        })
        
        print(f"✅ 统一策略配置已创建: {config_path}")
    
    def _fix_deployment_configurations(self):
        """修复部署配置"""
        print("\n🚀 修复部署配置...")
        
        # 修复Cloudflare Pages配置
        self._create_cloudflare_config()
        
        # 修复后端CORS配置
        self._fix_backend_cors()
        
        # 创建部署脚本
        self._create_deployment_script()
    
    def _create_cloudflare_config(self):
        """创建Cloudflare配置"""
        print("☁️ 创建Cloudflare Pages配置...")
        
        # 创建_redirects文件
        redirects_content = """# Cloudflare Pages重定向规则
/api/* https://api.aigupiao.me/api/:splat 200
/* /index.html 200
"""
        
        with open("_redirects", 'w', encoding='utf-8') as f:
            f.write(redirects_content)
        
        # 创建wrangler.toml
        wrangler_config = """name = "aigupiao-frontend"
compatibility_date = "2023-12-01"

[env.production]
route = "app.aigupiao.me/*"

[env.development]
route = "dev.aigupiao.me/*"
"""
        
        with open("wrangler.toml", 'w', encoding='utf-8') as f:
            f.write(wrangler_config)
        
        self.fixes_applied.append({
            "file": "_redirects, wrangler.toml",
            "action": "创建Cloudflare配置",
            "description": "配置域名路由和重定向"
        })
        
        print("✅ Cloudflare配置已创建")
    
    def _fix_backend_cors(self):
        """修复后端CORS配置"""
        print("🔒 修复后端CORS配置...")
        
        cors_files = ["backend/app.py", "cloud_app.py"]
        
        for file_path in cors_files:
            if os.path.exists(file_path):
                self._update_cors_config(file_path)
    
    def _update_cors_config(self, file_path: str):
        """更新CORS配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一CORS配置
            new_cors_config = '''# 统一CORS配置
origins = [
    "http://localhost:8080",     # 开发服务器
    "http://localhost:3000",     # 备用开发服务器
    "https://app.aigupiao.me",   # 主应用域名
    "https://aigupiao.me",       # 主域名
    "https://mobile.aigupiao.me", # 移动端域名
    "capacitor://localhost",     # 移动应用
    "ionic://localhost"
]'''
            
            # 替换现有CORS配置
            pattern = r'origins\s*=\s*\[[\s\S]*?\]'
            if re.search(pattern, content):
                content = re.sub(pattern, new_cors_config.split('# 统一CORS配置\n')[1], content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied.append({
                    "file": file_path,
                    "action": "更新CORS配置",
                    "description": "统一跨域访问配置"
                })
                
                print(f"✅ {file_path} CORS配置已更新")
            
        except Exception as e:
            print(f"❌ 更新CORS配置失败: {e}")
    
    def _cleanup_duplicate_files(self):
        """清理重复文件"""
        print("\n🧹 清理重复文件...")
        
        # 检查重复的前端目录
        frontend_dirs = ["frontend/gupiao1", "frontend/stock5", "炒股养家"]
        
        print("📁 检测到的前端目录:")
        for dir_path in frontend_dirs:
            if os.path.exists(dir_path):
                size = self._get_dir_size(dir_path)
                print(f"  {dir_path} - {size:.1f}MB")
        
        # 建议保留主要目录
        print("\n💡 建议:")
        print("  保留: 炒股养家 (主要前端)")
        print("  保留: frontend/gupiao1 (备用前端)")
        print("  考虑删除: frontend/stock5 (如果功能重复)")
    
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
    
    def _create_deployment_script(self):
        """创建部署脚本"""
        print("📜 创建部署脚本...")
        
        deploy_script = '''#!/bin/bash
# 项目自动部署脚本

echo "🚀 开始部署AI股票交易系统..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 提交当前更改..."
    git add .
    git commit -m "配置修复部署: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

echo "✅ 部署完成！"
echo "🌐 访问地址: https://app.aigupiao.me"
'''
        
        with open("deploy.sh", 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        # 设置执行权限
        try:
            os.chmod("deploy.sh", 0o755)
        except:
            pass
        
        print("✅ 部署脚本已创建: deploy.sh")
    
    def _generate_fix_report(self):
        """生成修复报告"""
        print("\n📊 生成修复报告...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "issues_found": len(self.issues_found),
                "fixes_applied": len(self.fixes_applied),
                "backup_location": str(self.backup_dir)
            },
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "unified_config": self.unified_config,
            "next_steps": [
                "测试前端API连接",
                "验证Agent策略配置",
                "部署到Cloudflare Pages",
                "检查移动端访问"
            ]
        }
        
        report_file = f"fix_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 显示摘要
        print(f"\n📋 修复摘要:")
        print(f"  发现问题: {len(self.issues_found)} 个")
        print(f"  应用修复: {len(self.fixes_applied)} 个")
        print(f"  备份位置: {self.backup_dir}")
        print(f"  详细报告: {report_file}")
        
        # 显示关键修复
        print(f"\n🔧 关键修复:")
        for fix in self.fixes_applied[:5]:  # 显示前5个
            print(f"  ✅ {fix['action']}: {fix['file']}")
    
    def _restore_backup(self):
        """恢复备份"""
        print(f"\n🔄 从备份恢复配置...")
        try:
            if self.backup_dir.exists():
                for backup_file in self.backup_dir.rglob("*"):
                    if backup_file.is_file():
                        original_path = backup_file.relative_to(self.backup_dir)
                        shutil.copy2(backup_file, original_path)
                print(f"✅ 配置已从 {self.backup_dir} 恢复")
            else:
                print("❌ 备份目录不存在")
        except Exception as e:
            print(f"❌ 恢复备份失败: {e}")

def main():
    """主函数"""
    fixer = ProjectConfigurationFixer()
    
    print("🎯 项目配置修复工具")
    print("=" * 30)
    print("此工具将修复:")
    print("1. 前端API地址配置不一致")
    print("2. Agent策略配置分散")
    print("3. 部署配置不完整")
    print("4. 重复文件清理")
    print()
    
    confirm = input("是否开始修复？(y/N): ")
    if confirm.lower() == 'y':
        fixer.run_comprehensive_fix()
    else:
        print("❌ 用户取消操作")

if __name__ == "__main__":
    main()
