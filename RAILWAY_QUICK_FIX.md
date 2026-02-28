# Railway 快速修复指南

## 立即执行的步骤

### 第 1 步：检查 Railway 设置

1. 打开 Railway 控制台：https://railway.app/dashboard
2. 进入你的项目：`settlement-operation-guide`
3. 点击服务（应该只有一个服务）
4. 点击 "Settings" 标签

### 第 2 步：清空所有手动配置

在 "Deploy" 部分，确保以下字段**全部为空**：

- ✓ Root Directory: **留空**
- ✓ Build Command: **留空**
- ✓ Start Command: **留空**
- ✓ Install Command: **留空**
- ✓ Watch Paths: **留空**

**为什么要清空？**
因为项目已经有配置文件（nixpacks.toml 和 railway.toml），手动配置会覆盖这些文件，导致冲突。

### 第 3 步：检查环境变量

在 "Variables" 标签：
- **不需要**设置 PORT（Railway 自动提供）
- **不需要**设置 NODE_ENV
- 如果有其他变量，可以删除

### 第 4 步：触发重新部署

有两种方法：

**方法 A: 通过 Git 推送（推荐）**
```bash
# 在本地运行
git push origin main
```

**方法 B: 手动触发**
1. 在 Railway 服务页面
2. 点击右上角的 "..." 菜单
3. 选择 "Redeploy"

### 第 5 步：监控部署过程

部署开始后，依次查看：

#### 5.1 Build Logs（构建日志）

点击 "Build Logs" 标签，应该看到：

```
✓ [setup] Installing Node.js 18.x
✓ [install] Installing dependencies
  npm ci --omit=dev
  cd frontend && npm ci
✓ [build] Building frontend
  cd frontend && npm run build
  ✓ Build successful
```

**如果看到错误：**
- 记录完整的错误信息
- 截图发给我

#### 5.2 Deploy Logs（部署日志）

点击 "Deploy Logs" 标签，应该看到：

```
==================================================
Settlement Operation Guide Server
==================================================
Node version: v18.x.x
✓ Frontend dist directory found
✓ index.html found
==================================================
✓ Server is running on http://0.0.0.0:XXXX
✓ Serving files from: /app/frontend/dist
==================================================
```

**如果看到错误：**
- 记录完整的错误信息
- 截图发给我

#### 5.3 HTTP Logs（HTTP 日志）

部署成功后，访问你的网站，然后查看 "HTTP Logs"：

```
GET / → 200 OK
GET /assets/index-xxx.js → 200 OK
GET /health → 200 OK
```

**如果看到 502：**
- 说明服务器没有正确启动
- 回到 Deploy Logs 查看错误

## 常见错误及解决方案

### 错误 1: "npm install failed"

**Build Logs 显示：**
```
npm ERR! code ENOTFOUND
npm ERR! network request failed
```

**解决方案：**
- 这是临时网络问题
- 等待 1-2 分钟后重新部署
- 或者点击 "Redeploy"

### 错误 2: "frontend/dist not found"

**Deploy Logs 显示：**
```
❌ Error: frontend/dist directory not found!
```

**解决方案：**
1. 检查 Build Logs，确认构建是否成功
2. 如果构建失败，查看具体错误
3. 如果构建成功但 dist 不存在，可能是路径问题

### 错误 3: "Cannot find module 'express'"

**Deploy Logs 显示：**
```
Error: Cannot find module 'express'
```

**解决方案：**
- 根目录的依赖没有安装
- 检查 Build Logs 中的 install 阶段
- 重新部署

### 错误 4: 502 Bad Gateway

**HTTP Logs 显示：**
```
GET / → 502 Bad Gateway
```

**解决方案：**
1. 检查 Deploy Logs，服务器是否启动
2. 如果没有启动日志，说明启动失败
3. 查看错误信息

## 如果所有方法都失败

### 最后的手段：完全重置

1. **删除现有服务**
   - 在 Railway 项目中
   - 点击服务 → Settings → Danger
   - 点击 "Remove Service from Project"

2. **创建新服务**
   - 点击 "New Service"
   - 选择 "GitHub Repo"
   - 选择 `settlement-operation-guide` 仓库
   - **不要**设置 Root Directory
   - 让 Railway 自动检测

3. **等待部署**
   - Railway 会自动检测 Node.js 项目
   - 自动读取配置文件
   - 自动构建和部署

## 本地测试（推荐先做）

在推送到 Railway 之前，先在本地测试：

```bash
# 运行测试脚本
test_local.bat
```

或者手动执行：

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

**如果本地测试失败：**
- 不要推送到 Railway
- 先修复本地问题
- 本地成功后再部署

**如果本地测试成功：**
- Railway 上应该也能成功
- 如果 Railway 失败，是配置问题

## 需要提供的信息

如果问题持续，请提供：

1. **Build Logs 截图**（完整的，从开始到结束）
2. **Deploy Logs 截图**（完整的，从开始到结束）
3. **HTTP Logs 截图**（显示 502 的那部分）
4. **Settings 截图**（Deploy 和 Variables 部分）
5. **本地测试结果**（成功还是失败）

## 预计时间

- 清空配置：1 分钟
- 重新部署：5-10 分钟
- 验证成功：1 分钟
- **总计：7-12 分钟**

## 成功的标志

部署成功后，你应该能：

1. ✓ 访问 `https://your-app.railway.app`
2. ✓ 看到前端页面
3. ✓ 访问 `https://your-app.railway.app/health` 返回 JSON
4. ✓ HTTP Logs 显示 200 OK

## 下一步

部署成功后：
1. 测试所有页面功能
2. 检查浏览器控制台
3. 配置自定义域名（可选）
4. 设置监控（可选）

## 联系方式

如果需要帮助：
- 提供上述信息
- 我会帮你诊断问题
- 找到解决方案
