#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查项目中缺失的依赖和导入错误
"""

import os
import ast
import importlib
import sys
from pathlib import Path

def check_imports_in_file(file_path):
    """检查单个文件的导入问题"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 解析AST
        tree = ast.parse(content)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # 检查每个导入
        missing_imports = []
        for imp in imports:
            try:
                # 尝试导入
                if '.' in imp:
                    # 处理子模块
                    main_module = imp.split('.')[0]
                    importlib.import_module(main_module)
                else:
                    importlib.import_module(imp)
            except ImportError:
                missing_imports.append(imp)
            except Exception:
                # 其他错误,可能是语法问题
                pass
        
        return missing_imports
        
    except SyntaxError as e:
        return [f"SYNTAX_ERROR: {str(e)}"]
    except Exception as e:
        return [f"ERROR: {str(e)}"]

def scan_project_dependencies():
    """扫描整个项目的依赖问题"""
    print("🔍 扫描项目依赖问题...")
    
    # 需要检查的文件扩展名
    extensions = ['.py']
    
    # 需要跳过的目录
    skip_dirs = {
        '__pycache__', '.git', 'node_modules', '.vscode', 
        'backup_deleted_20250624_224708', 'logs', 'models', 'venv'
    }
    
    issues = {}
    
    # 遍历项目目录
    for root, dirs, files in os.walk('.'):
        # 跳过指定目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                
                missing = check_imports_in_file(file_path)
                if missing:
                    issues[file_path] = missing
    
    return issues

def generate_requirements():
    """生成缺失依赖的安装命令"""
    common_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas', 
        'requests': 'requests',
        'aiohttp': 'aiohttp',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'websockets': 'websockets',
        'tensorflow': 'tensorflow',
        'sklearn': 'scikit-learn',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'yfinance': 'yfinance',
        'akshare': 'akshare',
        'tushare': 'tushare',
        'redis': 'redis',
        'pymongo': 'pymongo',
        'sqlalchemy': 'sqlalchemy',
        'psycopg2': 'psycopg2-binary',
        'openpyxl': 'openpyxl',
        'xlrd': 'xlrd',
        'win32gui': 'pywin32',
        'win32api': 'pywin32',
        'win32con': 'pywin32',
        'pyautogui': 'pyautogui',
        'optuna': 'optuna',
        'dnspython': 'dnspython',
        'schedule': 'schedule',
        'apscheduler': 'APScheduler',
        'celery': 'celery',
        'flask': 'flask',
        'django': 'django',
        'streamlit': 'streamlit',
        'dash': 'dash',
        'bokeh': 'bokeh',
        'jupyter': 'jupyter',
        'notebook': 'notebook',
        'ipython': 'ipython',
        'pytest': 'pytest',
        'unittest2': 'unittest2',
        'mock': 'mock',
        'coverage': 'coverage',
        'black': 'black',
        'flake8': 'flake8',
        'mypy': 'mypy',
        'pydantic': 'pydantic',
        'typing_extensions': 'typing-extensions',
        'dataclasses': 'dataclasses',
        'asyncio': '',  # 内置模块
        'json': '',     # 内置模块
        'os': '',       # 内置模块
        'sys': '',      # 内置模块
        'time': '',     # 内置模块
        'datetime': '', # 内置模块
        'logging': '',  # 内置模块
        'threading': '',# 内置模块
        'multiprocessing': '', # 内置模块
        'concurrent': '',      # 内置模块
        'collections': '',     # 内置模块
        'itertools': '',       # 内置模块
        'functools': '',       # 内置模块
        'operator': '',        # 内置模块
        'copy': '',            # 内置模块
        'pickle': '',          # 内置模块
        'socket': '',          # 内置模块
        'urllib': '',          # 内置模块
        'http': '',            # 内置模块
        'email': '',           # 内置模块
        'base64': '',          # 内置模块
        'hashlib': '',         # 内置模块
        'hmac': '',            # 内置模块
        'secrets': '',         # 内置模块
        'uuid': '',            # 内置模块
        'random': '',          # 内置模块
        'math': '',            # 内置模块
        'statistics': '',      # 内置模块
        'decimal': '',         # 内置模块
        'fractions': '',       # 内置模块
        'cmath': '',           # 内置模块
        're': '',              # 内置模块
        'string': '',          # 内置模块
        'textwrap': '',        # 内置模块
        'unicodedata': '',     # 内置模块
        'stringprep': '',      # 内置模块
        'readline': '',        # 内置模块
        'rlcompleter': '',     # 内置模块
        'struct': '',          # 内置模块
        'codecs': '',          # 内置模块
        'io': '',              # 内置模块
        'pathlib': '',         # 内置模块
        'glob': '',            # 内置模块
        'fnmatch': '',         # 内置模块
        'linecache': '',       # 内置模块
        'tempfile': '',        # 内置模块
        'shutil': '',          # 内置模块
        'macpath': '',         # 内置模块
        'stat': '',            # 内置模块
        'fileinput': '',       # 内置模块
        'filecmp': '',         # 内置模块
        'csv': '',             # 内置模块
        'configparser': '',    # 内置模块
        'netrc': '',           # 内置模块
        'xdrlib': '',          # 内置模块
        'plistlib': '',        # 内置模块
        'zlib': '',            # 内置模块
        'gzip': '',            # 内置模块
        'bz2': '',             # 内置模块
        'lzma': '',            # 内置模块
        'zipfile': '',         # 内置模块
        'tarfile': '',         # 内置模块
        'sqlite3': '',         # 内置模块
        'dbm': '',             # 内置模块
        'pickle': '',          # 内置模块
        'copyreg': '',         # 内置模块
        'shelve': '',          # 内置模块
        'marshal': '',         # 内置模块
        'dbm': '',             # 内置模块
        'sqlite3': '',         # 内置模块
        'zoneinfo': '',        # 内置模块
        'calendar': '',        # 内置模块
        'collections': '',     # 内置模块
        'heapq': '',           # 内置模块
        'bisect': '',          # 内置模块
        'array': '',           # 内置模块
        'weakref': '',         # 内置模块
        'types': '',           # 内置模块
        'copy': '',            # 内置模块
        'pprint': '',          # 内置模块
        'reprlib': '',         # 内置模块
        'enum': '',            # 内置模块
        'numbers': '',         # 内置模块
        'cmath': '',           # 内置模块
        'decimal': '',         # 内置模块
        'fractions': '',       # 内置模块
        'random': '',          # 内置模块
        'statistics': '',      # 内置模块
        'itertools': '',       # 内置模块
        'functools': '',       # 内置模块
        'operator': '',        # 内置模块
        'pathlib': '',         # 内置模块
        'os.path': '',         # 内置模块
        'fileinput': '',       # 内置模块
        'stat': '',            # 内置模块
        'filecmp': '',         # 内置模块
        'tempfile': '',        # 内置模块
        'glob': '',            # 内置模块
        'fnmatch': '',         # 内置模块
        'linecache': '',       # 内置模块
        'shutil': '',          # 内置模块
        'pickle': '',          # 内置模块
        'copyreg': '',         # 内置模块
        'shelve': '',          # 内置模块
        'marshal': '',         # 内置模块
        'dbm': '',             # 内置模块
        'sqlite3': '',         # 内置模块
        'zlib': '',            # 内置模块
        'gzip': '',            # 内置模块
        'bz2': '',             # 内置模块
        'lzma': '',            # 内置模块
        'zipfile': '',         # 内置模块
        'tarfile': '',         # 内置模块
        'csv': '',             # 内置模块
        'configparser': '',    # 内置模块
        'netrc': '',           # 内置模块
        'xdrlib': '',          # 内置模块
        'plistlib': '',        # 内置模块
        'hashlib': '',         # 内置模块
        'hmac': '',            # 内置模块
        'secrets': '',         # 内置模块
        'os': '',              # 内置模块
        'io': '',              # 内置模块
        'time': '',            # 内置模块
        'argparse': '',        # 内置模块
        'optparse': '',        # 内置模块
        'getopt': '',          # 内置模块
        'logging': '',         # 内置模块
        'logging.config': '',  # 内置模块
        'logging.handlers': '',# 内置模块
        'getpass': '',         # 内置模块
        'curses': '',          # 内置模块
        'curses.textpad': '',  # 内置模块
        'curses.ascii': '',    # 内置模块
        'curses.panel': '',    # 内置模块
        'platform': '',        # 内置模块
        'errno': '',           # 内置模块
        'ctypes': '',          # 内置模块
    }
    
    return common_packages

def main():
    """主函数"""
    print("=" * 60)
    print("项目依赖检查工具")
    print("=" * 60)
    
    # 扫描依赖问题
    issues = scan_project_dependencies()
    
    if not issues:
        print("✅ 没有发现依赖问题!")
        return
    
    print(f"❌ 发现 {len(issues)} 个文件有依赖问题:")
    print()
    
    # 收集所有缺失的包
    all_missing = set()
    
    for file_path, missing_imports in issues.items():
        print(f"📁 {file_path}:")
        for imp in missing_imports:
            print(f"  ❌ {imp}")
            if not imp.startswith(('SYNTAX_ERROR:', 'ERROR:')):
                all_missing.add(imp.split('.')[0])  # 只取主模块名
        print()
    
    # 生成安装命令
    if all_missing:
        print("🔧 建议安装以下依赖:")
        print()
        
        common_packages = generate_requirements()
        install_commands = []
        
        for package in sorted(all_missing):
            if package in common_packages:
                pip_name = common_packages[package]
                if pip_name:  # 不是内置模块
                    install_commands.append(pip_name)
                else:
                    print(f"✅ {package} 是内置模块,无需安装")
            else:
                install_commands.append(package)
        
        if install_commands:
            print(f"pip install {' '.join(install_commands)}")
            print()
            
            # 保存到文件
            with open('missing_requirements.txt', 'w') as f:
                for cmd in install_commands:
                    f.write(f"{cmd}\n")
            print("📝 已保存到 missing_requirements.txt")

if __name__ == "__main__":
    main()
