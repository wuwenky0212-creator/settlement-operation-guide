"""Tests for AccountingService"""
import pytest
from datetime import datetime
from app.services.accounting_service import AccountingService
from app.models.accounting import AccountingRecord
from app.models.cash_flow import CashFlow
from app.models.enums import (
    DebitCreditIndicator,
    Direction,
    SettlementMethod,
    CashFlowStatus
)
from app.schemas.common import PaginationParams


class TestAccountingService:
    """Test AccountingService"""
    
    def test_get_payment_info_returns_payment_information(self, db_session):
        """测试获取支付信息返回正确的支付信息"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建现金流记录
        cash_flow = CashFlow(
            cash_flow_id="CF-001",
            transaction_id=transaction_id,
            payment_info_id="PAY-001",
            settlement_id="SETTLE-001",
            direction=Direction.RECEIVE,
            currency="USD",
            amount=10000.0,
            payment_date=datetime(2026, 2, 28),
            account_number="ACC-001",
            account_name="Test Account",
            bank_name="Test Bank",
            bank_code="TB001",
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.CORE_SUCCESS,
            progress_percentage=100,
            version=1,
            last_modified_date=datetime(2026, 2, 27, 10, 0, 0)
        )
        db_session.add(cash_flow)
        db_session.commit()
        
        # 执行查询
        result = service.get_payment_info(transaction_id)
        
        # 验证结果
        assert result.our_bank_name == "Test Bank"
        assert result.our_bank_code == "TB001"
        assert result.our_account_name == "Test Account"
        assert result.our_account_number == "ACC-001"
        assert result.instruction_id == "PAY-001"
        assert result.payment_date == datetime(2026, 2, 28)
        assert result.currency == "USD"
        assert result.amount == 10000.0
    
    def test_get_payment_info_raises_error_when_no_cash_flow_found(self, db_session):
        """测试当没有现金流记录时抛出错误"""
        service = AccountingService(db_session)
        
        # 查询不存在的交易
        with pytest.raises(ValueError, match='RESOURCE_NOT_FOUND'):
            service.get_payment_info("NON-EXISTENT")
    
    def test_query_accounting_records_returns_records(self, db_session):
        """测试查询账务记录返回正确的记录列表"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建多个账务记录
        for i in range(3):
            record = AccountingRecord(
                voucher_id=f"VOUCHER-{i}",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, i, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number=f"EVT-{i}",
                debit_credit_indicator=DebitCreditIndicator.DEBIT if i % 2 == 0 else DebitCreditIndicator.CREDIT,
                currency="USD",
                account_subject=f"SUBJECT-{i}",
                transaction_amount=1000.0 * (i + 1)
            )
            db_session.add(record)
        db_session.commit()
        
        # 执行查询
        result = service.query_accounting_records(transaction_id)
        
        # 验证结果
        assert len(result.data) == 3
        assert result.pagination.total_records == 3
        assert result.pagination.current_page == 1
        assert all(record.transaction_id == transaction_id for record in result.data)
    
    def test_query_accounting_records_returns_empty_list_when_no_records_found(self, db_session):
        """测试当没有账务记录时返回空列表"""
        service = AccountingService(db_session)
        
        # 查询不存在的交易
        result = service.query_accounting_records("NON-EXISTENT")
        
        # 验证结果
        assert len(result.data) == 0
        assert result.pagination.total_records == 0
    
    def test_query_accounting_records_sorted_by_actual_accounting_date_descending(self, db_session):
        """测试账务记录按实际记账日降序排列"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建多个账务记录，实际记账日期不同
        dates = [
            datetime(2026, 2, 25, 10, 0, 0),
            datetime(2026, 2, 27, 10, 0, 0),
            datetime(2026, 2, 26, 10, 0, 0),
        ]
        
        for i, date in enumerate(dates):
            record = AccountingRecord(
                voucher_id=f"VOUCHER-{i}",
                transaction_id=transaction_id,
                actual_accounting_date=date,
                planned_accounting_date=datetime(2026, 2, 27),
                event_number=f"EVT-{i}",
                debit_credit_indicator=DebitCreditIndicator.DEBIT,
                currency="USD",
                account_subject=f"SUBJECT-{i}",
                transaction_amount=1000.0
            )
            db_session.add(record)
        db_session.commit()
        
        # 执行查询
        result = service.query_accounting_records(transaction_id)
        
        # 验证排序（应该按实际记账日降序）
        assert len(result.data) == 3
        assert result.data[0].actual_accounting_date >= result.data[1].actual_accounting_date
        assert result.data[1].actual_accounting_date >= result.data[2].actual_accounting_date
    
    def test_query_accounting_records_with_pagination(self, db_session):
        """测试分页功能"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建5个账务记录
        for i in range(5):
            record = AccountingRecord(
                voucher_id=f"VOUCHER-{i}",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, i, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number=f"EVT-{i}",
                debit_credit_indicator=DebitCreditIndicator.DEBIT,
                currency="USD",
                account_subject=f"SUBJECT-{i}",
                transaction_amount=1000.0
            )
            db_session.add(record)
        db_session.commit()
        
        # 执行查询（每页2条，第1页）
        pagination = PaginationParams(page=1, page_size=2)
        result = service.query_accounting_records(transaction_id, pagination)
        
        # 验证结果
        assert len(result.data) == 2
        assert result.pagination.total_records == 5
        assert result.pagination.total_pages == 3
        assert result.pagination.current_page == 1
        assert result.pagination.page_size == 2
    
    def test_get_amount_summary_returns_correct_summary(self, db_session):
        """测试金额汇总返回正确的汇总结果"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建多个账务记录，包含不同币种和借贷方向
        records = [
            # USD - 借方
            AccountingRecord(
                voucher_id="VOUCHER-1",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, 0, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number="EVT-1",
                debit_credit_indicator=DebitCreditIndicator.DEBIT,
                currency="USD",
                account_subject="SUBJECT-1",
                transaction_amount=1000.0
            ),
            # USD - 借方
            AccountingRecord(
                voucher_id="VOUCHER-2",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, 1, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number="EVT-2",
                debit_credit_indicator=DebitCreditIndicator.DEBIT,
                currency="USD",
                account_subject="SUBJECT-2",
                transaction_amount=500.0
            ),
            # USD - 贷方
            AccountingRecord(
                voucher_id="VOUCHER-3",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, 2, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number="EVT-3",
                debit_credit_indicator=DebitCreditIndicator.CREDIT,
                currency="USD",
                account_subject="SUBJECT-3",
                transaction_amount=800.0
            ),
            # CNY - 借方
            AccountingRecord(
                voucher_id="VOUCHER-4",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, 3, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number="EVT-4",
                debit_credit_indicator=DebitCreditIndicator.DEBIT,
                currency="CNY",
                account_subject="SUBJECT-4",
                transaction_amount=7000.0
            ),
            # CNY - 贷方
            AccountingRecord(
                voucher_id="VOUCHER-5",
                transaction_id=transaction_id,
                actual_accounting_date=datetime(2026, 2, 27, 10, 4, 0),
                planned_accounting_date=datetime(2026, 2, 27),
                event_number="EVT-5",
                debit_credit_indicator=DebitCreditIndicator.CREDIT,
                currency="CNY",
                account_subject="SUBJECT-5",
                transaction_amount=3500.0
            ),
        ]
        
        for record in records:
            db_session.add(record)
        db_session.commit()
        
        # 执行汇总
        result = service.get_amount_summary(transaction_id)
        
        # 验证结果
        assert "USD" in result
        assert "CNY" in result
        
        # USD: 借方 1000 + 500 = 1500, 贷方 800
        assert result["USD"]["debit"] == 1500.0
        assert result["USD"]["credit"] == 800.0
        
        # CNY: 借方 7000, 贷方 3500
        assert result["CNY"]["debit"] == 7000.0
        assert result["CNY"]["credit"] == 3500.0
    
    def test_get_amount_summary_returns_empty_dict_when_no_records(self, db_session):
        """测试当没有账务记录时返回空字典"""
        service = AccountingService(db_session)
        
        # 查询不存在的交易
        result = service.get_amount_summary("NON-EXISTENT")
        
        # 验证结果
        assert result == {}
    
    def test_query_accounting_records_includes_all_required_fields(self, db_session):
        """测试账务记录包含所有必需字段"""
        # 准备测试数据
        service = AccountingService(db_session)
        transaction_id = "TXN-001"
        
        # 创建账务记录
        record = AccountingRecord(
            voucher_id="VOUCHER-001",
            transaction_id=transaction_id,
            actual_accounting_date=datetime(2026, 2, 27, 10, 0, 0),
            planned_accounting_date=datetime(2026, 2, 27),
            event_number="EVT-001",
            debit_credit_indicator=DebitCreditIndicator.DEBIT,
            currency="USD",
            account_subject="SUBJECT-001",
            transaction_amount=1000.0
        )
        db_session.add(record)
        db_session.commit()
        
        # 执行查询
        result = service.query_accounting_records(transaction_id)
        
        # 验证所有必需字段都存在
        assert len(result.data) == 1
        record_response = result.data[0]
        
        assert record_response.voucher_id == "VOUCHER-001"
        assert record_response.transaction_id == transaction_id
        assert record_response.actual_accounting_date == datetime(2026, 2, 27, 10, 0, 0)
        assert record_response.planned_accounting_date == datetime(2026, 2, 27)
        assert record_response.event_number == "EVT-001"
        assert record_response.debit_credit_indicator == DebitCreditIndicator.DEBIT
        assert record_response.currency == "USD"
        assert record_response.account_subject == "SUBJECT-001"
        assert record_response.transaction_amount == 1000.0
