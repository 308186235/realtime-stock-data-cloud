#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟数据清除验证脚本
验证系统中是否还存在模拟数据
"""

import os
import re
import json
from pathlib import Path

class MockDataVerifier:
    def __init__(self):
        self.mock_patterns = [
            r'000001.*平安银行',
            r'000002.*万科A',
            r'600036.*招商银行',
            r'模拟数据',
            r'mock.*data',
            r'fake.*data',
            r'test.*data',
            r'demo.*data',
            r'sample.*data',
            r'simulated',
            r'generated.*data',
            r'random.*data',
            r'Math\.random',
            r'np\.random',
            r'mockPositions',
            r'mockTrades',
            r'mockData',
            r'createMockData',
            r'generateMockData',
            r'simulateDataPush'
        ]
        
        self.exclude_patterns = [
            r'# 已删除',
            r'# 已禁用',
            r'❌.*模拟',
            r'禁止.*模拟',
            r'拒绝.*模拟',
            r'检测到模拟数据',
            r'MockDataDetectedError',
            r'mock.*已.*移除',
            r'mock.*已.*删除',
            r'拒绝返回模拟数据',
            r'系统要求使用真实数据源',
            r'verify_mock_data',
            r'MOCK_DATA_REMOVAL',
            r'final_mock_data_cleanup'
        ]
        
        self.exclude_files = [
            'verify_mock_data_removal_complete.py',
            'verify_no_mock_data.py',
            'final_mock_data_cleanup.py',
            'MOCK_DATA_REMOVAL_COMPLETE.md',
            'REMOVE_ALL_MOCK_DATA.md',
            'FINAL_MOCK_DATA_REMOVAL_REPORT.md'
        ]
        
        self.exclude_dirs = [
            '.git',
            '__pycache__',
            'node_modules',
            '.vscode',
            'backup_deleted_',
            'backup_unused_',
            'localhost_fix_',
            'frontend_api_fix_',
            'domain_fix_',
            'validation_backup_',
            'high_priority_backup_',
            'deps_backup_',
            'config_backup_'
        ]
        
        self.results = {
            'files_checked': 0,
            'mock_data_found': [],
            'clean_files': [],
            'errors': []
        }

    def should_exclude_file(self, file_path):
        """检查文件是否应该被排除"""
        file_name = os.path.basename(file_path)
        
        # 排除特定文件
        if file_name in self.exclude_files:
            return True
            
        # 排除备份文件
        if '.backup' in file_name or '.bak' in file_name:
            return True
            
        # 排除特定目录
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in file_path:
                return True
                
        return False

    def check_file_for_mock_data(self, file_path):
        """检查单个文件是否包含模拟数据"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            mock_matches = []
            
            for pattern in self.mock_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 检查是否在排除模式中
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    line_content = content[line_start:line_end]
                    
                    # 检查是否是已禁用的模拟数据
                    is_excluded = False
                    for exclude_pattern in self.exclude_patterns:
                        if re.search(exclude_pattern, line_content, re.IGNORECASE):
                            is_excluded = True
                            break
                    
                    if not is_excluded:
                        line_number = content[:match.start()].count('\n') + 1
                        mock_matches.append({
                            'pattern': pattern,
                            'line': line_number,
                            'content': line_content.strip(),
                            'match': match.group()
                        })
            
            return mock_matches
            
        except Exception as e:
            self.results['errors'].append(f"读取文件失败 {file_path}: {str(e)}")
            return []

    def scan_directory(self, directory='.'):
        """扫描目录查找模拟数据"""
        print(f"🔍 开始扫描目录: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # 排除特定目录
            dirs[:] = [d for d in dirs if not any(exclude in d for exclude in self.exclude_dirs)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 只检查代码文件
                if not any(file.endswith(ext) for ext in ['.py', '.js', '.vue', '.html', '.md', '.json']):
                    continue
                    
                if self.should_exclude_file(file_path):
                    continue
                
                self.results['files_checked'] += 1
                mock_matches = self.check_file_for_mock_data(file_path)
                
                if mock_matches:
                    self.results['mock_data_found'].append({
                        'file': file_path,
                        'matches': mock_matches
                    })
                    print(f"❌ 发现模拟数据: {file_path}")
                    for match in mock_matches:
                        print(f"   行 {match['line']}: {match['content'][:100]}...")
                else:
                    self.results['clean_files'].append(file_path)

    def generate_report(self):
        """生成验证报告"""
        report = {
            'timestamp': '2025-07-03T00:00:00Z',
            'summary': {
                'files_checked': self.results['files_checked'],
                'files_with_mock_data': len(self.results['mock_data_found']),
                'clean_files': len(self.results['clean_files']),
                'errors': len(self.results['errors'])
            },
            'status': 'CLEAN' if len(self.results['mock_data_found']) == 0 else 'MOCK_DATA_FOUND',
            'mock_data_files': self.results['mock_data_found'],
            'errors': self.results['errors']
        }
        
        # 保存报告
        with open('mock_data_verification_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

    def print_summary(self, report):
        """打印验证摘要"""
        print("\n" + "="*60)
        print("📋 模拟数据清除验证报告")
        print("="*60)
        print(f"检查文件数量: {report['summary']['files_checked']}")
        print(f"发现模拟数据的文件: {report['summary']['files_with_mock_data']}")
        print(f"清洁文件数量: {report['summary']['clean_files']}")
        print(f"错误数量: {report['summary']['errors']}")
        
        if report['status'] == 'CLEAN':
            print("\n✅ 验证通过！系统中未发现模拟数据")
            print("🎉 所有模拟数据已成功清除！")
        else:
            print(f"\n❌ 验证失败！发现 {report['summary']['files_with_mock_data']} 个文件包含模拟数据")
            print("需要进一步清理以下文件:")
            for file_info in report['mock_data_files']:
                print(f"  - {file_info['file']}")
        
        print(f"\n📄 详细报告已保存到: mock_data_verification_report.json")

def main():
    """主函数"""
    print("🚨 开始验证模拟数据清除情况...")
    
    verifier = MockDataVerifier()
    verifier.scan_directory('.')
    report = verifier.generate_report()
    verifier.print_summary(report)
    
    # 返回退出码
    return 0 if report['status'] == 'CLEAN' else 1

if __name__ == '__main__':
    exit(main())
