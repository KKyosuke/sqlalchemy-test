CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    company_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email, company_id) VALUES ('Alice', 'alice@example.com', 1);
INSERT INTO users (name, email, company_id) VALUES ('Bob', 'bob@example.com', 2);
