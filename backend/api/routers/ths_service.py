"""
禁用模拟数据的API文件
系统要求真实数据源
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/account_info")
async def get_account_info():
    """获取账户信息 - 禁用模拟数据"""
    raise HTTPException(
        status_code=400, 
        detail="❌ 系统禁止返回模拟账户数据，请配置真实交易API接口"
    )

@router.get("/positions")
async def get_positions():
    """获取持仓信息 - 禁用模拟数据"""
    raise HTTPException(
        status_code=400,
        detail="❌ 系统禁止返回模拟持仓数据，请配置真实交易API接口"
    )
