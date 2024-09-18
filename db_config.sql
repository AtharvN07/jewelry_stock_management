CREATE DATABASE jewelry_management;

USE jewelry_management;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE ite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    barcode VARCHAR(100) UNIQUE,
    photo VARCHAR(255)
);

CREATE TABLE transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    quantity INT,
    subtotal DECIMAL(10, 2),
    total DECIMAL(10, 2),
    FOREIGN KEY (item_id) REFERENCES items(id)
);
