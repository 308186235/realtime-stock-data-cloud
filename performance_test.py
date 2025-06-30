"""
Supabase集成性能测试
"""
import asyncio
import time
import statistics
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import uuid

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.adapters.simple_database_adapter import simple_db_adapter

class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.db = simple_db_adapter
        self.test_data = {
            'users': [],
            'stocks': [],
            'portfolios': [],
            'holdings': [],
            'transactions': []
        }
    
    def measure_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def test_batch_create_users(self, count=100):
        """批量创建用户性能测试"""
        print(f"\n📊 批量创建 {count} 个用户...")
        
        times = []
        for i in range(count):
            user_data = {
                'id': str(uuid.uuid4()),
                'username': f'perf_user_{i}',
                'email': f'perf_user_{i}@example.com',
                'display_name': f'性能测试用户{i}',
                'is_active': True
            }
            
            result, exec_time = self.measure_time(self.db.create_user, user_data)
            times.append(exec_time)
            
            if result['success']:
                self.test_data['users'].append(result['data'])
            
            if (i + 1) % 20 == 0:
                print(f"  已创建 {i + 1} 个用户...")
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"✅ 用户创建完成:")
        print(f"   - 平均时间: {avg_time:.3f}秒")
        print(f"   - 最快时间: {min_time:.3f}秒")
        print(f"   - 最慢时间: {max_time:.3f}秒")
        print(f"   - 总时间: {sum(times):.3f}秒")
        
        return times
    
    def test_batch_create_stocks(self, count=50):
        """批量创建股票性能测试"""
        print(f"\n📈 批量创建 {count} 只股票...")
        
        times = []
        sectors = ['金融', '科技', '消费', '医药', '能源']
        markets = ['SH', 'SZ']
        
        for i in range(count):
            stock_data = {
                'code': f'{i:06d}',
                'name': f'测试股票{i}',
                'market': markets[i % 2],
                'sector': sectors[i % len(sectors)],
                'industry': f'行业{i % 10}'
            }
            
            result, exec_time = self.measure_time(self.db.create_stock, stock_data)
            times.append(exec_time)
            
            if result['success']:
                self.test_data['stocks'].append(result['data'])
            
            if (i + 1) % 10 == 0:
                print(f"  已创建 {i + 1} 只股票...")
        
        avg_time = statistics.mean(times)
        print(f"✅ 股票创建完成:")
        print(f"   - 平均时间: {avg_time:.3f}秒")
        print(f"   - 总时间: {sum(times):.3f}秒")
        
        return times
    
    def test_batch_create_portfolios(self, count=20):
        """批量创建投资组合性能测试"""
        print(f"\n💼 批量创建 {count} 个投资组合...")
        
        if not self.test_data['users']:
            print("❌ 需要先创建用户")
            return []
        
        times = []
        for i in range(count):
            user = self.test_data['users'][i % len(self.test_data['users'])]
            portfolio_data = {
                'user_id': user['id'],
                'name': f'性能测试组合{i}',
                'cash': 1000000.0 + i * 100000,
                'total_value': 1000000.0 + i * 100000,
                'stock_value': 0.0,
                'is_default': i == 0
            }
            
            result, exec_time = self.measure_time(self.db.create_portfolio, portfolio_data)
            times.append(exec_time)
            
            if result['success']:
                self.test_data['portfolios'].append(result['data'])
        
        avg_time = statistics.mean(times)
        print(f"✅ 投资组合创建完成:")
        print(f"   - 平均时间: {avg_time:.3f}秒")
        print(f"   - 总时间: {sum(times):.3f}秒")
        
        return times
    
    def test_batch_create_holdings(self, count=100):
        """批量创建持仓性能测试"""
        print(f"\n🛒 批量创建 {count} 个持仓...")
        
        if not self.test_data['portfolios'] or not self.test_data['stocks']:
            print("❌ 需要先创建投资组合和股票")
            return []
        
        times = []
        for i in range(count):
            portfolio = self.test_data['portfolios'][i % len(self.test_data['portfolios'])]
            stock = self.test_data['stocks'][i % len(self.test_data['stocks'])]
            
            holding_data = {
                'portfolio_id': portfolio['id'],
                'stock_code': stock['code'],
                'shares': (i + 1) * 100,
                'cost_price': 10.0 + (i % 50),
                'current_price': 10.0 + (i % 50)
            }
            
            result, exec_time = self.measure_time(self.db.create_holding, holding_data)
            times.append(exec_time)
            
            if result['success']:
                self.test_data['holdings'].append(result['data'])
            
            if (i + 1) % 20 == 0:
                print(f"  已创建 {i + 1} 个持仓...")
        
        avg_time = statistics.mean(times)
        print(f"✅ 持仓创建完成:")
        print(f"   - 平均时间: {avg_time:.3f}秒")
        print(f"   - 总时间: {sum(times):.3f}秒")
        
        return times
    
    def test_query_performance(self):
        """查询性能测试"""
        print(f"\n🔍 查询性能测试...")
        
        # 测试获取所有用户
        result, exec_time = self.measure_time(self.db.get_users)
        print(f"✅ 获取所有用户: {exec_time:.3f}秒 (共{len(result['data'])}个)")
        
        # 测试获取所有股票
        result, exec_time = self.measure_time(self.db.get_stocks)
        print(f"✅ 获取所有股票: {exec_time:.3f}秒 (共{len(result['data'])}只)")
        
        # 测试获取所有投资组合
        result, exec_time = self.measure_time(self.db.get_portfolios)
        print(f"✅ 获取所有投资组合: {exec_time:.3f}秒 (共{len(result['data'])}个)")
        
        # 测试获取单个投资组合详情
        if self.test_data['portfolios']:
            portfolio_id = self.test_data['portfolios'][0]['id']
            result, exec_time = self.measure_time(self.db.get_portfolio, portfolio_id)
            print(f"✅ 获取投资组合详情: {exec_time:.3f}秒")
        
        # 测试获取持仓列表
        if self.test_data['portfolios']:
            portfolio_id = self.test_data['portfolios'][0]['id']
            result, exec_time = self.measure_time(self.db.get_holdings, portfolio_id)
            print(f"✅ 获取持仓列表: {exec_time:.3f}秒 (共{len(result['data'])}个)")
    
    def test_concurrent_operations(self, concurrent_count=10):
        """并发操作测试"""
        print(f"\n⚡ 并发操作测试 ({concurrent_count} 个并发)...")
        
        def create_user_task(i):
            user_data = {
                'id': str(uuid.uuid4()),
                'username': f'concurrent_user_{i}',
                'email': f'concurrent_user_{i}@example.com',
                'display_name': f'并发测试用户{i}',
                'is_active': True
            }
            start_time = time.time()
            result = self.db.create_user(user_data)
            end_time = time.time()
            return result, end_time - start_time
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(create_user_task, i) for i in range(concurrent_count)]
            results = [future.result() for future in futures]
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_count = sum(1 for result, _ in results if result['success'])
        avg_individual_time = statistics.mean([exec_time for _, exec_time in results])
        
        print(f"✅ 并发操作完成:")
        print(f"   - 总时间: {total_time:.3f}秒")
        print(f"   - 成功数量: {successful_count}/{concurrent_count}")
        print(f"   - 平均单个操作时间: {avg_individual_time:.3f}秒")
        print(f"   - 并发效率: {(avg_individual_time * concurrent_count / total_time):.2f}x")
    
    def test_data_size_impact(self):
        """数据量对性能影响测试"""
        print(f"\n📊 数据量对性能影响测试...")
        
        # 测试不同数据量下的查询性能
        data_sizes = [10, 50, 100, 200]
        
        for size in data_sizes:
            # 创建测试数据
            print(f"\n  测试数据量: {size}")
            
            # 创建用户
            users = []
            start_time = time.time()
            for i in range(size):
                user_data = {
                    'id': str(uuid.uuid4()),
                    'username': f'size_test_user_{size}_{i}',
                    'email': f'size_test_user_{size}_{i}@example.com',
                    'display_name': f'数据量测试用户{i}',
                    'is_active': True
                }
                result = self.db.create_user(user_data)
                if result['success']:
                    users.append(result['data'])
            create_time = time.time() - start_time
            
            # 查询性能测试
            start_time = time.time()
            result = self.db.get_users()
            query_time = time.time() - start_time
            
            print(f"    创建时间: {create_time:.3f}秒")
            print(f"    查询时间: {query_time:.3f}秒")
            print(f"    查询到的用户数: {len(result['data'])}")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print(f"\n🧹 清理测试数据...")
        
        start_time = time.time()
        result = self.db.cleanup_test_data()
        end_time = time.time()
        
        if result['success']:
            print(f"✅ 清理完成: {result['data']['cleaned_count']} 条记录")
            print(f"   清理时间: {end_time - start_time:.3f}秒")
        else:
            print(f"❌ 清理失败: {result['error']}")
    
    def run_full_performance_test(self):
        """运行完整性能测试"""
        print("🚀 开始完整性能测试...")
        print("="*60)
        
        total_start_time = time.time()
        
        try:
            # 1. 批量创建测试
            self.test_batch_create_users(50)
            self.test_batch_create_stocks(30)
            self.test_batch_create_portfolios(10)
            self.test_batch_create_holdings(50)
            
            # 2. 查询性能测试
            self.test_query_performance()
            
            # 3. 并发操作测试
            self.test_concurrent_operations(5)
            
            # 4. 数据量影响测试
            self.test_data_size_impact()
            
            total_end_time = time.time()
            total_time = total_end_time - total_start_time
            
            print("\n" + "="*60)
            print("🎉 性能测试完成！")
            print(f"📊 总测试时间: {total_time:.3f}秒")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 性能测试过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理测试数据
            self.cleanup_test_data()

def main():
    """主函数"""
    test = PerformanceTest()
    test.run_full_performance_test()

if __name__ == "__main__":
    main()
