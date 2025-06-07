-- 智能家居系统示例数据库模式

-- 用户表
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 房屋表
CREATE TABLE homes (
    home_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    area_sqm REAL,
    floors INTEGER DEFAULT 1,
    bedrooms INTEGER,
    bathrooms INTEGER,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 房间表
CREATE TABLE rooms (
    room_id INTEGER PRIMARY KEY,
    home_id INTEGER,
    name TEXT NOT NULL,
    room_type TEXT NOT NULL, -- 客厅、卧室、厨房等
    floor INTEGER DEFAULT 1,
    area_sqm REAL,
    FOREIGN KEY (home_id) REFERENCES homes(home_id)
);

-- 设备类型表
CREATE TABLE device_types (
    type_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    manufacturer TEXT,
    category TEXT -- 照明、温控、安防等
);

-- 设备表
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY,
    room_id INTEGER,
    type_id INTEGER,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'offline', -- online, offline, maintenance
    ip_address TEXT,
    mac_address TEXT,
    firmware_version TEXT,
    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_maintenance TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    FOREIGN KEY (type_id) REFERENCES device_types(type_id)
);

-- 设备使用记录表
CREATE TABLE device_usage (
    usage_id INTEGER PRIMARY KEY,
    device_id INTEGER,
    user_id INTEGER,
    action TEXT NOT NULL, -- 打开、关闭、调节等
    value TEXT, -- 设备调节的值，如温度、亮度等
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 安防事件表
CREATE TABLE security_events (
    event_id INTEGER PRIMARY KEY,
    device_id INTEGER,
    event_type TEXT NOT NULL, -- 入侵检测、烟雾警报等
    description TEXT,
    severity TEXT, -- 低、中、高
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT 0,
    resolution_notes TEXT,
    resolution_timestamp TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- 自动化规则表
CREATE TABLE automation_rules (
    rule_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    trigger_condition TEXT NOT NULL, -- 触发条件，如"温度高于30度"
    action TEXT NOT NULL, -- 执行操作，如"打开空调"
    status BOOLEAN DEFAULT 1, -- 启用/禁用
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 用户反馈表
CREATE TABLE user_feedback (
    feedback_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    rating INTEGER, -- 1-5星评价
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending', -- pending, reviewed, resolved
    response TEXT,
    response_timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 系统日志表
CREATE TABLE system_logs (
    log_id INTEGER PRIMARY KEY,
    component TEXT NOT NULL, -- 系统组件名
    log_level TEXT NOT NULL, -- debug, info, warning, error, critical
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 能源消耗统计表
CREATE TABLE energy_consumption (
    consumption_id INTEGER PRIMARY KEY,
    device_id INTEGER,
    power_watts REAL,
    duration_minutes INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    energy_kwh REAL, -- 千瓦时
    cost REAL, -- 能源成本
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- 示例视图：设备使用频率视图
CREATE VIEW device_usage_frequency AS
SELECT 
    d.device_id,
    d.name AS device_name,
    dt.name AS device_type,
    r.name AS room_name,
    h.name AS home_name,
    COUNT(du.usage_id) AS usage_count,
    MAX(du.timestamp) AS last_used
FROM devices d
JOIN device_types dt ON d.type_id = dt.type_id
JOIN rooms r ON d.room_id = r.room_id
JOIN homes h ON r.home_id = h.home_id
LEFT JOIN device_usage du ON d.device_id = du.device_id
GROUP BY d.device_id; 