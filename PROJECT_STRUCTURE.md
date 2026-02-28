# Project Structure Overview

## 项目架构说明

本项目采用前后端分离架构，后端使用Python FastAPI，前端使用Vue.js 3。

## 目录结构

### 后端 (backend/)

```
backend/
├── app/                        # 应用主目录
│   ├── __init__.py            # 包初始化
│   ├── main.py                # FastAPI应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── api/                   # API路由层
│   │   └── __init__.py
│   ├── models/                # SQLAlchemy数据模型
│   │   └── __init__.py
│   ├── repositories/          # 数据访问层（Repository模式）
│   │   └── __init__.py
│   ├── services/              # 业务逻辑层
│   │   └── __init__.py
│   └── schemas/               # Pydantic请求/响应模式
│       └── __init__.py
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # Pytest配置和fixtures
│   └── test_setup.py         # 设置验证测试
├── requirements.txt           # Python依赖
├── pytest.ini                # Pytest配置
├── setup.py                  # 安装脚本
└── .env.example              # 环境变量示例
```

### 前端 (frontend/)

```
frontend/
├── src/                       # 源代码目录
│   ├── main.js               # 应用入口
│   ├── App.vue               # 根组件
│   ├── api/                  # API客户端
│   │   └── client.js         # Axios配置
│   ├── assets/               # 静态资源
│   │   └── main.css          # 全局样式
│   ├── components/           # 可复用组件
│   │   └── .gitkeep
│   ├── router/               # Vue Router配置
│   │   └── index.js
│   ├── stores/               # Pinia状态管理
│   │   └── index.js
│   └── views/                # 页面视图
│       └── HomeView.vue
├── index.html                # HTML入口
├── package.json              # Node.js依赖
├── vite.config.js            # Vite配置
└── setup.sh                  # 安装脚本
```

## 技术栈详情

### 后端技术栈
- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **PostgreSQL**: 关系型数据库
- **Pydantic**: 数据验证和设置管理
- **Pytest**: 测试框架
- **Hypothesis**: 基于属性的测试库

### 前端技术栈
- **Vue.js 3**: 渐进式JavaScript框架
- **Vite**: 下一代前端构建工具
- **Vue Router**: 官方路由管理器
- **Pinia**: Vue状态管理库
- **Axios**: HTTP客户端

## 设计模式

### 后端架构模式
1. **三层架构**:
   - API层: 处理HTTP请求和响应
   - 服务层: 业务逻辑处理
   - 数据访问层: 数据库操作

2. **Repository模式**: 
   - 封装数据访问逻辑
   - 提供统一的数据操作接口

3. **依赖注入**:
   - 使用FastAPI的依赖注入系统
   - 便于测试和维护

### 前端架构模式
1. **组件化开发**:
   - 可复用的Vue组件
   - 单文件组件(SFC)

2. **状态管理**:
   - 使用Pinia管理全局状态
   - 模块化的store设计

3. **路由管理**:
   - Vue Router实现页面导航
   - 支持路由守卫和懒加载

## 配置说明

### 后端配置
- `.env`: 环境变量配置（不提交到版本控制）
- `.env.example`: 环境变量模板
- `pytest.ini`: Pytest测试配置

### 前端配置
- `vite.config.js`: Vite构建配置
- `package.json`: 项目元数据和依赖

## 测试策略

### 单元测试
- 测试具体功能和边界情况
- 使用Pytest标记: `@pytest.mark.unit`

### 属性测试
- 使用Hypothesis验证通用属性
- 使用Pytest标记: `@pytest.mark.property`

### 集成测试
- 测试完整的请求-响应流程
- 使用Pytest标记: `@pytest.mark.integration`

## 开发工作流

1. **后端开发**:
   ```bash
   cd backend
   python setup.py  # 安装依赖
   uvicorn app.main:app --reload  # 启动开发服务器
   pytest  # 运行测试
   ```

2. **前端开发**:
   ```bash
   cd frontend
   npm install  # 安装依赖
   npm run dev  # 启动开发服务器
   npm test  # 运行测试
   ```

## 下一步

根据tasks.md中的实施计划，接下来需要：
1. 实现数据模型和数据库层
2. 实现并发控制机制
3. 实现查询服务
4. 实现事件服务
5. 实现账务服务
6. 实现状态跟踪服务
7. 实现操作指引服务
8. 实现前端页面

详细任务列表请参考 `.kiro/specs/settlement-operation-guide/tasks.md`
