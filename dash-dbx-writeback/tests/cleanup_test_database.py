#!/usr/bin/env python3
"""
Cleanup script to drop the test database in Databricks Lakebase.

This script removes the dedicated test database and all its data.
USE WITH CAUTION - This is destructive and cannot be undone!

Usage:
    python tests/cleanup_test_database.py
    
Environment Variables:
    LAKEBASE_INSTANCE_NAME - Your Lakebase instance name (required)
    LAKEBASE_TEST_DATABASE - Test database name (default: databricks_postgres_test)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient
import psycopg
import uuid


# Load environment variables
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from {env_path}")


def log(message: str, level: str = "INFO") -> None:
    """Print formatted log message"""
    symbols = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "WARNING": "⚠️ ",
        "STEP": "→",
    }
    symbol = symbols.get(level, "  ")
    print(f"{symbol} {message}")


class TestDatabaseCleanup:
    """Cleanup test database from Lakebase"""
    
    def __init__(self):
        self.instance_name = os.getenv("LAKEBASE_INSTANCE_NAME")
        self.prod_database = os.getenv("LAKEBASE_DATABASE", "databricks_postgres")
        self.test_database = os.getenv("LAKEBASE_TEST_DATABASE", f"{self.prod_database}_test")
        self.workspace_client = None
        self.host = None
        self.user = None
        
    def validate_config(self) -> bool:
        """Validate required configuration"""
        log("Validating configuration...", "STEP")
        
        if not self.instance_name:
            log("LAKEBASE_INSTANCE_NAME not set in environment", "ERROR")
            return False
        
        if not self.test_database:
            log("LAKEBASE_TEST_DATABASE not set in environment", "ERROR")
            log("Cannot determine which database to drop", "ERROR")
            return False
        
        # Safety check - don't allow dropping production database
        if self.test_database == self.prod_database:
            log("SAFETY CHECK FAILED!", "ERROR")
            log(f"Test database '{self.test_database}' matches production database!", "ERROR")
            log("Refusing to drop production database. Please check your configuration.", "ERROR")
            return False
        
        if "test" not in self.test_database.lower():
            log("SAFETY WARNING!", "WARNING")
            log(f"Database name '{self.test_database}' does not contain 'test'", "WARNING")
            log("Are you sure this is a test database?", "WARNING")
            user_input = input("\nType 'yes' to continue anyway: ")
            if user_input.lower() != "yes":
                log("Cleanup cancelled", "INFO")
                return False
        
        log(f"Instance: {self.instance_name}", "INFO")
        log(f"Production database: {self.prod_database}", "INFO")
        log(f"Test database to DROP: {self.test_database}", "WARNING")
        
        return True
    
    def initialize_workspace_client(self) -> bool:
        """Initialize Databricks workspace client"""
        log("Initializing Databricks workspace client...", "STEP")
        
        try:
            self.workspace_client = WorkspaceClient()
            log("Workspace client initialized", "SUCCESS")
            return True
        except Exception as e:
            log(f"Failed to initialize workspace client: {e}", "ERROR")
            return False
    
    def get_database_host(self) -> bool:
        """Get database host from Lakebase instance"""
        log("Retrieving database host...", "STEP")
        
        try:
            instance = self.workspace_client.database.get_database_instance(
                name=self.instance_name
            )
            self.host = instance.read_write_dns
            self.user = self.workspace_client.current_user.me().user_name
            
            log(f"Host: {self.host}", "INFO")
            log(f"User: {self.user}", "INFO")
            return True
        except Exception as e:
            log(f"Failed to get database host: {e}", "ERROR")
            return False
    
    def get_oauth_token(self) -> str:
        """Generate OAuth token for database connection"""
        token = self.workspace_client.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[self.instance_name]
        ).token
        return token
    
    def create_connection(self, database: str) -> psycopg.Connection:
        """Create a psycopg connection to the specified database"""
        token = self.get_oauth_token()
        
        conn = psycopg.connect(
            host=self.host,
            dbname=database,
            user=self.user,
            password=token,
            sslmode="require"
        )
        return conn
    
    def check_database_exists(self) -> bool:
        """Check if test database exists"""
        log(f"Checking if database '{self.test_database}' exists...", "STEP")
        
        try:
            conn = self.create_connection(self.prod_database)
            
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (self.test_database,)
                )
                exists = cur.fetchone() is not None
            
            conn.close()
            
            if exists:
                log(f"Database '{self.test_database}' exists", "INFO")
            else:
                log(f"Database '{self.test_database}' does not exist", "WARNING")
            
            return exists
        except Exception as e:
            log(f"Error checking database existence: {e}", "ERROR")
            return False
    
    def get_database_size(self) -> str:
        """Get the size of the test database"""
        try:
            conn = self.create_connection(self.test_database)
            
            with conn.cursor() as cur:
                cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
                size = cur.fetchone()[0]
            
            conn.close()
            return size
        except Exception as e:
            return "unknown"
    
    def count_tables(self) -> int:
        """Count tables in the test database"""
        try:
            conn = self.create_connection(self.test_database)
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                """)
                count = cur.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            return 0
    
    def drop_database(self) -> bool:
        """Drop the test database"""
        log(f"Dropping database '{self.test_database}'...", "STEP")
        
        try:
            # Connect to production database
            conn = self.create_connection(self.prod_database)
            conn.autocommit = True
            
            with conn.cursor() as cur:
                # Terminate all connections to the test database
                log("Terminating existing connections...", "STEP")
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{self.test_database}'
                    AND pid <> pg_backend_pid()
                """)
                
                # Drop the database
                cur.execute(f'DROP DATABASE IF EXISTS "{self.test_database}"')
                log(f"Database '{self.test_database}' dropped successfully", "SUCCESS")
            
            conn.close()
            return True
        except Exception as e:
            log(f"Error dropping database: {e}", "ERROR")
            return False
    
    def run(self) -> bool:
        """Run the complete cleanup process"""
        log("\n" + "=" * 60, "INFO")
        log("TEST DATABASE CLEANUP", "WARNING")
        log("=" * 60 + "\n", "INFO")
        
        # Validate configuration
        if not self.validate_config():
            return False
        
        print()
        
        # Initialize workspace client
        if not self.initialize_workspace_client():
            return False
        
        print()
        
        # Get database host
        if not self.get_database_host():
            return False
        
        print()
        
        # Check if database exists
        if not self.check_database_exists():
            log(f"Database '{self.test_database}' does not exist. Nothing to clean up.", "INFO")
            return True
        
        print()
        
        # Get database info
        log("Gathering database information...", "STEP")
        size = self.get_database_size()
        table_count = self.count_tables()
        
        log(f"Database size: {size}", "INFO")
        log(f"Number of tables: {table_count}", "INFO")
        
        print()
        
        # Confirm deletion
        log("⚠️  WARNING: This will permanently delete the test database!", "WARNING")
        log(f"⚠️  Database: {self.test_database}", "WARNING")
        log(f"⚠️  Tables: {table_count}", "WARNING")
        log(f"⚠️  Size: {size}", "WARNING")
        
        print()
        user_input = input("Type 'DELETE' to confirm deletion: ")
        
        if user_input != "DELETE":
            log("Cleanup cancelled", "INFO")
            return False
        
        print()
        
        # Drop database
        if not self.drop_database():
            return False
        
        log("\n" + "=" * 60, "SUCCESS")
        log("TEST DATABASE CLEANUP COMPLETE!", "SUCCESS")
        log("=" * 60, "SUCCESS")
        
        print(f"\nThe test database '{self.test_database}' has been removed.")
        print(f"To recreate it, run: python tests/setup_test_database.py")
        
        return True


def main():
    """Main entry point"""
    cleanup = TestDatabaseCleanup()
    
    try:
        success = cleanup.run()
        
        if success:
            print("\n" + "=" * 60)
            print("✓ Cleanup completed successfully!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("✗ Cleanup cancelled or failed.")
            print("=" * 60)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCleanup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



