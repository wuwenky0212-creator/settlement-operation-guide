"""Cash flow API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.query_service import QueryService
from app.services.status_tracking_service import StatusTrackingService
from app.services.operation_guide_service import OperationGuideService
from app.schemas.cash_flow import (
    CashFlowQueryCriteria,
    CashFlowSummary,
    CashFlowDetail
)
from app.schemas.payment_progress import PaymentProgress
from app.schemas.common import PaginationParams, PagedResult


router = APIRouter(prefix="/api/cash-flows", tags=["cash-flows"])


@router.get("", response_model=PagedResult[CashFlowSummary])
async def query_cash_flows(
    transaction_id: Optional[str] = Query(None, description="交易流水号"),
    cash_flow_id: Optional[str] = Query(None, description="现金流内部ID"),
    payment_info_id: Optional[str] = Query(None, description="收付信息ID"),
    settlement_id: Optional[str] = Query(None, description="结算内部ID"),
    direction: Optional[str] = Query(None, description="方向(RECEIVE/PAY)"),
    currency: Optional[str] = Query(None, description="币种"),
    amount_min: Optional[float] = Query(None, description="最小金额"),
    amount_max: Optional[float] = Query(None, description="最大金额"),
    payment_date_from: Optional[str] = Query(None, description="收付日期起始"),
    payment_date_to: Optional[str] = Query(None, description="收付日期结束"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """
    查询现金流列表
    
    支持多条件组合查询，返回分页结果
    """
    # 构建查询条件
    criteria = CashFlowQueryCriteria(
        transaction_id=transaction_id,
        cash_flow_id=cash_flow_id,
        payment_info_id=payment_info_id,
        settlement_id=settlement_id,
        direction=direction,
        currency=currency,
        amount_min=amount_min,
        amount_max=amount_max,
        payment_date_from=payment_date_from,
        payment_date_to=payment_date_to,
        status=status
    )
    
    # 构建分页参数
    pagination = PaginationParams(
        page=page,
        page_size=page_size
    )
    
    # 执行查询
    query_service = QueryService(db)
    result = query_service.query_cash_flows(criteria, pagination)
    
    return result


@router.get("/{cash_flow_id}", response_model=CashFlowDetail)
async def get_cash_flow_detail(
    cash_flow_id: str,
    db: Session = Depends(get_db)
):
    """
    查询现金流详情
    
    Args:
        cash_flow_id: 现金流内部ID
    
    Returns:
        CashFlowDetail: 现金流详情
    """
    query_service = QueryService(db)
    detail = query_service.get_cash_flow_detail(cash_flow_id)
    
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": f"未找到对应的现金流记录",
                "details": {
                    "resourceType": "CashFlow",
                    "resourceId": cash_flow_id
                }
            }
        )
    
    return detail


@router.get("/{cash_flow_id}/progress", response_model=PaymentProgress)
async def get_cash_flow_progress(
    cash_flow_id: str,
    db: Session = Depends(get_db)
):
    """
    查询现金流收付进度（4阶段流程）
    
    Args:
        cash_flow_id: 现金流内部ID
    
    Returns:
        PaymentProgress: 4阶段收付进度信息
    """
    status_tracking_service = StatusTrackingService(db)
    try:
        progress = status_tracking_service.get_cash_flow_progress(cash_flow_id)
        return progress
    except ValueError as e:
        error_msg = str(e)
        if "RESOURCE_NOT_FOUND" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise


@router.get("/{cash_flow_id}/operation-guide")
async def get_cash_flow_operation_guide(
    cash_flow_id: str,
    db: Session = Depends(get_db)
):
    """
    查询现金流操作指引
    
    Args:
        cash_flow_id: 现金流内部ID
    
    Returns:
        OperationGuide: 操作指引信息
    """
    operation_guide_service = OperationGuideService(db)
    try:
        guide = operation_guide_service.get_cash_flow_guide(cash_flow_id)
        return guide
    except ValueError as e:
        error_msg = str(e)
        if "RESOURCE_NOT_FOUND" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise
