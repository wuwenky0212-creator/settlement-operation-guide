# 环境配置说明

## 概述

本文档详细说明Settlement Operation Guide系统的环境配置，包括开发环境、测试环境和生产环境的配置要求。

## 环境类型

### 1. 开发环境 (Development)

用于本地开发和调试。

**特点**:
- 启用调试模式
- 详细的错误信息
- 热重载
- 使用本地数据库

### 2. 测试环境 (Testing/Staging)

用于集成测试和用户验收测试。

**特点**:
- 接近生产环境配置
- 使用测试数据
- 启用详细日志
- 可以重置数据

### 3. 生产环境 (Production)

实际运行环境。

**特点**:
- 禁用调试模式
- 优化性能
- 完整的监控和日志
- 数据备份和恢复

## 后端环境配置

### 环境变量文件

创建 `backend/.env` 文件，根据环境选择相应配置。

#### 开发环境配置

```ini
# ==================== 应用配置 ====================
APP_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# ==================== 数据库配置 ====================
# PostgreSQL
DATABASE_URL=postgresql://settlement_user:dev_password@localhost:5432/settlement_dev

# 或使用MySQL
# DATABASE_URL=mysql+pymysql://settlement_user:dev_password@localhost:3306/settlement_dev

# 数据库连接池配置
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ==================== API配置 ====================
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=True
API_WORKERS=1

# CORS配置（开发环境允许所有源）
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173

# ==================== 认证配置 ====================
JWT_SECRET_KEY=dev-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 开发环境可以禁用认证（仅用于测试）
AUTH_ENABLED=False

# ==================== 日志配置 ====================
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ==================== 导出配置 ====================
MAX_EXPORT_RECORDS=10000
EXPORT_TEMP_DIR=temp/exports

# ==================== 缓存配置 ====================
# Redis配置（可选）
REDIS_ENABLED=False
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 缓存过期时间（秒）
CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=1800
CACHE_TTL_LONG=86400

# ==================== 外部服务配置 ====================
# SWIFT系统（模拟）
SWIFT_API_URL=http://localhost:9000/swift
SWIFT_API_KEY=dev-swift-key

# 核心系统（模拟）
CORE_API_URL=http://localhost:9001/core
CORE_API_KEY=dev-core-key

# 反洗钱系统（模拟）
AML_API_URL=http://localhost:9002/aml
AML_API_KEY=dev-aml-key

# ==================== 性能配置 ====================
# 查询超时（秒）
QUERY_TIMEOUT=30

# 并发控制
MAX_CONCURRENT_REQUESTS=100

# ==================== 开发工具配置 ====================
# 启用API文档
ENABLE_DOCS=True
DOCS_URL=/docs
REDOC_URL=/redoc

# 启用性能分析
ENABLE_PROFILING=False
```

#### 测试环境配置

```ini
# ==================== 应用配置 ====================
APP_ENV=testing
DEBUG=False
SECRET_KEY=test-secret-key-change-in-production

# ==================== 数据库配置 ====================
DATABASE_URL=postgresql://settlement_user:test_password@test-db-server:5432/settlement_test

DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ==================== API配置 ====================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
API_WORKERS=4

CORS_ORIGINS=https://test.your-domain.com

# ==================== 认证配置 ====================
JWT_SECRET_KEY=test-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

AUTH_ENABLED=True

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/settlement-app/app.log
LOG_MAX_BYTES=52428800
LOG_BACKUP_COUNT=10

# ==================== 导出配置 ====================
MAX_EXPORT_RECORDS=10000
EXPORT_TEMP_DIR=/tmp/settlement-exports

# ==================== 缓存配置 ====================
REDIS_ENABLED=True
REDIS_HOST=test-redis-server
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=test-redis-password

CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=1800
CACHE_TTL_LONG=86400

# ==================== 外部服务配置 ====================
SWIFT_API_URL=https://test-swift.example.com/api
SWIFT_API_KEY=test-swift-api-key

CORE_API_URL=https://test-core.example.com/api
CORE_API_KEY=test-core-api-key

AML_API_URL=https://test-aml.example.com/api
AML_API_KEY=test-aml-api-key

# ==================== 性能配置 ====================
QUERY_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=200

# ==================== 开发工具配置 ====================
ENABLE_DOCS=True
DOCS_URL=/docs
REDOC_URL=/redoc
ENABLE_PROFILING=False
```

#### 生产环境配置

```ini
# ==================== 应用配置 ====================
APP_ENV=production
DEBUG=False
SECRET_KEY=<GENERATE_STRONG_SECRET_KEY>

# ==================== 数据库配置 ====================
# 使用主从配置
DATABASE_URL=postgresql://settlement_user:<STRONG_PASSWORD>@prod-db-master:5432/settlement_prod
DATABASE_REPLICA_URL=postgresql://settlement_user:<STRONG_PASSWORD>@prod-db-slave:5432/settlement_prod

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ==================== API配置 ====================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
API_WORKERS=8

# 严格的CORS配置
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ==================== 认证配置 ====================
JWT_SECRET_KEY=<GENERATE_STRONG_JWT_SECRET>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8

AUTH_ENABLED=True

# ==================== 日志配置 ====================
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_FILE=/var/log/settlement-app/app.log
LOG_MAX_BYTES=104857600
LOG_BACKUP_COUNT=30

# ==================== 导出配置 ====================
MAX_EXPORT_RECORDS=10000
EXPORT_TEMP_DIR=/var/tmp/settlement-exports

# ==================== 缓存配置 ====================
REDIS_ENABLED=True
REDIS_HOST=prod-redis-cluster
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<STRONG_REDIS_PASSWORD>

CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=1800
CACHE_TTL_LONG=86400

# ==================== 外部服务配置 ====================
SWIFT_API_URL=https://swift.example.com/api
SWIFT_API_KEY=<PRODUCTION_SWIFT_API_KEY>

CORE_API_URL=https://core.example.com/api
CORE_API_KEY=<PRODUCTION_CORE_API_KEY>

AML_API_URL=https://aml.example.com/api
AML_API_KEY=<PRODUCTION_AML_API_KEY>

# ==================== 性能配置 ====================
QUERY_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=500

# ==================== 监控配置 ====================
# Prometheus监控
ENABLE_METRICS=True
METRICS_PORT=9090

# Sentry错误追踪
SENTRY_DSN=<YOUR_SENTRY_DSN>
SENTRY_ENVIRONMENT=production

# ==================== 开发工具配置 ====================
# 生产环境禁用文档
ENABLE_DOCS=False
ENABLE_PROFILING=False
```

### 配置文件加载

在 `backend/app/config.py` 中实现配置加载：

```python
from pydantic import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_env: str = "development"
    debug: bool = False
    secret_key: str
    
    # 数据库配置
    database_url: str
    database_replica_url: Optional[str] = None
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    api_workers: int = 4
    cors_origins: List[str] = []
    
    # 认证配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    auth_enabled: bool = True
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10485760
    log_backup_count: int = 5
    
    # 导出配置
    max_export_records: int = 10000
    export_temp_dir: str = "temp/exports"
    
    # 缓存配置
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    cache_ttl_short: int = 300
    cache_ttl_medium: int = 1800
    cache_ttl_long: int = 86400
    
    # 外部服务配置
    swift_api_url: str
    swift_api_key: str
    core_api_url: str
    core_api_key: str
    aml_api_url: str
    aml_api_key: str
    
    # 性能配置
    query_timeout: int = 30
    max_concurrent_requests: int = 100
    
    # 监控配置
    enable_metrics: bool = False
    metrics_port: int = 9090
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None
    
    # 开发工具配置
    enable_docs: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    enable_profiling: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()
```

## 前端环境配置

### 环境变量文件

#### 开发环境 (`.env.development`)

```ini
# API配置
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=Settlement Operation Guide (Dev)
VITE_APP_ENV=development

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=true

# 轮询配置
VITE_POLLING_INTERVAL=10000

# 日志级别
VITE_LOG_LEVEL=debug
```

#### 测试环境 (`.env.test`)

```ini
# API配置
VITE_API_BASE_URL=https://test-api.your-domain.com

# 应用配置
VITE_APP_TITLE=Settlement Operation Guide (Test)
VITE_APP_ENV=testing

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=true

# 轮询配置
VITE_POLLING_INTERVAL=10000

# 日志级别
VITE_LOG_LEVEL=info
```

#### 生产环境 (`.env.production`)

```ini
# API配置
VITE_API_BASE_URL=https://api.your-domain.com

# 应用配置
VITE_APP_TITLE=Settlement Operation Guide
VITE_APP_ENV=production

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=false

# 轮询配置
VITE_POLLING_INTERVAL=10000

# 日志级别
VITE_LOG_LEVEL=error
```

## 数据库配置

### PostgreSQL配置

#### 开发环境

```sql
-- 创建数据库
CREATE DATABASE settlement_dev;

-- 创建用户
CREATE USER settlement_user WITH PASSWORD 'dev_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE settlement_dev TO settlement_user;

-- 连接到数据库
\c settlement_dev

-- 授予schema权限
GRANT ALL ON SCHEMA public TO settlement_user;
```

#### 生产环境

```sql
-- 创建数据库
CREATE DATABASE settlement_prod;

-- 创建用户（使用强密码）
CREATE USER settlement_user WITH PASSWORD '<STRONG_PASSWORD>';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE settlement_prod TO settlement_user;

-- 性能优化配置
ALTER DATABASE settlement_prod SET work_mem = '256MB';
ALTER DATABASE settlement_prod SET maintenance_work_mem = '512MB';
ALTER DATABASE settlement_prod SET effective_cache_size = '4GB';
```

### MySQL配置

#### 开发环境

```sql
-- 创建数据库
CREATE DATABASE settlement_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'settlement_user'@'localhost' IDENTIFIED BY 'dev_password';

-- 授权
GRANT ALL PRIVILEGES ON settlement_dev.* TO 'settlement_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 生产环境

```sql
-- 创建数据库
CREATE DATABASE settlement_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'settlement_user'@'%' IDENTIFIED BY '<STRONG_PASSWORD>';

-- 授权
GRANT ALL PRIVILEGES ON settlement_prod.* TO 'settlement_user'@'%';
FLUSH PRIVILEGES;

-- 性能优化
SET GLOBAL innodb_buffer_pool_size = 4294967296;  -- 4GB
SET GLOBAL max_connections = 500;
```

## 安全配置

### 生成安全密钥

```bash
# 生成SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 密码策略

- 最小长度: 16字符
- 包含大小写字母、数字和特殊字符
- 定期更换（每90天）
- 不使用默认密码
- 使用密码管理器

### 文件权限

```bash
# 设置.env文件权限
chmod 600 backend/.env

# 设置日志目录权限
sudo chown -R www-data:www-data /var/log/settlement-app
sudo chmod 755 /var/log/settlement-app
```

## 配置验证

### 后端配置验证

创建验证脚本 `backend/scripts/validate_config.py`:

```python
#!/usr/bin/env python3
"""配置验证脚本"""
import sys
from app.config import settings

def validate_config():
    """验证配置"""
    errors = []
    
    # 检查必需配置
    if not settings.secret_key or settings.secret_key == "dev-secret-key-change-in-production":
        errors.append("SECRET_KEY未设置或使用默认值")
    
    if not settings.database_url:
        errors.append("DATABASE_URL未设置")
    
    if settings.app_env == "production":
        if settings.debug:
            errors.append("生产环境不应启用DEBUG模式")
        
        if settings.enable_docs:
            errors.append("生产环境不应启用API文档")
        
        if not settings.redis_enabled:
            errors.append("生产环境建议启用Redis缓存")
    
    # 输出结果
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("配置验证通过")
        sys.exit(0)

if __name__ == "__main__":
    validate_config()
```

运行验证：

```bash
cd backend
source venv/bin/activate
python scripts/validate_config.py
```

## 环境切换

### 使用环境变量

```bash
# 开发环境
export APP_ENV=development
python -m uvicorn app.main:app --reload

# 测试环境
export APP_ENV=testing
python -m uvicorn app.main:app

# 生产环境
export APP_ENV=production
python -m uvicorn app.main:app --workers 8
```

### 使用不同的.env文件

```bash
# 开发环境
cp .env.development .env

# 测试环境
cp .env.testing .env

# 生产环境
cp .env.production .env
```

## 故障排查

### 配置问题诊断

```bash
# 检查环境变量
env | grep -i settlement

# 验证数据库连接
python -c "from app.database import engine; print(engine.url)"

# 测试Redis连接
redis-cli -h localhost -p 6379 ping

# 检查端口占用
netstat -tlnp | grep 8000
```

### 常见配置错误

1. **数据库连接失败**
   - 检查DATABASE_URL格式
   - 验证数据库服务是否运行
   - 确认用户名和密码正确

2. **CORS错误**
   - 检查CORS_ORIGINS配置
   - 确保包含前端域名
   - 注意协议（http/https）

3. **认证失败**
   - 检查JWT_SECRET_KEY配置
   - 验证Token格式
   - 确认Token未过期

## 最佳实践

1. **不要提交.env文件到版本控制**
   - 使用.env.example作为模板
   - 在.gitignore中排除.env

2. **使用环境特定的配置**
   - 开发环境使用宽松配置
   - 生产环境使用严格配置

3. **定期审查配置**
   - 检查过期的密钥
   - 更新依赖版本
   - 优化性能参数

4. **文档化配置变更**
   - 记录配置变更原因
   - 更新配置文档
   - 通知团队成员

## 联系支持

配置问题请联系：

- 技术支持: devops@example.com
- 文档: https://docs.example.com/configuration
