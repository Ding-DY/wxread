CREATE DATABASE IF NOT EXISTS wxread DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE wxread;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    headers TEXT NOT NULL,
    cookies TEXT NOT NULL,
    read_num INT DEFAULT 120,
    push_method VARCHAR(20),
    pushplus_token VARCHAR(255),
    telegram_bot_token VARCHAR(255),
    telegram_chat_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_running BOOLEAN DEFAULT FALSE,
    last_run TIMESTAMP,
    schedule_type VARCHAR(20),
    schedule_time TIME DEFAULT NULL,
    schedule_days VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS task_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'stopped'
    error_message TEXT,
    read_minutes INT,
    FOREIGN KEY (config_id) REFERENCES user_configs(id)
); 