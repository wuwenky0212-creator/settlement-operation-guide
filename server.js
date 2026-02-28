const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 检查 dist 目录是否存在
const distPath = path.join(__dirname, 'frontend/dist');
if (!fs.existsSync(distPath)) {
  console.error('Error: frontend/dist directory not found!');
  console.error('Please run "npm run build" first');
  process.exit(1);
}

// 提供静态文件
app.use(express.static(distPath));

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 所有路由都返回 index.html（支持 Vue Router）
app.get('*', (req, res) => {
  res.sendFile(path.join(distPath, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
  console.log(`Serving files from: ${distPath}`);
});
