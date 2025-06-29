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
import time
import matplotlib.pyplot as plt
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LearningAgentTester")

# 添加当前路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Agent模块
try:
    from backend.ai.agent_system import TradingAgent
    from backend.ai.learning_manager import LearningManager
    from backend.ai.reinforcement_learning import DeepQLearner, FeatureExtractor
    from backend.ai.experience_memory import ExperienceMemory
except ImportError:
    logger.error("无法导入Agent模块，请确保正确安装了所有依赖")
    traceback.print_exc()
    sys.exit(1)

class LearningAgentTester:
    """智能交易Agent学习测试工具"""
    
    def __init__(self, config_file=None):
        """初始化测试工具"""
        self.config = self._load_config(config_file)
        self.agent = None
        self.learning_manager = None
        self.experience_memory = None
        self.feature_extractor = None
        self.dqn_learner = None
        
        # 测试数据
        self.test_data = None
        
        # 性能跟踪
        self.performance_history = []
        
        logger.info("学习Agent测试工具初始化完成")
    
    def _load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            "agent": {
                "name": "LearningTradingAgent",
                "loop_interval": 10,
                "monitor_interval": 5
            },
            "learning": {
                "experience_buffer_size": 1000,
                "learning_rate": 0.01,
                "batch_size": 64,
                "save_model_interval": 100  # 每100个交易后保存模型
            },
            "test": {
                "episodes": 100,  # 测试轮数
                "trades_per_episode": 20,  # 每轮交易数
                "use_market_data": True,  # 是否使用市场数据
                "market_data_file": "market_data.csv",  # 市场数据文件
                "plot_results": True  # 是否绘制结果图表
            },
            "rewards": {
                "win_trade": 1.0,  # 成功交易奖励
                "lose_trade": -1.0,  # 失败交易惩罚
                "good_timing": 0.5,  # 良好时机奖励
                "bad_timing": -0.3   # 不良时机惩罚
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
            
            # 创建学习管理器
            self.learning_manager = LearningManager(config=self.config["learning"])
            
            # 创建经验记忆库
            self.experience_memory = ExperienceMemory({
                "memory_limit": self.config["learning"]["experience_buffer_size"]
            })
            
            # 创建特征提取器
            self.feature_extractor = FeatureExtractor()
            
            # 创建DQN学习器
            self.dqn_learner = DeepQLearner({
                "learning_rate": self.config["learning"]["learning_rate"],
                "batch_size": self.config["learning"]["batch_size"],
                "state_dim": 20,
                "action_dim": 3  # 买、卖、持有
            })
            
            # 加载测试数据
            self._load_test_data()
            
            logger.info("Agent学习系统设置完成")
            return True
        except Exception as e:
            logger.error(f"Agent学习系统设置失败: {str(e)}")
            traceback.print_exc()
            return False
    
    def _load_test_data(self):
        """加载测试数据"""
        try:
            if self.config["test"]["use_market_data"]:
                data_file = self.config["test"]["market_data_file"]
                
                if os.path.exists(data_file):
                    self.test_data = pd.read_csv(data_file)
                    logger.info(f"已加载市场数据: {data_file}, {len(self.test_data)}行")
                else:
                    logger.warning(f"市场数据文件不存在: {data_file}，将使用模拟数据")
                    self.test_data = self._generate_mock_data()
            else:
                self.test_data = self._generate_mock_data()
                logger.info("已生成模拟市场数据")
        except Exception as e:
            logger.error(f"加载测试数据失败: {str(e)}")
            traceback.print_exc()
            self.test_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        """生成模拟市场数据"""
        # 生成日期序列
        days = 500
        dates = pd.date_range(end=datetime.now(), periods=days)
        
        # 生成价格序列
        np.random.seed(42)  # 设置随机种子以保证可重复性
        
        # 生成带趋势和周期性的价格
        trend = np.linspace(0, 0.4, days)  # 上升趋势
        cycle = 0.1 * np.sin(np.linspace(0, 15, days))  # 周期性
        noise = np.random.normal(0, 0.01, days)  # 随机噪声
        
        # 组合成价格变化率
        returns = trend + cycle + noise
        
        # 计算价格
        price = 100 * (1 + returns).cumprod()
        
        # 创建DataFrame
        df = pd.DataFrame({
            'date': dates,
            'open': price * (1 + np.random.uniform(-0.005, 0.005, days)),
            'high': price * (1 + np.random.uniform(0, 0.01, days)),
            'low': price * (1 - np.random.uniform(0, 0.01, days)),
            'close': price,
            'volume': np.random.normal(1000000, 200000, days),
            'market_regime': np.random.choice(
                ['bull_trending', 'bull_volatile', 'bear_trending', 'bear_volatile', 
                 'neutral_low_vol', 'neutral_high_vol', 'transition_bullish', 'transition_bearish'],
                size=days,
                p=[0.2, 0.1, 0.15, 0.1, 0.15, 0.1, 0.1, 0.1]  # 各状态概率
            )
        })
        
        # 计算一些技术指标
        df['rsi'] = self._calculate_rsi(df['close'])
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_30'] = df['close'].rolling(window=30).mean()
        
        # 去除NaN值
        df = df.dropna()
        
        return df
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
                
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100. / (1. + rs)
            
        return rsi
    
    async def run_learning_test(self):
        """运行学习测试"""
        try:
            logger.info("开始运行Agent学习测试...")
            
            # 启动Agent
            start_result = await self.agent.start()
            if not start_result:
                logger.error("Agent启动失败")
                return False
            
            logger.info("Agent已启动，开始学习测试...")
            
            # 测试参数
            episodes = self.config["test"]["episodes"]
            trades_per_episode = self.config["test"]["trades_per_episode"]
            
            # 性能跟踪
            self.performance_history = []
            
            # 运行多轮测试
            for episode in range(1, episodes + 1):
                logger.info(f"开始第 {episode}/{episodes} 轮测试")
                
                # 运行一轮测试
                episode_performance = await self._run_episode(episode, trades_per_episode)
                
                # 记录性能
                self.performance_history.append(episode_performance)
                
                # 打印当前性能
                win_rate = episode_performance.get("win_rate", 0)
                avg_reward = episode_performance.get("avg_reward", 0)
                logger.info(f"第 {episode} 轮性能: 胜率={win_rate:.2f}, 平均奖励={avg_reward:.4f}")
                
                # 学习模型保存
                if episode % 10 == 0 or episode == episodes:
                    self.dqn_learner.save_model(f"dqn_model_ep{episode}")
                    logger.info(f"已保存模型: episode {episode}")
            
            # 停止Agent
            await self.agent.stop()
            
            # 绘制结果
            if self.config["test"]["plot_results"]:
                self._plot_learning_results()
            
            logger.info("Agent学习测试完成")
            return True
            
        except Exception as e:
            logger.error(f"测试过程中出错: {str(e)}")
            traceback.print_exc()
            
            # 确保Agent停止
            if self.agent and self.agent.active:
                await self.agent.stop()
                
            return False
    
    async def _run_episode(self, episode: int, trades_count: int) -> dict:
        """
        运行一轮测试
        
        Args:
            episode: 当前轮数
            trades_count: 交易数量
            
        Returns:
            本轮性能指标
        """
        # 本轮性能统计
        performance = {
            "episode": episode,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_reward": 0.0,
            "actions": {"buy": 0, "sell": 0, "hold": 0}
        }
        
        # 初始资金
        balance = 10000.0
        
        # 当前持仓
        position = 0
        
        # 选择本轮数据
        if episode == 1 or len(self.test_data) <= trades_count:
            # 第一轮或数据不足时使用全部数据
            episode_data = self.test_data
        else:
            # 随机选择一段连续数据
            start_idx = np.random.randint(0, len(self.test_data) - trades_count)
            episode_data = self.test_data.iloc[start_idx:start_idx + trades_count].copy()
        
        # 每个交易日
        for i in range(min(trades_count, len(episode_data))):
            # 获取当前数据
            current_data = episode_data.iloc[i]
            
            # 构建状态
            state = self._build_state(current_data, position, balance)
            
            # 提取特征
            features = self.feature_extractor.extract_features(state)
            
            # 选择动作
            action_idx, confidence = self.dqn_learner.select_action(features, evaluate=(episode == episodes))
            
            # 转换动作索引为动作
            action_map = {0: "buy", 1: "sell", 2: "hold"}
            action_name = action_map[action_idx]
            
            # 记录动作
            performance["actions"][action_name] += 1
            
            # 创建动作对象
            action = {
                "action": action_name,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            
            # 执行动作并获取奖励
            next_state, reward, done, trade_result = self._execute_action(
                action, state, current_data, i, episode_data
            )
            
            # 更新持仓和余额
            position = trade_result.get("position", position)
            balance = trade_result.get("balance", balance)
            
            # 提取下一状态特征
            next_features = self.feature_extractor.extract_features(next_state)
            
            # 添加经验
            self.dqn_learner.add_experience(features, action_idx, reward, next_features, done)
            self.experience_memory.add_experience(state, action, reward, next_state, done, {
                "episode": episode,
                "trade_idx": i,
                "balance": balance,
                "position": position
            })
            
            # 每10个交易后训练模型
            if i % 10 == 0 and i > 0:
                train_result = self.dqn_learner.train()
                if train_result.get("status") == "success":
                    logger.debug(f"训练结果: loss={train_result.get('loss', 0):.6f}")
            
            # 更新统计
            performance["trades"] += 1
            performance["total_reward"] += reward
            
            if reward > 0:
                performance["wins"] += 1
            elif reward < 0:
                performance["losses"] += 1
        
        # 计算性能指标
        performance["win_rate"] = performance["wins"] / performance["trades"] if performance["trades"] > 0 else 0
        performance["avg_reward"] = performance["total_reward"] / performance["trades"] if performance["trades"] > 0 else 0
        performance["final_balance"] = balance
        
        return performance
    
    def _build_state(self, data, position, balance):
        """构建状态对象"""
        # 提取OHLCV数据
        ohlcv = {
            "open": data["open"],
            "high": data["high"],
            "low": data["low"],
            "close": data["close"],
            "volume": data["volume"]
        }
        
        # 提取技术指标
        indicators = {
            "rsi": data["rsi"],
            "ma_10": data["ma_10"],
            "ma_30": data["ma_30"]
        }
        
        # 计算当前趋势
        trend_direction = "up" if data["ma_10"] > data["ma_30"] else "down"
        trend_strength = abs(data["ma_10"] / data["ma_30"] - 1) if data["ma_30"] > 0 else 0
        
        # 构建状态
        state = {
            "market_state": {
                "market_regime": data["market_regime"],
                "trend": {
                    "direction": trend_direction,
                    "strength": trend_strength
                }
            },
            "risk_state": {
                "level": "medium",  # 简化版
                "score": 0.5
            },
            "portfolio_state": {
                "position": position,
                "balance": balance,
                "cash_ratio": 1.0 if position == 0 else 0.0
            },
            "price_data": {
                "ohlcv": ohlcv,
                "current_price": data["close"],
                "recent_return": (data["close"] / data["open"] - 1) if data["open"] > 0 else 0
            },
            "indicators": indicators,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        return state
    
    def _execute_action(self, action, state, current_data, index, episode_data):
        """
        执行交易动作
        
        Returns:
            (next_state, reward, done, info)
        """
        action_type = action["action"]
        position = state["portfolio_state"]["position"]
        balance = state["portfolio_state"]["balance"]
        
        # 当前价格
        current_price = current_data["close"]
        
        # 下一个价格（如果可用）
        next_price = episode_data.iloc[index + 1]["close"] if index < len(episode_data) - 1 else current_price
        
        # 默认结果
        trade_result = {
            "position": position,
            "balance": balance,
            "trade_price": current_price,
            "trade_type": "none",
            "profit": 0.0
        }
        
        # 根据动作类型执行交易
        if action_type == "buy" and position <= 0:
            # 买入
            shares_to_buy = int(balance / current_price)
            if shares_to_buy > 0:
                new_position = shares_to_buy
                new_balance = balance - (shares_to_buy * current_price)
                
                trade_result["position"] = new_position
                trade_result["balance"] = new_balance
                trade_result["trade_type"] = "buy"
                
        elif action_type == "sell" and position > 0:
            # 卖出
            sell_price = current_price
            new_balance = balance + (position * sell_price)
            profit = position * (sell_price - current_price)
            
            trade_result["position"] = 0
            trade_result["balance"] = new_balance
            trade_result["trade_type"] = "sell"
            trade_result["profit"] = profit
        
        # 构建下一状态
        next_state = self._build_state(
            current_data if index == len(episode_data) - 1 else episode_data.iloc[index + 1],
            trade_result["position"],
            trade_result["balance"]
        )
        
        # 计算奖励
        reward = self._calculate_reward(action, state, next_state, trade_result, current_price, next_price)
        
        # 判断是否完成
        done = (index == len(episode_data) - 1) or (trade_result["trade_type"] == "sell")
        
        return next_state, reward, done, trade_result
    
    def _calculate_reward(self, action, state, next_state, trade_result, current_price, next_price):
        """计算奖励"""
        action_type = action["action"]
        market_regime = state["market_state"]["market_regime"]
        trend_direction = state["market_state"]["trend"]["direction"]
        
        reward = 0.0
        
        # 1. 交易结果奖励
        if trade_result["trade_type"] == "sell":
            profit = trade_result["profit"]
            if profit > 0:
                reward += self.config["rewards"]["win_trade"]
            else:
                reward += self.config["rewards"]["lose_trade"]
        
        # 2. 时机奖励 - 买入
        if action_type == "buy":
            # 买入时机奖励
            if trend_direction == "up" and market_regime in ["bull_trending", "transition_bullish"]:
                reward += self.config["rewards"]["good_timing"]
            elif trend_direction == "down" and market_regime in ["bear_trending", "transition_bearish"]:
                reward += self.config["rewards"]["bad_timing"]
                
            # 价格走势奖励 - 如果下一个价格高于当前价格，买入是好的
            price_change = next_price / current_price - 1
            reward += price_change * 5  # 放大奖励
        
        # 3. 时机奖励 - 卖出
        elif action_type == "sell":
            # 卖出时机奖励
            if trend_direction == "down" and market_regime in ["bear_trending", "transition_bearish"]:
                reward += self.config["rewards"]["good_timing"]
            elif trend_direction == "up" and market_regime in ["bull_trending", "transition_bullish"]:
                reward += self.config["rewards"]["bad_timing"]
                
            # 价格走势奖励 - 如果下一个价格低于当前价格，卖出是好的
            price_change = next_price / current_price - 1
            reward -= price_change * 5  # 放大奖励
        
        return reward
    
    def _plot_learning_results(self):
        """绘制学习结果图表"""
        try:
            if not self.performance_history:
                logger.warning("没有性能数据可绘制")
                return
            
            # 创建图表目录
            plots_dir = Path("plots")
            plots_dir.mkdir(exist_ok=True)
            
            # 提取数据
            episodes = [p["episode"] for p in self.performance_history]
            win_rates = [p["win_rate"] for p in self.performance_history]
            avg_rewards = [p["avg_reward"] for p in self.performance_history]
            
            # 创建绘图
            plt.figure(figsize=(12, 8))
            
            # 胜率曲线
            plt.subplot(2, 1, 1)
            plt.plot(episodes, win_rates, 'b-', label='Win Rate')
            plt.xlabel('Episode')
            plt.ylabel('Win Rate')
            plt.title('Learning Progress - Win Rate')
            plt.grid(True)
            plt.legend()
            
            # 平均奖励曲线
            plt.subplot(2, 1, 2)
            plt.plot(episodes, avg_rewards, 'r-', label='Average Reward')
            plt.xlabel('Episode')
            plt.ylabel('Average Reward')
            plt.title('Learning Progress - Average Reward')
            plt.grid(True)
            plt.legend()
            
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(plots_dir / f"learning_progress_{int(time.time())}.png")
            plt.close()
            
            logger.info(f"学习进度图表已保存到 plots 目录")
            
            # 绘制动作分布图
            action_counts = {
                "buy": [p["actions"]["buy"] for p in self.performance_history],
                "sell": [p["actions"]["sell"] for p in self.performance_history],
                "hold": [p["actions"]["hold"] for p in self.performance_history]
            }
            
            plt.figure(figsize=(10, 6))
            plt.stackplot(episodes, 
                        action_counts["buy"], 
                        action_counts["sell"], 
                        action_counts["hold"],
                        labels=["Buy", "Sell", "Hold"],
                        colors=['g', 'r', 'gray'])
            plt.xlabel('Episode')
            plt.ylabel('Action Count')
            plt.title('Action Distribution Over Episodes')
            plt.legend()
            plt.grid(True)
            
            plt.savefig(plots_dir / f"action_distribution_{int(time.time())}.png")
            plt.close()
            
            logger.info(f"动作分布图表已保存到 plots 目录")
            
        except Exception as e:
            logger.error(f"绘制图表失败: {str(e)}")
            traceback.print_exc()

async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='智能交易Agent学习测试工具')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--episodes', type=int, help='测试轮数')
    
    args = parser.parse_args()
    
    # 创建测试工具
    tester = LearningAgentTester(args.config)
    
    # 如果指定了轮数，覆盖配置
    if args.episodes is not None:
        tester.config["test"]["episodes"] = args.episodes
    
    # 设置Agent系统
    setup_success = await tester.setup()
    if not setup_success:
        logger.error("Agent学习系统设置失败，测试终止")
        return 1
    
    # 运行学习测试
    test_success = await tester.run_learning_test()
    
    if test_success:
        logger.info("Agent学习测试成功完成")
        return 0
    else:
        logger.error("Agent学习测试失败")
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