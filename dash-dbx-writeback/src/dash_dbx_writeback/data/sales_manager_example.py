#!/usr/bin/env python3
"""
SalesDataManager Usage Example

This example demonstrates how to use the SalesDataManager class for:
- Generating realistic sales data
- Writing data to Unity Catalog
- Reading data from Unity Catalog
- Getting sales summaries and analytics
- Managing the complete sales data lifecycle
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.dash_dbx_writeback.data.sample_product_data import INITIAL_DATA
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataManager, SalesDataGenerator


def main():
    """Main example demonstrating SalesDataManager usage."""
    
    print("🚀 SalesDataManager Usage Example")
    print("=" * 50)
    
    # Check if we have the required environment variables
    required_vars = [
        "DATABRICKS_HOST",
        "DATABRICKS_HTTP_PATH", 
        "DATABRICKS_TOKEN",
        "DATABRICKS_CATALOG",
        "DATABRICKS_SCHEMA"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before running this example.")
        return
    
    try:
        # Example 1: Create a SalesDataManager instance
        print("\n📊 Example 1: Creating SalesDataManager")
        print("-" * 40)
        
        # Create manager instance - handles connection, table names, etc.
        manager = SalesDataManager()
        print("✅ Created SalesDataManager instance")
        print(f"   - Connection: {manager.conn}")
        print(f"   - Generator: {manager.generator}")
        
        # Example 2: Generate data locally (no Unity Catalog needed)
        print("\n🔧 Example 2: Generate Data Locally")
        print("-" * 40)
        
        # Use the generator directly for local data generation
        generator = SalesDataGenerator()
        
        # Generate data for a specific date range
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        df = generator.generate_time_series_data(INITIAL_DATA, start_date, end_date)
        print(f"✅ Generated {len(df)} sales records locally")
        print(f"   - Date range: {start_date} to {end_date}")
        print(f"   - Products: {len(INITIAL_DATA)}")
        print(f"   - Total sales: {df['SALES'].sum():,}")
        
        # Show sample data
        print("\n📋 Sample generated data:")
        sample_data = df.head(5)[['SELL_ID', 'PRODUCT_NAME', 'DATE', 'SALES']]
        print(sample_data.to_string(index=False))
        
        # Example 3: Write data to Unity Catalog
        print("\n💾 Example 3: Write to Unity Catalog")
        print("-" * 40)
        
        # Write the generated data to Unity Catalog
        result = manager.write_sales_data(
            products=INITIAL_DATA,
            table_name="product_sales",
            start_date=start_date,
            end_date=end_date,
            overwrite=True  # Overwrite existing data
        )
        
        if isinstance(result, int):
            print(f"✅ Successfully wrote {result} rows to Unity Catalog")
        else:
            print(f"❌ Failed to write data: {result[0]}")
            return
        
        # Example 4: Read data from Unity Catalog
        print("\n📖 Example 4: Read from Unity Catalog")
        print("-" * 40)
        
        # Read all data for the month
        df_read = manager.read_sales_data(
            table_name="product_sales",
            start_date=start_date,
            end_date=end_date
        )
        print(f"✅ Read {len(df_read)} records from Unity Catalog")
        
        # Read specific products only
        specific_products = ["SELL001", "SELL003"]  # Milk and Tim Tams
        df_filtered = manager.read_sales_data(
            table_name="product_sales",
            start_date=start_date,
            end_date=end_date,
            product_ids=specific_products,
            limit=10
        )
        print(f"✅ Read {len(df_filtered)} records for specific products")
        print(f"   - Products: {specific_products}")
        print(f"   - Limited to: 10 records")
        
        # Example 5: Get sales summary
        print("\n📊 Example 5: Get Sales Summary")
        print("-" * 40)
        
        # Get monthly summary with aggregations
        summary = manager.get_sales_summary(
            table_name="product_sales",
            start_date=start_date,
            end_date=end_date
        )
        print(f"✅ Generated summary with {len(summary)} aggregated records")
        
        # Show summary data
        print("\n📈 Sales Summary:")
        summary_display = summary[['PRODUCT_NAME', 'TOTAL_SALES', 'AVG_DAILY_SALES', 'MAX_DAILY_SALES']].head(5)
        print(summary_display.to_string(index=False))
        
        # Example 6: Check table existence
        print("\n🔍 Example 6: Check Table Existence")
        print("-" * 40)
        
        # Check if our table exists
        exists = manager.check_table_exists("product_sales")
        print(f"✅ Sales table exists: {exists}")
        
        # Check if a non-existent table exists
        not_exists = manager.check_table_exists("non_existent_table")
        print(f"✅ Non-existent table exists: {not_exists}")
        
        # Example 7: Initialize complete tables
        print("\n🏗️  Example 7: Initialize Complete Tables")
        print("-" * 40)
        
        # Initialize both product and sales tables
        init_results = manager.initialize_tables(INITIAL_DATA)
        print("✅ Initialization results:")
        for table_name, result in init_results.items():
            if isinstance(result, int):
                print(f"   - {table_name}: {result} rows")
            else:
                print(f"   - {table_name}: Error - {result[0]}")
        
        # Example 8: Real-world scenario - Monthly report
        print("\n📈 Example 8: Real-world Scenario - Monthly Report")
        print("-" * 40)
        
        # Generate data for the last 3 months
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        print(f"Generating 3-month sales data: {start_date} to {end_date}")
        
        # Write new data (append mode)
        result = manager.write_sales_data(
            products=INITIAL_DATA,
            table_name="product_sales",
            start_date=start_date,
            end_date=end_date,
            overwrite=False  # Append to existing data
        )
        
        if isinstance(result, int):
            print(f"✅ Added {result} new sales records")
            
            # Get comprehensive summary
            full_summary = manager.get_sales_summary(
                table_name="product_sales",
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"✅ Generated comprehensive summary with {len(full_summary)} records")
            
            # Show top performing products
            top_products = full_summary.groupby('PRODUCT_NAME')['TOTAL_SALES'].sum().sort_values(ascending=False).head(3)
            print("\n🏆 Top 3 Products by Total Sales:")
            for product, sales in top_products.items():
                print(f"   - {product}: {sales:,.0f} units")
        
        # Example 9: Error handling demonstration
        print("\n🛡️  Example 9: Error Handling")
        print("-" * 40)
        
        try:
            # Try to read from non-existent table
            df_error = manager.read_sales_data("non_existent_table")
            print("❌ This should not print")
        except Exception as e:
            print(f"✅ Error properly caught: {str(e)[:50]}...")
        
        print("\n🎉 SalesDataManager Example Completed Successfully!")
        print("\n📝 Key Takeaways:")
        print("  - Single manager instance handles all operations")
        print("  - Clean, simple method calls")
        print("  - Automatic connection management")
        print("  - Consistent error handling")
        print("  - Easy to extend and modify")
        print("  - Perfect for Dash app integration")
        
    except Exception as e:
        print(f"❌ Error during example execution: {str(e)}")
        print("Please check your Databricks connection settings and try again.")


def quick_start_example():
    """Quick start example for basic usage."""
    print("\n⚡ Quick Start Example")
    print("=" * 30)
    
    # 1. Create manager
    manager = SalesDataManager()
    
    # 2. Generate and write data
    result = manager.write_sales_data(
        products=INITIAL_DATA,
        table_name="product_sales",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(f"✅ Wrote {result} rows")
    
    # 3. Read data
    df = manager.read_sales_data("product_sales", "2024-01-01", "2024-01-31")
    print(f"✅ Read {len(df)} rows")
    
    # 4. Get summary
    summary = manager.get_sales_summary("product_sales", "2024-01-01", "2024-01-31")
    print(f"✅ Summary: {len(summary)} aggregated records")
    
    print("🎯 That's it! Simple and efficient.")


if __name__ == "__main__":
    main()
    
    # Uncomment to run quick start example
    # quick_start_example() 