# SQL助手使用指南

这篇文档将帮助您了解如何使用SQL助手的各项功能。

## 安装

```bash
# 方法1：从源码安装
git clone https://github.com/yourusername/sqlassistant.git
cd sqlassistant
pip install -e .

# 方法2：直接使用
python -m sqlassistant <命令>
```

## 初始化数据库

在使用SQL助手前，首先需要初始化数据库：

```bash
# 使用默认设置初始化
sqlassistant init

# 指定数据库路径
sqlassistant init --path /path/to/your/database.db
```

## 导入关系模式

SQL助手需要导入关系模式（表结构）才能工作：

```bash
# 从SQL文件导入模式
sqlassistant schema import --file your_schema.sql

# 列出当前数据库中的表
sqlassistant schema list
```

### 关系模式文件示例 (your_schema.sql)

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 帖子表
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 检查SQL语句

您可以使用SQL助手来检查SQL语句是否存在语法或语义错误：

```bash
# 检查SQL语句
sqlassistant check "SELECT * FROM users WHERE age > 18"

# 指定SQL方言
sqlassistant check "SELECT * FROM users LIMIT 10" --dialect mysql
```

## 执行查询

在数据库中执行SQL查询并查看结果：

```bash
# 执行基本查询
sqlassistant query "SELECT * FROM users"

# 执行查询并可视化结果
sqlassistant query "SELECT age, COUNT(*) as count FROM users GROUP BY age" --visualize

# 将可视化结果保存到文件
sqlassistant query "SELECT * FROM users JOIN posts ON users.id = posts.user_id" --visualize --output result.png
```

## 自然语言查询

使用自然语言而非SQL语法来查询数据库：

```bash
# 基本自然语言查询
sqlassistant nlquery "查找年龄大于30岁的用户"

# 复杂自然语言查询并可视化
sqlassistant nlquery "统计每个年龄段的用户数量并绘制柱状图" --visualize

# 保存可视化结果
sqlassistant nlquery "找出发帖最多的前5名用户" --visualize --output top_users.png
```

## 重置系统

如果需要清除数据库并重新开始：

```bash
# 重置系统（会提示确认）
sqlassistant reset

# 强制重置，不提示确认
sqlassistant reset --force
```

## 样例使用场景

### 场景1：数据分析

```bash
# 导入样本数据
sqlassistant schema import --file sample_data.sql

# 使用自然语言分析数据
sqlassistant nlquery "每月新用户注册量趋势" --visualize
sqlassistant nlquery "用户年龄分布" --visualize
```

### 场景2：SQL学习辅助

```bash
# 检查学生编写的SQL语句
sqlassistant check "SELECT FROM users WHERE"

# 使用自然语言生成SQL
sqlassistant nlquery "查找最近7天内发布的帖子"
```

### 场景3：数据库探索

```bash
# 列出所有表
sqlassistant schema list

# 查看查询计划
sqlassistant query "SELECT * FROM users JOIN posts ON users.id = posts.user_id" --visualize
```

## 提示和技巧

1. 对于自然语言查询，尽量使用清晰、具体的描述
2. 使用 `--visualize` 选项可以更直观地理解查询结果
3. 查询执行计划可以帮助您优化复杂查询
4. 设置配置文件 (`config.yaml`) 可以自定义系统行为

## 故障排除

如果遇到问题，可以查看日志文件 (`logs/sqlassistant.log`) 获取详细信息。

常见问题：
- 数据库连接失败：检查数据库路径是否正确
- 可视化失败：确保正确安装了matplotlib或plotly
- 自然语言处理错误：检查LLM模型配置（参见`docs/llm_integration.md`）

---

有关更多详细信息和高级功能，请查看[项目GitHub仓库](https://github.com/yourusername/sqlassistant)。 