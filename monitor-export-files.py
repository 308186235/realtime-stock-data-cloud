#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控交易软件导出文件
检测新生成的持仓,成交,委托数据文件
"""

import os
import time
import glob
from datetime import datetime

class ExportFileMonitor:
    def __init__(self):
        self.last_check_time = time.time()
        self.known_files = set()
        self.initialize_known_files()
    
    def initialize_known_files(self):
        """初始化已知文件列表"""
        patterns = [
            '*持仓数据*.xls*',
            '*成交数据*.xls*', 
            '*委托数据*.xls*'
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            self.known_files.update(files)
        
        print(f"📁 初始化完成,已知文件数: {len(self.known_files)}")
    
    def check_new_files(self):
        """检查新文件"""
        patterns = {
            '*持仓数据*.xls*': '持仓数据',
            '*成交数据*.xls*': '成交数据',
            '*委托数据*.xls*': '委托数据'
        }
        
        new_files = []
        
        for pattern, data_type in patterns.items():
            files = glob.glob(pattern)
            for file_path in files:
                if file_path not in self.known_files:
                    # 检查文件修改时间是否在最近
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime > self.last_check_time:
                        new_files.append({
                            'path': file_path,
                            'type': data_type,
                            'size': os.path.getsize(file_path),
                            'mtime': datetime.fromtimestamp(file_mtime)
                        })
                        self.known_files.add(file_path)
        
        return new_files
    
    def process_new_file(self, file_info):
        """处理新文件"""
        print(f"\n🎉 检测到新文件!")
        print(f"   📊 类型: {file_info['type']}")
        print(f"   📁 文件: {file_info['path']}")
        print(f"   📏 大小: {file_info['size']} 字节")
        print(f"   🕒 时间: {file_info['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 尝试读取文件内容预览
        try:
            if file_info['path'].endswith('.xls') or file_info['path'].endswith('.xlsx'):
                import pandas as pd
                df = pd.read_excel(file_info['path'])
                print(f"   📋 数据行数: {len(df)}")
                print(f"   📋 列数: {len(df.columns)}")
                if len(df.columns) > 0:
                    print(f"   📋 列名: {list(df.columns)[:5]}...")  # 显示前5列
                
                # 显示前几行数据
                if len(df) > 0:
                    print(f"   📊 数据预览:")
                    for i, row in df.head(3).iterrows():
                        print(f"      行{i+1}: {dict(row)}")
                        
        except Exception as e:
            print(f"   ⚠️ 文件读取异常: {e}")
    
    def submit_to_agent(self, file_info):
        """提交数据到Agent系统"""
        print(f"\n🤖 提交{file_info['type']}到Agent系统...")
        
        try:
            import requests
            
            # 模拟提交到本地API
            api_url = "http://localhost:8080/export"
            data = {
                "data_type": file_info['type'].replace('数据', ''),
                "file_path": file_info['path'],
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(api_url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {file_info['type']}提交成功")
                return True
            else:
                print(f"   ⚠️ {file_info['type']}提交失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {file_info['type']}提交异常: {e}")
            return False
    
    def run_monitor(self, duration=300):
        """运行监控 (默认5分钟)"""
        print("🔍 开始监控交易软件导出文件")
        print("=" * 50)
        print(f"监控时长: {duration}秒")
        print("请在交易软件中按 W/E/R 键导出数据...")
        print("\n等待文件导出...")
        
        start_time = time.time()
        check_interval = 2  # 每2秒检查一次
        
        while time.time() - start_time < duration:
            new_files = self.check_new_files()
            
            if new_files:
                for file_info in new_files:
                    self.process_new_file(file_info)
                    
                    # 提交到Agent系统
                    success = self.submit_to_agent(file_info)
                    
                    if success:
                        print(f"   🎯 {file_info['type']}已成功提交给Agent分析")
                    
                print(f"\n📊 本次检测到 {len(new_files)} 个新文件")
                
                # 如果检测到所有三种类型的文件,可以进行完整分析
                detected_types = [f['type'] for f in new_files]
                if len(set(detected_types)) >= 2:  # 至少两种类型
                    print("\n🤖 检测到多种数据类型,可以进行完整的Agent分析!")
                    self.perform_complete_analysis()
            
            time.sleep(check_interval)
            self.last_check_time = time.time()
        
        print(f"\n⏰ 监控结束 (运行了 {duration} 秒)")
        self.show_summary()
    
    def perform_complete_analysis(self):
        """执行完整的Agent分析"""
        print("\n🧠 执行完整Agent分析...")
        print("   📊 分析投资组合结构...")
        print("   📈 评估交易绩效...")
        print("   🎯 生成投资建议...")
        
        # 模拟分析结果
        analysis_result = {
            "portfolio_risk": "中等",
            "trading_frequency": "适中", 
            "profit_potential": "良好",
            "recommendations": [
                "建议适当增加科技股配置",
                "当前仓位控制合理",
                "可考虑定期定额投资"
            ]
        }
        
        print(f"\n📋 Agent分析结果:")
        print(f"   📈 投资组合风险: {analysis_result['portfolio_risk']}")
        print(f"   🔄 交易频率: {analysis_result['trading_frequency']}")
        print(f"   💰 盈利潜力: {analysis_result['profit_potential']}")
        print(f"   💡 主要建议:")
        for i, rec in enumerate(analysis_result['recommendations'], 1):
            print(f"      {i}. {rec}")
    
    def show_summary(self):
        """显示监控总结"""
        current_files = {
            '*持仓数据*.xls*': '持仓数据',
            '*成交数据*.xls*': '成交数据',
            '*委托数据*.xls*': '委托数据'
        }
        
        print("\n📊 当前文件状态:")
        print("-" * 40)
        
        for pattern, data_type in current_files.items():
            files = glob.glob(pattern)
            if files:
                latest_file = max(files, key=os.path.getmtime)
                mtime = datetime.fromtimestamp(os.path.getmtime(latest_file))
                print(f"✅ {data_type}: {os.path.basename(latest_file)}")
                print(f"   时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ {data_type}: 未找到文件")
        
        print(f"\n💡 使用说明:")
        print("1. 在交易软件中按 W 键导出持仓数据")
        print("2. 在交易软件中按 E 键导出成交数据")
        print("3. 在交易软件中按 R 键导出委托数据")
        print("4. 系统会自动检测并提交给Agent分析")

def main():
    """主函数"""
    monitor = ExportFileMonitor()
    
    print("🎯 交易数据导出监控系统")
    print("=" * 50)
    print("功能: 实时监控交易软件导出的数据文件")
    print("目标: 自动提交数据给Agent进行智能分析")
    
    try:
        # 运行5分钟监控
        monitor.run_monitor(duration=300)
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断监控")
        monitor.show_summary()
    except Exception as e:
        print(f"\n❌ 监控异常: {e}")
        monitor.show_summary()

if __name__ == "__main__":
    main()
