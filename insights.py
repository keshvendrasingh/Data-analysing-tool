import streamlit as st
import pandas as pd
import numpy as np
from utils import data_processing, ml_utils
import plotly.express as px
import plotly.graph_objects as go

def show():
    st.header("Automated Insights")
    
    # Check if data is available
    if st.session_state.cleaned_data is None:
        st.warning("No data available. Please import and clean data first.")
        if st.button("Go to Import Data"):
            st.session_state.current_page = "Import Data"
            st.rerun()
        return
    
    # Get data
    df = st.session_state.cleaned_data
    
    # Display the data image
    st.image("https://images.unsplash.com/photo-1599658880436-c61792e70672", use_column_width=True)  # Myriam Jessier data analytics image
    
    # Basic data insights
    st.subheader("Basic Data Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()
        st.metric("Numeric/Categorical Columns", f"{len(numeric_cols)}/{len(categorical_cols)}")
    
    # Insight tabs
    summary_tab, correlation_tab, outlier_tab, prediction_tab, trends_tab = st.tabs([
        "📊 Data Summary", 
        "🔄 Correlations", 
        "🔍 Outliers", 
        "🔮 Predictions",
        "📈 Trends"
    ])
    
    # Data Summary Tab
    with summary_tab:
        st.subheader("Data Profile")
        
        if numeric_cols:
            # Show statistical summary for numeric columns
            st.write("**Numerical Data Summary**")
            numeric_summary = df[numeric_cols].describe().T
            # Add additional metrics
            numeric_summary['missing'] = df[numeric_cols].isnull().sum()
            numeric_summary['missing_pct'] = df[numeric_cols].isnull().sum() / len(df) * 100
            numeric_summary['unique'] = df[numeric_cols].nunique()
            
            st.dataframe(numeric_summary)
            
            # Visualization of key statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Select a column to visualize distribution
                selected_col = st.selectbox(
                    "Select a numeric column to visualize distribution",
                    options=numeric_cols
                )
                
                # Create histogram and density plot
                fig = px.histogram(
                    df, x=selected_col,
                    marginal="box",
                    title=f"Distribution of {selected_col}",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show additional stats and insights
                st.write(f"**Insights for {selected_col}**")
                
                # Calculate additional statistics
                skewness = df[selected_col].skew()
                kurtosis = df[selected_col].kurtosis()
                
                # Show statistics
                st.write(f"**Mean:** {df[selected_col].mean():.2f}")
                st.write(f"**Median:** {df[selected_col].median():.2f}")
                st.write(f"**Standard Deviation:** {df[selected_col].std():.2f}")
                st.write(f"**Skewness:** {skewness:.2f}")
                st.write(f"**Kurtosis:** {kurtosis:.2f}")
                
                # Interpret skewness
                if abs(skewness) < 0.5:
                    st.write("✅ The data is approximately symmetric")
                elif skewness < 0:
                    st.write("ℹ️ The data is negatively skewed (left tail is longer)")
                else:
                    st.write("ℹ️ The data is positively skewed (right tail is longer)")
                
                # Interpret kurtosis
                if kurtosis < -0.5:
                    st.write("ℹ️ The distribution has lighter tails than normal (platykurtic)")
                elif kurtosis > 0.5:
                    st.write("ℹ️ The distribution has heavier tails than normal (leptokurtic)")
                else:
                    st.write("✅ The distribution has similar tails to normal distribution (mesokurtic)")
        
        if categorical_cols:
            st.write("**Categorical Data Summary**")
            
            categorical_summary = pd.DataFrame({
                'unique_values': df[categorical_cols].nunique(),
                'missing': df[categorical_cols].isnull().sum(),
                'missing_pct': df[categorical_cols].isnull().sum() / len(df) * 100,
                'most_common': [df[col].value_counts().index[0] if not df[col].isnull().all() and len(df[col].value_counts()) > 0 else None for col in categorical_cols],
                'most_common_pct': [df[col].value_counts(normalize=True).iloc[0] * 100 if not df[col].isnull().all() and len(df[col].value_counts()) > 0 else None for col in categorical_cols]
            })
            
            st.dataframe(categorical_summary)
            
            # Visualization of categorical data
            col1, col2 = st.columns(2)
            
            with col1:
                # Select a column to visualize
                if categorical_cols:
                    selected_cat_col = st.selectbox(
                        "Select a categorical column to visualize",
                        options=categorical_cols
                    )
                    
                    # Count the values and show only top N for readability
                    value_counts = df[selected_cat_col].value_counts().reset_index()
                    value_counts.columns = [selected_cat_col, 'count']
                    
                    # Limit to top 10 categories for better visualization
                    if len(value_counts) > 10:
                        remaining_count = value_counts.iloc[10:]['count'].sum()
                        value_counts = value_counts.iloc[:10]
                        # Add 'Other' category for remaining values
                        value_counts = pd.concat([
                            value_counts,
                            pd.DataFrame({selected_cat_col: ['Other'], 'count': [remaining_count]})
                        ])
                    
                    fig = px.pie(
                        value_counts, 
                        names=selected_cat_col, 
                        values='count',
                        title=f"Distribution of {selected_cat_col}",
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write(f"**Insights for {selected_cat_col}**")
                
                # Get value counts and percentages
                val_counts = df[selected_cat_col].value_counts()
                val_percent = df[selected_cat_col].value_counts(normalize=True) * 100
                
                # Show most common values
                st.write(f"**Most common value:** {val_counts.index[0]} ({val_percent.iloc[0]:.1f}%)")
                
                # Calculate diversity metrics
                uniqueness = df[selected_cat_col].nunique() / len(df)
                st.write(f"**Uniqueness ratio:** {uniqueness:.4f}")
                
                if uniqueness < 0.01:
                    st.write("ℹ️ This column has very low variety (few unique values)")
                elif uniqueness > 0.9:
                    st.write("ℹ️ This column has very high variety (many unique values, potentially an ID)")
                
                # Missing values
                missing = df[selected_cat_col].isnull().sum()
                missing_pct = missing / len(df) * 100
                st.write(f"**Missing values:** {missing} ({missing_pct:.1f}%)")
    
    # Correlation Tab
    with correlation_tab:
        st.subheader("Correlation Analysis")
        
        if len(numeric_cols) >= 2:
            # Correlation method
            corr_method = st.selectbox(
                "Select correlation method",
                options=["pearson", "spearman", "kendall"],
                index=0
            )
            
            # Calculate correlation matrix
            corr_matrix = df[numeric_cols].corr(method=corr_method)
            
            # Show correlation matrix
            st.write("**Correlation Matrix**")
            st.dataframe(corr_matrix.style.background_gradient(cmap="coolwarm"))
            
            # Plot correlation heatmap
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                title=f"{corr_method.capitalize()} Correlation Heatmap",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Find and display strong correlations
            strong_correlations = data_processing.find_strong_correlations(corr_matrix, threshold=0.7)
            
            if strong_correlations:
                st.subheader("Strong Correlations Detected")
                st.write("The following pairs of variables show strong correlation:")
                
                for pair, corr_value in strong_correlations:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{pair[0]}** and **{pair[1]}** have a correlation of **{corr_value:.2f}**")
                        
                        # Interpret correlation
                        if corr_value > 0:
                            st.write("✅ Positive correlation: as one variable increases, the other tends to increase")
                        else:
                            st.write("ℹ️ Negative correlation: as one variable increases, the other tends to decrease")
                    
                    with col2:
                        # Scatter plot to visualize correlation
                        fig = px.scatter(
                            df, x=pair[0], y=pair[1],
                            title=f"Scatter Plot: {pair[0]} vs {pair[1]}",
                            trendline="ols",  # Add trend line
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No strong correlations found in the data (threshold: 0.7)")
        else:
            st.info("Correlation analysis requires at least 2 numeric columns.")
    
    # Outlier Tab
    with outlier_tab:
        st.subheader("Outlier Detection")
        
        if numeric_cols:
            # Select method for outlier detection
            outlier_method = st.selectbox(
                "Select outlier detection method",
                options=["Z-Score", "IQR (Interquartile Range)", "Isolation Forest"],
                index=1
            )
            
            # Select column for outlier detection
            selected_col = st.selectbox(
                "Select column to analyze for outliers",
                options=numeric_cols,
                key="outlier_column"
            )
            
            # Set parameters based on method
            if outlier_method == "Z-Score":
                threshold = st.slider("Z-Score threshold", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
                outliers = data_processing.detect_outliers_zscore(df[selected_col], threshold)
            
            elif outlier_method == "IQR (Interquartile Range)":
                factor = st.slider("IQR factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
                outliers = data_processing.detect_outliers_iqr(df[selected_col], factor)
            
            elif outlier_method == "Isolation Forest":
                contamination = st.slider("Contamination (expected proportion of outliers)", 
                                         min_value=0.01, max_value=0.2, value=0.05, step=0.01)
                outliers = ml_utils.detect_outliers_isolation_forest(df[[selected_col]], contamination)
            
            # Display results
            outlier_count = len(outliers)
            outlier_percent = outlier_count / len(df) * 100
            
            st.metric("Outliers Detected", f"{outlier_count} ({outlier_percent:.2f}%)")
            
            # Visualize outliers
            fig = px.box(
                df, y=selected_col,
                title=f"Box Plot of {selected_col} with Outliers",
                template="plotly_white",
                points="all"  # Show all points
            )
            
            # Highlight outliers
            if outliers:
                outlier_values = df.iloc[outliers][selected_col].values
                fig.add_trace(
                    go.Scatter(
                        y=outlier_values,
                        mode='markers',
                        marker=dict(color='red', size=10, symbol='circle-open'),
                        name='Outliers'
                    )
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display outlier data
            if outliers:
                st.write("**Outlier Details**")
                st.dataframe(df.iloc[outliers])
                
                # Option to remove outliers
                if st.button("Remove Outliers and Create New Dataset"):
                    cleaned_df = df.drop(outliers)
                    st.session_state.cleaned_data = cleaned_df
                    st.success(f"Removed {outlier_count} outliers from the dataset")
                    st.rerun()
            else:
                st.success("No outliers detected with the current settings.")
        else:
            st.info("Outlier detection requires numeric columns in the dataset.")
    
    # Prediction Tab
    with prediction_tab:
        st.subheader("Predictive Analysis")
        
        if len(numeric_cols) >= 2:
            # Select target variable
            target_col = st.selectbox(
                "Select target variable (what you want to predict)",
                options=numeric_cols,
                key="target_variable"
            )
            
            # Select features
            feature_cols = st.multiselect(
                "Select features for prediction (explanatory variables)",
                options=[col for col in numeric_cols if col != target_col],
                default=[col for col in numeric_cols[:3] if col != target_col]
            )
            
            if feature_cols:
                # Select model type
                model_type = st.selectbox(
                    "Select model type",
                    options=["Linear Regression", "Random Forest", "Gradient Boosting"],
                    index=0
                )
                
                # Set test size
                test_size = st.slider("Test set size (%)", min_value=10, max_value=50, value=20, step=5) / 100
                
                # Train model button
                if st.button("Train Model"):
                    with st.spinner("Training model..."):
                        # Train the model
                        model_result = ml_utils.train_and_evaluate_model(
                            df, 
                            target_col, 
                            feature_cols, 
                            model_type, 
                            test_size
                        )
                        
                        # Display model performance
                        st.subheader("Model Performance")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("R² Score", f"{model_result['r2_score']:.4f}")
                        
                        with col2:
                            st.metric("MAE", f"{model_result['mae']:.4f}")
                        
                        with col3:
                            st.metric("RMSE", f"{model_result['rmse']:.4f}")
                        
                        # Show feature importance
                        st.subheader("Feature Importance")
                        
                        fig = px.bar(
                            x=model_result['feature_importance'],
                            y=feature_cols,
                            orientation='h',
                            title="Feature Importance",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Predicted vs Actual plot
                        st.subheader("Predicted vs Actual Values")
                        
                        fig = px.scatter(
                            x=model_result['y_test'],
                            y=model_result['y_pred'],
                            labels={'x': 'Actual', 'y': 'Predicted'},
                            title=f"Actual vs Predicted {target_col}",
                            template="plotly_white",
                        )
                        
                        # Add diagonal line (perfect predictions)
                        fig.add_trace(
                            go.Scatter(
                                x=[min(model_result['y_test']), max(model_result['y_test'])],
                                y=[min(model_result['y_test']), max(model_result['y_test'])],
                                mode='lines',
                                line=dict(color='red', dash='dash'),
                                name='Perfect Prediction'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Model interpretation and insights
                        st.subheader("Model Interpretation")
                        
                        # Interpret R² score
                        if model_result['r2_score'] > 0.8:
                            st.write("✅ The model explains the data very well (R² > 0.8)")
                        elif model_result['r2_score'] > 0.6:
                            st.write("✅ The model explains the data reasonably well (R² > 0.6)")
                        elif model_result['r2_score'] > 0.4:
                            st.write("ℹ️ The model explains the data moderately (R² > 0.4)")
                        else:
                            st.write("⚠️ The model explains little of the variation in the data (R² < 0.4)")
                        
                        # Get top features
                        feature_importances = list(zip(feature_cols, model_result['feature_importance']))
                        feature_importances.sort(key=lambda x: x[1], reverse=True)
                        
                        st.write("**Most important features:**")
                        for feature, importance in feature_importances[:3]:
                            st.write(f"- **{feature}** (importance: {importance:.4f})")
            else:
                st.warning("Please select at least one feature for prediction.")
        else:
            st.info("Predictive analysis requires at least two numeric columns.")
    
    # Trends Tab
    with trends_tab:
        st.subheader("Trend Analysis")
        
        # Check if there are potential date or time columns
        date_cols = data_processing.identify_date_columns(df)
        
        if date_cols:
            # Select date column
            date_column = st.selectbox(
                "Select date/time column",
                options=date_cols
            )
            
            # Ensure column is properly formatted as datetime
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
            
            # Remove rows with invalid dates
            df_copy = df_copy.dropna(subset=[date_column])
            
            if not df_copy.empty:
                # Select numeric variable to analyze
                value_column = st.selectbox(
                    "Select numeric column to analyze",
                    options=numeric_cols
                )
                
                # Select time frequency for resampling
                time_freq = st.selectbox(
                    "Select time frequency",
                    options=["Day", "Week", "Month", "Quarter", "Year"],
                    index=2
                )
                
                # Map selected frequency to pandas offset string
                freq_map = {
                    "Day": "D",
                    "Week": "W",
                    "Month": "M",
                    "Quarter": "Q",
                    "Year": "Y"
                }
                
                # Apply aggregation method
                agg_method = st.selectbox(
                    "Select aggregation method",
                    options=["Mean", "Sum", "Min", "Max", "Count"],
                    index=0
                )
                
                # Map to pandas aggregation method
                agg_map = {
                    "Mean": "mean",
                    "Sum": "sum",
                    "Min": "min",
                    "Max": "max",
                    "Count": "count"
                }
                
                # Prepare data for time series
                df_copy = df_copy.sort_values(by=date_column)
                df_copy = df_copy.set_index(date_column)
                
                # Resample and aggregate
                time_series = df_copy[value_column].resample(freq_map[time_freq]).agg(agg_map[agg_method])
                
                # Plot time series
                fig = px.line(
                    time_series,
                    title=f"{agg_method} of {value_column} by {time_freq}",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Trend detection
                st.subheader("Trend Detection")
                
                # Calculate trend
                trend_result = ml_utils.analyze_trend(time_series)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display trend metrics
                    st.metric("Trend Direction", trend_result['direction'])
                    st.metric("Trend Strength", f"{trend_result['strength']:.2f}")
                
                with col2:
                    # Interpretation
                    st.write("**Trend Interpretation:**")
                    
                    if trend_result['direction'] == "Increasing":
                        st.write("✅ The data shows an **increasing** trend over time")
                    elif trend_result['direction'] == "Decreasing":
                        st.write("ℹ️ The data shows a **decreasing** trend over time")
                    else:
                        st.write("ℹ️ No clear trend detected in the data")
                    
                    if abs(trend_result['strength']) > 0.7:
                        st.write("✅ The trend is **strong**")
                    elif abs(trend_result['strength']) > 0.3:
                        st.write("ℹ️ The trend is **moderate**")
                    else:
                        st.write("ℹ️ The trend is **weak**")
                
                # Optional: Perform seasonal decomposition if enough data points
                if len(time_series) >= 4:
                    if st.checkbox("Perform Seasonal Decomposition"):
                        # Perform decomposition
                        try:
                            decomposition = ml_utils.perform_seasonal_decomposition(time_series)
                            
                            # Plot components
                            st.subheader("Seasonal Decomposition")
                            
                            # Trend component
                            fig_trend = px.line(
                                decomposition['trend'],
                                title="Trend Component",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_trend, use_container_width=True)
                            
                            # Seasonal component
                            fig_seasonal = px.line(
                                decomposition['seasonal'],
                                title="Seasonal Component",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_seasonal, use_container_width=True)
                            
                            # Residual component
                            fig_residual = px.line(
                                decomposition['residual'],
                                title="Residual Component",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_residual, use_container_width=True)
                            
                            # Interpretation
                            st.subheader("Seasonality Interpretation")
                            
                            # Check for significant seasonality
                            seasonal_strength = ml_utils.calculate_seasonal_strength(decomposition)
                            
                            if seasonal_strength > 0.6:
                                st.write("✅ Strong seasonal pattern detected")
                            elif seasonal_strength > 0.3:
                                st.write("ℹ️ Moderate seasonal pattern detected")
                            else:
                                st.write("ℹ️ Weak or no seasonal pattern detected")
                            
                            st.metric("Seasonality Strength", f"{seasonal_strength:.2f}")
                            
                        except Exception as e:
                            st.error(f"Error performing seasonal decomposition: {str(e)}")
                            st.info("Seasonal decomposition requires regular time series data with enough periods.")
                
                # Optional: Forecasting
                if st.checkbox("Generate Forecast"):
                    # Number of periods to forecast
                    periods = st.slider("Number of periods to forecast", min_value=1, max_value=12, value=3)
                    
                    # Perform forecasting
                    forecast_result = ml_utils.generate_forecast(time_series, periods)
                    
                    # Plot the forecast
                    st.subheader("Time Series Forecast")
                    
                    fig = go.Figure()
                    
                    # Add historical data
                    fig.add_trace(
                        go.Scatter(
                            x=time_series.index,
                            y=time_series.values,
                            name="Historical Data",
                            mode="lines"
                        )
                    )
                    
                    # Add forecast
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_result['forecast'].index,
                            y=forecast_result['forecast'].values,
                            name="Forecast",
                            mode="lines",
                            line=dict(dash='dash', color='red')
                        )
                    )
                    
                    # Add confidence intervals if available
                    if 'lower_bound' in forecast_result and 'upper_bound' in forecast_result:
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_result['lower_bound'].index,
                                y=forecast_result['lower_bound'].values,
                                fill=None,
                                mode='lines',
                                line=dict(color='rgba(0, 0, 255, 0)'),
                                showlegend=False
                            )
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_result['upper_bound'].index,
                                y=forecast_result['upper_bound'].values,
                                fill='tonexty',
                                mode='lines',
                                line=dict(color='rgba(0, 0, 255, 0)'),
                                name='95% Confidence Interval'
                            )
                        )
                    
                    fig.update_layout(
                        title=f"Forecast for {value_column} ({periods} periods ahead)",
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display forecast values
                    st.write("**Forecast Values:**")
                    forecast_df = forecast_result['forecast'].reset_index()
                    forecast_df.columns = ['Date', 'Forecast']
                    st.dataframe(forecast_df)
            else:
                st.warning("Failed to convert the selected column to valid dates.")
        else:
            st.info("No date/time columns detected in the data. Trend analysis requires a date or time column.")
            
            # Option to convert a column to datetime
            st.write("**Convert a column to date/time**")
            col_to_convert = st.selectbox("Select column to convert to date/time", options=df.columns.tolist())
            
            if st.button("Convert to Date/Time"):
                try:
                    df_copy = df.copy()
                    df_copy[col_to_convert] = pd.to_datetime(df_copy[col_to_convert], errors='coerce')
                    
                    invalid_dates = df_copy[col_to_convert].isna().sum()
                    
                    if invalid_dates / len(df_copy) > 0.5:
                        st.error(f"More than 50% of values in '{col_to_convert}' could not be converted to valid dates.")
                    else:
                        st.session_state.cleaned_data = df_copy
                        if invalid_dates > 0:
                            st.warning(f"{invalid_dates} values could not be converted to valid dates and were set to NaN.")
                        st.success(f"Column '{col_to_convert}' has been converted to date/time format.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error converting column to date/time: {str(e)}")
    
    # Navigation buttons
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Go to Export", type="primary"):
            st.session_state.current_page = "Export"
            st.rerun()
    
    with col2:
        if st.button("Back to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
