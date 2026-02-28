"""Error handling middleware"""
import logging
import traceback
import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.common import ErrorResponse


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    统一错误处理中间件
    
    捕获所有未处理的异常并返回标准化的错误响应
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并捕获异常
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # HTTPException should be handled by FastAPI's default handler
            # Re-raise it to let FastAPI handle it
            raise
        except ValueError as e:
            # 业务逻辑错误
            return self._handle_value_error(e, request_id)
        except Exception as e:
            # 未预期的错误
            return self._handle_unexpected_error(e, request, request_id)
    
    def _handle_value_error(self, error: ValueError, request_id: str) -> JSONResponse:
        """
        处理ValueError（业务逻辑错误）
        
        Args:
            error: ValueError异常
            request_id: 请求ID
            
        Returns:
            JSONResponse: 错误响应
        """
        error_msg = str(error)
        
        # 解析错误代码和消息
        if ':' in error_msg:
            parts = error_msg.split(':', 1)
            error_code = parts[0].strip()
            error_message = parts[1].strip()
        else:
            error_code = 'BUSINESS_ERROR'
            error_message = error_msg
        
        # 根据错误代码确定HTTP状态码
        status_code_map = {
            'INVALID_PARAMETER': status.HTTP_400_BAD_REQUEST,
            'MISSING_REQUIRED_FIELD': status.HTTP_400_BAD_REQUEST,
            'RESOURCE_NOT_FOUND': status.HTTP_404_NOT_FOUND,
            'RESOURCE_ALREADY_EXISTS': status.HTTP_409_CONFLICT,
            'CONCURRENT_CONFLICT': status.HTTP_409_CONFLICT,
            'EXPORT_LIMIT_EXCEEDED': status.HTTP_400_BAD_REQUEST,
            'UNAUTHORIZED': status.HTTP_401_UNAUTHORIZED,
            'FORBIDDEN': status.HTTP_403_FORBIDDEN,
        }
        
        http_status = status_code_map.get(error_code, status.HTTP_400_BAD_REQUEST)
        
        # 构建错误响应
        error_response = ErrorResponse(
            code=error_code,
            message=error_message,
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        )
        
        # 记录错误日志
        logger.warning(
            f"Business error: {error_code} - {error_message}",
            extra={
                'request_id': request_id,
                'error_code': error_code
            }
        )
        
        return JSONResponse(
            status_code=http_status,
            content=error_response.model_dump()
        )
    
    def _handle_unexpected_error(
        self,
        error: Exception,
        request: Request,
        request_id: str
    ) -> JSONResponse:
        """
        处理未预期的错误
        
        Args:
            error: 异常对象
            request: HTTP请求
            request_id: 请求ID
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录详细的错误日志
        logger.error(
            f"Unexpected error: {str(error)}",
            extra={
                'request_id': request_id,
                'path': request.url.path,
                'method': request.method,
                'traceback': traceback.format_exc()
            }
        )
        
        # 构建错误响应（不暴露内部错误细节）
        error_response = ErrorResponse(
            code='INTERNAL_ERROR',
            message='服务器内部错误，请稍后重试',
            details={
                'error_type': type(error).__name__
            },
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


def error_handler_middleware(app):
    """
    添加错误处理中间件到应用
    
    Args:
        app: FastAPI应用实例
    """
    app.add_middleware(ErrorHandlerMiddleware)
