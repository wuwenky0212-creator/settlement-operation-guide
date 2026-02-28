# Railway 部署失败修复指南

## 问题原因

Railway 尝试部署整个项目，但配置文件指向了后端，导致启动命令找不到。

## 解决方案

### 方案一：删除当前服务，分别部署前后端（推荐）

1. **删除当前的 web 服务**
   - 在 Railway 项目中，点击 "web" 服务
   - 点击 "Settings" → "Danger" → "Remove Service from Project"

2. **部署后端服务**
   - 点击 "New" → "GitHub Repo"
   - 选择 `settlement-operation-guide` 仓库
   - 在 Settings 中配置：
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - 添加环境变量：
     ```
     ENVIRONMENT=production
     CORS_ORIGINS=*
     ```

3. **添加数据库**
   - 点击 "New" → "Database" → "Add PostgreSQL"
   - Railway 会自动设置 DATABASE_URL

4. **部署前端服务**
   - 点击 "New" → "GitHub Repo"
   - 选择同一个仓库
   - 在 Settings 中配置：
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`
   - 添加环境变量（等后端部署完成后）：
     ```
     VITE_API_BASE_URL=https://your-backend-url.railway.app
     ```

### 方案二：修复当前服务（快速）

1. **点击 "Settings" 标签**

2. **配置服务设置**
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. **保存并重新部署**
   - 点击 "Deployments" 标签
   - 点击 "Redeploy" 或 "Deploy"

4. **之后再添加后端服务**
   - 按照方案一的步骤 2 添加后端

## 推荐流程

建议使用**方案一**，因为：
- ✅ 前后端分离，更清晰
- ✅ 可以独立扩展和监控
- ✅ 更容易调试和维护
- ✅ 符合微服务架构

## 下一步

选择一个方案后：
1. 完成配置
2. 等待部署成功
3. 获取前后端 URL
4. 更新前端环境变量中的后端 URL
5. 测试功能

## 需要帮助？

如果遇到问题，查看：
- Railway 部署日志
- 浏览器控制台错误
- 网络请求状态
