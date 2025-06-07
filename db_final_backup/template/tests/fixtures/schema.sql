-- 测试数据库模式
-- 用于SQL助手单元测试和集成测试

-- 用户表
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 部门表
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(100),
    manager_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_manager FOREIGN KEY (manager_id) REFERENCES users(user_id)
);

-- 员工表
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    dept_id INTEGER NOT NULL,
    position VARCHAR(50),
    salary NUMERIC(10, 2),
    hire_date DATE NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_department FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 项目表
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12, 2),
    dept_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, completed, cancelled
    CONSTRAINT fk_department FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 项目成员表
CREATE TABLE project_members (
    project_id INTEGER NOT NULL,
    emp_id INTEGER NOT NULL,
    role VARCHAR(50),
    join_date DATE DEFAULT CURRENT_DATE,
    hours_allocated INTEGER,
    PRIMARY KEY (project_id, emp_id),
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES projects(project_id),
    CONSTRAINT fk_employee FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 任务表
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    description TEXT,
    assigned_to INTEGER,
    created_by INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'todo', -- todo, in_progress, review, done
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high, urgent
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES projects(project_id),
    CONSTRAINT fk_assigned_to FOREIGN KEY (assigned_to) REFERENCES employees(emp_id),
    CONSTRAINT fk_created_by FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- 日志表
CREATE TABLE activity_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    activity_type VARCHAR(50) NOT NULL, -- login, task_update, project_create, etc.
    description TEXT,
    entity_type VARCHAR(50), -- users, projects, tasks, etc.
    entity_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 示例视图：员工详细信息视图
CREATE VIEW employee_details AS
SELECT 
    e.emp_id,
    u.username,
    u.email,
    d.dept_name,
    e.position,
    e.salary,
    e.hire_date,
    d.location
FROM employees e
JOIN users u ON e.user_id = u.user_id
JOIN departments d ON e.dept_id = d.dept_id;

-- 示例视图：项目统计视图
CREATE VIEW project_stats AS
SELECT 
    p.project_id,
    p.project_name,
    p.status,
    COUNT(DISTINCT pm.emp_id) AS total_members,
    COUNT(t.task_id) AS total_tasks,
    SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS completed_tasks,
    d.dept_name AS responsible_department
FROM projects p
LEFT JOIN project_members pm ON p.project_id = pm.project_id
LEFT JOIN tasks t ON p.project_id = t.project_id
LEFT JOIN departments d ON p.dept_id = d.dept_id
GROUP BY p.project_id, p.project_name, p.status, d.dept_name;

-- 示例数据
-- 用户数据
INSERT INTO users (username, email, password_hash, created_at) VALUES
('admin', 'admin@example.com', 'hashed_password_1', '2023-01-01 10:00:00'),
('john_doe', 'john@example.com', 'hashed_password_2', '2023-01-02 11:30:00'),
('jane_smith', 'jane@example.com', 'hashed_password_3', '2023-01-03 09:15:00'),
('robert_johnson', 'robert@example.com', 'hashed_password_4', '2023-01-04 14:20:00'),
('mary_williams', 'mary@example.com', 'hashed_password_5', '2023-01-05 16:45:00');

-- 部门数据
INSERT INTO departments (dept_name, location, manager_id) VALUES
('Engineering', 'Building A, Floor 2', 1),
('Marketing', 'Building B, Floor 1', 3),
('Finance', 'Building A, Floor 3', 4),
('Human Resources', 'Building B, Floor 2', 5);

-- 员工数据
INSERT INTO employees (user_id, dept_id, position, salary, hire_date) VALUES
(1, 1, 'CTO', 150000.00, '2022-01-15'),
(2, 1, 'Senior Developer', 120000.00, '2022-02-20'),
(3, 2, 'Marketing Director', 125000.00, '2022-03-10'),
(4, 3, 'Finance Manager', 130000.00, '2022-04-05'),
(5, 4, 'HR Manager', 115000.00, '2022-05-12');

-- 项目数据
INSERT INTO projects (project_name, description, start_date, end_date, budget, dept_id, status) VALUES
('Website Redesign', 'Redesign company website with modern UI/UX', '2023-02-01', '2023-05-31', 50000.00, 1, 'active'),
('Q2 Marketing Campaign', 'Summer promotional campaign', '2023-03-15', '2023-06-15', 35000.00, 2, 'active'),
('Financial Reporting System', 'Implement new financial reporting system', '2023-04-01', '2023-08-31', 75000.00, 3, 'active'),
('Employee Training Program', 'Develop training materials for new hires', '2023-05-01', '2023-07-31', 25000.00, 4, 'pending');

-- 项目成员数据
INSERT INTO project_members (project_id, emp_id, role, hours_allocated) VALUES
(1, 1, 'Project Manager', 20),
(1, 2, 'Lead Developer', 30),
(2, 3, 'Campaign Manager', 25),
(3, 4, 'System Architect', 30),
(4, 5, 'Program Coordinator', 15),
(2, 2, 'Technical Advisor', 10);

-- 任务数据
INSERT INTO tasks (project_id, task_name, description, assigned_to, created_by, status, priority, due_date) VALUES
(1, 'Design Homepage', 'Create mockups for the homepage', 2, 1, 'in_progress', 'high', '2023-02-28'),
(1, 'Implement User Authentication', 'Set up user login and registration', 2, 1, 'todo', 'medium', '2023-03-15'),
(2, 'Create Social Media Content', 'Prepare posts for Facebook and Instagram', 3, 3, 'in_progress', 'medium', '2023-04-10'),
(3, 'Database Schema Design', 'Design database schema for the reporting system', 4, 4, 'done', 'high', '2023-04-20'),
(4, 'Create Onboarding Slides', 'Develop presentation for new employee orientation', 5, 5, 'review', 'medium', '2023-05-30'); 