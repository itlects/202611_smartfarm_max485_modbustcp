CREATE DATABASE IF NOT EXISTS smartfarm CHARACTER SET utf8mb4;
USE smartfarm;
CREATE TABLE IF NOT EXISTS events (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 kind VARCHAR(24) NOT NULL,
 unit TINYINT NOT NULL,
 payload JSON NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_created_at(created_at)
);
-- Execute separately as root, replacing the local DB password:
-- CREATE USER IF NOT EXISTS 'smartfarm'@'localhost' IDENTIFIED BY 'YOUR_DB_PASSWORD';
-- GRANT SELECT, INSERT ON smartfarm.* TO 'smartfarm'@'localhost';
