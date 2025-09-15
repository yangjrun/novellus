-- Novellus PostgreSQL Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extension for UUID generation (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for additional data types
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create demo database schema
CREATE SCHEMA IF NOT EXISTS demo;

-- Create demo users table (as used in the MCP server)
CREATE TABLE IF NOT EXISTS demo_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_demo_users_updated_at
    BEFORE UPDATE ON demo_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO demo_users (name, email, age) VALUES
    ('Alice Johnson', 'alice@example.com', 28),
    ('Bob Smith', 'bob@example.com', 35),
    ('Charlie Brown', 'charlie@example.com', 42),
    ('Diana Prince', 'diana@example.com', 30),
    ('Edward Norton', 'edward@example.com', 45)
ON CONFLICT (email) DO NOTHING;

-- Create a simple products table for demo purposes
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger for products table
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample products
INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Laptop Pro 15"', 'High-performance laptop for professionals', 1299.99, 25, 'Electronics'),
    ('Wireless Mouse', 'Ergonomic wireless mouse with long battery life', 49.99, 100, 'Electronics'),
    ('Office Chair', 'Comfortable ergonomic office chair', 299.99, 15, 'Furniture'),
    ('Coffee Mug', 'Ceramic coffee mug with company logo', 12.99, 200, 'Accessories'),
    ('Notebook Set', 'Set of 3 premium notebooks', 24.99, 50, 'Stationery')
ON CONFLICT DO NOTHING;

-- Create an orders table to demonstrate relationships
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES demo_users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    total_price DECIMAL(10,2) NOT NULL CHECK (total_price >= 0),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'))
);

-- Insert sample orders
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
    (1, 1, 1, 1299.99, 'delivered'),
    (2, 2, 2, 99.98, 'shipped'),
    (3, 3, 1, 299.99, 'confirmed'),
    (1, 4, 3, 38.97, 'delivered'),
    (4, 5, 2, 49.98, 'pending')
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_demo_users_email ON demo_users(email);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);

-- Create a view for order details
CREATE OR REPLACE VIEW order_details AS
SELECT
    o.id as order_id,
    u.name as customer_name,
    u.email as customer_email,
    p.name as product_name,
    o.quantity,
    p.price as unit_price,
    o.total_price,
    o.order_date,
    o.status
FROM orders o
JOIN demo_users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id;

-- Grant permissions (adjust as needed for your security requirements)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON order_details TO PUBLIC;

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'Novellus database initialization completed successfully';
END $$;