from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Dict
from pydantic import BaseModel

from backend.auth.auth_service import AuthService

# 创建路由
router = APIRouter(prefix="/auth", tags=["认证"])

# 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    expires_at: datetime

# 添加测试路由
@router.get("/test")
async def test_api():
    """
    测试API是否正常工作
    """
    return {"message": "API服务器正常工作", "status": "ok"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录并获取访问令牌
    
    使用此端点进行用户认证并获取JWT令牌
    """
    user = AuthService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    # 计算过期时间
    expires_at = datetime.utcnow() + access_token_expires
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "expires_at": expires_at
    }

@router.get("/me", response_model=Dict)
async def read_users_me(current_user: Dict = Depends(AuthService.get_current_active_user)):
    """
    获取当前用户信息
    
    此端点返回当前已认证用户的信息
    """
    # 移除敏感信息
    user_info = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return user_info 
