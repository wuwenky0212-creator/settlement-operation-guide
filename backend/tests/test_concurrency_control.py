"""Tests for concurrency control service"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.concurrency_control import (
    ConcurrencyControl,
    TransactionConcurrencyControl,
    CashFlowConcurrencyControl,
    Lock,
    OptimisticLockError,
    EntityNotFoundError
)
from app.models.transaction import Transaction
from app.models.cash_flow import CashFlow
from app.models.enums import (
    ProductType, TransactionStatus, BackOfficeStatus,
    SettlementMethod, ConfirmationType, TransactionSource,
    Direction, CashFlowStatus
)


@pytest.fixture
def db(db_session):
    """Alias for db_session fixture"""
    return db_session


class TestConcurrencyControl:
    """测试并发控制基类"""
    
    def test_acquire_optimistic_lock_returns_lock_object(self, db: Session):
        """获取乐观锁应返回锁对象"""
        control = ConcurrencyControl(db)
        lock = control.acquire_optimistic_lock("test-id", 1)
        
        assert isinstance(lock, Lock)
        assert lock.entity_id == "test-id"
        assert lock.version == 1
        assert isinstance(lock.acquired_at, datetime)
    
    def test_release_lock_does_not_raise_error(self, db: Session):
        """释放锁不应抛出错误"""
        control = ConcurrencyControl(db)
        lock = Lock(entity_id="test-id", version=1, acquired_at=datetime.now())
        
        # 应该不抛出错误
        control.release_lock(lock)
    
    def test_get_current_version_returns_none_for_nonexistent_entity(self, db: Session):
        """获取不存在实体的版本号应返回None"""
        control = ConcurrencyControl(db)
        version = control.get_current_version(Transaction, "nonexistent-id")
        
        assert version is None
    
    def test_verify_version_returns_false_for_nonexistent_entity(self, db: Session):
        """验证不存在实体的版本号应返回False"""
        control = ConcurrencyControl(db)
        result = control.verify_version(Transaction, "nonexistent-id", 1)
        
        assert result is False


class TestTransactionConcurrencyControl:
    """测试交易并发控制"""
    
    def test_update_with_version_check_succeeds_when_version_matches(self, db: Session):
        """当版本号匹配时更新应成功"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-001",
            transaction_id="TXN-001",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-001",
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying="USD/CNY",
            counterparty="Bank A",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature="Normal",
            source=TransactionSource.GIT,
            operating_institution="BOCHK",
            trader="Trader A",
            version=1,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        # 使用并发控制更新
        control = TransactionConcurrencyControl(db)
        control.update_with_version_check(
            Transaction,
            "EXT-001",
            1,
            {"status": TransactionStatus.MATURED}
        )
        
        # 验证更新成功
        db.refresh(transaction)
        assert transaction.status == TransactionStatus.MATURED
        assert transaction.version == 2
    
    def test_update_with_version_check_raises_error_when_version_mismatch(self, db: Session):
        """当版本号不匹配时更新应抛出OptimisticLockError"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-002",
            transaction_id="TXN-002",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-002",
            product=ProductType.FX_FORWARD,
            direction=Direction.SELL,
            underlying="EUR/USD",
            counterparty="Bank B",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.NET,
            confirmation_type=ConfirmationType.SWIFT,
            nature="Normal",
            source=TransactionSource.FXO,
            operating_institution="BOCHK",
            trader="Trader B",
            version=2,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        # 尝试使用错误的版本号更新
        control = TransactionConcurrencyControl(db)
        with pytest.raises(OptimisticLockError) as exc_info:
            control.update_with_version_check(
                Transaction,
                "EXT-002",
                1,  # 期望版本号为1，但实际为2
                {"status": TransactionStatus.MATURED}
            )
        
        # 验证错误信息
        assert exc_info.value.entity_id == "EXT-002"
        assert exc_info.value.expected_version == 1
        assert exc_info.value.actual_version == 2
        
        # 验证交易未被更新
        db.refresh(transaction)
        assert transaction.status == TransactionStatus.EFFECTIVE
        assert transaction.version == 2
    
    def test_update_with_version_check_raises_error_when_entity_not_found(self, db: Session):
        """当实体不存在时更新应抛出EntityNotFoundError"""
        control = TransactionConcurrencyControl(db)
        
        with pytest.raises(EntityNotFoundError) as exc_info:
            control.update_with_version_check(
                Transaction,
                "NONEXISTENT",
                1,
                {"status": TransactionStatus.MATURED}
            )
        
        assert exc_info.value.entity_id == "NONEXISTENT"
    
    def test_detect_conflict_returns_true_when_version_mismatch(self, db: Session):
        """当版本号不匹配时detect_conflict应返回True"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-003",
            transaction_id="TXN-003",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-003",
            product=ProductType.FX_SWAP,
            direction=Direction.BUY,
            underlying="GBP/USD",
            counterparty="Bank C",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.CENTRALIZED,
            confirmation_type=ConfirmationType.TEXT,
            nature="Normal",
            source=TransactionSource.FXS,
            operating_institution="BOCHK",
            trader="Trader C",
            version=3,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        control = TransactionConcurrencyControl(db)
        has_conflict = control.detect_conflict("EXT-003", 1)
        
        assert has_conflict is True
    
    def test_detect_conflict_returns_false_when_version_matches(self, db: Session):
        """当版本号匹配时detect_conflict应返回False"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-004",
            transaction_id="TXN-004",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-004",
            product=ProductType.INTERBANK_LENDING,
            direction=Direction.BUY,
            underlying="CNY",
            counterparty="Bank D",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.NOT_REQUIRED,
            confirmation_type=ConfirmationType.NO_CONFIRMATION,
            nature="Normal",
            source=TransactionSource.GIT,
            operating_institution="BOCHK",
            trader="Trader D",
            version=1,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        control = TransactionConcurrencyControl(db)
        has_conflict = control.detect_conflict("EXT-004", 1)
        
        assert has_conflict is False
    
    def test_get_current_version_returns_correct_version(self, db: Session):
        """获取当前版本号应返回正确的版本"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-005",
            transaction_id="TXN-005",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-005",
            product=ProductType.MONEY_MARKET_DEPOSIT,
            direction=Direction.BUY,
            underlying="USD",
            counterparty="Bank E",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature="Normal",
            source=TransactionSource.GIT,
            operating_institution="BOCHK",
            trader="Trader E",
            version=5,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        control = TransactionConcurrencyControl(db)
        version = control.get_current_version(Transaction, "EXT-005")
        
        assert version == 5


class TestCashFlowConcurrencyControl:
    """测试现金流并发控制"""
    
    def test_update_cash_flow_with_version_check_succeeds(self, db: Session):
        """现金流版本号匹配时更新应成功"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id="CF-001",
            transaction_id="TXN-001",
            direction=Direction.RECEIVE,
            currency="USD",
            amount=10000.0,
            payment_date=datetime.now(),
            account_number="1234567890",
            account_name="Test Account",
            bank_name="Test Bank",
            bank_code="TEST001",
            settlement_method=SettlementMethod.GROSS,
            current_status=CashFlowStatus.PENDING_AML,
            progress_percentage=0,
            version=1,
            last_modified_date=datetime.now()
        )
        db.add(cash_flow)
        db.commit()
        
        # 使用并发控制更新
        control = CashFlowConcurrencyControl(db)
        control.update_with_version_check(
            CashFlow,
            "CF-001",
            1,
            {"current_status": CashFlowStatus.AML_APPROVED, "progress_percentage": 30},
            id_field='cash_flow_id'
        )
        
        # 验证更新成功
        db.refresh(cash_flow)
        assert cash_flow.current_status == CashFlowStatus.AML_APPROVED
        assert cash_flow.progress_percentage == 30
        assert cash_flow.version == 2
    
    def test_detect_conflict_for_cash_flow(self, db: Session):
        """现金流版本号不匹配时detect_conflict应返回True"""
        # 创建测试现金流
        cash_flow = CashFlow(
            cash_flow_id="CF-002",
            transaction_id="TXN-002",
            direction=Direction.PAY,
            currency="CNY",
            amount=50000.0,
            payment_date=datetime.now(),
            account_number="9876543210",
            account_name="Test Account 2",
            bank_name="Test Bank 2",
            bank_code="TEST002",
            settlement_method=SettlementMethod.NET,
            current_status=CashFlowStatus.PENDING_SWIFT,
            progress_percentage=50,
            version=2,
            last_modified_date=datetime.now()
        )
        db.add(cash_flow)
        db.commit()
        
        control = CashFlowConcurrencyControl(db)
        has_conflict = control.detect_conflict("CF-002", 1)
        
        assert has_conflict is True


class TestConcurrentUpdates:
    """测试并发更新场景"""
    
    def test_concurrent_updates_one_succeeds_one_fails(self, db: Session):
        """模拟两个并发更新，一个成功一个失败"""
        # 创建测试交易
        transaction = Transaction(
            external_id="EXT-CONCURRENT",
            transaction_id="TXN-CONCURRENT",
            entry_date=datetime.now(),
            trade_date=datetime.now(),
            value_date=datetime.now(),
            maturity_date=datetime.now(),
            account="ACC-CONCURRENT",
            product=ProductType.FX_SPOT,
            direction=Direction.BUY,
            underlying="USD/CNY",
            counterparty="Bank Concurrent",
            status=TransactionStatus.EFFECTIVE,
            back_office_status=BackOfficeStatus.CONFIRMED,
            settlement_method=SettlementMethod.GROSS,
            confirmation_type=ConfirmationType.SWIFT,
            nature="Normal",
            source=TransactionSource.GIT,
            operating_institution="BOCHK",
            trader="Trader Concurrent",
            version=1,
            last_modified_by="system"
        )
        db.add(transaction)
        db.commit()
        
        # 第一个用户的更新（应该成功）
        control1 = TransactionConcurrencyControl(db)
        control1.update_with_version_check(
            Transaction,
            "EXT-CONCURRENT",
            1,
            {"status": TransactionStatus.MATURED}
        )
        
        # 第二个用户的更新（应该失败，因为版本号已经变化）
        control2 = TransactionConcurrencyControl(db)
        with pytest.raises(OptimisticLockError):
            control2.update_with_version_check(
                Transaction,
                "EXT-CONCURRENT",
                1,  # 仍然使用旧版本号
                {"back_office_status": BackOfficeStatus.COMPLETED}
            )
        
        # 验证只有第一个更新生效
        db.refresh(transaction)
        assert transaction.status == TransactionStatus.MATURED
        assert transaction.back_office_status == BackOfficeStatus.CONFIRMED
        assert transaction.version == 2
