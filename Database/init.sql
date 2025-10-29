CREATE DATABASE IF NOT EXISTS insurance_db;
USE insurance_db;

CREATE TABLE metadata_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    type ENUM('policy','claim','reserve_model'),
    pii_tags VARCHAR(255),
    compliance_tags VARCHAR(255),
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lineage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_asset INT,
    to_asset INT,
    FOREIGN KEY (from_asset) REFERENCES metadata_assets(id),
    FOREIGN KEY (to_asset) REFERENCES metadata_assets(id)
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    role ENUM('viewer','editor','admin')
);
