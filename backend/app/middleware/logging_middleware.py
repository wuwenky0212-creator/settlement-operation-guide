"""Logging middleware"""
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    记录所有HTTP请求和响应的详细信息
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应
        """
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求ID（由错误处理中间件设置）
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # 记录请求信息
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_host': request.client.host if request.client else 'unknown'
            }
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'process_time': process_time
            }
        )
        
        # 添加响应头
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time'] = f"{process_time:.3f}"
        
        return response


def logging_middleware(app):
    """
    添加日志中间件到应用
    
    Args:
        app: FastAPI应用实例
    """
    app.add_middleware(LoggingMiddleware)
