# Railway 部署调试清单

## 当前部署状态

部署 ID: d8be8f16
状态: 显示网络流量但返回 502

## 需要检查的内容

### 1. Build Logs（构建日志）

在 Railway 控制台 → Build Logs 标签，查找：

**应该看到：**
```
✓ Installing dependencies
✓ cd frontend && npm install
✓ cd frontend && npm run build
✓ Build completed
```

**如果看到错误：**
- `npm ERR!` - 依赖安装失败
- `ERROR` - 构建失败
- `frontend/dist not found` - 构建输出目录未创建

**解决方案：**
- 记录完整的错误信息
- 检查是否是内存不足（Railway 免费版有限制）
- 检查是否是网络问题（npm install 超时）

### 2. Deploy Logs（部署日志）

在 Railway 控制台 → Deploy Logs 标签，查找：

**成功启动应该显示：**
```
Starting Settlement Operation Guide
✓ Frontend dist found
Files in frontend/dist:
  index.html
  assets/
Starting Express server...
Server is running on http://0.0.0.0:XXXX
Serving files from: /app/frontend/dist
```

**常见错误：**

#### 错误 A: "frontend/dist not found"
```
✗ Error: frontend/dist not found!
```
**原因：** 构建阶段失败，dist 目录未创建
**解决：** 检查 Build Logs，修复构建错误

#### 错误 B: "Cannot find module 'express'"
```
Error: Cannot find module 'express'
```
**原因：** 根目录的 npm install 失败
**解决：** 在 Railway 设置中触发重新部署

#### 错误 C: "EADDRINUSE"
```
Error: listen EADDRINUSE: address already in use
```
**原因：** 端口冲突（罕见）
**解决：** 重新部署服务

#### 错误 D: 没有任何输出
**原因：** 启动脚本没有执行权限或路径错误
**解决：** 检查 railway.toml 中的 startCommand

### 3. HTTP Logs（HTTP 日志）

在 Railway 控制台 → HTTP Logs 标签：

**如果看到 502：**
- 服务器没有正确启动
- 服务器启动了但崩溃了
- 健康检查失败

**如果看到 404：**
- 服务器运行正常，但路由配置有问题
- 静态文件路径不正确

**如果什么都没有：**
- 请求没有到达你的服务
- DNS 或路由问题

### 4. Railway 设置检查

在 Railway 控制台 → Settings：

**Environment Variables（环境变量）：**
- 不需要设置 PORT（Railway 自动提供）
- 不需要设置 NODE_ENV

**Deploy Settings（部署设置）：**
- Root Directory: 留空（使用项目根目录）
- Build Command: 留空（使用 nixpacks.toml）
- Start Command: 留空（使用 railway.toml）
- Watch Paths: 留空

**如果你手动设置了这些，请清空它们！**

## 快速修复步骤

### 方案 1: 完全重新部署

1. 在 Railway 控制台，点击服务
2. 点击右上角的 "..." 菜单
3. 选择 "Redeploy"
4. 等待 5-10 分钟
5. 查看所有日志标签

### 方案 2: 删除并重新创建服务

1. 在 Railway 项目中删除当前服务
2. 点击 "New Service"
3. 选择 "GitHub Repo"
4. 选择 `settlement-operation-guide` 仓库
5. 等待自动部署

### 方案 3: 使用 Railway CLI 调试

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接到项目
railway link

# 查看日志
railway logs

# 查看环境变量
railway variables

# 手动触发部署
railway up
```

## 本地测试

在推送到 Railway 之前，先在本地验证：

```bash
# Windows
build.bat
node server.js

# Linux/Mac
bash build.sh
node server.js
```

然后访问 http://localhost:3000

如果本地可以访问，说明代码没问题，是 Railway 配置问题。

## 检查前端构建输出

本地构建后，检查 `frontend/dist` 目录：

```bash
# 应该包含：
frontend/dist/
  ├── index.html          # 主 HTML 文件
  ├── assets/             # 静态资源
  │   ├── index-xxx.js    # 打包的 JS
  │   └── index-xxx.css   # 打包的 CSS
  └── favicon.ico         # 图标（可选）
```

如果缺少 `index.html`，构建失败了。

## Railway 平台限制

免费版限制：
- 内存: 512MB
- CPU: 共享
- 构建时间: 最多 10 分钟
- 运行时间: 无限制（但不活跃会休眠）

如果构建超时或内存不足：
- 简化前端依赖
- 使用更小的 Node.js 版本
- 考虑升级到付费计划

## 替代部署方案

如果 Railway 持续失败，可以尝试：

### 方案 A: 分离部署
- 前端部署到 Vercel/Netlify（免费且稳定）
- 后端保持在 Railway

### 方案 B: 使用 Docker
- 创建 Docker 镜像
- 推送到 Docker Hub
- Railway 从 Docker 镜像部署

### 方案 C: 使用其他平台
- Render.com（类似 Railway）
- Fly.io（更灵活）
- Heroku（经典选择）

## 需要提供的调试信息

如果问题持续，请提供：

1. **完整的 Build Logs**（从开始到结束）
2. **完整的 Deploy Logs**（从开始到结束）
3. **HTTP Logs 截图**（显示 502 错误）
4. **Railway Settings 截图**（Environment 和 Deploy 部分）
5. **本地测试结果**（是否能在本地运行）

## 联系支持

Railway 支持渠道：
- Discord: https://discord.gg/railway
- 文档: https://docs.railway.app
- 状态页: https://status.railway.app

## 最后的建议

如果所有方法都失败了，最简单的方案是：

1. **只部署前端到 Vercel**
   - 在 Vercel 中导入 GitHub 仓库
   - Root Directory 设置为 `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - 几分钟内就能部署成功

2. **后端暂时不部署**
   - 先让前端可以访问
   - 后端可以稍后再处理

这样至少可以让用户看到界面，即使后端功能暂时不可用。
