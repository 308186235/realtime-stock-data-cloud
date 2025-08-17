"""
Supabase投资组合API路由 - 使用新的数据库适配器
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, List, Dict, Any
import logging
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from adapters.simple_database_adapter import simple_db_adapter

# 初始化日志
logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== 用户管理 ====================

@router.post("/users")
async def create_user(user_data: Dict[str, Any] = Body(...)):
    """创建用户"""
    try:
        result = simple_db_adapter.create_user(user_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "用户创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"创建用户出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    try:
        result = simple_db_adapter.get_user(user_id)
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        logger.error(f"获取用户信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.get("/users")
async def get_users(username: Optional[str] = Query(None)):
    """获取用户列表"""
    try:
        filters = {'username': username} if username else None
        result = simple_db_adapter.get_users(filters)
        return {
            "success": True,
            "data": result['data']
        }
    except Exception as e:
        logger.error(f"获取用户列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

# ==================== 股票管理 ====================

@router.post("/stocks")
async def create_stock(stock_data: Dict[str, Any] = Body(...)):
    """创建股票信息"""
    try:
        result = simple_db_adapter.create_stock(stock_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "股票信息创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"创建股票信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建股票信息失败: {str(e)}")

@router.get("/stocks")
async def get_stocks(
    market: Optional[str] = Query(None),
    sector: Optional[str] = Query(None)
):
    """获取股票列表"""
    try:
        filters = {}
        if market:
            filters['market'] = market
        if sector:
            filters['sector'] = sector
        
        result = simple_db_adapter.get_stocks(filters)
        return {
            "success": True,
            "data": result['data']
        }
    except Exception as e:
        logger.error(f"获取股票列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")

@router.get("/stocks/{stock_code}")
async def get_stock(stock_code: str):
    """获取股票详情"""
    try:
        result = simple_db_adapter.get_stock(stock_code)
        if result['success'] and result['data']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=404, detail="股票不存在")
    except Exception as e:
        logger.error(f"获取股票详情出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取股票详情失败: {str(e)}")

# ==================== 投资组合管理 ====================

@router.post("/portfolios")
async def create_portfolio(portfolio_data: Dict[str, Any] = Body(...)):
    """创建投资组合"""
    try:
        result = simple_db_adapter.create_portfolio(portfolio_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "投资组合创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"创建投资组合出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建投资组合失败: {str(e)}")

@router.get("/portfolios")
async def get_portfolios(user_id: Optional[str] = Query(None)):
    """获取投资组合列表"""
    try:
        result = simple_db_adapter.get_portfolios(user_id)
        return {
            "success": True,
            "data": result['data']
        }
    except Exception as e:
        logger.error(f"获取投资组合列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取投资组合列表失败: {str(e)}")

@router.get("/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """获取投资组合详情"""
    try:
        # 获取投资组合基本信息
        portfolio_result = simple_db_adapter.get_portfolio(portfolio_id)
        if not portfolio_result['success'] or not portfolio_result['data']:
            raise HTTPException(status_code=404, detail="投资组合不存在")
        
        portfolio = portfolio_result['data']
        
        # 获取持仓信息
        holdings_result = simple_db_adapter.get_holdings(portfolio_id)
        if holdings_result['success']:
            portfolio['holdings'] = holdings_result['data']
            portfolio['holdings_count'] = len(holdings_result['data'])
            
            # 计算持仓统计
            total_market_value = 0
            for holding in holdings_result['data']:
                shares = holding.get('shares', 0)
                current_price = holding.get('current_price', holding.get('cost_price', 0))
                market_value = shares * current_price
                holding['market_value'] = market_value
                total_market_value += market_value
            
            portfolio['calculated_stock_value'] = total_market_value
        else:
            portfolio['holdings'] = []
            portfolio['holdings_count'] = 0
        
        return {
            "success": True,
            "data": portfolio
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取投资组合详情出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取投资组合详情失败: {str(e)}")

@router.put("/portfolios/{portfolio_id}")
async def update_portfolio(portfolio_id: str, update_data: Dict[str, Any] = Body(...)):
    """更新投资组合"""
    try:
        result = simple_db_adapter.update_portfolio(portfolio_id, update_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "投资组合更新成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新投资组合出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新投资组合失败: {str(e)}")

# ==================== 持仓管理 ====================

@router.post("/holdings")
async def create_holding(holding_data: Dict[str, Any] = Body(...)):
    """创建持仓"""
    try:
        result = simple_db_adapter.create_holding(holding_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "持仓创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"创建持仓出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建持仓失败: {str(e)}")

@router.get("/holdings")
async def get_holdings(portfolio_id: Optional[str] = Query(None)):
    """获取持仓列表"""
    try:
        result = simple_db_adapter.get_holdings(portfolio_id)
        return {
            "success": True,
            "data": result['data']
        }
    except Exception as e:
        logger.error(f"获取持仓列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取持仓列表失败: {str(e)}")

@router.put("/holdings/{holding_id}")
async def update_holding(holding_id: str, update_data: Dict[str, Any] = Body(...)):
    """更新持仓"""
    try:
        result = simple_db_adapter.update_holding(holding_id, update_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "持仓更新成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"更新持仓出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新持仓失败: {str(e)}")

# ==================== 交易记录管理 ====================

@router.post("/transactions")
async def create_transaction(transaction_data: Dict[str, Any] = Body(...)):
    """创建交易记录"""
    try:
        result = simple_db_adapter.create_transaction(transaction_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "交易记录创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except Exception as e:
        logger.error(f"创建交易记录出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建交易记录失败: {str(e)}")

@router.get("/transactions")
async def get_transactions(
    portfolio_id: Optional[str] = Query(None),
    stock_code: Optional[str] = Query(None)
):
    """获取交易记录"""
    try:
        result = simple_db_adapter.get_transactions(portfolio_id, stock_code)
        return {
            "success": True,
            "data": result['data']
        }
    except Exception as e:
        logger.error(f"获取交易记录出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")

# ==================== 系统配置管理 ====================

@router.get("/config")
async def get_system_config(key: Optional[str] = Query(None)):
    """获取系统配置"""
    try:
        result = simple_db_adapter.get_system_config(key)
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        logger.error(f"获取系统配置出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.put("/config/{key}")
async def update_system_config(
    key: str, 
    config_data: Dict[str, Any] = Body(...)
):
    """更新系统配置"""
    try:
        value = config_data.get('value')
        description = config_data.get('description')
        
        result = simple_db_adapter.update_system_config(key, value, description)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "系统配置更新成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新系统配置出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新系统配置失败: {str(e)}")

# ==================== 数据管理 ====================

@router.delete("/cleanup")
async def cleanup_test_data(data_types: Optional[List[str]] = Query(None)):
    """清理测试数据"""
    try:
        result = simple_db_adapter.cleanup_test_data(data_types)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": f"清理完成，删除了 {result['data']['cleaned_count']} 条记录"
            }
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清理测试数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理测试数据失败: {str(e)}")
