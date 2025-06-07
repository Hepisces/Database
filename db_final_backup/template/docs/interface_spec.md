# SQL助手接口规范文档

本文档定义了SQL助手各模块间的接口规范，包括输入输出格式、错误处理约定和模块交互方式，以确保团队成员能够独立开发各模块的同时保持系统整体功能的正常运行。

## 模块依赖关系

```
   +-------------+
   |    cli.py   |
   +------+------+
          |
          v
+------+  |  +------+  +------+  +------+
|utils.|<-+->|db.py |  |parser|  | nlp  |
|  py  |     |      |  |.py   |  | .py  |
+------+     +---+--+  +---+--+  +---+--+
                 ^         ^        ^
                 |         |        |
                 v         v        v
                 +----+----+----+---+
                      |visualizer.py|
                      +-------------+
```

## 1. 通用规范

### 1.1 返回值格式

所有可能失败的函数应返回元组 `(success, result_or_error)`，其中:
- `success`：布尔值，表示操作是否成功
- `result_or_error`：操作成功时为结果数据，失败时为错误消息（字符串）

### 1.2 错误处理

- 所有模块内部应捕获并处理异常，避免异常传播到CLI层
- 使用日志记录详细错误信息，向调用者返回用户友好的错误消息
- 错误消息应简洁明了，并尽可能提供修复建议

### 1.3 日志记录

- 使用 `utils.py` 中的日志函数记录信息
- 各模块使用独立的日志记录器，命名为 `sqlassistant.{module_name}`
- 日志级别约定：
  - DEBUG：详细调试信息
  - INFO：一般操作信息
  - WARNING：警告但不影响主要功能
  - ERROR：功能失败但程序可继续运行
  - CRITICAL：严重错误导致程序无法继续

### 1.4 配置项访问

- 所有模块通过构造函数接收完整的配置字典
- 模块内部从配置中提取自己需要的部分
- 避免直接修改配置字典

## 2. 数据库管理模块 (db.py)

### 2.1 DatabaseManager 类

#### 2.1.1 初始化

```python
def __init__(self, config: Dict[str, Any])
```
- 输入：配置字典，包含数据库连接信息
- 功能：初始化数据库管理器，但不创建连接

#### 2.1.2 设置数据库路径

```python
def set_db_path(self, path: str) -> None
```
- 输入：数据库路径字符串
- 输出：无
- 功能：设置数据库路径（对SQLite有效）

#### 2.1.3 初始化数据库

```python
def initialize_database(self) -> bool
```
- 输入：无
- 输出：布尔值，表示是否成功初始化
- 功能：创建/初始化数据库和必要的表结构

#### 2.1.4 导入关系模式

```python
def import_schema(self, schema_sql: str) -> Tuple[bool, str]
```
- 输入：包含建表语句的SQL字符串
- 输出：(操作是否成功, 结果或错误消息)
- 功能：将关系模式导入到数据库

#### 2.1.5 列出所有表

```python
def list_tables(self) -> List[Tuple[str, int]]
```
- 输入：无
- 输出：列表，每项为元组 (表名, 列数)
- 功能：列出数据库中的所有表及其列数

#### 2.1.6 执行查询

```python
def execute_query(self, query: str) -> Tuple[bool, Dict[str, Any]]
```
- 输入：SQL查询字符串
- 输出：(操作是否成功, 结果字典或错误消息)
- 结果字典格式：
  ```python
  {
      "columns": [列名列表],
      "data": [数据行列表],
      "row_count": 行数,
      "execution_time": 执行时间(秒)
  }
  ```

#### 2.1.7 获取模式信息

```python
def get_schema_info(self, table_name: Optional[str] = None) -> Dict[str, Any]
```
- 输入：（可选）表名
- 输出：数据库模式信息字典
- 功能：获取指定表或所有表的结构信息

#### 2.1.8 重置数据库

```python
def reset_database(self) -> bool
```
- 输入：无
- 输出：布尔值，表示是否成功重置
- 功能：清除数据库中的所有表和数据

## 3. SQL解析器模块 (parser.py)

### 3.1 SQLParser 类

#### 3.1.1 初始化

```python
def __init__(self, config: Dict[str, Any])
```
- 输入：配置字典
- 功能：初始化SQL解析器

#### 3.1.2 设置SQL方言

```python
def set_dialect(self, dialect: str) -> None
```
- 输入：SQL方言字符串（如"postgresql", "mysql", "sqlite"）
- 输出：无
- 功能：设置解析器使用的SQL方言

#### 3.1.3 检查查询

```python
def check_query(self, query: str) -> Tuple[bool, List[str], List[str]]
```
- 输入：SQL查询字符串
- 输出：元组 (是否有效, 错误列表, 建议列表)
- 功能：检查SQL语句的语法正确性并提供改进建议

#### 3.1.4 格式化查询

```python
def format_query(self, query: str) -> str
```
- 输入：SQL查询字符串
- 输出：格式化后的SQL字符串
- 功能：格式化SQL语句，使其更易读

#### 3.1.5 解析查询类型

```python
def parse_query_type(self, query: str) -> str
```
- 输入：SQL查询字符串
- 输出：查询类型字符串（如"SELECT", "INSERT", "UPDATE"等）
- 功能：判断SQL查询的类型

## 4. 查询可视化模块 (visualizer.py)

### 4.1 QueryVisualizer 类

#### 4.1.1 初始化

```python
def __init__(self, config: Dict[str, Any])
```
- 输入：配置字典
- 功能：初始化查询可视化器

#### 4.1.2 可视化查询结果

```python
def visualize_query_result(
    self, 
    query: str, 
    result: Dict[str, Any], 
    output_path: Optional[str] = None,
    title: Optional[str] = None
) -> bool
```
- 输入：
  - query: SQL查询字符串
  - result: 查询结果字典（与db.execute_query的返回格式一致）
  - output_path: （可选）输出文件路径
  - title: （可选）可视化标题
- 输出：布尔值，表示是否成功可视化
- 功能：可视化查询结果，如适用则保存到文件

#### 4.1.3 确定可视化类型

```python
def determine_visualization_type(self, query: str, result: Dict[str, Any]) -> str
```
- 输入：SQL查询和结果
- 输出：可视化类型字符串（如"bar", "line", "table"等）
- 功能：根据查询类型和结果数据自动确定适合的可视化类型

#### 4.1.4 可视化查询计划

```python
def visualize_query_plan(self, query: str, output_path: Optional[str] = None) -> bool
```
- 输入：
  - query: SQL查询字符串
  - output_path: （可选）输出文件路径
- 输出：布尔值，表示是否成功可视化
- 功能：可视化查询执行计划

## 5. 自然语言处理模块 (nlp.py)

### 5.1 NLProcessor 类

#### 5.1.1 初始化

```python
def __init__(self, config: Dict[str, Any])
```
- 输入：配置字典
- 功能：初始化自然语言处理器

#### 5.1.2 设置数据库模式

```python
def set_db_schema(self, schema: Dict[str, Any]) -> None
```
- 输入：数据库模式信息字典
- 输出：无
- 功能：设置数据库模式信息，用于生成更准确的SQL

#### 5.1.3 翻译为SQL

```python
def translate_to_sql(self, nl_query: str) -> Tuple[bool, str]
```
- 输入：自然语言查询字符串
- 输出：(操作是否成功, SQL查询或错误消息)
- 功能：将自然语言查询转换为SQL查询

#### 5.1.4 获取模型信息

```python
def get_model_info(self) -> Dict[str, str]
```
- 输入：无
- 输出：模型信息字典
- 功能：返回当前使用的模型信息

## 6. 工具函数模块 (utils.py)

### 6.1 配置函数

#### 6.1.1 加载配置

```python
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]
```
- 输入：（可选）配置文件路径
- 输出：配置字典
- 功能：加载配置文件并处理环境变量引用

#### 6.1.2 设置日志

```python
def setup_logging(config: Dict[str, Any]) -> None
```
- 输入：配置字典
- 输出：无
- 功能：根据配置设置日志系统

### 6.2 辅助函数

#### 6.2.1 格式化SQL

```python
def format_sql(sql: str) -> str
```
- 输入：SQL查询字符串
- 输出：格式化后的SQL字符串
- 功能：使用sqlparse格式化SQL语句

#### 6.2.2 创建目录

```python
def create_directory_if_not_exists(path: str) -> bool
```
- 输入：目录路径
- 输出：布尔值，表示是否成功创建或已存在
- 功能：如果目录不存在则创建

## 7. 命令行接口 (cli.py)

### 7.1 主要入口点

#### 7.1.1 主函数

```python
def main() -> None
```
- 输入：无（从命令行参数读取）
- 输出：无
- 功能：主程序入口点，初始化应用并处理命令行参数

### 7.2 命令函数

所有命令函数形式为：

```python
@app.command()
def command_name(arg1: Type, arg2: Type, ...) -> None
```

- 每个命令函数应处理一个特定的命令行命令
- 使用typer装饰器 `@app.command()` 标记
- 命令函数应妥善处理错误并通过退出码表示成功/失败

## 8. 数据结构规范

### 8.1 数据库模式信息

```python
{
    "table_name": {
        "columns": [
            {"name": "column_name", "type": "data_type", "nullable": bool, ...},
            ...
        ],
        "primary_keys": ["column_name", ...],
        "foreign_keys": [
            {
                "constrained_columns": ["column_name", ...],
                "referred_table": "table_name",
                "referred_columns": ["column_name", ...]
            },
            ...
        ],
        "indexes": [
            {"name": "index_name", "columns": ["column_name", ...]},
            ...
        ]
    },
    ...
}
```

### 8.2 查询结果

```python
{
    "columns": ["column_name", ...],
    "data": [
        [value1, value2, ...],  # 第一行
        [value1, value2, ...],  # 第二行
        ...
    ],
    "row_count": 整数,
    "execution_time": 浮点数  # 秒
}
```

## 9. 开发流程和规范

### 9.1 修改模块的步骤

1. 确保了解模块的接口规范（本文档）
2. 创建功能分支进行修改
3. 保持模块的公共接口不变
4. 添加或修改单元测试
5. 确保所有测试通过
6. 提交代码审查
7. 合并到主分支

### 9.2 兼容性规范

- **向后兼容**：模块更新不应破坏现有功能
- **参数扩展**：添加新参数时应提供默认值
- **返回值扩展**：可以扩展返回结构，但不应删除现有字段
- **废弃流程**：需要移除功能时，先标记为废弃并保留一段时间

### 9.3 编码风格

- 遵循 PEP 8 编码风格
- 使用类型注解
- 为所有函数和类编写文档字符串
- 使用 4 空格缩进
- 行长度限制为 100 字符

## 10. 测试规范

### 10.1 单元测试

- 每个模块应有相应的测试模块 `test_{module_name}.py`
- 使用 pytest 编写测试
- 测试覆盖率目标：80%以上
- 测试应独立且可重复运行

### 10.2 集成测试

- 使用测试数据库进行集成测试
- 测试命令行接口的完整功能流程
- 为每个主要用例编写端到端测试

## 11. 版本控制规范

### 11.1 版本号格式

遵循语义化版本控制 (Semantic Versioning) 2.0.0：
- MAJOR.MINOR.PATCH
- MAJOR：不兼容的 API 更改
- MINOR：向后兼容的功能性新增
- PATCH：向后兼容的问题修正

### 11.2 分支命名约定

- `main`：主分支，保持稳定可发布状态
- `feature/{feature-name}`：新功能分支
- `bugfix/{bug-id}`：错误修复分支
- `release/{version}`：发布准备分支 