"""Main application entry point"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from datetime import datetime

from app.api import transactions, cash_flows, export as export_api
from app.middleware.error_handler import error_handler_middleware
from app.middleware.logging_middleware import logging_middleware
from app.middleware.auth import auth_middleware
from app.logging_config import setup_logging

# 配置日志
setup_logging()

app = FastAPI(
    title="Settlement Operation Guide API",
    description="""
    ## 操作指导系统API
    
    提供交易结算操作指导的RESTful API服务，包括：
    
    * **交易管理**: 查询交易汇总、详情、事件记录、账务信息
    * **现金流管理**: 查询现金流列表、详情、收付进度
    * **生命周期跟踪**: 实时跟踪交易和现金流的处理进度
    * **操作指引**: 根据当前状态动态生成操作建议
    * **数据导出**: 支持Excel和CSV格式导出
    
    ### 认证
    
    所有API请求都需要在请求头中包含认证Token：
    ```
    Authorization: Bearer <your_token>
    ```
    
    ### 错误处理
    
    API使用标准HTTP状态码，错误响应包含详细的错误信息。
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "Proprietary"
    }
)

# Add exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and return proper JSON response"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters: logging -> auth -> error handler)
logging_middleware(app)
auth_middleware(app)
error_handler_middleware(app)

# Include routers
app.include_router(transactions.router)
app.include_router(cash_flows.router)
app.include_router(export_api.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Settlement Operation Guide API"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
