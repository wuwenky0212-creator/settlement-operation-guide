# Railway 部署指南

本指南将帮助你将项目部署到 Railway，使其可以在公共网站上访问。

## 前提条件

1. GitHub 账号
2. Railway 账号（可以使用 GitHub 账号登录）
3. Git 已安装并配置

## 部署步骤

### 第一步：准备 GitHub 仓库

1. **初始化 Git 仓库**（如果还没有）

```bash
git init
git add .
git commit -m "Initial commit: Settlement Operation Guide System"
```

2. **在 GitHub 上创建新仓库**

- 访问 https://github.com/new
- 仓库名称：`settlement-operation-guide`
- 设置为 Public（公开）或 Private（私有）
- 不要初始化 README、.gitignore 或 license

3. **推送代码到 GitHub**

```bash
git remote add origin https://github.com/YOUR_USERNAME/settlement-operation-guide.git
git branch -M main
git push -u origin main
```

### 第二步：部署后端到 Railway

1. **访问 Railway**
   - 打开 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你刚才创建的仓库 `settlement-operation-guide`

3. **配置后端服务**
   - Railway 会自动检测到 Python 项目
   - 点击项目进入设置

4. **添加环境变量**
   
   在 "Variables" 标签页添加以下环境变量：
   
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ENVIRONMENT=production
   CORS_ORIGINS=*
   ```
   
   注意：Railway 会自动提供 PostgreSQL 数据库，你可以：
   - 点击 "New" → "Database" → "Add PostgreSQL"
   - Railway 会自动设置 DATABASE_URL 环境变量

5. **配置构建和启动命令**
   
   在 "Settings" 标签页：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. **部署**
   - 点击 "Deploy"
   - 等待部署完成
   - 记录后端 URL（例如：`https://your-backend.railway.app`）

### 第三步：部署前端到 Railway

1. **创建第二个服务**
   - 在同一个项目中，点击 "New Service"
   - 选择 "GitHub Repo"
   - 选择同一个仓库

2. **配置前端服务**
   
   在 "Settings" 标签页：
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. **添加环境变量**
   
   ```
   VITE_API_BASE_URL=https://your-backend.railway.app
   ```

4. **更新前端 API 配置**
   
   需要修改 `frontend/src/api/client.js` 以使用环境变量：

   ```javascript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成
   - 记录前端 URL（例如：`https://your-frontend.railway.app`）

### 第四步：配置 CORS

更新后端的 CORS 配置以允许前端域名访问。

在 `backend/app/main.py` 中：

```python
# 从环境变量获取允许的源
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

然后在 Railway 后端服务的环境变量中设置：

```
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:5173
```

### 第五步：初始化数据库

1. **运行数据库迁移**
   
   在 Railway 后端服务的 "Settings" → "Deploy" 中添加：
   
   ```
   Release Command: cd backend && alembic upgrade head
   ```

2. **或者通过 Railway CLI**
   
   ```bash
   # 安装 Railway CLI
   npm i -g @railway/cli
   
   # 登录
   railway login
   
   # 链接到项目
   railway link
   
   # 运行迁移
   railway run alembic upgrade head
   ```

## 访问你的应用

部署完成后，你可以通过以下 URL 访问：

- **前端**: `https://your-frontend.railway.app`
- **后端 API**: `https://your-backend.railway.app/docs`

## 自动部署

配置完成后，每次你推送代码到 GitHub，Railway 会自动：
1. 检测到代码变更
2. 重新构建和部署
3. 更新线上服务

## 故障排查

### 1. 后端无法启动

检查日志：
- 在 Railway 项目中点击后端服务
- 查看 "Deployments" 标签页的日志
- 确认所有环境变量都已正确设置

### 2. 前端无法连接后端

- 确认 `VITE_API_BASE_URL` 环境变量正确设置
- 确认后端 CORS 配置包含前端域名
- 检查浏览器控制台的网络请求

### 3. 数据库连接失败

- 确认 PostgreSQL 数据库已添加到项目
- 确认 `DATABASE_URL` 环境变量已自动设置
- 检查数据库迁移是否成功运行

## 成本说明

Railway 提供：
- **免费额度**: $5/月的免费使用额度
- **按使用付费**: 超出免费额度后按实际使用付费
- **休眠策略**: 可以配置服务在不活跃时自动休眠以节省费用

## 替代方案

如果你想使用其他平台：

### Vercel（前端）+ Railway（后端）
- 前端部署到 Vercel（更快的 CDN）
- 后端保持在 Railway

### Netlify（前端）+ Railway（后端）
- 前端部署到 Netlify
- 后端保持在 Railway

### Render（全栈）
- 前后端都部署到 Render
- 类似 Railway 的体验

## 下一步

1. 配置自定义域名
2. 设置 HTTPS（Railway 自动提供）
3. 配置监控和日志
4. 设置备份策略

## 需要帮助？

- Railway 文档: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: 在你的仓库中创建 issue
