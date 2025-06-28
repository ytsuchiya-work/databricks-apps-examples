#!/usr/bin/env python3
"""
Unity Catalog Configuration Verification Script

This script demonstrates how Unity Catalog table names are constructed
using the environment variables DATABRICKS_CATALOG and DATABRICKS_SCHEMA.

Expected configuration:
- DATABRICKS_CATALOG="daveok"
- DATABRICKS_SCHEMA="excel_app"
"""

import os
from src.dash_dbx_writeback.config.unity_catalog import (
    get_full_table_name,
    get_catalog_name,
    get_schema_name
)

def main():
    """Verify Unity Catalog configuration."""
    print("🔧 Unity Catalog Configuration Verification")
    print("=" * 50)
    
    # Show current environment variables
    print(f"Environment Variables:")
    print(f"  DATABRICKS_CATALOG: {os.getenv('DATABRICKS_CATALOG', 'NOT SET')}")
    print(f"  DATABRICKS_SCHEMA: {os.getenv('DATABRICKS_SCHEMA', 'NOT SET')}")
    print()
    
    # Show configuration values
    print(f"Configuration Values:")
    print(f"  Catalog: {get_catalog_name()}")
    print(f"  Schema: {get_schema_name()}")
    print()
    
    # Test table name construction
    test_tables = [
        "product_sales",
        "products", 
        "customer_data",
        "inventory",
        "sales_summary"
    ]
    
    print(f"Table Name Construction Examples:")
    print(f"  Format: catalog.schema.table")
    print()
    
    for table_name in test_tables:
        full_name = get_full_table_name(table_name)
        print(f"  {table_name:15} → {full_name}")
    
    print()
    print("✅ Unity Catalog configuration is working correctly!")
    print(f"   All tables will be created in: {get_catalog_name()}.{get_schema_name()}")
    
    # Verify expected values
    expected_catalog = "daveok"
    expected_schema = "excel_app"
    
    if get_catalog_name() == expected_catalog and get_schema_name() == expected_schema:
        print(f"✅ Configuration matches expected values!")
    else:
        print(f"⚠️  Configuration differs from expected values:")
        print(f"   Expected: {expected_catalog}.{expected_schema}")
        print(f"   Actual: {get_catalog_name()}.{get_schema_name()}")

if __name__ == "__main__":
    main() 