"""Tests for query service"""
import pytest
from datetime import datetime
from app.services.query_service import QueryService
from app.models.transaction import Transaction
from app.models.cash_flow import CashFlow
from app.models.enums import (
    ProductType, TransactionStatus, BackOfficeStatus,
    SettlementMethod, ConfirmationType, TransactionSource,
    Direction, CashFlowStatus
)
from app.schemas.transaction import TransactionQueryCriteria
from app.schemas.cash_flow import CashFlowQueryCriteria
from app.schemas.common import PaginationParams


class TestQueryService:
    """Test query service"""
    
    def test_query_transactions_returns_empty_list_when_no_matches(self, db_session):
        """当没有交易匹配条件时应返回空列表"""
        service = QueryService(db_session)
        criteria = TransactionQueryCriteria(external_id='NON-EXISTENT')
        pagination = PaginationParams(page=1, page_size=20)
        
        result = service.query_transactions(criteria, pagination)
        
        assert result.data == []
        assert result.pagination.total_records == 0
        assert result.pagination.total_pages == 0
    
    def test_query_transactions_returns_matching_transactions(self, db_session):
        """查询应返回匹配条件的交易"""
        # 创建测试数据
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            value_date=datetime(2026, 2, 28),
            maturity_date=datetime(2026, 3, 28),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank A',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader A',
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        service = QueryService(db_session)
        criteria = TransactionQueryCriteria(external_id='EXT-001')
        pagination = PaginationParams(page=1, page_size=20)
        
        result = service.query_transactions(criteria, pagination)
        
        assert len(result.data) == 1
        assert result.data[0].external_id == 'EXT-001'
        assert result.pagination.total_records == 1
        assert result.pagination.total_pages == 1
    
    def test_query_transactions_applies_pagination(self, db_session):
        """查询应正确应用分页"""
        # 创建多条测试数据
        for i in range(25):
            transaction = Transaction(
                external_id=f'EXT-{i:03d}',
                transaction_id=f'TXN-{i:03d}',
                entry_date=datetime(2026, 2, 27, 10, 0, 0),
                trade_date=datetime(2026, 2, 27 - i % 10),
                value_date=datetime(2026, 2, 28),
                maturity_date=datetime(2026, 3, 28),
                account='ACC-001',
                product=ProductType.FX_SPOT,
                direction=Direction.BUY,
                underlying='USD/CNY',
                counterparty='Bank A',
                status=TransactionStatus.EFFECTIVE,
                back_office_status=BackOfficeStatus.CONFIRMED,
                settlement_method=SettlementMethod.GROSS,
                confirmation_type=ConfirmationType.SWIFT,
                nature='Normal',
                source=TransactionSource.GIT,
                operating_institution='1530H',
                trader='Trader A',
                last_modified_by='system'
            )
            db_session.add(transaction)
        db_session.commit()
        
        service = QueryService(db_session)
        criteria = TransactionQueryCriteria()
        pagination = PaginationParams(page=1, page_size=10)
        
        result = service.query_transactions(criteria, pagination)
        
        assert len(result.data) == 10
        assert result.pagination.total_records == 25
        assert result.pagination.total_pages == 3
        assert result.pagination.current_page == 1
    
    def test_get_transaction_detail_returns_none_when_not_found(self, db_session):
        """当交易不存在时应返回None"""
        service = QueryService(db_session)
        
        result = service.get_transaction_detail('NON-EXISTENT')
        
        assert result is None
    
    def test_get_transaction_detail_returns_transaction_when_found(self, db_session):
        """当交易存在时应返回交易详情"""
        # 创建测试数据
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            value_date=datetime(2026, 2, 28),
            maturity_date=datetime(2026, 3, 28),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank A',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader A',
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        service = QueryService(db_session)
        
        result = service.get_transaction_detail('EXT-001')
        
        assert result is not None
        assert result.external_id == 'EXT-001'
        assert result.transaction_id == 'TXN-001'
        assert result.product == ProductType.FX_SPOT
    
    def test_query_cash_flows_returns_empty_list_when_no_matches(self, db_session):
        """当没有现金流匹配条件时应返回空列表"""
        service = QueryService(db_session)
        criteria = CashFlowQueryCriteria(cash_flow_id='NON-EXISTENT')
        pagination = PaginationParams(page=1, page_size=20)
        
        result = service.query_cash_flows(criteria, pagination)
        
        assert result.data == []
        assert result.pagination.total_records == 0
        assert result.pagination.total_pages == 0
    
    def test_query_cash_flows_returns_matching_cash_flows(self, db_session):
        """查询应返回匹配条件的现金流"""
        # 先创建交易
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            value_date=datetime(2026, 2, 28),
            maturity_date=datetime(2026, 3, 28),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank A',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader A',
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 创建现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-001',
            transaction_id='TXN-001',
            direction=Direction.RECEIVE,
            currency='USD',
            amount=10000.0,
            payment_date=datetime(2026, 2, 28),
            account_number='1234567890',
            account_name='Test Account',
            bank_name='Test Bank',
            bank_code='TEST001',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.PENDING_AML,
            progress_percentage=0,
            last_modified_date=datetime(2026, 2, 27, 10, 0, 0)
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        service = QueryService(db_session)
        criteria = CashFlowQueryCriteria(cash_flow_id='CF-001')
        pagination = PaginationParams(page=1, page_size=20)
        
        result = service.query_cash_flows(criteria, pagination)
        
        assert len(result.data) == 1
        assert result.data[0].cash_flow_id == 'CF-001'
        assert result.pagination.total_records == 1
    
    def test_get_cash_flow_detail_returns_none_when_not_found(self, db_session):
        """当现金流不存在时应返回None"""
        service = QueryService(db_session)
        
        result = service.get_cash_flow_detail('NON-EXISTENT')
        
        assert result is None
    
    def test_get_cash_flow_detail_returns_cash_flow_when_found(self, db_session):
        """当现金流存在时应返回现金流详情"""
        # 先创建交易
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime(2026, 2, 27, 10, 0, 0),
            trade_date=datetime(2026, 2, 27),
            value_date=datetime(2026, 2, 28),
            maturity_date=datetime(2026, 3, 28),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying='USD/CNY',
            counterparty='Bank A',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature='Normal',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader A',
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 创建现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-001',
            transaction_id='TXN-001',
            direction=Direction.RECEIVE,
            currency='USD',
            amount=10000.0,
            payment_date=datetime(2026, 2, 28),
            account_number='1234567890',
            account_name='Test Account',
            bank_name='Test Bank',
            bank_code='TEST001',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.PENDING_AML,
            progress_percentage=0,
            last_modified_date=datetime(2026, 2, 27, 10, 0, 0)
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        service = QueryService(db_session)
        
        result = service.get_cash_flow_detail('CF-001')
        
        assert result is not None
        assert result.cash_flow_id == 'CF-001'
        assert result.transaction_id == 'TXN-001'
        assert result.currency == 'USD'
        assert result.amount == 10000.0
