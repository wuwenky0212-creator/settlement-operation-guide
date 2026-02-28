"""Cash flow repository"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.cash_flow import CashFlow
from app.schemas.cash_flow import CashFlowQueryCriteria
from app.schemas.common import PaginationParams


class CashFlowRepository:
    """现金流仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_cash_flow_id(self, cash_flow_id: str) -> Optional[CashFlow]:
        """根据现金流ID查询现金流"""
        return self.db.query(CashFlow).filter(
            CashFlow.cash_flow_id == cash_flow_id
        ).first()
    
    def find_by_transaction_id(
        self,
        transaction_id: str,
        pagination: PaginationParams
    ) -> tuple[List[CashFlow], int]:
        """根据交易流水号查询现金流列表"""
        query = self.db.query(CashFlow).filter(
            CashFlow.transaction_id == transaction_id
        )
        
        # 获取总记录数
        total_count = query.count()
        
        # 按收付日期降序排列
        query = query.order_by(CashFlow.payment_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def find_by_criteria(
        self,
        criteria: CashFlowQueryCriteria,
        pagination: PaginationParams
    ) -> tuple[List[CashFlow], int]:
        """根据条件查询现金流"""
        query = self.db.query(CashFlow)
        
        # 应用查询条件
        filters = []
        
        if criteria.transaction_id:
            filters.append(CashFlow.transaction_id == criteria.transaction_id)
        
        if criteria.cash_flow_id:
            filters.append(CashFlow.cash_flow_id == criteria.cash_flow_id)
        
        if criteria.payment_info_id:
            filters.append(CashFlow.payment_info_id == criteria.payment_info_id)
        
        if criteria.settlement_id:
            filters.append(CashFlow.settlement_id == criteria.settlement_id)
        
        if criteria.direction:
            filters.append(CashFlow.direction == criteria.direction)
        
        if criteria.currency:
            filters.append(CashFlow.currency == criteria.currency)
        
        if criteria.amount_min is not None:
            filters.append(CashFlow.amount >= criteria.amount_min)
        
        if criteria.amount_max is not None:
            filters.append(CashFlow.amount <= criteria.amount_max)
        
        if criteria.payment_date_from:
            filters.append(CashFlow.payment_date >= criteria.payment_date_from)
        
        if criteria.payment_date_to:
            filters.append(CashFlow.payment_date <= criteria.payment_date_to)
        
        if criteria.status:
            filters.append(CashFlow.current_status == criteria.status)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取总记录数
        total_count = query.count()
        
        # 按收付日期降序排列
        query = query.order_by(CashFlow.payment_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def get_amount_summary(
        self,
        criteria: CashFlowQueryCriteria
    ) -> Dict[str, Dict[str, float]]:
        """按币种和方向汇总金额"""
        query = self.db.query(CashFlow)
        
        # 应用查询条件（与find_by_criteria相同的逻辑）
        filters = []
        
        if criteria.transaction_id:
            filters.append(CashFlow.transaction_id == criteria.transaction_id)
        
        if criteria.cash_flow_id:
            filters.append(CashFlow.cash_flow_id == criteria.cash_flow_id)
        
        if criteria.payment_info_id:
            filters.append(CashFlow.payment_info_id == criteria.payment_info_id)
        
        if criteria.settlement_id:
            filters.append(CashFlow.settlement_id == criteria.settlement_id)
        
        if criteria.direction:
            filters.append(CashFlow.direction == criteria.direction)
        
        if criteria.currency:
            filters.append(CashFlow.currency == criteria.currency)
        
        if criteria.amount_min is not None:
            filters.append(CashFlow.amount >= criteria.amount_min)
        
        if criteria.amount_max is not None:
            filters.append(CashFlow.amount <= criteria.amount_max)
        
        if criteria.payment_date_from:
            filters.append(CashFlow.payment_date >= criteria.payment_date_from)
        
        if criteria.payment_date_to:
            filters.append(CashFlow.payment_date <= criteria.payment_date_to)
        
        if criteria.status:
            filters.append(CashFlow.current_status == criteria.status)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取所有记录
        records = query.all()
        
        # 按币种和方向汇总
        summary = {}
        for record in records:
            currency = record.currency
            direction = record.direction.value
            
            if currency not in summary:
                summary[currency] = {}
            
            if direction not in summary[currency]:
                summary[currency][direction] = 0.0
            
            summary[currency][direction] += record.amount
        
        return summary
    
    def create(self, cash_flow: CashFlow) -> CashFlow:
        """创建现金流"""
        self.db.add(cash_flow)
        self.db.commit()
        self.db.refresh(cash_flow)
        return cash_flow
    
    def update(self, cash_flow: CashFlow) -> CashFlow:
        """更新现金流"""
        self.db.commit()
        self.db.refresh(cash_flow)
        return cash_flow
    
    def update_status(
        self,
        cash_flow_id: str,
        status: str,
        progress_percentage: int,
        version: int
    ) -> bool:
        """更新现金流状态（使用乐观锁）"""
        result = self.db.query(CashFlow).filter(
            and_(
                CashFlow.cash_flow_id == cash_flow_id,
                CashFlow.version == version
            )
        ).update({
            'current_status': status,
            'progress_percentage': progress_percentage,
            'version': CashFlow.version + 1
        }, synchronize_session=False)
        
        self.db.commit()
        return result > 0
    
    def exists(self, cash_flow_id: str) -> bool:
        """检查现金流是否存在"""
        return self.db.query(CashFlow).filter(
            CashFlow.cash_flow_id == cash_flow_id
        ).count() > 0
    
    def delete(self, cash_flow_id: str) -> bool:
        """删除现金流"""
        result = self.db.query(CashFlow).filter(
            CashFlow.cash_flow_id == cash_flow_id
        ).delete()
        self.db.commit()
        return result > 0
