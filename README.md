# Settlement Operation Guide System

操作指导系统 - 用于支持交易确认书的查询、状态跟踪和操作指引

## 🌐 在线演示

**部署到公共网站**: 查看 [快速部署指南](./QUICK_DEPLOY.md)

- 前端: `https://your-app.railway.app`
- API 文档: `https://your-backend.railway.app/docs`

## 🚀 快速部署

想要将项目部署到公共网站？只需运行：

```bash
# Windows
deploy.bat

# Mac/Linux
chmod +x deploy.sh
./deploy.sh
```

详细说明请查看：
- [快速部署指南](./QUICK_DEPLOY.md) - 10分钟快速上线
- [Railway 部署详细指南](./RAILWAY_DEPLOYMENT.md) - 完整部署文档
- [部署配置总结](./DEPLOYMENT_SUMMARY.md) - 配置文件说明

## 项目结构

```
.
├── backend/                 # Python后端
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   ├── repositories/  # 数据访问层
│   │   ├── services/      # 业务逻辑层
│   │   ├── schemas/       # Pydantic模式
│   │   ├── config.py      # 配置
│   │   ├── database.py    # 数据库连接
│   │   └── main.py        # 应用入口
│   ├── tests/             # 测试
│   ├── requirements.txt   # Python依赖
│   └── pytest.ini         # Pytest配置
│
└── frontend/               # Vue.js前端
    ├── src/               # 源代码
    │   ├── api/          # API客户端
    │   ├── assets/       # 静态资源
    │   ├── components/   # Vue组件
    │   ├── router/       # 路由配置
    │   ├── stores/       # Pinia状态管理
    │   ├── views/        # 页面视图
    │   ├── App.vue       # 根组件
    │   └── main.js       # 应用入口
    ├── package.json       # Node依赖
    └── vite.config.js     # Vite配置
```

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **测试**: Pytest + Hypothesis

### 前端
- **框架**: Vue.js 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 快速开始

### 后端设置

1. 创建虚拟环境并安装依赖：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接
```

3. 启动开发服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. 运行测试：
```bash
pytest
```

### 前端设置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 运行测试：
```bash
npm test
```

## 数据库设置

1. 创建PostgreSQL数据库：
```sql
CREATE DATABASE settlement_operation_guide;
CREATE DATABASE settlement_operation_guide_test;
```

2. 运行数据库迁移（待实现）：
```bash
cd backend
alembic upgrade head
```

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 代码风格
- Python: 遵循 PEP 8
- JavaScript: 使用 ESLint

### 测试策略
- 单元测试：测试具体示例和边界情况
- 属性测试：使用 Hypothesis 验证通用属性
- 集成测试：测试完整的请求-响应流程

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- test: 测试相关
- refactor: 重构代码

## 许可证

内部项目
