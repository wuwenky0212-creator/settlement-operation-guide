"""Concurrency control service for optimistic locking"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class Lock:
    """锁对象"""
    entity_id: str
    version: int
    acquired_at: datetime


class ConcurrencyControlError(Exception):
    """并发控制错误基类"""
    pass


class OptimisticLockError(ConcurrencyControlError):
    """乐观锁冲突错误"""
    def __init__(self, entity_id: str, expected_version: int, actual_version: int):
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Optimistic lock conflict for entity {entity_id}: "
            f"expected version {expected_version}, but found {actual_version}"
        )


class EntityNotFoundError(ConcurrencyControlError):
    """实体不存在错误"""
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        super().__init__(f"Entity {entity_id} not found")


class ConcurrencyControl:
    """并发控制服务
    
    实现乐观锁机制，用于防止并发更新冲突。
    使用版本号（version）字段来检测并发冲突。
    """
    
    def __init__(self, db: Session):
        """初始化并发控制服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def acquire_optimistic_lock(
        self, 
        entity_id: str, 
        version: int
    ) -> Lock:
        """获取乐观锁
        
        乐观锁不会真正锁定记录，而是记录当前版本号。
        在更新时会检查版本号是否匹配。
        
        Args:
            entity_id: 实体ID
            version: 期望的版本号
            
        Returns:
            Lock: 锁对象
        """
        return Lock(
            entity_id=entity_id,
            version=version,
            acquired_at=datetime.now()
        )
    
    def release_lock(self, lock: Lock) -> None:
        """释放锁
        
        乐观锁不需要显式释放，此方法仅用于接口一致性。
        
        Args:
            lock: 锁对象
        """
        # 乐观锁不需要显式释放
        pass
    
    def detect_conflict(
        self, 
        entity_id: str, 
        expected_version: int
    ) -> bool:
        """检测并发冲突
        
        通过比较期望版本号和实际版本号来检测冲突。
        此方法需要子类实现具体的版本号查询逻辑。
        
        Args:
            entity_id: 实体ID
            expected_version: 期望的版本号
            
        Returns:
            bool: 如果存在冲突返回True，否则返回False
        """
        raise NotImplementedError("Subclass must implement detect_conflict method")
    
    def update_with_version_check(
        self,
        model_class: Any,
        entity_id: str,
        expected_version: int,
        update_data: dict,
        id_field: str = 'external_id'
    ) -> None:
        """使用版本号检查更新实体
        
        这是乐观锁的核心实现：
        1. 查询当前实体和版本号
        2. 检查版本号是否匹配
        3. 如果匹配，更新实体并递增版本号
        4. 如果不匹配，抛出OptimisticLockError
        
        Args:
            model_class: 模型类
            entity_id: 实体ID
            expected_version: 期望的版本号
            update_data: 要更新的数据字典
            id_field: ID字段名称，默认为'external_id'
            
        Raises:
            EntityNotFoundError: 实体不存在
            OptimisticLockError: 版本号不匹配（并发冲突）
            SQLAlchemyError: 数据库操作错误
        """
        try:
            # 查询当前实体
            entity = self.db.query(model_class).filter(
                getattr(model_class, id_field) == entity_id
            ).first()
            
            if entity is None:
                raise EntityNotFoundError(entity_id)
            
            # 检查版本号
            actual_version = entity.version
            if actual_version != expected_version:
                raise OptimisticLockError(
                    entity_id=entity_id,
                    expected_version=expected_version,
                    actual_version=actual_version
                )
            
            # 更新实体
            for key, value in update_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            # 递增版本号
            entity.version = actual_version + 1
            entity.last_modified_date = datetime.now()
            
            # 提交更新
            self.db.commit()
            self.db.refresh(entity)
            
        except (OptimisticLockError, EntityNotFoundError):
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ConcurrencyControlError(f"Database error during update: {str(e)}")
    
    def get_current_version(
        self,
        model_class: Any,
        entity_id: str,
        id_field: str = 'external_id'
    ) -> Optional[int]:
        """获取实体的当前版本号
        
        Args:
            model_class: 模型类
            entity_id: 实体ID
            id_field: ID字段名称，默认为'external_id'
            
        Returns:
            Optional[int]: 当前版本号，如果实体不存在返回None
        """
        entity = self.db.query(model_class).filter(
            getattr(model_class, id_field) == entity_id
        ).first()
        
        return entity.version if entity else None
    
    def verify_version(
        self,
        model_class: Any,
        entity_id: str,
        expected_version: int,
        id_field: str = 'external_id'
    ) -> bool:
        """验证版本号是否匹配
        
        Args:
            model_class: 模型类
            entity_id: 实体ID
            expected_version: 期望的版本号
            id_field: ID字段名称，默认为'external_id'
            
        Returns:
            bool: 版本号匹配返回True，否则返回False
        """
        current_version = self.get_current_version(model_class, entity_id, id_field)
        if current_version is None:
            return False
        return current_version == expected_version


class TransactionConcurrencyControl(ConcurrencyControl):
    """交易并发控制服务"""
    
    def detect_conflict(
        self, 
        entity_id: str, 
        expected_version: int
    ) -> bool:
        """检测交易并发冲突
        
        Args:
            entity_id: 交易外部流水号
            expected_version: 期望的版本号
            
        Returns:
            bool: 如果存在冲突返回True，否则返回False
        """
        from app.models.transaction import Transaction
        return not self.verify_version(Transaction, entity_id, expected_version)


class CashFlowConcurrencyControl(ConcurrencyControl):
    """现金流并发控制服务"""
    
    def detect_conflict(
        self, 
        entity_id: str, 
        expected_version: int
    ) -> bool:
        """检测现金流并发冲突
        
        Args:
            entity_id: 现金流ID
            expected_version: 期望的版本号
            
        Returns:
            bool: 如果存在冲突返回True，否则返回False
        """
        from app.models.cash_flow import CashFlow
        return not self.verify_version(
            CashFlow, 
            entity_id, 
            expected_version, 
            id_field='cash_flow_id'
        )
