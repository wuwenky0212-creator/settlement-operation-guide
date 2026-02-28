@echo off
echo ========================================
echo Railway 部署脚本
echo ========================================
echo.

echo 步骤 1: 添加所有更改...
git add .

echo.
echo 步骤 2: 提交更改...
set /p commit_msg="请输入提交信息 (默认: Update deployment configuration): "
if "%commit_msg%"=="" set commit_msg=Update deployment configuration
git commit -m "%commit_msg%"

echo.
echo 步骤 3: 推送到 GitHub...
git push origin main

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo Railway 会自动检测到更改并重新部署
echo 请访问 Railway 控制台查看部署进度：
echo https://railway.app/dashboard
echo.
echo 部署日志会显示构建和启动过程
echo 如果遇到问题，请检查：
echo 1. Build Logs - 查看构建过程
echo 2. Deploy Logs - 查看启动日志
echo 3. HTTP Logs - 查看请求日志
echo.
pause
