"""Transaction API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.query_service import QueryService
from app.services.event_service import EventService
from app.services.accounting_service import AccountingService
from app.services.status_tracking_service import StatusTrackingService
from app.services.operation_guide_service import OperationGuideService
from app.schemas.transaction import (
    TransactionQueryCriteria,
    TransactionSummary,
    TransactionDetail
)
from app.schemas.event import EventRecordResponse
from app.schemas.accounting import AccountingRecordResponse, PaymentInfo
from app.schemas.common import PaginationParams, PagedResult


router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=PagedResult[TransactionSummary])
async def query_transactions(
    external_id: Optional[str] = Query(None, description="外部流水号"),
    status: Optional[str] = Query(None, description="交易状态"),
    trade_date_from: Optional[str] = Query(None, description="交易日起始"),
    trade_date_to: Optional[str] = Query(None, description="交易日结束"),
    value_date_from: Optional[str] = Query(None, description="起息日起始"),
    value_date_to: Optional[str] = Query(None, description="起息日结束"),
    maturity_date_from: Optional[str] = Query(None, description="到期日起始"),
    maturity_date_to: Optional[str] = Query(None, description="到期日结束"),
    counterparty: Optional[str] = Query(None, description="交易对手"),
    product: Optional[str] = Query(None, description="产品"),
    currency: Optional[str] = Query(None, description="货币"),
    operating_institution: Optional[str] = Query(None, description="运营机构"),
    business_institution: Optional[str] = Query(None, description="业务机构"),
    settlement_method: Optional[str] = Query(None, description="清算方式"),
    confirmation_type: Optional[str] = Query(None, description="证实方式"),
    source: Optional[str] = Query(None, description="交易来源"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数"),
    sort_by: Optional[str] = Query("trade_date", description="排序字段"),
    sort_order: Optional[str] = Query("DESC", description="排序方向"),
    db: Session = Depends(get_db)
):
    """
    查询交易汇总列表
    
    支持多条件组合查询，返回分页结果
    """
    # 构建查询条件
    criteria = TransactionQueryCriteria(
        external_id=external_id,
        status=status,
        trade_date_from=trade_date_from,
        trade_date_to=trade_date_to,
        value_date_from=value_date_from,
        value_date_to=value_date_to,
        maturity_date_from=maturity_date_from,
        maturity_date_to=maturity_date_to,
        counterparty=counterparty,
        product=product,
        currency=currency,
        operating_institution=operating_institution,
        business_institution=business_institution,
        settlement_method=settlement_method,
        confirmation_type=confirmation_type,
        source=source
    )
    
    # 构建分页参数
    pagination = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # 执行查询
    query_service = QueryService(db)
    result = query_service.query_transactions(criteria, pagination)
    
    return result


@router.get("/{external_id}", response_model=TransactionDetail)
async def get_transaction_detail(
    external_id: str,
    db: Session = Depends(get_db)
):
    """
    查询交易详情
    
    Args:
        external_id: 外部流水号
    
    Returns:
        TransactionDetail: 交易详情
    """
    query_service = QueryService(db)
    detail = query_service.get_transaction_detail(external_id)
    
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": f"未找到对应的交易记录",
                "details": {
                    "resourceType": "Transaction",
                    "resourceId": external_id
                }
            }
        )
    
    return detail


@router.get("/{external_id}/events", response_model=PagedResult[EventRecordResponse])
async def get_transaction_events(
    external_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(15, ge=1, le=100, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """
    查询交易的事件记录列表
    
    Args:
        external_id: 外部流水号
        page: 页码
        page_size: 每页记录数
    
    Returns:
        PagedResult[EventRecordResponse]: 分页的事件记录列表
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    
    event_service = EventService(db)
    try:
        result = event_service.query_events(
            external_id=external_id,
            pagination=pagination
        )
        return result
    except ValueError as e:
        error_msg = str(e)
        if "MISSING_REQUIRED_FIELD" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise


@router.get("/{transaction_id}/payment-info", response_model=PaymentInfo)
async def get_payment_info(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    查询交易的支付信息
    
    Args:
        transaction_id: 交易流水号
    
    Returns:
        PaymentInfo: 支付信息
    """
    accounting_service = AccountingService(db)
    try:
        payment_info = accounting_service.get_payment_info(transaction_id)
        return payment_info
    except ValueError as e:
        error_msg = str(e)
        if "RESOURCE_NOT_FOUND" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise


@router.get("/{transaction_id}/accounting-records", response_model=PagedResult[AccountingRecordResponse])
async def get_accounting_records(
    transaction_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(15, ge=1, le=100, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """
    查询交易的账务记录列表
    
    Args:
        transaction_id: 交易流水号
        page: 页码
        page_size: 每页记录数
    
    Returns:
        PagedResult[AccountingRecordResponse]: 分页的账务记录列表
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    
    accounting_service = AccountingService(db)
    result = accounting_service.query_accounting_records(
        transaction_id=transaction_id,
        pagination=pagination
    )
    
    return result


@router.get("/{transaction_id}/accounting-summary")
async def get_accounting_summary(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    查询交易的账务金额汇总
    
    Args:
        transaction_id: 交易流水号
    
    Returns:
        Dict: 按币种汇总的借贷金额
    """
    accounting_service = AccountingService(db)
    summary = accounting_service.get_amount_summary(transaction_id)
    
    return summary


@router.get("/{transaction_id}/progress")
async def get_transaction_progress(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    查询交易生命周期进度
    
    Args:
        transaction_id: 交易流水号
    
    Returns:
        LifecycleProgress: 生命周期进度信息
    """
    status_tracking_service = StatusTrackingService(db)
    try:
        progress = status_tracking_service.get_transaction_progress(transaction_id)
        return progress
    except ValueError as e:
        error_msg = str(e)
        if "RESOURCE_NOT_FOUND" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise


@router.get("/{transaction_id}/operation-guide")
async def get_operation_guide(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    查询交易操作指引
    
    Args:
        transaction_id: 交易流水号
    
    Returns:
        OperationGuide: 操作指引信息
    """
    operation_guide_service = OperationGuideService(db)
    try:
        guide = operation_guide_service.get_transaction_guide(transaction_id)
        return guide
    except ValueError as e:
        error_msg = str(e)
        if "RESOURCE_NOT_FOUND" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise
