"""
最终增强版交易Agent - 集成所有安全和监控功能
"""

from auto_cleanup_trading_agent import AutoCleanupTradingAgent
from system_enhancements import *
import time
import threading
from datetime import datetime

class EnhancedSecureTradingAgent(AutoCleanupTradingAgent):
    def __init__(self):
        super().__init__()
        
        # 集成增强功能
        self.retry_handler = NetworkRetryHandler()
        self.data_validator = DataValidator()
        self.health_checker = SystemHealthChecker()
        self.security_manager = SecurityManager()
        
        # 监控线程
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # 性能统计
        self.performance_stats = {
            "trades_executed": 0,
            "errors_occurred": 0,
            "avg_execution_time": 0,
            "last_health_check": None
        }
    
    @performance_monitor
    def initialize_trading_day(self):
        """增强版交易日初始化"""
        print(" 最终增强版智能交易Agent - 交易日初始化")
        print("=" * 70)
        
        # 系统健康检查
        print(" 执行系统健康检查...")
        health_status = self.health_checker.check_system_health()
        
        if not all([health_status["memory"], health_status["disk_space"]]):
            logger.error("系统健康检查失败，无法启动交易")
            return False
        
        if not health_status["trading_software"]:
            logger.warning("交易软件未检测到，但继续启动")
        
        # 启动监控线程
        self.start_monitoring()
        
        # 调用父类初始化
        try:
            return super().initialize_trading_day()
        except Exception as e:
            logger.error(f"交易日初始化失败: {e}")
            raise TradingSystemException(f"初始化失败: {e}", "INIT_FAILED")
    
    @performance_monitor
    def sync_virtual_from_export(self):
        """增强版虚拟持仓同步"""
        try:
            # 调用父类方法
            super().sync_virtual_from_export()
            
            # 验证同步后的数据
            self.validate_virtual_holdings()
            
        except Exception as e:
            logger.error(f"虚拟持仓同步失败: {e}")
            raise TradingSystemException(f"持仓同步失败: {e}", "SYNC_FAILED")
    
    def validate_virtual_holdings(self):
        """验证虚拟持仓数据"""
        try:
            # 验证现金余额
            if self.virtual_cash < 0:
                raise ValueError(f"虚拟现金余额异常: {self.virtual_cash}")
            
            # 验证持仓数据
            for code, holding in self.virtual_holdings.items():
                if holding['quantity'] < 0:
                    raise ValueError(f"持仓数量异常: {code} {holding['quantity']}")
                
                if holding['cost_price'] <= 0:
                    raise ValueError(f"成本价异常: {code} {holding['cost_price']}")
            
            logger.debug("虚拟持仓数据验证通过")
            
        except Exception as e:
            logger.error(f"虚拟持仓数据验证失败: {e}")
            raise TradingSystemException(f"持仓数据验证失败: {e}", "DATA_VALIDATION_FAILED")
    
    @performance_monitor
    async def execute_trade_with_priority(self, trade_type, code, quantity, price=None):
        """增强版交易执行"""
        try:
            # 验证交易参数
            actual_price = price if price else 0
            trade_amount = quantity * actual_price if actual_price > 0 else quantity * 10  # 估算金额
            
            self.data_validator.validate_trade_params(code, quantity, actual_price or 10)
            
            # 安全检查
            self.security_manager.check_trade_limits(trade_amount)
            
            # 执行交易（带重试机制）
            async def trade_operation():
                return super(EnhancedSecureTradingAgent, self).execute_trade_with_priority(
                    trade_type, code, quantity, price
                )
            
            result = await self.retry_handler.retry_with_backoff(trade_operation)
            
            # 记录成功交易
            if result:
                self.security_manager.record_trade(trade_amount)
                self.performance_stats["trades_executed"] += 1
                logger.info(f" 交易执行成功: {trade_type} {code} {quantity}股")
            
            return result
            
        except TradingSystemException:
            raise
        except Exception as e:
            self.performance_stats["errors_occurred"] += 1
            logger.error(f"交易执行异常: {e}")
            raise TradingSystemException(f"交易执行失败: {e}", "TRADE_EXECUTION_FAILED")
    
    @performance_monitor
    def update_virtual_holdings_with_realtime_data(self):
        """增强版实时数据更新"""
        try:
            latest_stocks = get_stock_data()
            
            # 验证实时数据
            for code, stock_info in latest_stocks.items():
                try:
                    self.data_validator.validate_stock_data(stock_info)
                except Exception as e:
                    logger.warning(f"跳过无效股票数据 {code}: {e}")
                    continue
            
            # 调用父类方法
            super().update_virtual_holdings_with_realtime_data()
            
        except Exception as e:
            logger.error(f"实时数据更新失败: {e}")
            # 不抛出异常，允许系统继续运行
    
    def start_monitoring(self):
        """启动系统监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logger.info(" 系统监控已启动")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 每30秒执行一次健康检查
                health_status = self.health_checker.check_system_health()
                self.performance_stats["last_health_check"] = datetime.now()
                
                # 检查内存使用
                if not health_status["memory"]:
                    logger.warning("内存使用过高，建议重启系统")
                
                # 检查磁盘空间
                if not health_status["disk_space"]:
                    logger.warning("磁盘空间不足，清理文件")
                    self.cleanup_used_export_files()
                
                # 更新性能统计
                self._update_performance_stats()
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
            
            time.sleep(30)  # 30秒检查一次
    
    def _update_performance_stats(self):
        """更新性能统计"""
        try:
            # 计算错误率
            total_operations = self.performance_stats["trades_executed"] + self.performance_stats["errors_occurred"]
            error_rate = (self.performance_stats["errors_occurred"] / total_operations * 100) if total_operations > 0 else 0
            
            if error_rate > 10:  # 错误率超过10%
                logger.warning(f" 系统错误率过高: {error_rate:.2f}%")
            
            # 记录统计信息
            logger.debug(f"性能统计 - 交易:{self.performance_stats['trades_executed']} 错误:{self.performance_stats['errors_occurred']} 错误率:{error_rate:.2f}%")
            
        except Exception as e:
            logger.error(f"性能统计更新失败: {e}")
    
    def display_virtual_holdings(self):
        """增强版持仓显示"""
        try:
            # 调用父类方法
            super().display_virtual_holdings()
            
            # 显示系统状态
            if self.performance_stats["last_health_check"]:
                last_check = self.performance_stats["last_health_check"].strftime('%H:%M:%S')
                print(f" 系统状态: 最后检查 {last_check} | 交易 {self.performance_stats['trades_executed']} 笔 | 错误 {self.performance_stats['errors_occurred']} 次")
            
        except Exception as e:
            logger.error(f"持仓显示异常: {e}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info(" 系统监控已停止")
    
    def start_trading(self, host, port, token):
        """增强版交易启动"""
        try:
            print(" 启动最终增强版智能交易Agent")
            print(" 集成功能: 错误处理 | 性能监控 | 安全机制 | 数据验证")
            print("=" * 80)
            
            # 调用父类方法
            result = super().start_trading(host, port, token)
            
            return result
            
        except KeyboardInterrupt:
            print("\n 用户停止交易")
        except Exception as e:
            logger.error(f"交易系统启动失败: {e}")
            raise TradingSystemException(f"系统启动失败: {e}", "STARTUP_FAILED")
        finally:
            self.stop_monitoring()
            print(" 最终增强版交易Agent已安全停止")

# 使用示例
def main():
    agent = EnhancedSecureTradingAgent()
    
    # 配置股票数据服务器信息
    HOST = ''      # 填入实际服务器地址
    PORT = 0       # 填入实际端口
    TOKEN = ''     # 填入实际token
    
    if HOST and PORT and TOKEN:
        agent.start_trading(HOST, PORT, TOKEN)
    else:
        print(" 请先配置股票数据服务器信息")
        print(" 执行系统测试...")
        
        # 测试系统功能
        try:
            agent.initialize_trading_day()
            print(" 系统测试通过")
        except Exception as e:
            print(f" 系统测试失败: {e}")

if __name__ == "__main__":
    main()
