# SQL助手测试框架

本目录包含SQL助手项目的测试框架和测试用例。

## 测试结构

```
tests/
├── unit/                 # 单元测试
│   ├── test_db.py        # 数据库模块测试
│   ├── test_parser.py    # SQL解析器测试
│   ├── test_visualizer.py# 可视化模块测试
│   ├── test_nlp.py       # 自然语言处理测试
│   └── test_utils.py     # 工具函数测试
│
├── integration/          # 集成测试
│   ├── test_cli.py       # 命令行接口测试
│   └── test_workflow.py  # 工作流程测试
│
├── fixtures/             # 测试数据和固定装置
│   ├── schema.sql        # 测试用数据库模式
│   ├── sample_queries.py # 样例查询
│   └── mock_responses.py # 模拟响应数据
│
├── conftest.py           # pytest配置和共享夹具
└── README.md             # 本文档
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试模块

```bash
pytest tests/unit/test_db.py
```

### 运行特定测试函数

```bash
pytest tests/unit/test_db.py::test_initialize_database
```

### 运行带标记的测试

```bash
pytest -m "slow"  # 运行标记为slow的测试
pytest -m "not slow"  # 运行除标记为slow外的所有测试
```

## 编写测试的规范

### 1. 测试命名约定

- 测试文件名应以`test_`开头
- 测试函数名应以`test_`开头
- 测试类名应以`Test`开头

### 2. 测试结构

每个测试函数应遵循以下结构：

```python
def test_function_name():
    # 1. 准备 - 设置测试环境和数据
    # ...
    
    # 2. 执行 - 调用被测试的函数
    # ...
    
    # 3. 断言 - 验证结果
    # ...
```

### 3. 使用夹具

使用pytest夹具来设置和清理测试环境：

```python
@pytest.fixture
def db_manager():
    # 设置
    config = {...}
    manager = DatabaseManager(config)
    
    yield manager
    
    # 清理
    manager.reset_database()

def test_with_fixture(db_manager):
    # 使用db_manager夹具
    result = db_manager.initialize_database()
    assert result == True
```

### 4. 模拟外部依赖

使用`unittest.mock`或`pytest-mock`模拟外部依赖：

```python
def test_with_mock(mocker):
    # 模拟外部API
    mock_api = mocker.patch('sqlassistant.nlp.Generation.call')
    mock_api.return_value = {...}  # 模拟返回值
    
    # 测试使用模拟API的函数
    processor = NLProcessor(config)
    result = processor.translate_to_sql("查询所有用户")
    
    assert result[0] == True  # 检查是否成功
    assert "SELECT" in result[1]  # 检查SQL语句
```

### 5. 参数化测试

使用参数化测试处理多个测试案例：

```python
@pytest.mark.parametrize("query,expected", [
    ("SELECT * FROM users", True),
    ("SELECT FROM users", False),
    ("INSERT INTO users VALUES (1, 'name')", True)
])
def test_check_query_parametrized(query, expected, parser):
    is_valid, _, _ = parser.check_query(query)
    assert is_valid == expected
```

### 6. 测试标记

使用标记分类测试：

```python
@pytest.mark.slow  # 标记为慢测试
def test_large_database():
    # 测试大型数据库操作
    ...

@pytest.mark.integration  # 标记为集成测试
def test_full_workflow():
    # 测试完整工作流程
    ...
```

## 测试覆盖率

使用`pytest-cov`检查测试覆盖率：

```bash
pytest --cov=sqlassistant tests/
```

生成HTML覆盖率报告：

```bash
pytest --cov=sqlassistant --cov-report=html tests/
```

## 持续集成

项目使用GitHub Actions进行持续集成。每次推送代码时，CI系统会：

1. 在多个Python版本上运行测试
2. 检查代码风格
3. 运行静态代码分析
4. 生成测试覆盖率报告

请确保在提交代码前本地运行测试，并维持或提高测试覆盖率。 