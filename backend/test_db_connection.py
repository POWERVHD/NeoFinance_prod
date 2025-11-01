"""
Quick script to test PostgreSQL database connection.
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def test_connection():
    """Test database connection."""
    print(f"Testing connection to: {settings.DATABASE_URL}")
    print("=" * 60)

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version}")

            # Test database name
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"✓ Connected to database: {db_name}")

            # Test user
            result = connection.execute(text("SELECT current_user;"))
            user = result.fetchone()[0]
            print(f"✓ Connected as user: {user}")

        print("=" * 60)
        print("Database connection test PASSED ✓")
        return True

    except Exception as e:
        print("✗ Connection failed!")
        print(f"✗ Error: {e}")
        print("=" * 60)
        print("Database connection test FAILED ✗")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
