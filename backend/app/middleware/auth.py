"""Authentication and authorization middleware"""
import logging
from typing import Optional, List
from enum import Enum

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """权限枚举"""
    # 查询权限
    QUERY_TRANSACTIONS = "query:transactions"
    QUERY_CASH_FLOWS = "query:cash_flows"
    QUERY_EVENTS = "query:events"
    QUERY_ACCOUNTING = "query:accounting"
    
    # 导出权限
    EXPORT_TRANSACTIONS = "export:transactions"
    EXPORT_CASH_FLOWS = "export:cash_flows"
    
    # 管理权限
    ADMIN = "admin"


class User:
    """用户模型"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        permissions: List[Permission]
    ):
        self.user_id = user_id
        self.username = username
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """
        检查用户是否具有指定权限
        
        Args:
            permission: 权限
            
        Returns:
            bool: 是否具有权限
        """
        return (
            Permission.ADMIN in self.permissions or
            permission in self.permissions
        )


class AuthService:
    """
    认证服务
    
    注意：这是一个简化的实现，实际生产环境应该集成真实的认证系统
    """
    
    # 模拟的用户数据库
    _users = {
        "test-token-123": User(
            user_id="user-001",
            username="test_user",
            permissions=[
                Permission.QUERY_TRANSACTIONS,
                Permission.QUERY_CASH_FLOWS,
                Permission.QUERY_EVENTS,
                Permission.QUERY_ACCOUNTING,
                Permission.EXPORT_TRANSACTIONS,
                Permission.EXPORT_CASH_FLOWS
            ]
        ),
        "admin-token-456": User(
            user_id="admin-001",
            username="admin_user",
            permissions=[Permission.ADMIN]
        )
    }
    
    @classmethod
    def authenticate(cls, token: str) -> Optional[User]:
        """
        验证令牌并返回用户
        
        Args:
            token: 认证令牌
            
        Returns:
            Optional[User]: 用户对象，如果令牌无效则返回None
        """
        # 在实际生产环境中，这里应该：
        # 1. 验证JWT令牌
        # 2. 从数据库或缓存中获取用户信息
        # 3. 验证令牌是否过期
        
        return cls._users.get(token)
    
    @classmethod
    def authorize(cls, user: User, permission: Permission) -> bool:
        """
        检查用户是否具有指定权限
        
        Args:
            user: 用户对象
            permission: 权限
            
        Returns:
            bool: 是否具有权限
        """
        return user.has_permission(permission)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证和授权中间件
    
    验证请求的认证令牌并检查权限
    """
    
    # 不需要认证的路径
    PUBLIC_PATHS = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并验证认证
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应
        """
        # 检查是否是公开路径
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # 获取认证令牌
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(
                f"Missing authorization header for {request.url.path}",
                extra={'path': request.url.path}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "缺少认证令牌"
                }
            )
        
        # 解析令牌
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            logger.warning(
                f"Invalid authorization header format for {request.url.path}",
                extra={'path': request.url.path}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "无效的认证令牌格式"
                }
            )
        
        # 验证令牌
        user = AuthService.authenticate(token)
        
        if user is None:
            logger.warning(
                f"Invalid token for {request.url.path}",
                extra={'path': request.url.path}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "无效的认证令牌"
                }
            )
        
        # 将用户信息添加到请求状态
        request.state.user = user
        
        # 检查权限（基于路径）
        required_permission = self._get_required_permission(request.url.path)
        
        if required_permission and not AuthService.authorize(user, required_permission):
            logger.warning(
                f"Permission denied for user {user.username} on {request.url.path}",
                extra={
                    'user_id': user.user_id,
                    'username': user.username,
                    'path': request.url.path,
                    'required_permission': required_permission.value
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "没有权限访问该资源"
                }
            )
        
        # 记录认证成功
        logger.info(
            f"User {user.username} authenticated for {request.url.path}",
            extra={
                'user_id': user.user_id,
                'username': user.username,
                'path': request.url.path
            }
        )
        
        return await call_next(request)
    
    def _get_required_permission(self, path: str) -> Optional[Permission]:
        """
        根据路径获取所需权限
        
        Args:
            path: 请求路径
            
        Returns:
            Optional[Permission]: 所需权限，如果不需要特定权限则返回None
        """
        # 交易查询权限
        if path.startswith("/api/transactions"):
            return Permission.QUERY_TRANSACTIONS
        
        # 现金流查询权限
        if path.startswith("/api/cash-flows"):
            return Permission.QUERY_CASH_FLOWS
        
        # 导出权限
        if path.startswith("/api/export/transactions"):
            return Permission.EXPORT_TRANSACTIONS
        
        if path.startswith("/api/export/cash-flows"):
            return Permission.EXPORT_CASH_FLOWS
        
        # 默认需要查询权限
        return Permission.QUERY_TRANSACTIONS


def auth_middleware(app):
    """
    添加认证中间件到应用
    
    Args:
        app: FastAPI应用实例
    """
    app.add_middleware(AuthMiddleware)


# 依赖注入函数
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security
) -> User:
    """
    获取当前用户（用于依赖注入）
    
    Args:
        credentials: HTTP认证凭证
        
    Returns:
        User: 当前用户
        
    Raises:
        HTTPException: 如果认证失败
    """
    user = AuthService.authenticate(credentials.credentials)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "无效的认证令牌"
            }
        )
    
    return user


def require_permission(permission: Permission):
    """
    权限检查装饰器（用于依赖注入）
    
    Args:
        permission: 所需权限
        
    Returns:
        Callable: 依赖函数
    """
    async def permission_checker(user: User = get_current_user) -> User:
        """
        检查用户权限
        
        Args:
            user: 当前用户
            
        Returns:
            User: 当前用户
            
        Raises:
            HTTPException: 如果权限不足
        """
        if not AuthService.authorize(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "没有权限访问该资源"
                }
            )
        
        return user
    
    return permission_checker
