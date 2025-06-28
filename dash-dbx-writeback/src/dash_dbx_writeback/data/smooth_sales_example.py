#!/usr/bin/env python3
"""
Smooth Sales Data Example with Store Associations

This example demonstrates the enhanced SalesDataGenerator with:
- Smoother, more predictable sales data (reduced noise)
- Store associations with realistic store patterns
- Store-specific weekly patterns and characteristics
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.dash_dbx_writeback.data.sample_product_data import INITIAL_DATA
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataGenerator, SalesDataManager


def demonstrate_smooth_sales():
    """Demonstrate the new smooth sales data with store associations."""
    
    print("🚀 Smooth Sales Data with Store Associations")
    print("=" * 50)
    
    # Create generator instance
    generator = SalesDataGenerator()
    
    # Example 1: Generate data for a single store (no Unity Catalog needed)
    print("\n📊 Example 1: Single Store Data")
    print("-" * 40)
    
    # Generate data for one store only
    df_single = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2024-01-01", 
        "2024-01-31", 
        include_stores=False  # Only STORE001
    )
    
    print(f"✅ Generated {len(df_single)} sales records for single store")
    print(f"   - Products: {len(INITIAL_DATA)}")
    print(f"   - Date range: 2024-01-01 to 2024-01-31")
    print(f"   - Total sales: {df_single['SALES'].sum():,}")
    
    # Show sample data
    print("\n📋 Sample single store data:")
    sample_data = df_single.head(5)[['SELL_ID', 'PRODUCT_NAME', 'DATE', 'SALES']]
    print(sample_data.to_string(index=False))
    
    # Example 2: Generate data for all stores
    print("\n🏪 Example 2: Multi-Store Data")
    print("-" * 40)
    
    # Generate data for all stores
    df_multi = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2024-01-01", 
        "2024-01-31", 
        include_stores=True  # All stores
    )
    
    print(f"✅ Generated {len(df_multi)} sales records for all stores")
    print(f"   - Stores: {df_multi['STORE_ID'].nunique()}")
    print(f"   - Products: {df_multi['SELL_ID'].nunique()}")
    print(f"   - Total sales: {df_multi['SALES'].sum():,}")
    
    # Show store information
    print("\n🏪 Store Information:")
    stores_info = df_multi[['STORE_ID', 'STORE_NAME', 'STORE_LOCATION', 'STORE_SIZE']].drop_duplicates()
    print(stores_info.to_string(index=False))
    
    # Example 3: Compare sales patterns across stores
    print("\n📈 Example 3: Sales Patterns Across Stores")
    print("-" * 40)
    
    # Compare total sales by store
    store_sales = df_multi.groupby(['STORE_ID', 'STORE_NAME', 'STORE_SIZE'])['SALES'].sum().reset_index()
    store_sales = store_sales.sort_values('SALES', ascending=False)
    
    print("🏆 Total Sales by Store:")
    for _, row in store_sales.iterrows():
        print(f"   - {row['STORE_NAME']} ({row['STORE_SIZE']}): {row['SALES']:,.0f} units")
    
    # Example 4: Compare product performance across stores
    print("\n🍞 Example 4: Product Performance Across Stores")
    print("-" * 40)
    
    # Compare milk sales across stores
    milk_sales = df_multi[df_multi['PRODUCT_NAME'] == 'Coles Brand Milk 2L'].groupby(['STORE_ID', 'STORE_NAME'])['SALES'].sum().reset_index()
    milk_sales = milk_sales.sort_values('SALES', ascending=False)
    
    print("🥛 Milk Sales by Store:")
    for _, row in milk_sales.iterrows():
        print(f"   - {row['STORE_NAME']}: {row['SALES']:,.0f} units")
    
    # Example 5: Weekly patterns by store type
    print("\n📅 Example 5: Weekly Patterns by Store Type")
    print("-" * 40)
    
    # Add day of week for analysis
    df_multi['DAY_OF_WEEK'] = pd.to_datetime(df_multi['DATE']).dt.day_name()
    
    # Compare weekend vs weekday sales by store
    weekly_patterns = df_multi.groupby(['STORE_ID', 'STORE_NAME', 'DAY_OF_WEEK'])['SALES'].sum().reset_index()
    
    # Show business district vs shopping district patterns
    business_stores = ['STORE001']  # Sydney CBD
    shopping_stores = ['STORE002', 'STORE004']  # Bondi Junction, Chatswood
    
    print("🏢 Business District (Sydney CBD) - Weekday vs Weekend:")
    business_data = weekly_patterns[weekly_patterns['STORE_ID'].isin(business_stores)]
    for _, row in business_data.iterrows():
        print(f"   - {row['DAY_OF_WEEK']}: {row['SALES']:,.0f} units")
    
    print("\n🛍️ Shopping District (Bondi Junction, Chatswood) - Weekday vs Weekend:")
    shopping_data = weekly_patterns[weekly_patterns['STORE_ID'].isin(shopping_stores)]
    for _, row in shopping_data.iterrows():
        print(f"   - {row['DAY_OF_WEEK']}: {row['SALES']:,.0f} units")
    
    # Example 6: Smoothness comparison
    print("\n📊 Example 6: Data Smoothness Analysis")
    print("-" * 40)
    
    # Calculate coefficient of variation (lower = smoother)
    def calculate_smoothness(df, group_cols):
        cv = df.groupby(group_cols)['SALES'].agg(['mean', 'std']).reset_index()
        cv['cv'] = cv['std'] / cv['mean']
        return cv
    
    # Compare smoothness by product
    product_smoothness = calculate_smoothness(df_multi, ['PRODUCT_NAME'])
    product_smoothness = product_smoothness.sort_values('cv')
    
    print("📈 Product Smoothness (Coefficient of Variation - lower is smoother):")
    for _, row in product_smoothness.iterrows():
        print(f"   - {row['PRODUCT_NAME']}: {row['cv']:.3f}")
    
    # Example 7: Store size impact
    print("\n🏪 Example 7: Store Size Impact")
    print("-" * 40)
    
    size_performance = df_multi.groupby('STORE_SIZE')['SALES'].agg(['sum', 'mean', 'count']).reset_index()
    
    print("📊 Sales Performance by Store Size:")
    for _, row in size_performance.iterrows():
        print(f"   - {row['STORE_SIZE'].title()}: {row['sum']:,.0f} total, {row['mean']:.1f} avg daily")
    
    print("\n🎉 Smooth Sales Data Example Completed!")
    print("\n📝 Key Improvements:")
    print("  ✅ Reduced volatility for smoother, more predictable data")
    print("  ✅ Added realistic store associations")
    print("  ✅ Store-specific weekly patterns (business vs shopping districts)")
    print("  ✅ Store size and location effects")
    print("  ✅ Premium location multipliers")
    print("  ✅ Consistent noise generation for reproducibility")


def quick_comparison():
    """Quick comparison of old vs new volatility levels."""
    print("\n⚡ Quick Volatility Comparison")
    print("=" * 30)
    
    # Old volatility levels (before changes)
    old_volatility = {
        "Coles Brand Milk 2L": 0.15,
        "Woolworths Bread White": 0.12,
        "Arnott's Tim Tams": 0.25,
        "Vegemite 380g": 0.10,
        "Kangaroo Steak": 0.30,
        "Tim Tam Slam Kit": 0.40
    }
    
    # New volatility levels (after changes)
    new_volatility = {
        "Coles Brand Milk 2L": 0.08,
        "Woolworths Bread White": 0.06,
        "Arnott's Tim Tams": 0.12,
        "Vegemite 380g": 0.05,
        "Kangaroo Steak": 0.15,
        "Tim Tam Slam Kit": 0.20
    }
    
    print("📊 Volatility Reduction:")
    for product in old_volatility.keys():
        old_val = old_volatility[product]
        new_val = new_volatility[product]
        reduction = ((old_val - new_val) / old_val) * 100
        print(f"   - {product}: {old_val:.2f} → {new_val:.2f} ({reduction:.0f}% reduction)")


if __name__ == "__main__":
    demonstrate_smooth_sales()
    quick_comparison() 