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
        
        根据需求文档功能7定义的14个场景配置操作指引规则。
        """
        self.transaction_guide_rules = {
            # 场景1: SWIFT证实发送RMC失败
            'swift_confirmation_rmc_failed': {
                'next_action': '联系SWIFT技术支持，检查RMC连接状态',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '请确认RMC服务状态正常后重试',
                'estimated_time': '15-30分钟'
            },
            
            # 场景2: SWIFT证实FTM发送失败
            'swift_confirmation_ftm_failed': {
                'next_action': '检查FTM报文格式，重新发送',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='重新发送FTM',
                    action='resend_ftm'
                ),
                'notes': '请检查报文格式是否符合SWIFT标准',
                'estimated_time': '5-10分钟'
            },
            
            # 场景3: 证实匹配失败
            'confirmation_match_failed': {
                'next_action': '联系交易对手方核对交易信息，进行人工匹配',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='人工匹配处理',
                    action='manual_match'
                ),
                'notes': '请核对交易金额、日期、账户等关键信息是否一致',
                'estimated_time': '30-60分钟'
            },
            
            # 场景4: 证实匹配成功
            'confirmation_match_success': {
                'next_action': '系统自动进入收付发报流程',
                'action_entry': None,
                'notes': '无需人工操作，系统将自动处理',
                'estimated_time': '自动处理'
            },
            
            # 场景5: 反洗钱检查等待中
            'aml_waiting': {
                'next_action': '等待反洗钱系统审核完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='反洗钱系统查询',
                    url='/aml/query',
                    action='view_aml_status'
                ),
                'notes': '反洗钱审核通常在1-2小时内完成',
                'estimated_time': '1-2小时'
            },
            
            # 场景6: 反洗钱检查失败
            'aml_failed': {
                'next_action': '联系反洗钱部门，提供补充材料或申请人工审核',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='反洗钱人工审核申请',
                    action='apply_aml_manual_review'
                ),
                'notes': '请准备相关交易背景材料和客户信息',
                'estimated_time': '2-4小时'
            },
            
            # 场景7: 收付结算发报RMC失败
            'settlement_rmc_failed': {
                'next_action': '检查RMC连接状态，联系SWIFT技术支持',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': '请确认RMC服务状态正常后重试',
                'estimated_time': '15-30分钟'
            },
            
            # 场景8: 收付结算发报FTM失败
            'settlement_ftm_failed': {
                'next_action': '检查报文格式，重新发送FTM',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='重新发送FTM',
                    action='resend_settlement_ftm'
                ),
                'notes': '请检查报文格式是否符合SWIFT标准',
                'estimated_time': '5-10分钟'
            },
            
            # 场景9: 核心入账成功
            'core_success': {
                'next_action': '流程已完成，无需操作',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看账务详情',
                    url='/accounting/detail',
                    action='view_accounting_detail'
                ),
                'notes': '交易已成功完成',
                'estimated_time': '已完成'
            },
            
            # 场景10: 核心入账失败
            'core_failed': {
                'next_action': '查询内部账划转情况，联系核心系统支持',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '请检查账户余额和账户状态',
                'estimated_time': '30-60分钟'
            },
            
            # 场景11: 核心入账状态不明
            'core_unknown': {
                'next_action': '查询内部账划转情况，确认入账状态',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '请核实核心系统的入账记录',
                'estimated_time': '15-30分钟'
            },
            
            # 场景12: 撤销报文发送中
            'cancellation_processing': {
                'next_action': '等待撤销报文发送完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看撤销进度',
                    url='/cancellation/progress',
                    action='view_cancellation_progress'
                ),
                'notes': '撤销流程通常在10-20分钟内完成',
                'estimated_time': '10-20分钟'
            },
            
            # 场景13: 流程正常进行中（无异常）
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
            },
            
            # 场景14: 内部账结算（无SWIFT）
            'internal_settlement': {
                'next_action': '等待核心系统处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='核心系统查询',
                    url='/core/query',
                    action='view_core_status'
                ),
                'notes': '内部账结算通常在5-10分钟内完成',
                'estimated_time': '5-10分钟'
            }
        }
    
    def _configure_cash_flow_guide_rules(self):
        """配置现金流操作指引规则
        
        根据现金流的不同状态配置操作指引规则。
        """
        self.cash_flow_guide_rules = {
            # 待反洗钱检查
            'pending_aml': {
                'next_action': '等待反洗钱系统审核完成',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='反洗钱系统查询',
                    url='/aml/query',
                    action='view_aml_status'
                ),
                'notes': '反洗钱审核通常在1-2小时内完成',
                'estimated_time': '1-2小时'
            },
            
            # 反洗钱拒绝
            'aml_rejected': {
                'next_action': '联系反洗钱部门，提供补充材料或申请人工审核',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='反洗钱人工审核申请',
                    action='apply_aml_manual_review'
                ),
                'notes': '请准备相关交易背景材料和客户信息',
                'estimated_time': '2-4小时'
            },
            
            # 反洗钱通过
            'aml_approved': {
                'next_action': '系统自动进入SWIFT发报流程',
                'action_entry': None,
                'notes': '无需人工操作，系统将自动处理',
                'estimated_time': '自动处理'
            },
            
            # 待SWIFT发报
            'pending_swift': {
                'next_action': '等待SWIFT报文发送',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='SWIFT系统监控',
                    url='/swift/monitoring',
                    action='view_swift_monitoring'
                ),
                'notes': 'SWIFT发报通常在10-15分钟内完成',
                'estimated_time': '10-15分钟'
            },
            
            # SWIFT发送失败
            'swift_failed': {
                'next_action': '检查SWIFT连接状态，联系SWIFT技术支持',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='重新发送SWIFT',
                    action='resend_swift'
                ),
                'notes': '请确认SWIFT服务状态正常后重试',
                'estimated_time': '15-30分钟'
            },
            
            # SWIFT已发送
            'swift_sent': {
                'next_action': '等待核心系统入账',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='核心系统查询',
                    url='/core/query',
                    action='view_core_status'
                ),
                'notes': '核心入账通常在5-10分钟内完成',
                'estimated_time': '5-10分钟'
            },
            
            # 待核心入账
            'pending_core': {
                'next_action': '等待核心系统处理',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='核心系统查询',
                    url='/core/query',
                    action='view_core_status'
                ),
                'notes': '核心入账通常在5-10分钟内完成',
                'estimated_time': '5-10分钟'
            },
            
            # 核心入账成功
            'core_success': {
                'next_action': '流程已完成，无需操作',
                'action_entry': ActionEntry(
                    type='LINK',
                    label='查看账务详情',
                    url='/accounting/detail',
                    action='view_accounting_detail'
                ),
                'notes': '现金流已成功完成',
                'estimated_time': '已完成'
            },
            
            # 核心入账失败
            'core_failed': {
                'next_action': '查询内部账划转情况，联系核心系统支持',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '请检查账户余额和账户状态',
                'estimated_time': '30-60分钟'
            },
            
            # 核心入账状态不明
            'core_unknown': {
                'next_action': '查询内部账划转情况，确认入账状态',
                'action_entry': ActionEntry(
                    type='BUTTON',
                    label='内部账划转查询',
                    action='query_internal_transfer'
                ),
                'notes': '请核实核心系统的入账记录',
                'estimated_time': '15-30分钟'
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
        
        根据交易的证实方式、结算方式、匹配状态等信息，
        识别交易当前所处的具体场景。
        """
        # 检查证实匹配状态
        if transaction.confirmation_match_status == MatchStatus.UNMATCHED:
            return 'confirmation_match_failed'
        elif transaction.confirmation_match_status == MatchStatus.MATCHED:
            # 匹配成功后，检查后续流程
            pass
        elif transaction.confirmation_match_status == MatchStatus.PENDING:
            # 等待匹配
            return 'normal_processing'
        
        # 检查结算方式
        settlement_method = transaction.settlement_method
        
        # 判断是否需要SWIFT流程
        needs_swift = settlement_method in [
            SettlementMethod.GROSS,
            SettlementMethod.NET,
            SettlementMethod.CENTRALIZED
        ]
        
        if needs_swift:
            # SWIFT流程
            # 这里简化处理，实际应该根据事件记录判断具体状态
            # 假设流程正常进行
            return 'normal_processing'
        else:
            # 内部账结算
            return 'internal_settlement'
    
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
            CashFlowStatus.PENDING_AML: 'pending_aml',
            CashFlowStatus.AML_APPROVED: 'aml_approved',
            CashFlowStatus.AML_REJECTED: 'aml_rejected',
            CashFlowStatus.PENDING_SWIFT: 'pending_swift',
            CashFlowStatus.SWIFT_SENT: 'swift_sent',
            CashFlowStatus.SWIFT_FAILED: 'swift_failed',
            CashFlowStatus.PENDING_CORE: 'pending_core',
            CashFlowStatus.CORE_SUCCESS: 'core_success',
            CashFlowStatus.CORE_FAILED: 'core_failed',
            CashFlowStatus.CORE_UNKNOWN: 'core_unknown'
        }
        
        return status_to_scenario.get(current_status, 'pending_core')
