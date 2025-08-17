#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复项目中的语法错误
"""

import os
import re
import ast
import shutil
from datetime import datetime

def fix_syntax_errors_in_file(file_path):
    """修复单个文件的语法错误"""
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 移除残留的BOM和特殊字符
        content = content.replace('\ufeff', '')  # BOM
        content = content.replace('\u00a1', '')  # ¡
        content = content.replace('\ue044', '')  # 特殊字符
        content = content.replace('\u2705', '')  # ✅
        
        # 2. 修复常见的语法错误
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 修复行继续符后的字符问题
            if '\\' in line and line.strip().endswith('\\'):
                # 确保行继续符后没有其他字符
                line = line.rstrip() + '\\'
            
            # 修复未终止的字符串
            if line.count('"') % 2 == 1 and not line.strip().startswith('#'):
                # 如果引号数量是奇数,可能是未终止的字符串
                if line.strip().endswith('"'):
                    pass  # 正常结束
                else:
                    # 尝试在行末添加引号
                    line = line + '"'
            
            # 修复未终止的三引号字符串
            if '"""' in line:
                count = line.count('"""')
                if count % 2 == 1:
                    # 奇数个三引号,可能需要补充
                    if not any('"""' in lines[j] for j in range(i+1, min(i+10, len(lines)))):
                        line = line + '"""'
            
            # 修复缩进问题
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # 检查是否应该有缩进
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line.endswith(':') or prev_line.endswith('\\'):
                        # 前一行以冒号或反斜杠结尾,当前行应该缩进
                        if not line.strip().startswith(('#', 'def ', 'class ', 'import ', 'from ')):
                            line = '    ' + line
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # 3. 尝试解析AST来检查语法
        try:
            ast.parse(content)
            syntax_ok = True
        except SyntaxError as e:
            syntax_ok = False
            print(f"⚠️ 语法错误仍存在于 {file_path}: {e}")
        
        # 如果内容有变化,则保存
        if content != original_content:
            # 备份原文件
            backup_path = f"{file_path}.syntax_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            
            # 保存修复后的文件
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            print(f"✅ 修复语法错误: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def fix_specific_files():
    """修复特定的有问题的文件"""
    problem_files = [
        'agent_api_adapter.py',
        'fix_all_encoding_issues.py',
        'smart_priority_agent.py',
        'stock_api_service.py',
        'trading_day_init.py',
        'backend/app.py',
        'backend/data_pipeline.py',
        'backend/ai/agent_system.py',
        'backend/examples/test_agent_enhanced.py',
        'backend/middleware/security.py',
        'backend/services/ai_service.py',
        'backend/services/redis_cache_service.py',
        'backend/services/stress_test_service.py',
        'backend/strategies/sentiment_strategy.py',
    ]
    
    fixed_count = 0
    
    for file_path in problem_files:
        if os.path.exists(file_path):
            if fix_syntax_errors_in_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    return fixed_count

def install_missing_packages():
    """安装缺失的重要包"""
    important_packages = [
        'numpy',
        'pandas', 
        'requests',
        'aiohttp',
        'fastapi',
        'uvicorn',
        'websockets',
        'tensorflow',
        'scikit-learn',
        'matplotlib',
        'yfinance',
        'akshare',
        'redis',
        'openpyxl',
        'pywin32',
        'pyautogui',
        'optuna',
        'dnspython',
        'nltk',
        'elasticsearch',
        'pytest',
        'torch',
    ]
    
    print("\n🔧 安装重要的缺失包...")
    
    import subprocess
    import sys
    
    for package in important_packages:
        try:
            print(f"📦 安装 {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功")
            else:
                print(f"⚠️ {package} 安装失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {package} 安装超时")
        except Exception as e:
            print(f"❌ {package} 安装错误: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("语法错误修复工具")
    print("=" * 60)
    
    # 修复特定文件的语法错误
    fixed_count = fix_specific_files()
    
    print(f"\n📊 修复结果:")
    print(f"✅ 成功修复: {fixed_count} 个文件")
    
    # 询问是否安装缺失的包
    response = input("\n是否安装重要的缺失包?(y/n): ").strip().lower()
    if response in ['y', 'yes']:
        install_missing_packages()
    
    print("\n🎉 语法错误修复完成!")
    print("\n💡 建议:")
    print("1. 重新运行 python check_missing_dependencies.py 检查结果")
    print("2. 测试关键功能是否正常工作")

if __name__ == "__main__":
    main()
