"""Logging configuration"""
import logging
import sys
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> None:
    """
    配置应用日志
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 配置日志格式
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(message)s - [%(filename)s:%(lineno)d]"
    )
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 配置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


class ContextFilter(logging.Filter):
    """
    上下文过滤器
    
    为日志记录添加额外的上下文信息
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            bool: 是否保留该日志记录
        """
        # 添加默认的上下文信息
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        
        return True
