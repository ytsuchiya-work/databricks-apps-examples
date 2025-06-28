import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from ..config.unity_catalog import get_full_table_name
from ..config.workspace_client import get_connection
from ..callbacks.tables import (
    insert_overwrite_table,
    check_table_exists,
    log
)


class UnityCatalogManager:
    """Base class for Unity Catalog operations to eliminate code repetition."""
    
    def __init__(self, conn: Optional[Any] = None):
        self.conn = conn or get_connection()
    
    def _get_full_table_name(self, table_name: str) -> str:
        """Get full table name with catalog.schema prefix."""
        return get_full_table_name(table_name)
    
    def _check_table_exists(self, table_name: str) -> bool:
        """Check if table exists in Unity Catalog."""
        full_table_name = self._get_full_table_name(table_name)
        return check_table_exists(full_table_name, self.conn)
    
    def _write_dataframe(self, df: pd.DataFrame, table_name: str, overwrite: bool = True) -> Union[int, Tuple[str, int]]:
        """Write DataFrame to Unity Catalog table."""
        full_table_name = self._get_full_table_name(table_name)
        return insert_overwrite_table(
            table_name=full_table_name,
            df=df,
            conn=self.conn,
            overwrite=overwrite
        )
    
    def _read_dataframe(self, table_name: str, query: str) -> pd.DataFrame:
        """Read DataFrame from Unity Catalog table."""
        full_table_name = self._get_full_table_name(table_name)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()


class SalesDataGenerator:
    """Handles realistic sales data generation with product-specific patterns and store associations.
    
    Optimized for time series modeling with:
    - Proper time features (day of week, month, quarter, etc.)
    - Consistent data quality
    - Trend and seasonality patterns
    - Lag features for autoregressive models
    - Exogenous variables (holidays, events)
    """
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        
        # Store configurations with realistic characteristics
        self.stores = {
            "STORE001": {
                "name": "Coles Central Sydney",
                "location": "Sydney CBD",
                "size": "large",
                "traffic_multiplier": 1.4,  # High traffic area
                "premium_multiplier": 1.2,  # Premium location
                "weekly_pattern": "business_district"  # Business district pattern
            },
            "STORE002": {
                "name": "Woolworths Bondi Junction",
                "location": "Bondi Junction",
                "size": "large",
                "traffic_multiplier": 1.3,
                "premium_multiplier": 1.3,  # Very premium area
                "weekly_pattern": "shopping_district"
            },
            "STORE003": {
                "name": "Coles Parramatta Westfield",
                "location": "Parramatta",
                "size": "medium",
                "traffic_multiplier": 1.1,
                "premium_multiplier": 1.0,
                "weekly_pattern": "suburban"
            },
            "STORE004": {
                "name": "Woolworths Chatswood Chase",
                "location": "Chatswood",
                "size": "medium",
                "traffic_multiplier": 1.2,
                "premium_multiplier": 1.1,
                "weekly_pattern": "shopping_district"
            },
            "STORE005": {
                "name": "Coles Penrith Plaza",
                "location": "Penrith",
                "size": "small",
                "traffic_multiplier": 0.9,
                "premium_multiplier": 0.8,
                "weekly_pattern": "suburban"
            },
            "STORE006": {
                "name": "Woolworths Campbelltown",
                "location": "Campbelltown",
                "size": "small",
                "traffic_multiplier": 0.8,
                "premium_multiplier": 0.7,
                "weekly_pattern": "suburban"
            }
        }
        
        # Product-specific characteristics (reduced volatility for smoother data)
        self.product_profiles = {
            "Coles Brand Milk 2L": {
                "base_sales": 150, "category": "Dairy", "seasonality": "low",
                "weekly_pattern": "weekend_boost", "trend": 0.02, "volatility": 0.08, "loyalty_effect": 1.2
            },
            "Woolworths Bread White": {
                "base_sales": 120, "category": "Bakery", "seasonality": "low",
                "weekly_pattern": "weekend_boost", "trend": 0.01, "volatility": 0.06, "loyalty_effect": 1.1
            },
            "Arnott's Tim Tams": {
                "base_sales": 45, "category": "Confectionery", "seasonality": "high",
                "weekly_pattern": "weekend_boost", "trend": 0.03, "volatility": 0.12, "loyalty_effect": 1.3
            },
            "Vegemite 380g": {
                "base_sales": 35, "category": "Pantry", "seasonality": "medium",
                "weekly_pattern": "consistent", "trend": 0.005, "volatility": 0.05, "loyalty_effect": 1.0
            },
            "Kangaroo Steak": {
                "base_sales": 25, "category": "Meat", "seasonality": "high",
                "weekly_pattern": "weekend_boost", "trend": 0.04, "volatility": 0.15, "loyalty_effect": 1.4
            },
            "Tim Tam Slam Kit": {
                "base_sales": 15, "category": "Confectionery", "seasonality": "very_high",
                "weekly_pattern": "weekend_boost", "trend": 0.05, "volatility": 0.20, "loyalty_effect": 1.5
            }
        }
        
        # Seasonal patterns by category (smoother transitions)
        self.seasonal_patterns = {
            "Dairy": {"christmas": 1.1, "easter": 1.05, "summer": 1.15, "winter": 0.95, "back_to_school": 1.1},
            "Bakery": {"christmas": 1.3, "easter": 1.2, "summer": 0.9, "winter": 1.1, "back_to_school": 1.15},
            "Confectionery": {"christmas": 2.5, "easter": 2.0, "summer": 0.8, "winter": 1.2, "back_to_school": 1.1},
            "Pantry": {"christmas": 1.2, "easter": 1.1, "summer": 0.95, "winter": 1.05, "back_to_school": 1.3},
            "Meat": {"christmas": 1.4, "easter": 1.3, "summer": 1.2, "winter": 0.9, "back_to_school": 1.05}
        }
        
        # Holiday periods (Australian context)
        self.holidays = {
            "christmas": {"start": "2023-12-15", "end": "2023-12-31", "peak": "2023-12-24"},
            "easter": {"start": "2024-03-28", "end": "2024-04-01", "peak": "2024-03-31"},
            "back_to_school": {"start": "2024-01-20", "end": "2024-02-10", "peak": "2024-01-30"}
        }
    
    def generate_time_series_data(
        self,
        products: List[Dict[str, Any]],
        start_date: str = "2023-01-01",
        end_date: str = "2025-06-30",
        freq: str = "D",
        include_stores: bool = True,
        add_time_features: bool = True,
        add_lag_features: bool = False
    ) -> pd.DataFrame:
        """Generate realistic time series sales data for each product and store.
        
        Args:
            products: List of product dictionaries
            start_date: Start date for data generation
            end_date: End date for data generation
            freq: Frequency of data ('D' for daily)
            include_stores: Whether to include multiple stores
            add_time_features: Whether to add time-based features for modeling
            add_lag_features: Whether to add lag features for autoregressive models
        """
        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
        all_rows = []
        
        loyalty_multipliers = {"Core": 1.0, "Premium": 1.3, "Value": 0.8}
        
        for product in products:
            product_name = product["PRODUCT_NAME"]
            category = product["CATEGORY_NAME"]
            loyalty_group = product["LOYALTY_GROUP"]
            
            # Get product profile or create default
            profile = self.product_profiles.get(product_name, {
                "base_sales": 50, "category": category, "seasonality": "medium",
                "weekly_pattern": "consistent", "trend": 0.02, "volatility": 0.10, "loyalty_effect": 1.0
            })
            
            # Adjust base sales by loyalty group
            base_sales = profile["base_sales"] * loyalty_multipliers.get(loyalty_group, 1.0)
            
            # Generate data for each store
            stores_to_use = list(self.stores.keys()) if include_stores else ["STORE001"]
            
            for store_id in stores_to_use:
                store_config = self.stores[store_id]
                
                # Adjust base sales by store characteristics
                store_base_sales = base_sales * store_config["traffic_multiplier"]
                
                for i, date in enumerate(date_range):
                    sales = self._calculate_daily_sales(
                        store_base_sales, profile, category, date, i, len(date_range), store_config
                    )
                    
                    row = {
                        "SELL_ID": product["SELL_ID"],
                        "STORE_ID": store_id,
                        "STORE_NAME": store_config["name"],
                        "STORE_LOCATION": store_config["location"],
                        "STORE_SIZE": store_config["size"],
                        "DATE": date,
                        "SALES": sales,
                        **product,
                    }
                    all_rows.append(row)
        
        df = pd.DataFrame(all_rows)
        
        # Add time features for modeling
        if add_time_features:
            df = self._add_time_features(df)
        
        # Add lag features for autoregressive models
        if add_lag_features:
            df = self._add_lag_features(df)
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features for time series modeling."""
        df = df.copy()
        
        # Ensure DATE is datetime
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Basic time features
        df['YEAR'] = df['DATE'].dt.year
        df['MONTH'] = df['DATE'].dt.month
        df['DAY'] = df['DATE'].dt.day
        df['DAY_OF_WEEK'] = df['DATE'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['DAY_OF_YEAR'] = df['DATE'].dt.dayofyear
        df['WEEK_OF_YEAR'] = df['DATE'].dt.isocalendar().week
        df['QUARTER'] = df['DATE'].dt.quarter
        
        # Cyclical encoding for periodic features
        df['DAY_OF_WEEK_SIN'] = np.sin(2 * np.pi * df['DAY_OF_WEEK'] / 7)
        df['DAY_OF_WEEK_COS'] = np.cos(2 * np.pi * df['DAY_OF_WEEK'] / 7)
        df['MONTH_SIN'] = np.sin(2 * np.pi * df['MONTH'] / 12)
        df['MONTH_COS'] = np.cos(2 * np.pi * df['MONTH'] / 12)
        df['DAY_OF_YEAR_SIN'] = np.sin(2 * np.pi * df['DAY_OF_YEAR'] / 365.25)
        df['DAY_OF_YEAR_COS'] = np.cos(2 * np.pi * df['DAY_OF_YEAR'] / 365.25)
        
        # Weekend indicator
        df['IS_WEEKEND'] = (df['DAY_OF_WEEK'] >= 5).astype(int)
        
        # Month end/beginning indicators
        df['IS_MONTH_START'] = df['DATE'].dt.is_month_start.astype(int)
        df['IS_MONTH_END'] = df['DATE'].dt.is_month_end.astype(int)
        
        # Quarter end/beginning indicators
        df['IS_QUARTER_START'] = df['DATE'].dt.is_quarter_start.astype(int)
        df['IS_QUARTER_END'] = df['DATE'].dt.is_quarter_end.astype(int)
        
        # Holiday indicators
        df['IS_HOLIDAY'] = self._get_holiday_indicator(df['DATE'])
        
        # Store-specific features
        df['STORE_SIZE_LARGE'] = (df['STORE_SIZE'] == 'large').astype(int)
        df['STORE_SIZE_MEDIUM'] = (df['STORE_SIZE'] == 'medium').astype(int)
        df['STORE_SIZE_SMALL'] = (df['STORE_SIZE'] == 'small').astype(int)
        
        # Product category features
        df['CATEGORY_DAIRY'] = (df['CATEGORY_NAME'] == 'Dairy').astype(int)
        df['CATEGORY_BAKERY'] = (df['CATEGORY_NAME'] == 'Bakery').astype(int)
        df['CATEGORY_CONFECTIONERY'] = (df['CATEGORY_NAME'] == 'Confectionery').astype(int)
        df['CATEGORY_PANTRY'] = (df['CATEGORY_NAME'] == 'Pantry').astype(int)
        df['CATEGORY_MEAT'] = (df['CATEGORY_NAME'] == 'Meat').astype(int)
        
        # Loyalty group features
        df['LOYALTY_PREMIUM'] = (df['LOYALTY_GROUP'] == 'Premium').astype(int)
        df['LOYALTY_CORE'] = (df['LOYALTY_GROUP'] == 'Core').astype(int)
        df['LOYALTY_VALUE'] = (df['LOYALTY_GROUP'] == 'Value').astype(int)
        
        # Shelf space features
        df['SHELF_SPACE_SMALL'] = (df['SHELF_SPACE_CM'] <= 10.0).astype(int)
        df['SHELF_SPACE_MEDIUM'] = ((df['SHELF_SPACE_CM'] > 10.0) & (df['SHELF_SPACE_CM'] <= 15.0)).astype(int)
        df['SHELF_SPACE_LARGE'] = (df['SHELF_SPACE_CM'] > 15.0).astype(int)
        
        # Shelf space efficiency metrics
        df['SALES_PER_CM'] = df['SALES'] / df['SHELF_SPACE_CM']  # Sales per cm of shelf space
        df['SPACE_EFFICIENCY'] = df['SALES'] / (df['SHELF_SPACE_CM'] * 100)  # Normalized efficiency
        
        # Shelf space utilization (assuming standard shelf depth and height)
        # Standard shelf depth: 30cm, height: 40cm
        shelf_depth = 30.0
        shelf_height = 40.0
        df['SHELF_VOLUME_CM3'] = df['SHELF_SPACE_CM'] * shelf_depth * shelf_height
        df['VOLUME_UTILIZATION'] = df['SHELF_SPACE_CM'] / (shelf_depth * shelf_height) * 100
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame, lags: List[int] = [1, 7, 14, 30]) -> pd.DataFrame:
        """Add lag features for autoregressive models."""
        df = df.copy()
        
        # Sort by product, store, and date
        df = df.sort_values(['SELL_ID', 'STORE_ID', 'DATE'])
        
        # Add lag features for each product-store combination
        for lag in lags:
            df[f'SALES_LAG_{lag}'] = df.groupby(['SELL_ID', 'STORE_ID'])['SALES'].shift(lag)
        
        # Add rolling statistics
        for window in [7, 14, 30]:
            df[f'SALES_MEAN_{window}'] = df.groupby(['SELL_ID', 'STORE_ID'])['SALES'].rolling(window=window, min_periods=1).mean().reset_index(0, drop=True)
            df[f'SALES_STD_{window}'] = df.groupby(['SELL_ID', 'STORE_ID'])['SALES'].rolling(window=window, min_periods=1).std().reset_index(0, drop=True)
            df[f'SALES_MIN_{window}'] = df.groupby(['SELL_ID', 'STORE_ID'])['SALES'].rolling(window=window, min_periods=1).min().reset_index(0, drop=True)
            df[f'SALES_MAX_{window}'] = df.groupby(['SELL_ID', 'STORE_ID'])['SALES'].rolling(window=window, min_periods=1).max().reset_index(0, drop=True)
        
        return df
    
    def _get_holiday_indicator(self, dates: pd.Series) -> pd.Series:
        """Create holiday indicator for time series modeling."""
        holiday_indicator = pd.Series(0, index=dates.index)
        
        for holiday, period in self.holidays.items():
            holiday_start = pd.to_datetime(period["start"])
            holiday_end = pd.to_datetime(period["end"])
            mask = (dates >= holiday_start) & (dates <= holiday_end)
            holiday_indicator[mask] = 1
        
        return holiday_indicator
    
    def _calculate_daily_sales(
        self,
        base_sales: float,
        profile: Dict[str, Any],
        category: str,
        date: pd.Timestamp,
        day_index: int,
        total_days: int,
        store_config: Dict[str, Any]
    ) -> float:
        """Calculate daily sales with realistic patterns and seasonality."""
        
        # Base sales with trend
        trend_factor = 1 + (profile["trend"] * day_index / 365)  # Annual trend
        sales = base_sales * trend_factor
        
        # Weekly pattern
        day_of_week = date.dayofweek  # 0=Monday, 6=Sunday
        weekly_pattern = profile["weekly_pattern"]
        
        if weekly_pattern == "weekend_boost":
            if day_of_week >= 5:  # Weekend
                sales *= 1.3
            elif day_of_week == 4:  # Friday
                sales *= 1.1
        elif weekly_pattern == "business_district":
            if day_of_week < 5:  # Weekday
                sales *= 1.2
            else:  # Weekend
                sales *= 0.7
        elif weekly_pattern == "shopping_district":
            if day_of_week >= 5:  # Weekend
                sales *= 1.4
            elif day_of_week == 4:  # Friday
                sales *= 1.2
        elif weekly_pattern == "suburban":
            if day_of_week >= 5:  # Weekend
                sales *= 1.2
            elif day_of_week == 0:  # Monday
                sales *= 0.9
        
        # Seasonal patterns
        month = date.month
        seasonality = profile["seasonality"]
        
        if seasonality == "high" or seasonality == "very_high":
            # Summer (Dec-Feb in Australia)
            if month in [12, 1, 2]:
                if category == "Confectionery":
                    sales *= 0.8  # Less chocolate in summer
                elif category == "Dairy":
                    sales *= 1.15  # More dairy in summer
            # Winter (Jun-Aug)
            elif month in [6, 7, 8]:
                if category == "Confectionery":
                    sales *= 1.2  # More chocolate in winter
                elif category == "Dairy":
                    sales *= 0.95
            # Spring (Sep-Nov)
            elif month in [9, 10, 11]:
                if category == "Bakery":
                    sales *= 1.1  # Spring baking
            # Autumn (Mar-May)
            elif month in [3, 4, 5]:
                if category == "Pantry":
                    sales *= 1.05  # Comfort food
        
        # Holiday effects
        holiday_multiplier = 1.0
        for holiday, period in self.holidays.items():
            holiday_start = pd.to_datetime(period["start"])
            holiday_end = pd.to_datetime(period["end"])
            holiday_peak = pd.to_datetime(period["peak"])
            
            if holiday_start <= date <= holiday_end:
                # Calculate distance from peak
                days_from_peak = abs((date - holiday_peak).days)
                if days_from_peak <= 3:  # Peak period
                    holiday_multiplier = self.seasonal_patterns[category][holiday]
                else:  # Build-up or wind-down
                    holiday_multiplier = 1 + (self.seasonal_patterns[category][holiday] - 1) * 0.5
                break
        
        sales *= holiday_multiplier
        
        # Store-specific adjustments
        if store_config["weekly_pattern"] == "business_district" and day_of_week >= 5:
            sales *= 0.6  # Business district stores have lower weekend sales
        elif store_config["weekly_pattern"] == "shopping_district" and day_of_week < 5:
            sales *= 0.8  # Shopping district stores have lower weekday sales
        
        # Add realistic noise
        volatility = profile["volatility"]
        noise = self.rng.normal(0, volatility)
        sales *= (1 + noise)
        
        # Ensure non-negative sales
        sales = max(0, sales)
        
        # Round to realistic whole numbers
        sales = round(sales)
        
        return sales
    
    def prepare_for_modeling(
        self,
        df: pd.DataFrame,
        target_column: str = 'SALES',
        group_columns: List[str] = ['SELL_ID', 'STORE_ID'],
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        validation_size: float = 0.1
    ) -> Dict[str, Any]:
        """Prepare data for time series modeling with proper train/validation/test splits.
        
        Args:
            df: Input DataFrame with sales data
            target_column: Column to predict
            group_columns: Columns to group by for time series splits
            feature_columns: Columns to use as features (if None, auto-detect)
            test_size: Proportion of data for testing
            validation_size: Proportion of data for validation
            
        Returns:
            Dictionary with train, validation, and test datasets
        """
        df = df.copy()
        
        # Auto-detect feature columns if not provided
        if feature_columns is None:
            exclude_cols = ['DATE', 'SALES', 'SELL_ID', 'STORE_ID', 'STORE_NAME', 'STORE_LOCATION', 
                           'PRODUCT_NAME', 'CATEGORY_NAME', 'SUBCATEGORY_NAME', 'ITEM_CLASS_NAME',
                           'SUPPLIER', 'BRAND', 'PACK_SIZE', 'ORIGIN']
            feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        # Ensure data is sorted by time
        df = df.sort_values(group_columns + ['DATE'])
        
        # Create time series splits
        splits = self._create_time_series_splits(
            df, group_columns, test_size, validation_size
        )
        
        # Prepare datasets
        datasets = {}
        for split_name, split_indices in splits.items():
            split_df = df.iloc[split_indices].copy()
            
            # Prepare features and target
            X = split_df[feature_columns].copy()
            y = split_df[target_column].copy()
            
            # Handle missing values
            X = self._handle_missing_values(X)
            
            datasets[split_name] = {
                'X': X,
                'y': y,
                'metadata': {
                    'group_columns': group_columns,
                    'feature_columns': feature_columns,
                    'target_column': target_column,
                    'n_samples': len(split_df),
                    'date_range': (split_df['DATE'].min(), split_df['DATE'].max())
                }
            }
        
        return datasets
    
    def _create_time_series_splits(
        self,
        df: pd.DataFrame,
        group_columns: List[str],
        test_size: float,
        validation_size: float
    ) -> Dict[str, List[int]]:
        """Create time series splits ensuring no data leakage."""
        splits = {'train': [], 'validation': [], 'test': []}
        
        # Group by product-store combinations
        for name, group in df.groupby(group_columns):
            group_indices = group.index.tolist()
            n_samples = len(group_indices)
            
            # Calculate split points
            test_start = int(n_samples * (1 - test_size))
            val_start = int(n_samples * (1 - test_size - validation_size))
            
            # Assign indices to splits
            splits['train'].extend(group_indices[:val_start])
            splits['validation'].extend(group_indices[val_start:test_start])
            splits['test'].extend(group_indices[test_start:])
        
        return splits
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in feature matrix."""
        X = X.copy()
        
        # Fill numeric columns with forward fill, then backward fill, then 0
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if X[col].isnull().any():
                X[col] = X[col].fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        # Fill categorical columns with mode
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            if X[col].isnull().any():
                mode_val = X[col].mode()[0] if len(X[col].mode()) > 0 else 'Unknown'
                X[col] = X[col].fillna(mode_val)
        
        return X
    
    def get_modeling_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for modeling assessment."""
        summary = {
            'data_info': {
                'total_records': len(df),
                'unique_products': df['SELL_ID'].nunique(),
                'unique_stores': df['STORE_ID'].nunique(),
                'date_range': (df['DATE'].min(), df['DATE'].max()),
                'total_days': (df['DATE'].max() - df['DATE'].min()).days
            },
            'sales_stats': {
                'mean': df['SALES'].mean(),
                'std': df['SALES'].std(),
                'min': df['SALES'].min(),
                'max': df['SALES'].max(),
                'median': df['SALES'].median(),
                'zero_sales_pct': (df['SALES'] == 0).mean() * 100
            },
            'time_series_quality': {
                'missing_dates': self._check_missing_dates(df),
                'duplicate_records': df.duplicated().sum(),
                'consistent_frequency': self._check_consistent_frequency(df)
            },
            'feature_availability': {
                'time_features': [col for col in df.columns if any(x in col.lower() for x in ['year', 'month', 'day', 'week', 'quarter'])],
                'lag_features': [col for col in df.columns if 'lag' in col.lower()],
                'rolling_features': [col for col in df.columns if any(x in col.lower() for x in ['mean', 'std', 'min', 'max']) and 'lag' not in col.lower()]
            }
        }
        
        return summary
    
    def _check_missing_dates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing dates in the time series."""
        df = df.copy()
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Expected date range
        date_range = pd.date_range(df['DATE'].min(), df['DATE'].max(), freq='D')
        
        # Check each product-store combination
        missing_info = {}
        for name, group in df.groupby(['SELL_ID', 'STORE_ID']):
            group_dates = set(group['DATE'].dt.date)
            expected_dates = set(date_range.date)
            missing_dates = expected_dates - group_dates
            
            if missing_dates:
                missing_info[f"{name[0]}_{name[1]}"] = {
                    'missing_count': len(missing_dates),
                    'missing_pct': len(missing_dates) / len(expected_dates) * 100
                }
        
        return missing_info
    
    def _check_consistent_frequency(self, df: pd.DataFrame) -> bool:
        """Check if data has consistent daily frequency."""
        df = df.copy()
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Check if all product-store combinations have the same number of records
        record_counts = df.groupby(['SELL_ID', 'STORE_ID']).size()
        return record_counts.std() == 0


class SalesDataManager(UnityCatalogManager):
    """Manages sales data operations with Unity Catalog integration."""
    
    def __init__(self, conn: Optional[Any] = None):
        super().__init__(conn)
        self.generator = SalesDataGenerator()
    
    def write_sales_data(
        self,
        products: List[Dict[str, Any]],
        table_name: str = "product_sales",
        start_date: str = "2023-01-01",
        end_date: str = "2025-06-30",
        overwrite: bool = True,
        include_stores: bool = True,
        add_time_features: bool = True,
        add_lag_features: bool = False
    ) -> Union[int, Tuple[str, int]]:
        """Generate sales data and write it to Unity Catalog."""
        log(f"→ write_sales_data: Starting sales data generation and write")
        
        try:
            df = self.generator.generate_time_series_data(
                products, start_date, end_date, include_stores=include_stores,
                add_time_features=add_time_features, add_lag_features=add_lag_features
            )
            log(f"→ write_sales_data: Generated {len(df)} sales records")
            
            result = self._write_dataframe(df, table_name, overwrite)
            
            if isinstance(result, int):
                log(f"→ write_sales_data: Successfully wrote {result} rows")
            else:
                log(f"✗ write_sales_data: Failed to write data")
                
            return result
            
        except Exception as e:
            error_msg = f"Failed to write sales data: {str(e)}"
            log(f"✗ write_sales_data: {error_msg}")
            return error_msg, 0
    
    def read_sales_data(
        self,
        table_name: str = "product_sales",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        store_ids: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Read sales data from Unity Catalog with optional filtering."""
        log(f"→ read_sales_data: Reading from {table_name}")
        
        try:
            # Build query with filters
            query_parts = [f"SELECT * FROM {self._get_full_table_name(table_name)}"]
            where_conditions = []
            
            if start_date:
                where_conditions.append(f"DATE >= '{start_date}'")
            if end_date:
                where_conditions.append(f"DATE <= '{end_date}'")
            if product_ids:
                product_ids_str = "', '".join(product_ids)
                where_conditions.append(f"SELL_ID IN ('{product_ids_str}')")
            if store_ids:
                store_ids_str = "', '".join(store_ids)
                where_conditions.append(f"STORE_ID IN ('{store_ids_str}')")
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            if limit:
                query_parts.append(f"LIMIT {limit}")
            
            query = " ".join(query_parts)
            log(f"→ read_sales_data: Query: {query}")
            
            df = self._read_dataframe(table_name, query)
            log(f"→ read_sales_data: Retrieved {len(df)} rows")
            return df
            
        except Exception as e:
            error_msg = f"Failed to read sales data: {str(e)}"
            log(f"✗ read_sales_data: {error_msg}")
            raise
    
    def get_sales_summary(
        self,
        table_name: str = "product_sales",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by_store: bool = False
    ) -> pd.DataFrame:
        """Get sales summary with aggregations."""
        log(f"→ get_sales_summary: Generating summary for {table_name}")
        
        try:
            # Build query with optional store grouping
            if group_by_store:
                group_by_clause = "SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP, STORE_ID, STORE_NAME, DATE_TRUNC('month', DATE)"
                select_clause = """
                    SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP, 
                    STORE_ID, STORE_NAME, DATE_TRUNC('month', DATE) as MONTH,
                    SUM(SALES) as TOTAL_SALES, AVG(SALES) as AVG_DAILY_SALES,
                    COUNT(*) as DAYS_WITH_SALES, MIN(SALES) as MIN_DAILY_SALES,
                    MAX(SALES) as MAX_DAILY_SALES
                """
            else:
                group_by_clause = "SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP, DATE_TRUNC('month', DATE)"
                select_clause = """
                    SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP,
                    DATE_TRUNC('month', DATE) as MONTH,
                    SUM(SALES) as TOTAL_SALES, AVG(SALES) as AVG_DAILY_SALES,
                    COUNT(*) as DAYS_WITH_SALES, MIN(SALES) as MIN_DAILY_SALES,
                    MAX(SALES) as MAX_DAILY_SALES
                """
            
            query_parts = [f"SELECT {select_clause} FROM " + self._get_full_table_name(table_name)]
            
            where_conditions = []
            if start_date:
                where_conditions.append(f"DATE >= '{start_date}'")
            if end_date:
                where_conditions.append(f"DATE <= '{end_date}'")
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            query_parts.append(f"""
                GROUP BY {group_by_clause}
                ORDER BY SELL_ID, MONTH
            """)
            
            query = " ".join(query_parts)
            log(f"→ get_sales_summary: Query: {query}")
            
            df = self._read_dataframe(table_name, query)
            log(f"→ get_sales_summary: Retrieved {len(df)} summary rows")
            return df
            
        except Exception as e:
            error_msg = f"Failed to get sales summary: {str(e)}"
            log(f"✗ get_sales_summary: {error_msg}")
            raise
    
    def initialize_tables(self, products: List[Dict[str, Any]], include_stores: bool = True) -> Dict[str, Union[int, Tuple[str, int]]]:
        """Initialize both product and sales tables."""
        log(f"→ initialize_tables: Initializing product and sales tables")
        
        try:
            results = {}
            
            # Initialize products table
            from .sample_product_data import INITIAL_DATA
            products_df = pd.DataFrame(INITIAL_DATA)
            results["products"] = self._write_dataframe(products_df, "products", overwrite=True)
            
            # Initialize sales table
            results["sales"] = self.write_sales_data(
                products, "product_sales", overwrite=True, include_stores=include_stores
            )
            
            log(f"→ initialize_tables: Initialization complete")
            return results
            
        except Exception as e:
            error_msg = f"Failed to initialize tables: {str(e)}"
            log(f"✗ initialize_tables: {error_msg}")
            raise
    
    def check_table_exists(self, table_name: str = "product_sales") -> bool:
        """Check if sales table exists."""
        return self._check_table_exists(table_name)
    
    def prepare_modeling_data(
        self,
        table_name: str = "product_sales",
        target_column: str = 'SALES',
        group_columns: List[str] = ['SELL_ID', 'STORE_ID'],
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        store_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Prepare data for time series modeling with proper splits."""
        log(f"→ prepare_modeling_data: Preparing data for modeling")
        
        try:
            # Read data from Unity Catalog
            df = self.read_sales_data(
                table_name=table_name,
                start_date=start_date,
                end_date=end_date,
                product_ids=product_ids,
                store_ids=store_ids
            )
            
            # Prepare datasets using the generator
            datasets = self.generator.prepare_for_modeling(
                df, target_column, group_columns, feature_columns, test_size, validation_size
            )
            
            log(f"→ prepare_modeling_data: Prepared {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            error_msg = f"Failed to prepare modeling data: {str(e)}"
            log(f"✗ prepare_modeling_data: {error_msg}")
            raise
    
    def get_modeling_summary(
        self,
        table_name: str = "product_sales",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        store_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive summary for modeling assessment."""
        log(f"→ get_modeling_summary: Generating modeling summary")
        
        try:
            # Read data from Unity Catalog
            df = self.read_sales_data(
                table_name=table_name,
                start_date=start_date,
                end_date=end_date,
                product_ids=product_ids,
                store_ids=store_ids
            )
            
            # Get summary using the generator
            summary = self.generator.get_modeling_summary(df)
            
            log(f"→ get_modeling_summary: Generated summary")
            return summary
            
        except Exception as e:
            error_msg = f"Failed to get modeling summary: {str(e)}"
            log(f"✗ get_modeling_summary: {error_msg}")
            raise
    
    def export_modeling_data(
        self,
        table_name: str = "product_sales",
        export_path: str = "modeling_data",
        target_column: str = 'SALES',
        group_columns: List[str] = ['SELL_ID', 'STORE_ID'],
        test_size: float = 0.2,
        validation_size: float = 0.1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        store_ids: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Export model-ready datasets to files."""
        log(f"→ export_modeling_data: Exporting modeling data to {export_path}")
        
        try:
            import os
            
            # Create export directory
            os.makedirs(export_path, exist_ok=True)
            
            # Prepare datasets
            datasets = self.prepare_modeling_data(
                table_name=table_name,
                target_column=target_column,
                group_columns=group_columns,
                test_size=test_size,
                validation_size=validation_size,
                start_date=start_date,
                end_date=end_date,
                product_ids=product_ids,
                store_ids=store_ids
            )
            
            # Export each dataset
            exported_files = {}
            for split_name, dataset in datasets.items():
                # Combine features and target
                combined_df = dataset['X'].copy()
                combined_df[dataset['metadata']['target_column']] = dataset['y']
                
                # Save to CSV
                filename = f"{export_path}/{split_name}_data.csv"
                combined_df.to_csv(filename, index=False)
                exported_files[split_name] = filename
                
                log(f"→ export_modeling_data: Exported {split_name} data to {filename}")
            
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
            metadata_file = f"{export_path}/dataset_metadata.csv"
            metadata_df.to_csv(metadata_file, index=False)
            exported_files['metadata'] = metadata_file
            
            log(f"→ export_modeling_data: Exported metadata to {metadata_file}")
            return exported_files
            
        except Exception as e:
            error_msg = f"Failed to export modeling data: {str(e)}"
            log(f"✗ export_modeling_data: {error_msg}")
            raise


# Convenience functions for backward compatibility
def generate_time_series_data(products, start_date="2023-01-01", end_date="2025-06-30", freq="D", include_stores=True):
    """Generate realistic time series sales data."""
    generator = SalesDataGenerator()
    return generator.generate_time_series_data(products, start_date, end_date, freq, include_stores)

def write_sales_data_to_unity_catalog(products, table_name="product_sales", start_date="2023-01-01", 
                                     end_date="2025-06-30", overwrite=True, conn=None, include_stores=True):
    """Write sales data to Unity Catalog."""
    manager = SalesDataManager(conn)
    return manager.write_sales_data(products, table_name, start_date, end_date, overwrite, include_stores)

def read_sales_data_from_unity_catalog(table_name="product_sales", start_date=None, end_date=None, 
                                      product_ids=None, store_ids=None, limit=None, conn=None):
    """Read sales data from Unity Catalog."""
    manager = SalesDataManager(conn)
    return manager.read_sales_data(table_name, start_date, end_date, product_ids, store_ids, limit)

def get_sales_summary_from_unity_catalog(table_name="product_sales", start_date=None, end_date=None, 
                                        group_by_store=False, conn=None):
    """Get sales summary from Unity Catalog."""
    manager = SalesDataManager(conn)
    return manager.get_sales_summary(table_name, start_date, end_date, group_by_store)

def initialize_sales_tables(products, conn=None, include_stores=True):
    """Initialize sales tables."""
    manager = SalesDataManager(conn)
    return manager.initialize_tables(products, include_stores)

def check_sales_table_exists(table_name="product_sales", conn=None):
    """Check if sales table exists."""
    manager = SalesDataManager(conn)
    return manager.check_table_exists(table_name)

