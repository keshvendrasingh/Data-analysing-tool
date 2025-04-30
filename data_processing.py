import pandas as pd
import numpy as np
from scipy import stats
import re

def fill_missing_with_mean_mode(df):
    """
    Fill missing values with mean for numeric columns and mode for categorical columns.
    
    Args:
        df (DataFrame): Input DataFrame with missing values
        
    Returns:
        DataFrame: DataFrame with missing values filled
    """
    df_filled = df.copy()
    
    # For numeric columns, fill with mean
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        df_filled[col] = df_filled[col].fillna(df[col].mean())
    
    # For non-numeric columns, fill with mode
    categorical_cols = df.select_dtypes(exclude=np.number).columns
    for col in categorical_cols:
        if not df[col].empty:
            mode_value = df[col].mode()
            if not mode_value.empty:
                df_filled[col] = df_filled[col].fillna(mode_value[0])
    
    return df_filled

def detect_outliers_zscore(series, threshold=3):
    """
    Detect outliers in a series using Z-score method.
    
    Args:
        series (Series): Input series
        threshold (float): Z-score threshold (default: 3)
        
    Returns:
        list: Indices of outliers
    """
    # Calculate z-scores
    z_scores = np.abs(stats.zscore(series.dropna()))
    
    # Find outliers
    outliers = np.where(z_scores > threshold)[0]
    
    # Map back to original indices
    original_indices = series.dropna().index[outliers]
    
    return original_indices.tolist()

def detect_outliers_iqr(series, factor=1.5):
    """
    Detect outliers in a series using IQR method.
    
    Args:
        series (Series): Input series
        factor (float): IQR multiplier (default: 1.5)
        
    Returns:
        list: Indices of outliers
    """
    # Drop NaN values
    series_clean = series.dropna()
    
    # Calculate Q1, Q3, and IQR
    q1 = series_clean.quantile(0.25)
    q3 = series_clean.quantile(0.75)
    iqr = q3 - q1
    
    # Define bounds
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    
    # Find outliers
    outlier_mask = (series_clean < lower_bound) | (series_clean > upper_bound)
    outlier_indices = series_clean[outlier_mask].index.tolist()
    
    return outlier_indices

def find_strong_correlations(corr_matrix, threshold=0.7):
    """
    Find strong correlations in a correlation matrix.
    
    Args:
        corr_matrix (DataFrame): Correlation matrix
        threshold (float): Correlation threshold (default: 0.7)
        
    Returns:
        list: List of tuples containing (column1, column2, correlation_value)
    """
    strong_correlations = []
    
    # Get the upper triangle of the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) >= threshold:
                strong_correlations.append(
                    ((corr_matrix.columns[i], corr_matrix.columns[j]), corr_matrix.iloc[i, j])
                )
    
    return strong_correlations

def identify_date_columns(df):
    """
    Identify potential date or time columns in a DataFrame.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        list: List of column names that may contain dates
    """
    date_columns = []
    
    # Check column names for date-related keywords
    date_keywords = ['date', 'time', 'day', 'month', 'year', 'dt', 'created', 'updated', 'timestamp']
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Check if column name contains date keywords
        if any(keyword in col_lower for keyword in date_keywords):
            date_columns.append(col)
            continue
        
        # Try to convert the column to datetime
        if df[col].dtype == 'object':
            try:
                # Check a sample of values (first 100 or fewer)
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    # Try to parse dates
                    pd.to_datetime(sample, errors='raise')
                    date_columns.append(col)
            except:
                # Not a date column
                pass
    
    return date_columns

def convert_to_numeric(df, column):
    """
    Convert a column to numeric, handling currency symbols and other non-numeric characters.
    
    Args:
        df (DataFrame): Input DataFrame
        column (str): Column name to convert
        
    Returns:
        Series: Converted numeric series
    """
    # Create a copy to avoid modifying the original
    series = df[column].copy()
    
    # If already numeric, return as is
    if pd.api.types.is_numeric_dtype(series):
        return series
    
    # Convert to string to handle any data type
    series = series.astype(str)
    
    # Remove currency symbols, commas, etc.
    # This pattern matches common currency symbols, commas, spaces, and other non-numeric chars
    pattern = r'[^\d.-]'
    numeric_strings = series.str.replace(pattern, '', regex=True)
    
    # Convert to numeric
    return pd.to_numeric(numeric_strings, errors='coerce')

def normalize_column(df, column):
    """
    Normalize a numeric column to [0, 1] range.
    
    Args:
        df (DataFrame): Input DataFrame
        column (str): Column name to normalize
        
    Returns:
        Series: Normalized series
    """
    min_val = df[column].min()
    max_val = df[column].max()
    
    # Handle the case where min == max (avoid division by zero)
    if min_val == max_val:
        return pd.Series(0.5, index=df.index)
    
    return (df[column] - min_val) / (max_val - min_val)

def standardize_column(df, column):
    """
    Standardize a numeric column (z-score normalization).
    
    Args:
        df (DataFrame): Input DataFrame
        column (str): Column name to standardize
        
    Returns:
        Series: Standardized series
    """
    mean_val = df[column].mean()
    std_val = df[column].std()
    
    # Handle the case where std == 0 (avoid division by zero)
    if std_val == 0:
        return pd.Series(0, index=df.index)
    
    return (df[column] - mean_val) / std_val

def bin_numeric_column(df, column, bins, labels=None):
    """
    Create bins from a numeric column.
    
    Args:
        df (DataFrame): Input DataFrame
        column (str): Column name to bin
        bins (int or list): Number of bins or bin edges
        labels (list, optional): Labels for bins
        
    Returns:
        Series: Binned series
    """
    return pd.cut(df[column], bins=bins, labels=labels)

def find_duplicates(df, subset=None):
    """
    Find duplicate rows in a DataFrame.
    
    Args:
        df (DataFrame): Input DataFrame
        subset (list, optional): Columns to consider for identifying duplicates
        
    Returns:
        DataFrame: Duplicate rows
    """
    return df[df.duplicated(subset=subset, keep='first')]

def categorize_text_column(df, text_column, categories, case_sensitive=False):
    """
    Categorize text based on keywords.
    
    Args:
        df (DataFrame): Input DataFrame
        text_column (str): Column containing text
        categories (dict): Dictionary mapping category names to lists of keywords
        case_sensitive (bool): Whether matching should be case sensitive
        
    Returns:
        Series: Categorized series
    """
    # Convert to string type
    text_series = df[text_column].astype(str)
    
    # Prepare an empty result series
    result = pd.Series(index=df.index, dtype='object')
    
    # Process each category
    for category, keywords in categories.items():
        # Prepare regex pattern
        pattern = '|'.join([re.escape(keyword) for keyword in keywords])
        
        # Find matches
        if case_sensitive:
            mask = text_series.str.contains(pattern, regex=True, na=False)
        else:
            mask = text_series.str.contains(pattern, regex=True, case=False, na=False)
        
        # Assign category
        result[mask] = category
    
    # Fill remaining with 'Other'
    result = result.fillna('Other')
    
    return result
