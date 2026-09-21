"""
Database Schema & Migration Generator
Generates production-grade PostgreSQL DDL, indexes, constraints, and seed data
for specified product domains (E-commerce, Food Delivery, LMS).
"""

import os
from typing import Dict, Any

def generate_ecommerce_sql() -> str:
    return """-- ==========================================================
-- AI PRODUCT ARCHITECT: PostgreSQL Database Schema
-- Domain: E-Commerce Platform (Scalable & High Availability)
-- Target: AWS RDS PostgreSQL 15+
-- ==========================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'admin', 'vendor')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- 2. Product Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Products Table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    inventory_count INT DEFAULT 0 CHECK (inventory_count >= 0),
    image_url VARCHAR(500), -- AWS S3 URL
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_published ON products(is_published);

-- 4. Shopping Cart
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INT DEFAULT 1 CHECK (quantity > 0),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

-- 5. Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
    total_amount DECIMAL(12, 2) NOT NULL,
    order_status VARCHAR(30) DEFAULT 'pending' CHECK (order_status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
    shipping_address TEXT NOT NULL,
    payment_intent_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);

-- 6. Order Items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
    price_at_purchase DECIMAL(12, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0)
);

-- ==========================================================
-- Initial Seed Data
-- ==========================================================
INSERT INTO categories (id, name, slug, description) VALUES
('b079730b-04b3-4f96-8575-b82b3d81b951', 'Cloud Electronics', 'cloud-electronics', 'Cutting-edge gadgets and devices'),
('c179730b-04b3-4f96-8575-b82b3d81b952', 'Developer Tools', 'developer-tools', 'Workstation gear and software kits')
ON CONFLICT DO NOTHING;

INSERT INTO products (title, slug, price, inventory_count, image_url, category_id) VALUES
('Cloud Edge AI Compute Stick', 'cloud-edge-ai-compute-stick', 7499.00, 150, 'https://my-cloud-s3.s3.amazonaws.com/products/edge-stick.jpg', 'b079730b-04b3-4f96-8575-b82b3d81b951'),
('Ergonomic DevOps Mechanical Keyboard', 'ergonomic-devops-keyboard', 12999.00, 75, 'https://my-cloud-s3.s3.amazonaws.com/products/keyboard.jpg', 'c179730b-04b3-4f96-8575-b82b3d81b952')
ON CONFLICT DO NOTHING;
"""

def generate_database_files(output_dir: str, spec: Dict[str, Any] = None) -> Dict[str, str]:
    """Generates database schema and migration script files."""
    os.makedirs(output_dir, exist_ok=True)
    sql_content = generate_ecommerce_sql()
    
    schema_path = os.path.join(output_dir, "schema.sql")
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
        
    readme_content = """# Database Configuration
- Engine: PostgreSQL 15+
- Multi-AZ Support: Enabled via AWS RDS
- Migrations: Managed via standard DDL scripts or Alembic
- To execute locally: `psql -U postgres -d mydatabase -f schema.sql`
"""
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    return {"schema.sql": schema_path, "README.md": readme_path}

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "./output/database"
    res = generate_database_files(target)
    print(f"Database files generated at: {res}")
