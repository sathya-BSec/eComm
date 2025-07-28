-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- Create a user for the application (optional, for production use)
-- CREATE USER IF NOT EXISTS 'ecommerce_user'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Sample categories data
INSERT INTO categories (name, description) VALUES 
('Electronics', 'Electronic devices and gadgets'),
('Clothing', 'Fashion and apparel'),
('Books', 'Books and literature'),
('Home & Garden', 'Home improvement and gardening'),
('Sports', 'Sports and fitness equipment')
ON DUPLICATE KEY UPDATE name=name;

-- Sample products data (will be inserted after tables are created by SQLAlchemy)
-- Note: The actual table creation will be handled by SQLAlchemy models