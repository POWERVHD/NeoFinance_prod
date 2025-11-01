"""
Script to verify database tables and schema.
"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

def verify_tables():
    """Verify that all required tables exist in the database."""
    print("Verifying database tables...")
    print("=" * 60)

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)

        # Get all table names
        tables = inspector.get_table_names()

        print(f"✓ Connected to database: finance_dashboard_db")
        print(f"✓ Found {len(tables)} tables\n")

        if not tables:
            print("✗ No tables found!")
            return False

        # Check for expected tables
        expected_tables = ["users", "transactions", "alembic_version"]

        for table_name in tables:
            print(f"Table: {table_name}")

            # Get columns for each table
            columns = inspector.get_columns(table_name)
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"    - {col['name']}: {col_type} {nullable}")

            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"  Indexes ({len(indexes)}):")
                for idx in indexes:
                    cols = ', '.join(idx['column_names'])
                    unique = "UNIQUE" if idx.get('unique') else ""
                    print(f"    - {idx['name']}: ({cols}) {unique}")

            print()

        # Verify all expected tables exist
        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            print(f"✗ Missing tables: {', '.join(missing_tables)}")
            return False

        # Check row counts
        with engine.connect() as conn:
            print("Row counts:")
            for table in ["users", "transactions"]:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"  - {table}: {count} rows")

        print("=" * 60)
        print("✓ Database verification PASSED!")
        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    verify_tables()
