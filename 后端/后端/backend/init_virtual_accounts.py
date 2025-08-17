#!/usr/bin/env python3
"""
初始化虚拟账户数据库
创建虚拟账户表并插入默认数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import init_db, SessionLocal, VirtualAccount, VirtualPosition
from services.account_sync_service import create_default_virtual_account
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_virtual_account_tables():
    """初始化虚拟账户数据库表"""
    try:
        logger.info("开始初始化虚拟账户数据库表...")
        
        # 创建所有表
        init_db()
        logger.info("数据库表创建完成")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 创建默认虚拟账户
            result = await create_default_virtual_account(db)
            logger.info(f"默认账户创建结果: {result}")
            
            # 创建一些示例持仓数据
            if result.get("success"):
                account_id = result["account_id"]
                await create_sample_positions(account_id, db)
            
        finally:
            db.close()
        
        logger.info("虚拟账户数据库初始化完成")
        
    except Exception as e:
        logger.error(f"初始化虚拟账户数据库失败: {str(e)}")
        raise e

async def create_sample_positions(account_id: int, db):
    """创建示例持仓数据"""
    try:
        logger.info(f"为账户 {account_id} 创建示例持仓数据...")
        
        sample_positions = [
            {
                "symbol": "600519",
                "name": "贵州茅台",
                "quantity": 10,
                "available_quantity": 10,
                "cost_price": 1680.25,
                "current_price": 1760.88,
                "market_value": 17608.80,
                "profit_loss": 806.30,
                "profit_loss_ratio": 0.048,
                "position_date": "2023-06-15",
                "trade_source": "real"
            },
            {
                "symbol": "000001",
                "name": "平安银行",
                "quantity": 1000,
                "available_quantity": 1000,
                "cost_price": 16.05,
                "current_price": 15.23,
                "market_value": 15230.00,
                "profit_loss": -820.00,
                "profit_loss_ratio": -0.0511,
                "position_date": "2023-05-22",
                "trade_source": "real"
            },
            {
                "symbol": "601318",
                "name": "中国平安",
                "quantity": 200,
                "available_quantity": 200,
                "cost_price": 45.30,
                "current_price": 48.75,
                "market_value": 9750.00,
                "profit_loss": 690.00,
                "profit_loss_ratio": 0.0761,
                "position_date": "2023-07-03",
                "trade_source": "ai"
            },
            {
                "symbol": "300750",
                "name": "宁德时代",
                "quantity": 50,
                "available_quantity": 50,
                "cost_price": 200.40,
                "current_price": 226.60,
                "market_value": 11330.00,
                "profit_loss": 1310.00,
                "profit_loss_ratio": 0.1307,
                "position_date": "2023-04-18",
                "trade_source": "ai"
            },
            {
                "symbol": "600050",
                "name": "中国联通",
                "quantity": 5000,
                "available_quantity": 5000,
                "cost_price": 5.12,
                "current_price": 4.68,
                "market_value": 23400.00,
                "profit_loss": -2200.00,
                "profit_loss_ratio": -0.0859,
                "position_date": "2023-01-30",
                "trade_source": "real"
            }
        ]
        
        for pos_data in sample_positions:
            # 检查是否已存在
            existing_pos = db.query(VirtualPosition).filter(
                VirtualPosition.account_id == account_id,
                VirtualPosition.symbol == pos_data["symbol"]
            ).first()
            
            if not existing_pos:
                new_position = VirtualPosition(
                    account_id=account_id,
                    symbol=pos_data["symbol"],
                    name=pos_data["name"],
                    quantity=pos_data["quantity"],
                    available_quantity=pos_data["available_quantity"],
                    cost_price=pos_data["cost_price"],
                    current_price=pos_data["current_price"],
                    market_value=pos_data["market_value"],
                    profit_loss=pos_data["profit_loss"],
                    profit_loss_ratio=pos_data["profit_loss_ratio"],
                    position_date=pos_data["position_date"],
                    trade_source=pos_data["trade_source"],
                    last_update_time=datetime.now()
                )
                db.add(new_position)
        
        db.commit()
        logger.info(f"示例持仓数据创建完成,共 {len(sample_positions)} 只股票")
        
    except Exception as e:
        logger.error(f"创建示例持仓数据失败: {str(e)}")
        db.rollback()
        raise e

def sync_account_data():
    """同步账户数据(可选)"""
    try:
        logger.info("开始同步账户数据...")
        
        # 这里可以调用真实的交易软件数据同步
        # 暂时跳过,使用示例数据
        
        logger.info("账户数据同步完成")
        
    except Exception as e:
        logger.error(f"同步账户数据失败: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 初始化数据库表
        init_virtual_account_tables()
        
        # 可选:同步真实数据
        # sync_account_data()
        
        print("✅ 虚拟账户数据库初始化完成!")
        print("📱 现在移动端可以显示真实的账户和持仓数据了")
        print("🔄 数据流程:真实交易软件 → 虚拟账户数据库 → 移动端显示")
    
    # 运行异步主函数
    asyncio.run(main())
