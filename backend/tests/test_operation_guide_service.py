"""Tests for operation guide service"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.operation_guide_service import (
    OperationGuideService,
    OperationGuide,
    ActionEntry
)
from app.models.transaction import Transaction
from app.models.cash_flow import CashFlow
from app.models.enums import (
    ProductType,
    TransactionStatus,
    BackOfficeStatus,
    SettlementMethod,
    ConfirmationType,
    TransactionSource,
    MatchStatus,
    CashFlowStatus,
    Direction
)


class TestOperationGuideService:
    """操作指引服务测试"""
    
    def test_get_transaction_guide_for_match_failed(self, db_session: Session):
        """测试证实匹配失败场景的操作指引"""
        # 创建测试交易
        transaction = Transaction(
            external_id='EXT-001',
            transaction_id='TXN-001',
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account='ACC-001',
            product=ProductType.FX_SPOT,
            direction='BUY',
            underlying='USD/CNY',
            counterparty='COUNTER-001',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            confirmation_match_status=MatchStatus.UNMATCHED,
            nature='普通交易',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader-001',
            version=1,
            last_modified_date=datetime.now(),
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_transaction_guide('TXN-001')
        
        # 验证
        assert guide.next_action == '联系交易对手方核对交易信息，进行人工匹配'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '人工匹配处理'
        assert guide.action_entry.action == 'manual_match'
        assert guide.notes is not None
        assert guide.estimated_time is not None
    
    def test_get_transaction_guide_for_internal_settlement(self, db_session: Session):
        """测试内部账结算场景的操作指引"""
        # 创建测试交易（内部账结算）
        transaction = Transaction(
            external_id='EXT-002',
            transaction_id='TXN-002',
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account='ACC-002',
            product=ProductType.FX_SPOT,
            direction='SELL',
            underlying='USD/CNY',
            counterparty='COUNTER-002',
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.SETTLED_PENDING_REPORT,
            settlement_method=SettlementMethod.NOT_REQUIRED,  # 内部账
            confirmation_type=ConfirmationType.NO_CONFIRMATION,
            confirmation_match_status=MatchStatus.MATCHED,
            nature='普通交易',
            source=TransactionSource.GIT,
            operating_institution='1530H',
            trader='Trader-002',
            version=1,
            last_modified_date=datetime.now(),
            last_modified_by='system'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_transaction_guide('TXN-002')
        
        # 验证
        assert guide.next_action == '等待核心系统处理'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'LINK'
        assert guide.action_entry.label == '核心系统查询'
        assert '5-10分钟' in guide.estimated_time
    
    def test_get_transaction_guide_raises_error_for_nonexistent_transaction(
        self,
        db_session: Session
    ):
        """测试查询不存在的交易时抛出错误"""
        service = OperationGuideService(db_session)
        
        with pytest.raises(ValueError, match='RESOURCE_NOT_FOUND'):
            service.get_transaction_guide('NON-EXISTENT')
    
    def test_get_cash_flow_guide_for_pending_aml(self, db_session: Session):
        """测试待反洗钱检查场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-001',
            transaction_id='TXN-001',
            direction=Direction.PAY,
            currency='USD',
            amount=10000.00,
            payment_date=datetime.now(),
            account_number='ACC-001',
            account_name='Test Account',
            bank_name='Test Bank',
            bank_code='BANK001',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.PENDING_AML,
            progress_percentage=0,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-001')
        
        # 验证
        assert guide.next_action == '等待反洗钱系统审核完成'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'LINK'
        assert guide.action_entry.label == '反洗钱系统查询'
        assert '1-2小时' in guide.estimated_time
    
    def test_get_cash_flow_guide_for_aml_rejected(self, db_session: Session):
        """测试反洗钱拒绝场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-002',
            transaction_id='TXN-002',
            direction=Direction.RECEIVE,
            currency='CNY',
            amount=50000.00,
            payment_date=datetime.now(),
            account_number='ACC-002',
            account_name='Test Account 2',
            bank_name='Test Bank 2',
            bank_code='BANK002',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.AML_REJECTED,
            progress_percentage=10,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-002')
        
        # 验证
        assert guide.next_action == '联系反洗钱部门，提供补充材料或申请人工审核'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '反洗钱人工审核申请'
        assert guide.action_entry.action == 'apply_aml_manual_review'
    
    def test_get_cash_flow_guide_for_swift_failed(self, db_session: Session):
        """测试SWIFT发送失败场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-003',
            transaction_id='TXN-003',
            direction=Direction.PAY,
            currency='EUR',
            amount=20000.00,
            payment_date=datetime.now(),
            account_number='ACC-003',
            account_name='Test Account 3',
            bank_name='Test Bank 3',
            bank_code='BANK003',
            settlement_method=SettlementMethod.NET,
            current_status=CashFlowStatus.SWIFT_FAILED,
            progress_percentage=30,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-003')
        
        # 验证
        assert guide.next_action == '检查SWIFT连接状态，联系SWIFT技术支持'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '重新发送SWIFT'
    
    def test_get_cash_flow_guide_for_core_success(self, db_session: Session):
        """测试核心入账成功场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-004',
            transaction_id='TXN-004',
            direction=Direction.RECEIVE,
            currency='USD',
            amount=30000.00,
            payment_date=datetime.now(),
            account_number='ACC-004',
            account_name='Test Account 4',
            bank_name='Test Bank 4',
            bank_code='BANK004',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.CORE_SUCCESS,
            progress_percentage=100,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-004')
        
        # 验证
        assert guide.next_action == '流程已完成，无需操作'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'LINK'
        assert guide.action_entry.label == '查看账务详情'
        assert guide.estimated_time == '已完成'
    
    def test_get_cash_flow_guide_for_core_failed(self, db_session: Session):
        """测试核心入账失败场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-005',
            transaction_id='TXN-005',
            direction=Direction.PAY,
            currency='CNY',
            amount=40000.00,
            payment_date=datetime.now(),
            account_number='ACC-005',
            account_name='Test Account 5',
            bank_name='Test Bank 5',
            bank_code='BANK005',
            settlement_method=SettlementMethod.NOT_REQUIRED,
            current_status=CashFlowStatus.CORE_FAILED,
            progress_percentage=80,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-005')
        
        # 验证
        assert guide.next_action == '查询内部账划转情况，联系核心系统支持'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '内部账划转查询'
        assert guide.action_entry.action == 'query_internal_transfer'
    
    def test_get_cash_flow_guide_for_core_unknown(self, db_session: Session):
        """测试核心入账状态不明场景的操作指引"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-006',
            transaction_id='TXN-006',
            direction=Direction.RECEIVE,
            currency='HKD',
            amount=25000.00,
            payment_date=datetime.now(),
            account_number='ACC-006',
            account_name='Test Account 6',
            bank_name='Test Bank 6',
            bank_code='BANK006',
            settlement_method=SettlementMethod.CENTRALIZED,
            current_status=CashFlowStatus.CORE_UNKNOWN,
            progress_percentage=70,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-006')
        
        # 验证
        assert guide.next_action == '查询内部账划转情况，确认入账状态'
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '内部账划转查询'
        assert '15-30分钟' in guide.estimated_time
    
    def test_get_cash_flow_guide_raises_error_for_nonexistent_cash_flow(
        self,
        db_session: Session
    ):
        """测试查询不存在的现金流时抛出错误"""
        service = OperationGuideService(db_session)
        
        with pytest.raises(ValueError, match='RESOURCE_NOT_FOUND'):
            service.get_cash_flow_guide('NON-EXISTENT')
    
    def test_operation_guide_has_all_required_fields(self, db_session: Session):
        """测试操作指引包含所有必需字段"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-007',
            transaction_id='TXN-007',
            direction=Direction.PAY,
            currency='USD',
            amount=15000.00,
            payment_date=datetime.now(),
            account_number='ACC-007',
            account_name='Test Account 7',
            bank_name='Test Bank 7',
            bank_code='BANK007',
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.PENDING_SWIFT,
            progress_percentage=40,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-007')
        
        # 验证所有必需字段都存在
        assert guide.next_action is not None
        assert isinstance(guide.next_action, str)
        assert len(guide.next_action) > 0
        
        # action_entry可以为None（某些场景不需要操作入口）
        if guide.action_entry is not None:
            assert isinstance(guide.action_entry, ActionEntry)
            assert guide.action_entry.type in ['BUTTON', 'LINK']
            assert guide.action_entry.label is not None
        
        assert guide.notes is not None
        assert guide.estimated_time is not None
    
    def test_action_entry_structure(self, db_session: Session):
        """测试操作入口的数据结构"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id='CF-008',
            transaction_id='TXN-008',
            direction=Direction.RECEIVE,
            currency='CNY',
            amount=35000.00,
            payment_date=datetime.now(),
            account_number='ACC-008',
            account_name='Test Account 8',
            bank_name='Test Bank 8',
            bank_code='BANK008',
            settlement_method=SettlementMethod.NET,
            current_status=CashFlowStatus.AML_REJECTED,
            progress_percentage=10,
            version=1,
            last_modified_date=datetime.now()
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 创建服务
        service = OperationGuideService(db_session)
        
        # 获取操作指引
        guide = service.get_cash_flow_guide('CF-008')
        
        # 验证操作入口结构
        assert guide.action_entry is not None
        assert guide.action_entry.type == 'BUTTON'
        assert guide.action_entry.label == '反洗钱人工审核申请'
        assert guide.action_entry.action == 'apply_aml_manual_review'
        # URL对于BUTTON类型可以为None
        assert guide.action_entry.url is None
