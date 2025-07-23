#!/usr/bin/env python3
"""
分析云端API的数据源和配置
确定API是从OneDrive读取还是使用备用数据
"""

import json
import requests
from datetime import datetime
from pathlib import Path

class CloudAPIAnalyzer:
    """云端API分析器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        
    def analyze_local_files(self):
        """分析本地文件"""
        print("📁 分析本地OneDrive文件...")
        
        local_data = {}
        
        for filename in ["latest_positions.json", "latest_balance.json"]:
            file_path = self.onedrive_path / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    local_data[filename] = {
                        "timestamp": data.get("timestamp"),
                        "test_id": data.get("test_id"),
                        "source": data.get("source"),
                        "data_type": data.get("data_type"),
                        "export_method": data.get("export_method"),
                        "file_size": len(json.dumps(data)),
                        "has_test_markers": any("test" in str(v).lower() for v in data.values() if isinstance(v, (str, dict)))
                    }
                    
                    print(f"✅ {filename}:")
                    print(f"   时间戳: {local_data[filename]['timestamp']}")
                    print(f"   测试ID: {local_data[filename]['test_id']}")
                    print(f"   数据源: {local_data[filename]['source']}")
                    print(f"   导出方式: {local_data[filename]['export_method']}")
                    print(f"   文件大小: {local_data[filename]['file_size']} 字符")
                    print(f"   包含测试标记: {local_data[filename]['has_test_markers']}")
                    
                except Exception as e:
                    print(f"❌ {filename}: 读取错误 - {e}")
                    local_data[filename] = {"error": str(e)}
            else:
                print(f"❌ {filename}: 文件不存在")
                local_data[filename] = {"exists": False}
        
        return local_data
    
    def analyze_cloud_api(self):
        """分析云端API响应"""
        print("\n🌐 分析云端API响应...")
        
        endpoints = [
            ("positions", f"{self.cloud_api}/api/local-trading/positions"),
            ("balance", f"{self.cloud_api}/api/local-trading/balance")
        ]
        
        cloud_data = {}
        
        for data_type, url in endpoints:
            print(f"\n🔥 分析: {data_type} API")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    cloud_data[data_type] = {
                        "timestamp": data.get("timestamp"),
                        "test_id": data.get("test_id"),
                        "source": data.get("source"),
                        "data_type": data.get("data_type"),
                        "export_method": data.get("export_method"),
                        "response_size": len(json.dumps(data)),
                        "has_test_markers": any("test" in str(v).lower() for v in data.values() if isinstance(v, (str, dict))),
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code
                    }
                    
                    print(f"✅ 响应成功:")
                    print(f"   时间戳: {cloud_data[data_type]['timestamp']}")
                    print(f"   测试ID: {cloud_data[data_type]['test_id']}")
                    print(f"   数据源: {cloud_data[data_type]['source']}")
                    print(f"   导出方式: {cloud_data[data_type]['export_method']}")
                    print(f"   响应大小: {cloud_data[data_type]['response_size']} 字符")
                    print(f"   包含测试标记: {cloud_data[data_type]['has_test_markers']}")
                    print(f"   响应时间: {cloud_data[data_type]['response_time']:.2f}秒")
                    
                    # 显示原始数据的关键部分
                    print(f"   原始数据预览:")
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:3]:
                            if isinstance(value, (str, int, float)):
                                print(f"     {key}: {value}")
                            elif isinstance(value, dict):
                                print(f"     {key}: {{...}} (字典)")
                            elif isinstance(value, list):
                                print(f"     {key}: [...] (列表,{len(value)}项)")
                    
                else:
                    print(f"❌ 响应失败: {response.status_code}")
                    cloud_data[data_type] = {
                        "error": f"HTTP {response.status_code}",
                        "response": response.text[:200]
                    }
                    
            except Exception as e:
                print(f"❌ 请求异常: {e}")
                cloud_data[data_type] = {"error": str(e)}
        
        return cloud_data
    
    def compare_data_sources(self, local_data, cloud_data):
        """比较本地和云端数据源"""
        print("\n📊 数据源比较分析")
        print("=" * 60)
        
        comparisons = []
        
        # 比较持仓数据
        if "latest_positions.json" in local_data and "positions" in cloud_data:
            local_pos = local_data["latest_positions.json"]
            cloud_pos = cloud_data["positions"]
            
            comparison = {
                "data_type": "持仓数据",
                "local_timestamp": local_pos.get("timestamp"),
                "cloud_timestamp": cloud_pos.get("timestamp"),
                "timestamp_match": local_pos.get("timestamp") == cloud_pos.get("timestamp"),
                "test_id_match": local_pos.get("test_id") == cloud_pos.get("test_id"),
                "source_match": local_pos.get("source") == cloud_pos.get("source"),
                "size_difference": abs((local_pos.get("file_size", 0)) - (cloud_pos.get("response_size", 0)))
            }
            comparisons.append(comparison)
        
        # 比较余额数据
        if "latest_balance.json" in local_data and "balance" in cloud_data:
            local_bal = local_data["latest_balance.json"]
            cloud_bal = cloud_data["balance"]
            
            comparison = {
                "data_type": "余额数据",
                "local_timestamp": local_bal.get("timestamp"),
                "cloud_timestamp": cloud_bal.get("timestamp"),
                "timestamp_match": local_bal.get("timestamp") == cloud_bal.get("timestamp"),
                "test_id_match": local_bal.get("test_id") == cloud_bal.get("test_id"),
                "source_match": local_bal.get("source") == cloud_bal.get("source"),
                "size_difference": abs((local_bal.get("file_size", 0)) - (cloud_bal.get("response_size", 0)))
            }
            comparisons.append(comparison)
        
        # 显示比较结果
        for comp in comparisons:
            print(f"\n📋 {comp['data_type']}:")
            print(f"   本地时间戳: {comp['local_timestamp']}")
            print(f"   云端时间戳: {comp['cloud_timestamp']}")
            
            if comp['timestamp_match']:
                print("   ✅ 时间戳匹配 - 云端使用本地数据")
            else:
                print("   ❌ 时间戳不匹配 - 云端可能使用备用数据")
            
            if comp['test_id_match']:
                print("   ✅ 测试ID匹配")
            else:
                print("   ❌ 测试ID不匹配")
            
            if comp['source_match']:
                print("   ✅ 数据源匹配")
            else:
                print("   ❌ 数据源不匹配")
            
            print(f"   📏 大小差异: {comp['size_difference']} 字符")
        
        return comparisons
    
    def generate_analysis_report(self, local_data, cloud_data, comparisons):
        """生成分析报告"""
        print("\n" + "=" * 60)
        print("📊 云端API数据源分析报告")
        print("=" * 60)
        print(f"⏰ 分析时间: {datetime.now().isoformat()}")
        
        # 判断数据源类型
        using_local_data = any(comp['timestamp_match'] for comp in comparisons)
        using_backup_data = not using_local_data
        
        print(f"\n🔍 数据源判断:")
        if using_local_data:
            print("✅ 云端API正在使用本地OneDrive数据")
            print("✅ 本地导出 → OneDrive → 云端API 流程正常")
        else:
            print("⚠️ 云端API可能使用备用/缓存数据")
            print("📝 原因可能包括:")
            print("   1. OneDrive同步延迟")
            print("   2. 云端缓存机制")
            print("   3. 备用数据源配置")
            print("   4. API读取路径配置问题")
        
        # 数据新鲜度分析
        print(f"\n📅 数据新鲜度分析:")
        for comp in comparisons:
            if comp['local_timestamp'] and comp['cloud_timestamp']:
                try:
                    from datetime import datetime as dt
                    local_time = dt.fromisoformat(comp['local_timestamp'].replace('Z', '+00:00'))
                    cloud_time = dt.fromisoformat(comp['cloud_timestamp'].replace('Z', '+00:00'))
                    time_diff = abs((local_time - cloud_time).total_seconds())
                    
                    print(f"   {comp['data_type']}: 时间差 {time_diff:.0f} 秒")
                    
                    if time_diff < 60:
                        print("     ✅ 数据很新鲜 (< 1分钟)")
                    elif time_diff < 3600:
                        print("     ⚠️ 数据较新 (< 1小时)")
                    else:
                        print("     ❌ 数据较旧 (> 1小时)")
                        
                except Exception as e:
                    print(f"     ❌ 时间解析错误: {e}")
        
        # 建议和结论
        print(f"\n💡 建议和结论:")
        if using_local_data:
            print("🎉 系统工作正常!")
            print("✅ 云端Agent能够获取本地导出的实时数据")
            print("✅ 可以开始使用真实交易软件进行数据同步")
        else:
            print("🔧 需要进一步配置:")
            print("1. 检查云端API是否正确配置了OneDrive数据源")
            print("2. 验证OneDrive文件同步状态")
            print("3. 检查云端缓存设置")
            print("4. 确认API读取路径配置")
        
        print("=" * 60)
        
        return using_local_data
    
    def run_analysis(self):
        """运行完整分析"""
        print("🔍 云端API数据源深度分析")
        print("=" * 60)
        
        # 分析本地文件
        local_data = self.analyze_local_files()
        
        # 分析云端API
        cloud_data = self.analyze_cloud_api()
        
        # 比较数据源
        comparisons = self.compare_data_sources(local_data, cloud_data)
        
        # 生成分析报告
        success = self.generate_analysis_report(local_data, cloud_data, comparisons)
        
        return success

def main():
    """主函数"""
    analyzer = CloudAPIAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\n🎯 分析完成:系统正常工作!")
    else:
        print("\n🔧 分析完成:需要进一步配置")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
