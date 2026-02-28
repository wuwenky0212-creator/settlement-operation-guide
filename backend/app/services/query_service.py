"""Query service for transactions and cash flows"""
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.cash_flow_repository import CashFlowRepository
from app.schemas.transaction import (
    TransactionQueryCriteria,
    TransactionSummary,
    TransactionDetail
)
from app.schemas.cash_flow import (
    CashFlowQueryCriteria,
    CashFlowSummary,
    CashFlowDetail
)
from app.schemas.common import PaginationParams, PagedResult, PaginationMeta
import math


class QueryService:
    """查询服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.cash_flow_repo = CashFlowRepository(db)
    
    def query_transactions(
        self,
        criteria: TransactionQueryCriteria,
        pagination: PaginationParams
    ) -> PagedResult[TransactionSummary]:
        """
        查询交易汇总列表
        
        Args:
            criteria: 查询条件
            pagination: 分页参数
            
        Returns:
            PagedResult[TransactionSummary]: 分页的交易汇总列表
        """
        # 调用仓储层查询
        transactions, total_count = self.transaction_repo.find_by_criteria(
            criteria, pagination
        )
        
        # 转换为汇总对象
        summaries = [
            TransactionSummary.model_validate(txn)
            for txn in transactions
        ]
        
        # 计算分页元数据
        total_pages = math.ceil(total_count / pagination.page_size) if total_count > 0 else 0
        
        pagination_meta = PaginationMeta(
            current_page=pagination.page,
            total_pages=total_pages,
            total_records=total_count,
            page_size=pagination.page_size
        )
        
        return PagedResult(
            data=summaries,
            pagination=pagination_meta
        )
    
    def get_transaction_detail(self, external_id: str) -> Optional[TransactionDetail]:
        """
        查询交易详情
        
        Args:
            external_id: 外部流水号
            
        Returns:
            Optional[TransactionDetail]: 交易详情，如果不存在则返回None
        """
        transaction = self.transaction_repo.find_by_external_id(external_id)
        
        if transaction is None:
            return None
        
        return TransactionDetail.model_validate(transaction)
    
    def query_cash_flows(
        self,
        criteria: CashFlowQueryCriteria,
        pagination: PaginationParams
    ) -> PagedResult[CashFlowSummary]:
        """
        查询现金流列表
        
        Args:
            criteria: 查询条件
            pagination: 分页参数
            
        Returns:
            PagedResult[CashFlowSummary]: 分页的现金流汇总列表
        """
        # 调用仓储层查询
        cash_flows, total_count = self.cash_flow_repo.find_by_criteria(
            criteria, pagination
        )
        
        # 转换为汇总对象
        summaries = [
            CashFlowSummary.model_validate(cf)
            for cf in cash_flows
        ]
        
        # 计算分页元数据
        total_pages = math.ceil(total_count / pagination.page_size) if total_count > 0 else 0
        
        pagination_meta = PaginationMeta(
            current_page=pagination.page,
            total_pages=total_pages,
            total_records=total_count,
            page_size=pagination.page_size
        )
        
        return PagedResult(
            data=summaries,
            pagination=pagination_meta
        )
    
    def get_cash_flow_detail(self, cash_flow_id: str) -> Optional[CashFlowDetail]:
        """
        查询现金流详情
        
        Args:
            cash_flow_id: 现金流内部ID
            
        Returns:
            Optional[CashFlowDetail]: 现金流详情，如果不存在则返回None
        """
        cash_flow = self.cash_flow_repo.find_by_cash_flow_id(cash_flow_id)
        
        if cash_flow is None:
            return None
        
        return CashFlowDetail.model_validate(cash_flow)
