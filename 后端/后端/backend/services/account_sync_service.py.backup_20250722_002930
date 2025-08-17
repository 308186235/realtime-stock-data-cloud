"""
账户同步服务
负责从真实交易软件同步数据到虚拟账户数据库
"""

import logging
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

from ..models import VirtualAccount, VirtualPosition, VirtualTrade
from .trading_service import TradingService

logger = logging.getLogger(__name__)

class AccountSyncService:
    """账户同步服务"""
    
    def __init__(self):
        self.trading_service = TradingService()
    
    async def sync_account_from_trading_software(self, account_id: int, db: Session) -> Dict:
        """从交易软件同步账户数据"""
        try:
            # 获取虚拟账户
            account = db.query(VirtualAccount).filter(VirtualAccount.id == account_id).first()
            if not account:
                raise Exception(f"虚拟账户 {account_id} 不存在")
            
            # 连接交易服务
            connect_result = self.trading_service.connect(
                broker_type=account.broker_type,
                account_id=account.account_name
            )
            
            if not connect_result.get("success"):
                raise Exception(f"连接交易服务失败: {connect_result.get('message')}")
            
            # 获取账户信息
            account_info_result = self.trading_service.get_account_info()
            if not account_info_result.get("success"):
                raise Exception(f"获取账户信息失败: {account_info_result.get('message')}")
            
            account_info = account_info_result["data"]
            
            # 更新虚拟账户信息
            account.total_assets = account_info.get("total_assets", 0.0)
            account.available_cash = account_info.get("available", 0.0)
            account.market_value = account_info.get("market_value", 0.0)
            account.frozen_amount = account_info.get("frozen", 0.0)
            account.last_sync_time = datetime.now()
            account.data_source = "trading_software_sync"
            
            # 获取持仓信息
            positions_result = self.trading_service.get_positions()
            if positions_result.get("success") and positions_result.get("data"):
                await self._sync_positions(account_id, positions_result["data"], db)
            
            # 计算盈亏
            self._calculate_profit_loss(account, db)
            
            db.commit()
            
            logger.info(f"账户 {account_id} 同步成功")
            
            return {
                "account_id": account_id,
                "total_assets": account.total_assets,
                "available_cash": account.available_cash,
                "market_value": account.market_value,
                "sync_time": account.last_sync_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"同步账户 {account_id} 失败: {str(e)}")
            db.rollback()
            raise e
        finally:
            # 断开交易服务连接
            self.trading_service.disconnect()
    
    async def _sync_positions(self, account_id: int, real_positions: List[Dict], db: Session):
        """同步持仓数据"""
        try:
            # 获取现有虚拟持仓
            existing_positions = db.query(VirtualPosition).filter(
                VirtualPosition.account_id == account_id
            ).all()
            
            existing_symbols = {pos.symbol: pos for pos in existing_positions}
            
            # 处理真实持仓数据
            for real_pos in real_positions:
                symbol = real_pos.get("symbol", "")
                if not symbol:
                    continue
                
                if symbol in existing_symbols:
                    # 更新现有持仓
                    pos = existing_symbols[symbol]
                    pos.quantity = real_pos.get("volume", 0)
                    pos.available_quantity = real_pos.get("available_volume", 0)
                    pos.cost_price = real_pos.get("cost_price", 0.0)
                    pos.current_price = real_pos.get("current_price", 0.0)
                    pos.market_value = real_pos.get("market_value", 0.0)
                    pos.profit_loss = real_pos.get("profit_loss", 0.0)
                    pos.profit_loss_ratio = real_pos.get("profit_loss_ratio", 0.0)
                    pos.last_update_time = datetime.now()
                    pos.trade_source = "real"
                else:
                    # 创建新持仓
                    new_pos = VirtualPosition(
                        account_id=account_id,
                        symbol=symbol,
                        name=real_pos.get("name", ""),
                        quantity=real_pos.get("volume", 0),
                        available_quantity=real_pos.get("available_volume", 0),
                        cost_price=real_pos.get("cost_price", 0.0),
                        current_price=real_pos.get("current_price", 0.0),
                        market_value=real_pos.get("market_value", 0.0),
                        profit_loss=real_pos.get("profit_loss", 0.0),
                        profit_loss_ratio=real_pos.get("profit_loss_ratio", 0.0),
                        position_date=datetime.now().strftime('%Y-%m-%d'),
                        trade_source="real",
                        last_update_time=datetime.now()
                    )
                    db.add(new_pos)
            
            # 清理已清仓的持仓（数量为0的持仓）
            real_symbols = {pos.get("symbol") for pos in real_positions if pos.get("volume", 0) > 0}
            for symbol, pos in existing_symbols.items():
                if symbol not in real_symbols and pos.trade_source == "real":
                    pos.quantity = 0
                    pos.available_quantity = 0
                    pos.market_value = 0.0
                    pos.last_update_time = datetime.now()
            
            logger.info(f"账户 {account_id} 持仓同步完成，共 {len(real_positions)} 只股票")
            
        except Exception as e:
            logger.error(f"同步持仓数据失败: {str(e)}")
            raise e
    
    def _calculate_profit_loss(self, account: VirtualAccount, db: Session):
        """计算账户总盈亏"""
        try:
            # 获取所有持仓
            positions = db.query(VirtualPosition).filter(
                VirtualPosition.account_id == account.id,
                VirtualPosition.quantity > 0
            ).all()
            
            total_profit_loss = sum(pos.profit_loss for pos in positions)
            total_cost = sum(pos.quantity * pos.cost_price for pos in positions)
            
            account.profit_loss = total_profit_loss
            account.profit_loss_ratio = (total_profit_loss / total_cost) if total_cost > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算盈亏失败: {str(e)}")

# 全局服务实例
account_sync_service = AccountSyncService()

# 导出函数
async def sync_account_from_trading_software(account_id: int, db: Session) -> Dict:
    """从交易软件同步账户数据"""
    return await account_sync_service.sync_account_from_trading_software(account_id, db)

async def create_default_virtual_account(db: Session) -> Dict:
    """创建默认虚拟账户"""
    try:
        # 检查是否已存在默认账户
        existing_account = db.query(VirtualAccount).filter(
            VirtualAccount.account_name == "东吴秀才",
            VirtualAccount.is_active == True
        ).first()
        
        if existing_account:
            return {
                "success": True,
                "message": "默认账户已存在",
                "account_id": existing_account.id
            }
        
        # 创建默认账户
        default_account = VirtualAccount(
            user_id=1,
            account_name="东吴秀才",
            broker_type="dongwu_xiucai",
            total_assets=120000.00,
            available_cash=80000.00,
            market_value=40000.00,
            frozen_amount=0.00,
            profit_loss=0.00,
            profit_loss_ratio=0.00,
            last_sync_time=datetime.now(),
            data_source="default_create"
        )
        
        db.add(default_account)
        db.commit()
        db.refresh(default_account)
        
        logger.info(f"默认虚拟账户创建成功，ID: {default_account.id}")
        
        return {
            "success": True,
            "message": "默认账户创建成功",
            "account_id": default_account.id
        }
        
    except Exception as e:
        logger.error(f"创建默认虚拟账户失败: {str(e)}")
        db.rollback()
        raise e
