"""Payment progress response models for 4-stage settlement flow"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PrerequisiteCheck(BaseModel):
    """前置触发校验"""
    product_type: str = Field(..., description='产品类型')
    required_condition: str = Field(..., description='需满足的条件')
    condition_met: bool = Field(..., description='条件是否满足')


class NettingStage(BaseModel):
    """阶段1: 清算轧差"""
    prerequisite_check: Optional[PrerequisiteCheck] = Field(None, description='前置触发校验')
    netting_type: str = Field(..., description='轧差类型: AUTO/MANUAL')
    status: str = Field(..., description='阶段状态')
    timestamp: Optional[datetime] = Field(None, description='完成时间')


class AMLCheck(BaseModel):
    """反洗钱检查"""
    status: str = Field(..., description='状态: CHECKING/APPROVED/BLOCKED')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='消息')


class RouteDecision(BaseModel):
    """路径决策"""
    route: str = Field(..., description='路径: SWIFT/CBMNet/INTERNAL')
    timestamp: Optional[datetime] = Field(None, description='时间戳')


class ManualApproval(BaseModel):
    """人工审批"""
    status: str = Field(..., description='状态: PENDING/APPROVED/REJECTED')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    approver: Optional[str] = Field(None, description='审批人')


class ComplianceStage(BaseModel):
    """阶段2: 合规准入"""
    aml_check: Optional[AMLCheck] = Field(None, description='反洗钱检查')
    route_decision: Optional[RouteDecision] = Field(None, description='路径决策')
    manual_approval: Optional[ManualApproval] = Field(None, description='人工审批')


class TransmissionReceipt(BaseModel):
    """传输层回执"""
    status: str = Field(..., description='状态: SENDING/SUCCESS/FAILED')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='消息')


class TransmissionLayer(BaseModel):
    """传输层"""
    rmc: TransmissionReceipt = Field(..., description='RMC发送')
    ftm: Optional[TransmissionReceipt] = Field(None, description='FTM处理（仅当RMC成功时存在）')


class ManualConfirm(BaseModel):
    """人工确认（CBMNet路径）"""
    status: str = Field(..., description='状态: PENDING/APPROVED/REJECTED')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    operator: Optional[str] = Field(None, description='操作员')


class AccountingLayer(BaseModel):
    """账务层回执"""
    mode: str = Field(..., description='模式: AUTO/MANUAL')
    status: str = Field(..., description='状态: PROCESSING/SUCCESS/FAILED/UNKNOWN')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='消息')


class SettlementStage(BaseModel):
    """阶段3: 结算执行与回执"""
    transmission_layer: Optional[TransmissionLayer] = Field(None, description='传输层回执（SWIFT路径）')
    manual_confirm: Optional[ManualConfirm] = Field(None, description='人工确认（CBMNet路径）')
    accounting_layer: AccountingLayer = Field(..., description='账务层回执')


class ReversalProcessing(BaseModel):
    """资金冲正"""
    status: str = Field(..., description='状态: PROCESSING/SUCCESS/FAILED')
    timestamp: Optional[datetime] = Field(None, description='时间戳')
    message: Optional[str] = Field(None, description='消息')


class CancellationStage(BaseModel):
    """阶段4: 结算撤销"""
    transmission_layer: Optional[TransmissionLayer] = Field(None, description='传输层（SWIFT路径）')
    reversal_processing: ReversalProcessing = Field(..., description='资金冲正')


class ActionEntry(BaseModel):
    """操作入口"""
    type: str = Field(..., description='入口类型: BUTTON/LINK')
    label: str = Field(..., description='显示文本')
    url: Optional[str] = Field(None, description='链接地址')
    action: Optional[str] = Field(None, description='操作标识')


class OperationGuide(BaseModel):
    """操作指引"""
    next_action: str = Field(..., description='下一步操作')
    action_entry: Optional[ActionEntry] = Field(None, description='操作入口')
    notes: Optional[str] = Field(None, description='注意事项')
    estimated_time: Optional[str] = Field(None, description='预计时间')


class FlowNode(BaseModel):
    """流程节点"""
    id: str = Field(..., description='节点ID')
    name: str = Field(..., description='节点名称')
    status: str = Field(..., description='节点状态: COMPLETED/CURRENT/PENDING/FAILED/BLOCKED/WAITING_APPROVAL')
    timestamp: Optional[datetime] = Field(None, description='完成时间')


class PaymentProgress(BaseModel):
    """现金流收付进度（4阶段流程）"""
    current_stage: str = Field(..., description='当前阶段')
    current_status: str = Field(..., description='当前状态')
    sending_route: str = Field(..., description='发送路径: SWIFT/CBMNet/INTERNAL')
    progress_percentage: int = Field(..., description='进度百分比')
    
    netting_stage: Optional[NettingStage] = Field(None, description='阶段1: 清算轧差')
    compliance_stage: Optional[ComplianceStage] = Field(None, description='阶段2: 合规准入')
    settlement_stage: Optional[SettlementStage] = Field(None, description='阶段3: 结算执行与回执')
    cancellation_stage: Optional[CancellationStage] = Field(None, description='阶段4: 结算撤销')
    
    flow_visualization: List[FlowNode] = Field(..., description='流程可视化数据')
    operation_guide: Optional[OperationGuide] = Field(None, description='操作指引')
    
    class Config:
        populate_by_name = True
