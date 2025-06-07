"""
pytest配置文件 - 提供共享夹具和测试环境设置
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlassistant.db import DatabaseManager
from sqlassistant.parser import SQLParser
from sqlassistant.visualizer import QueryVisualizer
from sqlassistant.nlp import NLProcessor


@pytest.fixture(scope="session")
def test_config():
    """测试配置夹具"""
    return {
        "database": {
            "type": "sqlite",
            "path": ":memory:"  # 使用内存数据库进行测试
        },
        "parser": {
            "error_format": "friendly",
            "suggest_fixes": True,
            "dialect": "postgresql"
        },
        "visualization": {
            "engine": "matplotlib",
            "theme": "default",
            "query_plan": True,
            "max_results": 1000
        },
        "nlp": {
            "model_type": "mock",  # 测试时使用模拟模型
            "local": {
                "model_path": "mock_model_path",
                "max_tokens": 1024,
                "temperature": 0.3
            },
            "online": {
                "provider": "mock_provider",
                "api_key": "mock_api_key",
                "model": "mock_model",
                "max_tokens": 1024,
                "temperature": 0.3
            }
        },
        "logging": {
            "level": "DEBUG",
            "file": None  # 测试时不写入日志文件
        }
    }


@pytest.fixture
def temp_dir():
    """创建临时目录夹具"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_manager(test_config):
    """数据库管理器夹具"""
    manager = DatabaseManager(test_config)
    manager.initialize_database()
    yield manager
    # SQLite内存数据库会在连接关闭时自动清理，不需要显式清理


@pytest.fixture
def sqlite_file_db(temp_dir, test_config):
    """基于文件的SQLite数据库夹具"""
    db_path = temp_dir / "test_db.sqlite"
    config = test_config.copy()
    config["database"] = {
        "type": "sqlite",
        "path": str(db_path)
    }
    
    manager = DatabaseManager(config)
    manager.initialize_database()
    yield manager
    
    # 清理：关闭连接并删除文件
    if hasattr(manager, 'engine') and manager.engine:
        manager.engine.dispose()
    
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def initialized_db(db_manager):
    """
    加载了测试模式的数据库夹具
    
    使用fixtures/schema.sql加载测试模式和数据
    """
    # 读取模式文件
    schema_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # 导入模式（SQLite不支持所有PostgreSQL功能，会自动转换或跳过）
    db_manager.import_schema(schema_sql.replace('SERIAL', 'INTEGER'))
    
    return db_manager


@pytest.fixture
def sql_parser(test_config):
    """SQL解析器夹具"""
    return SQLParser(test_config)


@pytest.fixture
def visualizer(test_config):
    """查询可视化器夹具"""
    return QueryVisualizer(test_config)


@pytest.fixture
def nlp_processor(mocker, test_config):
    """
    自然语言处理器夹具（带模拟）
    
    由于NLP模块可能依赖外部服务或大型模型，此夹具模拟其行为
    """
    processor = NLProcessor(test_config)
    
    # 创建一个模拟的translate_to_sql方法
    def mock_translate_to_sql(nl_query):
        # 模拟的转换逻辑，基于自然语言查询返回预定义的SQL
        simple_responses = {
            "显示所有用户": "SELECT * FROM users;",
            "列出所有部门": "SELECT * FROM departments;",
            "查询高薪员工": "SELECT * FROM employees WHERE salary > 100000;",
            "最近创建的项目": "SELECT * FROM projects ORDER BY start_date DESC LIMIT 5;"
        }
        
        # 检查是否有预定义响应
        for key, sql in simple_responses.items():
            if key in nl_query:
                return True, sql
        
        # 默认返回一个基本的查询
        return True, "SELECT * FROM users LIMIT 10;"
    
    # 使用模拟方法替换真实方法
    mocker.patch.object(processor, 'translate_to_sql', side_effect=mock_translate_to_sql)
    
    return processor


@pytest.fixture
def sample_queries():
    """样例查询夹具"""
    from tests.fixtures.sample_queries import (
        get_all_valid_queries,
        get_all_invalid_queries,
        NL_QUERY_PAIRS
    )
    
    return {
        "valid": get_all_valid_queries(),
        "invalid": get_all_invalid_queries(),
        "nl_pairs": NL_QUERY_PAIRS
    } 