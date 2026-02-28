"""Tests for status tracking service"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.status_tracking_service import StatusTrackingService
from app.models.transaction import Transaction
from app.models.cash_flow import CashFlow
from app.models.enums import (
    ProductType, TransactionStatus, BackOfficeStatus,
    SettlementMethod, ConfirmationType, TransactionSource,
    MatchStatus, Direction, CashFlowStatus
)


class TestStatusTrackingService:
    """状态跟踪服务测试"""
    
    def test_get_transaction_progress_returns_lifecycle_progress(self, db_session: Session):
        """测试获取交易生命周期进度返回正确的进度信息"""
        # 创建测试交易
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime(2026, 1, 1),
            trade_date=datetime(2026, 1, 1),
            value_date=datetime(2026, 1, 2),
            maturity_date=datetime(2026, 2, 1),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank A',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            confirmation_match_status=MatchStatus.MATCHED,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='INST-001',
            trader='Trader A',
            version=1,
            last_modified_date=datetime(2026, 1, 1, 10, 0, 0),
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 执行测试
        service = StatusTrackingService(db_session)
        progress = service.get_transaction_progress('TXN-001')
        
        # 验证结果
        assert progress is not None
        assert progress.current_stage is not None
        assert progress.current_status is not None
        assert 0 <= progress.progress_percentage <= 100
        assert len(progress.status_receipts) > 0
        assert len(progress.flow_visualization) > 0
    
    def test_get_transaction_progress_raises_error_for_nonexistent_transaction(self, db_session: Session):
        """测试查询不存在的交易时抛出错误"""
        service = StatusTrackingService(db_session)
        
        with pytest.raises(ValueError, match='RESOURCE_NOT_FOUND'):
            service.get_transaction_progress('NONEXISTENT')
    
    def test_get_cash_flow_progress_returns_payment_progress(self, db_session: Session):
        """测试获取现金流收付进度返回正确的进度信息"""
        # 先创建交易
        transaction = Transaction(
            external_id='EXT-005',
            transaction_id='TXN-005',
            entry_date=datetime(2026, 1, 1),
            trade_date=datetime(2026, 1, 1),
            value_date=datetime(2026, 1, 2),
            maturity_date=datetime(2026, 2, 1),
            account='ACC-005',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank E',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='INST-005',
            trader='Trader E',
            version=1,
            last_modified_date=datetime(2026, 1, 1, 14, 0, 0),
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 创建现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-001',
            transaction_id='TXN-005',
            direction=Direction.RECEIVE,
            currency='USD',
            amount=100000.0,
            payment_date=datetime(2026, 1, 2),
            account_number='1234567890',
            account_name='Test Account',
            bank_name='Test Bank',
            bank_code='TEST001',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.AML_APPROVED,
            progress_percentage=33,
            version=1,
            last_modified_date=datetime(2026, 1, 1, 15, 0, 0)
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 执行测试
        service = StatusTrackingService(db_session)
        progress = service.get_cash_flow_progress('CF-001')
        
        # 验证结果
        assert progress is not None
        assert progress.current_stage is not None
        assert progress.current_status is not None
        assert 0 <= progress.progress_percentage <= 100
        assert len(progress.status_receipts) > 0
        assert len(progress.flow_visualization) > 0
    
    def test_get_cash_flow_progress_raises_error_for_nonexistent_cash_flow(self, db_session: Session):
        """测试查询不存在的现金流时抛出错误"""
        service = StatusTrackingService(db_session)
        
        with pytest.raises(ValueError, match='RESOURCE_NOT_FOUND'):
            service.get_cash_flow_progress('NONEXISTENT')
