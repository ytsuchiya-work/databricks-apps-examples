#!/usr/bin/env python3
"""
Shelf Space Analysis Example

This example demonstrates the new shelf space features and provides analysis of:
- Shelf space utilization by product category
- Sales efficiency per unit of shelf space
- Store layout optimization insights
- Space allocation recommendations
"""

import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.dash_dbx_writeback.data.sample_product_data import INITIAL_DATA
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataGenerator, SalesDataManager


def demonstrate_shelf_space_features():
    """Demonstrate the new shelf space features and analysis."""
    
    print("🏪 Shelf Space Analysis with Enhanced Product Data")
    print("=" * 55)
    
    # Create generator instance
    generator = SalesDataGenerator()
    
    # Example 1: Generate data with shelf space features
    print("\n📊 Example 1: Generate Data with Shelf Space Features")
    print("-" * 55)
    
    # Generate data with time features (includes shelf space features)
    df = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2024-01-01", 
        "2024-01-31", 
        include_stores=True,
        add_time_features=True,
        add_lag_features=False  # Keep it simple for this example
    )
    
    print(f"✅ Generated {len(df)} records with shelf space features")
    print(f"   - Products: {df['SELL_ID'].nunique()}")
    print(f"   - Stores: {df['STORE_ID'].nunique()}")
    print(f"   - Date range: {df['DATE'].min()} to {df['DATE'].max()}")
    
    # Show shelf space features
    shelf_features = [col for col in df.columns if 'shelf' in col.lower() or 'space' in col.lower()]
    print(f"\n📏 Shelf Space Features ({len(shelf_features)}):")
    for feature in shelf_features:
        print(f"   - {feature}")
    
    # Example 2: Product shelf space analysis
    print("\n📦 Example 2: Product Shelf Space Analysis")
    print("-" * 55)
    
    # Analyze shelf space by product
    product_space = df.groupby(['SELL_ID', 'PRODUCT_NAME', 'CATEGORY_NAME', 'PACK_SIZE'])['SHELF_SPACE_CM'].first().reset_index()
    product_space = product_space.sort_values('SHELF_SPACE_CM', ascending=False)
    
    print("📏 Product Shelf Space Requirements:")
    for _, row in product_space.iterrows():
        print(f"   - {row['PRODUCT_NAME']} ({row['PACK_SIZE']}): {row['SHELF_SPACE_CM']} cm")
    
    # Example 3: Category shelf space analysis
    print("\n🏷️ Example 3: Category Shelf Space Analysis")
    print("-" * 55)
    
    # Analyze shelf space by category
    category_space = df.groupby('CATEGORY_NAME').agg({
        'SHELF_SPACE_CM': ['mean', 'min', 'max', 'std'],
        'SALES': 'sum',
        'SALES_PER_CM': 'mean'
    }).round(2)
    
    print("📊 Category Shelf Space Statistics:")
    for category in category_space.index:
        stats = category_space.loc[category]
        print(f"   - {category}:")
        print(f"     * Avg shelf space: {stats[('SHELF_SPACE_CM', 'mean')]} cm")
        print(f"     * Range: {stats[('SHELF_SPACE_CM', 'min')]} - {stats[('SHELF_SPACE_CM', 'max')]} cm")
        print(f"     * Sales per cm: {stats[('SALES_PER_CM', 'mean')]:.2f} units/cm")
    
    # Example 4: Store shelf space utilization
    print("\n🏪 Example 4: Store Shelf Space Utilization")
    print("-" * 55)
    
    # Analyze shelf space utilization by store
    store_utilization = df.groupby(['STORE_ID', 'STORE_NAME', 'STORE_SIZE']).agg({
        'SHELF_SPACE_CM': 'sum',
        'SALES': 'sum',
        'SALES_PER_CM': 'mean',
        'VOLUME_UTILIZATION': 'mean'
    }).round(2)
    
    print("📊 Store Shelf Space Utilization:")
    for store_id in store_utilization.index.get_level_values(0).unique():
        store_data = store_utilization.loc[store_id]
        print(f"   - {store_data.name[1]} ({store_data.name[2]}):")
        print(f"     * Total shelf space: {store_data[('SHELF_SPACE_CM', 'sum')]:.0f} cm")
        print(f"     * Total sales: {store_data[('SALES', 'sum')]:.0f} units")
        print(f"     * Avg sales per cm: {store_data[('SALES_PER_CM', 'mean')]:.2f}")
        print(f"     * Volume utilization: {store_data[('VOLUME_UTILIZATION', 'mean')]:.1f}%")
    
    # Example 5: Shelf space efficiency ranking
    print("\n🏆 Example 5: Shelf Space Efficiency Ranking")
    print("-" * 55)
    
    # Rank products by sales efficiency per shelf space
    efficiency_ranking = df.groupby(['SELL_ID', 'PRODUCT_NAME', 'CATEGORY_NAME']).agg({
        'SALES': 'sum',
        'SHELF_SPACE_CM': 'first',
        'SALES_PER_CM': 'mean',
        'SPACE_EFFICIENCY': 'mean'
    }).reset_index()
    
    efficiency_ranking = efficiency_ranking.sort_values('SALES_PER_CM', ascending=False)
    
    print("🏆 Top 5 Most Space-Efficient Products:")
    for i, (_, row) in enumerate(efficiency_ranking.head(5).iterrows(), 1):
        print(f"   {i}. {row['PRODUCT_NAME']} ({row['CATEGORY_NAME']}):")
        print(f"      * Sales: {row['SALES']:.0f} units")
        print(f"      * Shelf space: {row['SHELF_SPACE_CM']} cm")
        print(f"      * Sales per cm: {row['SALES_PER_CM']:.2f}")
    
    print("\n📉 Bottom 5 Least Space-Efficient Products:")
    for i, (_, row) in enumerate(efficiency_ranking.tail(5).iterrows(), 1):
        print(f"   {i}. {row['PRODUCT_NAME']} ({row['CATEGORY_NAME']}):")
        print(f"      * Sales: {row['SALES']:.0f} units")
        print(f"      * Shelf space: {row['SHELF_SPACE_CM']} cm")
        print(f"      * Sales per cm: {row['SALES_PER_CM']:.2f}")
    
    # Example 6: Shelf space optimization recommendations
    print("\n💡 Example 6: Shelf Space Optimization Recommendations")
    print("-" * 55)
    
    # Calculate opportunity scores
    efficiency_ranking['OPPORTUNITY_SCORE'] = (
        efficiency_ranking['SALES_PER_CM'] * 
        efficiency_ranking['SHELF_SPACE_CM'] * 
        (1 - efficiency_ranking['SPACE_EFFICIENCY'])
    )
    
    # Find products with high opportunity for space optimization
    high_opportunity = efficiency_ranking[
        (efficiency_ranking['SHELF_SPACE_CM'] > 15) & 
        (efficiency_ranking['SALES_PER_CM'] < efficiency_ranking['SALES_PER_CM'].median())
    ].sort_values('OPPORTUNITY_SCORE', ascending=False)
    
    print("🎯 High-Opportunity Products for Space Optimization:")
    for i, (_, row) in enumerate(high_opportunity.head(3).iterrows(), 1):
        print(f"   {i}. {row['PRODUCT_NAME']}:")
        print(f"      * Current shelf space: {row['SHELF_SPACE_CM']} cm")
        print(f"      * Sales per cm: {row['SALES_PER_CM']:.2f}")
        print(f"      * Recommendation: Consider reducing shelf space allocation")
    
    # Example 7: Store layout recommendations
    print("\n🏗️ Example 7: Store Layout Recommendations")
    print("-" * 55)
    
    # Analyze space allocation by store size
    layout_analysis = df.groupby('STORE_SIZE').agg({
        'SHELF_SPACE_CM': ['mean', 'sum'],
        'SALES_PER_CM': 'mean',
        'VOLUME_UTILIZATION': 'mean'
    }).round(2)
    
    print("📊 Store Layout Analysis by Store Size:")
    for store_size in layout_analysis.index:
        stats = layout_analysis.loc[store_size]
        print(f"   - {store_size.title()} stores:")
        print(f"     * Avg shelf space per product: {stats[('SHELF_SPACE_CM', 'mean')]} cm")
        print(f"     * Avg sales per cm: {stats[('SALES_PER_CM', 'mean')]:.2f}")
        print(f"     * Volume utilization: {stats[('VOLUME_UTILIZATION', 'mean')]:.1f}%")
        
        # Provide recommendations
        if store_size == 'small':
            print(f"     * 💡 Recommendation: Focus on high-efficiency products")
        elif store_size == 'medium':
            print(f"     * 💡 Recommendation: Balance variety with efficiency")
        else:  # large
            print(f"     * 💡 Recommendation: Optimize space allocation by category")
    
    # Example 8: Category space allocation strategy
    print("\n📋 Example 8: Category Space Allocation Strategy")
    print("-" * 55)
    
    # Calculate optimal space allocation based on sales efficiency
    category_strategy = df.groupby('CATEGORY_NAME').agg({
        'SALES': 'sum',
        'SHELF_SPACE_CM': 'sum',
        'SALES_PER_CM': 'mean'
    }).reset_index()
    
    category_strategy['SALES_SHARE'] = category_strategy['SALES'] / category_strategy['SALES'].sum() * 100
    category_strategy['SPACE_SHARE'] = category_strategy['SHELF_SPACE_CM'] / category_strategy['SHELF_SPACE_CM'].sum() * 100
    category_strategy['EFFICIENCY_RATIO'] = category_strategy['SALES_SHARE'] / category_strategy['SPACE_SHARE']
    
    print("📊 Category Space Allocation Analysis:")
    for _, row in category_strategy.iterrows():
        print(f"   - {row['CATEGORY_NAME']}:")
        print(f"     * Sales share: {row['SALES_SHARE']:.1f}%")
        print(f"     * Space share: {row['SPACE_SHARE']:.1f}%")
        print(f"     * Efficiency ratio: {row['EFFICIENCY_RATIO']:.2f}")
        
        # Provide recommendations
        if row['EFFICIENCY_RATIO'] > 1.2:
            print(f"     * ✅ High efficiency - consider increasing space")
        elif row['EFFICIENCY_RATIO'] < 0.8:
            print(f"     * ⚠️ Low efficiency - consider reducing space")
        else:
            print(f"     * ➡️ Balanced efficiency - maintain current allocation")
    
    print("\n🎉 Shelf Space Analysis Example Completed!")
    print("\n📝 Key Insights:")
    print("  ✅ Shelf space requirements vary significantly by product category")
    print("  ✅ Sales per cm is a key efficiency metric")
    print("  ✅ Store size affects optimal space allocation")
    print("  ✅ Category-specific strategies improve overall efficiency")
    print("  ✅ Data-driven recommendations for space optimization")


def demonstrate_shelf_space_modeling():
    """Demonstrate how shelf space features can be used in time series modeling."""
    
    print("\n🤖 Shelf Space Features in Time Series Modeling")
    print("=" * 50)
    
    generator = SalesDataGenerator()
    
    # Generate data with all features
    df = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2024-01-01", 
        "2024-01-31", 
        include_stores=True,
        add_time_features=True,
        add_lag_features=True
    )
    
    # Prepare for modeling
    datasets = generator.prepare_for_modeling(df)
    
    # Analyze shelf space feature importance
    train_data = datasets['train']
    X_train = train_data['X']
    y_train = train_data['y']
    
    # Find shelf space related features
    shelf_features = [col for col in X_train.columns if 'shelf' in col.lower() or 'space' in col.lower()]
    
    # Calculate correlations with sales
    correlations = X_train[shelf_features].corrwith(y_train).abs().sort_values(ascending=False)
    
    print("🎯 Shelf Space Feature Importance:")
    for feature, corr in correlations.items():
        print(f"   - {feature}: {corr:.3f}")
    
    # Show feature categories
    feature_categories = {
        'Shelf Space Size': [col for col in shelf_features if any(x in col for x in ['SMALL', 'MEDIUM', 'LARGE'])],
        'Shelf Space Efficiency': [col for col in shelf_features if 'EFFICIENCY' in col or 'PER_CM' in col],
        'Shelf Space Utilization': [col for col in shelf_features if 'UTILIZATION' in col or 'VOLUME' in col]
    }
    
    print("\n📊 Shelf Space Feature Categories:")
    for category, features in feature_categories.items():
        if features:
            avg_corr = correlations[features].mean()
            print(f"   - {category}: {len(features)} features (avg correlation: {avg_corr:.3f})")
    
    print("\n✅ Shelf space features are now integrated into time series modeling!")


if __name__ == "__main__":
    demonstrate_shelf_space_features()
    demonstrate_shelf_space_modeling() 