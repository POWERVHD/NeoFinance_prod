# Database Migrations with Alembic

This project uses **Alembic** for database schema migrations. Alembic provides version control for your database schema.

## Quick Reference

### Common Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration (auto-detect model changes)
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1

# Rollback to a specific version
alembic downgrade <revision_id>

# Show current migration version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Initial Setup (Already Completed)

The database has been initialized with:
- ✓ Alembic configuration
- ✓ Initial migration creating `users` and `transactions` tables
- ✓ PostgreSQL database: `finance_dashboard_db`

## Workflow for Schema Changes

### 1. Modify Your Models

Edit your SQLAlchemy models in `app/models/`:
```python
# Example: Adding a new column to User model
class User(Base):
    __tablename__ = "users"
    # ... existing columns ...
    phone_number = Column(String(20), nullable=True)  # New column
```

### 2. Create a Migration

```bash
alembic revision --autogenerate -m "Add phone_number to users table"
```

This will:
- Detect changes in your models
- Generate a migration file in `alembic/versions/`
- Include upgrade() and downgrade() functions

### 3. Review the Migration

Always review the generated migration file before applying:
```bash
ls -lt alembic/versions/  # Find the newest file
cat alembic/versions/<newest_file>.py
```

### 4. Apply the Migration

```bash
alembic upgrade head
```

### 5. Verify the Changes

```bash
python verify_tables.py
```

## Database Connection

The database connection is configured in:
- **Development**: `.env` file (`DATABASE_URL`)
- **Alembic**: `alembic/env.py` (reads from `.env`)

Current configuration:
```
DATABASE_URL=postgresql://finance_dashboard_user:finance_dev_password_123@localhost:5432/finance_dashboard_db
```

## Migration Files

Migration files are stored in `alembic/versions/` and follow this format:
```
<revision_id>_<description>.py
```

Example:
```
5a550a03ba92_initial_migration_create_users_and_.py
```

Each migration contains:
- `upgrade()`: How to apply this migration
- `downgrade()`: How to rollback this migration

## Troubleshooting

### "Target database is not up to date"

This means there are pending migrations. Run:
```bash
alembic upgrade head
```

### "Can't locate revision identified by"

This means your local migrations don't match the database. Options:
1. Pull latest migrations from git
2. Reset the database (development only)

### Reset Database (Development Only)

```bash
# Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS finance_dashboard_db;
CREATE DATABASE finance_dashboard_db WITH OWNER finance_dashboard_user;
GRANT ALL PRIVILEGES ON DATABASE finance_dashboard_db TO finance_dashboard_user;
\q
EOF

# Apply all migrations
alembic upgrade head
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic may not detect all changes correctly
2. **Test migrations on development first** - Never run untested migrations in production
3. **Commit migrations to git** - Migration files should be version controlled
4. **Write descriptive migration messages** - Makes history easier to understand
5. **Don't modify applied migrations** - Create a new migration to fix issues

## Production Deployment

For production deployments:

1. **Backup the database first**
```bash
pg_dump finance_dashboard_db > backup_$(date +%Y%m%d).sql
```

2. **Apply migrations**
```bash
alembic upgrade head
```

3. **Verify**
```bash
python verify_tables.py
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
