"""
虚拟账户API路由
提供虚拟账户、持仓、交易记录的管理接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ...models import get_db, VirtualAccount, VirtualPosition, VirtualTrade
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/virtual-account", tags=["虚拟账户"])

# 数据模型
class VirtualAccountCreate(BaseModel):
    account_name: str = Field(..., description="账户名称")
    broker_type: str = Field(..., description="券商类型")
    total_assets: float = Field(default=0.0, description="总资产")
    available_cash: float = Field(default=0.0, description="可用资金")

class VirtualAccountUpdate(BaseModel):
    total_assets: Optional[float] = None
    available_cash: Optional[float] = None
    market_value: Optional[float] = None
    frozen_amount: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_ratio: Optional[float] = None
    last_sync_time: Optional[datetime] = None
    data_source: Optional[str] = None

class VirtualPositionCreate(BaseModel):
    symbol: str = Field(..., description="证券代码")
    name: str = Field(..., description="证券名称")
    quantity: int = Field(..., description="持仓数量")
    available_quantity: int = Field(..., description="可用数量")
    cost_price: float = Field(..., description="成本价")
    current_price: float = Field(..., description="当前价")
    trade_source: str = Field(default="manual", description="交易来源")

class VirtualTradeCreate(BaseModel):
    order_id: str = Field(..., description="委托编号")
    symbol: str = Field(..., description="证券代码")
    name: str = Field(..., description="证券名称")
    action: str = Field(..., description="交易动作")
    price: float = Field(..., description="成交价格")
    quantity: int = Field(..., description="成交数量")
    trade_source: str = Field(default="manual", description="交易来源")

# API路由
@router.get("/accounts", response_model=List[Dict])
async def get_virtual_accounts(db: Session = Depends(get_db)):
    """获取所有虚拟账户"""
    try:
        accounts = db.query(VirtualAccount).filter(VirtualAccount.is_active == True).all()
        return [
            {
                "id": account.id,
                "account_name": account.account_name,
                "broker_type": account.broker_type,
                "total_assets": account.total_assets,
                "available_cash": account.available_cash,
                "market_value": account.market_value,
                "frozen_amount": account.frozen_amount,
                "profit_loss": account.profit_loss,
                "profit_loss_ratio": account.profit_loss_ratio,
                "last_sync_time": account.last_sync_time.isoformat() if account.last_sync_time else None,
                "data_source": account.data_source,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
            for account in accounts
        ]
    except Exception as e:
        logger.error(f"获取虚拟账户列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取虚拟账户列表失败: {str(e)}")

@router.get("/accounts/{account_id}", response_model=Dict)
async def get_virtual_account(account_id: int, db: Session = Depends(get_db)):
    """获取指定虚拟账户详情"""
    try:
        account = db.query(VirtualAccount).filter(
            VirtualAccount.id == account_id,
            VirtualAccount.is_active == True
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="虚拟账户不存在")
        
        return {
            "success": True,
            "data": {
                "id": account.id,
                "account_name": account.account_name,
                "broker_type": account.broker_type,
                "total_assets": account.total_assets,
                "available_cash": account.available_cash,
                "market_value": account.market_value,
                "frozen_amount": account.frozen_amount,
                "profit_loss": account.profit_loss,
                "profit_loss_ratio": account.profit_loss_ratio,
                "last_sync_time": account.last_sync_time.isoformat() if account.last_sync_time else None,
                "data_source": account.data_source,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取虚拟账户详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取虚拟账户详情失败: {str(e)}")

@router.get("/accounts/{account_id}/positions", response_model=Dict)
async def get_virtual_positions(account_id: int, db: Session = Depends(get_db)):
    """获取虚拟账户持仓列表"""
    try:
        # 验证账户存在
        account = db.query(VirtualAccount).filter(
            VirtualAccount.id == account_id,
            VirtualAccount.is_active == True
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="虚拟账户不存在")
        
        positions = db.query(VirtualPosition).filter(
            VirtualPosition.account_id == account_id,
            VirtualPosition.quantity > 0
        ).all()
        
        position_list = []
        for pos in positions:
            position_list.append({
                "symbol": pos.symbol,
                "name": pos.name,
                "quantity": pos.quantity,
                "available_quantity": pos.available_quantity,
                "cost_price": pos.cost_price,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "profit_loss": pos.profit_loss,
                "profit_loss_ratio": pos.profit_loss_ratio,
                "position_date": pos.position_date,
                "trade_source": pos.trade_source,
                "last_update_time": pos.last_update_time.isoformat() if pos.last_update_time else None
            })
        
        return {
            "success": True,
            "data": position_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取虚拟持仓列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取虚拟持仓列表失败: {str(e)}")

@router.post("/accounts", response_model=Dict)
async def create_virtual_account(account_data: VirtualAccountCreate, db: Session = Depends(get_db)):
    """创建虚拟账户"""
    try:
        # 检查账户名是否已存在
        existing_account = db.query(VirtualAccount).filter(
            VirtualAccount.account_name == account_data.account_name,
            VirtualAccount.is_active == True
        ).first()
        
        if existing_account:
            raise HTTPException(status_code=400, detail="账户名已存在")
        
        # 创建新账户
        new_account = VirtualAccount(
            user_id=1,  # 默认用户ID，实际应用中应从认证信息获取
            account_name=account_data.account_name,
            broker_type=account_data.broker_type,
            total_assets=account_data.total_assets,
            available_cash=account_data.available_cash,
            market_value=0.0,
            frozen_amount=0.0,
            profit_loss=0.0,
            profit_loss_ratio=0.0,
            last_sync_time=datetime.now(),
            data_source="manual_create"
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return {
            "success": True,
            "message": "虚拟账户创建成功",
            "data": {
                "id": new_account.id,
                "account_name": new_account.account_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建虚拟账户失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建虚拟账户失败: {str(e)}")

@router.put("/accounts/{account_id}/sync", response_model=Dict)
async def sync_virtual_account_from_trading_software(account_id: int, db: Session = Depends(get_db)):
    """从交易软件同步虚拟账户数据"""
    try:
        # 这里应该调用真实的交易软件数据获取接口
        # 暂时使用模拟数据
        from ...services.account_sync_service import sync_account_from_trading_software
        
        result = await sync_account_from_trading_software(account_id, db)
        
        return {
            "success": True,
            "message": "账户数据同步成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"同步虚拟账户数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"同步虚拟账户数据失败: {str(e)}")
