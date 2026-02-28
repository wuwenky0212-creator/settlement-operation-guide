"""Export API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.export_service import ExportService, ExportFormat
from app.schemas.transaction import TransactionQueryCriteria
from app.schemas.cash_flow import CashFlowQueryCriteria


router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/transactions")
async def export_transactions(
    format: str = Query("excel", description="导出格式(excel/csv)"),
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
    fields: Optional[str] = Query(None, description="导出字段(逗号分隔)"),
    db: Session = Depends(get_db)
):
    """
    导出交易列表
    
    支持Excel和CSV格式导出
    """
    # 验证导出格式
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAMETER",
                "message": f"不支持的导出格式: {format}",
                "details": {
                    "invalidFields": [
                        {
                            "field": "format",
                            "reason": "必须是 'excel' 或 'csv'"
                        }
                    ]
                }
            }
        )
    
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
    
    # 解析导出字段
    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(',')]
    
    # 执行导出
    export_service = ExportService(db)
    try:
        result = export_service.export_transactions(
            criteria=criteria,
            format=export_format,
            fields=field_list
        )
    except ValueError as e:
        error_msg = str(e)
        if "EXPORT_LIMIT_EXCEEDED" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise
    
    # 设置响应头
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if export_format == ExportFormat.EXCEL
        else "text/csv"
    )
    
    return Response(
        content=result.content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{result.filename}"'
        }
    )


@router.get("/cash-flows")
async def export_cash_flows(
    format: str = Query("excel", description="导出格式(excel/csv)"),
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
    db: Session = Depends(get_db)
):
    """
    导出现金流列表
    
    支持Excel和CSV格式导出
    """
    # 验证导出格式
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAMETER",
                "message": f"不支持的导出格式: {format}",
                "details": {
                    "invalidFields": [
                        {
                            "field": "format",
                            "reason": "必须是 'excel' 或 'csv'"
                        }
                    ]
                }
            }
        )
    
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
    
    # 执行导出
    export_service = ExportService(db)
    try:
        result = export_service.export_cash_flows(
            criteria=criteria,
            format=export_format
        )
    except ValueError as e:
        error_msg = str(e)
        if "EXPORT_LIMIT_EXCEEDED" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise
    
    # 设置响应头
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if export_format == ExportFormat.EXCEL
        else "text/csv"
    )
    
    return Response(
        content=result.content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{result.filename}"'
        }
    )
