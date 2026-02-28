const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 检查 dist 目录是否存在
const distPath = path.join(__dirname, 'frontend', 'dist');

console.log('='.repeat(50));
console.log('Settlement Operation Guide Server');
console.log('='.repeat(50));
console.log(`Node version: ${process.version}`);
console.log(`Working directory: ${__dirname}`);
console.log(`Dist path: ${distPath}`);
console.log(`PORT: ${PORT}`);

if (!fs.existsSync(distPath)) {
  console.error('❌ Error: frontend/dist directory not found!');
  console.error('Please ensure the build process completed successfully.');
  console.error('Expected path:', distPath);
  process.exit(1);
}

const indexPath = path.join(distPath, 'index.html');
if (!fs.existsSync(indexPath)) {
  console.error('❌ Error: index.html not found in dist directory!');
  console.error('Expected path:', indexPath);
  process.exit(1);
}

console.log('✓ Frontend dist directory found');
console.log('✓ index.html found');

// 提供静态文件
app.use(express.static(distPath));

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    nodeVersion: process.version
  });
});

// 所有路由都返回 index.html（支持 Vue Router）
app.get('*', (req, res) => {
  res.sendFile(indexPath);
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log(`✓ Server is running on http://0.0.0.0:${PORT}`);
  console.log(`✓ Serving files from: ${distPath}`);
  console.log(`✓ Health check: http://0.0.0.0:${PORT}/health`);
  console.log('='.repeat(50));
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
