"""Status tracking service for transaction lifecycle and cash flow progress"""
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.cash_flow_repository import CashFlowRepository
from app.repositories.event_repository import EventRepository
from app.models.enums import (
    SettlementMethod, MatchStatus, CashFlowStatus, ConfirmationType
)


# Response models for status tracking
class StatusReceipt(BaseModel):
    """状态回执"""
    stage: str = Field(..., description='阶段名称')
    status: str = Field(..., description='状态: SUCCESS, FAILED, WAITING, PROCESSING')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='状态消息')
    can_proceed: bool = Field(..., description='是否可继续后续流程')


class FlowNode(BaseModel):
    """流程节点"""
    id: str = Field(..., description='节点ID')
    name: str = Field(..., description='节点名称')
    status: str = Field(..., description='节点状态: COMPLETED, CURRENT, PENDING, FAILED')
    timestamp: Optional[datetime] = Field(None, description='完成时间')


class LifecycleProgress(BaseModel):
    """交易生命周期进度"""
    current_stage: str = Field(..., description='当前阶段')
    current_status: str = Field(..., description='当前状态')
    progress_percentage: int = Field(..., description='进度百分比')
    stage_completion_time: Optional[datetime] = Field(None, description='阶段完成时间')
    status_receipts: List[StatusReceipt] = Field(..., description='状态回执详情')
    flow_visualization: List[FlowNode] = Field(..., description='流程可视化数据')
    
    class Config:
        populate_by_name = True


class PaymentProgress(BaseModel):
    """现金流收付进度"""
    current_stage: str = Field(..., description='当前阶段')
    current_status: str = Field(..., description='当前状态')
    progress_percentage: int = Field(..., description='进度百分比')
    stage_completion_time: Optional[datetime] = Field(None, description='阶段完成时间')
    status_receipts: List[StatusReceipt] = Field(..., description='状态回执详情')
    flow_visualization: List[FlowNode] = Field(..., description='流程可视化数据')
    
    class Config:
        populate_by_name = True


class StatusTrackingService:
    """状态跟踪服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.cash_flow_repo = CashFlowRepository(db)
        self.event_repo = EventRepository(db)
    
    def get_transaction_progress(self, transaction_id: str) -> LifecycleProgress:
        """获取交易生命周期进度
        
        根据交易当前状态和回执信息，识别交易所处的生命周期阶段，
        并生成状态回执和流程可视化数据。
        
        Args:
            transaction_id: 交易流水号
            
        Returns:
            LifecycleProgress: 生命周期进度信息
            
        Raises:
            ValueError: 当交易不存在时
        """
        # 查询交易
        transaction = self.transaction_repo.find_by_transaction_id(transaction_id)
        if not transaction:
            raise ValueError(f'RESOURCE_NOT_FOUND: 未找到交易 {transaction_id}')
        
        # 根据结算方式和证实方式确定流程路径
        settlement_method = transaction.settlement_method
        confirmation_type = transaction.confirmation_type
        
        # 生成状态回执
        status_receipts = self._generate_status_receipts(transaction)
        
        # 生成流程可视化数据
        flow_nodes = self._generate_flow_nodes(transaction, status_receipts)
        
        # 计算当前阶段和进度
        current_stage, current_status, progress_percentage = self._calculate_progress(
            transaction, status_receipts
        )
        
        # 获取阶段完成时间
        stage_completion_time = self._get_stage_completion_time(transaction, current_stage)
        
        return LifecycleProgress(
            current_stage=current_stage,
            current_status=current_status,
            progress_percentage=progress_percentage,
            stage_completion_time=stage_completion_time,
            status_receipts=status_receipts,
            flow_visualization=flow_nodes
        )
    
    def _generate_status_receipts(self, transaction) -> List[StatusReceipt]:
        """生成状态回执列表
        
        根据交易的证实方式和结算方式，生成对应的状态回执序列。
        """
        receipts = []
        
        # 1. SWIFT证实回执状态（如果证实方式为SWIFT）
        if transaction.confirmation_type == ConfirmationType.SWIFT:
            receipts.extend(self._generate_swift_confirmation_receipts(transaction))
        
        # 2. 证实匹配状态
        receipts.extend(self._generate_match_receipts(transaction))
        
        # 3. 收付发报回执状态（根据结算方式）
        receipts.extend(self._generate_settlement_receipts(transaction))
        
        return receipts
    
    def _generate_swift_confirmation_receipts(self, transaction) -> List[StatusReceipt]:
        """生成SWIFT证实回执"""
        receipts = []
        
        # 发送RMC
        # 这里简化处理，实际应该从事件记录中获取详细状态
        rmc_receipt = StatusReceipt(
            stage='SWIFT证实-发送RMC',
            status='SUCCESS',  # 简化：假设成功
            timestamp=transaction.last_modified_date,
            message='RMC发送成功',
            can_proceed=True
        )
        receipts.append(rmc_receipt)
        
        # 由RMC发送FTM
        ftm_receipt = StatusReceipt(
            stage='SWIFT证实-发送FTM',
            status='SUCCESS',  # 简化：假设成功
            timestamp=transaction.last_modified_date,
            message='FTM发送成功',
            can_proceed=True
        )
        receipts.append(ftm_receipt)
        
        return receipts
    
    def _generate_match_receipts(self, transaction) -> List[StatusReceipt]:
        """生成证实匹配回执"""
        receipts = []
        
        match_status = transaction.confirmation_match_status
        
        if match_status == MatchStatus.MATCHED:
            receipt = StatusReceipt(
                stage='证实匹配',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='匹配成功',
                can_proceed=True
            )
        elif match_status == MatchStatus.UNMATCHED:
            receipt = StatusReceipt(
                stage='证实匹配',
                status='FAILED',
                timestamp=transaction.last_modified_date,
                message='匹配失败，不可进行后续流程',
                can_proceed=False
            )
        else:  # PENDING or None
            receipt = StatusReceipt(
                stage='证实匹配',
                status='WAITING',
                timestamp=None,
                message='等待匹配',
                can_proceed=False
            )
        
        receipts.append(receipt)
        return receipts
    
    def _generate_settlement_receipts(self, transaction) -> List[StatusReceipt]:
        """生成收付发报回执
        
        根据结算方式生成不同的流程路径：
        - SWIFT/HKSWIFT: 反洗钱 -> SWIFT发报 -> 核心入账
        - 内部账: 直接核心入账
        """
        receipts = []
        settlement_method = transaction.settlement_method
        
        # 判断是否需要SWIFT流程
        needs_swift = settlement_method in [
            SettlementMethod.GROSS,
            SettlementMethod.NET,
            SettlementMethod.CENTRALIZED
        ]
        
        if needs_swift:
            # 路径A: SWIFT/HKSWIFT + 内部账
            
            # 反洗钱检查
            aml_receipt = StatusReceipt(
                stage='反洗钱检查',
                status='SUCCESS',  # 简化：假设通过
                timestamp=transaction.last_modified_date,
                message='反洗钱检查通过，可结算发报',
                can_proceed=True
            )
            receipts.append(aml_receipt)
            
            # SWIFT发报 - 发送RMC
            swift_rmc_receipt = StatusReceipt(
                stage='收付发报-发送RMC',
                status='SUCCESS',  # 简化：假设成功
                timestamp=transaction.last_modified_date,
                message='RMC发送成功，可收到后续回执',
                can_proceed=True
            )
            receipts.append(swift_rmc_receipt)
            
            # SWIFT发报 - 发送FTM
            swift_ftm_receipt = StatusReceipt(
                stage='收付发报-发送FTM',
                status='SUCCESS',  # 简化：假设成功
                timestamp=transaction.last_modified_date,
                message='FTM发送成功',
                can_proceed=True
            )
            receipts.append(swift_ftm_receipt)
            
            # 核心入账
            core_receipt = StatusReceipt(
                stage='核心入账',
                status='SUCCESS',  # 简化：假设成功
                timestamp=transaction.last_modified_date,
                message='入账成功',
                can_proceed=True
            )
            receipts.append(core_receipt)
        else:
            # 路径B: 内部账
            core_receipt = StatusReceipt(
                stage='核心入账',
                status='SUCCESS',  # 简化：假设成功
                timestamp=transaction.last_modified_date,
                message='入账成功',
                can_proceed=True
            )
            receipts.append(core_receipt)
        
        return receipts
    
    def _generate_flow_nodes(
        self,
        transaction,
        status_receipts: List[StatusReceipt]
    ) -> List[FlowNode]:
        """生成流程可视化节点"""
        nodes = []
        
        for i, receipt in enumerate(status_receipts):
            # 确定节点状态
            if receipt.status == 'SUCCESS':
                node_status = 'COMPLETED'
            elif receipt.status == 'FAILED':
                node_status = 'FAILED'
            elif receipt.status == 'PROCESSING':
                node_status = 'CURRENT'
            else:  # WAITING
                # 如果前一个节点成功，当前节点是CURRENT，否则是PENDING
                if i > 0 and status_receipts[i-1].status == 'SUCCESS':
                    node_status = 'CURRENT'
                else:
                    node_status = 'PENDING'
            
            node = FlowNode(
                id=f'node_{i+1}',
                name=receipt.stage,
                status=node_status,
                timestamp=receipt.timestamp
            )
            nodes.append(node)
        
        return nodes
    
    def _calculate_progress(
        self,
        transaction,
        status_receipts: List[StatusReceipt]
    ) -> tuple[str, str, int]:
        """计算当前阶段、状态和进度百分比"""
        if not status_receipts:
            return '未开始', 'PENDING', 0
        
        # 找到当前阶段（第一个非成功的阶段，或最后一个阶段）
        current_stage_receipt = None
        completed_count = 0
        
        for receipt in status_receipts:
            if receipt.status == 'SUCCESS':
                completed_count += 1
            else:
                current_stage_receipt = receipt
                break
        
        # 如果所有阶段都成功，当前阶段是最后一个
        if current_stage_receipt is None:
            current_stage_receipt = status_receipts[-1]
        
        # 计算进度百分比
        total_stages = len(status_receipts)
        progress_percentage = int((completed_count / total_stages) * 100)
        
        return (
            current_stage_receipt.stage,
            current_stage_receipt.status,
            progress_percentage
        )
    
    def _get_stage_completion_time(
        self,
        transaction,
        current_stage: str
    ) -> Optional[datetime]:
        """获取阶段完成时间"""
        # 简化处理：返回交易最后修改时间
        return transaction.last_modified_date
    
    def get_cash_flow_progress(self, cash_flow_id: str) -> PaymentProgress:
        """获取现金流收付进度
        
        根据现金流当前状态和回执信息，识别现金流所处的收付阶段，
        并生成状态回执和流程可视化数据。
        
        Args:
            cash_flow_id: 现金流内部ID
            
        Returns:
            PaymentProgress: 收付进度信息
            
        Raises:
            ValueError: 当现金流不存在时
        """
        # 查询现金流
        cash_flow = self.cash_flow_repo.find_by_cash_flow_id(cash_flow_id)
        if not cash_flow:
            raise ValueError(f'RESOURCE_NOT_FOUND: 未找到现金流 {cash_flow_id}')
        
        # 生成状态回执
        status_receipts = self._generate_cash_flow_receipts(cash_flow)
        
        # 生成流程可视化数据
        flow_nodes = self._generate_cash_flow_nodes(cash_flow, status_receipts)
        
        # 计算当前阶段和进度
        current_stage, current_status, progress_percentage = self._calculate_cash_flow_progress(
            cash_flow, status_receipts
        )
        
        # 获取阶段完成时间
        stage_completion_time = cash_flow.last_modified_date
        
        return PaymentProgress(
            current_stage=current_stage,
            current_status=current_status,
            progress_percentage=progress_percentage,
            stage_completion_time=stage_completion_time,
            status_receipts=status_receipts,
            flow_visualization=flow_nodes
        )
    
    def _generate_cash_flow_receipts(self, cash_flow) -> List[StatusReceipt]:
        """生成现金流状态回执
        
        根据结算方式生成不同的流程路径：
        - SWIFT/HKSWIFT: 反洗钱 -> SWIFT发报 -> 核心入账
        - 内部账: 直接核心入账
        """
        receipts = []
        settlement_method = cash_flow.settlement_method
        current_status = cash_flow.current_status
        
        # 判断是否需要SWIFT流程
        needs_swift = settlement_method in [
            SettlementMethod.GROSS,
            SettlementMethod.NET,
            SettlementMethod.CENTRALIZED
        ]
        
        if needs_swift:
            # 路径A: SWIFT/HKSWIFT方式
            
            # 1. 反洗钱检查
            if current_status in [CashFlowStatus.PENDING_AML]:
                aml_receipt = StatusReceipt(
                    stage='反洗钱检查',
                    status='WAITING',
                    timestamp=None,
                    message='等待反洗钱检查',
                    can_proceed=False
                )
            elif current_status == CashFlowStatus.AML_REJECTED:
                aml_receipt = StatusReceipt(
                    stage='反洗钱检查',
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='反洗钱检查失败，不可结算发报',
                    can_proceed=False
                )
            else:
                aml_receipt = StatusReceipt(
                    stage='反洗钱检查',
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='反洗钱检查通过，可结算发报',
                    can_proceed=True
                )
            receipts.append(aml_receipt)
            
            # 2. SWIFT发报
            if current_status in [CashFlowStatus.PENDING_SWIFT]:
                swift_receipt = StatusReceipt(
                    stage='SWIFT发报',
                    status='WAITING',
                    timestamp=None,
                    message='等待SWIFT发报',
                    can_proceed=False
                )
            elif current_status == CashFlowStatus.SWIFT_FAILED:
                swift_receipt = StatusReceipt(
                    stage='SWIFT发报',
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='SWIFT发送失败，无后续回执',
                    can_proceed=False
                )
            elif current_status in [
                CashFlowStatus.SWIFT_SENT,
                CashFlowStatus.PENDING_CORE,
                CashFlowStatus.CORE_SUCCESS,
                CashFlowStatus.CORE_FAILED,
                CashFlowStatus.CORE_UNKNOWN
            ]:
                swift_receipt = StatusReceipt(
                    stage='SWIFT发报',
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='SWIFT发送成功',
                    can_proceed=True
                )
            else:
                swift_receipt = StatusReceipt(
                    stage='SWIFT发报',
                    status='PENDING',
                    timestamp=None,
                    message='待SWIFT发报',
                    can_proceed=False
                )
            receipts.append(swift_receipt)
            
            # 3. 核心入账
            if current_status == CashFlowStatus.CORE_SUCCESS:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='入账成功',
                    can_proceed=True
                )
            elif current_status == CashFlowStatus.CORE_FAILED:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='入账失败',
                    can_proceed=False
                )
            elif current_status == CashFlowStatus.CORE_UNKNOWN:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='PROCESSING',
                    timestamp=cash_flow.last_modified_date,
                    message='入账状态不明',
                    can_proceed=False
                )
            elif current_status == CashFlowStatus.PENDING_CORE:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='WAITING',
                    timestamp=None,
                    message='等待核心入账',
                    can_proceed=False
                )
            else:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='PENDING',
                    timestamp=None,
                    message='待核心入账',
                    can_proceed=False
                )
            receipts.append(core_receipt)
        else:
            # 路径B: 内部账方式
            if current_status == CashFlowStatus.CORE_SUCCESS:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='入账成功',
                    can_proceed=True
                )
            elif current_status == CashFlowStatus.CORE_FAILED:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='入账失败',
                    can_proceed=False
                )
            elif current_status == CashFlowStatus.CORE_UNKNOWN:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='PROCESSING',
                    timestamp=cash_flow.last_modified_date,
                    message='入账状态不明',
                    can_proceed=False
                )
            else:
                core_receipt = StatusReceipt(
                    stage='核心入账',
                    status='WAITING',
                    timestamp=None,
                    message='等待核心入账',
                    can_proceed=False
                )
            receipts.append(core_receipt)
        
        return receipts
    
    def _generate_cash_flow_nodes(
        self,
        cash_flow,
        status_receipts: List[StatusReceipt]
    ) -> List[FlowNode]:
        """生成现金流流程可视化节点"""
        nodes = []
        
        for i, receipt in enumerate(status_receipts):
            # 确定节点状态
            if receipt.status == 'SUCCESS':
                node_status = 'COMPLETED'
            elif receipt.status == 'FAILED':
                node_status = 'FAILED'
            elif receipt.status == 'PROCESSING':
                node_status = 'CURRENT'
            elif receipt.status == 'WAITING':
                # 如果前一个节点成功，当前节点是CURRENT，否则是PENDING
                if i > 0 and status_receipts[i-1].status == 'SUCCESS':
                    node_status = 'CURRENT'
                else:
                    node_status = 'PENDING'
            else:  # PENDING
                node_status = 'PENDING'
            
            node = FlowNode(
                id=f'cf_node_{i+1}',
                name=receipt.stage,
                status=node_status,
                timestamp=receipt.timestamp
            )
            nodes.append(node)
        
        return nodes
    
    def _calculate_cash_flow_progress(
        self,
        cash_flow,
        status_receipts: List[StatusReceipt]
    ) -> tuple[str, str, int]:
        """计算现金流当前阶段、状态和进度百分比"""
        if not status_receipts:
            return '未开始', 'PENDING', 0
        
        # 找到当前阶段（第一个非成功的阶段，或最后一个阶段）
        current_stage_receipt = None
        completed_count = 0
        
        for receipt in status_receipts:
            if receipt.status == 'SUCCESS':
                completed_count += 1
            else:
                current_stage_receipt = receipt
                break
        
        # 如果所有阶段都成功，当前阶段是最后一个
        if current_stage_receipt is None:
            current_stage_receipt = status_receipts[-1]
        
        # 计算进度百分比
        total_stages = len(status_receipts)
        progress_percentage = int((completed_count / total_stages) * 100)
        
        return (
            current_stage_receipt.stage,
            current_stage_receipt.status,
            progress_percentage
        )
