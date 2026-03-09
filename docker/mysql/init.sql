-- Smart Pet Feeder Database — CODE-COMPATIBLE SCHEMA
-- Drop and recreate for clean migration

USE smart_pet_feeder;

-- ============================================================
--  Users table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Devices table
--  Code uses: id (PK), device_sn, owner_id, current_stock,
--             max_capacity, nickname
-- ============================================================
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_sn VARCHAR(50) UNIQUE NOT NULL,
    owner_id INT NOT NULL,
    nickname VARCHAR(100),
    max_capacity INT DEFAULT 600,
    current_stock INT DEFAULT 600,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Pets table
--  Code uses: device_id (FK to devices.id), name, species,
--             category, weight_kg, kcal_per_kg, daily_target_grams
-- ============================================================
CREATE TABLE IF NOT EXISTS pets (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    species ENUM('cat', 'dog') NOT NULL,
    category ENUM('kitten', 'neutered_adult', 'intact_adult', 'senior') NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    kcal_per_kg INT NOT NULL,
    daily_target_grams INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Feeding schedules
--  Code uses: id (PK), device_id, waktu, porsi_gram, mode, is_active
-- ============================================================
CREATE TABLE IF NOT EXISTS feeding_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    waktu TIME NOT NULL,
    porsi_gram INT NOT NULL,
    mode ENUM('system', 'manual') DEFAULT 'system',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_active (device_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Feeding logs
--  Code uses: device_id (FK to devices.id), grams_out, method
-- ============================================================
CREATE TABLE IF NOT EXISTS feeding_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    grams_out INT NOT NULL,
    method ENUM('manual', 'otomatis') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_timestamp (device_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Pantry refills
-- ============================================================
CREATE TABLE IF NOT EXISTS pantry_refills (
    refill_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    grams_added INT NOT NULL,
    refilled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_refilled_at (refilled_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  Default admin user (password: admin123)
--  CHANGE PASSWORD IN PRODUCTION!
-- ============================================================
INSERT IGNORE INTO users (username, email, password_hash) VALUES
('admin', 'admin@smartpetfeeder.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF6q1vQy');
