#!/usr/bin/env python3
"""
验证系统中没有模拟数据
确保所有模拟数据已被完全移除
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class MockDataDetector:
    """模拟数据检测器"""
    
    def __init__(self):
        self.mock_patterns = [
            r'mock',
            r'fake',
            r'test.*data',
            r'demo.*data',
            r'sample.*data',
            r'simulated',
            r'generated.*data',
            r'random.*data',
            r'artificial',
            r'synthetic',
            r'Math\.random',
            r'np\.random',
            r'random\.',
            r'data_source.*[\'"]mock[\'"]',
            r'source.*[\'"]mock[\'"]',
            r'USE_MOCK_DATA',
            r'mockResponse',
            r'createMockData',
            r'generateMockData'
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
            r'mock.*已.*删除'
        ]
        
        self.exclude_files = [
            'verify_no_mock_data.py',
            'MOCK_DATA_REMOVAL_COMPLETE.md',
            'REMOVE_ALL_MOCK_DATA.md',
            'data_validation.py'
        ]
        
        self.exclude_dirs = [
            '.git',
            '__pycache__',
            'node_modules',
            '.vscode',
            'backup_deleted_*'
        ]
    
    def scan_directory(self, directory: str) -> Dict[str, List[Tuple[int, str]]]:
        """扫描目录查找模拟数据"""
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # 排除特定目录
            dirs[:] = [d for d in dirs if not any(
                re.match(pattern, d) for pattern in self.exclude_dirs
            )]
            
            for file in files:
                if file in self.exclude_files:
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                # 只检查代码文件
                if self._is_code_file(file):
                    mock_lines = self._scan_file(file_path)
                    if mock_lines:
                        results[relative_path] = mock_lines
        
        return results
    
    def _is_code_file(self, filename: str) -> bool:
        """判断是否为代码文件"""
        code_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue',
            '.html', '.css', '.scss', '.less',
            '.json', '.yaml', '.yml', '.toml'
        ]
        
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _scan_file(self, file_path: str) -> List[Tuple[int, str]]:
        """扫描单个文件"""
        mock_lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_lower = line.lower().strip()
                    
                    # 跳过排除的行
                    if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.exclude_patterns):
                        continue
                    
                    # 检查模拟数据模式
                    for pattern in self.mock_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            mock_lines.append((line_num, line.strip()))
                            break
        
        except Exception as e:
            print(f"⚠️ 无法读取文件 {file_path}: {e}")
        
        return mock_lines
    
    def generate_report(self, results: Dict[str, List[Tuple[int, str]]]) -> str:
        """生成检测报告"""
        if not results:
            return """
✅ 模拟数据检测完成 - 未发现模拟数据

🎉 恭喜！系统中没有检测到任何模拟数据！
所有模拟数据已被成功移除。

系统现在是100%真实数据驱动的！
"""
        
        report = "❌ 模拟数据检测报告 - 发现问题\n"
        report += "=" * 50 + "\n\n"
        
        total_files = len(results)
        total_lines = sum(len(lines) for lines in results.values())
        
        report += f"发现 {total_files} 个文件包含 {total_lines} 行可疑代码\n\n"
        
        for file_path, lines in results.items():
            report += f"📁 {file_path}\n"
            for line_num, line_content in lines:
                report += f"   第{line_num}行: {line_content}\n"
            report += "\n"
        
        report += "🚨 请立即修复这些问题！\n"
        report += "系统不允许任何形式的模拟数据！\n"
        
        return report

def main():
    """主函数"""
    print("🔍 开始扫描系统中的模拟数据...")
    print("=" * 50)
    
    detector = MockDataDetector()
    
    # 扫描当前目录
    current_dir = os.getcwd()
    results = detector.scan_directory(current_dir)
    
    # 生成报告
    report = detector.generate_report(results)
    print(report)
    
    # 保存报告
    report_file = "mock_data_detection_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 详细报告已保存到: {report_file}")
    
    # 返回状态码
    if results:
        print("\n❌ 检测失败：发现模拟数据")
        return 1
    else:
        print("\n✅ 检测通过：未发现模拟数据")
        return 0

if __name__ == "__main__":
    sys.exit(main())
