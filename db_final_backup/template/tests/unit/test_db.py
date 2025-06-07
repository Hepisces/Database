"""
数据库管理模块单元测试
"""

import os
import pytest
from sqlalchemy import text
from sqlassistant.db import DatabaseManager


@pytest.fixture
def config():
    """测试配置夹具"""
    return {
        "database": {
            "type": "sqlite",
            "path": ":memory:"  # 使用内存数据库进行测试
        }
    }


@pytest.fixture
def db_manager(config):
    """数据库管理器夹具"""
    manager = DatabaseManager(config)
    yield manager
    # 清理工作在这里进行


@pytest.fixture
def initialized_db(db_manager):
    """已初始化的数据库夹具"""
    db_manager.initialize_database()
    return db_manager


@pytest.fixture
def sample_schema():
    """样例数据库模式"""
    return """
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT UNIQUE
    );
    
    CREATE TABLE posts (
        post_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """


def test_initialize_database(db_manager):
    """测试数据库初始化"""
    # 执行
    result = db_manager.initialize_database()
    
    # 断言
    assert result is True
    
    # 验证引擎已创建
    assert db_manager.engine is not None


def test_import_schema(initialized_db, sample_schema):
    """测试导入关系模式"""
    # 执行
    success, message = initialized_db.import_schema(sample_schema)
    
    # 断言
    assert success is True
    assert isinstance(message, str)
    
    # 验证表已创建
    tables = initialized_db.list_tables()
    table_names = [t[0] for t in tables]
    assert "users" in table_names
    assert "posts" in table_names


def test_execute_query(initialized_db, sample_schema):
    """测试执行查询"""
    # 准备：导入模式并插入数据
    initialized_db.import_schema(sample_schema)
    
    insert_query = """
    INSERT INTO users (user_id, username, email) VALUES 
    (1, 'user1', 'user1@example.com'),
    (2, 'user2', 'user2@example.com');
    """
    initialized_db.execute_query(insert_query)
    
    # 执行：查询数据
    success, result = initialized_db.execute_query("SELECT * FROM users")
    
    # 断言
    assert success is True
    assert isinstance(result, dict)
    assert "columns" in result
    assert "data" in result
    assert "row_count" in result
    assert result["row_count"] == 2
    
    # 验证返回的数据正确
    assert len(result["columns"]) == 3  # user_id, username, email
    assert len(result["data"]) == 2     # 两行数据
    assert result["data"][0][1] == "user1"
    assert result["data"][1][1] == "user2"


def test_execute_query_error(initialized_db):
    """测试执行错误的查询"""
    # 执行：错误的SQL
    success, error = initialized_db.execute_query("SELECT * FROM nonexistent_table")
    
    # 断言
    assert success is False
    assert isinstance(error, str)
    assert "nonexistent_table" in error.lower()


def test_list_tables(initialized_db, sample_schema):
    """测试列出表"""
    # 准备：导入模式
    initialized_db.import_schema(sample_schema)
    
    # 执行
    tables = initialized_db.list_tables()
    
    # 断言
    assert isinstance(tables, list)
    assert len(tables) >= 2
    
    # 验证返回格式：[(表名, 列数), ...]
    for table_info in tables:
        assert isinstance(table_info, tuple)
        assert len(table_info) == 2
        assert isinstance(table_info[0], str)   # 表名
        assert isinstance(table_info[1], int)   # 列数


def test_get_schema_info(initialized_db, sample_schema):
    """测试获取模式信息"""
    # 准备：导入模式
    initialized_db.import_schema(sample_schema)
    
    # 执行：获取所有表的模式信息
    schema_info = initialized_db.get_schema_info()
    
    # 断言
    assert isinstance(schema_info, dict)
    assert "users" in schema_info
    assert "posts" in schema_info
    
    # 验证users表结构
    users_info = schema_info["users"]
    assert "columns" in users_info
    assert len(users_info["columns"]) == 3  # user_id, username, email
    
    # 验证主键信息
    assert "primary_keys" in users_info
    assert "user_id" in users_info["primary_keys"]
    
    # 验证外键信息
    posts_info = schema_info["posts"]
    assert "foreign_keys" in posts_info
    assert len(posts_info["foreign_keys"]) > 0
    
    # 执行：获取特定表的模式信息
    users_schema = initialized_db.get_schema_info("users")
    
    # 断言
    assert isinstance(users_schema, dict)
    assert "columns" in users_schema
    assert len(users_schema["columns"]) == 3


def test_reset_database(initialized_db, sample_schema):
    """测试重置数据库"""
    # 准备：导入模式并添加数据
    initialized_db.import_schema(sample_schema)
    initialized_db.execute_query("INSERT INTO users VALUES (1, 'test', 'test@example.com')")
    
    # 验证数据存在
    success, result = initialized_db.execute_query("SELECT COUNT(*) FROM users")
    assert result["data"][0][0] == 1
    
    # 执行：重置数据库
    result = initialized_db.reset_database()
    
    # 断言
    assert result is True
    
    # 重新初始化数据库
    initialized_db.initialize_database()
    
    # 验证表不存在
    tables = initialized_db.list_tables()
    table_names = [t[0] for t in tables]
    assert "users" not in table_names
    assert "posts" not in table_names 