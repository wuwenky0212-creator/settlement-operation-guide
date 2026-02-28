"""Event repository"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.event import EventRecord
from app.schemas.common import PaginationParams


class EventRepository:
    """事件仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_external_id(
        self,
        external_id: str,
        pagination: PaginationParams
    ) -> tuple[List[EventRecord], int]:
        """根据外部流水号查询事件列表"""
        query = self.db.query(EventRecord).filter(
            EventRecord.external_id == external_id
        )
        
        # 获取总记录数
        total_count = query.count()
        
        # 按修改日降序排列
        query = query.order_by(EventRecord.modified_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def find_by_transaction_id(
        self,
        transaction_id: str,
        pagination: PaginationParams
    ) -> tuple[List[EventRecord], int]:
        """根据交易流水号查询事件列表"""
        query = self.db.query(EventRecord).filter(
            EventRecord.transaction_id == transaction_id
        )
        
        # 获取总记录数
        total_count = query.count()
        
        # 按修改日降序排列
        query = query.order_by(EventRecord.modified_date.desc())
        
        # 应用分页
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        results = query.all()
        
        return results, total_count
    
    def find_by_event_id(self, event_id: str) -> EventRecord:
        """根据事件ID查询事件"""
        return self.db.query(EventRecord).filter(
            EventRecord.event_id == event_id
        ).first()
    
    def create(self, event: EventRecord) -> EventRecord:
        """创建事件记录"""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def exists(self, event_id: str) -> bool:
        """检查事件是否存在"""
        return self.db.query(EventRecord).filter(
            EventRecord.event_id == event_id
        ).count() > 0
