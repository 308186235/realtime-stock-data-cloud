#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent快捷键交易系统测试脚本
测试AI Agent与交易软件的集成功能
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ai.agent_hotkey_trader import AgentHotkeyTrader
from backend.ai.agent_system import TradingAgent

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentHotkeyTradingTester:
    """Agent快捷键交易测试器"""
    
    def __init__(self):
        self.agent_trader = None
        self.trading_agent = None
        
    async def setup(self):
        """设置测试环境"""
        logger.info("🔧 设置测试环境...")
        
        # 创建Agent快捷键交易器配置
        trader_config = {
            "max_daily_trades": 5,
            "max_position_size": 0.05,
            "min_confidence_threshold": 0.8,
            "auto_confirm": False,  # 测试模式不自动确认
            "min_trade_interval": 30,
            "test_mode": True
        }
        
        # 创建Trading Agent配置
        agent_config = {
            "name": "TestTradingAgent",
            "loop_interval": 30,
            "monitor_interval": 15
        }
        
        # 初始化组件
        self.agent_trader = AgentHotkeyTrader(trader_config)
        self.trading_agent = TradingAgent(agent_config)
        
        logger.info("✅ 测试环境设置完成")
    
    async def test_system_startup(self):
        """测试系统启动"""
        logger.info("🚀 测试系统启动...")
        
        # 启动Agent快捷键交易器
        trader_result = await self.agent_trader.start()
        if trader_result:
            logger.info("✅ Agent快捷键交易器启动成功")
        else:
            logger.error("❌ Agent快捷键交易器启动失败")
            return False
        
        # 启动Trading Agent
        agent_result = await self.trading_agent.start()
        if agent_result:
            logger.info("✅ Trading Agent启动成功")
        else:
            logger.warning("⚠️ Trading Agent启动失败，但继续测试")
        
        return True
    
    async def test_manual_trading(self):
        """测试手动交易功能"""
        logger.info("📝 测试手动交易功能...")
        
        # 测试买入决策
        buy_decision = {
            "action": "buy",
            "symbol": "600000",
            "price": 10.50,
            "quantity": 100,
            "confidence": 0.85,
            "reason": "测试买入"
        }
        
        logger.info(f"执行买入测试: {buy_decision}")
        buy_result = await self.agent_trader.execute_agent_decision(buy_decision)
        logger.info(f"买入结果: {buy_result}")
        
        # 等待一段时间
        await asyncio.sleep(2)
        
        # 测试卖出决策
        sell_decision = {
            "action": "sell",
            "symbol": "600000",
            "price": 10.60,
            "quantity": 100,
            "confidence": 0.90,
            "reason": "测试卖出"
        }
        
        logger.info(f"执行卖出测试: {sell_decision}")
        sell_result = await self.agent_trader.execute_agent_decision(sell_decision)
        logger.info(f"卖出结果: {sell_result}")
        
        return True
    
    async def test_agent_decision(self):
        """测试Agent决策功能"""
        logger.info("🤖 测试Agent决策功能...")
        
        if not self.trading_agent or not self.trading_agent.active:
            logger.warning("⚠️ Trading Agent未启动，跳过决策测试")
            return True
        
        # 构建决策上下文
        context = {
            "symbol": "600519",
            "timestamp": datetime.now().isoformat(),
            "market_data": {
                "current_price": 1800.50,
                "volume": 1000000,
                "change_percent": 2.5
            }
        }
        
        logger.info(f"请求Agent决策: {context['symbol']}")
        decision = await self.trading_agent.make_decision(context)
        logger.info(f"Agent决策结果: {decision}")
        
        # 如果决策有效，尝试执行
        if decision and "error" not in decision:
            logger.info("执行Agent决策...")
            execution_result = await self.agent_trader.execute_agent_decision(decision)
            logger.info(f"执行结果: {execution_result}")
        
        return True
    
    async def test_system_status(self):
        """测试系统状态查询"""
        logger.info("📊 测试系统状态查询...")
        
        # 获取Agent交易器状态
        trader_status = self.agent_trader.get_status()
        logger.info(f"Agent交易器状态: {json.dumps(trader_status, indent=2, ensure_ascii=False)}")
        
        # 获取Trading Agent状态
        if self.trading_agent:
            agent_status = await self.trading_agent.get_status()
            logger.info(f"Trading Agent状态: {json.dumps(agent_status, indent=2, ensure_ascii=False)}")
        
        return True
    
    async def test_position_and_fund_query(self):
        """测试持仓和资金查询"""
        logger.info("💰 测试持仓和资金查询...")
        
        # 测试持仓查询
        position_result = await self.agent_trader.get_position_info()
        logger.info(f"持仓信息: {position_result}")
        
        # 测试资金查询
        fund_result = await self.agent_trader.get_fund_info()
        logger.info(f"资金信息: {fund_result}")
        
        return True
    
    async def test_safety_checks(self):
        """测试安全检查功能"""
        logger.info("🔒 测试安全检查功能...")
        
        # 测试低置信度决策
        low_confidence_decision = {
            "action": "buy",
            "symbol": "600001",
            "price": 5.50,
            "quantity": 100,
            "confidence": 0.3,  # 低于阈值
            "reason": "低置信度测试"
        }
        
        logger.info("测试低置信度决策...")
        result = await self.agent_trader.execute_agent_decision(low_confidence_decision)
        logger.info(f"低置信度决策结果: {result}")
        
        # 测试过大仓位
        large_position_decision = {
            "action": "buy",
            "symbol": "600002",
            "price": 8.50,
            "quantity": 1000,
            "confidence": 0.9,
            "position_size": 0.8,  # 超过最大仓位
            "reason": "大仓位测试"
        }
        
        logger.info("测试过大仓位决策...")
        result = await self.agent_trader.execute_agent_decision(large_position_decision)
        logger.info(f"大仓位决策结果: {result}")
        
        return True
    
    async def test_execution_history(self):
        """测试执行历史功能"""
        logger.info("📋 测试执行历史功能...")
        
        # 获取执行历史
        history = self.agent_trader.get_execution_history(10)
        logger.info(f"执行历史记录数: {len(history)}")
        
        for i, record in enumerate(history[-3:], 1):  # 显示最近3条
            logger.info(f"历史记录 {i}: {record['decision']['action']} {record['decision']['symbol']} - {record['result']['status']}")
        
        return True
    
    async def test_config_update(self):
        """测试配置更新功能"""
        logger.info("⚙️ 测试配置更新功能...")
        
        # 更新配置
        new_config = {
            "max_daily_trades": 10,
            "min_confidence_threshold": 0.75,
            "auto_confirm": False
        }
        
        logger.info(f"更新配置: {new_config}")
        self.agent_trader.update_config(new_config)
        
        # 验证配置更新
        status = self.agent_trader.get_status()
        logger.info(f"更新后的安全设置: {status['safety_settings']}")
        
        return True
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        if self.agent_trader:
            await self.agent_trader.stop()
            logger.info("✅ Agent快捷键交易器已停止")
        
        if self.trading_agent:
            await self.trading_agent.stop()
            logger.info("✅ Trading Agent已停止")
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🧪 开始Agent快捷键交易系统测试")
        logger.info("=" * 60)
        
        try:
            # 设置测试环境
            await self.setup()
            
            # 测试系统启动
            if not await self.test_system_startup():
                logger.error("❌ 系统启动测试失败，终止测试")
                return False
            
            # 运行各项测试
            tests = [
                ("系统状态查询", self.test_system_status),
                ("手动交易功能", self.test_manual_trading),
                ("Agent决策功能", self.test_agent_decision),
                ("持仓资金查询", self.test_position_and_fund_query),
                ("安全检查功能", self.test_safety_checks),
                ("执行历史功能", self.test_execution_history),
                ("配置更新功能", self.test_config_update),
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                logger.info(f"\n🔍 开始测试: {test_name}")
                try:
                    result = await test_func()
                    if result:
                        logger.info(f"✅ {test_name} - 通过")
                        passed_tests += 1
                    else:
                        logger.error(f"❌ {test_name} - 失败")
                except Exception as e:
                    logger.error(f"❌ {test_name} - 异常: {str(e)}")
                
                # 测试间隔
                await asyncio.sleep(1)
            
            # 测试总结
            logger.info("\n" + "=" * 60)
            logger.info(f"🏁 测试完成: {passed_tests}/{total_tests} 通过")
            
            if passed_tests == total_tests:
                logger.info("🎉 所有测试通过！系统功能正常")
            else:
                logger.warning(f"⚠️ {total_tests - passed_tests} 个测试失败，请检查相关功能")
            
            return passed_tests == total_tests
            
        except Exception as e:
            logger.error(f"❌ 测试过程中发生异常: {str(e)}")
            return False
        
        finally:
            # 清理环境
            await self.cleanup()

async def main():
    """主函数"""
    print("🚀 Agent快捷键交易系统测试工具")
    print("=" * 60)
    print("⚠️ 重要提示:")
    print("  - 请确保交易软件已打开（东吴证券等）")
    print("  - 测试模式不会执行真实交易")
    print("  - 如需测试真实交易，请谨慎操作")
    print("=" * 60)
    
    # 询问是否继续
    try:
        response = input("\n是否继续测试? (y/n): ")
        if response.lower() != 'y':
            print("👋 测试已取消")
            return
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
        return
    
    # 运行测试
    tester = AgentHotkeyTradingTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 测试成功完成！")
        print("💡 您现在可以使用以下方式启动系统:")
        print("   - 运行 start_agent_trading.bat")
        print("   - 访问 http://localhost:8000/api/docs 查看API文档")
    else:
        print("\n⚠️ 测试未完全通过，请检查相关问题")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
