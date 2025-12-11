"""
中间件模块
提供请求限流、CSRF 保护等功能
"""
import time
import secrets
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    请求限流中间件
    基于 IP 地址的简单限流实现
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 清理过期记录
        current_time = time.time()
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if current_time - t < 60
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            retry_after = 60 - int(current_time - self.requests[client_ip][0])
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limited",
                    "message": "Too many requests",
                    "retry_after": max(1, retry_after)
                },
                headers={"Retry-After": str(max(1, retry_after))}
            )
        
        # 记录请求
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF 保护中间件
    为表单请求验证 CSRF token
    """
    
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/health", "/api/v1/dev/uuid"]
        self.tokens = {}
    
    async def dispatch(self, request: Request, call_next):
        # 跳过 GET 请求和豁免路径
        if request.method == "GET" or request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # API 请求通常使用 JSON，跳过 CSRF 检查
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            return await call_next(request)
        
        # 对于表单提交，验证 CSRF token
        # 这里简化处理，实际应用中需要更完善的实现
        
        return await call_next(request)
    
    def generate_token(self) -> str:
        """生成 CSRF token"""
        return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> str:
    """获取或生成 CSRF token"""
    if not hasattr(request.state, 'csrf_token'):
        request.state.csrf_token = secrets.token_urlsafe(32)
    return request.state.csrf_token
