# Settlement Operation Guide API 文档

## 概述

Settlement Operation Guide API 是一个用于交易结算操作指导的RESTful API服务。该API提供交易查询、现金流管理、生命周期跟踪和操作指引等功能。

**版本**: 1.0.0  
**基础URL**: `http://localhost:8000`  
**协议**: HTTP/HTTPS

## 认证

所有API请求都需要通过认证。系统使用基于Token的认证机制。

### 请求头

```
Authorization: Bearer <your_token>
```

## 通用响应格式

### 成功响应

```json
{
  "data": [...],
  "pagination": {
    "currentPage": 1,
    "totalPages": 10,
    "totalRecords": 200,
    "pageSize": 20
  }
}
```

### 错误响应

```json
{
  "code": "ERROR_CODE",
  "message": "错误描述",
  "details": {},
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12345"
}
```

### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| INVALID_PARAMETER | 400 | 参数无效 |
| MISSING_REQUIRED_FIELD | 400 | 缺少必填字段 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 无权限 |
| CONCURRENT_CONFLICT | 409 | 并发冲突 |
| EXPORT_LIMIT_EXCEEDED | 400 | 导出记录数超限 |
| INTERNAL_ERROR | 500 | 内部错误 |
| DATABASE_ERROR | 500 | 数据库错误 |

## API端点

### 1. 健康检查

#### GET /health

检查API服务健康状态。

**响应示例**:
```json
{
  "status": "healthy"
}
```

---

## 交易管理 (Transactions)

### 2. 查询交易汇总列表

#### GET /api/transactions

查询交易汇总列表，支持多条件组合查询和分页。

**查询参数**:

| 参数 | 类型 | 必填 | 描述 | 示例 |
|-----|------|------|------|------|
| external_id | string | 否 | 外部流水号 | EXT-12345 |
| status | string | 否 | 交易状态 | 生效/到期/失效 |
| trade_date_from | string | 否 | 交易日起始 | 2026-01-01 |
| trade_date_to | string | 否 | 交易日结束 | 2026-12-31 |
| value_date_from | string | 否 | 起息日起始 | 2026-01-01 |
| value_date_to | string | 否 | 起息日结束 | 2026-12-31 |
| maturity_date_from | string | 否 | 到期日起始 | 2026-01-01 |
| maturity_date_to | string | 否 | 到期日结束 | 2026-12-31 |
| counterparty | string | 否 | 交易对手 | ABC Bank |
| product | string | 否 | 产品类型 | 外汇即期/外汇远期 |
| currency | string | 否 | 货币 | USD/CNY/EUR |
| operating_institution | string | 否 | 运营机构 | 1530H |
| business_institution | string | 否 | 业务机构 | Branch-01 |
| settlement_method | string | 否 | 清算方式 | 全额/净额 |
| confirmation_type | string | 否 | 证实方式 | SWIFT/文本 |
| source | string | 否 | 交易来源 | GIT/FXO |
| page | integer | 否 | 页码(默认1) | 1 |
| page_size | integer | 否 | 每页记录数(默认20) | 20 |
| sort_by | string | 否 | 排序字段(默认trade_date) | trade_date |
| sort_order | string | 否 | 排序方向(默认DESC) | DESC/ASC |

**响应示例**:
```json
{
  "data": [
    {
      "external_id": "EXT-12345",
      "transaction_id": "TXN-67890",
      "entry_date": "2026-02-20",
      "trade_date": "2026-02-21",
      "value_date": "2026-02-23",
      "maturity_date": "2026-03-23",
      "account": "ACC-001",
      "product": "外汇即期",
      "direction": "BUY",
      "underlying": "USD/CNY",
      "counterparty": "ABC Bank",
      "status": "生效",
      "back_office_status": "已证实",
      "settlement_method": "全额",
      "confirmation_number": "CONF-123",
      "confirmation_type": "SWIFT",
      "operating_institution": "1530H",
      "trader": "张三"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_records": 82,
    "page_size": 20
  }
}
```

---

### 3. 查询交易详情

#### GET /api/transactions/{external_id}

根据外部流水号查询交易详细信息。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| external_id | string | 是 | 外部流水号 |

**响应示例**:
```json
{
  "external_id": "EXT-12345",
  "transaction_id": "TXN-67890",
  "trade_date": "2026-02-21",
  "value_date": "2026-02-23",
  "maturity_date": "2026-03-23",
  "product": "外汇即期",
  "currency_pair": "USD/CNY",
  "buy_amount": 100000.00,
  "sell_amount": 720000.00,
  "exchange_rate": 7.2000,
  "counterparty": "ABC Bank",
  "status": "生效",
  "back_office_status": "已证实"
}
```

**错误响应**:
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "未找到对应的交易记录",
  "details": {
    "resourceType": "Transaction",
    "resourceId": "EXT-12345"
  }
}
```

---

### 4. 查询交易事件记录

#### GET /api/transactions/{external_id}/events

查询交易的所有事件流转记录。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| external_id | string | 是 | 外部流水号 |

**查询参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| page | integer | 否 | 页码(默认1) |
| page_size | integer | 否 | 每页记录数(默认15) |

**响应示例**:
```json
{
  "data": [
    {
      "event_id": "EVT-001",
      "external_id": "EXT-12345",
      "transaction_id": "TXN-67890",
      "event_type": "BOOKED",
      "transaction_status": "生效",
      "entry_date": "2026-02-20",
      "trade_date": "2026-02-21",
      "modified_date": "2026-02-21T10:30:00Z",
      "back_office_status": "已证实",
      "operator": "张三"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_records": 4,
    "page_size": 15
  }
}
```

---

### 5. 查询交易支付信息

#### GET /api/transactions/{transaction_id}/payment-info

查询交易的支付信息和清算方式。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 是 | 交易流水号 |

**响应示例**:
```json
{
  "settlement_method": {
    "our_bank": {
      "bank_name": "中国银行香港",
      "bank_code": "BKCHHKHH",
      "account_name": "BOC HK",
      "account_number": "012-345-678"
    },
    "counterparty_bank": {
      "bank_name": "ABC Bank",
      "bank_code": "ABCCHKHH",
      "account_name": "ABC Corp",
      "account_number": "987-654-321"
    }
  },
  "payment_info": {
    "instruction_id": "INST-001",
    "payment_date": "2026-02-23",
    "message_type": "pacs.008",
    "currency": "USD",
    "amount": 100000.00,
    "sender": "BKCHHKHH",
    "send_time": "2026-02-23T09:00:00Z"
  }
}
```

---

### 6. 查询交易账务记录

#### GET /api/transactions/{transaction_id}/accounting-records

查询交易的账务处理记录。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 是 | 交易流水号 |

**查询参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| page | integer | 否 | 页码(默认1) |
| page_size | integer | 否 | 每页记录数(默认15) |

**响应示例**:
```json
{
  "data": [
    {
      "voucher_id": "VCH-001",
      "actual_accounting_date": "2026-02-23",
      "planned_accounting_date": "2026-02-23",
      "event_number": "EVT-001",
      "debit_credit_indicator": "DEBIT",
      "currency": "USD",
      "account_subject": "1001",
      "transaction_amount": 100000.00
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_records": 2,
    "page_size": 15
  }
}
```

---

### 7. 查询账务金额汇总

#### GET /api/transactions/{transaction_id}/accounting-summary

查询交易的账务金额按币种汇总。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 是 | 交易流水号 |

**响应示例**:
```json
{
  "USD": {
    "debit": 100000.00,
    "credit": 0.00,
    "net": 100000.00
  },
  "CNY": {
    "debit": 0.00,
    "credit": 720000.00,
    "net": -720000.00
  }
}
```

---

### 8. 查询交易生命周期进度

#### GET /api/transactions/{transaction_id}/progress

查询交易当前所处的生命周期阶段和进度。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 是 | 交易流水号 |

**响应示例**:
```json
{
  "current_stage": "收付发报",
  "current_status": "处理中",
  "progress_percentage": 75,
  "stage_completion_time": null,
  "status_receipts": [
    {
      "stage": "SWIFT证实",
      "status": "SUCCESS",
      "timestamp": "2026-02-21T10:30:00Z",
      "message": "证实成功",
      "can_proceed": true
    },
    {
      "stage": "证实匹配",
      "status": "SUCCESS",
      "timestamp": "2026-02-21T11:00:00Z",
      "message": "匹配成功",
      "can_proceed": true
    },
    {
      "stage": "收付发报",
      "status": "PROCESSING",
      "timestamp": null,
      "message": "正在处理",
      "can_proceed": true
    }
  ],
  "flow_visualization": [
    {
      "id": "swift_confirm",
      "name": "SWIFT证实",
      "status": "COMPLETED",
      "timestamp": "2026-02-21T10:30:00Z"
    },
    {
      "id": "match",
      "name": "证实匹配",
      "status": "COMPLETED",
      "timestamp": "2026-02-21T11:00:00Z"
    },
    {
      "id": "payment",
      "name": "收付发报",
      "status": "CURRENT",
      "timestamp": null
    }
  ]
}
```

---

### 9. 查询交易操作指引

#### GET /api/transactions/{transaction_id}/operation-guide

根据交易当前状态生成操作指引。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 是 | 交易流水号 |

**响应示例**:
```json
{
  "next_action": "等待SWIFT发报完成",
  "action_entry": {
    "type": "LINK",
    "label": "查看SWIFT系统状态",
    "url": "/swift/status"
  },
  "notes": "系统正在自动处理，无需人工干预",
  "estimated_time": "预计5分钟内完成"
}
```

---

## 现金流管理 (Cash Flows)

### 10. 查询现金流列表

#### GET /api/cash-flows

查询现金流列表，支持多条件组合查询和分页。

**查询参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| transaction_id | string | 否 | 交易流水号 |
| cash_flow_id | string | 否 | 现金流内部ID |
| payment_info_id | string | 否 | 收付信息ID |
| settlement_id | string | 否 | 结算内部ID |
| direction | string | 否 | 方向(RECEIVE/PAY) |
| currency | string | 否 | 币种 |
| amount_min | number | 否 | 最小金额 |
| amount_max | number | 否 | 最大金额 |
| payment_date_from | string | 否 | 收付日期起始 |
| payment_date_to | string | 否 | 收付日期结束 |
| status | string | 否 | 状态 |
| page | integer | 否 | 页码(默认1) |
| page_size | integer | 否 | 每页记录数(默认20) |

**响应示例**:
```json
{
  "data": [
    {
      "cash_flow_id": "CF-001",
      "transaction_id": "TXN-67890",
      "direction": "PAY",
      "currency": "USD",
      "amount": 100000.00,
      "payment_date": "2026-02-23",
      "account_number": "012-345-678",
      "current_status": "待SWIFT发报",
      "progress_percentage": 50
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_records": 45,
    "page_size": 20
  },
  "summary": {
    "USD": {
      "receive": 50000.00,
      "pay": 100000.00
    },
    "CNY": {
      "receive": 720000.00,
      "pay": 0.00
    }
  }
}
```

---

### 11. 查询现金流详情

#### GET /api/cash-flows/{cash_flow_id}

根据现金流ID查询详细信息。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| cash_flow_id | string | 是 | 现金流内部ID |

**响应示例**:
```json
{
  "cash_flow_id": "CF-001",
  "transaction_id": "TXN-67890",
  "direction": "PAY",
  "currency": "USD",
  "amount": 100000.00,
  "payment_date": "2026-02-23",
  "account_info": {
    "account_number": "012-345-678",
    "account_name": "BOC HK",
    "bank_name": "中国银行香港",
    "bank_code": "BKCHHKHH"
  },
  "settlement_method": "SWIFT",
  "current_status": "待SWIFT发报",
  "progress_percentage": 50
}
```

---

### 12. 查询现金流收付进度

#### GET /api/cash-flows/{cash_flow_id}/progress

查询现金流的收付进度详情。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| cash_flow_id | string | 是 | 现金流内部ID |

**响应示例**:
```json
{
  "current_stage": "SWIFT发报",
  "current_status": "处理中",
  "progress_percentage": 50,
  "status_receipts": [
    {
      "stage": "反洗钱检查",
      "status": "SUCCESS",
      "timestamp": "2026-02-23T08:00:00Z",
      "message": "反洗钱检查通过",
      "can_proceed": true
    },
    {
      "stage": "SWIFT发报",
      "status": "PROCESSING",
      "timestamp": null,
      "message": "正在发送SWIFT报文",
      "can_proceed": true
    }
  ],
  "flow_visualization": [
    {
      "id": "aml_check",
      "name": "反洗钱检查",
      "status": "COMPLETED",
      "timestamp": "2026-02-23T08:00:00Z"
    },
    {
      "id": "swift_send",
      "name": "SWIFT发报",
      "status": "CURRENT",
      "timestamp": null
    },
    {
      "id": "core_posting",
      "name": "核心入账",
      "status": "PENDING",
      "timestamp": null
    }
  ]
}
```

---

### 13. 查询现金流操作指引

#### GET /api/cash-flows/{cash_flow_id}/operation-guide

根据现金流当前状态生成操作指引。

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| cash_flow_id | string | 是 | 现金流内部ID |

**响应示例**:
```json
{
  "next_action": "等待SWIFT报文发送完成",
  "action_entry": {
    "type": "LINK",
    "label": "查看SWIFT发送状态",
    "url": "/swift/messages"
  },
  "notes": "系统正在自动发送SWIFT报文",
  "estimated_time": "预计3分钟内完成"
}
```

---

## 数据导出 (Export)

### 14. 导出交易列表

#### GET /api/export/transactions

导出交易列表为Excel或CSV文件。

**查询参数**:

支持所有交易查询参数，外加：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| format | string | 否 | 导出格式(excel/csv，默认excel) |
| fields | string | 否 | 导出字段(逗号分隔) |

**响应**:

返回文件流，Content-Type根据格式设置：
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- CSV: `text/csv`

**错误响应**:
```json
{
  "code": "EXPORT_LIMIT_EXCEEDED",
  "message": "导出记录数超过限制，请缩小查询范围",
  "details": {
    "maxRecords": 10000,
    "requestedRecords": 15000
  }
}
```

---

### 15. 导出现金流列表

#### GET /api/export/cash-flows

导出现金流列表为Excel或CSV文件。

**查询参数**:

支持所有现金流查询参数，外加：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| format | string | 否 | 导出格式(excel/csv，默认excel) |

**响应**:

返回文件流，Content-Type根据格式设置。

---

## 使用示例

### Python示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 认证Token
headers = {
    "Authorization": "Bearer your_token_here"
}

# 1. 查询交易列表
response = requests.get(
    f"{BASE_URL}/api/transactions",
    params={
        "external_id": "EXT-12345",
        "page": 1,
        "page_size": 20
    },
    headers=headers
)
transactions = response.json()

# 2. 查询交易详情
external_id = "EXT-12345"
response = requests.get(
    f"{BASE_URL}/api/transactions/{external_id}",
    headers=headers
)
detail = response.json()

# 3. 查询生命周期进度
transaction_id = "TXN-67890"
response = requests.get(
    f"{BASE_URL}/api/transactions/{transaction_id}/progress",
    headers=headers
)
progress = response.json()

# 4. 导出交易列表
response = requests.get(
    f"{BASE_URL}/api/export/transactions",
    params={
        "format": "excel",
        "trade_date_from": "2026-01-01",
        "trade_date_to": "2026-12-31"
    },
    headers=headers
)
with open("transactions.xlsx", "wb") as f:
    f.write(response.content)
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:8000";
const token = "your_token_here";

// 1. 查询交易列表
async function getTransactions() {
  const response = await fetch(
    `${BASE_URL}/api/transactions?external_id=EXT-12345&page=1&page_size=20`,
    {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data;
}

// 2. 查询交易详情
async function getTransactionDetail(externalId) {
  const response = await fetch(
    `${BASE_URL}/api/transactions/${externalId}`,
    {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data;
}

// 3. 查询生命周期进度
async function getProgress(transactionId) {
  const response = await fetch(
    `${BASE_URL}/api/transactions/${transactionId}/progress`,
    {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data;
}
```

---

## 速率限制

API实施速率限制以保护服务：

- 每个用户每分钟最多100个请求
- 超过限制将返回429状态码

---

## 版本控制

API使用URL路径进行版本控制。当前版本为v1，所有端点都在 `/api/` 路径下。

未来版本将使用 `/api/v2/` 等路径。

---

## 支持

如有问题或需要帮助，请联系：

- 邮箱: support@example.com
- 文档: http://docs.example.com
- 问题追踪: http://issues.example.com
