"""
更新的投资组合API路由 - 使用Supabase数据库适配器
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
import logging
import sys
import os

# 添加路径以导入适配器
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from adapters.simple_database_adapter import simple_db_adapter
from services.portfolio_service import PortfolioService

# 初始化日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
portfolio_service = PortfolioService()

@router.get("/")
async def get_portfolios(user_id: Optional[str] = Query(None)):
    """获取所有投资组合列表"""
    try:
        if user_id:
            # 获取指定用户的投资组合
            result = portfolio_service.get_user_portfolios(user_id)
            if result['success']:
                return {
                    "success": True,
                    "data": result['data']
                }
            else:
                raise HTTPException(status_code=404, detail=result.get('error', '获取投资组合失败'))
        else:
            # 获取所有投资组合（演示数据）
            all_portfolios = simple_db_adapter.get_portfolios()
            return {
                "success": True,
                "data": all_portfolios
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取投资组合列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取投资组合失败: {str(e)}")

@router.post("/")
async def create_portfolio(portfolio_data: Dict[str, Any] = Body(...)):
    """创建新投资组合"""
    try:
        user_id = portfolio_data.get('user_id')
        name = portfolio_data.get('name')
        initial_cash = portfolio_data.get('initial_cash', 100000.0)
        
        if not user_id or not name:
            raise HTTPException(status_code=400, detail="用户ID和组合名称不能为空")
        
        result = portfolio_service.create_portfolio(user_id, name, initial_cash)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "投资组合创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', '创建投资组合失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建投资组合出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建投资组合失败: {str(e)}")

@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """获取指定投资组合详情"""
    try:
        result = simple_db_adapter.get_portfolio(portfolio_id)
        if result['success']:
            portfolio = result['data']
            
            # 获取持仓信息
            holdings_result = simple_db_adapter.get_holdings(portfolio_id)
            if holdings_result['success']:
                portfolio['holdings'] = holdings_result['data']
            else:
                portfolio['holdings'] = []
            
            return {
                "success": True,
                "data": portfolio
            }
        else:
            raise HTTPException(status_code=404, detail="投资组合不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取投资组合详情出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取投资组合详情失败: {str(e)}")

@router.put("/{portfolio_id}")
async def update_portfolio(portfolio_id: str, portfolio_data: Dict[str, Any] = Body(...)):
    """更新投资组合信息"""
    try:
        result = simple_db_adapter.update_portfolio(portfolio_id, portfolio_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "投资组合更新成功"
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '投资组合不存在'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新投资组合出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新投资组合失败: {str(e)}")

@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: str):
    """删除投资组合"""
    try:
        result = simple_db_adapter.delete_portfolio(portfolio_id)
        if result['success']:
            return {
                "success": True,
                "message": "投资组合删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '投资组合不存在'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除投资组合出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除投资组合失败: {str(e)}")

@router.get("/{portfolio_id}/holdings")
async def get_portfolio_holdings(portfolio_id: str):
    """获取投资组合的持仓信息"""
    try:
        result = simple_db_adapter.get_holdings(portfolio_id)
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '获取持仓信息失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取持仓信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取持仓信息失败: {str(e)}")

@router.post("/{portfolio_id}/holdings")
async def add_holding(portfolio_id: str, holding_data: Dict[str, Any] = Body(...)):
    """添加持仓"""
    try:
        holding_data['portfolio_id'] = portfolio_id
        result = simple_db_adapter.create_holding(holding_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "持仓添加成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', '添加持仓失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加持仓出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加持仓失败: {str(e)}")

@router.put("/{portfolio_id}/holdings/{holding_id}")
async def update_holding(portfolio_id: str, holding_id: str, holding_data: Dict[str, Any] = Body(...)):
    """更新持仓"""
    try:
        result = simple_db_adapter.update_holding(holding_id, holding_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "持仓更新成功"
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '持仓不存在'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新持仓出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新持仓失败: {str(e)}")

@router.delete("/{portfolio_id}/holdings/{holding_id}")
async def delete_holding(portfolio_id: str, holding_id: str):
    """删除持仓"""
    try:
        result = simple_db_adapter.delete_holding(holding_id)
        if result['success']:
            return {
                "success": True,
                "message": "持仓删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '持仓不存在'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除持仓出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除持仓失败: {str(e)}")

@router.get("/{portfolio_id}/transactions")
async def get_portfolio_transactions(portfolio_id: str):
    """获取投资组合的交易记录"""
    try:
        result = simple_db_adapter.get_transactions(portfolio_id)
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '获取交易记录失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取交易记录出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")

@router.post("/{portfolio_id}/transactions")
async def add_transaction(portfolio_id: str, transaction_data: Dict[str, Any] = Body(...)):
    """添加交易记录"""
    try:
        transaction_data['portfolio_id'] = portfolio_id
        result = simple_db_adapter.create_transaction(transaction_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "交易记录添加成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', '添加交易记录失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加交易记录出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加交易记录失败: {str(e)}")

@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(portfolio_id: str):
    """获取投资组合的业绩表现"""
    try:
        result = portfolio_service.get_portfolio_performance(portfolio_id)
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=404, detail=result.get('error', '获取业绩表现失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取业绩表现出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取业绩表现失败: {str(e)}")
