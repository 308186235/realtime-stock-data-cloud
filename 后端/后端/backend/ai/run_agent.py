#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trading Agent 运行脚本

用于启动和管理Trading Agent实例,支持命令行参数配置
"""

import os
import sys
import json
import logging
import argparse
import asyncio
import signal
import datetime
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)

# 导入Agent类
from backend.ai.agent_system import TradingAgent, AgentAPI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', f'agent_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    ]
)
logger = logging.getLogger('run_agent')

# 默认配置
DEFAULT_CONFIG = {
    "name": "TradingAgent",
    "loop_interval": 60,
    "monitor_interval": 30,
    "market_analyzer": {
        "enabled": True,
        "update_interval": 300
    },
    "risk_manager": {
        "enabled": True,
        "max_position_size": 0.2,
        "max_daily_loss": 0.03
    },
    "trade_executor": {
        "enable_paper_trading": True,
        "broker": {
            "api_key": "",
            "api_secret": "",
            "base_url": "http://localhost:8080/api",
            "account_id": ""
        },
        "max_position_size": 0.2,
        "max_orders_per_day": 100,
        "min_order_interval": 60
    }
}

# 信号处理
stop_event = asyncio.Event()

def signal_handler():
    """处理终止信号"""
    logger.info("接收到终止信号,正在停止Agent...")
    stop_event.set()

# 加载配置文件
def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载Agent配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载配置文件: {config_path}")
            return config
        else:
            logger.warning(f"配置文件不存在: {config_path},使用默认配置")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)},使用默认配置")
        return DEFAULT_CONFIG

# 创建必要的目录
def create_directories():
    """创建必要的目录"""
    dirs = ['logs', 'data', 'models', 'reports']
    for dir_name in dirs:
        dir_path = os.path.join(project_root, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建目录: {dir_path}")

# 主函数
async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启动Trading Agent')
    parser.add_argument('--config', type=str, default='config/agent_config.json',
                        help='配置文件路径')
    parser.add_argument('--auto-trade', type=str, choices=['true', 'false'], default='false',
                        help='是否启用自动交易')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 创建必要的目录
    create_directories()
    
    # 加载配置
    config_path = os.path.join(project_root, args.config)
    config = load_config(config_path)
    
    # 更新配置:自动交易设置
    enable_auto_trade = args.auto_trade.lower() == 'true'
    config['trade_executor']['enable_paper_trading'] = not enable_auto_trade
    
    if enable_auto_trade:
        logger.info("自动交易已启用 - 执行真实交易")
    else:
        logger.info("自动交易已禁用 - 仅运行模拟交易模式")
    
    # 创建Agent实例
    agent = TradingAgent(config=config)
    
    # 创建API
    api = AgentAPI(agent)
    
    try:
        # 注册信号处理
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
        
        # 启动Agent
        logger.info("正在启动Agent...")
        await agent.start()
        
        # 等待停止信号
        await stop_event.wait()
        
    except Exception as e:
        logger.error(f"Agent运行出错: {str(e)}")
    finally:
        # 停止Agent
        logger.info("正在停止Agent...")
        await agent.stop()
        logger.info("Agent已停止")

if __name__ == "__main__":
    asyncio.run(main()) 
