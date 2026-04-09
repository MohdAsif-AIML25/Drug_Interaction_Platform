CREATE TABLE IF NOT EXISTS drug_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_a VARCHAR(255) NOT NULL,
    drug_b VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    raw_text JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interaction_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_a VARCHAR(255) NOT NULL,
    drug_b VARCHAR(255) NOT NULL,
    severity VARCHAR(50),
    confidence FLOAT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sub_category VARCHAR(255),
    product_name VARCHAR(255),
    salt_composition VARCHAR(255),
    medicine_desc TEXT,
    side_effects TEXT,
    drug_interactions TEXT
);

CREATE TABLE IF NOT EXISTS rag_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_a VARCHAR(255),
    drug_b VARCHAR(255),
    text TEXT,
    severity VARCHAR(50)
);