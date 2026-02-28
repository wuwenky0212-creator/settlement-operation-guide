# UI组件库

本目录包含操作指导系统的通用UI组件，采用murex风格设计。

## 组件列表

### 1. PaginationComponent（分页组件）

用于数据列表的分页控制。

**Props:**
- `currentPage` (Number, required): 当前页码
- `pageSize` (Number, required): 每页记录数
- `totalRecords` (Number, required): 总记录数
- `pageSizeOptions` (Array): 每页记录数选项，默认 [15, 20, 50, 100]

**Events:**
- `page-change`: 页码变化时触发，参数为新页码
- `page-size-change`: 每页记录数变化时触发，参数为新的每页记录数

**使用示例:**
```vue
<PaginationComponent
  :current-page="1"
  :page-size="20"
  :total-records="82"
  @page-change="handlePageChange"
  @page-size-change="handlePageSizeChange"
/>
```

### 2. DataTable（数据表格组件）

用于展示数据列表，支持斑马纹样式、排序、行点击等功能。

**Props:**
- `columns` (Array, required): 列配置
  - `key`: 列的键名
  - `label`: 列的显示名称
  - `width`: 列宽（可选）
  - `sortable`: 是否可排序（可选）
  - `formatter`: 格式化函数（可选）
- `data` (Array, required): 数据数组
- `rowKey` (String|Function): 行的唯一标识，默认 'id'
- `emptyText` (String): 无数据时的提示文本

**Events:**
- `row-click`: 行点击时触发，参数为行数据
- `sort-change`: 排序变化时触发，参数为 { key, order }

**Slots:**
- `cell-{columnKey}`: 自定义单元格内容

**使用示例:**
```vue
<DataTable 
  :columns="columns" 
  :data="tableData"
  @row-click="handleRowClick"
>
  <template #cell-status="{ value }">
    <span :class="getStatusClass(value)">{{ value }}</span>
  </template>
</DataTable>
```

### 3. TabsComponent（标签页组件）

用于多标签页内容展示，采用murex红色主题。

**Props:**
- `tabs` (Array, required): 标签页配置
  - `key`: 标签页的键名
  - `label`: 标签页的显示名称
- `modelValue` (String): 当前激活的标签页键名（支持v-model）

**Events:**
- `update:modelValue`: 激活标签页变化时触发
- `tab-change`: 标签页切换时触发，参数为新的标签页键名

**Slots:**
- 动态slot，名称为标签页的key

**使用示例:**
```vue
<TabsComponent :tabs="tabs" v-model="activeTab">
  <template #info>
    <div>交易信息内容</div>
  </template>
  <template #events>
    <div>事件信息内容</div>
  </template>
</TabsComponent>
```

### 4. LoadingSpinner（加载动画组件）

用于显示加载状态。

**Props:**
- `fullscreen` (Boolean): 是否全屏显示，默认 false
- `text` (String): 加载提示文本，默认 '加载中...'
- `size` (String): 加载动画大小，默认 '40px'

**使用示例:**
```vue
<LoadingSpinner :fullscreen="false" text="加载中..." size="40px" />
```

### 5. MessageAlert（消息提示组件）

用于显示成功、错误、警告、信息等提示消息。

**Props:**
- `type` (String): 消息类型，可选值：'success', 'error', 'warning', 'info'
- `title` (String): 消息标题（可选）
- `message` (String, required): 消息内容
- `duration` (Number): 自动关闭时间（毫秒），默认 3000，设为 0 则不自动关闭
- `closable` (Boolean): 是否可手动关闭，默认 true
- `modelValue` (Boolean): 是否显示（支持v-model）

**Events:**
- `update:modelValue`: 显示状态变化时触发
- `close`: 关闭时触发

**使用示例:**
```vue
<MessageAlert 
  type="success" 
  title="成功" 
  message="操作成功完成！" 
  v-model="showMessage"
/>
```

## 样式主题

所有组件采用murex风格设计，主要特点：

- **主色调**: 红色 (#D32F2F)
- **表格**: 斑马纹样式（白色和浅灰色交替）
- **标签页**: 选中标签为红色背景，未选中为灰色
- **按钮**: 主要按钮为红色，次要按钮为白色
- **交互**: 悬停效果使用红色高亮

## 查看演示

访问 `/demo` 路由可以查看所有组件的演示效果。

## 导入方式

```javascript
// 导入单个组件
import { PaginationComponent } from '@/components'

// 导入多个组件
import { 
  PaginationComponent, 
  DataTable, 
  TabsComponent 
} from '@/components'
```
