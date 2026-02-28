"""Event service for managing event records"""
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventRecordCreate, EventRecordResponse
from app.schemas.common import PaginationParams, PagedResult, PaginationMeta
from app.models.event import EventRecord


class EventService:
    """事件服务"""
    
    def __init__(self, db: Session):
        """
        Initialize event service
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = EventRepository(db)
    
    def query_events(
        self,
        transaction_id: Optional[str] = None,
        external_id: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> PagedResult[EventRecordResponse]:
        """
        查询事件列表
        
        Args:
            transaction_id: 交易流水号（可选）
            external_id: 外部流水号（可选）
            pagination: 分页参数
        
        Returns:
            PagedResult[EventRecordResponse]: 分页的事件记录列表
        
        Raises:
            ValueError: 当transaction_id和external_id都未提供时
        """
        # 验证至少提供一个查询条件
        if not transaction_id and not external_id:
            raise ValueError('MISSING_REQUIRED_FIELD: transaction_id or external_id is required')
        
        # 使用默认分页参数
        if pagination is None:
            pagination = PaginationParams(page=1, page_size=15)
        
        # 根据提供的条件查询
        if external_id:
            events, total_count = self.repository.find_by_external_id(
                external_id=external_id,
                pagination=pagination
            )
        else:
            events, total_count = self.repository.find_by_transaction_id(
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
        event_responses = [
            EventRecordResponse.model_validate(event)
            for event in events
        ]
        
        return PagedResult(
            data=event_responses,
            pagination=pagination_meta
        )
    
    def record_event(self, event_data: EventRecordCreate) -> EventRecordResponse:
        """
        记录新事件
        
        Args:
            event_data: 事件数据
        
        Returns:
            EventRecordResponse: 创建的事件记录
        
        Raises:
            ValueError: 当事件ID已存在时
        """
        # 检查事件ID是否已存在
        if self.repository.exists(event_data.event_id):
            raise ValueError(f'RESOURCE_ALREADY_EXISTS: Event with id {event_data.event_id} already exists')
        
        # 创建事件记录实体
        event = EventRecord(
            event_id=event_data.event_id,
            external_id=event_data.external_id,
            transaction_id=event_data.transaction_id,
            parent_transaction_id=event_data.parent_transaction_id,
            product=event_data.product,
            account=event_data.account,
            event_type=event_data.event_type,
            transaction_status=event_data.transaction_status,
            entry_date=event_data.entry_date,
            trade_date=event_data.trade_date,
            modified_date=event_data.modified_date,
            back_office_status=event_data.back_office_status,
            confirmation_status=event_data.confirmation_status,
            confirmation_match_status=event_data.confirmation_match_status,
            operator=event_data.operator
        )
        
        # 保存到数据库
        created_event = self.repository.create(event)
        
        # 返回响应模型
        return EventRecordResponse.model_validate(created_event)
