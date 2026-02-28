# 进度跟踪功能快速启动指南

## 功能说明

在交易信息和现金流信息页面底部添加了简化的生命周期进度指示器，用户可以快速查看当前处理进度。

## 启动步骤

### 1. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或使用提供的启动脚本：
```bash
cd backend
./start_backend.bat  # Windows
```

### 2. 启动前端服务

```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

前端将在 http://localhost:5173 启动

### 3. 验证功能

#### 验证交易信息进度条

1. 打开浏览器访问 http://localhost:5173
2. 进入交易汇总页面
3. 点击任意交易记录，打开交易详情
4. 在"交易信息"标签页，滚动到底部
5. 应该能看到"生命周期进度"部分，显示横向的步骤条

#### 验证现金流进度条

1. 在交易详情页面，切换到"现金流信息"标签页（如果有）
2. 或者直接访问现金流详情页面
3. 在基本信息部分下方，应该能看到"收付进度"指示器

## 预期效果

### 进度条外观

```
○ ━━━ ○ ━━━ ● ━━━ ○ ━━━ ○
交易点  已证实  已记账  已发报  已完成
```

- ✓ 绿色圆圈：已完成的步骤
- ● 红色圆圈（带动画）：当前步骤
- ○ 灰色圆圈：待处理步骤
- ✗ 红色圆圈：失败步骤

### 连接线颜色

- 绿色：连接已完成的步骤
- 灰色：连接待处理的步骤
- 红色：失败步骤的连接线

## 测试数据

如果后端API尚未完全实现，可以使用以下模拟数据进行测试：

### 模拟交易进度数据

```json
{
  "flowVisualization": [
    {
      "id": "1",
      "name": "交易点",
      "status": "COMPLETED",
      "timestamp": "2026-02-27T10:00:00Z"
    },
    {
      "id": "2",
      "name": "已证实",
      "status": "COMPLETED",
      "timestamp": "2026-02-27T10:05:00Z"
    },
    {
      "id": "3",
      "name": "已记账",
      "status": "CURRENT",
      "timestamp": null
    },
    {
      "id": "4",
      "name": "已发报",
      "status": "PENDING",
      "timestamp": null
    },
    {
      "id": "5",
      "name": "已完成",
      "status": "PENDING",
      "timestamp": null
    }
  ]
}
```

### 模拟现金流进度数据

```json
{
  "flow_visualization": [
    {
      "id": "1",
      "name": "反洗钱检查",
      "status": "COMPLETED",
      "timestamp": "2026-02-27T10:00:00Z"
    },
    {
      "id": "2",
      "name": "SWIFT发报",
      "status": "COMPLETED",
      "timestamp": "2026-02-27T10:10:00Z"
    },
    {
      "id": "3",
      "name": "核心入账",
      "status": "CURRENT",
      "timestamp": null
    }
  ]
}
```

## 故障排查

### 问题1: 进度条不显示

**可能原因**:
- API未返回进度数据
- 数据格式不正确

**解决方法**:
1. 打开浏览器开发者工具（F12）
2. 查看Console标签，检查是否有错误信息
3. 查看Network标签，检查API请求是否成功
4. 确认API返回的数据格式符合预期

### 问题2: 进度条显示异常

**可能原因**:
- 状态值不正确（应为 COMPLETED、CURRENT、PENDING、FAILED）
- 数据结构不匹配

**解决方法**:
1. 检查API返回的status字段值
2. 确保status值为大写（组件会自动转换为小写）
3. 检查flowVisualization或flow_visualization字段是否存在

### 问题3: 样式显示不正确

**可能原因**:
- CSS未正确加载
- 浏览器缓存问题

**解决方法**:
1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 硬刷新页面（Ctrl+F5）
3. 检查浏览器控制台是否有CSS加载错误

## 运行测试

```bash
cd frontend
npm test
```

测试将验证：
- ProgressStepper组件正确渲染
- 状态类正确应用
- 连接线正确显示
- 边界情况处理

## 浏览器兼容性

支持的浏览器：
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 移动端测试

1. 在浏览器中按F12打开开发者工具
2. 点击设备工具栏图标（或按Ctrl+Shift+M）
3. 选择移动设备（如iPhone 12）
4. 验证进度条支持横向滚动
5. 验证步骤图标和文字大小适配移动端

## 性能优化

- 进度数据加载失败不会影响主要功能
- 使用异步加载，不阻塞页面渲染
- 错误静默处理，不显示错误提示（进度是可选功能）

## 下一步开发

如果需要进一步增强功能，可以考虑：

1. **实时更新**: 添加轮询机制，每10秒自动刷新进度
2. **点击交互**: 点击步骤节点显示详细信息
3. **动画效果**: 步骤状态变化时添加过渡动画
4. **工具提示**: 鼠标悬停显示时间戳和详细状态
5. **导出功能**: 支持导出进度报告

## 相关文档

- [完整实施文档](./PROGRESS_STEPPER_IMPLEMENTATION.md)
- [组件使用文档](./frontend/src/components/ProgressStepper.README.md)
- [需求文档](./.kiro/specs/settlement-operation-guide/requirements.md)
- [设计文档](./.kiro/specs/settlement-operation-guide/design.md)

## 联系支持

如有问题，请查看：
1. 浏览器控制台错误信息
2. 后端API日志
3. 组件文档和测试文件
