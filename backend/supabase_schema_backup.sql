-- ============================================================================
-- NeoFinance Database Schema for Supabase - BACKUP/REFERENCE ONLY
-- ============================================================================
-- ⚠️ OPTION A - MANUAL SQL APPROACH (NOT RECOMMENDED)
--
-- This file is kept as a backup/reference for the database schema.
--
-- RECOMMENDED APPROACH: Use Alembic migrations instead (see README below)
--
-- Only use this SQL file if:
-- - You cannot run Alembic from your local machine
-- - You need to manually inspect the schema
-- - You need emergency database recovery
-- ============================================================================

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- TRANSACTIONS TABLE
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    description TEXT NOT NULL,
    type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT check_transaction_type CHECK (type IN ('income', 'expense'))
);

CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions (id);
CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions (user_id);
CREATE INDEX IF NOT EXISTS ix_transactions_transaction_date ON transactions (transaction_date);

-- ALEMBIC VERSION TABLE
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num) VALUES ('5a550a03ba92') ON CONFLICT DO NOTHING;

-- ============================================================================
-- RECOMMENDED APPROACH: Use Alembic Instead
-- ============================================================================
--
-- 1. Get your Supabase DATABASE_URL:
--    Dashboard → Settings → Database → Connection String (URI)
--    Format: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
--
-- 2. Temporarily set in your local environment:
--    export DATABASE_URL="postgresql://postgres:..."
--
--    OR update backend/.env with Supabase URL
--
-- 3. Run migrations from backend directory:
--    cd backend
--    alembic upgrade head
--
-- 4. Verify in Supabase:
--    Dashboard → Table Editor → Check tables exist
--
-- Benefits:
-- ✅ Proper migration tracking
-- ✅ Can rollback if needed (alembic downgrade)
-- ✅ Future migrations automatically work
-- ✅ No manual SQL copy-paste errors
--
-- ============================================================================
