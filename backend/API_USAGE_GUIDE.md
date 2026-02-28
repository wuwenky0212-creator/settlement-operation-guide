# API使用指南

## 快速开始

### 1. 获取访问Token

在使用API之前，您需要获取访问Token。请联系系统管理员获取您的Token。

### 2. 设置请求头

所有API请求都需要包含以下请求头：

```
Authorization: Bearer <your_token>
Content-Type: application/json
```

### 3. 发起第一个请求

使用curl测试健康检查端点：

```bash
curl -X GET "http://localhost:8000/health" \
  -H "Authorization: Bearer your_token_here"
```

## 常见使用场景

### 场景1: 查询特定交易的完整信息

**步骤**:

1. 使用外部流水号查询交易详情
2. 查询交易的事件记录
3. 查询交易的账务信息
4. 查询交易的生命周期进度
5. 获取操作指引

**示例代码**:

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"Authorization": "Bearer your_token"}
external_id = "EXT-12345"

# 1. 查询交易详情
detail = requests.get(
    f"{BASE_URL}/api/transactions/{external_id}",
    headers=headers
).json()

transaction_id = detail["transaction_id"]

# 2. 查询事件记录
events = requests.get(
    f"{BASE_URL}/api/transactions/{external_id}/events",
    headers=headers
).json()

# 3. 查询账务信息
accounting = requests.get(
    f"{BASE_URL}/api/transactions/{transaction_id}/accounting-records",
    headers=headers
).json()

# 4. 查询生命周期进度
progress = requests.get(
    f"{BASE_URL}/api/transactions/{transaction_id}/progress",
    headers=headers
).json()

# 5. 获取操作指引
guide = requests.get(
    f"{BASE_URL}/api/transactions/{transaction_id}/operation-guide",
    headers=headers
).json()

print(f"当前阶段: {progress['current_stage']}")
print(f"下一步操作: {guide['next_action']}")
```

---

### 场景2: 按条件查询交易并导出

**步骤**:

1. 使用查询条件获取交易列表
2. 确认查询结果
3. 使用相同条件导出数据

**示例代码**:

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"Authorization": "Bearer your_token"}

# 查询条件
params = {
    "trade_date_from": "2026-01-01",
    "trade_date_to": "2026-12-31",
    "product": "外汇即期",
    "status": "生效",
    "page": 1,
    "page_size": 20
}

# 1. 查询交易列表
response = requests.get(
    f"{BASE_URL}/api/transactions",
    params=params,
    headers=headers
)
result = response.json()

print(f"找到 {result['pagination']['total_records']} 条记录")

# 2. 导出数据
export_params = params.copy()
export_params["format"] = "excel"
del export_params["page"]
del export_params["page_size"]

response = requests.get(
    f"{BASE_URL}/api/export/transactions",
    params=export_params,
    headers=headers
)

# 保存文件
with open("transactions.xlsx", "wb") as f:
    f.write(response.content)

print("导出完成: transactions.xlsx")
```

---

### 场景3: 监控现金流收付进度

**步骤**:

1. 查询特定交易的现金流列表
2. 对每个现金流查询收付进度
3. 根据状态获取操作指引

**示例代码**:

```python
import requests
import time

BASE_URL = "http://localhost:8000"
headers = {"Authorization": "Bearer your_token"}
transaction_id = "TXN-67890"

# 1. 查询现金流列表
cash_flows = requests.get(
    f"{BASE_URL}/api/cash-flows",
    params={"transaction_id": transaction_id},
    headers=headers
).json()

# 2. 监控每个现金流的进度
for cf in cash_flows["data"]:
    cash_flow_id = cf["cash_flow_id"]
    
    # 查询进度
    progress = requests.get(
        f"{BASE_URL}/api/cash-flows/{cash_flow_id}/progress",
        headers=headers
    ).json()
    
    # 获取操作指引
    guide = requests.get(
        f"{BASE_URL}/api/cash-flows/{cash_flow_id}/operation-guide",
        headers=headers
    ).json()
    
    print(f"现金流 {cash_flow_id}:")
    print(f"  当前阶段: {progress['current_stage']}")
    print(f"  进度: {progress['progress_percentage']}%")
    print(f"  下一步: {guide['next_action']}")
    print()
```

---

### 场景4: 实时轮询状态更新

**步骤**:

1. 定期查询交易进度
2. 检测状态变化
3. 根据新状态采取行动

**示例代码**:

```python
import requests
import time

BASE_URL = "http://localhost:8000"
headers = {"Authorization": "Bearer your_token"}
transaction_id = "TXN-67890"

def check_progress():
    """检查交易进度"""
    response = requests.get(
        f"{BASE_URL}/api/transactions/{transaction_id}/progress",
        headers=headers
    )
    return response.json()

# 轮询直到完成
last_stage = None
while True:
    progress = check_progress()
    current_stage = progress["current_stage"]
    
    # 检测状态变化
    if current_stage != last_stage:
        print(f"状态更新: {current_stage}")
        print(f"进度: {progress['progress_percentage']}%")
        
        # 获取操作指引
        guide = requests.get(
            f"{BASE_URL}/api/transactions/{transaction_id}/operation-guide",
            headers=headers
        ).json()
        print(f"下一步: {guide['next_action']}")
        print()
        
        last_stage = current_stage
    
    # 检查是否完成
    if progress["progress_percentage"] == 100:
        print("交易处理完成!")
        break
    
    # 等待10秒后再次检查
    time.sleep(10)
```

---

## 分页处理

### 基本分页

API使用基于页码的分页：

```python
# 获取第一页
response = requests.get(
    f"{BASE_URL}/api/transactions",
    params={"page": 1, "page_size": 20},
    headers=headers
)
result = response.json()

print(f"当前页: {result['pagination']['current_page']}")
print(f"总页数: {result['pagination']['total_pages']}")
print(f"总记录数: {result['pagination']['total_records']}")
```

### 遍历所有页

```python
def get_all_transactions(params):
    """获取所有交易记录"""
    all_transactions = []
    page = 1
    
    while True:
        params["page"] = page
        response = requests.get(
            f"{BASE_URL}/api/transactions",
            params=params,
            headers=headers
        )
        result = response.json()
        
        all_transactions.extend(result["data"])
        
        # 检查是否还有更多页
        if page >= result["pagination"]["total_pages"]:
            break
        
        page += 1
    
    return all_transactions

# 使用示例
transactions = get_all_transactions({
    "trade_date_from": "2026-01-01",
    "page_size": 50
})
print(f"共获取 {len(transactions)} 条记录")
```

---

## 错误处理

### 处理常见错误

```python
import requests

def safe_api_call(url, **kwargs):
    """安全的API调用，包含错误处理"""
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("资源不存在")
            return None
        elif e.response.status_code == 400:
            error = e.response.json()
            print(f"参数错误: {error.get('message')}")
            return None
        elif e.response.status_code == 409:
            print("并发冲突，请重试")
            return None
        else:
            print(f"API错误: {e}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        return None

# 使用示例
detail = safe_api_call(
    f"{BASE_URL}/api/transactions/EXT-12345",
    headers=headers
)

if detail:
    print(f"交易状态: {detail['status']}")
else:
    print("获取交易详情失败")
```

### 重试机制

```python
import requests
import time

def api_call_with_retry(url, max_retries=3, **kwargs):
    """带重试机制的API调用"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # 并发冲突
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"并发冲突，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
            raise
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"请求失败，重试中...")
                time.sleep(1)
                continue
            raise
    
    raise Exception("达到最大重试次数")
```

---

## 性能优化

### 1. 使用合适的分页大小

```python
# 不推荐：每次只获取少量记录
params = {"page_size": 10}  # 需要更多请求

# 推荐：使用较大的分页大小
params = {"page_size": 50}  # 减少请求次数
```

### 2. 只请求需要的字段

```python
# 导出时指定字段
params = {
    "format": "excel",
    "fields": "external_id,transaction_id,trade_date,status"
}
```

### 3. 使用连接池

```python
import requests

# 创建会话以复用连接
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})

# 使用会话发起请求
response = session.get(f"{BASE_URL}/api/transactions")
```

---

## 最佳实践

### 1. 缓存Token

```python
class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
    
    def get(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, **kwargs)

# 使用示例
client = APIClient(BASE_URL, token)
response = client.get("/api/transactions")
```

### 2. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_call(url, **kwargs):
    logger.info(f"API请求: {url}")
    response = requests.get(url, **kwargs)
    logger.info(f"响应状态: {response.status_code}")
    return response.json()
```

### 3. 超时设置

```python
# 设置合理的超时时间
response = requests.get(
    url,
    headers=headers,
    timeout=30  # 30秒超时
)
```

---

## 常见问题

### Q1: 如何处理大量数据导出？

A: 对于大量数据，建议：
1. 使用查询条件缩小范围
2. 分批导出（按日期范围）
3. 使用CSV格式（比Excel更快）

```python
# 分批导出示例
from datetime import datetime, timedelta

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 12, 31)
batch_days = 30

current = start_date
while current < end_date:
    batch_end = min(current + timedelta(days=batch_days), end_date)
    
    params = {
        "format": "csv",
        "trade_date_from": current.strftime("%Y-%m-%d"),
        "trade_date_to": batch_end.strftime("%Y-%m-%d")
    }
    
    response = requests.get(
        f"{BASE_URL}/api/export/transactions",
        params=params,
        headers=headers
    )
    
    filename = f"transactions_{current.strftime('%Y%m%d')}.csv"
    with open(filename, "wb") as f:
        f.write(response.content)
    
    current = batch_end + timedelta(days=1)
```

### Q2: 如何实现实时更新？

A: 推荐使用轮询机制：

```python
# 前端轮询示例（JavaScript）
function pollProgress(transactionId) {
    const interval = setInterval(async () => {
        const response = await fetch(
            `${BASE_URL}/api/transactions/${transactionId}/progress`,
            { headers: { "Authorization": `Bearer ${token}` } }
        );
        const progress = await response.json();
        
        // 更新UI
        updateProgressUI(progress);
        
        // 如果完成，停止轮询
        if (progress.progress_percentage === 100) {
            clearInterval(interval);
        }
    }, 10000);  // 每10秒轮询一次
}
```

### Q3: 如何处理并发冲突？

A: 使用重试机制：

```python
def update_with_retry(transaction_id, new_status):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 获取当前版本
            detail = requests.get(
                f"{BASE_URL}/api/transactions/{transaction_id}",
                headers=headers
            ).json()
            
            # 更新（假设有更新API）
            response = requests.put(
                f"{BASE_URL}/api/transactions/{transaction_id}",
                json={
                    "status": new_status,
                    "version": detail["version"]
                },
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # 并发冲突
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            raise
```

---

## 支持与反馈

如有问题或建议，请联系：

- 技术支持: support@example.com
- 文档反馈: docs@example.com
- Bug报告: https://issues.example.com
