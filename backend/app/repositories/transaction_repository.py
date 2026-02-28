"""Transaction repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionQueryCriteria
from app.schemas.common import PaginationParams


class TransactionRepository:
    """交易仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_external_id(self, external_id: str) -> Optional[Transaction]:
        """根据外部流水号查询交易"""
        return self.db.query(Transaction).filter(
            Transaction.external_id == external_id
        ).first()
    
    def find_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """根据交易流水号查询交易"""
        return self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
    
    def find_by_criteria(
        self,
        criteria: TransactionQueryCriteria,
        pagination: PaginationParams
    ) -> tuple[List[Transaction], int]:
        """根据条件查询交易"""
        query = self.db.query(Transaction)
        
        # 应用查询条件
        filters = []
        
        if criteria.external_id:
            filters.append(Transaction.external_id == criteria.external_id)
        
        if criteria.status:
            filters.append(Transaction.status == criteria.status)
        
        if criteria.trade_date_from:
            filters.append(Transaction.trade_date >= criteria.trade_date_from)
        
        if criteria.trade_date_to:
            filters.append(Transaction.trade_date <= criteria.trade_date_to)
        
        if criteria.value_date_from:
            filters.append(Transaction.value_date >= criteria.value_date_from)
        
        if criteria.value_date_to:
            filters.append(Transaction.value_date <= criteria.value_date_to)
        
        if criteria.maturity_date_from:
            filters.append(Transaction.maturity_date >= criteria.maturity_date_from)
        
        if criteria.maturity_date_to:
            filters.append(Transaction.maturity_date <= criteria.maturity_date_to)
        
        if criteria.counterparty:
            filters.append(Transaction.counterparty.like(f'%{criteria.counterparty}%'))
        
        if criteria.product:
            filters.append(Transaction.product == criteria.product)
        
        if criteria.operating_institution:
            filters.append(Transaction.operating_institution == criteria.operating_institution)
        
        if criteria.business_institution:
            filters.append(Transaction.business_institution == criteria.business_institution)
        
        if criteria.settlement_method:
            filters.append(Transaction.settlement_method == criteria.settlement_method)
        
        if criteria.confirmation_type:
            filters.append(Transaction.confirmation_type == criteria.confirmation_type)
        
        if criteria.source:
            filters.append(Transaction.source == criteria.source)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取总记录数
        total_count = query.count()
        
        # 应用排序
        sort_by = pagination.sort_by or 'trade_date'
        sort_order = pagination.sort_order or 'DESC'
        
        if hasattr(Transaction, sort_by):
            order_column = getattr(Transaction, sort_by)
            if sort_order.upper() == 'DESC':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            # 默认按交易日降序
            query = query.order_by(Transaction.trade_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def create(self, transaction: Transaction) -> Transaction:
        """创建交易"""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update(self, transaction: Transaction) -> Transaction:
        """更新交易"""
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update_status(
        self,
        external_id: str,
        status: str,
        version: int,
        last_modified_by: str
    ) -> bool:
        """更新交易状态（使用乐观锁）"""
        result = self.db.query(Transaction).filter(
            and_(
                Transaction.external_id == external_id,
                Transaction.version == version
            )
        ).update({
            'status': status,
            'version': Transaction.version + 1,
            'last_modified_by': last_modified_by
        }, synchronize_session=False)
        
        self.db.commit()
        return result > 0
    
    def exists(self, external_id: str) -> bool:
        """检查交易是否存在"""
        return self.db.query(Transaction).filter(
            Transaction.external_id == external_id
        ).count() > 0
    
    def delete(self, external_id: str) -> bool:
        """删除交易"""
        result = self.db.query(Transaction).filter(
            Transaction.external_id == external_id
        ).delete()
        self.db.commit()
        return result > 0
