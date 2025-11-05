import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Import for legacy Databricks Unity Catalog tests
try:
    from dash_dbx_writeback.config.workspace_client import get_connection as get_uc_connection
    from dash_dbx_writeback.data.sample_product_data import generate_product_data
    DATABRICKS_UC_AVAILABLE = True
except ImportError:
    DATABRICKS_UC_AVAILABLE = False

# Import for PostgreSQL/Lakebase tests
from dash_dbx_writeback.database_operations import (
    initialize_connection_pool,
    get_connection,
    close_all_connections,
    execute_sql,
)
from dash_dbx_writeback.config import db_config


def pytest_configure(config):
    """Load environment variables from .env file before any tests run."""
    # Get the project root directory (where pyproject.toml is located)
    project_root = Path(__file__).parent.parent

    # Try to load .env file from project root
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✓ Loaded environment variables from {env_path}")
    else:
        print(
            "⚠️  No .env file found. Make sure to set required environment variables manually."
        )
    
    # Use test database if configured to completely isolate from production
    test_database = os.getenv("LAKEBASE_TEST_DATABASE")
    if test_database:
        os.environ["LAKEBASE_DATABASE"] = test_database
        print(f"✓ Using dedicated test database: {test_database}")
    else:
        print(f"ℹ️  No test database configured, using production database with test schema")
        print(f"   To use a dedicated test database, run: python tests/setup_test_database.py")
    
    # Set test-specific environment variables if not already set
    if not os.getenv("LAKEBASE_SCHEMA"):
        # Use a test schema to avoid impacting production data
        test_schema = os.getenv("LAKEBASE_TEST_SCHEMA", "test_schema")
        os.environ["LAKEBASE_SCHEMA"] = test_schema
        print(f"✓ Using test schema: {test_schema}")
    
    print(f"✓ Lakebase Instance: {os.getenv('LAKEBASE_INSTANCE_NAME', 'NOT SET')}")
    print(f"✓ Lakebase Database: {os.getenv('LAKEBASE_DATABASE', 'NOT SET')}")
    print(f"✓ Lakebase Schema: {os.getenv('LAKEBASE_SCHEMA', 'NOT SET')}")
    
    # Reload the db_config after environment variables are set
    from dash_dbx_writeback.config import db_config
    db_config.__init__()
    print(f"✓ Reloaded database configuration with test settings")


def pytest_sessionstart(session):
    """Setup test schema before running tests."""
    print("\n" + "=" * 60)
    print("🚀 INITIALIZING TEST SESSION")
    print("=" * 60)
    
    # Initialize connection pool
    success = initialize_connection_pool()
    if success:
        print("✓ PostgreSQL connection pool initialized")
        
        # Create test schema if it doesn't exist
        schema = db_config.SCHEMA
        if schema and schema != "public":
            try:
                execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                print(f"✓ Test schema '{schema}' ready")
            except Exception as e:
                print(f"⚠️  Could not create test schema: {e}")
    else:
        print("⚠️  Failed to initialize connection pool")
    
    print("=" * 60 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Cleanup after all tests complete."""
    print("\n" + "=" * 60)
    print("🧹 CLEANING UP TEST SESSION")
    print("=" * 60)
    
    # Check if we're using a dedicated test database
    test_database = os.getenv("LAKEBASE_TEST_DATABASE")
    
    if test_database:
        print(f"ℹ️  Test database '{test_database}' will be preserved")
        print(f"   To drop it, run: python tests/cleanup_test_database.py")
    else:
        # Optionally drop test schema and all its tables if using production database
        # Uncomment the following lines if you want to clean up the test schema after tests
        # schema = db_config.SCHEMA
        # if schema and schema != "public":
        #     try:
        #         execute_sql(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        #         print(f"✓ Dropped test schema: {schema}")
        #     except Exception as e:
        #         print(f"⚠️  Could not drop test schema: {e}")
        pass
    
    # Close all database connections
    close_all_connections()
    print("✓ Closed all database connections")
    print("=" * 60 + "\n")


# ============================================================================
# PostgreSQL/Lakebase Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def pg_connection_pool():
    """Get PostgreSQL connection pool for the session."""
    pool = get_connection()
    if pool is None:
        pytest.skip("PostgreSQL connection pool not available")
    yield pool
    # Connection cleanup happens in pytest_sessionfinish


@pytest.fixture(scope="session")
def test_schema():
    """Get the test schema name."""
    return db_config.SCHEMA


# ============================================================================
# Legacy Databricks Unity Catalog Fixtures (for backward compatibility)
# ============================================================================

@pytest.fixture(scope="session")
def conn():
    """Get a Databricks Unity Catalog connection (legacy)."""
    if not DATABRICKS_UC_AVAILABLE:
        pytest.skip("Databricks Unity Catalog connection not available")
    
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    if not http_path:
        pytest.skip("DATABRICKS_HTTP_PATH not set")
    
    return get_uc_connection(http_path)


@pytest.fixture(scope="session")
def test_table_name():
    """Legacy test table name for Unity Catalog tests."""
    return "daveok.excel_app.pytest_read"


@pytest.fixture(scope="session")
def write_table(conn, test_table_name):
    """Legacy fixture for Unity Catalog write tests."""
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {test_table_name} (x int, x_squared int)"
        )

        squares = [(i, i * i) for i in range(100)]
        values = ",".join([f"({x}, {y})" for (x, y) in squares])

        cursor.execute(f"INSERT INTO {test_table_name} VALUES {values}")
        yield values
        cursor.execute(f"DROP TABLE {test_table_name}")


@pytest.fixture(scope="session")
def custom_data():
    """Legacy fixture for sample product data."""
    if not DATABRICKS_UC_AVAILABLE:
        pytest.skip("Sample data generation not available")
    yield generate_product_data(num_products=3)
