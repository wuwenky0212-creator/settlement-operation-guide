# Vercel 前端部署指南（推荐）

如果 Railway 部署遇到问题，使用 Vercel 部署前端是最简单可靠的方案。

## 为什么选择 Vercel？

- ✓ 专门为前端优化
- ✓ 自动检测 Vue/Vite 项目
- ✓ 全球 CDN，访问速度快
- ✓ 免费额度充足
- ✓ 部署成功率高
- ✓ 3 分钟内完成部署

## 部署步骤

### 1. 访问 Vercel

1. 打开 https://vercel.com
2. 点击 "Sign Up" 或 "Login"
3. 选择 "Continue with GitHub"
4. 授权 Vercel 访问你的 GitHub

### 2. 导入项目

1. 点击 "Add New..." → "Project"
2. 在列表中找到 `settlement-operation-guide`
3. 点击 "Import"

### 3. 配置项目

在配置页面设置：

**Framework Preset:** Vite

**Root Directory:** `frontend` （点击 Edit 修改）

**Build and Output Settings:**
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

**Environment Variables:**（可选）
- 如果需要连接后端 API，添加：
  - Name: `VITE_API_BASE_URL`
  - Value: `https://your-backend-url.railway.app`

### 4. 部署

1. 点击 "Deploy"
2. 等待 2-3 分钟
3. 部署完成后会显示预览链接

### 5. 访问你的网站

部署成功后，你会得到一个 URL：
```
https://settlement-operation-guide-xxx.vercel.app
```

## 自动部署

配置完成后，每次推送到 GitHub 的 `main` 分支，Vercel 会自动：
1. 检测代码变更
2. 重新构建前端
3. 部署到生产环境

## 自定义域名（可选）

1. 在 Vercel 项目设置中
2. 点击 "Domains"
3. 添加你的域名
4. 按照提示配置 DNS

## 故障排查

### 构建失败

**错误：** `npm install` 失败
**解决：** 检查 `frontend/package.json` 中的依赖是否正确

**错误：** `npm run build` 失败
**解决：** 在本地运行 `cd frontend && npm run build` 查看详细错误

### 页面空白

**原因：** 路由配置问题
**解决：** Vercel 会自动处理 Vue Router，通常不需要额外配置

### API 请求失败

**原因：** 后端 URL 未配置或 CORS 问题
**解决：** 
1. 确保设置了 `VITE_API_BASE_URL` 环境变量
2. 确保后端允许 Vercel 域名的 CORS 请求

## 完整方案：Vercel（前端）+ Railway（后端）

这是最推荐的部署方案：

### 前端（Vercel）
- 快速、稳定、免费
- 全球 CDN 加速
- 自动 HTTPS

### 后端（Railway）
- 支持 Python/FastAPI
- 提供 PostgreSQL 数据库
- 自动 HTTPS

### 连接前后端

1. **部署后端到 Railway**
   - 按照之前的指南部署后端
   - 记录后端 URL（例如：`https://backend.railway.app`）

2. **配置前端环境变量**
   - 在 Vercel 项目设置中
   - 添加环境变量：`VITE_API_BASE_URL=https://backend.railway.app`
   - 重新部署

3. **配置后端 CORS**
   - 在后端环境变量中添加：
   - `CORS_ORIGINS=https://your-frontend.vercel.app`

## 成本

Vercel 免费版包括：
- 无限网站
- 100GB 带宽/月
- 无限请求
- 自动 HTTPS
- 全球 CDN

对于个人项目完全够用！

## 与 Railway 对比

| 特性 | Vercel | Railway |
|------|--------|---------|
| 前端部署 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 后端部署 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 部署速度 | 2-3 分钟 | 5-10 分钟 |
| 稳定性 | 非常高 | 高 |
| 免费额度 | 充足 | 有限 |
| 学习曲线 | 简单 | 中等 |

## 推荐策略

1. **先部署前端到 Vercel**
   - 快速让网站上线
   - 验证前端功能正常

2. **再部署后端到 Railway**
   - 慢慢调试后端问题
   - 不影响前端访问

3. **连接前后端**
   - 配置环境变量
   - 测试 API 调用

## 下一步

部署成功后：
1. 测试所有页面功能
2. 检查浏览器控制台是否有错误
3. 配置自定义域名（可选）
4. 设置监控和分析（可选）

## 需要帮助？

- Vercel 文档: https://vercel.com/docs
- Vercel 支持: https://vercel.com/support
- Discord 社区: https://vercel.com/discord
