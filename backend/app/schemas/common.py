"""Common schemas"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description='页码（从1开始）')
    page_size: int = Field(default=20, ge=1, le=100, description='每页记录数')
    sort_by: Optional[str] = Field(None, description='排序字段')
    sort_order: Optional[str] = Field('DESC', description='排序方向')


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    current_page: int = Field(..., description='当前页码')
    total_pages: int = Field(..., description='总页数')
    total_records: int = Field(..., description='记录总数')
    page_size: int = Field(..., description='每页记录数')


class PagedResult(BaseModel, Generic[T]):
    """Paged result"""
    data: List[T] = Field(..., description='当前页数据')
    pagination: PaginationMeta = Field(..., description='分页信息')
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response"""
    code: str = Field(..., description='错误代码')
    message: str = Field(..., description='错误消息')
    details: Optional[dict] = Field(None, description='详细信息')
    timestamp: str = Field(..., description='时间戳')
    request_id: str = Field(..., description='请求ID')
