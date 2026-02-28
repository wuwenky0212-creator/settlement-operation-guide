"""Accounting service for managing accounting records and payment information"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.repositories.accounting_repository import AccountingRepository
from app.repositories.cash_flow_repository import CashFlowRepository
from app.schemas.accounting import AccountingRecordResponse, PaymentInfo
from app.schemas.common import PaginationParams, PagedResult, PaginationMeta


class AccountingService:
    """账务服务"""
    
    def __init__(self, db: Session):
        """
        Initialize accounting service
        
        Args:
            db: Database session
        """
        self.db = db
        self.accounting_repository = AccountingRepository(db)
        self.cash_flow_repository = CashFlowRepository(db)
    
    def get_payment_info(self, transaction_id: str) -> PaymentInfo:
        """
        查询支付信息
        
        Args:
            transaction_id: 交易流水号
        
        Returns:
            PaymentInfo: 支付信息
        
        Raises:
            ValueError: 当交易不存在或没有现金流记录时
        """
        # 查询交易的现金流记录（获取第一条作为支付信息）
        pagination = PaginationParams(page=1, page_size=1)
        cash_flows, total_count = self.cash_flow_repository.find_by_transaction_id(
            transaction_id=transaction_id,
            pagination=pagination
        )
        
        if total_count == 0:
            raise ValueError(f'RESOURCE_NOT_FOUND: No cash flow found for transaction {transaction_id}')
        
        cash_flow = cash_flows[0]
        
        # 构建支付信息
        # 注意：根据设计文档，支付信息包含我行和对手方的账户信息
        # 这里我们从现金流中获取账户信息，并构造支付信息
        # 实际实现中，可能需要从多个现金流记录中获取完整的支付信息
        
        payment_info = PaymentInfo(
            # 清算方式 - 我行信息
            our_bank_name=cash_flow.bank_name,
            our_bank_code=cash_flow.bank_code,
            our_account_name=cash_flow.account_name,
            our_account_number=cash_flow.account_number,
            
            # 清算方式 - 对手方信息（从其他现金流记录获取，这里暂时使用占位符）
            counterparty_bank_name="Counterparty Bank",  # TODO: 从对手方现金流获取
            counterparty_bank_code="CP001",
            counterparty_account_name="Counterparty Account",
            counterparty_account_number="CP-ACCOUNT-001",
            
            # 支付信息
            instruction_id=cash_flow.payment_info_id or cash_flow.cash_flow_id,
            payment_date=cash_flow.payment_date,
            message_type="pacs.008",  # TODO: 从实际数据获取
            currency=cash_flow.currency,
            amount=cash_flow.amount,
            message_sender="SYSTEM",  # TODO: 从实际数据获取
            message_send_time=cash_flow.last_modified_date
        )
        
        return payment_info
    
    def query_accounting_records(
        self,
        transaction_id: str,
        pagination: Optional[PaginationParams] = None
    ) -> PagedResult[AccountingRecordResponse]:
        """
        查询账务记录列表
        
        Args:
            transaction_id: 交易流水号
            pagination: 分页参数
        
        Returns:
            PagedResult[AccountingRecordResponse]: 分页的账务记录列表
        """
        # 使用默认分页参数
        if pagination is None:
            pagination = PaginationParams(page=1, page_size=15)
        
        # 查询账务记录
        records, total_count = self.accounting_repository.find_by_transaction_id(
            transaction_id=transaction_id,
            pagination=pagination
        )
        
        # 计算总页数
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
        
        # 构建分页元数据
        pagination_meta = PaginationMeta(
            current_page=pagination.page,
            total_pages=total_pages,
            total_records=total_count,
            page_size=pagination.page_size
        )
        
        # 转换为响应模型
        record_responses = [
            AccountingRecordResponse.model_validate(record)
            for record in records
        ]
        
        return PagedResult(
            data=record_responses,
            pagination=pagination_meta
        )
    
    def get_amount_summary(self, transaction_id: str) -> Dict[str, Dict[str, float]]:
        """
        按币种汇总借贷金额
        
        Args:
            transaction_id: 交易流水号
        
        Returns:
            Dict[str, Dict[str, float]]: 按币种汇总的借贷金额
            格式: {
                'USD': {'debit': 1000.0, 'credit': 500.0},
                'CNY': {'debit': 7000.0, 'credit': 3500.0}
            }
        """
        return self.accounting_repository.get_amount_summary_by_currency(transaction_id)
