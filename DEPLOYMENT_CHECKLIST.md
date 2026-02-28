# 🚀 部署检查清单

使用此清单确保部署过程顺利完成。

## 📋 部署前准备

### 1. 账号准备
- [ ] GitHub 账号已创建
- [ ] Railway 账号已创建（使用 GitHub 登录）
- [ ] Git 已安装并配置

### 2. 代码准备
- [ ] 所有代码已提交
- [ ] 所有测试通过
- [ ] 依赖文件已更新（requirements.txt, package.json）
- [ ] 环境变量示例文件已创建

### 3. 配置文件检查
- [ ] `railway.json` 已创建
- [ ] `nixpacks.toml` 已创建
- [ ] `Procfile` 已创建
- [ ] `runtime.txt` 已创建
- [ ] `frontend/.env.example` 已创建

## 🔧 GitHub 设置

### 1. 创建仓库
- [ ] 在 GitHub 上创建新仓库
- [ ] 仓库名称：`settlement-operation-guide`
- [ ] 设置为 Public 或 Private
- [ ] 不要初始化 README

### 2. 推送代码
- [ ] 本地 Git 仓库已初始化
- [ ] 远程仓库已添加
- [ ] 代码已推送到 main 分支

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/settlement-operation-guide.git
git branch -M main
git push -u origin main
```

## 🚂 Railway 后端部署

### 1. 创建项目
- [ ] 访问 https://railway.app
- [ ] 使用 GitHub 登录
- [ ] 点击 "New Project"
- [ ] 选择 "Deploy from GitHub repo"
- [ ] 选择 `settlement-operation-guide` 仓库

### 2. 配置后端服务
- [ ] 服务名称：`backend`
- [ ] Root Directory：`backend`
- [ ] Build Command：`pip install -r requirements.txt`
- [ ] Start Command：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. 添加数据库
- [ ] 点击 "New" → "Database" → "Add PostgreSQL"
- [ ] 等待数据库创建完成
- [ ] 确认 `DATABASE_URL` 环境变量已自动设置

### 4. 配置环境变量
- [ ] `DATABASE_URL` - 自动设置
- [ ] `ENVIRONMENT=production`
- [ ] `CORS_ORIGINS=*` （临时，后续更新为前端域名）

### 5. 运行数据库迁移
- [ ] 安装 Railway CLI：`npm i -g @railway/cli`
- [ ] 登录：`railway login`
- [ ] 链接项目：`railway link`
- [ ] 运行迁移：`railway run alembic upgrade head`

### 6. 验证部署
- [ ] 后端服务状态为 "Active"
- [ ] 访问后端 URL 显示欢迎信息
- [ ] 访问 `/docs` 显示 API 文档
- [ ] 记录后端 URL：`_______________________`

## 🎨 Railway 前端部署

### 1. 创建前端服务
- [ ] 在同一项目中点击 "New Service"
- [ ] 选择 "GitHub Repo"
- [ ] 选择同一个仓库

### 2. 配置前端服务
- [ ] 服务名称：`frontend`
- [ ] Root Directory：`frontend`
- [ ] Build Command：`npm install && npm run build`
- [ ] Start Command：`npm run preview -- --host 0.0.0.0 --port $PORT`

### 3. 配置环境变量
- [ ] `VITE_API_BASE_URL=https://your-backend.railway.app`
  （替换为实际的后端 URL）

### 4. 验证部署
- [ ] 前端服务状态为 "Active"
- [ ] 访问前端 URL 显示应用界面
- [ ] 记录前端 URL：`_______________________`

## 🔗 连接前后端

### 1. 更新 CORS 配置
- [ ] 在后端服务的环境变量中更新：
  ```
  CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:5173
  ```
- [ ] 重新部署后端服务

### 2. 测试连接
- [ ] 打开前端网站
- [ ] 打开浏览器开发者工具（F12）
- [ ] 查看网络请求
- [ ] 确认 API 请求成功
- [ ] 测试主要功能：
  - [ ] 交易汇总列表加载
  - [ ] 交易详情查看
  - [ ] 现金流信息查看
  - [ ] 进度跟踪显示

## ✅ 功能验证

### 1. 交易汇总功能
- [ ] 页面加载正常
- [ ] 可以查询交易
- [ ] 分页功能正常
- [ ] 可以点击查看详情

### 2. 交易详情功能
- [ ] 详情弹窗打开正常
- [ ] 操作指引显示正确
- [ ] 标签页切换正常
- [ ] 交易信息显示完整

### 3. 进度跟踪功能
- [ ] 交易生命周期进度显示
- [ ] 结算支付进度显示
- [ ] 卡片式布局正常
- [ ] 状态颜色正确

### 4. 现金流信息功能
- [ ] 现金流列表显示
- [ ] 数据加载正常
- [ ] 进度跟踪显示

## 🎯 性能检查

- [ ] 首页加载时间 < 3秒
- [ ] API 响应时间 < 500ms
- [ ] 图片和资源加载正常
- [ ] 移动端显示正常

## 🔒 安全检查

- [ ] HTTPS 已启用（Railway 自动提供）
- [ ] CORS 配置正确
- [ ] 敏感信息不在代码中
- [ ] 环境变量已正确设置

## 📊 监控设置

- [ ] Railway 监控已启用
- [ ] 日志可以正常查看
- [ ] 错误追踪已配置

## 📝 文档更新

- [ ] README.md 已更新部署信息
- [ ] 访问 URL 已记录
- [ ] 部署日期已记录：`_______________________`
- [ ] 部署人员：`_______________________`

## 🎉 部署完成

恭喜！你的应用已成功部署到公共网站。

### 访问信息

- **前端网站**: `_______________________`
- **后端 API**: `_______________________`
- **API 文档**: `_______________________/docs`

### 分享你的成果

```
🌐 结算操作指引系统已上线！
📱 访问地址：https://your-app.railway.app
📖 API 文档：https://your-backend.railway.app/docs
🚀 技术栈：Vue.js + FastAPI + PostgreSQL
```

## 📞 遇到问题？

- 查看 [故障排查指南](./RAILWAY_DEPLOYMENT.md#故障排查)
- 查看 Railway 部署日志
- 在 GitHub 仓库创建 Issue
- 访问 Railway Discord 社区

## 🔄 后续维护

- [ ] 设置自动备份
- [ ] 配置自定义域名
- [ ] 设置监控告警
- [ ] 定期更新依赖
- [ ] 定期检查日志

---

**部署日期**: `_______________________`  
**部署人员**: `_______________________`  
**版本号**: `v1.0.0`
