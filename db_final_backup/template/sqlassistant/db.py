"""
数据库管理模块 - 处理数据库连接、初始化和查询执行
"""

import os
import sqlite3
import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, inspect
from typing import Dict, List, Tuple, Any, Optional, Union


class DatabaseManager:
    """
    数据库管理器，用于处理数据库操作
    """
    
    def __init__(self, config: Dict):
        """
        初始化数据库管理器
        
        Args:
            config: 配置字典，包含数据库连接信息
        """
        self.config = config
        self.db_config = config.get("database", {})
        self.db_type = self.db_config.get("type", "sqlite")
        self.db_path = self.db_config.get("path", "project2025.db")
        self.engine = None
        self.metadata = MetaData()
        self.connection = None
    
    def set_db_path(self, path: str):
        """
        设置数据库路径
        
        Args:
            path: 数据库文件路径
        """
        self.db_path = path
    
    def _create_engine(self) -> bool:
        """
        创建数据库引擎
        
        Returns:
            bool: 引擎创建是否成功
        """
        try:
            if self.db_type == "sqlite":
                # SQLite连接
                self.engine = create_engine(f"sqlite:///{self.db_path}")
            elif self.db_type == "postgresql":
                # PostgreSQL连接
                host = self.db_config.get("host", "localhost")
                port = self.db_config.get("port", 5432)
                user = self.db_config.get("user", "postgres")
                password = self.db_config.get("password", "")
                dbname = self.db_config.get("dbname", "project2025")
                
                self.engine = create_engine(
                    f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
                )
            elif self.db_type == "mysql":
                # MySQL连接
                host = self.db_config.get("host", "localhost")
                port = self.db_config.get("port", 3306)
                user = self.db_config.get("user", "root")
                password = self.db_config.get("password", "")
                dbname = self.db_config.get("dbname", "project2025")
                
                self.engine = create_engine(
                    f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
                )
            else:
                print(f"不支持的数据库类型: {self.db_type}")
                return False
            
            return True
        except Exception as e:
            print(f"创建数据库引擎时出错: {str(e)}")
            return False
    
    def initialize_database(self) -> bool:
        """
        初始化数据库
        
        Returns:
            bool: 初始化是否成功
        """
        # 如果是SQLite且不存在父目录，创建目录
        if self.db_type == "sqlite":
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
        
        # 创建引擎
        if not self._create_engine():
            return False
        
        # 尝试连接
        try:
            self.connection = self.engine.connect()
            return True
        except Exception as e:
            print(f"连接数据库时出错: {str(e)}")
            return False
    
    def import_schema(self, schema_sql: str) -> Tuple[bool, str]:
        """
        导入数据库模式
        
        Args:
            schema_sql: 包含表定义的SQL语句
            
        Returns:
            Tuple[bool, str]: 成功标志和消息
        """
        if not self.engine:
            if not self._create_engine():
                return False, "数据库引擎未初始化"
        
        try:
            # 创建连接
            with self.engine.begin() as conn:
                # 执行模式创建语句
                conn.execute(text(schema_sql))
            
            # 刷新元数据
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            return True, "成功导入数据库模式"
        except Exception as e:
            return False, f"导入模式失败: {str(e)}"
    
    def list_tables(self) -> List[Tuple[str, int]]:
        """
        列出数据库中的所有表
        
        Returns:
            List[Tuple[str, int]]: 表名和列数的列表
        """
        if not self.engine:
            if not self._create_engine():
                return []
        
        try:
            # 使用inspector获取表信息
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            
            result = []
            for table_name in table_names:
                columns = inspector.get_columns(table_name)
                result.append((table_name, len(columns)))
            
            return result
        except Exception as e:
            print(f"获取表列表时出错: {str(e)}")
            return []
    
    def execute_query(
        self, query: str
    ) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            
        Returns:
            Tuple[bool, Union[Dict[str, Any], str]]: 成功标志和结果
        """
        if not self.engine:
            if not self._create_engine():
                return False, "数据库引擎未初始化"
        
        try:
            with self.engine.connect() as conn:
                # 执行查询
                result = conn.execute(text(query))
                
                # 如果是SELECT查询，返回结果集
                if query.strip().upper().startswith("SELECT"):
                    columns = result.keys()
                    data = [list(row) for row in result.fetchall()]
                    
                    return True, {
                        "columns": columns,
                        "data": data,
                        "row_count": len(data)
                    }
                else:
                    # 非查询操作，返回受影响的行数
                    return True, {
                        "row_count": result.rowcount,
                        "message": f"执行成功，影响 {result.rowcount} 行"
                    }
        
        except Exception as e:
            return False, f"查询执行失败: {str(e)}"
    
    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            Optional[Dict[str, Any]]: 表结构信息或None
        """
        if not self.engine:
            if not self._create_engine():
                return None
        
        try:
            inspector = inspect(self.engine)
            
            if table_name not in inspector.get_table_names():
                return None
            
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                "table_name": table_name,
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            }
        
        except Exception as e:
            print(f"获取表结构时出错: {str(e)}")
            return None
    
    def reset_database(self) -> bool:
        """
        重置数据库，删除所有表
        
        Returns:
            bool: 重置是否成功
        """
        if not self.engine:
            if not self._create_engine():
                return False
        
        try:
            # 删除所有表
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            with self.engine.begin() as conn:
                # 按照正确的顺序删除表（考虑外键约束）
                self.metadata.drop_all(conn)
            
            return True
        
        except Exception as e:
            print(f"重置数据库时出错: {str(e)}")
            return False
    
    def get_all_schema_info(self) -> Dict[str, Any]:
        """
        获取数据库所有表的结构信息，用于自然语言处理
        
        Returns:
            Dict[str, Any]: 数据库模式信息
        """
        if not self.engine:
            if not self._create_engine():
                return {}
        
        try:
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            
            schema_info = {}
            for table_name in table_names:
                schema_info[table_name] = self.get_table_schema(table_name)
            
            return schema_info
        
        except Exception as e:
            print(f"获取数据库模式信息时出错: {str(e)}")
            return {} 