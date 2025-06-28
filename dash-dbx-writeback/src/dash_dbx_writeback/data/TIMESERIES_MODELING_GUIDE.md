# Time Series Modeling Guide

## Overview

The enhanced `SalesDataGenerator` and `SalesDataManager` classes now provide comprehensive support for time series modeling with realistic sales data. The generated data is optimized for machine learning models with proper time features, data quality, and model-ready datasets.

## Key Features

### 🕒 **Time Features**
- **Basic time features**: Year, month, day, day of week, day of year, week of year, quarter
- **Cyclical encoding**: Sin/cos transformations for periodic features (day of week, month, day of year)
- **Weekend indicators**: Binary flags for weekend vs weekday
- **Month/quarter boundaries**: Indicators for month start/end, quarter start/end
- **Holiday indicators**: Binary flags for holiday periods

### 📈 **Lag Features**
- **Autoregressive features**: Sales lagged by 1, 7, 14, 30 days
- **Customizable lags**: Configurable lag periods for different modeling needs
- **Rolling statistics**: Mean, standard deviation, min, max over 7, 14, 30-day windows

### 🏪 **Store & Product Features**
- **Store characteristics**: Size, location, traffic multipliers
- **Product categories**: One-hot encoded category features
- **Loyalty groups**: Premium, Core, Value indicators
- **Store-specific patterns**: Business district vs shopping district vs suburban

### 📊 **Data Quality**
- **Consistent frequency**: Daily data with no missing dates
- **Missing value handling**: Forward fill, backward fill, and zero imputation
- **Data validation**: Comprehensive quality checks and summaries

## Usage Examples

### Basic Time Series Data Generation

```python
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataGenerator
from src.dash_dbx_writeback.data.sample_product_data import INITIAL_DATA

# Create generator
generator = SalesDataGenerator()

# Generate data with time features
df = generator.generate_time_series_data(
    INITIAL_DATA,
    "2023-01-01",
    "2024-12-31",
    include_stores=True,
    add_time_features=True,
    add_lag_features=True
)
```

### Data Preparation for Modeling

```python
# Prepare datasets with proper time series splits
datasets = generator.prepare_for_modeling(
    df,
    target_column='SALES',
    group_columns=['SELL_ID', 'STORE_ID'],
    test_size=0.2,
    validation_size=0.1
)

# Access train, validation, and test sets
train_data = datasets['train']
X_train = train_data['X']  # Features
y_train = train_data['y']  # Target
```

### Data Quality Assessment

```python
# Get comprehensive modeling summary
summary = generator.get_modeling_summary(df)

print("Data Information:", summary['data_info'])
print("Sales Statistics:", summary['sales_stats'])
print("Time Series Quality:", summary['time_series_quality'])
```

### Unity Catalog Integration

```python
from src.dash_dbx_writeback.data.sample_product_sales import SalesDataManager

# Create manager
manager = SalesDataManager()

# Write data with time features
manager.write_sales_data(
    INITIAL_DATA,
    table_name="product_sales",
    add_time_features=True,
    add_lag_features=True
)

# Prepare modeling data from Unity Catalog
datasets = manager.prepare_modeling_data(
    table_name="product_sales",
    start_date="2023-01-01",
    end_date="2024-12-31"
)

# Export model-ready datasets
exported_files = manager.export_modeling_data(
    table_name="product_sales",
    export_path="modeling_data"
)
```

## Feature Categories

### Time Features
- `YEAR`, `MONTH`, `DAY`, `DAY_OF_WEEK`, `DAY_OF_YEAR`, `WEEK_OF_YEAR`, `QUARTER`
- `DAY_OF_WEEK_SIN`, `DAY_OF_WEEK_COS` (cyclical encoding)
- `MONTH_SIN`, `MONTH_COS` (cyclical encoding)
- `DAY_OF_YEAR_SIN`, `DAY_OF_YEAR_COS` (cyclical encoding)
- `IS_WEEKEND`, `IS_MONTH_START`, `IS_MONTH_END`, `IS_QUARTER_START`, `IS_QUARTER_END`
- `IS_HOLIDAY`

### Lag Features
- `SALES_LAG_1`, `SALES_LAG_7`, `SALES_LAG_14`, `SALES_LAG_30`
- `SALES_MEAN_7`, `SALES_MEAN_14`, `SALES_MEAN_30`
- `SALES_STD_7`, `SALES_STD_14`, `SALES_STD_30`
- `SALES_MIN_7`, `SALES_MIN_14`, `SALES_MIN_30`
- `SALES_MAX_7`, `SALES_MAX_14`, `SALES_MAX_30`

### Store Features
- `STORE_SIZE_LARGE`, `STORE_SIZE_MEDIUM`, `STORE_SIZE_SMALL`

### Category Features
- `CATEGORY_DAIRY`, `CATEGORY_BAKERY`, `CATEGORY_CONFECTIONERY`, `CATEGORY_PANTRY`, `CATEGORY_MEAT`

### Loyalty Features
- `LOYALTY_PREMIUM`, `LOYALTY_CORE`, `LOYALTY_VALUE`

## Modeling Workflow

### 1. Data Generation
```python
# Generate comprehensive time series data
df = generator.generate_time_series_data(
    products,
    start_date="2023-01-01",
    end_date="2024-12-31",
    include_stores=True,
    add_time_features=True,
    add_lag_features=True
)
```

### 2. Data Quality Check
```python
# Assess data quality
summary = generator.get_modeling_summary(df)
if not summary['time_series_quality']['consistent_frequency']:
    print("Warning: Inconsistent data frequency detected")
```

### 3. Data Preparation
```python
# Prepare for modeling with proper splits
datasets = generator.prepare_for_modeling(
    df,
    target_column='SALES',
    group_columns=['SELL_ID', 'STORE_ID'],
    test_size=0.2,
    validation_size=0.1
)
```

### 4. Feature Analysis
```python
# Analyze feature importance
train_data = datasets['train']
correlations = train_data['X'].corrwith(train_data['y']).abs().sort_values(ascending=False)
print("Top features:", correlations.head(10))
```

### 5. Model Training
```python
# Use with any ML framework
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(train_data['X'], train_data['y'])

# Evaluate on validation set
val_data = datasets['validation']
y_pred = model.predict(val_data['X'])
mae = mean_absolute_error(val_data['y'], y_pred)
print(f"Validation MAE: {mae:.2f}")
```

## Best Practices

### 1. **Time Series Splits**
- Always use time-based splits to avoid data leakage
- Keep the most recent data for testing
- Use validation set for hyperparameter tuning

### 2. **Feature Engineering**
- Use cyclical encoding for periodic features
- Include lag features for autoregressive models
- Add rolling statistics for trend capture

### 3. **Data Quality**
- Check for missing dates and inconsistent frequency
- Handle missing values appropriately
- Validate data ranges and distributions

### 4. **Model Selection**
- Consider models that handle time series well (ARIMA, Prophet, LSTM)
- Use ensemble methods for robust predictions
- Include exogenous variables (holidays, events)

### 5. **Evaluation**
- Use time series-specific metrics (MAPE, RMSE, MAE)
- Validate on out-of-sample data
- Consider business metrics (revenue impact, inventory optimization)

## Advanced Usage

### Custom Lag Features
```python
# Add custom lag periods
custom_lags = [1, 3, 7, 14, 30, 90]
df_with_custom_lags = generator._add_lag_features(df, lags=custom_lags)
```

### Store-Specific Modeling
```python
# Model for specific store types
business_stores = ['STORE001']  # Sydney CBD
df_business = df[df['STORE_ID'].isin(business_stores)]
datasets_business = generator.prepare_for_modeling(df_business)
```

### Product Category Modeling
```python
# Model for specific product categories
dairy_products = df[df['CATEGORY_NAME'] == 'Dairy']
datasets_dairy = generator.prepare_for_modeling(dairy_products)
```

## Integration with ML Frameworks

### Scikit-learn
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Train multiple models
models = {
    'RandomForest': RandomForestRegressor(n_estimators=100),
    'LinearRegression': LinearRegression()
}

for name, model in models.items():
    model.fit(train_data['X'], train_data['y'])
    y_pred = model.predict(val_data['X'])
    mae = mean_absolute_error(val_data['y'], y_pred)
    print(f"{name} MAE: {mae:.2f}")
```

### Prophet (Facebook)
```python
from prophet import Prophet

# Prepare data for Prophet
prophet_data = df[['DATE', 'SALES']].rename(columns={'DATE': 'ds', 'SALES': 'y'})
model = Prophet()
model.fit(prophet_data)
```

### TensorFlow/Keras
```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Prepare data for LSTM
def prepare_lstm_data(X, y, time_steps=30):
    X_lstm, y_lstm = [], []
    for i in range(time_steps, len(X)):
        X_lstm.append(X[i-time_steps:i])
        y_lstm.append(y[i])
    return np.array(X_lstm), np.array(y_lstm)

# Create LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(time_steps, n_features)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(1)
])
```

## Troubleshooting

### Common Issues

1. **Missing Time Features**
   - Ensure `add_time_features=True` when generating data
   - Check that DATE column is properly formatted

2. **Data Leakage**
   - Always use time series splits, not random splits
   - Keep future data separate from training data

3. **Memory Issues**
   - Use smaller date ranges for initial testing
   - Consider sampling products/stores for development

4. **Poor Model Performance**
   - Check feature correlations with target
   - Ensure sufficient historical data
   - Consider adding more lag features

### Performance Optimization

1. **Data Generation**
   - Use smaller date ranges for development
   - Generate data in chunks for large datasets

2. **Feature Engineering**
   - Cache computed features
   - Use efficient rolling window calculations

3. **Model Training**
   - Use appropriate model complexity
   - Consider ensemble methods for robustness

## Conclusion

The enhanced sales data generation system provides a comprehensive foundation for time series modeling. With proper time features, lag variables, and data quality assurance, you can build robust forecasting models for retail sales prediction.

Key benefits:
- ✅ **Realistic data patterns** with store and product-specific characteristics
- ✅ **Model-ready features** with proper time series encoding
- ✅ **Data quality assurance** with comprehensive validation
- ✅ **Flexible integration** with Unity Catalog and ML frameworks
- ✅ **Scalable architecture** for large-scale modeling projects 