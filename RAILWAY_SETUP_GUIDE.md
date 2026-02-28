# Railway 正确配置指南

## 当前配置说明

这个项目配置为在 Railway 上部署一个 Node.js 服务，该服务会：
1. 在构建阶段编译前端（Vue + Vite）
2. 使用 Express 提供静态文件服务
3. 支持 Vue Router 的 HTML5 History 模式

## Railway 项目设置

### 方法 1: 让 Railway 自动检测（推荐）

1. **删除所有手动配置**
   - 进入 Railway 项目 → Settings
   - 在 "Deploy" 部分，确保以下字段为空：
     - Root Directory: 留空
     - Build Command: 留空
     - Start Command: 留空
     - Watch Paths: 留空

2. **Railway 会自动使用项目中的配置文件**
   - `nixpacks.toml` - 定义构建步骤
   - `railway.toml` - 定义部署配置
   - `package.json` - 定义依赖和脚本

3. **触发重新部署**
   - 推送代码到 GitHub
   - 或在 Railway 中点击 "Redeploy"

### 方法 2: 手动配置（如果自动检测失败）

如果 Railway 没有正确读取配置文件，手动设置：

**Settings → Deploy:**
- Root Directory: 留空
- Build Command: `cd frontend && npm install && npm run build`
- Start Command: `node server.js`
- Install Command: `npm install`

**Settings → Environment:**
- 不需要添加任何环境变量
- PORT 会由 Railway 自动提供

## 构建流程说明

### 阶段 1: Setup（设置）
```
安装 Node.js 18.x
```

### 阶段 2: Install（安装依赖）
```bash
# 安装根目录依赖（Express）
npm ci --omit=dev || npm install --omit=dev

# 安装前端依赖
cd frontend && npm ci || npm install
```

### 阶段 3: Build（构建）
```bash
# 构建前端
cd frontend && npm run build

# 验证构建结果
test -d frontend/dist && echo '✓ Build successful'
```

### 阶段 4: Start（启动）
```bash
# 启动 Express 服务器
node server.js
```

## 预期的日志输出

### Build Logs（构建日志）

成功的构建日志应该包含：

```
#1 [setup] Installing Node.js 18.x
✓ Setup complete

#2 [install] Installing dependencies
npm ci --omit=dev
added 58 packages
cd frontend && npm ci
added 234 packages
✓ Install complete

#3 [build] Building frontend
cd frontend && npm run build
vite v5.0.11 building for production...
✓ 123 modules transformed
dist/index.html                   0.45 kB
dist/assets/index-abc123.js      145.23 kB
dist/assets/index-abc123.css      12.34 kB
✓ built in 15.23s
✓ Build successful
✓ Build complete
```

### Deploy Logs（部署日志）

成功的部署日志应该包含：

```
==================================================
Settlement Operation Guide Server
==================================================
Node version: v18.x.x
Working directory: /app
Dist path: /app/frontend/dist
PORT: 3000
✓ Frontend dist directory found
✓ index.html found
==================================================
✓ Server is running on http://0.0.0.0:3000
✓ Serving files from: /app/frontend/dist
✓ Health check: http://0.0.0.0:3000/health
==================================================
```

### HTTP Logs（HTTP 日志）

成功部署后，访问网站应该看到：

```
GET / → 200 OK
GET /assets/index-abc123.js → 200 OK
GET /assets/index-abc123.css → 200 OK
GET /health → 200 OK
```

## 常见问题排查

### 问题 1: Build Logs 显示 "npm install failed"

**可能原因：**
- 网络问题
- package.json 中的依赖版本冲突
- 内存不足

**解决方案：**
1. 检查 package.json 中的依赖是否正确
2. 尝试重新部署（可能是临时网络问题）
3. 检查 Railway 的构建日志，查看具体错误信息

### 问题 2: Build Logs 显示 "npm run build failed"

**可能原因：**
- 前端代码有语法错误
- Vite 配置问题
- 依赖版本不兼容

**解决方案：**
1. 在本地运行 `cd frontend && npm run build` 查看错误
2. 修复错误后重新推送
3. 检查 frontend/vite.config.js 配置

### 问题 3: Deploy Logs 显示 "frontend/dist not found"

**可能原因：**
- 构建阶段失败，但没有报错
- 构建输出目录配置错误

**解决方案：**
1. 检查 Build Logs，确认构建成功
2. 检查 frontend/vite.config.js 中的 build.outDir 配置
3. 确认 frontend/package.json 中的 build 脚本正确

### 问题 4: HTTP Logs 显示 502 Bad Gateway

**可能原因：**
- 服务器没有启动
- 服务器启动后崩溃
- 健康检查失败

**解决方案：**
1. 检查 Deploy Logs，确认服务器成功启动
2. 查看是否有错误信息或异常退出
3. 测试健康检查端点：`curl https://your-app.railway.app/health`

### 问题 5: 页面显示但样式丢失

**可能原因：**
- 静态资源路径不正确
- Vite 的 base 配置问题

**解决方案：**
1. 检查浏览器控制台的网络请求
2. 确认 frontend/vite.config.js 中没有设置错误的 base 路径
3. 检查 HTTP Logs 中静态资源的请求状态

## 验证部署成功

部署完成后，执行以下检查：

### 1. 健康检查
```bash
curl https://your-app.railway.app/health
```

应该返回：
```json
{
  "status": "ok",
  "timestamp": "2026-02-28T...",
  "uptime": 123.45,
  "nodeVersion": "v18.x.x"
}
```

### 2. 访问首页
在浏览器中访问：`https://your-app.railway.app`

应该看到前端页面正常显示。

### 3. 检查浏览器控制台
按 F12 打开开发者工具，检查：
- Console 标签：不应该有错误
- Network 标签：所有请求都应该是 200 OK

### 4. 测试路由
访问不同的页面路径，确认 Vue Router 正常工作。

## 本地测试

在推送到 Railway 之前，务必在本地测试：

```bash
# 1. 安装依赖
npm install
cd frontend && npm install && cd ..

# 2. 构建前端
cd frontend && npm run build && cd ..

# 3. 启动服务器
node server.js

# 4. 访问 http://localhost:3000
```

如果本地测试成功，Railway 上应该也能成功。

## 回滚到之前的版本

如果新部署出现问题：

1. 进入 Railway 项目
2. 点击 "Deployments" 标签
3. 找到之前成功的部署（绿色勾号）
4. 点击该部署右侧的 "..." 菜单
5. 选择 "Redeploy"

## 监控和日志

### 实时日志
```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接项目
railway link

# 查看实时日志
railway logs
```

### 查看历史日志
在 Railway 控制台：
1. 点击服务
2. 点击 "Deployments" 标签
3. 选择任意部署
4. 查看 Build Logs、Deploy Logs、HTTP Logs

## 性能优化建议

1. **启用 Gzip 压缩**
   - 在 server.js 中添加 compression 中间件

2. **设置缓存头**
   - 为静态资源设置长期缓存

3. **使用 CDN**
   - 考虑将静态资源上传到 CDN

4. **监控性能**
   - 使用 Railway 的 Metrics 功能
   - 设置告警

## 成本控制

Railway 免费额度：$5/月

节省成本的方法：
1. 配置休眠策略（不活跃时自动休眠）
2. 优化构建时间（减少依赖）
3. 监控使用量

## 需要帮助？

如果遇到问题：
1. 查看本文档的"常见问题排查"部分
2. 检查 Railway 状态页：https://status.railway.app
3. 查看 Railway 文档：https://docs.railway.app
4. 加入 Railway Discord：https://discord.gg/railway

## 配置文件说明

### package.json
定义项目依赖和脚本：
- `dependencies`: 生产环境依赖（Express）
- `engines`: 指定 Node.js 版本
- `scripts.build`: 构建前端
- `scripts.start`: 启动服务器

### nixpacks.toml
定义构建流程：
- `phases.setup`: 安装 Node.js
- `phases.install`: 安装依赖
- `phases.build`: 构建前端
- `start`: 启动命令

### railway.toml
定义部署配置：
- `builder`: 使用 Nixpacks
- `startCommand`: 启动命令
- `healthcheckPath`: 健康检查路径
- `restartPolicy`: 重启策略

### server.js
Express 服务器：
- 提供静态文件服务
- 支持 Vue Router
- 健康检查端点
- 详细的日志输出

## 更新日志

- 2026-02-28: 创建详细配置指南
- 2026-02-28: 添加构建流程说明
- 2026-02-28: 添加常见问题排查
- 2026-02-28: 添加验证和监控说明
