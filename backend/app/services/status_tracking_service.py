"""Status tracking service for transaction lifecycle and cash flow progress - Updated for 4-stage flow"""
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.cash_flow_repository import CashFlowRepository
from app.repositories.event_repository import EventRepository
from app.models.enums import (
    SettlementMethod, MatchStatus, CashFlowStatus, ConfirmationType, ProductType
)
from app.schemas.payment_progress import (
    PaymentProgress, NettingStage, ComplianceStage, SettlementStage, CancellationStage,
    PrerequisiteCheck, AMLCheck, RouteDecision, ManualApproval,
    TransmissionLayer, TransmissionReceipt, ManualConfirm, AccountingLayer,
    ReversalProcessing, OperationGuide, ActionEntry, FlowNode
)


# Legacy models for transaction lifecycle progress (kept for backward compatibility)
class StatusReceipt(BaseModel):
    """状态回执"""
    stage: str = Field(..., description='阶段名称')
    status: str = Field(..., description='状态: SUCCESS, FAILED, WAITING, PROCESSING')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='状态消息')
    can_proceed: bool = Field(..., description='是否可继续后续流程')


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


class StatusTrackingService:
    """状态跟踪服务 - 支持4阶段结算支付流程"""
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.cash_flow_repo = CashFlowRepository(db)
        self.event_repo = EventRepository(db)

    
    def get_transaction_progress(self, transaction_id: str) -> LifecycleProgress:
        """获取交易生命周期进度 - 保持原有实现
        
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
        
        # 生成状态回执
        status_receipts = self._generate_status_receipts(transaction)
        
        # 生成流程可视化数据
        flow_nodes = self._generate_legacy_flow_nodes(transaction, status_receipts)
        
        # 计算当前阶段和进度
        current_stage, current_status, progress_percentage = self._calculate_legacy_progress(
            transaction, status_receipts
        )
        
        # 获取阶段完成时间
        stage_completion_time = transaction.last_modified_date
        
        return LifecycleProgress(
            current_stage=current_stage,
            current_status=current_status,
            progress_percentage=progress_percentage,
            stage_completion_time=stage_completion_time,
            status_receipts=status_receipts,
            flow_visualization=flow_nodes
        )
    
    def _generate_status_receipts(self, transaction) -> List[StatusReceipt]:
        """生成状态回执列表"""
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
        
        rmc_receipt = StatusReceipt(
            stage='SWIFT证实-发送RMC',
            status='SUCCESS',
            timestamp=transaction.last_modified_date,
            message='RMC发送成功',
            can_proceed=True
        )
        receipts.append(rmc_receipt)
        
        ftm_receipt = StatusReceipt(
            stage='SWIFT证实-发送FTM',
            status='SUCCESS',
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
        else:
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
        """生成收付发报回执"""
        receipts = []
        settlement_method = transaction.settlement_method
        
        needs_swift = settlement_method in [
            SettlementMethod.GROSS,
            SettlementMethod.NET,
            SettlementMethod.CENTRALIZED
        ]
        
        if needs_swift:
            aml_receipt = StatusReceipt(
                stage='反洗钱检查',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='反洗钱检查通过，可结算发报',
                can_proceed=True
            )
            receipts.append(aml_receipt)
            
            swift_rmc_receipt = StatusReceipt(
                stage='收付发报-发送RMC',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='RMC发送成功，可收到后续回执',
                can_proceed=True
            )
            receipts.append(swift_rmc_receipt)
            
            swift_ftm_receipt = StatusReceipt(
                stage='收付发报-发送FTM',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='FTM发送成功',
                can_proceed=True
            )
            receipts.append(swift_ftm_receipt)
            
            core_receipt = StatusReceipt(
                stage='核心入账',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='入账成功',
                can_proceed=True
            )
            receipts.append(core_receipt)
        else:
            core_receipt = StatusReceipt(
                stage='核心入账',
                status='SUCCESS',
                timestamp=transaction.last_modified_date,
                message='入账成功',
                can_proceed=True
            )
            receipts.append(core_receipt)
        
        return receipts
    
    def _generate_legacy_flow_nodes(
        self,
        transaction,
        status_receipts: List[StatusReceipt]
    ) -> List[FlowNode]:
        """生成流程可视化节点"""
        nodes = []
        
        for i, receipt in enumerate(status_receipts):
            if receipt.status == 'SUCCESS':
                node_status = 'COMPLETED'
            elif receipt.status == 'FAILED':
                node_status = 'FAILED'
            elif receipt.status == 'PROCESSING':
                node_status = 'CURRENT'
            else:
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
    
    def _calculate_legacy_progress(
        self,
        transaction,
        status_receipts: List[StatusReceipt]
    ) -> tuple[str, str, int]:
        """计算当前阶段、状态和进度百分比"""
        if not status_receipts:
            return '未开始', 'PENDING', 0
        
        current_stage_receipt = None
        completed_count = 0
        
        for receipt in status_receipts:
            if receipt.status == 'SUCCESS':
                completed_count += 1
            else:
                current_stage_receipt = receipt
                break
        
        if current_stage_receipt is None:
            current_stage_receipt = status_receipts[-1]
        
        total_stages = len(status_receipts)
        progress_percentage = int((completed_count / total_stages) * 100)
        
        return (
            current_stage_receipt.stage,
            current_stage_receipt.status,
            progress_percentage
        )
    
    def get_cash_flow_progress(self, cash_flow_id: str) -> PaymentProgress:
        """获取现金流收付进度 - 新的4阶段流程实现
        
        Args:
            cash_flow_id: 现金流内部ID
            
        Returns:
            PaymentProgress: 4阶段收付进度信息
            
        Raises:
            ValueError: 当现金流不存在时
        """
        # 查询现金流
        cash_flow = self.cash_flow_repo.find_by_cash_flow_id(cash_flow_id)
        if not cash_flow:
            raise ValueError(f'RESOURCE_NOT_FOUND: 未找到现金流 {cash_flow_id}')
        
        # 确定发送路径
        sending_route = self._determine_sending_route(cash_flow)
        
        # 生成各阶段数据
        netting_stage = self._generate_netting_stage(cash_flow)
        compliance_stage = self._generate_compliance_stage(cash_flow, sending_route)
        settlement_stage = self._generate_settlement_stage(cash_flow, sending_route)
        cancellation_stage = self._generate_cancellation_stage(cash_flow, sending_route)
        
        # 计算当前阶段和进度
        current_stage, current_status, progress_percentage = self._calculate_current_progress(
            cash_flow, netting_stage, compliance_stage, settlement_stage, cancellation_stage
        )
        
        # 生成流程可视化
        flow_nodes = self._generate_flow_visualization(
            cash_flow, netting_stage, compliance_stage, settlement_stage, cancellation_stage
        )
        
        # 生成操作指引
        operation_guide = self._generate_operation_guide(cash_flow, current_stage, current_status)
        
        return PaymentProgress(
            current_stage=current_stage,
            current_status=current_status,
            sending_route=sending_route,
            progress_percentage=progress_percentage,
            netting_stage=netting_stage,
            compliance_stage=compliance_stage,
            settlement_stage=settlement_stage,
            cancellation_stage=cancellation_stage,
            flow_visualization=flow_nodes,
            operation_guide=operation_guide
        )

    
    def _determine_sending_route(self, cash_flow) -> str:
        """确定发送路径"""
        settlement_method = cash_flow.settlement_method
        
        # 根据结算方式判断路径
        if settlement_method in [SettlementMethod.GROSS, SettlementMethod.NET, SettlementMethod.CENTRALIZED]:
            # 简化：这里应该根据SSI参数判断，暂时默认SWIFT
            return 'SWIFT'
        elif settlement_method == SettlementMethod.NOT_REQUIRED:
            return 'INTERNAL'
        else:
            # 其他情况默认SWIFT
            return 'SWIFT'
    
    def _generate_netting_stage(self, cash_flow) -> Optional[NettingStage]:
        """生成阶段1: 清算轧差"""
        current_status = cash_flow.current_status
        
        # 判断产品类型
        # 简化：这里应该从关联的交易中获取产品类型
        product_type = "外汇/拆借"  # 或 "现券/回购"
        required_condition = "证实匹配成功" if product_type == "外汇/拆借" else "文本证实通过"
        
        # 简化：假设条件已满足
        condition_met = True
        
        prerequisite_check = PrerequisiteCheck(
            product_type=product_type,
            required_condition=required_condition,
            condition_met=condition_met
        )
        
        # 判断轧差类型和状态
        if current_status in [CashFlowStatus.PENDING_NETTING]:
            netting_type = 'AUTO'
            status = '待轧差'
            timestamp = None
        elif current_status in [CashFlowStatus.AUTO_NETTING_COMPLETE]:
            netting_type = 'AUTO'
            status = '自动轧差完成'
            timestamp = cash_flow.last_modified_date
        elif current_status in [CashFlowStatus.MANUAL_NETTING_COMPLETE]:
            netting_type = 'MANUAL'
            status = '手工轧差完成'
            timestamp = cash_flow.last_modified_date
        elif current_status in [CashFlowStatus.PENDING_DISPATCH]:
            netting_type = 'AUTO'  # 简化
            status = '待发报'
            timestamp = cash_flow.last_modified_date
        else:
            # 已经过了轧差阶段
            netting_type = 'AUTO'
            status = '已完成'
            timestamp = cash_flow.last_modified_date
        
        return NettingStage(
            prerequisite_check=prerequisite_check,
            netting_type=netting_type,
            status=status,
            timestamp=timestamp
        )

    
    def _generate_compliance_stage(self, cash_flow, sending_route: str) -> Optional[ComplianceStage]:
        """生成阶段2: 合规准入"""
        current_status = cash_flow.current_status
        
        # 反洗钱检查
        aml_check = None
        if current_status == CashFlowStatus.COMPLIANCE_CHECKING:
            aml_check = AMLCheck(
                status='CHECKING',
                timestamp=cash_flow.last_modified_date,
                message='正在进行反洗钱检查'
            )
        elif current_status == CashFlowStatus.COMPLIANCE_BLOCKED:
            aml_check = AMLCheck(
                status='BLOCKED',
                timestamp=cash_flow.last_modified_date,
                message='反洗钱检查失败，已阻断'
            )
        elif current_status in [CashFlowStatus.COMPLIANCE_APPROVED, CashFlowStatus.ROUTE_DETERMINED,
                                CashFlowStatus.PENDING_APPROVAL, CashFlowStatus.APPROVAL_APPROVED]:
            aml_check = AMLCheck(
                status='APPROVED',
                timestamp=cash_flow.last_modified_date,
                message='反洗钱检查通过'
            )
        
        # 路径决策
        route_decision = None
        if current_status in [CashFlowStatus.ROUTE_DETERMINED, CashFlowStatus.PENDING_APPROVAL,
                             CashFlowStatus.APPROVAL_APPROVED, CashFlowStatus.APPROVAL_REJECTED]:
            route_decision = RouteDecision(
                route=sending_route,
                timestamp=cash_flow.last_modified_date
            )
        
        # 人工审批
        manual_approval = None
        if current_status == CashFlowStatus.PENDING_APPROVAL:
            manual_approval = ManualApproval(
                status='PENDING',
                timestamp=cash_flow.last_modified_date,
                approver=None
            )
        elif current_status == CashFlowStatus.APPROVAL_APPROVED:
            manual_approval = ManualApproval(
                status='APPROVED',
                timestamp=cash_flow.last_modified_date,
                approver='系统管理员'  # 简化
            )
        elif current_status == CashFlowStatus.APPROVAL_REJECTED:
            manual_approval = ManualApproval(
                status='REJECTED',
                timestamp=cash_flow.last_modified_date,
                approver='系统管理员'  # 简化
            )
        
        if aml_check or route_decision or manual_approval:
            return ComplianceStage(
                aml_check=aml_check,
                route_decision=route_decision,
                manual_approval=manual_approval
            )
        return None

    
    def _generate_settlement_stage(self, cash_flow, sending_route: str) -> Optional[SettlementStage]:
        """生成阶段3: 结算执行与回执"""
        current_status = cash_flow.current_status
        
        transmission_layer = None
        manual_confirm = None
        
        # SWIFT路径：传输层回执
        if sending_route == 'SWIFT':
            # RMC
            if current_status == CashFlowStatus.RMC_SENDING:
                rmc = TransmissionReceipt(
                    status='SENDING',
                    timestamp=cash_flow.last_modified_date,
                    message='RMC发送中'
                )
                ftm = None
            elif current_status == CashFlowStatus.RMC_FAILED:
                rmc = TransmissionReceipt(
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='RMC发送失败'
                )
                ftm = None  # RMC失败时不显示FTM
            elif current_status in [CashFlowStatus.RMC_SUCCESS, CashFlowStatus.FTM_SENDING,
                                   CashFlowStatus.FTM_SUCCESS, CashFlowStatus.FTM_FAILED,
                                   CashFlowStatus.CORE_PROCESSING, CashFlowStatus.CORE_SUCCESS,
                                   CashFlowStatus.CORE_FAILED, CashFlowStatus.CORE_UNKNOWN]:
                rmc = TransmissionReceipt(
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='RMC发送成功'
                )
                
                # FTM（仅当RMC成功时）
                if current_status == CashFlowStatus.FTM_SENDING:
                    ftm = TransmissionReceipt(
                        status='SENDING',
                        timestamp=cash_flow.last_modified_date,
                        message='FTM发送中'
                    )
                elif current_status == CashFlowStatus.FTM_FAILED:
                    ftm = TransmissionReceipt(
                        status='FAILED',
                        timestamp=cash_flow.last_modified_date,
                        message='FTM发送失败'
                    )
                elif current_status in [CashFlowStatus.FTM_SUCCESS, CashFlowStatus.CORE_PROCESSING,
                                       CashFlowStatus.CORE_SUCCESS, CashFlowStatus.CORE_FAILED,
                                       CashFlowStatus.CORE_UNKNOWN]:
                    ftm = TransmissionReceipt(
                        status='SUCCESS',
                        timestamp=cash_flow.last_modified_date,
                        message='FTM发送成功'
                    )
                else:
                    ftm = None
            else:
                rmc = None
                ftm = None
            
            if rmc:
                transmission_layer = TransmissionLayer(rmc=rmc, ftm=ftm)
        
        # CBMNet路径：人工确认
        elif sending_route == 'CBMNet':
            if current_status == CashFlowStatus.PENDING_MANUAL_CONFIRM:
                manual_confirm = ManualConfirm(
                    status='PENDING',
                    timestamp=cash_flow.last_modified_date,
                    operator=None
                )
            elif current_status == CashFlowStatus.MANUAL_CONFIRM_APPROVED:
                manual_confirm = ManualConfirm(
                    status='APPROVED',
                    timestamp=cash_flow.last_modified_date,
                    operator='操作员'  # 简化
                )
            elif current_status == CashFlowStatus.MANUAL_CONFIRM_REJECTED:
                manual_confirm = ManualConfirm(
                    status='REJECTED',
                    timestamp=cash_flow.last_modified_date,
                    operator='操作员'  # 简化
                )
        
        # 账务层回执（通用）
        accounting_layer = None
        if current_status == CashFlowStatus.CORE_PROCESSING:
            accounting_layer = AccountingLayer(
                mode='AUTO',  # 简化
                status='PROCESSING',
                timestamp=cash_flow.last_modified_date,
                message='核心入账处理中'
            )
        elif current_status == CashFlowStatus.CORE_SUCCESS:
            accounting_layer = AccountingLayer(
                mode='AUTO',
                status='SUCCESS',
                timestamp=cash_flow.last_modified_date,
                message='入账成功'
            )
        elif current_status == CashFlowStatus.CORE_FAILED:
            accounting_layer = AccountingLayer(
                mode='AUTO',
                status='FAILED',
                timestamp=cash_flow.last_modified_date,
                message='入账失败'
            )
        elif current_status == CashFlowStatus.CORE_UNKNOWN:
            accounting_layer = AccountingLayer(
                mode='AUTO',
                status='UNKNOWN',
                timestamp=cash_flow.last_modified_date,
                message='入账状态不明'
            )
        
        if transmission_layer or manual_confirm or accounting_layer:
            # 如果没有账务层数据，创建默认的
            if not accounting_layer:
                accounting_layer = AccountingLayer(
                    mode='AUTO',
                    status='PROCESSING',
                    timestamp=None,
                    message='待核心入账'
                )
            
            return SettlementStage(
                transmission_layer=transmission_layer,
                manual_confirm=manual_confirm,
                accounting_layer=accounting_layer
            )
        return None

    
    def _generate_cancellation_stage(self, cash_flow, sending_route: str) -> Optional[CancellationStage]:
        """生成阶段4: 结算撤销"""
        current_status = cash_flow.current_status
        
        # 只有在撤销相关状态时才生成此阶段
        cancellation_statuses = [
            CashFlowStatus.CANCEL_RMC_SENDING, CashFlowStatus.CANCEL_RMC_FAILED,
            CashFlowStatus.CANCEL_FTM_SENDING, CashFlowStatus.CANCEL_FTM_FAILED,
            CashFlowStatus.CANCEL_PROCESSING, CashFlowStatus.CANCEL_SUCCESS,
            CashFlowStatus.CANCEL_FAILED
        ]
        
        if current_status not in cancellation_statuses:
            return None
        
        transmission_layer = None
        
        # SWIFT路径：传输层
        if sending_route == 'SWIFT':
            if current_status == CashFlowStatus.CANCEL_RMC_SENDING:
                rmc = TransmissionReceipt(
                    status='SENDING',
                    timestamp=cash_flow.last_modified_date,
                    message='撤销RMC发送中'
                )
                ftm = None
            elif current_status == CashFlowStatus.CANCEL_RMC_FAILED:
                rmc = TransmissionReceipt(
                    status='FAILED',
                    timestamp=cash_flow.last_modified_date,
                    message='撤销RMC发送失败'
                )
                ftm = None
            elif current_status in [CashFlowStatus.CANCEL_FTM_SENDING, CashFlowStatus.CANCEL_FTM_FAILED,
                                   CashFlowStatus.CANCEL_PROCESSING, CashFlowStatus.CANCEL_SUCCESS,
                                   CashFlowStatus.CANCEL_FAILED]:
                rmc = TransmissionReceipt(
                    status='SUCCESS',
                    timestamp=cash_flow.last_modified_date,
                    message='撤销RMC发送成功'
                )
                
                if current_status == CashFlowStatus.CANCEL_FTM_SENDING:
                    ftm = TransmissionReceipt(
                        status='SENDING',
                        timestamp=cash_flow.last_modified_date,
                        message='撤销FTM发送中'
                    )
                elif current_status == CashFlowStatus.CANCEL_FTM_FAILED:
                    ftm = TransmissionReceipt(
                        status='FAILED',
                        timestamp=cash_flow.last_modified_date,
                        message='撤销FTM发送失败'
                    )
                else:
                    ftm = TransmissionReceipt(
                        status='SUCCESS',
                        timestamp=cash_flow.last_modified_date,
                        message='撤销FTM发送成功'
                    )
            else:
                rmc = None
                ftm = None
            
            if rmc:
                transmission_layer = TransmissionLayer(rmc=rmc, ftm=ftm)
        
        # 资金冲正
        if current_status == CashFlowStatus.CANCEL_PROCESSING:
            reversal = ReversalProcessing(
                status='PROCESSING',
                timestamp=cash_flow.last_modified_date,
                message='资金冲正处理中'
            )
        elif current_status == CashFlowStatus.CANCEL_SUCCESS:
            reversal = ReversalProcessing(
                status='SUCCESS',
                timestamp=cash_flow.last_modified_date,
                message='资金冲正成功'
            )
        elif current_status == CashFlowStatus.CANCEL_FAILED:
            reversal = ReversalProcessing(
                status='FAILED',
                timestamp=cash_flow.last_modified_date,
                message='资金冲正失败'
            )
        else:
            reversal = ReversalProcessing(
                status='PROCESSING',
                timestamp=None,
                message='待资金冲正'
            )
        
        return CancellationStage(
            transmission_layer=transmission_layer,
            reversal_processing=reversal
        )

    
    def _calculate_current_progress(
        self,
        cash_flow,
        netting_stage: Optional[NettingStage],
        compliance_stage: Optional[ComplianceStage],
        settlement_stage: Optional[SettlementStage],
        cancellation_stage: Optional[CancellationStage]
    ) -> tuple[str, str, int]:
        """计算当前阶段、状态和进度百分比"""
        current_status = cash_flow.current_status
        
        # 阶段4: 结算撤销
        if cancellation_stage:
            return '结算撤销', str(current_status.value), 90
        
        # 阶段3: 结算执行与回执
        if current_status in [
            CashFlowStatus.RMC_SENDING, CashFlowStatus.RMC_SUCCESS, CashFlowStatus.RMC_FAILED,
            CashFlowStatus.FTM_SENDING, CashFlowStatus.FTM_SUCCESS, CashFlowStatus.FTM_FAILED,
            CashFlowStatus.PENDING_MANUAL_CONFIRM, CashFlowStatus.MANUAL_CONFIRM_APPROVED,
            CashFlowStatus.MANUAL_CONFIRM_REJECTED,
            CashFlowStatus.CORE_PROCESSING, CashFlowStatus.CORE_SUCCESS,
            CashFlowStatus.CORE_FAILED, CashFlowStatus.CORE_UNKNOWN
        ]:
            if current_status == CashFlowStatus.CORE_SUCCESS:
                return '结算执行与回执', '结算完成', 100
            else:
                return '结算执行与回执', str(current_status.value), 70
        
        # 阶段2: 合规准入
        if current_status in [
            CashFlowStatus.COMPLIANCE_CHECKING, CashFlowStatus.COMPLIANCE_APPROVED,
            CashFlowStatus.COMPLIANCE_BLOCKED, CashFlowStatus.PENDING_APPROVAL,
            CashFlowStatus.APPROVAL_APPROVED, CashFlowStatus.APPROVAL_REJECTED,
            CashFlowStatus.ROUTE_DETERMINED
        ]:
            if current_status == CashFlowStatus.COMPLIANCE_BLOCKED:
                return '合规准入', '合规拦截', 40
            elif current_status == CashFlowStatus.APPROVAL_REJECTED:
                return '合规准入', '审批拒绝', 40
            else:
                return '合规准入', str(current_status.value), 40
        
        # 阶段1: 清算轧差
        if current_status in [
            CashFlowStatus.PENDING_NETTING, CashFlowStatus.AUTO_NETTING_COMPLETE,
            CashFlowStatus.MANUAL_NETTING_COMPLETE, CashFlowStatus.PENDING_DISPATCH
        ]:
            return '清算轧差', str(current_status.value), 20
        
        # 默认
        return '清算轧差', '待轧差', 0

    
    def _generate_flow_visualization(
        self,
        cash_flow,
        netting_stage: Optional[NettingStage],
        compliance_stage: Optional[ComplianceStage],
        settlement_stage: Optional[SettlementStage],
        cancellation_stage: Optional[CancellationStage]
    ) -> List[FlowNode]:
        """生成流程可视化节点"""
        nodes = []
        current_status = cash_flow.current_status
        
        # 节点1: 清算轧差
        if netting_stage:
            if netting_stage.status in ['已完成', '待发报']:
                node_status = 'COMPLETED'
            elif current_status in [CashFlowStatus.PENDING_NETTING, CashFlowStatus.AUTO_NETTING_COMPLETE,
                                   CashFlowStatus.MANUAL_NETTING_COMPLETE, CashFlowStatus.PENDING_DISPATCH]:
                node_status = 'CURRENT'
            else:
                node_status = 'PENDING'
            
            nodes.append(FlowNode(
                id='stage_1',
                name='清算轧差',
                status=node_status,
                timestamp=netting_stage.timestamp
            ))
        
        # 节点2: 合规准入
        if compliance_stage:
            if current_status in [CashFlowStatus.COMPLIANCE_BLOCKED, CashFlowStatus.APPROVAL_REJECTED]:
                node_status = 'BLOCKED'
            elif current_status in [CashFlowStatus.ROUTE_DETERMINED, CashFlowStatus.APPROVAL_APPROVED]:
                node_status = 'COMPLETED'
            elif current_status in [CashFlowStatus.COMPLIANCE_CHECKING, CashFlowStatus.COMPLIANCE_APPROVED,
                                   CashFlowStatus.PENDING_APPROVAL]:
                node_status = 'CURRENT'
            else:
                node_status = 'PENDING'
            
            timestamp = None
            if compliance_stage.aml_check:
                timestamp = compliance_stage.aml_check.timestamp
            
            nodes.append(FlowNode(
                id='stage_2',
                name='合规准入',
                status=node_status,
                timestamp=timestamp
            ))
        
        # 节点3: 结算执行与回执
        if settlement_stage:
            if current_status == CashFlowStatus.CORE_SUCCESS:
                node_status = 'COMPLETED'
            elif current_status in [CashFlowStatus.RMC_FAILED, CashFlowStatus.FTM_FAILED,
                                   CashFlowStatus.MANUAL_CONFIRM_REJECTED, CashFlowStatus.CORE_FAILED]:
                node_status = 'FAILED'
            elif current_status in [CashFlowStatus.RMC_SENDING, CashFlowStatus.RMC_SUCCESS,
                                   CashFlowStatus.FTM_SENDING, CashFlowStatus.FTM_SUCCESS,
                                   CashFlowStatus.PENDING_MANUAL_CONFIRM, CashFlowStatus.MANUAL_CONFIRM_APPROVED,
                                   CashFlowStatus.CORE_PROCESSING, CashFlowStatus.CORE_UNKNOWN]:
                node_status = 'CURRENT'
            else:
                node_status = 'PENDING'
            
            nodes.append(FlowNode(
                id='stage_3',
                name='结算执行与回执',
                status=node_status,
                timestamp=settlement_stage.accounting_layer.timestamp
            ))
        
        # 节点4: 结算撤销（仅在撤销流程中显示）
        if cancellation_stage:
            if current_status == CashFlowStatus.CANCEL_SUCCESS:
                node_status = 'COMPLETED'
            elif current_status in [CashFlowStatus.CANCEL_RMC_FAILED, CashFlowStatus.CANCEL_FTM_FAILED,
                                   CashFlowStatus.CANCEL_FAILED]:
                node_status = 'FAILED'
            else:
                node_status = 'CURRENT'
            
            nodes.append(FlowNode(
                id='stage_4',
                name='结算撤销',
                status=node_status,
                timestamp=cancellation_stage.reversal_processing.timestamp
            ))
        
        return nodes

    
    def _generate_operation_guide(
        self,
        cash_flow,
        current_stage: str,
        current_status: str
    ) -> Optional[OperationGuide]:
        """生成操作指引"""
        status = cash_flow.current_status
        
        # 根据不同状态生成操作指引
        guides = {
            CashFlowStatus.PENDING_NETTING: {
                'next_action': '等待系统自动轧差或手动执行轧差操作',
                'notes': '系统将在日终批处理时自动执行轧差',
                'estimated_time': '日终批处理时间'
            },
            CashFlowStatus.COMPLIANCE_CHECKING: {
                'next_action': '等待反洗钱系统审核完成',
                'notes': '系统正在进行反洗钱和黑名单扫描',
                'estimated_time': '1-5分钟'
            },
            CashFlowStatus.COMPLIANCE_BLOCKED: {
                'next_action': '联系合规部门，提供补充材料或申请人工审核',
                'notes': '反洗钱检查失败，已硬性阻断后续流程',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='申请人工审核',
                    action='request_manual_review'
                )
            },
            CashFlowStatus.PENDING_APPROVAL: {
                'next_action': '等待审批人员审批',
                'notes': '需要人工审批通过后方可继续',
                'estimated_time': '根据审批流程而定'
            },
            CashFlowStatus.RMC_FAILED: {
                'next_action': '检查RMC连接状态，联系SWIFT技术支持',
                'notes': 'RMC发送失败，已阻断后续流程',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitor'
                )
            },
            CashFlowStatus.FTM_FAILED: {
                'next_action': '检查报文格式，重新发送FTM',
                'notes': 'FTM发送失败，需要补发处理',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='重新发送FTM',
                    action='resend_ftm'
                )
            },
            CashFlowStatus.PENDING_MANUAL_CONFIRM: {
                'next_action': '进行人工确认',
                'notes': 'CBMNet路径需要人工确认后方可进行核心扣划账',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='确认处理',
                    action='manual_confirm'
                )
            },
            CashFlowStatus.CORE_FAILED: {
                'next_action': '查询内部账划转情况，联系核心系统支持',
                'notes': '核心入账失败，需要进行冲正或重试',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_account'
                )
            },
            CashFlowStatus.CORE_UNKNOWN: {
                'next_action': '查询内部账划转情况，确认入账状态',
                'notes': '核心入账状态不明，需要人工确认',
                'estimated_time': '需人工处理',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_account'
                )
            },
            CashFlowStatus.CORE_SUCCESS: {
                'next_action': '流程已完成，无需操作',
                'notes': '结算已成功完成',
                'estimated_time': None
            },
            CashFlowStatus.CANCEL_PROCESSING: {
                'next_action': '等待撤销处理完成',
                'notes': '系统正在处理撤销流程',
                'estimated_time': '5-10分钟'
            }
        }
        
        guide_data = guides.get(status)
        if guide_data:
            return OperationGuide(
                next_action=guide_data['next_action'],
                action_entry=guide_data.get('action_entry'),
                notes=guide_data.get('notes'),
                estimated_time=guide_data.get('estimated_time')
            )
        
        # 默认指引
        return OperationGuide(
            next_action='系统自动处理中，无需人工干预',
            notes='请等待系统处理完成',
            estimated_time='根据流程而定'
        )
