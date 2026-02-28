@echo off
echo ==========================================
echo 本地测试脚本
echo ==========================================
echo.

echo 步骤 1: 检查 Node.js 版本...
node --version
if errorlevel 1 (
    echo [31m错误: Node.js 未安装[0m
    pause
    exit /b 1
)

echo.
echo 步骤 2: 安装根目录依赖...
call npm install
if errorlevel 1 goto error

echo.
echo 步骤 3: 安装前端依赖...
cd frontend
call npm install
if errorlevel 1 goto error

echo.
echo 步骤 4: 构建前端...
call npm run build
if errorlevel 1 goto error

echo.
echo 步骤 5: 验证构建结果...
cd ..
if exist "frontend\dist\index.html" (
    echo [32m✓ 构建成功！[0m
    echo [32m✓ 找到 index.html[0m
) else (
    echo [31m✗ 构建失败 - 未找到 index.html[0m
    goto error
)

echo.
echo 步骤 6: 启动服务器...
echo [33m服务器将在 http://localhost:3000 启动[0m
echo [33m按 Ctrl+C 停止服务器[0m
echo.
node server.js

goto end

:error
echo.
echo [31m==========================================
echo 测试失败！
echo ==========================================[0m
pause
exit /b 1

:end
