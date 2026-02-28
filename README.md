# Settlement Operation Guide System

结算操作指南系统 - 一个用于管理和展示结算流程的 Web 应用。

## 🚀 快速开始

### 本地开发

```bash
# 1. 安装依赖
npm install
cd frontend && npm install && cd ..

# 2. 构建前端
cd frontend && npm run build && cd ..

# 3. 启动服务器
node server.js

# 4. 访问应用
# 打开浏览器访问 http://localhost:3000
```

或者使用快捷脚本：
```bash
test_local.bat
```

### 前端开发模式

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

## 📦 项目结构

```
settlement-operation-guide/
├── frontend/           # Vue 3 前端应用
│   ├── src/           # 源代码
│   ├── dist/          # 构建输出（自动生成）
│   └── package.json   # 前端依赖
├── backend/           # FastAPI 后端应用
│   ├── app/           # 应用代码
│   ├── tests/         # 测试文件
│   └── requirements.txt
├── server.js          # Express 静态文件服务器
├── package.json       # 根目录依赖
├── nixpacks.toml      # Railway 构建配置
└── railway.toml       # Railway 部署配置
```

## 🌐 部署

### Railway 部署（推荐）

1. **连接 GitHub 仓库**
   - 访问 [Railway](https://railway.app)
   - 创建新项目，选择 GitHub 仓库

2. **配置设置**
   - Root Directory: 留空
   - 其他设置保持默认（使用项目配置文件）

3. **自动部署**
   - 推送代码到 main 分支会自动触发部署

详细说明：[RAILWAY_SETUP_GUIDE.md](./RAILWAY_SETUP_GUIDE.md)

## 🛠️ 技术栈

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- Vue Router - 路由管理
- Pinia - 状态管理
- Vite - 构建工具
- Axios - HTTP 客户端

### 后端
- FastAPI - 现代 Python Web 框架
- SQLAlchemy - ORM
- Alembic - 数据库迁移
- PostgreSQL - 数据库

### 部署
- Express - 静态文件服务器
- Railway - 部署平台
- Nixpacks - 构建系统

## 📝 开发指南

### 前端开发

```bash
cd frontend
npm run dev      # 开发服务器
npm run build    # 生产构建
npm run test     # 运行测试
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API 文档: http://localhost:8000/docs
```

## 🔧 配置文件说明

- `package.json` - Node.js 依赖和脚本
- `nixpacks.toml` - Railway 构建流程配置
- `railway.toml` - Railway 部署配置
- `.npmrc` - npm 配置
- `.railwayignore` - Railway 忽略文件

## 📚 文档

- [Railway 设置指南](./RAILWAY_SETUP_GUIDE.md) - Railway 部署配置说明
- [项目结构说明](./PROJECT_STRUCTURE.md) - 详细的项目结构
- [用户手册](./USER_MANUAL.md) - 系统使用说明
- [FAQ](./FAQ.md) - 常见问题

## 🧪 测试

### 前端测试
```bash
cd frontend
npm run test
```

### 后端测试
```bash
cd backend
pytest
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请创建 Issue 或联系项目维护者。
