-- setup.sql
DROP DATABASE IF EXISTS library_db;
CREATE DATABASE library_db;
USE library_db;

-- Admin table
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Books table
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity INT NOT NULL DEFAULT 0
);

-- Members table
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(150),
    phone VARCHAR(50),
    email VARCHAR(150)
);

-- Issued books
CREATE TABLE issued_books (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status ENUM('issued','returned') NOT NULL DEFAULT 'issued',
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);

-- Minimal sample data
INSERT INTO admin (username, password) VALUES
('admin', 'admin123'); -- NOTE: Plain text for demo; replace with hashed password in production

INSERT INTO books (title, author, category, quantity) VALUES
('The C Programming Language','Brian Kernighan','Programming',5),
('Introduction to Algorithms','Cormen','Programming',3),
('Python Crash Course','Eric Matthes','Programming',4);

INSERT INTO members (name, department, phone, email) VALUES
('Alice Rahman','CSE','01700000001','alice@example.com'),
('Bob Karim','EEE','01700000002','bob@example.com');

-- Issue one book as sample
INSERT INTO issued_books (book_id, member_id, issue_date, due_date, status) VALUES
(1, 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY), 'issued');
