"""
茶股帮数据源集成脚本
将茶股帮实时数据接收器集成到股票交易系统中
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chagubang_receiver import ChaguBangReceiver, start_chagubang_service, get_service_stats

class ChaguBangIntegrator:
    """茶股帮数据集成器"""
    
    def __init__(self, token: str = ''):
        """
        初始化集成器
        
        Args:
            token: 茶股帮API token
        """
        self.token = token
        self.receiver: Optional[ChaguBangReceiver] = None
        self.running = False
        
        # 数据存储
        self.stock_data_cache: Dict[str, Dict] = {}
        self.data_callbacks = []
        
        # 统计信息
        self.integration_stats = {
            'start_time': None,
            'total_received': 0,
            'unique_stocks': 0,
            'last_update': None,
            'status': 'stopped'
        }
        
        # 配置信息
        self.config = {
            'host': 'l1.chagubang.com',
            'port': 6380,
            'token': token,
            'auto_restart': True,
            'max_cache_size': 10000,
            'log_interval': 100  # 每100条数据记录一次日志
        }
    
    def add_data_callback(self, callback):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)
    
    def _on_stock_data_received(self, stock_data: Dict[str, Any]):
        """处理接收到的股票数据"""
        try:
            # 更新缓存
            code = stock_data['stock_code']
            self.stock_data_cache[code] = stock_data
            
            # 限制缓存大小
            if len(self.stock_data_cache) > self.config['max_cache_size']:
                # 移除最旧的数据
                oldest_code = min(self.stock_data_cache.keys(), 
                                key=lambda k: self.stock_data_cache[k].get('update_time', ''))
                del self.stock_data_cache[oldest_code]
            
            # 更新统计
            self.integration_stats['total_received'] += 1
            self.integration_stats['unique_stocks'] = len(self.stock_data_cache)
            self.integration_stats['last_update'] = datetime.now().isoformat()
            
            # 调用回调函数
            for callback in self.data_callbacks:
                try:
                    callback(stock_data)
                except Exception as e:
                    print(f"回调函数执行失败: {e}")
            
            # 定期日志
            if self.integration_stats['total_received'] % self.config['log_interval'] == 0:
                print(f"📊 茶股帮数据统计: 已接收 {self.integration_stats['total_received']} 条, "
                      f"股票数量 {self.integration_stats['unique_stocks']}")
                
        except Exception as e:
            print(f"处理股票数据失败: {e}")
    
    def start_integration(self) -> bool:
        """启动茶股帮数据集成"""
        try:
            print("🚀 启动茶股帮数据集成...")
            print(f"服务器: {self.config['host']}:{self.config['port']}")
            print(f"Token: {self.config['token'] if self.config['token'] else '空token'}")
            
            # 创建接收器
            self.receiver = ChaguBangReceiver(
                host=self.config['host'],
                port=self.config['port'],
                token=self.config['token']
            )
            
            # 添加数据回调
            self.receiver.add_data_callback(self._on_stock_data_received)
            
            # 启动接收线程
            self.thread = threading.Thread(target=self.receiver.start_receiving, daemon=True)
            self.thread.start()
            
            # 更新状态
            self.running = True
            self.integration_stats['status'] = 'running'
            self.integration_stats['start_time'] = datetime.now().isoformat()
            
            print("✅ 茶股帮数据集成启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 启动茶股帮数据集成失败: {e}")
            return False
    
    def stop_integration(self):
        """停止茶股帮数据集成"""
        print("⏹️ 停止茶股帮数据集成...")
        
        self.running = False
        self.integration_stats['status'] = 'stopped'
        
        if self.receiver:
            self.receiver.stop_receiving()
        
        print("✅ 茶股帮数据集成已停止")
    
    def get_stock_data(self, stock_code: str = None) -> Dict:
        """获取股票数据"""
        if stock_code:
            return self.stock_data_cache.get(stock_code, {})
        return self.stock_data_cache.copy()
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        stats = self.integration_stats.copy()
        
        # 添加接收器统计
        if self.receiver:
            receiver_stats = self.receiver.get_stats()
            stats.update({
                'receiver_status': receiver_stats.get('connection_status', 'unknown'),
                'receiver_errors': receiver_stats.get('error_count', 0),
                'queue_size': receiver_stats.get('queue_size', 0)
            })
        
        return stats
    
    def is_running(self) -> bool:
        """检查集成是否运行中"""
        return self.running and (self.receiver and self.receiver.is_connected())
    
    def export_data_to_json(self, filename: str = None) -> str:
        """导出数据到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chagubang_data_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'stats': self.get_integration_stats(),
            'stock_data': self.stock_data_cache
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 数据已导出到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 导出数据失败: {e}")
            return ""


def create_trading_system_integration(token: str = '') -> ChaguBangIntegrator:
    """为交易系统创建茶股帮集成"""
    integrator = ChaguBangIntegrator(token=token)
    
    # 添加交易系统专用的数据处理回调
    def trading_system_callback(stock_data):
        """交易系统数据处理回调"""
        # 这里可以添加特定的交易逻辑
        # 例如：价格异动检测、交易信号生成等
        
        code = stock_data['stock_code']
        price = stock_data['last_price']
        change_pct = stock_data['change_pct']
        
        # 示例：检测大幅波动
        if abs(change_pct) > 5.0:  # 涨跌幅超过5%
            print(f"🚨 价格异动提醒: {code} {stock_data.get('stock_name', '')} "
                  f"涨跌幅: {change_pct:+.2f}% 价格: {price:.2f}")
    
    integrator.add_data_callback(trading_system_callback)
    return integrator


def main():
    """主函数 - 演示茶股帮集成使用"""
    print("🎯 茶股帮数据源集成演示")
    print("=" * 50)
    
    # 从环境变量或命令行获取token
    token = os.environ.get('CHAGUBANG_TOKEN', '')
    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    print(f"使用Token: {token if token else '空token'}")
    
    # 创建集成器
    integrator = create_trading_system_integration(token=token)
    
    try:
        # 启动集成
        if integrator.start_integration():
            print("\n⏱️ 运行60秒演示...")
            
            # 运行60秒
            for i in range(60):
                time.sleep(1)
                
                # 每10秒显示统计
                if (i + 1) % 10 == 0:
                    stats = integrator.get_integration_stats()
                    print(f"\n📊 运行 {i+1} 秒统计:")
                    print(f"   接收数据: {stats['total_received']} 条")
                    print(f"   股票数量: {stats['unique_stocks']} 只")
                    print(f"   连接状态: {stats.get('receiver_status', 'unknown')}")
            
            # 显示最终统计
            final_stats = integrator.get_integration_stats()
            print(f"\n🎯 最终统计:")
            print(f"   总接收数据: {final_stats['total_received']} 条")
            print(f"   不同股票: {final_stats['unique_stocks']} 只")
            print(f"   错误次数: {final_stats.get('receiver_errors', 0)} 次")
            
            # 导出数据
            if final_stats['total_received'] > 0:
                export_file = integrator.export_data_to_json()
                if export_file:
                    print(f"✅ 演示数据已保存到: {export_file}")
            
        else:
            print("❌ 集成启动失败")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        integrator.stop_integration()
    
    print("\n✅ 茶股帮集成演示完成")


if __name__ == "__main__":
    main()
