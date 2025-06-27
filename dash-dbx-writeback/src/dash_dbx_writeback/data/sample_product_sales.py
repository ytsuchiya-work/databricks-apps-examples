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
    """Handles realistic sales data generation with product-specific patterns."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        
        # Product-specific characteristics
        self.product_profiles = {
            "Coles Brand Milk 2L": {
                "base_sales": 150, "category": "Dairy", "seasonality": "low",
                "weekly_pattern": "weekend_boost", "trend": 0.02, "volatility": 0.15, "loyalty_effect": 1.2
            },
            "Woolworths Bread White": {
                "base_sales": 120, "category": "Bakery", "seasonality": "low",
                "weekly_pattern": "weekend_boost", "trend": 0.01, "volatility": 0.12, "loyalty_effect": 1.1
            },
            "Arnott's Tim Tams": {
                "base_sales": 45, "category": "Confectionery", "seasonality": "high",
                "weekly_pattern": "weekend_boost", "trend": 0.03, "volatility": 0.25, "loyalty_effect": 1.3
            },
            "Vegemite 380g": {
                "base_sales": 35, "category": "Pantry", "seasonality": "medium",
                "weekly_pattern": "consistent", "trend": 0.005, "volatility": 0.10, "loyalty_effect": 1.0
            },
            "Kangaroo Steak": {
                "base_sales": 25, "category": "Meat", "seasonality": "high",
                "weekly_pattern": "weekend_boost", "trend": 0.04, "volatility": 0.30, "loyalty_effect": 1.4
            },
            "Tim Tam Slam Kit": {
                "base_sales": 15, "category": "Confectionery", "seasonality": "very_high",
                "weekly_pattern": "weekend_boost", "trend": 0.05, "volatility": 0.40, "loyalty_effect": 1.5
            }
        }
        
        # Seasonal patterns by category
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
        freq: str = "D"
    ) -> pd.DataFrame:
        """Generate realistic time series sales data for each product."""
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
                "weekly_pattern": "consistent", "trend": 0.02, "volatility": 0.20, "loyalty_effect": 1.0
            })
            
            # Adjust base sales by loyalty group
            base_sales = profile["base_sales"] * loyalty_multipliers.get(loyalty_group, 1.0)
            
            for i, date in enumerate(date_range):
                sales = self._calculate_daily_sales(base_sales, profile, category, date, i, len(date_range))
                
                row = {
                    "SELL_ID": product["SELL_ID"],
                    "DATE": date,
                    "SALES": sales,
                    **product,
                }
                all_rows.append(row)
        
        return pd.DataFrame(all_rows)
    
    def _calculate_daily_sales(self, base_sales: float, profile: Dict, category: str, date: datetime, day_index: int, total_days: int) -> int:
        """Calculate sales for a specific day with all effects applied."""
        sales = base_sales
        
        # Add linear trend
        trend_factor = 1 + profile["trend"] * (day_index / total_days)
        sales *= trend_factor
        
        # Add weekly pattern
        sales *= self._get_weekly_multiplier(profile["weekly_pattern"], date)
        
        # Add seasonal effects
        sales *= self._get_seasonal_multiplier(category, date)
        
        # Add holiday effects
        sales *= self._get_holiday_multiplier(category, date)
        
        # Add random noise/variability
        noise = self.rng.normal(0, profile["volatility"])
        sales *= (1 + noise)
        
        return max(0, int(sales))
    
    def _get_weekly_multiplier(self, weekly_pattern: str, date: datetime) -> float:
        """Get weekly pattern multiplier."""
        day_of_week = date.weekday()
        if weekly_pattern == "weekend_boost":
            if day_of_week >= 5:  # Weekend
                return 1.3
            elif day_of_week == 4:  # Friday
                return 1.1
        return 1.0
    
    def _get_seasonal_multiplier(self, category: str, date: datetime) -> float:
        """Get seasonal multiplier."""
        month = date.month
        seasonal_pattern = self.seasonal_patterns.get(category, {})
        
        if month in [12, 1, 2]:  # Summer (Dec-Feb in Australia)
            return seasonal_pattern.get("summer", 1.0)
        elif month in [6, 7, 8]:  # Winter (Jun-Aug)
            return seasonal_pattern.get("winter", 1.0)
        return 1.0
    
    def _get_holiday_multiplier(self, category: str, date: datetime) -> float:
        """Get holiday multiplier."""
        seasonal_pattern = self.seasonal_patterns.get(category, {})
        multiplier = 1.0
        
        for holiday, period in self.holidays.items():
            holiday_start = datetime.strptime(period["start"], "%Y-%m-%d")
            holiday_end = datetime.strptime(period["end"], "%Y-%m-%d")
            holiday_peak = datetime.strptime(period["peak"], "%Y-%m-%d")
            
            if holiday_start <= date <= holiday_end:
                days_from_peak = abs((date - holiday_peak).days)
                holiday_intensity = max(0.1, 1 - (days_from_peak / 7) ** 2)
                holiday_mult = seasonal_pattern.get(holiday, 1.0)
                multiplier *= (1 + (holiday_mult - 1) * holiday_intensity)
        
        return multiplier


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
        overwrite: bool = True
    ) -> Union[int, Tuple[str, int]]:
        """Generate sales data and write it to Unity Catalog."""
        log(f"→ write_sales_data: Starting sales data generation and write")
        
        try:
            df = self.generator.generate_time_series_data(products, start_date, end_date)
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
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Get sales summary with aggregations."""
        log(f"→ get_sales_summary: Generating summary for {table_name}")
        
        try:
            query_parts = ["""
                SELECT 
                    SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP,
                    DATE_TRUNC('month', DATE) as MONTH,
                    SUM(SALES) as TOTAL_SALES, AVG(SALES) as AVG_DAILY_SALES,
                    COUNT(*) as DAYS_WITH_SALES, MIN(SALES) as MIN_DAILY_SALES,
                    MAX(SALES) as MAX_DAILY_SALES
                FROM """ + self._get_full_table_name(table_name)]
            
            where_conditions = []
            if start_date:
                where_conditions.append(f"DATE >= '{start_date}'")
            if end_date:
                where_conditions.append(f"DATE <= '{end_date}'")
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            query_parts.append("""
                GROUP BY SELL_ID, PRODUCT_NAME, CATEGORY_NAME, BRAND, LOYALTY_GROUP, DATE_TRUNC('month', DATE)
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
    
    def initialize_tables(self, products: List[Dict[str, Any]]) -> Dict[str, Union[int, Tuple[str, int]]]:
        """Initialize both product and sales tables."""
        log(f"→ initialize_tables: Initializing product and sales tables")
        
        try:
            results = {}
            
            # Initialize products table
            from .sample_product_data import INITIAL_DATA
            products_df = pd.DataFrame(INITIAL_DATA)
            results["products"] = self._write_dataframe(products_df, "products", overwrite=True)
            
            # Initialize sales table
            results["sales"] = self.write_sales_data(products, "product_sales", overwrite=True)
            
            log(f"→ initialize_tables: Initialization complete")
            return results
            
        except Exception as e:
            error_msg = f"Failed to initialize tables: {str(e)}"
            log(f"✗ initialize_tables: {error_msg}")
            raise
    
    def check_table_exists(self, table_name: str = "product_sales") -> bool:
        """Check if sales table exists."""
        return self._check_table_exists(table_name)

