# SQL助手

SQL助手是一个功能强大的SQL命令行工具，支持SQL检查、可视化查询结果以及自然语言转SQL功能。

## 主要功能

- **数据库管理**：初始化、创建数据库和导入关系模式
- **SQL检查**：分析SQL语句的语法正确性，提供用户友好的错误信息和修改建议
- **查询可视化**：直观展示查询结果和执行计划
- **自然语言查询**：将自然语言转换为SQL查询
- **系统重置**：清除数据库以便重新开始

## 安装

### 使用pip安装

```bash
pip install sqlassistant
```

### 从源码安装

```bash
git clone https://github.com/example/sqlassistant.git
cd sqlassistant
pip install -e .
```

## 配置文件

首次运行时，SQL助手会在用户主目录的`.sqlassistant`文件夹下创建配置文件`config.yaml`。
您可以根据需要修改该配置文件，主要配置项包括：

```yaml
database:
  type: postgresql        # 数据库类型
  host: localhost         # 主机地址
  port: 5432              # 端口号
  user: postgres          # 用户名
  password: postgres      # 密码
  dbname: postgres        # 数据库名

parser:
  dialect: postgresql     # SQL方言
  error_format: friendly  # 错误格式
  provide_suggestions: true  # 是否提供修改建议

visualizer:
  engine: plotly          # 可视化引擎
  theme: light            # 主题
  show_query_plan: true   # 是否显示查询计划

nlp:
  model_type: local       # 模型类型：local 或 online
  local_model:
    provider: huggingface  # 本地模型提供商
    model_path: models/mistral-7b-sql-finetuned  # 模型路径
    device: cuda           # 设备：cuda 或 cpu
    max_tokens: 1024       # 最大token数
    temperature: 0.2       # 温度参数
  online_model:
    provider: qwen         # 在线模型提供商：qwen 或 deepseek
    model_name: qwen-max   # 模型名称
    api_key: ""            # API密钥
    max_tokens: 1024       # 最大token数
    temperature: 0.2       # 温度参数
```

## 使用方法

SQL助手提供以下命令：

### 初始化数据库

```bash
sqlassistant init [--path PATH]
```

### 管理数据库模式

导入模式：
```bash
sqlassistant schema import --file schema.sql
```

列出所有表：
```bash
sqlassistant schema list
```

### 检查SQL语句

```bash
sqlassistant check "SELECT * FROM users WHERE id = 1"
```

### 执行查询

```bash
sqlassistant query "SELECT * FROM users LIMIT 10"
```

带可视化：
```bash
sqlassistant query "SELECT department, COUNT(*) FROM employees GROUP BY department" --visualize
```

保存可视化结果：
```bash
sqlassistant query "SELECT department, COUNT(*) FROM employees GROUP BY department" --visualize --output result.png
```

### 自然语言查询

```bash
sqlassistant nlquery "显示所有用户的邮箱和注册日期"
```

带可视化：
```bash
sqlassistant nlquery "每个部门的员工数量" --visualize
```

### 重置系统

```bash
sqlassistant reset
```

强制重置：
```bash
sqlassistant reset --force
```

## 数据库支持

SQL助手优先支持PostgreSQL数据库，可以通过配置文件调整数据库连接参数。

## 自然语言处理

SQL助手支持两种模式的自然语言处理：

1. **本地模式**：使用Hugging Face模型在本地设备上进行文本到SQL的转换。要求本地安装相应的模型。

2. **在线模式**：使用阿里云Qwen或DeepSeek的API服务进行文本到SQL的转换。需要提供对应的API密钥。

## 常见问题

### Q: 如何设置API密钥？

A: 您可以直接修改配置文件，或通过环境变量设置：

```bash
export QWEN_API_KEY="your_api_key_here"
# 或
export DEEPSEEK_API_KEY="your_api_key_here"
```

### Q: 支持哪些可视化类型？

A: SQL助手会根据查询类型自动选择合适的可视化类型，包括：
- 聚合分析：柱状图、饼图、热图
- 时间序列：线图、面积图
- 多表关联：散点图、相关性矩阵
- 查询计划：树状图

### Q: 如何使用本地模型？

A: 确保已下载相应的模型，并在配置文件中正确设置模型路径。然后将`model_type`设置为`local`。

## 许可证

MIT 