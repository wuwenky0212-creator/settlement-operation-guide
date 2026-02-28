# 部署指南

## 概述

本文档提供Settlement Operation Guide系统的完整部署指南，包括环境配置、数据库设置、应用部署和运维监控。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      负载均衡器                           │
│                    (Nginx/HAProxy)                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  前端服务器1  │    │  前端服务器2  │    │  前端服务器N  │
│   (Vue.js)   │    │   (Vue.js)   │    │   (Vue.js)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      API网关                             │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  后端服务器1  │    │  后端服务器2  │    │  后端服务器N  │
│  (FastAPI)   │    │  (FastAPI)   │    │  (FastAPI)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据库集群                             │
│              (PostgreSQL/MySQL Master-Slave)            │
└─────────────────────────────────────────────────────────┘
```

## 环境要求

### 硬件要求

**最小配置**:
- CPU: 4核
- 内存: 8GB
- 磁盘: 100GB SSD
- 网络: 100Mbps

**推荐配置**:
- CPU: 8核或更多
- 内存: 16GB或更多
- 磁盘: 500GB SSD
- 网络: 1Gbps

### 软件要求

**操作系统**:
- Linux (Ubuntu 20.04+ / CentOS 8+ / RHEL 8+)
- Windows Server 2019+ (仅用于开发环境)

**运行时环境**:
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ 或 MySQL 8+

**其他依赖**:
- Nginx 1.18+ (反向代理)
- Redis 6+ (可选，用于缓存)
- Git (版本控制)

## 环境配置

### 1. 安装Python环境

#### Ubuntu/Debian

```bash
# 更新包管理器
sudo apt update

# 安装Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip

# 验证安装
python3.9 --version
```

#### CentOS/RHEL

```bash
# 安装Python 3.9+
sudo dnf install python39 python39-pip

# 验证安装
python3.9 --version
```

### 2. 安装Node.js环境

#### 使用NodeSource仓库

```bash
# 安装Node.js 16.x
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version
npm --version
```

### 3. 安装数据库

#### PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
```

```sql
-- 在PostgreSQL命令行中执行
CREATE DATABASE settlement_db;
CREATE USER settlement_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE settlement_db TO settlement_user;
\q
```

#### MySQL

```bash
# Ubuntu/Debian
sudo apt install mysql-server

# 启动服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql
```

```sql
-- 在MySQL命令行中执行
CREATE DATABASE settlement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'settlement_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON settlement_db.* TO 'settlement_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. 安装Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 验证安装
nginx -v
```

## 应用部署

### 后端部署

#### 1. 克隆代码仓库

```bash
# 创建应用目录
sudo mkdir -p /opt/settlement-app
sudo chown $USER:$USER /opt/settlement-app

# 克隆代码
cd /opt/settlement-app
git clone <repository_url> .
```

#### 2. 配置Python虚拟环境

```bash
# 进入后端目录
cd /opt/settlement-app/backend

# 创建虚拟环境
python3.9 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件：

```bash
cd /opt/settlement-app/backend
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```ini
# 数据库配置
DATABASE_URL=postgresql://settlement_user:your_secure_password@localhost:5432/settlement_db
# 或使用MySQL
# DATABASE_URL=mysql+pymysql://settlement_user:your_secure_password@localhost:3306/settlement_db

# 应用配置
APP_ENV=production
DEBUG=False
SECRET_KEY=your_very_long_random_secret_key_here

# API配置
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-domain.com

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/settlement-app/app.log

# 认证配置
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 导出限制
MAX_EXPORT_RECORDS=10000
```

#### 4. 运行数据库迁移

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行迁移
alembic upgrade head
```

#### 5. 配置Systemd服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/settlement-api.service
```

添加以下内容：

```ini
[Unit]
Description=Settlement Operation Guide API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/settlement-app/backend
Environment="PATH=/opt/settlement-app/backend/venv/bin"
ExecStart=/opt/settlement-app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start settlement-api

# 设置开机自启
sudo systemctl enable settlement-api

# 查看状态
sudo systemctl status settlement-api
```

### 前端部署

#### 1. 构建前端应用

```bash
# 进入前端目录
cd /opt/settlement-app/frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.production
nano .env.production
```

编辑 `.env.production`：

```ini
VITE_API_BASE_URL=https://api.your-domain.com
VITE_APP_TITLE=Settlement Operation Guide
```

构建应用：

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
```

#### 2. 配置Nginx

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/settlement-app
```

添加以下内容：

```nginx
# 前端服务器配置
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 前端静态文件
    root /opt/settlement-app/frontend/dist;
    index index.html;
    
    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# API服务器配置（可选，如果需要独立域名）
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    
    ssl_certificate /etc/ssl/certs/api.your-domain.crt;
    ssl_certificate_key /etc/ssl/private/api.your-domain.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/settlement-app /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

## 数据库迁移

### 创建新迁移

```bash
cd /opt/settlement-app/backend
source venv/bin/activate

# 创建新迁移
alembic revision --autogenerate -m "描述迁移内容"

# 查看迁移文件
ls alembic/versions/
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision_id>

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 迁移脚本示例

位置: `backend/alembic/versions/`

```python
"""添加新字段示例

Revision ID: 002_add_new_field
Revises: 001_create_initial_tables
Create Date: 2026-02-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_new_field'
down_revision = '001_create_initial_tables'
branch_labels = None
depends_on = None

def upgrade():
    # 添加新字段
    op.add_column('transactions', 
        sa.Column('new_field', sa.String(100), nullable=True)
    )
    
    # 创建索引
    op.create_index('idx_transactions_new_field', 
        'transactions', ['new_field']
    )

def downgrade():
    # 删除索引
    op.drop_index('idx_transactions_new_field', 
        table_name='transactions'
    )
    
    # 删除字段
    op.drop_column('transactions', 'new_field')
```

## 监控与日志

### 应用日志

日志配置在 `backend/app/logging_config.py`。

**日志位置**:
- 应用日志: `/var/log/settlement-app/app.log`
- 错误日志: `/var/log/settlement-app/error.log`
- 访问日志: `/var/log/nginx/access.log`

**查看日志**:

```bash
# 查看应用日志
tail -f /var/log/settlement-app/app.log

# 查看错误日志
tail -f /var/log/settlement-app/error.log

# 查看Nginx访问日志
tail -f /var/log/nginx/access.log

# 查看systemd服务日志
sudo journalctl -u settlement-api -f
```

### 日志轮转

创建日志轮转配置：

```bash
sudo nano /etc/logrotate.d/settlement-app
```

添加以下内容：

```
/var/log/settlement-app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload settlement-api > /dev/null 2>&1 || true
    endscript
}
```

### 性能监控

#### 使用Prometheus + Grafana

1. 安装Prometheus客户端：

```bash
pip install prometheus-client
```

2. 在应用中添加监控端点（已在代码中实现）

3. 配置Prometheus抓取：

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'settlement-api'
    static_configs:
      - targets: ['localhost:8000']
```

#### 数据库监控

```bash
# PostgreSQL
sudo apt install postgresql-contrib

# 启用pg_stat_statements
sudo -u postgres psql -d settlement_db
```

```sql
CREATE EXTENSION pg_stat_statements;
```

## 备份与恢复

### 数据库备份

#### PostgreSQL

```bash
# 创建备份脚本
sudo nano /opt/scripts/backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/settlement-db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/settlement_db_$DATE.sql.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump -U settlement_user settlement_db | gzip > $BACKUP_FILE

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_FILE"
```

```bash
# 设置执行权限
sudo chmod +x /opt/scripts/backup-db.sh

# 添加到crontab（每天凌晨2点执行）
sudo crontab -e
```

添加：

```
0 2 * * * /opt/scripts/backup-db.sh >> /var/log/settlement-app/backup.log 2>&1
```

#### MySQL

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/settlement-db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/settlement_db_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

mysqldump -u settlement_user -p'your_password' settlement_db | gzip > $BACKUP_FILE

find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_FILE"
```

### 数据库恢复

#### PostgreSQL

```bash
# 恢复备份
gunzip < /var/backups/settlement-db/settlement_db_20260227_020000.sql.gz | \
    psql -U settlement_user -d settlement_db
```

#### MySQL

```bash
# 恢复备份
gunzip < /var/backups/settlement-db/settlement_db_20260227_020000.sql.gz | \
    mysql -u settlement_user -p'your_password' settlement_db
```

## 安全配置

### 1. 防火墙配置

```bash
# 使用UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. SSL证书配置

#### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 数据库安全

```sql
-- PostgreSQL: 限制远程访问
-- 编辑 /etc/postgresql/13/main/pg_hba.conf
-- 只允许本地连接
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

### 4. 应用安全

- 使用强密码和密钥
- 定期更新依赖包
- 启用HTTPS
- 配置CORS正确的源
- 实施速率限制
- 定期安全审计

## 故障排查

### 常见问题

#### 1. 应用无法启动

```bash
# 查看服务状态
sudo systemctl status settlement-api

# 查看详细日志
sudo journalctl -u settlement-api -n 100

# 检查端口占用
sudo netstat -tlnp | grep 8000
```

#### 2. 数据库连接失败

```bash
# 测试数据库连接
psql -U settlement_user -d settlement_db -h localhost

# 检查数据库服务
sudo systemctl status postgresql

# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 3. Nginx配置错误

```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 重新加载配置
sudo systemctl reload nginx
```

#### 4. 性能问题

```bash
# 查看系统资源
top
htop

# 查看数据库连接
psql -U settlement_user -d settlement_db -c "SELECT count(*) FROM pg_stat_activity;"

# 查看慢查询
psql -U settlement_user -d settlement_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 升级流程

### 1. 准备升级

```bash
# 备份数据库
/opt/scripts/backup-db.sh

# 备份当前代码
cd /opt/settlement-app
tar -czf ../settlement-app-backup-$(date +%Y%m%d).tar.gz .
```

### 2. 更新代码

```bash
# 拉取最新代码
cd /opt/settlement-app
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 更新前端依赖
cd ../frontend
npm install
```

### 3. 运行迁移

```bash
cd /opt/settlement-app/backend
source venv/bin/activate
alembic upgrade head
```

### 4. 重新构建前端

```bash
cd /opt/settlement-app/frontend
npm run build
```

### 5. 重启服务

```bash
# 重启后端
sudo systemctl restart settlement-api

# 重新加载Nginx
sudo systemctl reload nginx
```

### 6. 验证升级

```bash
# 检查服务状态
sudo systemctl status settlement-api

# 测试API
curl https://your-domain.com/health

# 查看日志
tail -f /var/log/settlement-app/app.log
```

## 性能优化

### 1. 数据库优化

```sql
-- PostgreSQL: 创建索引
CREATE INDEX idx_transactions_trade_date ON transactions(trade_date);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_cash_flows_transaction_id ON cash_flows(transaction_id);

-- 分析表
ANALYZE transactions;
ANALYZE cash_flows;
ANALYZE events;
```

### 2. 应用优化

- 增加worker数量（根据CPU核心数）
- 启用连接池
- 配置缓存（Redis）
- 使用CDN加速静态资源

### 3. Nginx优化

```nginx
# 增加worker进程
worker_processes auto;

# 增加连接数
events {
    worker_connections 2048;
}

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # ... 其他配置
}
```

## 联系支持

如有部署问题，请联系：

- 技术支持: devops@example.com
- 紧急热线: +86-xxx-xxxx-xxxx
- 文档: https://docs.example.com
