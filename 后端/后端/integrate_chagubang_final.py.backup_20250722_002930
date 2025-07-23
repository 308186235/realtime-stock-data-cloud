"""
茶股帮最终集成方案
基于MCP分析，将简化的茶股帮接收器集成到现有交易系统
"""

import os
import sys
import time
import json
import threading
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chagubang_simple_receiver import ChaguBangSimpleReceiver
from chagubang_token_manager import TokenManager

class ChaguBangFinalIntegration:
    """茶股帮最终集成器"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.receiver: Optional[ChaguBangSimpleReceiver] = None
        self.running = False
        
        # 数据存储
        self.stock_data_cache: Dict[str, Dict] = {}
        self.market_stats = {
            'total_stocks': 0,
            'rising_stocks': 0,
            'falling_stocks': 0,
            'avg_change': 0.0,
            'last_update': None
        }
        
        # 集成状态
        self.integration_status = {
            'chagubang_connected': False,
            'data_receiving': False,
            'last_data_time': None,
            'total_received': 0,
            'error_count': 0
        }
    
    def initialize(self) -> bool:
        """初始化集成"""
        print("🚀 初始化茶股帮最终集成...")
        
        # 获取最佳Token
        best_token = self.token_manager.get_best_token()
        if not best_token:
            print("⚠️ 没有可用Token，将使用空Token测试连接")
            best_token = ''
        
        # 创建简化接收器
        self.receiver = ChaguBangSimpleReceiver(token=best_token)
        
        # 添加数据处理回调
        self.receiver.add_data_callback(self._process_stock_data)
        
        print(f"✅ 茶股帮集成初始化完成")
        print(f"   服务器: l1.chagubang.com:6380")
        print(f"   Token: {best_token[:15] + '...' if best_token else '空Token'}")
        
        return True
    
    def _process_stock_data(self, stock_data: Dict[str, Any]):
        """处理接收到的股票数据"""
        try:
            code = stock_data['stock_code']
            
            # 更新缓存
            self.stock_data_cache[code] = {
                **stock_data,
                'received_time': datetime.now().isoformat(),
                'integration_source': 'chagubang_final'
            }
            
            # 更新集成状态
            self.integration_status['data_receiving'] = True
            self.integration_status['last_data_time'] = datetime.now().isoformat()
            self.integration_status['total_received'] += 1
            
            # 更新市场统计
            self._update_market_stats()
            
            # 输出关键数据（每100条输出一次）
            if self.integration_status['total_received'] % 100 == 0:
                print(f"📊 已接收 {self.integration_status['total_received']} 条数据，"
                      f"股票数量: {len(self.stock_data_cache)}")
            
            # 检测异动股票
            if abs(stock_data.get('change_pct', 0)) > 5.0:
                print(f"🚨 异动股票: {code} {stock_data.get('stock_name', '')} "
                      f"涨跌: {stock_data['change_pct']:+.2f}% "
                      f"价格: {stock_data['last_price']:.2f}")
                
        except Exception as e:
            print(f"❌ 处理股票数据失败: {e}")
            self.integration_status['error_count'] += 1
    
    def _update_market_stats(self):
        """更新市场统计"""
        try:
            if not self.stock_data_cache:
                return
            
            stocks = list(self.stock_data_cache.values())
            changes = [s.get('change_pct', 0) for s in stocks]
            
            self.market_stats = {
                'total_stocks': len(stocks),
                'rising_stocks': len([c for c in changes if c > 0]),
                'falling_stocks': len([c for c in changes if c < 0]),
                'avg_change': sum(changes) / len(changes) if changes else 0.0,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 更新市场统计失败: {e}")
    
    def start_integration(self) -> bool:
        """启动集成"""
        if not self.receiver:
            print("❌ 接收器未初始化")
            return False
        
        print("🚀 启动茶股帮数据集成...")
        
        # 启动接收线程
        self.thread = threading.Thread(target=self.receiver.start_receiving, daemon=True)
        self.thread.start()
        
        # 等待连接建立
        time.sleep(3)
        
        # 检查连接状态
        if self.receiver.is_connected():
            self.integration_status['chagubang_connected'] = True
            print("✅ 茶股帮连接成功")
            self.running = True
            return True
        else:
            print("❌ 茶股帮连接失败")
            return False
    
    def stop_integration(self):
        """停止集成"""
        print("⏹️ 停止茶股帮集成...")
        
        self.running = False
        
        if self.receiver:
            self.receiver.stop_receiving()
        
        self.integration_status['chagubang_connected'] = False
        self.integration_status['data_receiving'] = False
        
        print("✅ 茶股帮集成已停止")
    
    def get_stock_data(self, stock_code: str = None) -> Dict:
        """获取股票数据 - API接口"""
        if stock_code:
            return self.stock_data_cache.get(stock_code, {})
        return self.stock_data_cache.copy()
    
    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览 - API接口"""
        return {
            **self.market_stats,
            'integration_status': self.integration_status
        }
    
    def get_hot_stocks(self, limit: int = 10) -> list:
        """获取热门股票 - API接口"""
        stocks = list(self.stock_data_cache.values())
        
        # 按涨跌幅排序
        hot_stocks = sorted(stocks, 
                           key=lambda x: abs(x.get('change_pct', 0)), 
                           reverse=True)
        
        return hot_stocks[:limit]
    
    def search_stocks(self, query: str, limit: int = 10) -> list:
        """搜索股票 - API接口"""
        results = []
        query_upper = query.upper()
        
        for stock_data in self.stock_data_cache.values():
            code = stock_data.get('stock_code', '').upper()
            name = stock_data.get('stock_name', '').upper()
            
            if query_upper in code or query_upper in name:
                results.append(stock_data)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """获取集成统计 - API接口"""
        stats = {
            'integration_status': self.integration_status,
            'market_stats': self.market_stats,
            'cache_size': len(self.stock_data_cache),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.receiver:
            receiver_stats = self.receiver.get_stats()
            stats['receiver_stats'] = receiver_stats
        
        return stats
    
    def export_data(self, filename: str = None) -> str:
        """导出数据"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chagubang_data_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'integration_stats': self.get_integration_stats(),
            'stock_data': self.stock_data_cache,
            'market_overview': self.get_market_overview()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 数据已导出到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 导出数据失败: {e}")
            return ""


# 全局集成实例
_integration: Optional[ChaguBangFinalIntegration] = None

def get_chagubang_integration() -> ChaguBangFinalIntegration:
    """获取全局集成实例"""
    global _integration
    
    if _integration is None:
        _integration = ChaguBangFinalIntegration()
        _integration.initialize()
    
    return _integration

def start_chagubang_integration() -> bool:
    """启动茶股帮集成"""
    integration = get_chagubang_integration()
    return integration.start_integration()

def stop_chagubang_integration():
    """停止茶股帮集成"""
    global _integration
    
    if _integration:
        _integration.stop_integration()

# API接口函数
def get_realtime_stock_data(stock_code: str = None) -> Dict:
    """获取实时股票数据"""
    integration = get_chagubang_integration()
    return integration.get_stock_data(stock_code)

def get_market_overview_data() -> Dict[str, Any]:
    """获取市场概览数据"""
    integration = get_chagubang_integration()
    return integration.get_market_overview()

def get_hot_stocks_data(limit: int = 10) -> list:
    """获取热门股票数据"""
    integration = get_chagubang_integration()
    return integration.get_hot_stocks(limit)

def search_stocks_data(query: str, limit: int = 10) -> list:
    """搜索股票数据"""
    integration = get_chagubang_integration()
    return integration.search_stocks(query, limit)

def get_integration_stats_data() -> Dict[str, Any]:
    """获取集成统计数据"""
    integration = get_chagubang_integration()
    return integration.get_integration_stats()


def main():
    """主函数 - 演示完整集成"""
    print("🎯 茶股帮最终集成演示")
    print("=" * 50)
    
    try:
        # 启动集成
        if start_chagubang_integration():
            print("\n⏱️ 运行60秒演示...")
            
            # 运行60秒
            for i in range(60):
                time.sleep(1)
                
                # 每10秒显示统计
                if (i + 1) % 10 == 0:
                    stats = get_integration_stats_data()
                    print(f"\n📊 运行 {i+1} 秒统计:")
                    print(f"   连接状态: {stats['integration_status']['chagubang_connected']}")
                    print(f"   接收数据: {stats['integration_status']['total_received']} 条")
                    print(f"   股票数量: {stats['cache_size']} 只")
                    print(f"   市场概览: 涨{stats['market_stats']['rising_stocks']}/"
                          f"跌{stats['market_stats']['falling_stocks']}/"
                          f"平均{stats['market_stats']['avg_change']:.2f}%")
            
            # 显示最终结果
            final_stats = get_integration_stats_data()
            print(f"\n🎯 最终结果:")
            print(f"   总接收数据: {final_stats['integration_status']['total_received']} 条")
            print(f"   不同股票: {final_stats['cache_size']} 只")
            print(f"   错误次数: {final_stats['integration_status']['error_count']} 次")
            
            # 导出数据
            if final_stats['cache_size'] > 0:
                integration = get_chagubang_integration()
                export_file = integration.export_data()
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
        stop_chagubang_integration()
    
    print("\n✅ 茶股帮最终集成演示完成")
    print("\n📋 使用方法:")
    print("from integrate_chagubang_final import *")
    print("start_chagubang_integration()")
    print("data = get_realtime_stock_data('000001')")
    print("overview = get_market_overview_data()")


if __name__ == "__main__":
    main()
