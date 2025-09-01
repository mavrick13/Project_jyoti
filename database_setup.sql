-- Project Moriarty Database Setup Script
-- Run this script as a PostgreSQL superuser (postgres)

-- Create database
CREATE DATABASE project_moriarty
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect to the new database
\c project_moriarty;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE project_moriarty TO postgres;
GRANT ALL ON SCHEMA public TO postgres;

-- Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL DEFAULT 'Employee',
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create farmers table (matching your existing schema)
CREATE TABLE farmers (
    beneficiary_id TEXT PRIMARY KEY,
    beneficiary_name TEXT NOT NULL,
    phone_no TEXT,
    aadhaar_no TEXT,
    scheme TEXT NOT NULL,
    pumphp TEXT,
    pumphead TEXT,
    pumphp_combined TEXT GENERATED ALWAYS AS (
        CASE 
            WHEN pumphp IS NOT NULL AND pumphead IS NOT NULL 
            THEN pumphp || '-' || pumphead 
            ELSE NULL 
        END
    ) STORED,
    selection_date DATE,
    circle_name TEXT,
    taluka_name TEXT,
    village_name TEXT,
    installer_user_id INTEGER REFERENCES users(user_id),
    ld TEXT,
    jsr_status TEXT,
    dispatch_status TEXT DEFAULT 'Not Dispatched',
    dispatch_date DATE,
    vehicle_no TEXT,
    driver_info TEXT,
    installation_status TEXT DEFAULT 'Not Started',
    installation_remark TEXT,
    icr_status TEXT DEFAULT 'Not Started',
    photos TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory table
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    specification VARCHAR(50),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    min_stock_level INTEGER NOT NULL DEFAULT 10 CHECK (min_stock_level >= 0),
    unit_price DECIMAL(10,2) CHECK (unit_price >= 0),
    supplier VARCHAR(255),
    part_number VARCHAR(100),
    description TEXT,
    document_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    location VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER REFERENCES users(user_id)
);

-- Create inventory transactions table for tracking all movements
CREATE TABLE inventory_transactions (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('in', 'out', 'adjustment')),
    quantity INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(50),
    notes TEXT,
    unit_cost DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Create farmer dispatch tracking tables
CREATE TABLE farmer_dispatches (
    id SERIAL PRIMARY KEY,
    farmer_beneficiary_id TEXT NOT NULL REFERENCES farmers(beneficiary_id),
    dispatch_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    total_value DECIMAL(12,2),
    notes TEXT,
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id)
);

CREATE TABLE farmer_dispatch_items (
    id SERIAL PRIMARY KEY,
    dispatch_id INTEGER NOT NULL REFERENCES farmer_dispatches(id) ON DELETE CASCADE,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2)
);

-- Create tasks table
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to_user_id INTEGER NOT NULL REFERENCES users(user_id),
    assigned_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
    farmer_beneficiary_id TEXT REFERENCES farmers(beneficiary_id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    due_date DATE,
    tags TEXT,
    notes TEXT,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat groups table
CREATE TABLE chat_groups (
    group_id SERIAL PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat group members table
CREATE TABLE chat_group_members (
    member_id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(group_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    UNIQUE(group_id, user_id)
);

-- Create messages table
CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES chat_groups(group_id) ON DELETE CASCADE,
    sender_user_id INTEGER NOT NULL REFERENCES users(user_id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    file_url VARCHAR(500),
    reply_to_message_id INTEGER REFERENCES messages(message_id),
    mentions TEXT,
    tags TEXT,
    task_id INTEGER REFERENCES tasks(task_id),
    farmer_beneficiary_id TEXT REFERENCES farmers(beneficiary_id),
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_farmers_scheme ON farmers(scheme);
CREATE INDEX idx_farmers_dispatch_status ON farmers(dispatch_status);
CREATE INDEX idx_farmers_installation_status ON farmers(installation_status);
CREATE INDEX idx_farmers_circle_name ON farmers(circle_name);
CREATE INDEX idx_farmers_created_at ON farmers(created_at);

CREATE INDEX idx_inventory_category ON inventory(category);
CREATE INDEX idx_inventory_status ON inventory(status);
CREATE INDEX idx_inventory_quantity ON inventory(quantity);
CREATE INDEX idx_inventory_created_at ON inventory(created_at);

CREATE INDEX idx_inventory_transactions_inventory_id ON inventory_transactions(inventory_id);
CREATE INDEX idx_inventory_transactions_created_at ON inventory_transactions(created_at);

CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to_user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

CREATE INDEX idx_messages_group_id ON messages(group_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farmers_updated_at BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_groups_updated_at BEFORE UPDATE ON chat_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial admin user (password is 'admin123' hashed with bcrypt)
INSERT INTO users (name, email, phone, role, password_hash, status) VALUES
('Admin User', 'admin@jyotielectrotech.com', '9999999999', 'Admin', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/3FdLyMhSu', 'active'),
('Installer One', 'installer1@jyotielectrotech.com', '8888888888', 'Employee', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/3FdLyMhSu', 'active'),
('Installer Two', 'installer2@jyotielectrotech.com', '7777777777', 'Employee', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/3FdLyMhSu', 'active');

-- Insert sample inventory items
INSERT INTO inventory (category, type, specification, quantity, min_stock_level, unit_price, supplier, part_number, description, location, created_by_user_id) VALUES
-- Motors
('motor', '3hp', '30', 15, 5, 18000.00, 'Motor Tech Ltd', 'MOT-3HP-30', '3HP motor with 30m pump head', 'Warehouse A', 1),
('motor', '3hp', '50', 12, 5, 19000.00, 'Motor Tech Ltd', 'MOT-3HP-50', '3HP motor with 50m pump head', 'Warehouse A', 1),
('motor', '3hp', '70', 10, 3, 20000.00, 'Motor Tech Ltd', 'MOT-3HP-70', '3HP motor with 70m pump head', 'Warehouse A', 1),
('motor', '5hp', '30', 20, 5, 25000.00, 'Motor Tech Ltd', 'MOT-5HP-30', '5HP motor with 30m pump head', 'Warehouse A', 1),
('motor', '5hp', '50', 18, 5, 26000.00, 'Motor Tech Ltd', 'MOT-5HP-50', '5HP motor with 50m pump head', 'Warehouse A', 1),
('motor', '5hp', '70', 15, 3, 27000.00, 'Motor Tech Ltd', 'MOT-5HP-70', '5HP motor with 70m pump head', 'Warehouse A', 1),
('motor', '5hp', '100', 8, 3, 28000.00, 'Motor Tech Ltd', 'MOT-5HP-100', '5HP motor with 100m pump head', 'Warehouse A', 1),
('motor', '7.5hp', '30', 10, 3, 35000.00, 'Motor Tech Ltd', 'MOT-7.5HP-30', '7.5HP motor with 30m pump head', 'Warehouse A', 1),
('motor', '7.5hp', '50', 8, 3, 36000.00, 'Motor Tech Ltd', 'MOT-7.5HP-50', '7.5HP motor with 50m pump head', 'Warehouse A', 1),
('motor', '7.5hp', '70', 6, 2, 37000.00, 'Motor Tech Ltd', 'MOT-7.5HP-70', '7.5HP motor with 70m pump head', 'Warehouse A', 1),
('motor', '7.5hp', '100', 4, 2, 38000.00, 'Motor Tech Ltd', 'MOT-7.5HP-100', '7.5HP motor with 100m pump head', 'Warehouse A', 1),

-- Controllers
('controller', '3hp', '', 25, 8, 8000.00, 'Control Systems Inc', 'CTRL-3HP', '3HP pump controller', 'Warehouse B', 1),
('controller', '5hp', '', 20, 6, 12000.00, 'Control Systems Inc', 'CTRL-5HP', '5HP pump controller', 'Warehouse B', 1),
('controller', '7.5hp', '', 15, 5, 15000.00, 'Control Systems Inc', 'CTRL-7.5HP', '7.5HP pump controller', 'Warehouse B', 1),

-- Solar Panels
('solar_panel', '520wp', '', 100, 30, 12000.00, 'Solar Tech Ltd', 'SOLAR-520', '520W solar panel', 'Warehouse C', 1),
('solar_panel', '540wp', '', 80, 25, 13000.00, 'Solar Tech Ltd', 'SOLAR-540', '540W solar panel', 'Warehouse C', 1),

-- BOS (Balance of System)
('bos', '3hp', '', 30, 10, 5000.00, 'BOS Systems Ltd', 'BOS-3HP', '3HP Balance of System components', 'Warehouse D', 1),
('bos', '5hp', '', 25, 8, 7000.00, 'BOS Systems Ltd', 'BOS-5HP', '5HP Balance of System components', 'Warehouse D', 1),
('bos', '7.5hp', '', 20, 6, 9000.00, 'BOS Systems Ltd', 'BOS-7.5HP', '7.5HP Balance of System components', 'Warehouse D', 1),

-- Structure
('structure', '3hp', '', 40, 12, 3000.00, 'Structure Co', 'STRUCT-3HP', '3HP system mounting structure', 'Warehouse E', 1),
('structure', '5hp', '', 35, 10, 4000.00, 'Structure Co', 'STRUCT-5HP', '5HP system mounting structure', 'Warehouse E', 1),
('structure', '7.5hp', '', 25, 8, 5000.00, 'Structure Co', 'STRUCT-7.5HP', '7.5HP system mounting structure', 'Warehouse E', 1),

-- Wire
('wire', '3hp', '', 150, 30, 500.00, 'Cable Works', 'WIRE-3HP', '3HP system wiring kit', 'Warehouse F', 1),
('wire', '5hp', '', 120, 25, 700.00, 'Cable Works', 'WIRE-5HP', '5HP system wiring kit', 'Warehouse F', 1),
('wire', '7.5hp', '', 100, 20, 900.00, 'Cable Works', 'WIRE-7.5HP', '7.5HP system wiring kit', 'Warehouse F', 1),

-- Pipe
('pipe', '3hp', '', 200, 40, 200.00, 'Pipe Industries', 'PIPE-3HP', '3HP system piping kit', 'Warehouse G', 1),
('pipe', '5hp', '', 180, 35, 250.00, 'Pipe Industries', 'PIPE-5HP', '5HP system piping kit', 'Warehouse G', 1),
('pipe', '7.5hp', '', 150, 30, 300.00, 'Pipe Industries', 'PIPE-7.5HP', '7.5HP system piping kit', 'Warehouse G', 1);

-- Create a default chat group
INSERT INTO chat_groups (group_name, description, created_by_user_id) VALUES
('General Discussion', 'Main discussion group for all team members', 1);

-- Add all users to the general group
INSERT INTO chat_group_members (group_id, user_id, is_admin) VALUES
(1, 1, TRUE),
(1, 2, FALSE),
(1, 3, FALSE);

-- Display success message
SELECT 'Database project_moriarty created successfully!' as status;
SELECT 'Total inventory items: ' || COUNT(*) as inventory_count FROM inventory;
SELECT 'Total users: ' || COUNT(*) as users_count FROM users;

-- Show default login credentials
SELECT 
    'Default Login Credentials:' as info,
    email as email,
    'Password: admin123 (for admin) or installer123 (for employees)' as password
FROM users;