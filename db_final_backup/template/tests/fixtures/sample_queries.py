"""
样例SQL查询集合，用于测试SQL解析器和可视化模块
"""

# 有效的简单查询
VALID_SIMPLE_QUERIES = [
    {
        "description": "查询所有用户",
        "sql": "SELECT * FROM users;",
        "visualization_type": "table"
    },
    {
        "description": "查询所有部门名称和位置",
        "sql": "SELECT dept_name, location FROM departments;",
        "visualization_type": "table"
    },
    {
        "description": "查询高薪员工",
        "sql": "SELECT * FROM employees WHERE salary > 100000;",
        "visualization_type": "table"
    },
    {
        "description": "按薪资降序排列员工",
        "sql": "SELECT emp_id, username, position, salary FROM employee_details ORDER BY salary DESC;",
        "visualization_type": "table"
    }
]

# 有效的聚合查询
VALID_AGGREGATE_QUERIES = [
    {
        "description": "各部门员工数量",
        "sql": """
        SELECT d.dept_name, COUNT(e.emp_id) AS employee_count
        FROM departments d
        LEFT JOIN employees e ON d.dept_id = e.dept_id
        GROUP BY d.dept_name
        ORDER BY employee_count DESC;
        """,
        "visualization_type": "bar"
    },
    {
        "description": "各部门平均薪资",
        "sql": """
        SELECT d.dept_name, AVG(e.salary) AS avg_salary
        FROM departments d
        JOIN employees e ON d.dept_id = e.dept_id
        GROUP BY d.dept_name
        ORDER BY avg_salary DESC;
        """,
        "visualization_type": "bar"
    },
    {
        "description": "项目状态分布",
        "sql": """
        SELECT status, COUNT(*) AS project_count
        FROM projects
        GROUP BY status;
        """,
        "visualization_type": "pie"
    },
    {
        "description": "任务优先级分布",
        "sql": """
        SELECT priority, COUNT(*) AS task_count
        FROM tasks
        GROUP BY priority
        ORDER BY 
            CASE 
                WHEN priority = 'urgent' THEN 1
                WHEN priority = 'high' THEN 2
                WHEN priority = 'medium' THEN 3
                WHEN priority = 'low' THEN 4
            END;
        """,
        "visualization_type": "pie"
    }
]

# 有效的复杂查询
VALID_COMPLEX_QUERIES = [
    {
        "description": "项目任务完成率",
        "sql": """
        WITH project_task_stats AS (
            SELECT 
                p.project_id,
                p.project_name,
                COUNT(*) AS total_tasks,
                SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS completed_tasks
            FROM projects p
            LEFT JOIN tasks t ON p.project_id = t.project_id
            GROUP BY p.project_id, p.project_name
        )
        SELECT 
            project_name,
            total_tasks,
            completed_tasks,
            CASE 
                WHEN total_tasks = 0 THEN 0
                ELSE ROUND((completed_tasks::float / total_tasks) * 100, 2)
            END AS completion_percentage
        FROM project_task_stats
        ORDER BY completion_percentage DESC;
        """,
        "visualization_type": "bar"
    },
    {
        "description": "员工工时分配",
        "sql": """
        SELECT 
            u.username,
            p.project_name,
            pm.hours_allocated
        FROM project_members pm
        JOIN employees e ON pm.emp_id = e.emp_id
        JOIN users u ON e.user_id = u.user_id
        JOIN projects p ON pm.project_id = p.project_id
        ORDER BY u.username, pm.hours_allocated DESC;
        """,
        "visualization_type": "stacked_bar"
    },
    {
        "description": "部门项目预算分析",
        "sql": """
        SELECT 
            d.dept_name,
            COUNT(p.project_id) AS project_count,
            SUM(p.budget) AS total_budget,
            ROUND(AVG(p.budget), 2) AS avg_project_budget,
            MIN(p.budget) AS min_project_budget,
            MAX(p.budget) AS max_project_budget
        FROM departments d
        LEFT JOIN projects p ON d.dept_id = p.dept_id
        GROUP BY d.dept_name
        ORDER BY total_budget DESC NULLS LAST;
        """,
        "visualization_type": "multi_bar"
    },
    {
        "description": "任务状态随时间变化",
        "sql": """
        SELECT 
            DATE_TRUNC('week', t.created_at)::date AS week_start,
            t.status,
            COUNT(*) AS task_count
        FROM tasks t
        GROUP BY week_start, t.status
        ORDER BY week_start, t.status;
        """,
        "visualization_type": "line"
    }
]

# 无效的查询（语法错误）
INVALID_SYNTAX_QUERIES = [
    {
        "description": "SELECT缺少FROM子句",
        "sql": "SELECT username, email;",
        "error_type": "syntax"
    },
    {
        "description": "WHERE子句语法错误",
        "sql": "SELECT * FROM users WHERE;",
        "error_type": "syntax"
    },
    {
        "description": "GROUP BY语法错误",
        "sql": "SELECT dept_name, COUNT(*) FROM departments GROUP;",
        "error_type": "syntax"
    },
    {
        "description": "JOIN语法错误",
        "sql": "SELECT * FROM users JOIN employees;",
        "error_type": "syntax"
    }
]

# 无效的查询（语义错误）
INVALID_SEMANTIC_QUERIES = [
    {
        "description": "表不存在",
        "sql": "SELECT * FROM nonexistent_table;",
        "error_type": "semantic"
    },
    {
        "description": "列不存在",
        "sql": "SELECT username, nonexistent_column FROM users;",
        "error_type": "semantic"
    },
    {
        "description": "分组错误",
        "sql": "SELECT username, COUNT(*) FROM users;",
        "error_type": "semantic"
    },
    {
        "description": "数据类型不匹配",
        "sql": "SELECT * FROM users WHERE user_id = 'abc';",
        "error_type": "semantic"
    }
]

# 自然语言查询对
NL_QUERY_PAIRS = [
    {
        "natural_language": "显示所有用户的邮箱和注册日期",
        "expected_sql": "SELECT username, email, created_at FROM users;"
    },
    {
        "natural_language": "列出薪资超过12万的员工",
        "expected_sql": "SELECT * FROM employees WHERE salary > 120000;"
    },
    {
        "natural_language": "每个部门的平均薪资是多少？",
        "expected_sql": """
        SELECT d.dept_name, AVG(e.salary) AS average_salary
        FROM departments d
        JOIN employees e ON d.dept_id = e.dept_id
        GROUP BY d.dept_name;
        """
    },
    {
        "natural_language": "哪个项目的完成任务比例最高？",
        "expected_sql": """
        SELECT 
            p.project_name,
            COUNT(t.task_id) AS total_tasks,
            SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS completed_tasks,
            SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END)::float / COUNT(t.task_id) AS completion_ratio
        FROM projects p
        LEFT JOIN tasks t ON p.project_id = t.project_id
        GROUP BY p.project_name
        ORDER BY completion_ratio DESC
        LIMIT 1;
        """
    }
]


def get_all_valid_queries():
    """获取所有有效的查询列表"""
    return VALID_SIMPLE_QUERIES + VALID_AGGREGATE_QUERIES + VALID_COMPLEX_QUERIES


def get_all_invalid_queries():
    """获取所有无效的查询列表"""
    return INVALID_SYNTAX_QUERIES + INVALID_SEMANTIC_QUERIES 