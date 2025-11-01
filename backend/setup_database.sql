-- Finance Dashboard Database Setup Script
-- Run this script to create the database and user for the application

-- Create database user (if not exists)
CREATE USER finance_dashboard_user WITH PASSWORD 'your_secure_password_here';

-- Create database
CREATE DATABASE finance_dashboard_db WITH OWNER finance_dashboard_user;

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE finance_dashboard_db TO finance_dashboard_user;

-- Connect to the new database
\c finance_dashboard_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO finance_dashboard_user;

-- Grant privileges on all tables (for future tables created by the app)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO finance_dashboard_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO finance_dashboard_user;

-- Display confirmation
\echo 'Database setup completed successfully!'
\echo 'Database: finance_dashboard_db'
\echo 'User: finance_dashboard_user'
\echo ''
\echo 'Update your .env file with:'
\echo 'DATABASE_URL=postgresql://finance_dashboard_user:your_secure_password_here@localhost:5432/finance_dashboard_db'
