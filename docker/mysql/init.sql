-- Smart Pet Feeder Database Initialization
-- Auto-executed on first MySQL container startup

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS smart_pet_feeder;
USE smart_pet_feeder;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pets table
CREATE TABLE IF NOT EXISTS pets (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    species ENUM('cat', 'dog') NOT NULL,
    category ENUM('kitten', 'neutered_adult', 'intact_adult', 'senior') NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    kcal_per_kg INT NOT NULL,
    daily_target_grams INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Devices table (ESP32 feeders)
CREATE TABLE IF NOT EXISTS devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT NOT NULL,
    device_sn VARCHAR(50) UNIQUE NOT NULL,
    device_name VARCHAR(100),
    max_capacity INT DEFAULT 600,
    current_stock INT DEFAULT 600,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Feeding schedules
CREATE TABLE IF NOT EXISTS feeding_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    time TIME NOT NULL,
    grams_per_feed INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Feeding logs
CREATE TABLE IF NOT EXISTS feeding_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    grams_out INT NOT NULL,
    method ENUM('manual', 'otomatis') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_timestamp (device_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pantry refills
CREATE TABLE IF NOT EXISTS pantry_refills (
    refill_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    grams_added INT NOT NULL,
    refilled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    INDEX idx_refilled_at (refilled_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user for development (password: admin123)
-- Note: In production, remove this or use stronger password
INSERT IGNORE INTO users (username, email, password_hash) VALUES 
('admin', 'admin@smartpetfeeder.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF6q1vQy');

FLUSH PRIVILEGES;
