# 使用GitHub Desktop推送代码

如果命令行推送遇到网络问题，可以使用GitHub Desktop（图形界面工具）。

## 📥 下载和安装

1. **下载GitHub Desktop**
   - 访问：https://desktop.github.com
   - 点击 "Download for Windows"
   - 安装下载的文件

2. **登录GitHub账号**
   - 打开GitHub Desktop
   - 点击 "Sign in to GitHub.com"
   - 使用你的GitHub账号登录

## 📂 添加现有仓库

1. **添加本地仓库**
   - 点击 "File" → "Add local repository"
   - 或者点击 "Add" → "Add existing repository"
   
2. **选择项目文件夹**
   - 浏览到：`D:\Kiro Workspace\guideline`
   - 点击 "Add repository"

3. **发布仓库**
   - GitHub Desktop会检测到这是一个Git仓库
   - 点击 "Publish repository" 按钮
   - 确认仓库名称：`settlement-operation-guide`
   - 取消勾选 "Keep this code private"（如果你想公开）
   - 点击 "Publish repository"

## ✅ 验证推送成功

1. 推送完成后，访问：
   https://github.com/wuwenky0212-creator/settlement-operation-guide

2. 你应该能看到所有代码文件

## 🔄 后续更新

以后修改代码后，使用GitHub Desktop：

1. **查看更改**
   - GitHub Desktop会自动显示所有更改的文件

2. **提交更改**
   - 在左下角输入提交信息
   - 点击 "Commit to main"

3. **推送到GitHub**
   - 点击 "Push origin"

## 🚂 下一步：部署到Railway

代码推送成功后，按照以下步骤部署：

### 1. 访问Railway
- 打开 https://railway.app
- 使用GitHub账号登录

### 2. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择 `settlement-operation-guide` 仓库

### 3. 添加数据库
- 点击 "New" → "Database" → "Add PostgreSQL"
- 等待数据库创建完成

### 4. 配置环境变量

在后端服务中添加：
```
ENVIRONMENT=production
CORS_ORIGINS=*
```

### 5. 等待部署完成
- Railway会自动检测并部署
- 查看部署日志确认成功

### 6. 获取访问链接
- 部署完成后，点击服务查看URL
- 记录下来：
  - 前端: `https://your-app.railway.app`
  - 后端: `https://your-backend.railway.app`

## 📖 详细文档

- [Railway部署详细指南](./RAILWAY_DEPLOYMENT.md)
- [快速部署指南](./QUICK_DEPLOY.md)
- [部署检查清单](./DEPLOYMENT_CHECKLIST.md)

## 💡 GitHub Desktop的优势

- ✅ 图形界面，更直观
- ✅ 自动处理网络问题
- ✅ 可视化查看更改
- ✅ 简化Git操作
- ✅ 适合Git新手

## 🎯 你的仓库信息

- **GitHub仓库**: https://github.com/wuwenky0212-creator/settlement-operation-guide
- **本地路径**: D:\Kiro Workspace\guideline
- **分支**: main

---

**推荐使用GitHub Desktop，它能更好地处理网络问题！** 🚀
