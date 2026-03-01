"""Operation guide service for generating operation guidance based on status"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.cash_flow_repository import CashFlowRepository
from app.models.enums import (
    MatchStatus, CashFlowStatus, SettlementMethod, ConfirmationType
)


class ActionEntry(BaseModel):
    """操作入口"""
    type: str = Field(..., description='入口类型: BUTTON, LINK')
    label: str = Field(..., description='显示文本')
    url: Optional[str] = Field(None, description='链接地址')
    action: Optional[str] = Field(None, description='操作标识')


class OperationGuide(BaseModel):
    """操作指引"""
    next_action: str = Field(..., description='下一步操作')
    action_entry: Optional[ActionEntry] = Field(None, description='操作入口')
    notes: Optional[str] = Field(None, description='注意事项')
    estimated_time: Optional[str] = Field(None, description='预计时间')


class OperationGuideService:
    """操作指引服务
    
    根据交易和现金流的当前状态，动态生成操作指引，
    明确告知用户下一步应该执行的操作。
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.cash_flow_repo = CashFlowRepository(db)
        
        # 配置操作指引规则
        self._configure_transaction_guide_rules()
        self._configure_cash_flow_guide_rules()
    
    def _configure_transaction_guide_rules(self):
        """配置交易操作指引规则
        
        根据需求文档功能8定义的场景配置操作指引规则。
        涵盖交易进度跟踪、交易修改流程、交易撤销流程的所有场景。
        """
        self.transaction_guide_rules = {
            # ===== 节点1: 后台复核 =====
            # 场景 1.1: 后台复核 - 复核中
            'back_office_in_review': {
                'next_action': '请在"后线工作台 - 交易复核"进行审批',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 交易复核',
                    url='/backoffice/review',
                    action='review_transaction'
                ),
                'notes': '交易已同步至后线，等待结算员核对交易要素与清算路径',
                'estimated_time': '根据审批流程而定'
            },
            
            # 场景 1.2: 后台复核 - 复核通过
            'back_office_approved': {
                'next_action': '系统将自动进入SWIFT证实回执状态节点（仅适用于外汇掉期和拆借交易）',
                'action_entry': None,
                'notes': '交易复核通过，已触发后续证实流程',
                'estimated_time': '自动处理'
            },
            
            # 场景 1.3: 后台复核 - 交易已删除
            'back_office_deleted': {
                'next_action': '流程已终结，无需操作',
                'action_entry': None,
                'notes': '交易已被删除',
                'estimated_time': None
            },
            
            # ===== 节点2: SWIFT证实回执状态 =====
            # 场景 2.1: SWIFT证实 - RMC发送中
            'swift_rmc_sending': {
                'next_action': '请等待RMC回执',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '已复核通过，系统正在发送RMC报文至SWIFT网关',
                'estimated_time': '1-3分钟'
            },
            
            # 场景 2.2: SWIFT证实 - RMC回执成功
            'swift_rmc_success': {
                'next_action': '系统将自动发送FTM报文',
                'action_entry': None,
                'notes': 'RMC回执成功，系统自动触发FTM发送',
                'estimated_time': '自动处理'
            },
            
            # 场景 2.3: SWIFT证实 - RMC回执失败
            'swift_rmc_failed': {
                'next_action': '报文出口受阻，请检查报文规范或联系技术支持',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': 'RMC回执失败，流程已阻断，无后续FTM回执',
                'estimated_time': '需人工处理'
            },
            
            # 场景 2.4: SWIFT证实 - FTM发送中
            'swift_ftm_sending': {
                'next_action': '请等待FTM回执',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': 'RMC回执成功，系统正在发送FTM报文至SWIFT网络',
                'estimated_time': '1-3分钟'
            },
            
            # 场景 2.5: SWIFT证实 - FTM回执成功
            'swift_ftm_success': {
                'next_action': '系统将自动进入证实匹配节点',
                'action_entry': None,
                'notes': 'FTM回执成功，报文正式送出',
                'estimated_time': '自动处理'
            },
            
            # 场景 2.6: SWIFT证实 - FTM回执失败
            'swift_ftm_failed': {
                'next_action': '报文传输中断，请在"后线工作台 - 证实报文"进行处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 证实报文',
                    url='/backoffice/confirmation',
                    action='handle_confirmation'
                ),
                'notes': 'FTM回执失败',
                'estimated_time': '需人工处理'
            },
            
            # ===== 节点3: 证实匹配 =====
            # 场景 3.1: 证实匹配 - 待匹配
            'match_pending': {
                'next_action': '等待系统自动匹配',
                'action_entry': None,
                'notes': 'FTM回执成功，等待证实匹配处理',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 3.2: 证实匹配 - 匹配中
            'match_processing': {
                'next_action': '等待匹配结果',
                'action_entry': None,
                'notes': '系统正在对对手方报文进行自动打分',
                'estimated_time': '1-5分钟'
            },
            
            # 场景 3.3: 证实匹配 - 匹配成功
            'match_success': {
                'next_action': '交易进度跟踪完成，将进入收付流程',
                'action_entry': None,
                'notes': '证实匹配成功',
                'estimated_time': None
            },
            
            # 场景 3.4: 证实匹配 - 手工处理
            'match_manual': {
                'next_action': '请在"后线工作台 - 证实匹配"中进行手工匹配或执行撤销处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 证实匹配',
                    url='/backoffice/matching',
                    action='manual_match'
                ),
                'notes': '自动匹配失败，需要结算员执行人工匹配或撤销处理',
                'estimated_time': '需人工处理'
            },
            
            # ===== 交易修改流程 =====
            # 场景 4.1: 交易修改 - 原交易已回退
            'modification_returned': {
                'next_action': '前台人员可以修改交易并重新提交',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='修改交易',
                    action='modify_transaction'
                ),
                'notes': '原交易已被后台结算人员回退',
                'estimated_time': '需前台操作'
            },
            
            # 场景 4.2: 交易修改 - 修改后交易审核中
            'modification_reviewing': {
                'next_action': '请在"后线工作台 - 交易复核"进行审批',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 交易复核',
                    url='/backoffice/review',
                    action='review_transaction'
                ),
                'notes': '修改后的交易已提交至后台，等待审核',
                'estimated_time': '根据审批流程而定'
            },
            
            # 场景 4.3: 交易修改 - 证实报文重发中
            'modification_resending': {
                'next_action': '等待报文发送完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '系统正在发送cancel报文或重发证实报文',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 4.4: 交易修改 - 修改完成
            'modification_completed': {
                'next_action': '流程完成，可查看修改后的交易详情',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看交易详情',
                    url='/transaction/detail',
                    action='view_detail'
                ),
                'notes': '修改后的交易已完成全部流程',
                'estimated_time': None
            },
            
            # ===== 交易撤销流程 =====
            # 场景 5.1: 交易撤销 - 原交易已回退
            'cancellation_returned': {
                'next_action': '前台人员可以撤销交易',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='撤销交易',
                    action='cancel_transaction'
                ),
                'notes': '原交易已被后台结算人员回退',
                'estimated_time': '需前台操作'
            },
            
            # 场景 5.2: 交易撤销 - 撤销事件审核中
            'cancellation_reviewing': {
                'next_action': '请在"后线工作台 - 交易复核"进行审批',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 交易复核',
                    url='/backoffice/review',
                    action='review_transaction'
                ),
                'notes': '撤销事件已提交至后台，等待审核',
                'estimated_time': '根据审批流程而定'
            },
            
            # 场景 5.3: 交易撤销 - 撤销报文发送中
            'cancellation_sending': {
                'next_action': '等待撤销报文发送完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '系统正在发送cancel证实报文',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 5.4: 交易撤销 - 撤销完成
            'cancellation_completed': {
                'next_action': '流程已终止，无需操作',
                'action_entry': None,
                'notes': '交易撤销完成',
                'estimated_time': None
            },
            
            # ===== 默认场景 =====
            # 场景: 流程正常进行中（无异常）
            'normal_processing': {
                'next_action': '系统自动处理中，无需人工干预',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看详细进度',
                    url='/transaction/progress',
                    action='view_progress'
                ),
                'notes': '系统将自动完成后续流程',
                'estimated_time': '自动处理'
            }
        }
    
    def _configure_cash_flow_guide_rules(self):
        """配置现金流操作指引规则
        
        根据需求文档功能8定义的结算支付进度跟踪场景配置操作指引规则。
        涵盖清算轧差、合规准入、结算执行与回执、收付撤销的所有场景。
        """
        self.cash_flow_guide_rules = {
            # ===== 阶段1: 清算轧差 =====
            # 场景 6.1: 清算轧差 - 等待证实（外汇/拆借）
            'netting_waiting_confirmation_fx': {
                'next_action': '请在"后线工作台 - 证实匹配"中进行手工匹配或执行撤销处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 证实匹配',
                    url='/backoffice/matching',
                    action='manual_match'
                ),
                'notes': '证实匹配未成功',
                'estimated_time': '需人工处理'
            },
            
            # 场景 6.2: 清算轧差 - 等待证实（现券/回购）
            'netting_waiting_confirmation_bond': {
                'next_action': '等待文本证实流程完成',
                'action_entry': None,
                'notes': '文本证实未通过',
                'estimated_time': '根据流程而定'
            },
            
            # 场景 6.3: 清算轧差 - 证实完成
            'netting_confirmation_completed': {
                'next_action': '系统将自动进入轧差执行节点',
                'action_entry': None,
                'notes': '证实匹配成功',
                'estimated_time': '自动处理'
            },
            
            # 场景 6.4: 清算轧差 - 待轧差
            'netting_pending': {
                'next_action': '等待系统日终批处理自动轧差，或在"后线工作台 - 清算轧差"中手动执行轧差操作',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 清算轧差',
                    url='/backoffice/netting',
                    action='manual_netting'
                ),
                'notes': '证实匹配成功，等待轧差处理',
                'estimated_time': '日终批处理时间或手动操作'
            },
            
            # 场景 6.5: 清算轧差 - 自动轧差完成
            'netting_auto_completed': {
                'next_action': '系统将自动计算发报时机',
                'action_entry': None,
                'notes': '系统已完成轧差处理',
                'estimated_time': '自动处理'
            },
            
            # 场景 6.6: 清算轧差 - 手工轧差完成
            'netting_manual_completed': {
                'next_action': '系统将自动计算发报时机',
                'action_entry': None,
                'notes': '已完成手工轧差',
                'estimated_time': '自动处理'
            },
            
            # 场景 6.7: 清算轧差 - 待达发报日
            'netting_waiting_dispatch_date': {
                'next_action': '等待发报日到达（预计发报日期：YYYY-MM-DD，距离发报日还有 X 天）',
                'action_entry': None,
                'notes': '收付发报记录已生成，但未达到发报预定日（结算日 - N天）',
                'estimated_time': '等待发报日'
            },
            
            # 场景 6.8: 清算轧差 - 待发报
            'netting_pending_dispatch': {
                'next_action': '系统进入反洗钱检查阶段',
                'action_entry': None,
                'notes': '已到达发报预定日',
                'estimated_time': '自动处理'
            },
            
            # ===== 阶段2: 反洗钱检查 =====
            # 场景 7.1: 反洗钱检查 - 数据上送中
            'aml_data_submitting': {
                'next_action': '等待数据上送完成',
                'action_entry': None,
                'notes': '系统正在将结算指令信息推送至反洗钱系统',
                'estimated_time': '1-2分钟'
            },
            
            # 场景 7.2: 反洗钱检查 - 数据上送成功
            'aml_data_submitted': {
                'next_action': '系统将自动进入反洗钱检查',
                'action_entry': None,
                'notes': '数据已成功推送至反洗钱系统',
                'estimated_time': '自动处理'
            },
            
            # 场景 7.3: 反洗钱检查 - 数据上送失败
            'aml_data_submission_failed': {
                'next_action': '请检查反洗钱系统连接状态或联系技术支持',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='系统监控',
                    url='/system/monitoring',
                    action='view_monitoring'
                ),
                'notes': '数据上送失败，无法进行反洗钱校验',
                'estimated_time': '需人工处理'
            },
            
            # 场景 7.4: 反洗钱检查 - 反洗钱扫描中
            'aml_scanning': {
                'next_action': '等待反洗钱系统审核完成',
                'action_entry': None,
                'notes': '系统正在进行反洗钱检查',
                'estimated_time': '1-5分钟'
            },
            
            # 场景 7.5: 反洗钱检查 - 合规校验通过
            'aml_approved': {
                'next_action': '系统将自动进入路径决策与发送准入阶段',
                'action_entry': None,
                'notes': '反洗钱校验通过，所有风险检查均通过',
                'estimated_time': '自动处理'
            },
            
            # 场景 7.6: 反洗钱检查 - 反洗钱拦截
            'aml_blocked': {
                'next_action': '流程已终止，请联系相关人员',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='申请人工审核',
                    action='request_manual_review'
                ),
                'notes': '触发反洗钱硬拦截，风险提示命中（错误码：[系统错误码]，拦截原因：[具体原因]）',
                'estimated_time': '需人工处理'
            },
            
            # ===== 阶段2.5: 路径决策与发送准入 =====
            # 场景 8.1: 路径决策 - 路径判定中
            'route_determining': {
                'next_action': '等待路径判定完成',
                'action_entry': None,
                'notes': '系统正在根据SSI参数判断发送路径',
                'estimated_time': '1-2分钟'
            },
            
            # 场景 8.2: 路径决策 - SWIFT路径已确定
            'route_swift_determined': {
                'next_action': '系统将进入人工收付审批流程',
                'action_entry': None,
                'notes': '反洗钱检验通过',
                'estimated_time': '自动处理'
            },
            
            # 场景 8.3: 路径决策 - CBMNet路径已确定
            'route_cbmnet_determined': {
                'next_action': '系统将进入CBMNet路径线下处理流程',
                'action_entry': None,
                'notes': '反洗钱检验通过',
                'estimated_time': '自动处理'
            },
            
            # 场景 8.4: SWIFT路径 - 待审批
            'swift_pending_approval': {
                'next_action': '请在"后线工作台 - 收付审批"中进行审批',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 收付审批',
                    url='/backoffice/approval',
                    action='approve_payment'
                ),
                'notes': 'SWIFT报文需进行人工审批，等待审批人员审批',
                'estimated_time': '根据审批流程而定'
            },
            
            # 场景 8.5: SWIFT路径 - 审批通过
            'swift_approval_approved': {
                'next_action': '系统将自动进入结算执行与回执确认阶段（RMC/FTM发送）',
                'action_entry': None,
                'notes': '审批通过，SWIFT报文已获准发送',
                'estimated_time': '自动处理'
            },
            
            # 场景 8.6: SWIFT路径 - 审批拒绝
            'swift_approval_rejected': {
                'next_action': '流程已阻断，请联系审批人员了解拒绝原因',
                'action_entry': None,
                'notes': '审批人员拒绝审批，流程已终止',
                'estimated_time': None
            },
            
            # 场景 8.7: CBMNet路径 - 待线下处理
            'cbmnet_pending_manual': {
                'next_action': '请导出收付指令',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='导出收付指令',
                    action='export_payment_instruction'
                ),
                'notes': '系统已生成收付指令，等待结算员导出并在CBMNet系统完成线下操作',
                'estimated_time': '需人工处理'
            },
            
            # 场景 8.8: CBMNet路径 - 人工确认通过
            'cbmnet_manual_confirmed': {
                'next_action': '系统将直接进入核心入账环节（跳过RMC/FTM发送）',
                'action_entry': None,
                'notes': '结算员已完成CBMNet线下操作并确认通过',
                'estimated_time': '自动处理'
            },
            
            # 场景 8.9: CBMNet路径 - 确认拒绝
            'cbmnet_manual_rejected': {
                'next_action': '流程已终止，请联系相关人员',
                'action_entry': None,
                'notes': '人工确认拒绝或线下处理失败，流程已终止',
                'estimated_time': None
            },
            
            # ===== 阶段3: 结算执行与回执确认 =====
            # 场景 9.1: 结算执行 - RMC发送中
            'settlement_rmc_sending': {
                'next_action': '请等待RMC回执',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '收付审批通过，系统正在发送RMC报文至SWIFT网关',
                'estimated_time': '1-3分钟'
            },
            
            # 场景 9.2: 结算执行 - RMC回执成功
            'settlement_rmc_success': {
                'next_action': '系统将自动发送FTM报文',
                'action_entry': None,
                'notes': '已收到RMC回执，RMC发送成功',
                'estimated_time': '自动处理'
            },
            
            # 场景 9.3: 结算执行 - RMC回执失败
            'settlement_rmc_failed': {
                'next_action': '请检查报文规范或联系技术支持',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '未收到RMC回执，流程已阻断',
                'estimated_time': '需人工处理'
            },
            
            # 场景 9.4: 结算执行 - FTM发送中
            'settlement_ftm_sending': {
                'next_action': '请等待FTM回执',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': 'RMC回执成功，系统正在发送FTM报文至SWIFT网络',
                'estimated_time': '1-3分钟'
            },
            
            # 场景 9.5: 结算执行 - FTM回执成功
            'settlement_ftm_success': {
                'next_action': '系统将自动进入核心入账处理',
                'action_entry': None,
                'notes': '已收到FTM回执，报文正式出库',
                'estimated_time': '自动处理'
            },
            
            # 场景 9.6: 结算执行 - FTM发送失败
            'settlement_ftm_failed': {
                'next_action': '请在"后线工作台 - 证实报文"中执行"补发处理"',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 证实报文',
                    url='/backoffice/confirmation',
                    action='resend_message'
                ),
                'notes': 'FTM发送失败，报文传输中断',
                'estimated_time': '需人工处理'
            },
            
            # 场景 9.7: 结算执行 - CBMNet路径核心入账
            'settlement_cbmnet_core': {
                'next_action': '系统将自动推送账务信息至核心系统',
                'action_entry': None,
                'notes': 'CBMNet路径人工确认通过，跳过RMC/FTM发送，直接进入核心入账',
                'estimated_time': '自动处理'
            },
            
            # 场景 9.8: 结算执行 - 核心入账处理中
            'settlement_core_processing': {
                'next_action': '等待核心系统处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='核心系统查询',
                    url='/core/query',
                    action='view_core_status'
                ),
                'notes': '账务信息已送达核心系统，等待回执反馈',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 9.9: 结算执行 - 入账成功（结算完成）
            'settlement_core_success': {
                'next_action': '流程已完成，无需操作',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看账务详情',
                    url='/accounting/detail',
                    action='view_accounting_detail'
                ),
                'notes': '核心入账成功',
                'estimated_time': None
            },
            
            # 场景 9.10: 结算执行 - 入账失败
            'settlement_core_failed': {
                'next_action': '请在"内部账划转查询"进行确认',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '核心入账失败，回执反馈入账失败',
                'estimated_time': '需人工处理'
            },
            
            # 场景 9.11: 结算执行 - 入账不明
            'settlement_core_unknown': {
                'next_action': '请在"内部账划转查询"进行确认',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '核心系统超时或未给出明确回执，入账状态不明',
                'estimated_time': '需人工处理'
            },
            
            # ===== 收付撤销流程 =====
            # 场景 10.1: 收付撤销 - 撤销处理中
            'cancellation_processing': {
                'next_action': '请确认撤销报文内容并进行审批',
                'action_entry': None,
                'notes': '结算人员正在执行收付撤销处理，系统正在生成撤销报文',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 10.2: 收付撤销 - 待审批（可选）
            'cancellation_pending_approval': {
                'next_action': '请等待审批人员审批',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 收付审批',
                    url='/backoffice/approval',
                    action='approve_cancellation'
                ),
                'notes': '撤销报文已生成，等待审批人员审批',
                'estimated_time': '根据审批流程而定'
            },
            
            # 场景 10.3: 收付撤销 - 审批拒绝（可选）
            'cancellation_approval_rejected': {
                'next_action': '撤销操作已终止，请联系审批人员了解拒绝原因',
                'action_entry': None,
                'notes': '审批人员拒绝撤销审批，撤销操作终止',
                'estimated_time': None
            },
            
            # 场景 10.4: 收付撤销 - 撤销报文发送中
            'cancellation_sending': {
                'next_action': '等待撤销报文发送完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '系统正在发送撤销报文（cancel报文）至代理行',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 10.5: 收付撤销 - 撤销成功
            'cancellation_success': {
                'next_action': '请进行现金流调整或录入单边现金流进行调整',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='现金流调整',
                    action='adjust_cash_flow'
                ),
                'notes': '收付已撤销，收付状态已回退至"待收付"，轧差状态已回退至"待轧差"',
                'estimated_time': '需人工操作'
            },
            
            # 场景 10.6: 收付撤销 - 重做中（方案1：现金流修改）
            'cancellation_redo_modify': {
                'next_action': '等待系统完成清算记录计算，将重新进入结算支付进度跟踪流程',
                'action_entry': None,
                'notes': '已发起现金流修改，系统正在重新计算清算记录',
                'estimated_time': '5-10分钟'
            },
            
            # 场景 10.7: 收付撤销 - 重做中（方案2：补做单边现金流）
            'cancellation_redo_unilateral': {
                'next_action': '请在"后线工作台 - 清算轧差"中手动勾选现金流记录并执行手工轧差操作',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='后线工作台 - 清算轧差',
                    url='/backoffice/netting',
                    action='manual_netting'
                ),
                'notes': '已补做单边现金流，等待手工清算轧差处理',
                'estimated_time': '需人工操作'
            }
        }
    
    def get_transaction_guide(
        self,
        transaction_id: str
    ) -> OperationGuide:
        """获取交易操作指引
        
        根据交易当前的生命周期状态，动态生成操作指引，
        明确告知用户下一步应该执行的操作。
        
        Args:
            transaction_id: 交易流水号
            
        Returns:
            OperationGuide: 操作指引信息
            
        Raises:
            ValueError: 当交易不存在时
        """
        # 查询交易
        transaction = self.transaction_repo.find_by_transaction_id(transaction_id)
        if not transaction:
            raise ValueError(f'RESOURCE_NOT_FOUND: 未找到交易 {transaction_id}')
        
        # 根据交易状态确定场景
        scenario = self._identify_transaction_scenario(transaction)
        
        # 获取对应的操作指引
        guide_config = self.transaction_guide_rules.get(
            scenario,
            self.transaction_guide_rules['normal_processing']
        )
        
        return OperationGuide(**guide_config)
    
    def _identify_transaction_scenario(self, transaction) -> str:
        """识别交易当前所处的场景
        
        根据交易的后台复核状态、SWIFT回执状态、证实匹配状态等信息，
        识别交易当前所处的具体场景。
        """
        # 检查后台复核状态
        back_office_status = transaction.back_office_status
        
        if back_office_status == '复核中':
            return 'back_office_in_review'
        elif back_office_status == '已删除':
            return 'back_office_deleted'
        elif back_office_status == '复核通过':
            # 复核通过后，检查后续流程
            pass
        
        # 检查是否为外汇掉期或拆借产品（需要SWIFT证实）
        is_swap_or_lending = transaction.product in [
            ProductType.FX_SWAP,
            ProductType.INTERBANK_LENDING
        ]
        
        if is_swap_or_lending:
            # 检查SWIFT证实回执状态
            rmc_status = getattr(transaction, 'swift_rmc_status', 'SUCCESS')
            ftm_status = getattr(transaction, 'swift_ftm_status', 'SUCCESS')
            
            if rmc_status == 'SENDING':
                return 'swift_rmc_sending'
            elif rmc_status == 'FAILED':
                return 'swift_rmc_failed'
            elif rmc_status == 'SUCCESS':
                if ftm_status == 'SENDING':
                    return 'swift_ftm_sending'
                elif ftm_status == 'FAILED':
                    return 'swift_ftm_failed'
                elif ftm_status == 'SUCCESS':
                    # FTM成功后，检查证实匹配状态
                    pass
        
        # 检查证实匹配状态
        match_status = transaction.confirmation_match_status
        
        if match_status == MatchStatus.PENDING:
            # 检查是否在匹配中
            if hasattr(transaction, 'matching_in_progress') and transaction.matching_in_progress:
                return 'match_processing'
            else:
                return 'match_pending'
        elif match_status == MatchStatus.UNMATCHED:
            return 'match_manual'
        elif match_status == MatchStatus.MATCHED:
            return 'match_success'
        
        # 检查是否为交易修改流程
        if hasattr(transaction, 'is_modification') and transaction.is_modification:
            modification_status = getattr(transaction, 'modification_status', None)
            if modification_status == 'returned':
                return 'modification_returned'
            elif modification_status == 'reviewing':
                return 'modification_reviewing'
            elif modification_status == 'resending':
                return 'modification_resending'
            elif modification_status == 'completed':
                return 'modification_completed'
        
        # 检查是否为交易撤销流程
        if hasattr(transaction, 'is_cancellation') and transaction.is_cancellation:
            cancellation_status = getattr(transaction, 'cancellation_status', None)
            if cancellation_status == 'returned':
                return 'cancellation_returned'
            elif cancellation_status == 'reviewing':
                return 'cancellation_reviewing'
            elif cancellation_status == 'sending':
                return 'cancellation_sending'
            elif cancellation_status == 'completed':
                return 'cancellation_completed'
        
        # 默认为正常处理中
        return 'normal_processing'
    
    def get_cash_flow_guide(
        self,
        cash_flow_id: str
    ) -> OperationGuide:
        """获取现金流操作指引
        
        根据现金流当前的收付状态，动态生成操作指引，
        明确告知用户下一步应该执行的操作。
        
        Args:
            cash_flow_id: 现金流内部ID
            
        Returns:
            OperationGuide: 操作指引信息
            
        Raises:
            ValueError: 当现金流不存在时
        """
        # 查询现金流
        cash_flow = self.cash_flow_repo.find_by_cash_flow_id(cash_flow_id)
        if not cash_flow:
            raise ValueError(f'RESOURCE_NOT_FOUND: 未找到现金流 {cash_flow_id}')
        
        # 根据现金流状态确定场景
        scenario = self._identify_cash_flow_scenario(cash_flow)
        
        # 获取对应的操作指引
        guide_config = self.cash_flow_guide_rules.get(
            scenario,
            {
                'next_action': '系统处理中',
                'action_entry': None,
                'notes': '请等待系统处理',
                'estimated_time': '处理中'
            }
        )
        
        return OperationGuide(**guide_config)
    
    def _identify_cash_flow_scenario(self, cash_flow) -> str:
        """识别现金流当前所处的场景
        
        根据现金流的当前状态，识别对应的场景。
        """
        current_status = cash_flow.current_status
        
        # 映射现金流状态到场景
        status_to_scenario = {
            # 阶段1: 清算轧差
            CashFlowStatus.PENDING_NETTING: 'netting_pending',
            CashFlowStatus.AUTO_NETTING_COMPLETE: 'netting_auto_completed',
            CashFlowStatus.MANUAL_NETTING_COMPLETE: 'netting_manual_completed',
            CashFlowStatus.PENDING_DISPATCH: 'netting_pending_dispatch',
            
            # 阶段2: 反洗钱检查
            CashFlowStatus.COMPLIANCE_CHECKING: 'aml_scanning',
            CashFlowStatus.COMPLIANCE_APPROVED: 'aml_approved',
            CashFlowStatus.COMPLIANCE_BLOCKED: 'aml_blocked',
            
            # 阶段2.5: 路径决策与发送准入
            CashFlowStatus.ROUTE_DETERMINED: 'route_swift_determined',  # 简化，实际应根据路径判断
            CashFlowStatus.PENDING_APPROVAL: 'swift_pending_approval',
            CashFlowStatus.APPROVAL_APPROVED: 'swift_approval_approved',
            CashFlowStatus.APPROVAL_REJECTED: 'swift_approval_rejected',
            
            # 阶段3: 结算执行与回执 - SWIFT路径
            CashFlowStatus.RMC_SENDING: 'settlement_rmc_sending',
            CashFlowStatus.RMC_SUCCESS: 'settlement_rmc_success',
            CashFlowStatus.RMC_FAILED: 'settlement_rmc_failed',
            CashFlowStatus.FTM_SENDING: 'settlement_ftm_sending',
            CashFlowStatus.FTM_SUCCESS: 'settlement_ftm_success',
            CashFlowStatus.FTM_FAILED: 'settlement_ftm_failed',
            
            # 阶段3: 结算执行与回执 - CBMNet路径
            CashFlowStatus.PENDING_MANUAL_CONFIRM: 'cbmnet_pending_manual',
            CashFlowStatus.MANUAL_CONFIRM_APPROVED: 'cbmnet_manual_confirmed',
            CashFlowStatus.MANUAL_CONFIRM_REJECTED: 'cbmnet_manual_rejected',
            
            # 阶段3: 账务层回执（通用）
            CashFlowStatus.CORE_PROCESSING: 'settlement_core_processing',
            CashFlowStatus.CORE_SUCCESS: 'settlement_core_success',
            CashFlowStatus.CORE_FAILED: 'settlement_core_failed',
            CashFlowStatus.CORE_UNKNOWN: 'settlement_core_unknown',
            
            # 阶段4: 结算撤销
            CashFlowStatus.CANCEL_RMC_SENDING: 'cancellation_sending',
            CashFlowStatus.CANCEL_RMC_FAILED: 'cancellation_sending',
            CashFlowStatus.CANCEL_FTM_SENDING: 'cancellation_sending',
            CashFlowStatus.CANCEL_FTM_FAILED: 'cancellation_sending',
            CashFlowStatus.CANCEL_PROCESSING: 'cancellation_processing',
            CashFlowStatus.CANCEL_SUCCESS: 'cancellation_success',
            CashFlowStatus.CANCEL_FAILED: 'cancellation_processing'
        }
        
        scenario = status_to_scenario.get(current_status)
        
        # 如果没有匹配的场景，返回默认场景
        if not scenario:
            # 检查是否在待达发报日状态
            if current_status == CashFlowStatus.PENDING_DISPATCH:
                # 检查是否到达发报日
                dispatch_date = getattr(cash_flow, 'dispatch_date', None)
                if dispatch_date:
                    from datetime import datetime
                    today = datetime.now().date()
                    if today < dispatch_date:
                        return 'netting_waiting_dispatch_date'
                return 'netting_pending_dispatch'
            
            # 默认场景
            return 'settlement_core_processing'
        
        return scenario
