#!/usr/bin/env python3
"""
基于现有表结构的数据整合系统
使用stocks和system_config表实现完整的数据同步功能
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta

# 配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'
API_URL = 'https://realtime-stock-api.pages.dev'

class WorkingDataIntegration:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'apikey': SUPABASE_KEY
        }
        
    def test_connections(self):
        """测试所有连接"""
        print("🔍 测试系统连接...")
        
        results = {}
        
        # 测试API连接
        try:
            response = requests.get(f'{API_URL}/api/health', timeout=10)
            results['api'] = response.status_code == 200
            print(f"API连接: {'✅ 正常' if results['api'] else '❌ 失败'}")
        except Exception as e:
            results['api'] = False
            print(f"API连接: ❌ 失败 - {e}")
        
        # 测试数据库连接
        try:
            response = requests.get(f'{SUPABASE_URL}/rest/v1/stocks?select=count&limit=1', 
                                  headers=self.headers, timeout=10)
            results['database'] = response.status_code == 200
            print(f"数据库连接: {'✅ 正常' if results['database'] else '❌ 失败'}")
        except Exception as e:
            results['database'] = False
            print(f"数据库连接: ❌ 失败 - {e}")
        
        return results
    
    def sync_stock_data(self):
        """同步股票数据到现有表结构"""
        print("\n🔄 开始股票数据同步...")
        
        try:
            # 获取API数据
            response = requests.get(f'{API_URL}/api/quotes?symbols=sz000001,sh600519,sz300750,sz002415,sh688599', timeout=15)
            if response.status_code != 200:
                print(f"❌ API请求失败: {response.status_code}")
                return False
                
            api_data = response.json()
            stocks = api_data.get('data', [])
            
            if not stocks:
                print("❌ API返回空数据")
                return False
                
            print(f"✅ 获取到 {len(stocks)} 只股票的数据")
            
            # 同步每只股票
            success_count = 0
            for stock in stocks:
                if self.update_stock_record(stock):
                    success_count += 1
                    
            print(f"✅ 成功同步 {success_count}/{len(stocks)} 只股票")
            
            # 记录同步状态
            self.record_sync_status(success_count, len(stocks))
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 数据同步异常: {e}")
            return False
    
    def update_stock_record(self, stock_data):
        """更新单只股票记录"""
        try:
            stock_code = stock_data.get('stock_code')
            
            # 准备更新数据
            update_data = {
                'name': stock_data.get('stock_name', ''),
                'current_price': float(stock_data.get('current_price', 0)),
                'volume': int(stock_data.get('volume', 0)),
                'change_percent': float(stock_data.get('change_percent', 0)),
                'last_updated': datetime.now().isoformat()
            }
            
            # 尝试更新现有记录
            response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/stocks?code=eq.{stock_code}',
                headers=self.headers,
                json=update_data,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print(f"  ✅ 更新 {stock_code}: {stock_data.get('current_price')}")
                return True
            elif response.status_code == 406:
                # 记录不存在，创建新记录
                return self.create_stock_record(stock_code, stock_data)
            else:
                print(f"  ❌ 更新失败 {stock_code}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 更新异常 {stock_code}: {e}")
            return False
    
    def create_stock_record(self, stock_code, stock_data):
        """创建新的股票记录"""
        try:
            new_record = {
                'code': stock_code,
                'name': stock_data.get('stock_name', ''),
                'current_price': float(stock_data.get('current_price', 0)),
                'volume': int(stock_data.get('volume', 0)),
                'change_percent': float(stock_data.get('change_percent', 0)),
                'last_updated': datetime.now().isoformat()
            }
            
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/stocks',
                headers=self.headers,
                json=new_record,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ 创建 {stock_code}: {stock_data.get('current_price')}")
                return True
            else:
                print(f"  ❌ 创建失败 {stock_code}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建异常 {stock_code}: {e}")
            return False
    
    def record_sync_status(self, success_count, total_count):
        """记录同步状态到system_config"""
        try:
            sync_status = {
                'key': 'last_sync_status',
                'value': json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'success_count': success_count,
                    'total_count': total_count,
                    'success_rate': round(success_count / total_count * 100, 2) if total_count > 0 else 0
                }),
                'description': '最后一次数据同步状态',
                'category': 'sync'
            }
            
            # 尝试更新现有记录
            response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/system_config?key=eq.last_sync_status',
                headers=self.headers,
                json=sync_status,
                timeout=10
            )
            
            if response.status_code not in [200, 204]:
                # 创建新记录
                requests.post(
                    f'{SUPABASE_URL}/rest/v1/system_config',
                    headers=self.headers,
                    json=sync_status,
                    timeout=10
                )
                
        except Exception as e:
            print(f"⚠️ 记录同步状态失败: {e}")
    
    def process_push_data_files(self):
        """处理推送数据文件"""
        print("\n📡 处理推送数据文件...")
        
        data_dir = 'stock_data'
        if not os.path.exists(data_dir):
            print("📁 推送数据目录不存在，创建目录...")
            os.makedirs(data_dir)
            return True
        
        # 获取所有数据文件
        dat_files = [f for f in os.listdir(data_dir) if f.endswith('.dat')]
        pkl_files = [f for f in os.listdir(data_dir) if f.endswith('.pkl')]
        
        total_files = len(dat_files) + len(pkl_files)
        print(f"📊 找到 {len(dat_files)} 个.dat文件和 {len(pkl_files)} 个.pkl文件")
        
        if total_files == 0:
            print("✅ 没有待处理的推送数据文件")
            return True
        
        # 处理文件（记录到system_config而不是专门的表）
        processed_count = 0
        
        for file_name in dat_files[:10]:  # 只处理前10个文件作为示例
            try:
                file_path = os.path.join(data_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 记录到system_config
                self.record_push_data(data, file_name)
                processed_count += 1
                
            except Exception as e:
                print(f"⚠️ 处理文件 {file_name} 失败: {e}")
        
        print(f"✅ 处理了 {processed_count} 个推送数据文件")
        
        # 清理旧文件
        self.cleanup_old_files(data_dir)
        
        return True
    
    def record_push_data(self, data, file_name):
        """记录推送数据到system_config"""
        try:
            push_record = {
                'key': f'push_data_{int(time.time())}',
                'value': json.dumps({
                    'symbol': data.get('symbol'),
                    'price': data.get('price'),
                    'volume': data.get('volume'),
                    'timestamp': data.get('timestamp'),
                    'file_name': file_name,
                    'processed_at': datetime.now().isoformat()
                }),
                'description': f'推送数据记录 - {data.get("symbol")}',
                'category': 'push_data'
            }
            
            requests.post(
                f'{SUPABASE_URL}/rest/v1/system_config',
                headers=self.headers,
                json=push_record,
                timeout=10
            )
            
        except Exception as e:
            print(f"⚠️ 记录推送数据失败: {e}")
    
    def cleanup_old_files(self, data_dir):
        """清理旧文件"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # 1小时前的文件
            cleaned_count = 0
            
            for file_name in os.listdir(data_dir):
                file_path = os.path.join(data_dir, file_name)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"🧹 清理了 {cleaned_count} 个旧文件")
                
        except Exception as e:
            print(f"⚠️ 清理文件失败: {e}")
    
    def get_system_status(self):
        """获取系统状态"""
        print("\n📊 获取系统状态...")
        
        try:
            # 获取stocks表统计
            response = requests.get(f'{SUPABASE_URL}/rest/v1/stocks?select=*', 
                                  headers=self.headers, timeout=10)
            stocks_data = response.json() if response.status_code == 200 else []
            
            # 获取system_config统计
            response = requests.get(f'{SUPABASE_URL}/rest/v1/system_config?select=*', 
                                  headers=self.headers, timeout=10)
            config_data = response.json() if response.status_code == 200 else []
            
            # 统计信息
            status = {
                'stocks_count': len(stocks_data),
                'config_count': len(config_data),
                'last_sync': None,
                'push_data_count': 0
            }
            
            # 查找最后同步时间
            for config in config_data:
                if config.get('key') == 'last_sync_status':
                    try:
                        sync_data = json.loads(config.get('value', '{}'))
                        status['last_sync'] = sync_data.get('timestamp')
                    except:
                        pass
                elif config.get('category') == 'push_data':
                    status['push_data_count'] += 1
            
            print(f"📈 股票记录数: {status['stocks_count']}")
            print(f"⚙️ 配置记录数: {status['config_count']}")
            print(f"📡 推送数据记录数: {status['push_data_count']}")
            print(f"🕐 最后同步时间: {status['last_sync'] or '未知'}")
            
            return status
            
        except Exception as e:
            print(f"❌ 获取系统状态失败: {e}")
            return {}
    
    def run_full_integration(self):
        """运行完整的数据整合"""
        print("🚀 开始完整数据整合...")
        print("=" * 60)
        
        # 测试连接
        connections = self.test_connections()
        if not all(connections.values()):
            print("❌ 连接测试失败，无法继续")
            return False
        
        # 同步股票数据
        sync_success = self.sync_stock_data()
        
        # 处理推送数据
        push_success = self.process_push_data_files()
        
        # 获取系统状态
        status = self.get_system_status()
        
        # 总结
        print("\n" + "=" * 60)
        print("📋 数据整合结果总结:")
        print(f"连接测试: {'✅ 通过' if all(connections.values()) else '❌ 失败'}")
        print(f"数据同步: {'✅ 成功' if sync_success else '❌ 失败'}")
        print(f"推送处理: {'✅ 成功' if push_success else '❌ 失败'}")
        
        overall_success = all(connections.values()) and sync_success and push_success
        
        if overall_success:
            print("🎉 数据整合完全成功！系统运行正常！")
        else:
            print("⚠️ 部分功能正常，系统基本可用")
        
        print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return overall_success

def main():
    """主函数"""
    integration = WorkingDataIntegration()
    success = integration.run_full_integration()
    
    if success:
        print("\n🎯 下一步建议:")
        print("1. 设置定时任务每5分钟运行一次数据同步")
        print("2. 在Supabase中创建完整的表结构以获得更好的性能")
        print("3. 部署数据同步API到Cloudflare Pages")
    else:
        print("\n🔧 需要修复的问题:")
        print("1. 检查网络连接稳定性")
        print("2. 验证API密钥和权限")
        print("3. 确认数据库表结构")

if __name__ == '__main__':
    main()
