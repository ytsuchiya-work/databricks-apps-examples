#!/usr/bin/env python3
"""
Time Series Modeling Example with Enhanced Sales Data

This example demonstrates how to use the enhanced SalesDataGenerator for time series modeling:
- Data preparation and feature engineering
- Time series splits (train/validation/test)
- Model-ready datasets
- Data quality assessment
- Feature importance analysis
"""

import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.dash_dbx_writeback.data.sample_product_data import INITIAL_DATA
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataGenerator, SalesDataManager


def demonstrate_timeseries_modeling():
    """Demonstrate time series modeling capabilities with the enhanced sales data."""
    
    print("🚀 Time Series Modeling with Enhanced Sales Data")
    print("=" * 60)
    
    # Create generator instance
    generator = SalesDataGenerator()
    
    # Example 1: Generate data with time features for modeling
    print("\n📊 Example 1: Generate Data with Time Features")
    print("-" * 50)
    
    # Generate data with time features and lag features
    df = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2023-01-01", 
        "2024-12-31", 
        include_stores=True,
        add_time_features=True,
        add_lag_features=True
    )
    
    print(f"✅ Generated {len(df)} records with time series features")
    print(f"   - Products: {df['SELL_ID'].nunique()}")
    print(f"   - Stores: {df['STORE_ID'].nunique()}")
    print(f"   - Date range: {df['DATE'].min()} to {df['DATE'].max()}")
    print(f"   - Features: {len(df.columns)} total columns")
    
    # Show time features
    time_features = [col for col in df.columns if any(x in col.lower() for x in ['year', 'month', 'day', 'week', 'quarter', 'sin', 'cos'])]
    print(f"\n⏰ Time Features ({len(time_features)}):")
    for feature in time_features[:10]:  # Show first 10
        print(f"   - {feature}")
    if len(time_features) > 10:
        print(f"   ... and {len(time_features) - 10} more")
    
    # Show lag features
    lag_features = [col for col in df.columns if 'lag' in col.lower()]
    print(f"\n📈 Lag Features ({len(lag_features)}):")
    for feature in lag_features:
        print(f"   - {feature}")
    
    # Example 2: Data quality assessment
    print("\n🔍 Example 2: Data Quality Assessment")
    print("-" * 50)
    
    summary = generator.get_modeling_summary(df)
    
    print("📊 Data Information:")
    for key, value in summary['data_info'].items():
        print(f"   - {key}: {value}")
    
    print("\n📈 Sales Statistics:")
    for key, value in summary['sales_stats'].items():
        if isinstance(value, float):
            print(f"   - {key}: {value:.2f}")
        else:
            print(f"   - {key}: {value}")
    
    print("\n✅ Time Series Quality:")
    for key, value in summary['time_series_quality'].items():
        if isinstance(value, dict):
            print(f"   - {key}: {len(value)} product-store combinations affected")
        else:
            print(f"   - {key}: {value}")
    
    # Example 3: Prepare data for modeling
    print("\n🤖 Example 3: Prepare Data for Modeling")
    print("-" * 50)
    
    # Prepare datasets with proper time series splits
    datasets = generator.prepare_for_modeling(
        df,
        target_column='SALES',
        group_columns=['SELL_ID', 'STORE_ID'],
        test_size=0.2,
        validation_size=0.1
    )
    
    print("📊 Dataset Splits:")
    for split_name, dataset in datasets.items():
        metadata = dataset['metadata']
        print(f"   - {split_name.upper()}:")
        print(f"     * Samples: {metadata['n_samples']:,}")
        print(f"     * Features: {len(metadata['feature_columns'])}")
        print(f"     * Date range: {metadata['date_range'][0]} to {metadata['date_range'][1]}")
        print(f"     * Target: {metadata['target_column']}")
    
    # Example 4: Feature analysis
    print("\n📊 Example 4: Feature Analysis")
    print("-" * 50)
    
    # Analyze feature correlations with target
    train_data = datasets['train']
    X_train = train_data['X']
    y_train = train_data['y']
    
    # Calculate correlations
    correlations = X_train.corrwith(y_train).abs().sort_values(ascending=False)
    
    print("🎯 Top 10 Features by Correlation with Sales:")
    for feature, corr in correlations.head(10).items():
        print(f"   - {feature}: {corr:.3f}")
    
    # Example 5: Time series patterns analysis
    print("\n📅 Example 5: Time Series Patterns Analysis")
    print("-" * 50)
    
    # Analyze weekly patterns
    weekly_analysis = df.groupby(['DAY_OF_WEEK', 'STORE_SIZE'])['SALES'].mean().reset_index()
    
    print("📈 Average Sales by Day of Week and Store Size:")
    for _, row in weekly_analysis.iterrows():
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][row['DAY_OF_WEEK']]
        print(f"   - {day_name} ({row['STORE_SIZE']}): {row['SALES']:.1f} units")
    
    # Analyze seasonal patterns
    seasonal_analysis = df.groupby(['MONTH', 'CATEGORY_NAME'])['SALES'].mean().reset_index()
    
    print("\n🌤️ Seasonal Patterns by Category:")
    for category in df['CATEGORY_NAME'].unique():
        category_data = seasonal_analysis[seasonal_analysis['CATEGORY_NAME'] == category]
        print(f"   - {category}:")
        for _, row in category_data.iterrows():
            month_name = datetime(2024, row['MONTH'], 1).strftime('%B')
            print(f"     * {month_name}: {row['SALES']:.1f} units")
    
    # Example 6: Model-ready dataset export
    print("\n💾 Example 6: Model-Ready Dataset Export")
    print("-" * 50)
    
    # Export datasets for modeling
    export_path = "timeseries_modeling_data"
    os.makedirs(export_path, exist_ok=True)
    
    for split_name, dataset in datasets.items():
        # Combine features and target
        combined_df = dataset['X'].copy()
        combined_df[dataset['metadata']['target_column']] = dataset['y']
        
        # Save to CSV
        filename = f"{export_path}/{split_name}_data.csv"
        combined_df.to_csv(filename, index=False)
        print(f"   ✅ Saved {split_name} data: {filename} ({len(combined_df):,} rows)")
    
    # Save metadata
    metadata_df = pd.DataFrame([
        {
            'split': split_name,
            'samples': dataset['metadata']['n_samples'],
            'features': len(dataset['metadata']['feature_columns']),
            'start_date': dataset['metadata']['date_range'][0],
            'end_date': dataset['metadata']['date_range'][1]
        }
        for split_name, dataset in datasets.items()
    ])
    metadata_df.to_csv(f"{export_path}/dataset_metadata.csv", index=False)
    print(f"   ✅ Saved metadata: {export_path}/dataset_metadata.csv")
    
    # Example 7: Feature importance summary
    print("\n🎯 Example 7: Feature Importance Summary")
    print("-" * 50)
    
    # Categorize features
    feature_categories = {
        'Time Features': [col for col in X_train.columns if any(x in col.lower() for x in ['year', 'month', 'day', 'week', 'quarter', 'sin', 'cos'])],
        'Lag Features': [col for col in X_train.columns if 'lag' in col.lower()],
        'Rolling Features': [col for col in X_train.columns if any(x in col.lower() for x in ['mean', 'std', 'min', 'max']) and 'lag' not in col.lower()],
        'Store Features': [col for col in X_train.columns if 'store' in col.lower()],
        'Category Features': [col for col in X_train.columns if 'category' in col.lower()],
        'Loyalty Features': [col for col in X_train.columns if 'loyalty' in col.lower()],
        'Holiday Features': [col for col in X_train.columns if 'holiday' in col.lower()],
        'Other Features': [col for col in X_train.columns if not any(x in col.lower() for x in ['year', 'month', 'day', 'week', 'quarter', 'sin', 'cos', 'lag', 'mean', 'std', 'min', 'max', 'store', 'category', 'loyalty', 'holiday'])]
    }
    
    print("📊 Feature Categories:")
    for category, features in feature_categories.items():
        if features:
            avg_corr = correlations[features].mean()
            print(f"   - {category}: {len(features)} features (avg correlation: {avg_corr:.3f})")
    
    print("\n🎉 Time Series Modeling Example Completed!")
    print("\n📝 Key Capabilities:")
    print("  ✅ Comprehensive time features (cyclical encoding)")
    print("  ✅ Lag features for autoregressive models")
    print("  ✅ Rolling statistics (mean, std, min, max)")
    print("  ✅ Proper time series splits (no data leakage)")
    print("  ✅ Data quality assessment and validation")
    print("  ✅ Feature importance analysis")
    print("  ✅ Model-ready dataset export")
    print("  ✅ Store and product-specific patterns")


def demonstrate_advanced_features():
    """Demonstrate advanced time series modeling features."""
    
    print("\n🔬 Advanced Time Series Features")
    print("=" * 40)
    
    generator = SalesDataGenerator()
    
    # Generate data with all features
    df = generator.generate_time_series_data(
        INITIAL_DATA[:2],  # Use fewer products for demonstration
        "2023-01-01", 
        "2024-06-30", 
        include_stores=True,
        add_time_features=True,
        add_lag_features=True
    )
    
    # Example: Custom lag features
    print("\n📈 Custom Lag Features:")
    custom_lags = [1, 3, 7, 14, 30, 90]  # Different lag periods
    df_custom = generator._add_lag_features(df, lags=custom_lags)
    
    lag_features = [col for col in df_custom.columns if 'lag' in col.lower()]
    print(f"   - Added {len(lag_features)} lag features: {lag_features}")
    
    # Example: Rolling window analysis
    print("\n📊 Rolling Window Analysis:")
    rolling_features = [col for col in df_custom.columns if any(x in col.lower() for x in ['mean', 'std', 'min', 'max']) and 'lag' not in col.lower()]
    print(f"   - Rolling features: {rolling_features}")
    
    # Example: Cyclical encoding benefits
    print("\n🔄 Cyclical Encoding Benefits:")
    cyclical_features = [col for col in df_custom.columns if any(x in col.lower() for x in ['sin', 'cos'])]
    print(f"   - Cyclical features: {cyclical_features}")
    print("   - Benefits: Preserves periodicity, avoids discontinuity at boundaries")
    
    # Example: Holiday effects
    print("\n🎄 Holiday Effects:")
    holiday_data = df_custom[df_custom['IS_HOLIDAY'] == 1]
    regular_data = df_custom[df_custom['IS_HOLIDAY'] == 0]
    
    if len(holiday_data) > 0:
        holiday_avg = holiday_data['SALES'].mean()
        regular_avg = regular_data['SALES'].mean()
        holiday_effect = (holiday_avg / regular_avg - 1) * 100
        print(f"   - Holiday sales: {holiday_avg:.1f} units (avg)")
        print(f"   - Regular sales: {regular_avg:.1f} units (avg)")
        print(f"   - Holiday effect: {holiday_effect:+.1f}%")


def demonstrate_modeling_workflow():
    """Demonstrate a complete modeling workflow."""
    
    print("\n🔄 Complete Modeling Workflow")
    print("=" * 35)
    
    generator = SalesDataGenerator()
    
    # Step 1: Generate data
    print("\n1️⃣ Step 1: Generate Time Series Data")
    df = generator.generate_time_series_data(
        INITIAL_DATA, 
        "2023-01-01", 
        "2024-12-31", 
        include_stores=True,
        add_time_features=True,
        add_lag_features=True
    )
    
    # Step 2: Data quality check
    print("\n2️⃣ Step 2: Data Quality Assessment")
    summary = generator.get_modeling_summary(df)
    print(f"   - Data quality: {'✅ Good' if summary['time_series_quality']['consistent_frequency'] else '❌ Issues'}")
    print(f"   - Missing dates: {len(summary['time_series_quality']['missing_dates'])} combinations")
    
    # Step 3: Prepare for modeling
    print("\n3️⃣ Step 3: Prepare for Modeling")
    datasets = generator.prepare_for_modeling(df)
    
    # Step 4: Feature analysis
    print("\n4️⃣ Step 4: Feature Analysis")
    train_data = datasets['train']
    correlations = train_data['X'].corrwith(train_data['y']).abs().sort_values(ascending=False)
    top_features = correlations.head(5).index.tolist()
    print(f"   - Top features: {top_features}")
    
    # Step 5: Model-ready datasets
    print("\n5️⃣ Step 5: Model-Ready Datasets")
    for split_name, dataset in datasets.items():
        print(f"   - {split_name}: {dataset['metadata']['n_samples']:,} samples, {len(dataset['metadata']['feature_columns'])} features")
    
    print("\n✅ Workflow completed successfully!")


if __name__ == "__main__":
    demonstrate_timeseries_modeling()
    demonstrate_advanced_features()
    demonstrate_modeling_workflow() 