"""Tests for EventService"""
import pytest
from datetime import datetime
from app.services.event_service import EventService
from app.schemas.event import EventRecordCreate
from app.schemas.common import PaginationParams
from app.models.enums import ProductType, TransactionStatus, BackOfficeStatus, MatchStatus
from app.models.event import EventRecord


class TestEventService:
    """Test EventService"""
    
    def test_query_events_by_external_id_returns_events(self, db_session):
        """测试通过外部流水号查询事件返回正确的事件列表"""
        # 准备测试数据
        service = EventService(db_session)
        external_id = "EXT-001"
        
        # 创建多个事件
        for i in range(3):
            event = EventRecord(
                event_id=f"EVT-{i}",
                external_id=external_id,
                transaction_id=f"TXN-{i}",
                product=ProductType.FX_SPOT,
                account="ACC-001",
                event_type="BOOKED",
                transaction_status=TransactionStatus.EFFECTIVE,
                entry_date=datetime(2026, 2, 27, 10, 0, 0),
                trade_date=datetime(2026, 2, 27),
                modified_date=datetime(2026, 2, 27, 10, i, 0),
                back_office_status=BackOfficeStatus.CONFIRMED,
                operator="user1"
            )
            db_session.add(event)
        db_session.commit()
        
        # 执行查询
        result = service.query_events(external_id=external_id)
        
        # 验证结果
        assert len(result.data) == 3
        assert result.pagination.total_records == 3
        assert result.pagination.current_page == 1
        assert all(event.external_id == external_id for event in result.data)
    
    def test_query_events_by_transaction_id_returns_events(self, db_session):
        """测试通过交易流水号查询事件返回正确的事件列表"""
        # 准备测试数据
        service = EventService(db_session)
        transaction_id = "TXN-001"
        
        # 创建事件
        event = EventRecord(
            event_id="EVT-001",
            external_id="EXT-001",
            transaction_id=transaction_id,
            product=ProductType.FX_FORWARD,
            account="ACC-001",
            event_type="MATURED",
            transaction_status=TransactionStatus.MATURED,
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            modified_date=datetime(2026, 2, 27, 10, 0, 0),
            back_office_status=BackOfficeStatus.COMPLETED,
            operator="user1"
        )
        db_session.add(event)
        db_session.commit()
        
        # 执行查询
        result = service.query_events(transaction_id=transaction_id)
        
        # 验证结果
        assert len(result.data) == 1
        assert result.data[0].transaction_id == transaction_id
    
    def test_query_events_returns_empty_list_when_no_events_found(self, db_session):
        """测试当没有事件时返回空列表"""
        service = EventService(db_session)
        
        # 查询不存在的外部流水号
        result = service.query_events(external_id="NON-EXISTENT")
        
        # 验证结果
        assert len(result.data) == 0
        assert result.pagination.total_records == 0
    
    def test_query_events_raises_error_when_no_criteria_provided(self, db_session):
        """测试当未提供查询条件时抛出错误"""
        service = EventService(db_session)
        
        # 执行查询（不提供任何条件）
        with pytest.raises(ValueError, match='MISSING_REQUIRED_FIELD'):
            service.query_events()
    
    def test_query_events_sorted_by_modified_date_descending(self, db_session):
        """测试事件按修改日降序排列"""
        # 准备测试数据
        service = EventService(db_session)
        external_id = "EXT-001"
        
        # 创建多个事件，修改日期不同
        dates = [
            datetime(2026, 2, 25, 10, 0, 0),
            datetime(2026, 2, 27, 10, 0, 0),
            datetime(2026, 2, 26, 10, 0, 0),
        ]
        
        for i, date in enumerate(dates):
            event = EventRecord(
                event_id=f"EVT-{i}",
                external_id=external_id,
                transaction_id=f"TXN-{i}",
                product=ProductType.FX_SPOT,
                account="ACC-001",
                event_type="BOOKED",
                transaction_status=TransactionStatus.EFFECTIVE,
                entry_date=datetime(2026, 2, 27, 10, 0, 0),
                trade_date=datetime(2026, 2, 27),
                modified_date=date,
                back_office_status=BackOfficeStatus.CONFIRMED,
                operator="user1"
            )
            db_session.add(event)
        db_session.commit()
        
        # 执行查询
        result = service.query_events(external_id=external_id)
        
        # 验证排序（应该按修改日降序）
        assert len(result.data) == 3
        assert result.data[0].modified_date >= result.data[1].modified_date
        assert result.data[1].modified_date >= result.data[2].modified_date
    
    def test_query_events_with_pagination(self, db_session):
        """测试分页功能"""
        # 准备测试数据
        service = EventService(db_session)
        external_id = "EXT-001"
        
        # 创建5个事件
        for i in range(5):
            event = EventRecord(
                event_id=f"EVT-{i}",
                external_id=external_id,
                transaction_id=f"TXN-{i}",
                product=ProductType.FX_SPOT,
                account="ACC-001",
                event_type="BOOKED",
                transaction_status=TransactionStatus.EFFECTIVE,
                entry_date=datetime(2026, 2, 27, 10, 0, 0),
                trade_date=datetime(2026, 2, 27),
                modified_date=datetime(2026, 2, 27, 10, i, 0),
                back_office_status=BackOfficeStatus.CONFIRMED,
                operator="user1"
            )
            db_session.add(event)
        db_session.commit()
        
        # 执行查询（每页2条，第1页）
        pagination = PaginationParams(page=1, page_size=2)
        result = service.query_events(external_id=external_id, pagination=pagination)
        
        # 验证结果
        assert len(result.data) == 2
        assert result.pagination.total_records == 5
        assert result.pagination.total_pages == 3
        assert result.pagination.current_page == 1
        assert result.pagination.page_size == 2
    
    def test_record_event_creates_new_event(self, db_session):
        """测试记录新事件成功创建"""
        service = EventService(db_session)
        
        # 准备事件数据
        event_data = EventRecordCreate(
            event_id="EVT-NEW-001",
            external_id="EXT-001",
            transaction_id="TXN-001",
            parent_transaction_id=None,
            product=ProductType.FX_SWAP,
            account="ACC-001",
            event_type="PAYMENT-DAILY",
            transaction_status=TransactionStatus.EFFECTIVE,
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            modified_date=datetime(2026, 2, 27, 10, 0, 0),
            back_office_status=BackOfficeStatus.SETTLED_PENDING_REPORT,
            confirmation_status="CONFIRMED",
            confirmation_match_status=MatchStatus.MATCHED,
            operator="user1"
        )
        
        # 记录事件
        result = service.record_event(event_data)
        
        # 验证结果
        assert result.event_id == "EVT-NEW-001"
        assert result.external_id == "EXT-001"
        assert result.transaction_id == "TXN-001"
        assert result.event_type == "PAYMENT-DAILY"
        assert result.operator == "user1"
        
        # 验证数据库中存在该事件
        db_event = db_session.query(EventRecord).filter(
            EventRecord.event_id == "EVT-NEW-001"
        ).first()
        assert db_event is not None
        assert db_event.event_id == "EVT-NEW-001"
    
    def test_record_event_raises_error_when_event_id_exists(self, db_session):
        """测试当事件ID已存在时抛出错误"""
        service = EventService(db_session)
        
        # 先创建一个事件
        existing_event = EventRecord(
            event_id="EVT-EXISTING",
            external_id="EXT-001",
            transaction_id="TXN-001",
            product=ProductType.FX_SPOT,
            account="ACC-001",
            event_type="BOOKED",
            transaction_status=TransactionStatus.EFFECTIVE,
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            modified_date=datetime(2026, 2, 27, 10, 0, 0),
            back_office_status=BackOfficeStatus.CONFIRMED,
            operator="user1"
        )
        db_session.add(existing_event)
        db_session.commit()
        
        # 尝试创建相同ID的事件
        event_data = EventRecordCreate(
            event_id="EVT-EXISTING",
            external_id="EXT-002",
            transaction_id="TXN-002",
            product=ProductType.FX_SPOT,
            account="ACC-002",
            event_type="BOOKED",
            transaction_status=TransactionStatus.EFFECTIVE,
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            modified_date=datetime(2026, 2, 27, 10, 0, 0),
            back_office_status=BackOfficeStatus.CONFIRMED,
            operator="user2"
        )
        
        # 验证抛出错误
        with pytest.raises(ValueError, match='RESOURCE_ALREADY_EXISTS'):
            service.record_event(event_data)
    
    def test_record_event_with_all_optional_fields(self, db_session):
        """测试记录包含所有可选字段的事件"""
        service = EventService(db_session)
        
        # 准备包含所有字段的事件数据
        event_data = EventRecordCreate(
            event_id="EVT-FULL-001",
            external_id="EXT-001",
            transaction_id="TXN-001",
            parent_transaction_id="PARENT-TXN-001",
            product=ProductType.BOND_TRADING,
            account="ACC-001",
            event_type="MATURED",
            transaction_status=TransactionStatus.MATURED,
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            modified_date=datetime(2026, 2, 27, 10, 0, 0),
            back_office_status=BackOfficeStatus.COMPLETED,
            confirmation_status="CONFIRMED",
            confirmation_match_status=MatchStatus.MATCHED,
            operator="user1"
        )
        
        # 记录事件
        result = service.record_event(event_data)
        
        # 验证所有字段
        assert result.event_id == "EVT-FULL-001"
        assert result.parent_transaction_id == "PARENT-TXN-001"
        assert result.confirmation_status == "CONFIRMED"
        assert result.confirmation_match_status == MatchStatus.MATCHED
