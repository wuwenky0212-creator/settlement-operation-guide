# Railway 502 错误修复指南

## 问题诊断

502 Bad Gateway 错误通常表示：
1. 应用没有正确启动
2. 应用没有监听正确的端口
3. 构建过程失败
4. 健康检查失败

## 修复步骤

### 1. 检查 Railway 设置

在 Railway 项目设置中确认：

**Settings → Environment**
- 不需要设置 PORT（Railway 会自动提供）
- 确保没有冲突的环境变量

**Settings → Deploy**
- Build Command: 留空（使用 package.json 中的脚本）
- Start Command: `npm start`
- Watch Paths: 留空

### 2. 检查构建日志

在 Railway 控制台：
1. 点击最新的部署
2. 查看 "Build Logs" 标签
3. 确认以下步骤都成功：
   ```
   ✓ Installing dependencies (npm install)
   ✓ Building frontend (npm run build)
   ✓ Creating frontend/dist directory
   ```

如果构建失败，查看错误信息并修复。

### 3. 检查部署日志

在 "Deploy Logs" 标签中查找：

**成功的启动日志应该显示：**
```
Server is running on http://0.0.0.0:XXXX
Serving files from: /app/frontend/dist
```

**常见错误：**

#### 错误 1: "frontend/dist directory not found"
```
Error: frontend/dist directory not found!
Please run "npm run build" first
```

**解决方案：**
- 构建过程失败
- 检查 Build Logs 查看构建错误
- 可能是前端依赖安装失败

#### 错误 2: "EADDRINUSE"
```
Error: listen EADDRINUSE: address already in use
```

**解决方案：**
- 端口冲突（不太可能在 Railway 上发生）
- 重新部署服务

#### 错误 3: "Cannot find module"
```
Error: Cannot find module 'express'
```

**解决方案：**
- 依赖安装失败
- 确保 package.json 中有 express
- 触发重新部署

### 4. 测试健康检查

部署成功后，测试健康检查端点：

```bash
curl https://your-app.railway.app/health
```

应该返回：
```json
{"status":"ok","timestamp":"2026-02-28T..."}
```

### 5. 检查 HTTP 日志

在 "HTTP Logs" 标签中：
- 查看是否有请求到达
- 检查响应状态码
- 确认路由是否正确

## 重新部署步骤

### 方法 1: 通过 Git 推送（推荐）

```bash
# 1. 提交更改
git add .
git commit -m "Fix Railway deployment configuration"

# 2. 推送到 GitHub
git push origin main

# 3. Railway 会自动检测并重新部署
```

或者使用提供的脚本：
```bash
deploy_railway.bat
```

### 方法 2: 手动触发重新部署

在 Railway 控制台：
1. 进入你的项目
2. 点击服务
3. 点击右上角的 "Deploy" 按钮
4. 选择 "Redeploy"

### 方法 3: 从头开始

如果问题持续存在：

1. **删除现有服务**
   - 在 Railway 中删除当前服务
   
2. **创建新服务**
   - New Service → GitHub Repo
   - 选择你的仓库
   
3. **等待自动配置**
   - Railway 会自动检测 Node.js 项目
   - 自动运行 npm install 和 npm start

## 验证清单

部署成功后，验证以下内容：

- [ ] 构建日志显示 "Build successful"
- [ ] 部署日志显示 "Server is running"
- [ ] 健康检查端点返回 200 OK
- [ ] 访问根路径显示前端页面
- [ ] 浏览器控制台没有错误

## 本地测试

在推送到 Railway 之前，先在本地测试：

```bash
# 1. 安装依赖
npm install

# 2. 构建前端
npm run build

# 3. 启动服务器
npm start

# 4. 访问 http://localhost:3000
```

如果本地工作正常，Railway 上也应该能正常工作。

## 常见问题

### Q: 为什么本地可以运行，Railway 上不行？

A: 可能的原因：
1. 环境变量不同
2. Node.js 版本不同（检查 package.json 中的 engines）
3. 构建过程在 Railway 上失败
4. 文件路径问题（Windows vs Linux）

### Q: 如何查看详细的错误信息？

A: 在 Railway 控制台：
1. 点击服务
2. 查看 "Deployments" 标签
3. 点击最新的部署
4. 查看所有日志标签（Build, Deploy, HTTP）

### Q: 部署需要多长时间？

A: 通常：
- 构建: 2-5 分钟
- 部署: 30 秒 - 1 分钟
- 总计: 3-6 分钟

### Q: 如何回滚到之前的版本？

A: 在 Railway 控制台：
1. 进入 "Deployments" 标签
2. 找到之前成功的部署
3. 点击 "Redeploy"

## 需要更多帮助？

如果问题仍然存在：

1. **检查 Railway 状态**
   - https://status.railway.app
   
2. **查看 Railway 文档**
   - https://docs.railway.app
   
3. **Railway Discord 社区**
   - https://discord.gg/railway
   
4. **提供以下信息寻求帮助**
   - 完整的构建日志
   - 完整的部署日志
   - package.json 内容
   - 错误截图

## 更新记录

- 2026-02-28: 添加 postinstall 脚本自动构建前端
- 2026-02-28: 添加健康检查端点
- 2026-02-28: 改进错误处理和日志输出
- 2026-02-28: 添加 Railway 和 Nixpacks 配置文件
