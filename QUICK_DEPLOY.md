# 快速部署到公共网站

## 🎯 目标

将结算操作指引系统部署到公共网站，让任何人都可以通过互联网访问。

## 🚀 最快部署方式（推荐）

### 方法一：使用 Railway（最简单）

**时间：约 10 分钟**

1. **准备 GitHub 仓库**
   
   ```bash
   # Windows 用户
   deploy.bat
   
   # Mac/Linux 用户
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **部署到 Railway**
   
   - 访问 https://railway.app
   - 使用 GitHub 账号登录
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择你的仓库 `settlement-operation-guide`
   - Railway 会自动检测并部署

3. **配置数据库**
   
   - 在项目中点击 "New" → "Database" → "Add PostgreSQL"
   - Railway 会自动配置数据库连接

4. **获取访问链接**
   
   - 部署完成后，点击服务查看 URL
   - 例如：`https://settlement-guide.railway.app`

### 方法二：使用 Vercel（前端）+ Railway（后端）

**前端部署到 Vercel（更快的 CDN）**

1. 访问 https://vercel.com
2. 导入 GitHub 仓库
3. 设置 Root Directory 为 `frontend`
4. 添加环境变量：`VITE_API_BASE_URL=https://your-backend.railway.app`
5. 部署

**后端部署到 Railway**

按照方法一的步骤部署后端

## 📋 详细步骤

详细的部署指南请查看：[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

## 🌐 部署后的访问地址

部署成功后，你将获得：

- **前端网站**: `https://your-app.railway.app` 或 `https://your-app.vercel.app`
- **后端 API**: `https://your-backend.railway.app`
- **API 文档**: `https://your-backend.railway.app/docs`

## 💰 费用说明

### Railway
- **免费额度**: $5/月
- **超出后**: 按使用量付费（约 $0.000463/GB-hour）
- **预估成本**: 小型项目通常在免费额度内

### Vercel
- **免费额度**: 
  - 100GB 带宽/月
  - 无限部署
- **超出后**: 按使用量付费

## ✅ 部署检查清单

- [ ] 代码已推送到 GitHub
- [ ] Railway 项目已创建
- [ ] 数据库已添加并配置
- [ ] 环境变量已设置
- [ ] 前端可以访问
- [ ] 后端 API 可以访问
- [ ] 前后端可以正常通信

## 🔧 常见问题

### 1. 前端无法连接后端

**解决方案**:
- 检查 `VITE_API_BASE_URL` 环境变量
- 确认后端 CORS 配置正确
- 查看浏览器控制台的错误信息

### 2. 数据库连接失败

**解决方案**:
- 确认 PostgreSQL 已添加到项目
- 检查 `DATABASE_URL` 环境变量
- 运行数据库迁移：`railway run alembic upgrade head`

### 3. 构建失败

**解决方案**:
- 查看 Railway 的部署日志
- 确认所有依赖都在 requirements.txt 中
- 检查 Python 版本是否兼容

## 📞 获取帮助

- Railway 文档: https://docs.railway.app
- Vercel 文档: https://vercel.com/docs
- 项目 Issues: 在 GitHub 仓库中创建 issue

## 🎉 部署成功后

分享你的网站链接：
```
🌐 我的结算操作指引系统已上线！
访问地址：https://your-app.railway.app
```

## 下一步

- [ ] 配置自定义域名
- [ ] 设置 HTTPS（自动提供）
- [ ] 配置监控和日志
- [ ] 添加用户认证
- [ ] 设置自动备份
