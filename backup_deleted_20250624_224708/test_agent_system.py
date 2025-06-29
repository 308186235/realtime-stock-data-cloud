import asyncio
import argparse
import json
import logging
import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import traceback

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AgentTester")

# 添加当前路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Agent模块
try:
    from backend.ai.agent_system import TradingAgent, AgentAPI
    from backend.ai.market_analyzer import MarketAnalyzer
    from backend.ai.decision_engine import DecisionEngine
    from backend.ai.risk_manager import RiskManager
    from backend.ai.strategy_fusion import StrategyFusion
except ImportError:
    logger.error("无法导入Agent模块，请确保正确安装了所有依赖")
    traceback.print_exc()
    sys.exit(1)

class AgentTester:
    """Agent系统测试工具"""
    
    def __init__(self, config_file=None):
        """初始化测试工具"""
        self.config = self._load_config(config_file)
        self.agent = None
        self.api = None
        
        logger.info("Agent测试工具初始化完成")
    
    def _load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            "agent": {
                "name": "TestTradingAgent",
                "loop_interval": 10,
                "monitor_interval": 5
            },
            "test": {
                "duration": 60,  # 测试持续时间（秒）
                "mock_data": True,  # 是否使用模拟数据
                "test_decisions": True,  # 是否测试决策功能
                "test_execution": False  # 是否测试执行功能
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置
                    default_config.update(loaded_config)
                logger.info(f"已加载配置文件: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        
        return default_config
    
    async def setup(self):
        """设置Agent系统"""
        try:
            # 创建Agent实例
            self.agent = TradingAgent(config=self.config["agent"])
            
            # 创建API接口
            self.api = AgentAPI(self.agent)
            
            logger.info("Agent系统设置完成")
            return True
        except Exception as e:
            logger.error(f"Agent系统设置失败: {str(e)}")
            traceback.print_exc()
            return False
    
    async def run_test(self):
        """运行测试"""
        try:
            logger.info("开始运行Agent测试...")
            
            # 启动Agent
            start_result = await self.agent.start()
            if not start_result:
                logger.error("Agent启动失败")
                return False
            
            logger.info("Agent已启动，开始测试...")
            
            # 获取Agent状态
            status = await self.agent.get_status()
            logger.info(f"Agent状态: active={status['active']}")
            
            # 测试决策功能
            if self.config["test"]["test_decisions"]:
                await self._test_decision_making()
            
            # 测试执行功能
            if self.config["test"]["test_execution"]:
                await self._test_execution()
            
            # 测试API接口
            await self._test_api()
            
            # 等待指定时间
            test_duration = self.config["test"]["duration"]
            if test_duration > 0:
                logger.info(f"测试运行中，将在{test_duration}秒后停止...")
                await asyncio.sleep(test_duration)
            
            # 停止Agent
            await self.agent.stop()
            logger.info("Agent已停止，测试完成")
            
            return True
        except Exception as e:
            logger.error(f"测试过程中出错: {str(e)}")
            traceback.print_exc()
            
            # 确保Agent停止
            if self.agent and self.agent.active:
                await self.agent.stop()
            
            return False
    
    async def _test_decision_making(self):
        """测试决策功能"""
        logger.info("测试决策功能...")
        
        # 生成模拟市场数据
        market_data = self._generate_mock_market_data()
        
        # 生成模拟投资组合状态
        portfolio_state = self._generate_mock_portfolio_state()
        
        # 创建决策上下文
        context = {
            "market_data": market_data,
            "portfolio_state": portfolio_state,
            "timestamp": datetime.now().isoformat(),
            "symbol": "AAPL"
        }
        
        # 请求决策
        decision = await self.agent.make_decision(context)
        
        # 检查决策结果
        if "error" in decision:
            logger.error(f"决策生成失败: {decision['error']}")
        else:
            logger.info(f"决策结果: action={decision['action']}, confidence={decision.get('confidence', 0):.2f}")
            logger.info(f"决策因素: {json.dumps(decision.get('factors', {}), indent=2)}")
        
        return decision
    
    async def _test_execution(self):
        """测试执行功能"""
        logger.info("测试执行功能...")
        
        # 创建模拟动作
        action = {
            "action": "buy",
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.25,
            "order_type": "market",
            "timestamp": datetime.now().isoformat()
        }
        
        # 执行动作
        result = await self.agent.execute_action(action)
        
        # 检查执行结果
        if "error" in result:
            logger.error(f"动作执行失败: {result['error']}")
        else:
            logger.info(f"执行结果: {json.dumps(result, indent=2)}")
        
        return result
    
    async def _test_api(self):
        """测试API接口"""
        logger.info("测试API接口...")
        
        # 测试状态请求
        status_request = {"action": "status"}
        status_response = await self.api.handle_request(status_request)
        logger.info(f"API状态响应: status={status_response.get('status')}")
        
        # 测试决策请求
        context = {"symbol": "MSFT", "timeframe": "1h"}
        decision_request = {"action": "decision", "context": context}
        decision_response = await self.api.handle_request(decision_request)
        
        if decision_response.get("status") == "success":
            decision = decision_response.get("decision", {})
            logger.info(f"API决策响应: action={decision.get('action')}, confidence={decision.get('confidence', 0):.2f}")
        else:
            logger.error(f"API决策请求失败: {decision_response.get('message', '')}")
        
        return True
    
    def _generate_mock_market_data(self):
        """生成模拟市场数据"""
        # 生成模拟价格数据
        n_days = 60
        dates = pd.date_range(end=datetime.now(), periods=n_days)
        
        # 生成随机价格
        np.random.seed(42)  # 设置随机种子以便重现
        
        # 生成带趋势的随机价格
        trend = np.linspace(0, 0.2, n_days)  # 上升趋势
        noise = np.random.normal(0, 0.01, n_days)  # 随机噪声
        returns = trend + noise
        
        # 计算价格
        price = 100 * (1 + returns).cumprod()
        
        # 生成OHLC数据
        high = price * (1 + np.random.uniform(0, 0.015, n_days))
        low = price * (1 - np.random.uniform(0, 0.015, n_days))
        open_price = price * (1 + np.random.uniform(-0.01, 0.01, n_days))
        
        # 生成交易量
        volume = np.random.normal(1000000, 200000, n_days)
        volume = np.abs(volume)
        
        # 转换为列表
        close_list = price.tolist()
        open_list = open_price.tolist()
        high_list = high.tolist()
        low_list = low.tolist()
        volume_list = volume.tolist()
        
        # 创建市场数据字典
        market_data = {
            "prices": {
                "close": close_list,
                "open": open_list,
                "high": high_list,
                "low": low_list,
                "volume": volume_list
            },
            "time_period": "1d",
            "symbol": "AAPL",
            "sentiment": {
                "score": 0.3,
                "source": "mock"
            },
            "liquidity": {
                "average_spread": 0.001,
                "volume": volume_list[-1],
                "turnover": volume_list[-1] * close_list[-1]
            }
        }
        
        logger.info(f"已生成模拟市场数据: {n_days}天, 当前价格: {close_list[-1]:.2f}")
        return market_data
    
    def _generate_mock_portfolio_state(self):
        """生成模拟投资组合状态"""
        portfolio_state = {
            "total_value": 100000.0,
            "cash_available": 25000.0,
            "open_positions": 3,
            "positions": [
                {
                    "symbol": "AAPL",
                    "quantity": 50,
                    "entry_price": 145.75,
                    "current_price": 150.25,
                    "value": 7512.5,
                    "unrealized_pnl": 225.0,
                    "unrealized_pnl_percent": 0.031,
                    "sector": "technology"
                },
                {
                    "symbol": "MSFT",
                    "quantity": 30,
                    "entry_price": 290.50,
                    "current_price": 305.25,
                    "value": 9157.5,
                    "unrealized_pnl": 442.5,
                    "unrealized_pnl_percent": 0.051,
                    "sector": "technology"
                },
                {
                    "symbol": "JNJ",
                    "quantity": 40,
                    "entry_price": 165.30,
                    "current_price": 160.75,
                    "value": 6430.0,
                    "unrealized_pnl": -182.0,
                    "unrealized_pnl_percent": -0.028,
                    "sector": "healthcare"
                }
            ],
            "allocation": {
                "technology": 0.55,
                "healthcare": 0.15,
                "cash": 0.30
            }
        }
        
        logger.info(f"已生成模拟投资组合状态: 总值={portfolio_state['total_value']:.2f}, 现金={portfolio_state['cash_available']:.2f}")
        return portfolio_state

async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='智能交易Agent系统测试工具')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--duration', type=int, help='测试持续时间（秒）')
    
    args = parser.parse_args()
    
    # 创建测试工具
    tester = AgentTester(args.config)
    
    # 如果指定了持续时间，覆盖配置
    if args.duration is not None:
        tester.config["test"]["duration"] = args.duration
    
    # 设置Agent系统
    setup_success = await tester.setup()
    if not setup_success:
        logger.error("Agent系统设置失败，测试终止")
        return 1
    
    # 运行测试
    test_success = await tester.run_test()
    
    if test_success:
        logger.info("Agent系统测试成功完成")
        return 0
    else:
        logger.error("Agent系统测试失败")
        return 1

if __name__ == "__main__":
    try:
        # 运行异步主函数
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"测试过程中发生未处理异常: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 