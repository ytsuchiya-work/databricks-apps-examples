"""
Centralized database configuration for Lakebase PostgreSQL.

This module provides configuration for connecting to Databricks Lakebase
PostgreSQL instances with OAuth authentication.
"""

import os
from typing import Optional


class DatabaseConfig:
    """Database configuration for Lakebase"""
    
    def __init__(self):
        # Lakebase instance name (e.g., "dbase_instance")
        self.INSTANCE_NAME = os.getenv("LAKEBASE_INSTANCE_NAME", "")
        
        # Database name
        self.DATABASE = os.getenv("LAKEBASE_DATABASE", "databricks_postgres")
        
        # Schema name
        self.SCHEMA = os.getenv("LAKEBASE_SCHEMA", "public")
        
        # Connection pool settings
        self.POOL_MIN_SIZE = int(os.getenv("POOL_MIN_SIZE", "1"))
        self.POOL_MAX_SIZE = int(os.getenv("POOL_MAX_SIZE", "5"))
    
    def get_full_table_name(self, table_name: str) -> str:
        """
        Get the full table name in format schema.table
        
        Args:
            table_name: The table name without schema
            
        Returns:
            str: Full table name with schema
        """
        if self.SCHEMA and self.SCHEMA != "public":
            return f"{self.SCHEMA}.{table_name}"
        return table_name
    
    def get_schema_name(self) -> str:
        """Get the current schema name"""
        return self.SCHEMA


# Singleton instance
db_config = DatabaseConfig()

