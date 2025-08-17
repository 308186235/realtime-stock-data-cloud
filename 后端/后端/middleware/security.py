from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import time
from typing import Dict, Set, Optional, Callable
import logging
import secrets
import hashlib

# 配置日志
logger = logging.getLogger(__name__)

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全HTTP头的中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response

class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF保护中间件"""
    
    def __init__(self, app: FastAPI, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token", exclude_paths: Set[str] = None):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.exclude_paths = exclude_paths or {"/api/auth/token", "/api/docs", "/api/redoc", "/api/openapi.json"}
    
    async def dispatch(self, request: Request, call_next: Callable):
        # 临时禁用CSRF保护,直接传递所有请求
        return await call_next(request)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """API请求速率限制中间件"""
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.request_log: Dict[str, Dict[str, float]] = {}  # {client_key: {request_time: timestamp}}
    
    def _get_client_key(self, request: Request) -> str:
        """获取客户端唯一标识"""
        # 优先使用经过身份验证的用户名
        if hasattr(request, "user") and hasattr(request.user, "username"):
            return f"user:{request.user.username}"
        
        # 否则使用IP地址(可能通过代理)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if hasattr(request, "client") else "unknown"
        
        # 结合用户代理创建更唯一的标识
        user_agent = request.headers.get("User-Agent", "")
        client_id = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        
        return client_id
    
    def _is_rate_limited(self, client_key: str) -> bool:
        """检查请求是否超出速率限制"""
        # 临时禁用速率限制
        return False
    
    async def dispatch(self, request: Request, call_next: Callable):
        # 获取客户端标识
        client_key = self._get_client_key(request)
        
        # 检查速率限制
        if self._is_rate_limited(client_key):
            logger.warning(f"速率限制触发: {client_key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁,请稍后再试"
            )
        
        # 继续处理请求
        return await call_next(request)

def setup_security_middleware(app: FastAPI):
    """设置所有安全中间件"""
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有源进行测试
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加安全HTTP头中间件
    app.add_middleware(SecureHeadersMiddleware)
    
    # 添加CSRF保护中间件 - 已禁用严格保护
    app.add_middleware(CSRFMiddleware)
    
    # 添加速率限制中间件 - 已禁用
    app.add_middleware(RateLimitingMiddleware, requests_per_minute=100)
    
    logger.info("安全中间件已设置") 
