"""
工具函数模块 - 提供配置加载等通用功能
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
import re
import platform


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认为当前目录下的config.yaml
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    # 默认配置路径
    if not config_path:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
    
    # 检查文件是否存在
    if not os.path.exists(config_path):
        logging.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return get_default_config()
    
    # 加载配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 处理环境变量引用
        config = _process_env_vars(config)
        
        return config
    except Exception as e:
        logging.error(f"加载配置文件出错: {str(e)}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        Dict[str, Any]: 默认配置字典
    """
    return {
        "database": {
            "type": "sqlite",
            "path": "project2025.db"
        },
        "parser": {
            "error_format": "friendly",
            "suggest_fixes": True,
            "dialect": "sqlite"
        },
        "visualization": {
            "engine": "matplotlib",
            "theme": "default",
            "query_plan": True,
            "max_results": 1000
        },
        "nlp": {
            "model_type": "online",
            "local": {
                "model_path": "models/llama-2-7b-sql.gguf",
                "max_tokens": 1024,
                "temperature": 0.3
            },
            "online": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "max_tokens": 1024,
                "temperature": 0.3
            }
        },
        "logging": {
            "level": "info",
            "file": "logs/sqlassistant.log"
        }
    }


def _process_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理配置中的环境变量引用
    
    Args:
        config: 原始配置字典
        
    Returns:
        Dict[str, Any]: 处理后的配置字典
    """
    if isinstance(config, dict):
        return {k: _process_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_process_env_vars(item) for item in config]
    elif isinstance(config, str):
        # 处理环境变量引用，例如 ${VAR_NAME}
        env_vars = re.findall(r'\${([^}]+)}', config)
        if env_vars:
            for var in env_vars:
                env_value = os.environ.get(var, '')
                config = config.replace(f'${{{var}}}', env_value)
        return config
    else:
        return config


def setup_logging(config: Dict[str, Any]):
    """
    设置日志
    
    Args:
        config: 配置字典
    """
    log_config = config.get("logging", {})
    log_level_str = log_config.get("level", "info").upper()
    log_file = log_config.get("file")
    
    # 映射日志级别字符串到logging模块的级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = level_map.get(log_level_str, logging.INFO)
    
    # 基本配置
    logging_config = {
        "level": log_level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging_config["filename"] = log_file
    
    # 应用配置
    logging.basicConfig(**logging_config)


def get_system_info() -> Dict[str, str]:
    """
    获取系统信息
    
    Returns:
        Dict[str, str]: 系统信息字典
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "machine": platform.machine()
    }


def format_sql(sql: str) -> str:
    """
    格式化SQL语句，使其更易读
    
    Args:
        sql: 原始SQL语句
        
    Returns:
        str: 格式化后的SQL语句
    """
    try:
        import sqlparse
        return sqlparse.format(
            sql,
            reindent=True,
            keyword_case='upper',
            strip_comments=False,
            indent_width=4
        )
    except ImportError:
        # 如果sqlparse不可用，返回原始SQL
        return sql


def create_directory_if_not_exists(path: str) -> bool:
    """
    如果目录不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        bool: 是否成功创建或已存在
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        logging.error(f"创建目录失败: {str(e)}")
        return False