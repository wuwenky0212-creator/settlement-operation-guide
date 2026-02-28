"""Accounting repository"""
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.accounting import AccountingRecord
from app.schemas.common import PaginationParams


class AccountingRepository:
    """账务仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_transaction_id(
        self,
        transaction_id: str,
        pagination: PaginationParams
    ) -> tuple[List[AccountingRecord], int]:
        """根据交易流水号查询账务记录列表"""
        query = self.db.query(AccountingRecord).filter(
            AccountingRecord.transaction_id == transaction_id
        )
        
        # 获取总记录数
        total_count = query.count()
        
        # 按实际记账日降序排列
        query = query.order_by(AccountingRecord.actual_accounting_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def find_by_voucher_id(self, voucher_id: str) -> AccountingRecord:
        """根据传票号查询账务记录"""
        return self.db.query(AccountingRecord).filter(
            AccountingRecord.voucher_id == voucher_id
        ).first()
    
    def get_amount_summary_by_currency(
        self,
        transaction_id: str
    ) -> Dict[str, Dict[str, float]]:
        """按币种汇总借贷金额"""
        records = self.db.query(AccountingRecord).filter(
            AccountingRecord.transaction_id == transaction_id
        ).all()
        
        summary = {}
        for record in records:
            currency = record.currency
            if currency not in summary:
                summary[currency] = {'debit': 0.0, 'credit': 0.0}
            
            if record.debit_credit_indicator.value == 'DEBIT':
                summary[currency]['debit'] += record.transaction_amount
            else:
                summary[currency]['credit'] += record.transaction_amount
        
        return summary
    
    def create(self, accounting_record: AccountingRecord) -> AccountingRecord:
        """创建账务记录"""
        self.db.add(accounting_record)
        self.db.commit()
        self.db.refresh(accounting_record)
        return accounting_record
    
    def exists(self, voucher_id: str) -> bool:
        """检查账务记录是否存在"""
        return self.db.query(AccountingRecord).filter(
            AccountingRecord.voucher_id == voucher_id
        ).count() > 0
