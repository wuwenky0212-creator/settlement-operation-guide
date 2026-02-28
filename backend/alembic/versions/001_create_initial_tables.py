"""Create initial tables

Revision ID: 001
Revises: 
Create Date: 2026-02-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('external_id', sa.String(100), primary_key=True, comment='外部流水号'),
        sa.Column('transaction_id', sa.String(100), nullable=False, comment='交易流水号'),
        sa.Column('parent_transaction_id', sa.String(100), nullable=True, comment='父交易流水号'),
        sa.Column('entry_date', sa.DateTime(), nullable=False, comment='录入日'),
        sa.Column('trade_date', sa.DateTime(), nullable=False, comment='交易日'),
        sa.Column('value_date', sa.DateTime(), nullable=False, comment='起息日'),
        sa.Column('maturity_date', sa.DateTime(), nullable=False, comment='到期日'),
        sa.Column('account', sa.String(100), nullable=False, comment='账户'),
        sa.Column('product', sa.String(50), nullable=False, comment='产品类型'),
        sa.Column('direction', sa.String(20), nullable=False, comment='买卖方向'),
        sa.Column('underlying', sa.String(200), nullable=False, comment='标的物'),
        sa.Column('counterparty', sa.String(200), nullable=False, comment='交易对手'),
        sa.Column('status', sa.String(20), nullable=False, comment='交易状态'),
        sa.Column('back_office_status', sa.String(50), nullable=False, comment='后线处理状态'),
        sa.Column('settlement_method', sa.String(50), nullable=False, comment='清算方式'),
        sa.Column('confirmation_number', sa.String(100), nullable=True, comment='证实编号'),
        sa.Column('confirmation_type', sa.String(20), nullable=False, comment='证实方式'),
        sa.Column('confirmation_match_type', sa.String(50), nullable=True, comment='证实匹配方式'),
        sa.Column('confirmation_match_status', sa.String(50), nullable=True, comment='证实匹配状态'),
        sa.Column('nature', sa.String(100), nullable=False, comment='交易性质'),
        sa.Column('source', sa.String(20), nullable=False, comment='交易来源'),
        sa.Column('latest_event_type', sa.String(50), nullable=True, comment='最新事件类型'),
        sa.Column('operating_institution', sa.String(200), nullable=False, comment='运营机构'),
        sa.Column('business_institution', sa.String(200), nullable=True, comment='业务机构'),
        sa.Column('trader', sa.String(100), nullable=False, comment='交易员'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1', comment='版本号（乐观锁）'),
        sa.Column('last_modified_date', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='最后修改日期'),
        sa.Column('last_modified_by', sa.String(100), nullable=False, comment='最后修改人'),
    )
    
    # Create indexes for transactions
    op.create_index('idx_transaction_id', 'transactions', ['transaction_id'], unique=True)
    op.create_index('idx_parent_transaction_id', 'transactions', ['parent_transaction_id'])
    op.create_index('idx_trade_date', 'transactions', ['trade_date'])
    op.create_index('idx_value_date', 'transactions', ['value_date'])
    op.create_index('idx_maturity_date', 'transactions', ['maturity_date'])
    op.create_index('idx_product', 'transactions', ['product'])
    op.create_index('idx_counterparty', 'transactions', ['counterparty'])
    op.create_index('idx_status', 'transactions', ['status'])
    op.create_index('idx_back_office_status', 'transactions', ['back_office_status'])
    op.create_index('idx_settlement_method', 'transactions', ['settlement_method'])
    op.create_index('idx_confirmation_type', 'transactions', ['confirmation_type'])
    op.create_index('idx_confirmation_match_status', 'transactions', ['confirmation_match_status'])
    op.create_index('idx_source', 'transactions', ['source'])
    op.create_index('idx_operating_institution', 'transactions', ['operating_institution'])
    op.create_index('idx_trade_date_status', 'transactions', ['trade_date', 'status'])
    op.create_index('idx_counterparty_product', 'transactions', ['counterparty', 'product'])
    op.create_index('idx_operating_institution_trade_date', 'transactions', ['operating_institution', 'trade_date'])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('event_id', sa.String(100), primary_key=True, comment='事件ID'),
        sa.Column('external_id', sa.String(100), nullable=False, comment='外部流水号'),
        sa.Column('transaction_id', sa.String(100), nullable=False, comment='交易流水号'),
        sa.Column('parent_transaction_id', sa.String(100), nullable=True, comment='父交易流水号'),
        sa.Column('product', sa.String(50), nullable=False, comment='产品'),
        sa.Column('account', sa.String(100), nullable=False, comment='账户'),
        sa.Column('event_type', sa.String(50), nullable=False, comment='事件类型'),
        sa.Column('transaction_status', sa.String(20), nullable=False, comment='交易状态'),
        sa.Column('entry_date', sa.DateTime(), nullable=False, comment='录入日'),
        sa.Column('trade_date', sa.DateTime(), nullable=False, comment='交易日'),
        sa.Column('modified_date', sa.DateTime(), nullable=False, comment='修改日'),
        sa.Column('back_office_status', sa.String(50), nullable=False, comment='后线处理状态'),
        sa.Column('confirmation_status', sa.String(50), nullable=True, comment='证实状态'),
        sa.Column('confirmation_match_status', sa.String(50), nullable=True, comment='证实匹配状态'),
        sa.Column('operator', sa.String(100), nullable=False, comment='操作用户'),
        sa.ForeignKeyConstraint(['external_id'], ['transactions.external_id']),
    )
    
    # Create indexes for events
    op.create_index('idx_event_external_id', 'events', ['external_id'])
    op.create_index('idx_event_transaction_id', 'events', ['transaction_id'])
    op.create_index('idx_event_parent_transaction_id', 'events', ['parent_transaction_id'])
    op.create_index('idx_event_type', 'events', ['event_type'])
    op.create_index('idx_modified_date', 'events', ['modified_date'])
    op.create_index('idx_external_id_modified_date', 'events', ['external_id', 'modified_date'])
    op.create_index('idx_transaction_id_event_type', 'events', ['transaction_id', 'event_type'])
    
    # Create accounting_records table
    op.create_table(
        'accounting_records',
        sa.Column('voucher_id', sa.String(100), primary_key=True, comment='传票号'),
        sa.Column('transaction_id', sa.String(100), nullable=False, comment='交易流水号'),
        sa.Column('actual_accounting_date', sa.DateTime(), nullable=False, comment='实际记账日'),
        sa.Column('planned_accounting_date', sa.DateTime(), nullable=False, comment='计划记账日'),
        sa.Column('event_number', sa.String(100), nullable=False, comment='事件号'),
        sa.Column('debit_credit_indicator', sa.String(20), nullable=False, comment='借贷方向'),
        sa.Column('currency', sa.String(3), nullable=False, comment='货币'),
        sa.Column('account_subject', sa.String(100), nullable=False, comment='科目'),
        sa.Column('transaction_amount', sa.Float(), nullable=False, comment='交易金额'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id']),
    )
    
    # Create indexes for accounting_records
    op.create_index('idx_accounting_transaction_id', 'accounting_records', ['transaction_id'])
    op.create_index('idx_actual_accounting_date', 'accounting_records', ['actual_accounting_date'])
    op.create_index('idx_currency', 'accounting_records', ['currency'])
    op.create_index('idx_transaction_id_accounting_date', 'accounting_records', ['transaction_id', 'actual_accounting_date'])
    op.create_index('idx_currency_debit_credit', 'accounting_records', ['currency', 'debit_credit_indicator'])
    
    # Create cash_flows table
    op.create_table(
        'cash_flows',
        sa.Column('cash_flow_id', sa.String(100), primary_key=True, comment='现金流内部ID'),
        sa.Column('transaction_id', sa.String(100), nullable=False, comment='交易流水号'),
        sa.Column('payment_info_id', sa.String(100), nullable=True, comment='收付信息ID'),
        sa.Column('settlement_id', sa.String(100), nullable=True, comment='结算内部ID'),
        sa.Column('direction', sa.String(20), nullable=False, comment='方向'),
        sa.Column('currency', sa.String(3), nullable=False, comment='币种'),
        sa.Column('amount', sa.Float(), nullable=False, comment='金额'),
        sa.Column('payment_date', sa.DateTime(), nullable=False, comment='收付日期'),
        sa.Column('account_number', sa.String(100), nullable=False, comment='账号'),
        sa.Column('account_name', sa.String(200), nullable=False, comment='户名'),
        sa.Column('bank_name', sa.String(200), nullable=False, comment='开户行'),
        sa.Column('bank_code', sa.String(50), nullable=False, comment='开户行号'),
        sa.Column('settlement_method', sa.String(50), nullable=False, comment='结算方式'),
        sa.Column('current_status', sa.String(50), nullable=False, comment='当前状态'),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0', comment='进度百分比'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1', comment='版本号'),
        sa.Column('last_modified_date', sa.DateTime(), nullable=False, comment='最后修改日期'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id']),
    )
    
    # Create indexes for cash_flows
    op.create_index('idx_cashflow_transaction_id', 'cash_flows', ['transaction_id'])
    op.create_index('idx_payment_info_id', 'cash_flows', ['payment_info_id'])
    op.create_index('idx_settlement_id', 'cash_flows', ['settlement_id'])
    op.create_index('idx_cashflow_direction', 'cash_flows', ['direction'])
    op.create_index('idx_cashflow_currency', 'cash_flows', ['currency'])
    op.create_index('idx_payment_date', 'cash_flows', ['payment_date'])
    op.create_index('idx_cashflow_settlement_method', 'cash_flows', ['settlement_method'])
    op.create_index('idx_current_status', 'cash_flows', ['current_status'])
    op.create_index('idx_transaction_id_direction', 'cash_flows', ['transaction_id', 'direction'])
    op.create_index('idx_payment_date_status', 'cash_flows', ['payment_date', 'current_status'])
    op.create_index('idx_currency_direction', 'cash_flows', ['currency', 'direction'])


def downgrade() -> None:
    op.drop_table('cash_flows')
    op.drop_table('accounting_records')
    op.drop_table('events')
    op.drop_table('transactions')
