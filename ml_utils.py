import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import statsmodels.api as sm
import math

def detect_outliers_isolation_forest(df, contamination=0.05):
    """
    Detect outliers using Isolation Forest algorithm.
    
    Args:
        df (DataFrame): Input DataFrame with features
        contamination (float): Expected proportion of outliers in the data
        
    Returns:
        list: Indices of outliers
    """
    # Initialize and fit the Isolation Forest model
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    predictions = iso_forest.fit_predict(df)
    
    # -1 represents outliers in Isolation Forest
    outlier_indices = np.where(predictions == -1)[0]
    
    return outlier_indices.tolist()

def train_and_evaluate_model(df, target_col, feature_cols, model_type='Linear Regression', test_size=0.2):
    """
    Train and evaluate a regression model.
    
    Args:
        df (DataFrame): Input DataFrame
        target_col (str): Target column name
        feature_cols (list): List of feature column names
        model_type (str): Type of model to train
        test_size (float): Proportion of data to use for testing
        
    Returns:
        dict: Dictionary containing model evaluation results
    """
    # Prepare features and target
    X = df[feature_cols]
    y = df[target_col]
    
    # Handle missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Train model based on the selected type
    if model_type == 'Linear Regression':
        model = LinearRegression()
    elif model_type == 'Random Forest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    elif model_type == 'Gradient Boosting':
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Fit the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate evaluation metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    
    # Get feature importance
    if model_type in ['Random Forest', 'Gradient Boosting']:
        importance = model.feature_importances_
    elif model_type == 'Linear Regression':
        importance = np.abs(model.coef_)
    
    # Create results dictionary
    results = {
        'model_type': model_type,
        'r2_score': r2,
        'mae': mae,
        'rmse': rmse,
        'feature_importance': importance,
        'y_test': y_test,
        'y_pred': y_pred
    }
    
    return results

def perform_clustering(df, columns, n_clusters=3, pca_components=None):
    """
    Perform K-means clustering on selected columns.
    
    Args:
        df (DataFrame): Input DataFrame
        columns (list): List of columns to use for clustering
        n_clusters (int): Number of clusters
        pca_components (int, optional): Number of PCA components to use
        
    Returns:
        dict: Dictionary containing clustering results
    """
    # Prepare data
    X = df[columns].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Optionally perform PCA
    if pca_components is not None and pca_components < len(columns):
        pca = PCA(n_components=pca_components)
        X_transformed = pca.fit_transform(X_scaled)
        explained_variance = pca.explained_variance_ratio_
    else:
        X_transformed = X_scaled
        explained_variance = None
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_transformed)
    
    # Calculate cluster centers (in original feature space)
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    
    # Calculate sizes of each cluster
    cluster_sizes = np.bincount(clusters)
    
    # Calculate the inertia (within-cluster sum of squares)
    inertia = kmeans.inertia_
    
    # Create results dictionary
    results = {
        'clusters': clusters,
        'cluster_centers': cluster_centers,
        'cluster_sizes': cluster_sizes,
        'inertia': inertia,
        'explained_variance': explained_variance
    }
    
    return results

def analyze_trend(time_series):
    """
    Analyze the trend in a time series.
    
    Args:
        time_series (Series): Time series data
        
    Returns:
        dict: Dictionary containing trend analysis results
    """
    # Calculate a simple trend line (linear regression)
    x = np.arange(len(time_series))
    y = time_series.values
    
    # Handle NaN values
    mask = ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    
    # Fit linear regression
    if len(y) > 1:
        slope, intercept = np.polyfit(x, y, 1)
    else:
        slope, intercept = 0, 0
    
    # Calculate trend direction
    if slope > 0.01:
        direction = "Increasing"
    elif slope < -0.01:
        direction = "Decreasing"
    else:
        direction = "Stable"
    
    # Calculate trend strength (correlation coefficient)
    if len(y) > 1:
        correlation = np.corrcoef(x, y)[0, 1]
    else:
        correlation = 0
    
    # Calculate trend line
    trend_line = intercept + slope * x
    
    # Create results dictionary
    results = {
        'direction': direction,
        'slope': slope,
        'intercept': intercept,
        'strength': correlation,
        'trend_line': trend_line
    }
    
    return results

def perform_seasonal_decomposition(time_series, period=None):
    """
    Perform seasonal decomposition of a time series.
    
    Args:
        time_series (Series): Time series data
        period (int, optional): Period for seasonal decomposition
        
    Returns:
        dict: Dictionary containing decomposition results
    """
    # Estimate period if not provided
    if period is None:
        # Try to infer the frequency from the time series index
        if hasattr(time_series.index, 'freq') and time_series.index.freq is not None:
            freq = time_series.index.freq.name
            if freq in ['M', 'MS']:  # Monthly
                period = 12
            elif freq in ['Q', 'QS']:  # Quarterly
                period = 4
            elif freq in ['D', 'B']:  # Daily or Business
                period = 7
            elif freq in ['W', 'W-SUN', 'W-MON']:  # Weekly
                period = 52
            else:
                # Default periods for common frequencies
                if len(time_series) >= 12:
                    period = min(12, len(time_series) // 2)
                else:
                    period = len(time_series) // 2
        else:
            # If frequency not available, use a reasonable default
            if len(time_series) >= 12:
                period = min(12, len(time_series) // 2)
            else:
                period = len(time_series) // 2
    
    # Ensure period is at least 2
    period = max(2, period)
    
    # Perform decomposition
    decomposition = seasonal_decompose(
        time_series, 
        model='additive', 
        period=period
    )
    
    # Extract components
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid
    
    # Create results dictionary
    results = {
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual,
        'period': period
    }
    
    return results

def calculate_seasonal_strength(decomposition):
    """
    Calculate the strength of seasonality from a decomposition.
    
    Args:
        decomposition (dict): Dictionary containing decomposition results
        
    Returns:
        float: Strength of seasonality (0-1)
    """
    # Extract components
    residual = decomposition['residual']
    seasonal = decomposition['seasonal']
    
    # Calculate variances (ignoring NaN values)
    var_resid = np.nanvar(residual)
    var_seasonal = np.nanvar(seasonal)
    
    # Calculate strength of seasonality
    if var_resid + var_seasonal > 0:
        strength = max(0, 1 - var_resid / (var_resid + var_seasonal))
    else:
        strength = 0
    
    return strength

def generate_forecast(time_series, periods=5):
    """
    Generate a forecast for a time series.
    
    Args:
        time_series (Series): Time series data
        periods (int): Number of periods to forecast
        
    Returns:
        dict: Dictionary containing forecast results
    """
    # Check if time series has enough data points
    if len(time_series) < 4:
        # Simple forecasting (mean-based)
        forecast_index = pd.date_range(
            start=time_series.index[-1], 
            periods=periods+1, 
            freq=time_series.index.inferred_freq
        )[1:]
        
        forecast_values = np.full(periods, time_series.mean())
        forecast = pd.Series(forecast_values, index=forecast_index)
        
        # No confidence intervals for simple method
        return {
            'forecast': forecast
        }
    
    # Try to use exponential smoothing for better forecasts
    try:
        # Determine if the series has seasonality
        if len(time_series) >= 12:
            # Check for annual seasonality
            seasonal_periods = 12
            model = ExponentialSmoothing(
                time_series, 
                seasonal='add', 
                seasonal_periods=seasonal_periods
            )
        else:
            # No seasonality for short series
            model = ExponentialSmoothing(
                time_series, 
                trend='add', 
                seasonal=None
            )
        
        # Fit the model
        fit_model = model.fit()
        
        # Generate forecast
        forecast = fit_model.forecast(periods)
        
        # Create results dictionary (no confidence intervals from ExponentialSmoothing)
        return {
            'forecast': forecast
        }
    
    except Exception:
        # Fallback to ARIMA if exponential smoothing fails
        try:
            # Fit ARIMA model
            model = sm.tsa.ARIMA(time_series, order=(1, 1, 0))
            fit_model = model.fit()
            
            # Generate forecast with confidence intervals
            forecast_results = fit_model.get_forecast(steps=periods)
            forecast = forecast_results.predicted_mean
            
            # Get confidence intervals
            conf_int = forecast_results.conf_int()
            lower_bound = conf_int.iloc[:, 0]
            upper_bound = conf_int.iloc[:, 1]
            
            # Create results dictionary
            return {
                'forecast': forecast,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        except Exception:
            # Worst case: use a simple moving average
            if len(time_series) > 1:
                # Create a date range for the forecast
                if hasattr(time_series.index, 'freq') and time_series.index.freq is not None:
                    freq = time_series.index.freq
                else:
                    # Try to infer frequency
                    freq = pd.infer_freq(time_series.index)
                
                # If frequency couldn't be inferred, use the average difference
                if freq is None:
                    # Average time delta between consecutive observations
                    time_deltas = np.diff(time_series.index)
                    avg_delta = np.mean(time_deltas)
                    freq = pd.Timedelta(avg_delta)
                
                # Create forecast index
                forecast_index = pd.date_range(
                    start=time_series.index[-1], 
                    periods=periods+1, 
                    freq=freq
                )[1:]
                
                # Use the average of last 3 values (or fewer if not available)
                window = min(3, len(time_series))
                forecast_value = time_series.iloc[-window:].mean()
                
                forecast_values = np.full(periods, forecast_value)
                forecast = pd.Series(forecast_values, index=forecast_index)
                
                return {
                    'forecast': forecast
                }
            else:
                # Degenerate case: only one data point
                return {
                    'forecast': pd.Series()
                }
