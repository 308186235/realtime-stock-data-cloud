#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复项目中的编码问题和乱码
"""

import os
import re
import chardet
import shutil
from datetime import datetime

def detect_encoding(file_path):
    """检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    except Exception as e:
        print(f"❌ 检测编码失败 {file_path}: {e}")
        return None

def fix_chinese_encoding(content):
    """修复中文编码问题"""
    # 常见的乱码模式和对应的正确中文
    fixes = {
        # 执行相关
        '鎵ц': '执行',
        '鍐崇瓥': '决策',
        '杩囩▼': '过程',
        '鐢熸垚': '生成',
        '浜ゆ槗': '交易',
        '鍐崇瓥涓婁笅鏂囦俊鎭': '决策上下文信息',
        '鍐崇瓥缁撴灉': '决策结果',
        '瑕佹墽琛岀殑鍔ㄤ綔': '要执行的动作',
        '鎵ц缁撴灉': '执行结果',
        
        # 学习相关
        '浠庡弽棣堜腑瀛範': '从反馈中学习',
        '鏀硅繘': '改进',
        '妯瀷': '模型',
        '瀛範鍙嶉鏁版嵁': '学习反馈数据',
        '瀛範缁撴灉': '学习结果',
        
        # 连接相关
        '杩炴帴澶栭儴妯潡': '连接外部模块',
        '绯荤粺': '系统',
        '妯潡淇℃伅': '模块信息',
        '杩炴帴缁撴灉': '连接结果',
        
        # 初始化相关
        '鍒濆鍖': '初始化',
        '鍚勪釜瀛愮郴缁': '各个子系统',
        '鍒濆鍖栧競鍦哄垎鏋愬櫒': '初始化市场分析器',
        
        # 监控相关
        '绯荤粺鐩戞帶': '系统监控',
        '妫€鏌': '检查',
        '璧勬簮浣跨敤': '资源使用',
        '鍋ュ悍鐘舵€': '健康状态',
        
        # 风险相关
        '璇勪及褰撳墠椋庨櫓鐘跺喌': '评估当前风险状况',
        '椋庨櫓璇勪及': '风险评估',
        
        # 策略相关
        '铻嶅悎澶氱': '融合多种',
        '绛栫暐': '策略',
        '绛栫暐铻嶅悎': '策略融合',
        '閫昏緫': '逻辑',
        
        # 买入相关
        '涔板叆鎿嶄綔': '买入操作',
        '浣跨敤浜ゆ槗鎵ц鍣': '使用交易执行器',
        '鎵ц涔板叆': '执行买入',
        
        # 处理相关
        '澶勭悊鍐崇瓥璇锋眰': '处理决策请求',
        '澶勭悊鎵ц璇锋眰': '处理执行请求',
        
        # 其他常见乱码
        '鍑洪敊鍚庣煭鏆傛殏鍋': '出错后短暂暂停',
        '鍒嗘瀽甯傚満鐘舵€': '分析市场状态',
        '鐢熸垚鏈€缁堝喅绛': '生成最终决策',
        '搴旂敤瀵瑰啿绛栫暐': '应用对冲策略',
        '鍙栨秷璁㈠崟': '取消订单',
        '妯潡杩炴帴': '模块连接',
        '楠岃瘉妯潡淇℃伅': '验证模块信息',
        '澶勭悊鍋ュ悍闂': '处理健康问题',
        
        # 特殊字符修复
        '\ue511': '',
        '\ue750': '',
        '\ue5c5': '',
        '\ue752': '',
        '\ufe3f': '',
        '\u2033': '',
    }
    
    # 应用修复
    for wrong, correct in fixes.items():
        content = content.replace(wrong, correct)
    
    return content

def fix_file_encoding(file_path):
    """修复单个文件的编码问题"""
    try:
        # 检测当前编码
        encoding = detect_encoding(file_path)
        if not encoding:
            return False
        
        # 读取文件内容
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        # 修复中文乱码
        fixed_content = fix_chinese_encoding(content)
        
        # 如果内容有变化,则保存
        if fixed_content != content:
            # 备份原文件
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            
            # 保存修复后的文件
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(fixed_content)
            
            print(f"✅ 修复文件: {file_path}")
            return True
        else:
            print(f"⚪ 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def scan_and_fix_project():
    """扫描并修复整个项目"""
    print("🔍 开始扫描项目编码问题...")
    
    # 需要检查的文件扩展名
    extensions = ['.py', '.js', '.vue', '.json', '.md', '.txt', '.csv']
    
    # 需要跳过的目录
    skip_dirs = {
        '__pycache__', '.git', 'node_modules', '.vscode', 
        'backup_deleted_20250624_224708', 'logs', 'models'
    }
    
    fixed_files = []
    error_files = []
    
    # 遍历项目目录
    for root, dirs, files in os.walk('.'):
        # 跳过指定目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            # 检查文件扩展名
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                
                try:
                    if fix_file_encoding(file_path):
                        fixed_files.append(file_path)
                except Exception as e:
                    error_files.append((file_path, str(e)))
    
    # 输出结果
    print(f"\n📊 修复结果:")
    print(f"✅ 成功修复: {len(fixed_files)} 个文件")
    print(f"❌ 修复失败: {len(error_files)} 个文件")
    
    if fixed_files:
        print(f"\n✅ 已修复的文件:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    
    if error_files:
        print(f"\n❌ 修复失败的文件:")
        for file_path, error in error_files:
            print(f"  - {file_path}: {error}")

if __name__ == "__main__":
    try:
        import chardet
    except ImportError:
        print("❌ 缺少 chardet 库,正在安装...")
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
    
    scan_and_fix_project()
    print("\n🎉 编码修复完成!")
