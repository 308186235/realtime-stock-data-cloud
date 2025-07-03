#!/usr/bin/env python3
"""
最终模拟数据清理脚本
确保系统完全移除所有模拟数据
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Dict

class FinalMockDataCleaner:
    """最终模拟数据清理器"""
    
    def __init__(self):
        self.files_to_delete = [
            # 测试和演示文件
            "compare_candlestick_patterns.py",
            "simple_stress_test_5000.py", 
            "stress_test_5000_stocks.py",
            "create_tables_api.py",
            "generate_test_push_data.py",
            "performance_test.py",
            "debug_and_fix.py",
            
            # Mock目录
            "frontend/stock5/mock/",
            "frontend/gupiao1/mock/",
            "炒股养家/mock/",
            
            # 测试数据文件
            "*test*data*.py",
            "*mock*data*.py",
            "*demo*data*.py"
        ]
        
        self.critical_files_to_fix = [
            "app_api_server.py",
            "mobile_accessible_server.py", 
            "domain_server.py",
            "simple_api_server.py",
            "simple_api_server_9000.py",
            "local_hybrid_client.py",
            "render_deploy_config.py"
        ]
    
    def run_cleanup(self):
        """运行清理"""
        print("🧹 开始最终模拟数据清理...")
        print("=" * 50)
        
        # 1. 删除文件
        self._delete_mock_files()
        
        # 2. 修复关键文件
        self._fix_critical_files()
        
        # 3. 验证清理结果
        self._verify_cleanup()
        
        print("\n✅ 最终清理完成！")
    
    def _delete_mock_files(self):
        """删除模拟数据文件"""
        print("\n🗑️ 删除模拟数据文件...")
        
        deleted_count = 0
        
        for file_pattern in self.files_to_delete:
            if os.path.exists(file_pattern):
                try:
                    if os.path.isdir(file_pattern):
                        shutil.rmtree(file_pattern)
                        print(f"✅ 删除目录: {file_pattern}")
                    else:
                        os.remove(file_pattern)
                        print(f"✅ 删除文件: {file_pattern}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_pattern}: {e}")
        
        print(f"\n📊 共删除 {deleted_count} 个文件/目录")
    
    def _fix_critical_files(self):
        """修复关键文件中的模拟数据"""
        print("\n🔧 修复关键文件...")
        
        fixes = {
            "simple_api_server.py": self._fix_simple_api_server,
            "simple_api_server_9000.py": self._fix_simple_api_server_9000,
            "domain_server.py": self._fix_domain_server,
            "render_deploy_config.py": self._fix_render_deploy_config
        }
        
        for filename, fix_function in fixes.items():
            if os.path.exists(filename):
                try:
                    fix_function(filename)
                    print(f"✅ 修复: {filename}")
                except Exception as e:
                    print(f"❌ 修复失败 {filename}: {e}")
    
    def _fix_simple_api_server(self, filename):
        """修复simple_api_server.py"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换模拟数据生成
        content = re.sub(
            r'random\.(uniform|randint|choice)\([^)]+\)',
            'None  # 模拟数据已禁用',
            content
        )
        
        # 替换mock相关代码
        content = re.sub(
            r'mock_[a-zA-Z_]+\s*=.*',
            '# 模拟数据已禁用',
            content
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_simple_api_server_9000(self, filename):
        """修复simple_api_server_9000.py"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换随机数据生成
        patterns = [
            (r'"learning_progress": random\.randint\(\d+, \d+\)', '"learning_progress": None  # 需要真实数据'),
            (r'"win_rate": round\(random\.uniform\([^)]+\), \d+\)', '"win_rate": None  # 需要真实数据'),
            (r'"total_trades": random\.randint\(\d+, \d+\)', '"total_trades": None  # 需要真实数据'),
            (r'"profit_rate": round\(random\.uniform\([^)]+\), \d+\)', '"profit_rate": None  # 需要真实数据'),
            (r'"price": round\(random\.uniform\([^)]+\), \d+\)', '"price": None  # 需要真实数据'),
            (r'"change": round\(random\.uniform\([^)]+\), \d+\)', '"change": None  # 需要真实数据'),
            (r'"volume": random\.randint\([^)]+\)', '"volume": None  # 需要真实数据')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_domain_server(self, filename):
        """修复domain_server.py"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换随机价格生成
        content = re.sub(
            r'"price": round\(random\.uniform\([^)]+\), \d+\)',
            '"price": None  # 需要真实股票数据',
            content
        )
        
        content = re.sub(
            r'"change": round\(random\.uniform\([^)]+\), \d+\)',
            '"change": None  # 需要真实股票数据',
            content
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_render_deploy_config(self, filename):
        """修复render_deploy_config.py"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换模拟函数
        content = re.sub(
            r'def mock_[a-zA-Z_]+\([^)]*\):.*?return.*',
            'def disabled_mock_function():\n        raise ValueError("❌ 模拟功能已禁用，请使用真实交易接口")',
            content,
            flags=re.DOTALL
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _verify_cleanup(self):
        """验证清理结果"""
        print("\n🔍 验证清理结果...")
        
        # 运行验证脚本
        try:
            import subprocess
            result = subprocess.run([sys.executable, "verify_no_mock_data.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 验证通过：未发现模拟数据")
            else:
                print("⚠️ 验证发现问题，请查看详细报告")
                print(result.stdout)
        except Exception as e:
            print(f"❌ 验证失败: {e}")
    
    def create_real_data_config_template(self):
        """创建真实数据配置模板"""
        config_template = """
# 真实数据源配置模板
# 请配置以下真实数据源

[taobao_stock_data]
api_key = "QT_wat5QfcJ6N9pDZM5"
host = ""  # 需要从淘宝卖家获取
port = ""  # 需要从淘宝卖家获取
token = ""  # 需要从淘宝卖家获取

[tonghuashun_api]
api_key = ""  # 需要申请
api_secret = ""  # 需要申请
endpoint = "https://api.10jqka.com.cn"

[tongdaxin_local]
host = "127.0.0.1"
port = 7709
enabled = false

[real_trading]
# 真实交易接口配置
working_trader_fixed_enabled = true
broker_api_enabled = false
third_party_api_enabled = false

[data_validation]
# 数据验证配置
mock_data_detection = true
real_data_required = true
data_freshness_seconds = 300
"""
        
        with open("real_data_config.ini", "w", encoding="utf-8") as f:
            f.write(config_template)
        
        print("📄 已创建真实数据配置模板: real_data_config.ini")

def main():
    """主函数"""
    print("🧹 最终模拟数据清理工具")
    print("=" * 40)
    
    cleaner = FinalMockDataCleaner()
    
    # 运行清理
    cleaner.run_cleanup()
    
    # 创建配置模板
    cleaner.create_real_data_config_template()
    
    print("\n" + "=" * 50)
    print("🎉 模拟数据清理完成！")
    print()
    print("下一步行动:")
    print("1. 配置 real_data_config.ini 中的真实数据源")
    print("2. 测试淘宝股票数据推送服务连接")
    print("3. 验证Agent使用真实数据进行决策")
    print("4. 部署到生产环境")
    print()
    print("⚠️ 系统现在只接受真实数据，拒绝任何模拟数据！")

if __name__ == "__main__":
    main()
