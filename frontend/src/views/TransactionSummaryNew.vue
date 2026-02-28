<template>
  <div class="rcs-container">
    <!-- Top Navigation Bar -->
    <div class="top-nav">
      <div class="nav-left">
        <div class="logo">
          <span class="logo-text">RCS 5.0</span>
        </div>
        <nav class="nav-menu">
          <a href="#" class="nav-item">后线工作台</a>
          <a href="#" class="nav-item active">查询统计</a>
          <a href="#" class="nav-item">规则管理</a>
          <a href="#" class="nav-item">基础数据</a>
        </nav>
      </div>
      <div class="nav-right">
        <span class="user-info">wang_lp</span>
      </div>
    </div>

    <!-- Main Layout with Sidebar -->
    <div class="main-layout">
      <!-- Left Sidebar -->
      <div class="sidebar">
        <div class="sidebar-menu">
          <div class="menu-item active">
            <span>操作指导</span>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="content-area">

        <!-- Query Section -->
        <div class="query-section">
          <div class="query-row">
            <div class="query-field">
              <label>外部流水号</label>
              <input v-model="query.externalId" type="text" placeholder="请输入" />
            </div>
            <div class="query-field">
              <label>交易状态</label>
              <select v-model="query.status">
                <option value="">全部</option>
                <option value="生效">生效</option>
                <option value="到期">到期</option>
                <option value="失效">失效</option>
              </select>
            </div>
            <div class="query-field">
              <label>交易日</label>
              <input v-model="query.tradeDateFrom" type="date" />
              <span class="separator">~</span>
              <input v-model="query.tradeDateTo" type="date" />
            </div>
            <div class="query-field">
              <label>起息日</label>
              <input v-model="query.valueDateFrom" type="date" />
              <span class="separator">~</span>
              <input v-model="query.valueDateTo" type="date" />
            </div>
            <div class="query-field">
              <label>产品</label>
              <select v-model="query.product">
                <option value="">全部</option>
                <option value="外汇即期">外汇即期</option>
                <option value="外汇远期">外汇远期</option>
                <option value="外汇掉期">外汇掉期</option>
                <option value="同业拆借">同业拆借</option>
                <option value="货币市场存款">货币市场存款</option>
                <option value="现券买卖">现券买卖</option>
                <option value="买断式回购">买断式回购</option>
                <option value="质押式回购">质押式回购</option>
                <option value="单边现金流">单边现金流</option>
              </select>
            </div>
            
            <!-- 可折叠的高级查询条件 -->
            <div v-show="showAdvanced" class="query-field">
              <label>到期日</label>
              <input v-model="query.maturityDateFrom" type="date" />
              <span class="separator">~</span>
              <input v-model="query.maturityDateTo" type="date" />
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>交易对手</label>
              <input v-model="query.counterparty" type="text" placeholder="请输入" />
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>货币</label>
              <input v-model="query.currency" type="text" placeholder="如CNY、USD" />
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>运营机构</label>
              <select v-model="query.operatingInstitution">
                <option value="">全部</option>
                <option value="1530H">1530H_中国银行(香港)有限公司</option>
                <option value="052">052_中国银行（香港）有限公司文莱分行</option>
                <option value="053">053_中国银行（香港）有限公司仰光分行</option>
              </select>
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>清算方式</label>
              <select v-model="query.settlementMethod">
                <option value="">全部</option>
                <option value="全额">全额</option>
                <option value="净额">净额</option>
                <option value="集中">集中</option>
                <option value="无需">无需</option>
                <option value="我行代理">我行代理</option>
                <option value="他行代理">他行代理</option>
              </select>
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>证实方式</label>
              <select v-model="query.confirmationType">
                <option value="">全部</option>
                <option value="SWIFT">SWIFT</option>
                <option value="文本">文本</option>
                <option value="无证实">无证实</option>
              </select>
            </div>
            <div v-show="showAdvanced" class="query-field">
              <label>交易来源</label>
              <select v-model="query.source">
                <option value="">全部</option>
                <option value="GIT">GIT</option>
                <option value="FXO">FXO</option>
                <option value="FXS">FXS</option>
                <option value="FXY">FXY</option>
                <option value="FXW">FXW</option>
              </select>
            </div>
            
            <div class="query-actions">
              <button class="btn-toggle" @click="toggleAdvanced">
                {{ showAdvanced ? '收起' : '展开' }}
              </button>
              <button class="btn-reset" @click="handleReset">重置</button>
              <button class="btn-query" @click="handleQuery">查询</button>
              <button class="btn-export" @click="handleExport">导出</button>
            </div>
          </div>
        </div>

        <!-- Data Table -->
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>外部流水号</th>
                <th>交易流水号</th>
                <th>录入日</th>
                <th>交易日</th>
                <th>起息日</th>
                <th>到期日</th>
                <th>账户</th>
                <th>产品</th>
                <th>买卖方向</th>
                <th>标的物</th>
                <th>交易对手</th>
                <th>交易状态</th>
                <th>后线处理状态</th>
                <th>清算方式</th>
                <th>证实方式</th>
                <th>运营机构</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in transactions" :key="index" 
                  @click="handleRowClick(item)">
                <td class="text-blue">{{ item.external_id }}</td>
                <td>{{ item.transaction_id }}</td>
                <td>{{ item.entry_date }}</td>
                <td>{{ item.trade_date }}</td>
                <td>{{ item.value_date }}</td>
                <td>{{ item.maturity_date }}</td>
                <td>{{ item.account }}</td>
                <td>{{ item.product }}</td>
                <td :class="item.direction === '买入' ? 'text-green' : 'text-red'">{{ item.direction }}</td>
                <td>{{ item.underlying }}</td>
                <td>{{ item.counterparty }}</td>
                <td><span :class="'status-' + getStatusClass(item.status)">{{ item.status }}</span></td>
                <td class="text-orange">{{ item.back_office_status }}</td>
                <td>{{ item.settlement_method }}</td>
                <td>{{ item.confirmation_type }}</td>
                <td>{{ item.operating_institution }}</td>
                <td>
                  <button class="btn-detail" @click.stop="viewDetail(item)">详情</button>
                </td>
              </tr>
              <tr v-if="transactions.length === 0 && !loading">
                <td colspan="17" class="no-data">未找到符合条件的交易记录</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Detail Modal -->
        <div v-if="showDetailModal" class="modal-overlay" @click="closeModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>交易详情 - {{ selectedTransaction?.external_id }}</h3>
              <button class="btn-close" @click="closeModal">×</button>
            </div>
            
            <!-- 操作指引区域 -->
            <div class="operation-guide">
              <div class="guide-status">
                <span class="status-icon">ℹ️</span>
                <div class="status-info">
                  <div class="status-title">当前状态：</div>
                  <div class="status-content">
                    <span class="status-value">{{ currentStatus }}</span>
                    <div class="status-desc">{{ currentStatusDesc }}</div>
                  </div>
                </div>
              </div>
              <div class="guide-action">
                <div class="action-title">下一步操作：</div>
                <div class="action-desc">{{ nextAction }}</div>
              </div>
            </div>
            
            <div class="modal-tabs">
              <button 
                v-for="tab in tabs" 
                :key="tab.id"
                :class="['tab-item', { active: activeTab === tab.id }]"
                @click="activeTab = tab.id"
              >
                {{ tab.label }}
              </button>
            </div>
            <div class="modal-body">
              <!-- 标签页1: 交易信息 -->
              <div v-if="activeTab === 'transaction'" class="tab-content">
                <!-- 交易信息 -->
                <div class="detail-section">
                  <h4 class="section-title">交易信息</h4>
                  <div class="transaction-info-grid">
                    <div class="info-row">
                      <label>货币对</label>
                      <span>{{ selectedTransaction?.underlying }}</span>
                    </div>
                    <div class="info-row amount-row">
                      <label>金额(USD/CNY)</label>
                      <div class="amount-group">
                        <span class="amount-label buy">BUY ⇄</span>
                        <span class="amount-value">{{ selectedTransaction?.buy_amount }}</span>
                        <span class="amount-label sell">SELL ⇄</span>
                        <span class="amount-value-sell">{{ selectedTransaction?.sell_amount }}</span>
                      </div>
                    </div>
                    <div class="info-row">
                      <label>即期汇率/点差/成本汇率</label>
                      <span>{{ selectedTransaction?.spot_rate }} / {{ selectedTransaction?.points }} / {{ selectedTransaction?.cost_rate }}</span>
                    </div>
                    <div class="info-row">
                      <label>分润金额</label>
                      <span>{{ selectedTransaction?.profit_amount }}</span>
                      <label style="margin-left: 40px;">分润币种</label>
                      <span>{{ selectedTransaction?.profit_currency }}</span>
                    </div>
                    <div class="info-row">
                      <label>交易日</label>
                      <span>{{ selectedTransaction?.trade_date }}</span>
                      <label style="margin-left: 40px;">交易时间</label>
                      <span>{{ selectedTransaction?.trade_time }}</span>
                    </div>
                    <div class="info-row">
                      <label>起息日</label>
                      <span>{{ selectedTransaction?.value_date }}</span>
                    </div>
                  </div>
                </div>

                <!-- 交易账户 -->
                <div class="detail-section">
                  <h4 class="section-title">交易账户</h4>
                  <div class="detail-grid-2col">
                    <div class="detail-row">
                      <label>账户</label>
                      <span>{{ selectedTransaction?.account }}</span>
                      <span style="margin-left: 40px;">{{ selectedTransaction?.account_cny }}</span>
                    </div>
                    <div class="detail-row">
                      <label>交易对手</label>
                      <span class="text-orange">{{ selectedTransaction?.counterparty }}</span>
                      <span style="margin-left: 20px;">{{ selectedTransaction?.counterparty_name }}</span>
                    </div>
                    <div class="detail-row">
                      <label>经纪商</label>
                      <span>{{ selectedTransaction?.broker || '-' }}</span>
                    </div>
                    <div class="detail-row">
                      <label>背对背账户</label>
                      <span>{{ selectedTransaction?.back_to_back || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- 备注 -->
                <div class="detail-section">
                  <h4 class="section-title">备注</h4>
                  <div class="detail-grid-2col">
                    <div class="detail-row">
                      <label>交易性质</label>
                      <span>{{ selectedTransaction?.trade_nature || '-' }}</span>
                    </div>
                    <div class="detail-row">
                      <label>外部流水号</label>
                      <span class="text-blue">{{ selectedTransaction?.external_id }}</span>
                      <span class="badge-rcs">RCS</span>
                    </div>
                    <div class="detail-row">
                      <label>交易目的</label>
                      <span>{{ selectedTransaction?.trade_purpose || '-' }}</span>
                    </div>
                    <div class="detail-row">
                      <label>备注</label>
                      <span>{{ selectedTransaction?.remark || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- 拆展字段 -->
                <div class="detail-section">
                  <h4 class="section-title">拆展字段</h4>
                  <div class="detail-grid-1col">
                    <div class="detail-row">
                      <label>我方收结算路径(USD)</label>
                      <span>{{ selectedTransaction?.our_settlement_path_usd }}</span>
                    </div>
                    <div class="detail-row">
                      <label>对手方付结算路径(USD)</label>
                      <span>{{ selectedTransaction?.counterparty_settlement_path_usd }}</span>
                    </div>
                    <div class="detail-row">
                      <label>我方付结算路径(CNY)</label>
                      <span>{{ selectedTransaction?.our_settlement_path_cny }}</span>
                    </div>
                    <div class="detail-row">
                      <label>对手方收结算路径(CNY)</label>
                      <span>{{ selectedTransaction?.counterparty_settlement_path_cny }}</span>
                    </div>
                    <div class="detail-row">
                      <label>清算方式</label>
                      <span>{{ selectedTransaction?.settlement_method }}</span>
                    </div>
                  </div>
                </div>

                <!-- 拆分信息 -->
                <div class="detail-section">
                  <h4 class="section-title">拆分信息</h4>
                  <div class="detail-row">
                    <label>交易拆分</label>
                    <label class="checkbox-label">
                      <input type="checkbox" :checked="selectedTransaction?.split_currency" disabled />
                      拆分货币对
                    </label>
                  </div>
                </div>

                <!-- 交易生命周期进度跟踪 -->
                <div class="lifecycle-progress-section">
                  <TransactionLifecycleProgress 
                    :transaction-id="selectedTransaction?.transaction_id"
                    :product-type="selectedTransaction?.product"
                    :stage-statuses="lifecycleStageStatuses"
                    :rmc-status="rmcStatus"
                    :ftm-status="ftmStatus"
                    :timestamps="lifecycleTimestamps"
                  />
                </div>
              </div>

              <!-- 标签页2: 事件信息 -->
              <div v-if="activeTab === 'events'" class="tab-content">
                <div class="event-table-container">
                  <table class="detail-table">
                    <thead>
                      <tr>
                        <th>外部流水号</th>
                        <th>交易流水号</th>
                        <th>父交易流水号</th>
                        <th>产品</th>
                        <th>账户</th>
                        <th>事件类型</th>
                        <th>交易状态</th>
                        <th>录入日</th>
                        <th>交易日</th>
                        <th>修改日</th>
                        <th>后线处理状态</th>
                        <th>证实状态</th>
                        <th>证实匹配状态</th>
                        <th>操作用户</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(event, index) in mockEventData" :key="index">
                        <td class="text-blue">{{ event.external_id }}</td>
                        <td>{{ event.transaction_id }}</td>
                        <td>{{ event.parent_transaction_id || '-' }}</td>
                        <td>{{ event.product }}</td>
                        <td>{{ event.account }}</td>
                        <td>{{ event.event_type }}</td>
                        <td><span :class="'status-' + getStatusClass(event.status)">{{ event.status }}</span></td>
                        <td>{{ event.entry_date }}</td>
                        <td>{{ event.trade_date }}</td>
                        <td>{{ event.modified_date }}</td>
                        <td class="text-orange">{{ event.back_office_status }}</td>
                        <td>{{ event.confirmation_status || '-' }}</td>
                        <td>{{ event.confirmation_match_status || '-' }}</td>
                        <td>{{ event.operator }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="pagination-info">
                  <span>显示1到{{ mockEventData.length }}，共{{ mockEventData.length }}记录</span>
                </div>
              </div>

              <!-- 标签页3: 现金流信息 -->
              <div v-if="activeTab === 'cashflow'" class="tab-content">
                <div class="event-table-container">
                  <table class="detail-table">
                    <thead>
                      <tr>
                        <th>序号</th>
                        <th>现金流内部ID</th>
                        <th>我方结算路径</th>
                        <th>对手方结算路径</th>
                        <th>结算渠道</th>
                        <th>交割模式</th>
                        <th>收付类型</th>
                        <th>支付日</th>
                        <th>计划轧差日</th>
                        <th>轧差规则</th>
                        <th>轧差状态</th>
                        <th>收付状态</th>
                        <th>货币</th>
                        <th>金额</th>
                        <th>清算方式</th>
                        <th>现金流类型</th>
                        <th>收付方向</th>
                        <th>计息开始日</th>
                        <th>计息结束日</th>
                        <th>阶段</th>
                        <th>计息基础</th>
                        <th>LEG</th>
                        <th>现金流号</th>
                        <th>产品</th>
                        <th>外部流水号</th>
                        <th>交易流水号</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(cashflow, index) in mockCashflowData" :key="index">
                        <td>{{ cashflow.seq }}</td>
                        <td class="text-blue">{{ cashflow.cashflow_internal_id }}</td>
                        <td>{{ cashflow.our_settlement_path }}</td>
                        <td>{{ cashflow.counterparty_settlement_path }}</td>
                        <td>{{ cashflow.settlement_channel }}</td>
                        <td>{{ cashflow.delivery_mode }}</td>
                        <td>{{ cashflow.payment_type }}</td>
                        <td>{{ cashflow.payment_date }}</td>
                        <td>{{ cashflow.planned_netting_date }}</td>
                        <td>{{ cashflow.netting_rule }}</td>
                        <td>{{ cashflow.netting_status }}</td>
                        <td class="text-orange">{{ cashflow.payment_status }}</td>
                        <td>{{ cashflow.currency }}</td>
                        <td class="text-right">{{ cashflow.amount }}</td>
                        <td>{{ cashflow.settlement_method }}</td>
                        <td>{{ cashflow.cashflow_type }}</td>
                        <td :class="cashflow.payment_direction === '收入' ? 'text-green' : 'text-red'">{{ cashflow.payment_direction }}</td>
                        <td>{{ cashflow.interest_start_date }}</td>
                        <td>{{ cashflow.interest_end_date }}</td>
                        <td>{{ cashflow.stage }}</td>
                        <td>{{ cashflow.interest_basis }}</td>
                        <td>{{ cashflow.leg }}</td>
                        <td>{{ cashflow.cashflow_number }}</td>
                        <td>{{ cashflow.product }}</td>
                        <td class="text-blue">{{ cashflow.external_id }}</td>
                        <td>{{ cashflow.transaction_id }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="pagination-info">
                  <span>显示1到{{ mockCashflowData.length }}，共{{ mockCashflowData.length }}记录</span>
                </div>
                
                <!-- 结算支付进度跟踪流程图 -->
                <div class="settlement-progress-section">
                  <SettlementPaymentProgress 
                    :current-stage="currentSettlementStage"
                    :stage-statuses="settlementStageStatuses"
                  />
                </div>
              </div>

              <!-- 标签页4: 账务信息 -->
              <div v-if="activeTab === 'accounting'" class="tab-content">
                <h4 class="section-title">账务记录</h4>
                <div class="event-table-container">
                  <table class="detail-table">
                    <thead>
                      <tr>
                        <th>传票号</th>
                        <th>实际记账日</th>
                        <th>计划记账日</th>
                        <th>事件号</th>
                        <th>借贷方向</th>
                        <th>货币</th>
                        <th>科目</th>
                        <th>交易金额</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>V{{ selectedTransaction?.transaction_id?.slice(-6) }}</td>
                        <td>{{ selectedTransaction?.entry_date }}</td>
                        <td>{{ selectedTransaction?.value_date }}</td>
                        <td>{{ selectedTransaction?.transaction_id }}</td>
                        <td>借</td>
                        <td>{{ selectedTransaction?.underlying?.split('/')[0] }}</td>
                        <td>1001-现金</td>
                        <td class="text-right">1,000,000.00</td>
                      </tr>
                      <tr>
                        <td>V{{ selectedTransaction?.transaction_id?.slice(-6) }}</td>
                        <td>{{ selectedTransaction?.entry_date }}</td>
                        <td>{{ selectedTransaction?.value_date }}</td>
                        <td>{{ selectedTransaction?.transaction_id }}</td>
                        <td>贷</td>
                        <td>{{ selectedTransaction?.underlying?.split('/')[1] }}</td>
                        <td>2001-应付款</td>
                        <td class="text-right">6,500,000.00</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="info-text">显示1到2，共2记录</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination-bar">
          <div class="pagination-left">
            <span>共 {{ totalRecords }} 条</span>
          </div>
          <div class="pagination-center">
            <button @click="goToPage(1)" :class="{ active: currentPage === 1 }">1</button>
            <button @click="goToPage(2)" :class="{ active: currentPage === 2 }">2</button>
            <button @click="goToPage(3)" :class="{ active: currentPage === 3 }">3</button>
            <button @click="goToPage(4)" :class="{ active: currentPage === 4 }">4</button>
            <button @click="goToPage(5)" :class="{ active: currentPage === 5 }">5</button>
            <button @click="goToPage(6)" :class="{ active: currentPage === 6 }">6</button>
            <span class="page-dots">...</span>
            <button @click="goToPage(totalPages)">{{ totalPages }}</button>
          </div>
          <div class="pagination-right">
            <select v-model="pageSize" @change="handlePageSizeChange">
              <option :value="20">20条/页</option>
              <option :value="50">50条/页</option>
              <option :value="100">100条/页</option>
            </select>
            <span class="page-jump">
              转到
              <input v-model.number="jumpPage" type="number" min="1" :max="totalPages" />
              页
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ProgressStepper from '@/components/ProgressStepper.vue'
import SettlementPaymentProgress from '@/components/SettlementPaymentProgress.vue'
import TransactionLifecycleProgress from '@/components/TransactionLifecycleProgress.vue'
import apiClient from '@/api/client'

const router = useRouter()

// Modal state
const showDetailModal = ref(false)
const selectedTransaction = ref(null)
const activeTab = ref('function2')
const tabs = [
  { id: 'transaction', label: '交易信息' },
  { id: 'events', label: '事件信息' },
  { id: 'cashflow', label: '现金流信息' },
  { id: 'accounting', label: '账务信息' }
]

// Advanced query toggle
const showAdvanced = ref(false)

const toggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}

// Query parameters
const query = ref({
  externalId: '',
  status: '',
  tradeDateFrom: '2026-01-01',
  tradeDateTo: '2026-02-28',
  valueDateFrom: '2026-01-01',
  valueDateTo: '2026-03-31',
  maturityDateFrom: '',
  maturityDateTo: '',
  counterparty: '',
  product: '',
  currency: '',
  operatingInstitution: '',
  settlementMethod: '',
  confirmationType: '',
  source: ''
})

// Table data
const transactions = ref([])
const loading = ref(false)
const currentPage = ref(1)

// Progress tracking
const cashflowProgressSteps = ref([])
const lifecycleStages = ref([
  {
    name: '交易点',
    description: '交易录入',
    status: 'completed',
    time: '2026-02-16 17:13'
  },
  {
    name: '证实点',
    description: '交易证实',
    status: 'completed',
    time: '2026-02-16 18:20'
  },
  {
    name: '收付点',
    description: '收付结算',
    status: 'current',
    time: ''
  },
  {
    name: '账务点',
    description: '账务处理',
    status: 'pending',
    time: ''
  }
])

// Settlement payment progress tracking
const currentSettlementStage = ref('netting')
const settlementStageStatuses = ref({
  netting: 'completed',
  compliance: 'completed',
  routing: 'current',
  swift: 'pending',
  accounting: 'pending',
  completed: 'pending'
})

// Transaction lifecycle progress tracking
const lifecycleStageStatuses = ref({
  review: 'approved',      // 后台复核已通过
  swift: 'processing',     // SWIFT证实处理中
  matching: 'pending'      // 证实匹配待处理
})
const rmcStatus = ref('success')  // RMC成功
const ftmStatus = ref('processing')  // FTM处理中
const lifecycleTimestamps = ref({
  review: '2026-02-16T17:13:00',
  rmc: '2026-02-16T18:15:00',
  ftm: null,
  matching: null
})

// Load cash flow progress when a transaction is selected and cashflow tab is active
watch([selectedTransaction, activeTab], async ([transaction, tab]) => {
  if (transaction && tab === 'cashflow' && mockCashflowData.length > 0) {
    await loadCashflowProgress(mockCashflowData[0].cashflow_internal_id)
  }
})

const loadCashflowProgress = async (cashFlowId) => {
  if (!cashFlowId) return
  
  try {
    const response = await apiClient.get(`/cash-flows/${cashFlowId}/progress`)
    const flowData = response?.flowVisualization || response?.flow_visualization
    if (flowData) {
      cashflowProgressSteps.value = flowData.map(node => ({
        label: node.name,
        status: node.status.toLowerCase()
      }))
    }
  } catch (err) {
    console.error('Load cash flow progress error:', err)
    // Silently fail - progress is optional
    cashflowProgressSteps.value = []
  }
}
const pageSize = ref(20)
const totalPages = ref(1)
const totalRecords = ref(15)
const jumpPage = ref(1)

// Mock data - 15条真实数据
const mockData = [
  {
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001',
    entry_date: '2026-02-16',
    trade_date: '2026-02-15',
    trade_time: '17:13',
    value_date: '2026-02-25',
    maturity_date: '2026-05-18',
    account: 'WxxTest7_FXX_USD',
    account_cny: 'WxxTest7_FXX_美元',
    product: '外汇即期',
    direction: '买入',
    underlying: 'USDCNY',
    buy_amount: '2,000,000.00',
    buy_currency: 'USD',
    sell_amount: '13,820,000.00',
    sell_currency: 'CNY',
    spot_rate: '6.910000',
    points: '0.00',
    cost_rate: '6.910000',
    profit_amount: '0.00',
    profit_currency: 'CNY',
    counterparty: '10201',
    counterparty_name: 'SH上海银行股份有限公司',
    broker: '-',
    back_to_back: '-',
    trade_nature: '同业交易',
    trade_purpose: '-',
    remark: '-',
    our_settlement_path_usd: 'BANKZB_HOME_USD',
    counterparty_settlement_path_usd: 'BANKZB_CPTY_10201',
    our_settlement_path_cny: 'BANKZB_HOME_CNY',
    counterparty_settlement_path_cny: 'BANKZB_CPTY_10201_CNY',
    status: '生效',
    back_office_status: '待发报',
    settlement_method: '集中清算结算',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司',
    split_currency: false
  },
  {
    external_id: 'FX202602160002',
    transaction_id: 'TXN20260216002',
    entry_date: '2026-02-16',
    trade_date: '2026-02-16',
    value_date: '2026-02-18',
    maturity_date: '2026-08-18',
    account: 'ACC1530H002',
    product: '外汇远期',
    direction: '卖出',
    underlying: 'EUR/USD',
    counterparty: '中国建设银行',
    status: '生效',
    back_office_status: '待回执',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602150001',
    transaction_id: 'TXN20260215001',
    entry_date: '2026-02-15',
    trade_date: '2026-02-15',
    value_date: '2026-02-17',
    maturity_date: '2026-02-17',
    account: 'ACC052001',
    product: '外汇即期',
    direction: '买入',
    underlying: 'USD/CNY',
    counterparty: '中国农业银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '全额',
    confirmation_type: 'SWIFT',
    operating_institution: '052_中国银行（香港）有限公司文莱分行'
  },
  {
    external_id: 'FX202602150002',
    transaction_id: 'TXN20260215002',
    entry_date: '2026-02-15',
    trade_date: '2026-02-15',
    value_date: '2026-02-19',
    maturity_date: '2026-06-19',
    account: 'ACC1530H003',
    product: '外汇掉期',
    direction: '买入',
    underlying: 'GBP/USD',
    counterparty: '汇丰银行',
    status: '生效',
    back_office_status: '待结算',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602140001',
    transaction_id: 'TXN20260214001',
    entry_date: '2026-02-14',
    trade_date: '2026-02-14',
    value_date: '2026-02-16',
    maturity_date: '2026-02-16',
    account: 'ACC053001',
    product: '外汇即期',
    direction: '卖出',
    underlying: 'JPY/USD',
    counterparty: '渣打银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '净额',
    confirmation_type: 'SWIFT',
    operating_institution: '053_中国银行（香港）有限公司仰光分行'
  },
  {
    external_id: 'FX202602140002',
    transaction_id: 'TXN20260214002',
    entry_date: '2026-02-14',
    trade_date: '2026-02-14',
    value_date: '2026-02-18',
    maturity_date: '2026-07-18',
    account: 'ACC1530H004',
    product: '外汇远期',
    direction: '买入',
    underlying: 'AUD/USD',
    counterparty: '花旗银行',
    status: '生效',
    back_office_status: '复核中',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602130001',
    transaction_id: 'TXN20260213001',
    entry_date: '2026-02-13',
    trade_date: '2026-02-13',
    value_date: '2026-02-15',
    maturity_date: '2026-02-15',
    account: 'ACC1530H005',
    product: '外汇即期',
    direction: '卖出',
    underlying: 'USD/HKD',
    counterparty: '东亚银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '内部账',
    confirmation_type: '无证实',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602130002',
    transaction_id: 'TXN20260213002',
    entry_date: '2026-02-13',
    trade_date: '2026-02-13',
    value_date: '2026-02-17',
    maturity_date: '2026-09-17',
    account: 'ACC1530H006',
    product: '外汇远期',
    direction: '买入',
    underlying: 'CAD/USD',
    counterparty: '中国银行总行',
    status: '生效',
    back_office_status: '待证实',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602120001',
    transaction_id: 'TXN20260212001',
    entry_date: '2026-02-12',
    trade_date: '2026-02-12',
    value_date: '2026-02-14',
    maturity_date: '2026-02-14',
    account: 'ACC052002',
    product: '外汇即期',
    direction: '买入',
    underlying: 'EUR/CNY',
    counterparty: '交通银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '全额',
    confirmation_type: 'SWIFT',
    operating_institution: '052_中国银行（香港）有限公司文莱分行'
  },
  {
    external_id: 'FX202602120002',
    transaction_id: 'TXN20260212002',
    entry_date: '2026-02-12',
    trade_date: '2026-02-12',
    value_date: '2026-02-16',
    maturity_date: '2026-05-16',
    account: 'ACC1530H007',
    product: '外汇掉期',
    direction: '卖出',
    underlying: 'CHF/USD',
    counterparty: '瑞银集团',
    status: '生效',
    back_office_status: '复核通过',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602110001',
    transaction_id: 'TXN20260211001',
    entry_date: '2026-02-11',
    trade_date: '2026-02-11',
    value_date: '2026-02-13',
    maturity_date: '2026-02-13',
    account: 'ACC1530H008',
    product: '外汇即期',
    direction: '买入',
    underlying: 'NZD/USD',
    counterparty: '恒生银行',
    status: '失效',
    back_office_status: '已取消',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602110002',
    transaction_id: 'TXN20260211002',
    entry_date: '2026-02-11',
    trade_date: '2026-02-11',
    value_date: '2026-02-15',
    maturity_date: '2026-08-15',
    account: 'ACC053002',
    product: '外汇远期',
    direction: '卖出',
    underlying: 'SGD/USD',
    counterparty: '星展银行',
    status: '生效',
    back_office_status: '待发报',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '053_中国银行（香港）有限公司仰光分行'
  },
  {
    external_id: 'FX202602100001',
    transaction_id: 'TXN20260210001',
    entry_date: '2026-02-10',
    trade_date: '2026-02-10',
    value_date: '2026-02-12',
    maturity_date: '2026-02-12',
    account: 'ACC1530H009',
    product: '外汇即期',
    direction: '买入',
    underlying: 'USD/CNY',
    counterparty: '招商银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '集中',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602100002',
    transaction_id: 'TXN20260210002',
    entry_date: '2026-02-10',
    trade_date: '2026-02-10',
    value_date: '2026-02-14',
    maturity_date: '2026-06-14',
    account: 'ACC1530H010',
    product: '外汇掉期',
    direction: '卖出',
    underlying: 'USD/JPY',
    counterparty: '三菱日联银行',
    status: '生效',
    back_office_status: '待结算',
    settlement_method: 'SWIFT',
    confirmation_type: 'SWIFT',
    operating_institution: '1530H_中国银行(香港)有限公司'
  },
  {
    external_id: 'FX202602090001',
    transaction_id: 'TXN20260209001',
    entry_date: '2026-02-09',
    trade_date: '2026-02-09',
    value_date: '2026-02-11',
    maturity_date: '2026-02-11',
    account: 'ACC052003',
    product: '外汇即期',
    direction: '买入',
    underlying: 'GBP/CNY',
    counterparty: '中信银行',
    status: '到期',
    back_office_status: '已完成',
    settlement_method: '全额',
    confirmation_type: '文本',
    operating_institution: '052_中国银行（香港）有限公司文莱分行'
  }
]

onMounted(() => {
  loadData()
})

const loadData = () => {
  transactions.value = mockData
  totalRecords.value = mockData.length
  totalPages.value = Math.ceil(mockData.length / pageSize.value)
}

const handleQuery = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  query.value = {
    externalId: '',
    status: '',
    tradeDateFrom: '',
    tradeDateTo: '',
    valueDateFrom: '',
    valueDateTo: '',
    maturityDateFrom: '',
    maturityDateTo: '',
    counterparty: '',
    product: '',
    currency: '',
    operatingInstitution: '',
    settlementMethod: '',
    confirmationType: '',
    source: ''
  }
  loadData()
}

const handleExport = () => {
  alert('导出功能')
}

const handleRowClick = (item) => {
  viewDetail(item)
}

const viewDetail = (item) => {
  selectedTransaction.value = item
  activeTab.value = 'transaction'
  showDetailModal.value = true
}

const closeModal = () => {
  showDetailModal.value = false
  selectedTransaction.value = null
}

// Operation guide data
const currentStatus = ref('复核中')
const currentStatusDesc = ref('交易已同步至后线，等待结算员核对交易要素与清算路径')
const nextAction = ref('请在"后线工作台 - 交易复核"中确认并进行审批')
const actionButtons = ref([
  { label: '查看证实详情', action: 'view-confirmation' },
  { label: '查看进度', action: 'view-progress' }
])

const handleActionClick = (action) => {
  console.log('Action clicked:', action)
  // 这里可以根据不同的action执行不同的操作
  if (action === 'view-confirmation') {
    alert('查看证实详情功能')
  } else if (action === 'view-progress') {
    alert('查看进度功能')
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadData()
  }
}

const jumpToPage = () => {
  if (jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
    currentPage.value = jumpPage.value
    loadData()
  }
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  totalPages.value = Math.ceil(totalRecords.value / pageSize.value)
  loadData()
}

const getStatusClass = (status) => {
  const statusMap = {
    '生效': 'active',
    '到期': 'expired',
    '失效': 'invalid'
  }
  return statusMap[status] || 'default'
}

const getStageClass = (stage) => {
  return {
    'stage-completed': stage.status === 'completed',
    'stage-current': stage.status === 'current',
    'stage-pending': stage.status === 'pending',
    'stage-failed': stage.status === 'failed'
  }
}

const getConnectorClass = (index) => {
  if (index === 0) return ''
  const prevStage = lifecycleStages.value[index - 1]
  if (prevStage.status === 'completed') {
    return 'connector-active'
  }
  return 'connector-inactive'
}

const getNodeIconClass = (nodeType) => {
  // 根据节点类型返回对应的状态类
  // 这里可以根据实际数据动态判断
  const statusMap = {
    'review': 'node-completed',
    'swift': 'node-current',
    'matching': 'node-pending',
    'payment': 'node-pending'
  }
  return statusMap[nodeType] || 'node-pending'
}

const formatAmount = (transaction) => {
  if (!transaction) return ''
  return '1,000,000.00'
}

// Mock event data for events tab
const mockEventData = ref([
  {
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001',
    parent_transaction_id: null,
    product: '外汇即期',
    account: 'WxxTest7_FXX_USD',
    event_type: 'BOOKED',
    status: '生效',
    entry_date: '2026-02-16',
    trade_date: '2026-02-15',
    modified_date: '2026-02-16 17:15:23',
    back_office_status: '待证实',
    confirmation_status: '未证实',
    confirmation_match_status: '待匹配',
    operator: 'system'
  },
  {
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001',
    parent_transaction_id: null,
    product: '外汇即期',
    account: 'WxxTest7_FXX_USD',
    event_type: 'CONFIRMED',
    status: '生效',
    entry_date: '2026-02-16',
    trade_date: '2026-02-15',
    modified_date: '2026-02-16 18:20:15',
    back_office_status: '已证实',
    confirmation_status: '已证实',
    confirmation_match_status: '匹配成功',
    operator: 'wang_lp'
  },
  {
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001',
    parent_transaction_id: null,
    product: '外汇即期',
    account: 'WxxTest7_FXX_USD',
    event_type: 'PAYMENT-DAILY',
    status: '生效',
    entry_date: '2026-02-16',
    trade_date: '2026-02-15',
    modified_date: '2026-02-25 09:30:00',
    back_office_status: '待发报',
    confirmation_status: '已证实',
    confirmation_match_status: '匹配成功',
    operator: 'system'
  },
  {
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001',
    parent_transaction_id: null,
    product: '外汇即期',
    account: 'WxxTest7_FXX_USD',
    event_type: 'SETTLEMENT-SENT',
    status: '生效',
    entry_date: '2026-02-16',
    trade_date: '2026-02-15',
    modified_date: '2026-02-25 10:15:42',
    back_office_status: '已发报',
    confirmation_status: '已证实',
    confirmation_match_status: '匹配成功',
    operator: 'system'
  }
])

// Mock cashflow data for cashflow tab
const mockCashflowData = ref([
  {
    seq: 1,
    cashflow_internal_id: 'CF20260216001',
    our_settlement_path: 'BANKZB_HOME_USD',
    counterparty_settlement_path: 'BANKZB_CPTY_10201',
    settlement_channel: 'SWIFT',
    delivery_mode: '全额交割',
    payment_type: '收款',
    payment_date: '2026-02-25',
    planned_netting_date: '2026-02-25',
    netting_rule: '日终轧差',
    netting_status: '待轧差',
    payment_status: '待支付',
    currency: 'USD',
    amount: '2,000,000.00',
    settlement_method: '集中清算结算',
    cashflow_type: '本金',
    payment_direction: '收入',
    interest_start_date: '2026-02-25',
    interest_end_date: '2026-02-25',
    stage: '起息',
    interest_basis: 'ACT/360',
    leg: 'LEG1',
    cashflow_number: 'CF001',
    product: '外汇即期',
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001'
  },
  {
    seq: 2,
    cashflow_internal_id: 'CF20260216002',
    our_settlement_path: 'BANKZB_HOME_CNY',
    counterparty_settlement_path: 'BANKZB_CPTY_10201_CNY',
    settlement_channel: 'SWIFT',
    delivery_mode: '全额交割',
    payment_type: '付款',
    payment_date: '2026-02-25',
    planned_netting_date: '2026-02-25',
    netting_rule: '日终轧差',
    netting_status: '待轧差',
    payment_status: '待支付',
    currency: 'CNY',
    amount: '13,820,000.00',
    settlement_method: '集中清算结算',
    cashflow_type: '本金',
    payment_direction: '支出',
    interest_start_date: '2026-02-25',
    interest_end_date: '2026-02-25',
    stage: '起息',
    interest_basis: 'ACT/360',
    leg: 'LEG1',
    cashflow_number: 'CF002',
    product: '外汇即期',
    external_id: 'FX202602160001',
    transaction_id: 'TXN20260216001'
  }
])
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.rcs-container {
  background: #f5f7fa;
  min-height: 100vh;
  color: #2c3e50;
  font-family: -apple-system, BlinkMacSystemFont, 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
  font-size: 12px;
  display: flex;
  flex-direction: column;
}

/* Top Navigation */
.top-nav {
  background: #ffffff;
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  display: flex;
  align-items: center;
  color: #1890ff;
  font-weight: 600;
  font-size: 18px;
}

.nav-menu {
  display: flex;
  gap: 2px;
  align-items: center;
}

.nav-item {
  color: #5a6c7d;
  text-decoration: none;
  padding: 6px 16px;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 15px;
}

.nav-item:hover {
  background: #f0f5ff;
  color: #1890ff;
}

.nav-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.nav-right {
  display: flex;
  align-items: center;
  color: #5a6c7d;
}

.user-info {
  font-size: 14px;
}

/* Main Layout */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  max-width: 1800px;
  margin: 0 auto;
  width: 100%;
}

/* Sidebar */
.sidebar {
  width: 120px;
  background: #ffffff;
  border-right: 1px solid #e1e8ed;
  flex-shrink: 0;
  padding: 20px 0;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  padding: 12px 12px;
  color: #5a6c7d;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: #f0f5ff;
  color: #1890ff;
}

.menu-item.active {
  background: #e6f7ff;
  color: #1890ff;
  border-left-color: #1890ff;
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Query Section */
.query-section {
  background: #ffffff;
  padding: 16px 16px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
}

.query-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  align-items: center;
}

.query-field {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 280px;
}

.query-field label {
  color: #5a6c7d;
  white-space: nowrap;
  font-size: 13px;
  min-width: 80px;
  text-align: right;
}

.query-field input,
.query-field select {
  background: #ffffff;
  border: 1px solid #d9d9d9;
  color: #2c3e50;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 13px;
  flex: 1;
  height: 32px;
}

.query-field input:focus,
.query-field select:focus {
  outline: none;
  border-color: #1890ff;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.separator {
  color: #8c8c8c;
  margin: 0 4px;
}

.query-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  width: 100%;
  margin-top: 8px;
}

.btn-reset,
.btn-query,
.btn-export,
.btn-toggle {
  padding: 6px 20px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  height: 32px;
}

.btn-toggle {
  background: #ffffff;
  color: #5a6c7d;
  border: 1px solid #d9d9d9;
}

.btn-toggle:hover {
  background: #f0f5ff;
  color: #1890ff;
  border-color: #1890ff;
}

.btn-reset {
  background: #ffffff;
  color: #5a6c7d;
  border: 1px solid #d9d9d9;
}

.btn-reset:hover {
  background: #f5f5f5;
  border-color: #b3b3b3;
}

.btn-query {
  background: #1890ff;
  color: #ffffff;
  border: 1px solid #1890ff;
}

.btn-query:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-export {
  background: #1890ff;
  color: #ffffff;
  border: 1px solid #1890ff;
}

.btn-export:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

/* Table */
.table-container {
  flex: 1;
  overflow: auto;
  background: #ffffff;
  border: none;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  border: none;
}

.data-table thead {
  background: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 500;
  color: #666;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
  font-size: 12px;
  border-left: none;
}

.data-table th:first-child {
  border-left: none;
}

.data-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
  white-space: nowrap;
  border-right: 1px solid #f0f0f0;
  border-left: none;
}

.data-table td:first-child {
  border-left: none;
}

.data-table td:last-child {
  border-right: none;
}

.data-table th {
  border-right: 1px solid #e0e0e0;
  border-left: none;
}

.data-table th:first-child {
  border-left: none;
}

.data-table th:last-child {
  border-right: none;
}

.data-table tbody tr {
  cursor: pointer;
  transition: background 0.1s;
  background: #ffffff;
}

.data-table tbody tr:hover {
  background: #E3F2FD;
}

.text-blue {
  color: #1890ff;
}

.text-orange {
  color: #fa8c16;
}

.text-green {
  color: #52c41a;
}

.text-red {
  color: #f5222d;
}

.text-right {
  text-align: right;
}

.status-badge {
  background: #fa8c16;
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 500;
}

.status-active {
  color: #52c41a;
}

.status-expired {
  color: #8c8c8c;
}

.status-invalid {
  color: #f5222d;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #8c8c8c;
}

.btn-detail,
.btn-action {
  padding: 4px 12px;
  margin-right: 6px;
  background: #ffffff;
  color: #5a6c7d;
  border: 1px solid #d9d9d9;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.btn-detail:hover,
.btn-action:hover {
  background: #f0f5ff;
  color: #1890ff;
  border: 1px solid #1890ff;
}

/* Pagination */
.pagination-bar {
  background: #ffffff;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #e1e8ed;
  flex-shrink: 0;
}

.pagination-left {
  color: #5a6c7d;
  font-size: 12px;
}

.pagination-center {
  display: flex;
  gap: 6px;
  align-items: center;
}

.pagination-center button {
  padding: 5px 12px;
  background: #ffffff;
  color: #2c3e50;
  border: 1px solid #d9d9d9;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  min-width: 32px;
  height: 28px;
}

.pagination-center button:hover {
  background: #f0f5ff;
  border-color: #1890ff;
  color: #1890ff;
}

.pagination-center button.active {
  background: #1890ff;
  color: #ffffff;
  border-color: #1890ff;
}

.page-dots {
  color: #8c8c8c;
  padding: 0 6px;
  font-size: 12px;
}

.pagination-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-right select {
  background: #ffffff;
  color: #2c3e50;
  border: 1px solid #d9d9d9;
  padding: 5px 10px;
  border-radius: 3px;
  font-size: 12px;
  height: 28px;
}

.pagination-right select:focus {
  outline: none;
  border-color: #1890ff;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5a6c7d;
  font-size: 12px;
}

.page-jump input {
  width: 50px;
  padding: 5px 8px;
  background: #ffffff;
  border: 1px solid #d9d9d9;
  color: #2c3e50;
  border-radius: 3px;
  font-size: 12px;
  text-align: center;
  height: 28px;
}

.page-jump input:focus {
  outline: none;
  border-color: #1890ff;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #ffffff;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  width: 90%;
  max-width: 1200px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e8ed;
  background: #fafafa;
}

.modal-header h3 {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

/* Operation Guide Styles - Removed duplicate, see line 2235 */


.btn-close {
  background: transparent;
  border: none;
  color: #5a6c7d;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  transition: all 0.2s;
  line-height: 1;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #2c3e50;
}

.modal-tabs {
  display: flex;
  gap: 2px;
  padding: 12px 20px 0;
  background: #ffffff;
  border-bottom: 1px solid #e1e8ed;
}

.tab-item {
  padding: 10px 24px;
  background: transparent;
  border: none;
  color: #5a6c7d;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px 4px 0 0;
  transition: all 0.2s;
  position: relative;
}

.tab-item:hover {
  background: #f0f5ff;
  color: #1890ff;
}

.tab-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1890ff;
}

.modal-body {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: #f5f7fa;
}

.tab-content {
  color: #2c3e50;
}

.tab-content h4 {
  color: #1890ff;
  font-size: 15px;
  margin-bottom: 16px;
  font-weight: 500;
}

.tab-content p {
  color: #5a6c7d;
  font-size: 13px;
  line-height: 1.6;
}

/* Detail Sections */
.detail-section {
  margin-bottom: 20px;
  background: #ffffff;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.section-title {
  color: #1890ff;
  font-size: 13px;
  margin-bottom: 16px;
  font-weight: 500;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.transaction-info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  font-size: 13px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  color: #666;
  min-width: 180px;
}

.info-row span {
  color: #333;
}

.amount-row {
  align-items: center;
}

.amount-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.amount-label {
  font-weight: 500;
  font-size: 12px;
}

.amount-label.buy {
  color: #10b981;
}

.amount-label.sell {
  color: #ef4444;
  margin-left: 40px;
}

.amount-value {
  background: #f0f8ff;
  padding: 6px 16px;
  border-radius: 3px;
  border: 1px solid #b3d9ff;
  min-width: 150px;
  text-align: right;
  color: #333;
}

.amount-value-sell {
  background: #fff5f5;
  padding: 6px 16px;
  border-radius: 3px;
  border: 1px solid #ffcccc;
  min-width: 150px;
  text-align: right;
  color: #333;
}

.detail-grid-2col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-grid-1col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  align-items: center;
  font-size: 13px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row label {
  color: #666;
  min-width: 180px;
}

.detail-row span {
  color: #333;
}

.badge-rcs {
  background: #e6f7ff;
  color: #1890ff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  margin-left: 8px;
  font-weight: 500;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px 24px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.detail-item label {
  color: #666;
  min-width: 120px;
  text-align: right;
}

.detail-item span {
  color: #333;
  flex: 1;
}

/* Detail Table */
.event-table-container {
  overflow-x: auto;
  margin-bottom: 12px;
  background: #ffffff;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: #ffffff;
}

.detail-table thead {
  background: #f5f5f5;
}

.detail-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 500;
  color: #666;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
  font-size: 12px;
  background: #f5f5f5;
}

.detail-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
  white-space: nowrap;
  background: #ffffff;
}

.detail-table tbody tr {
  background: #ffffff;
}

.detail-table tbody tr:hover {
  background: #E3F2FD;
}

.info-text {
  color: #666;
  font-size: 12px;
  margin-top: 8px;
}

.pagination-info {
  margin-top: 12px;
  padding: 8px 0;
  color: #666;
  font-size: 12px;
  text-align: left;
}

/* Operation Guide Styles */
.operation-guide {
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: flex-start;
}

.guide-status {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  background: #E3F2FD;
  border-radius: 4px;
  border-left: 3px solid #1890ff;
}

.status-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.status-info {
  flex: 1;
  min-width: 0;
}

.status-title {
  color: #333;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.status-content {
  flex: 1;
}

.status-value {
  color: #1890ff;
  font-weight: 600;
}

.status-desc {
  color: #666;
  font-size: 12px;
  line-height: 1.5;
}

.guide-action {
  padding: 12px;
  background: #E8F5E9;
  border-radius: 4px;
  border-left: 3px solid #4CAF50;
}

.action-title {
  color: #333;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.action-desc {
  color: #666;
  font-size: 12px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-guide-action {
  padding: 6px 16px;
  background: #1890ff;
  color: #ffffff;
  border: 1px solid #1890ff;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-guide-action:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.progress-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.progress-section .section-title {
  color: #e74c3c;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e74c3c;
}

.settlement-progress-section {
  margin-top: 2rem;
}

.lifecycle-progress-section {
  margin-top: 2rem;
}

/* Lifecycle Progress Styles */
.lifecycle-progress {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  padding: 2rem 0;
}

.progress-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.stage-connector {
  position: absolute;
  top: 20px;
  left: -50%;
  right: 50%;
  height: 3px;
  z-index: 0;
}

.connector-line {
  height: 100%;
  transition: all 0.3s ease;
}

.connector-active {
  background: #4CAF50;
}

.connector-inactive {
  background: #e0e0e0;
}

.stage-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.node-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid #e0e0e0;
  background: #f5f5f5;
  color: #999;
}

.stage-completed .node-circle {
  background: #4CAF50;
  border-color: #4CAF50;
  color: white;
}

.stage-current .node-circle {
  background: #D32F2F;
  border-color: #D32F2F;
  color: white;
  box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.1);
}

.stage-pending .node-circle {
  background: #f5f5f5;
  border-color: #e0e0e0;
  color: #999;
}

.stage-failed .node-circle {
  background: #F44336;
  border-color: #F44336;
  color: white;
}

.stage-info {
  text-align: center;
}

.stage-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.stage-desc {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.stage-time {
  font-size: 0.75rem;
  color: #1890ff;
}

.stage-completed .stage-name {
  color: #4CAF50;
}

.stage-current .stage-name {
  color: #D32F2F;
}

/* New Lifecycle Progress Styles */
.lifecycle-progress-new {
  display: flex;
  gap: 0;
  padding: 2rem 0;
  position: relative;
}

.progress-node {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 0 1rem;
}

.progress-node:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 30px;
  right: -1px;
  width: 100%;
  height: 2px;
  background: #e0e0e0;
  z-index: 0;
}

.node-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.node-icon.node-completed {
  background: #1890ff;
  color: white;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.2);
}

.node-icon.node-current {
  background: #D32F2F;
  color: white;
  box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.2);
  animation: pulse-node 2s infinite;
}

.node-icon.node-pending {
  background: #f5f5f5;
  color: #999;
  border: 2px solid #e0e0e0;
}

@keyframes pulse-node {
  0%, 100% {
    box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(211, 47, 47, 0.1);
  }
}

.node-content {
  text-align: center;
  width: 100%;
}

.node-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.node-subtitle {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.75rem;
}

.node-status {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.status-item i {
  font-size: 0.875rem;
}

.status-item.success {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-item.error {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.status-item.warning {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.status-item.pending {
  background: rgba(136, 145, 168, 0.1);
  color: #8891a8;
  border: 1px solid rgba(136, 145, 168, 0.3);
}

.status-item.terminated {
  background: rgba(158, 158, 158, 0.1);
  color: #9e9e9e;
  border: 1px solid rgba(158, 158, 158, 0.3);
}

.node-substeps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.substep {
  font-size: 0.75rem;
  color: #c5cad3;
  padding: 0.25rem 0;
}

.substep-label {
  display: block;
  margin-bottom: 0.25rem;
}

.substep-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.substep-action i {
  font-size: 0.875rem;
}

.substep-action.error {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.substep-action.warning {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

/* Icon placeholders (using text as icons) */
.icon-clipboard::before { content: '📋'; }
.icon-send::before { content: '📤'; }
.icon-check-square::before { content: '☑️'; }
.icon-dollar::before { content: '💰'; }
.icon-check-circle::before { content: '✓'; }
.icon-x-circle::before { content: '✕'; }
.icon-alert::before { content: '⚠️'; }
.icon-refresh::before { content: '🔄'; }
.icon-x::before { content: '✕'; }
.icon-edit::before { content: '✏️'; }
.icon-clock::before { content: '⏰'; }
.icon-check::before { content: '✓'; }

/* Responsive */
@media (max-width: 1200px) {
  .lifecycle-progress-new {
    flex-direction: column;
    gap: 2rem;
  }

  .progress-node:not(:last-child)::after {
    display: none;
  }

  .progress-node {
    padding: 0;
  }
}

.stage-current .stage-name {
  color: #D32F2F;
}

</style>
