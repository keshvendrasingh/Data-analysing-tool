import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import visualization_utils

def show():
    st.header("Data Visualization")
    
    # Check if data is available
    if st.session_state.cleaned_data is None:
        st.warning("No data available. Please import and clean data first.")
        if st.button("Go to Import Data"):
            st.session_state.current_page = "Import Data"
            st.rerun()
        return
    
    # Get data and columns
    df = st.session_state.cleaned_data
    
    # Basic info about the data
    st.subheader("Data Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Rows:** {df.shape[0]}")
        st.write(f"**Columns:** {df.shape[1]}")
    with col2:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()
        st.write(f"**Numeric columns:** {len(numeric_cols)}")
        st.write(f"**Categorical columns:** {len(categorical_cols)}")
    
    # Display data preview
    with st.expander("Data Preview"):
        st.dataframe(df.head(10))
    
    # Create tabs for different chart types
    basic_tab, dist_tab, rel_tab, geo_tab, time_tab, hierarchy_tab, custom_tab = st.tabs([
        "📊 Basic Charts", 
        "📈 Distribution", 
        "🔗 Relationships", 
        "🗺️ Geo & Maps",
        "⏱️ Time Series",
        "🌳 Hierarchical",
        "🎨 Advanced Charts"
    ])
    
    # Basic Charts Tab
    with basic_tab:
        st.subheader("Basic Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "Select chart type",
                options=["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Bubble Chart", "Area Chart"],
                key="basic_chart_type"
            )
        
        with col2:
            # Different options depending on chart type
            if chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
                x_col = st.selectbox("X-axis column", options=df.columns.tolist(), key="basic_x")
                y_col = st.selectbox("Y-axis column", options=numeric_cols, key="basic_y")
                
                if chart_type == "Bar Chart":
                    orientation = st.radio("Orientation", options=["Vertical", "Horizontal"], key="bar_orientation")
            
            elif chart_type == "Pie Chart":
                label_col = st.selectbox("Labels", options=df.columns.tolist(), key="pie_labels")
                value_col = st.selectbox("Values", options=numeric_cols, key="pie_values")
            
            elif chart_type in ["Scatter Plot", "Bubble Chart"]:
                x_col = st.selectbox("X-axis column", options=numeric_cols, key="scatter_x")
                y_col = st.selectbox("Y-axis column", options=numeric_cols, key="scatter_y")
                
                if chart_type == "Bubble Chart":
                    size_col = st.selectbox("Size column", options=numeric_cols, key="bubble_size")
        
        # Additional options
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if chart_type not in ["Pie Chart"]:
                title = st.text_input("Chart Title", value=f"{chart_type}", key="basic_title")
            else:
                title = st.text_input("Chart Title", value=f"Distribution of {label_col}", key="pie_title")
        
        with col2:
            color_col = st.selectbox("Color by (optional)", options=["None"] + df.columns.tolist(), key="basic_color")
            color_col = None if color_col == "None" else color_col
        
        with col3:
            theme = st.selectbox(
                "Color theme",
                options=["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"],
                key="basic_theme"
            )
        
        # Generate the chart
        st.divider()
        try:
            if chart_type == "Bar Chart":
                fig = visualization_utils.create_bar_chart(
                    df, x_col, y_col, 
                    color_col=color_col, 
                    title=title,
                    is_horizontal=(orientation == "Horizontal"), 
                    template=theme
                )
            
            elif chart_type == "Line Chart":
                fig = visualization_utils.create_line_chart(
                    df, x_col, y_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif chart_type == "Pie Chart":
                fig = visualization_utils.create_pie_chart(
                    df, label_col, value_col,
                    title=title,
                    template=theme
                )
            
            elif chart_type == "Scatter Plot":
                fig = visualization_utils.create_scatter_plot(
                    df, x_col, y_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif chart_type == "Bubble Chart":
                fig = visualization_utils.create_bubble_chart(
                    df, x_col, y_col, size_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif chart_type == "Area Chart":
                fig = visualization_utils.create_area_chart(
                    df, x_col, y_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Save button for dashboard
            if st.button("Add to Dashboard", key="add_basic_chart"):
                if 'visualizations' not in st.session_state:
                    st.session_state.visualizations = []
                
                # Save visualization info
                vis_info = {
                    "type": chart_type,
                    "fig": fig,
                    "title": title,
                    "params": {
                        "chart_type": chart_type,
                        "x_col": x_col if chart_type not in ["Pie Chart"] else None,
                        "y_col": y_col if chart_type not in ["Pie Chart"] else None,
                        "label_col": label_col if chart_type == "Pie Chart" else None,
                        "value_col": value_col if chart_type == "Pie Chart" else None,
                        "size_col": size_col if chart_type == "Bubble Chart" else None,
                        "color_col": color_col,
                        "theme": theme,
                        "orientation": orientation if chart_type == "Bar Chart" else None
                    }
                }
                
                st.session_state.visualizations.append(vis_info)
                st.success(f"Added {chart_type} to dashboard!")
        
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    # Distribution Tab
    with dist_tab:
        st.subheader("Distribution Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dist_chart_type = st.selectbox(
                "Select distribution chart",
                options=["Histogram", "Box Plot", "Violin Plot", "Density Plot"],
                key="dist_chart_type"
            )
            
            if dist_chart_type in ["Histogram", "Density Plot"]:
                value_col = st.selectbox("Value column", options=numeric_cols, key="hist_value")
            
            elif dist_chart_type in ["Box Plot", "Violin Plot"]:
                value_col = st.selectbox("Value column", options=numeric_cols, key="box_value")
                group_col = st.selectbox("Group by (optional)", options=["None"] + categorical_cols, key="box_group")
                group_col = None if group_col == "None" else group_col
        
        with col2:
            title = st.text_input("Chart Title", value=f"{dist_chart_type} of {value_col}", key="dist_title")
            
            color_col = st.selectbox("Color by (optional)", options=["None"] + categorical_cols, key="dist_color")
            color_col = None if color_col == "None" else color_col
            
            theme = st.selectbox(
                "Color theme",
                options=["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"],
                key="dist_theme"
            )
        
        # Generate the chart
        st.divider()
        try:
            if dist_chart_type == "Histogram":
                bins = st.slider("Number of bins", min_value=5, max_value=100, value=20, key="hist_bins")
                
                fig = visualization_utils.create_histogram(
                    df, value_col, 
                    bins=bins,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif dist_chart_type == "Box Plot":
                fig = visualization_utils.create_box_plot(
                    df, value_col, 
                    group_col=group_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif dist_chart_type == "Violin Plot":
                fig = visualization_utils.create_violin_plot(
                    df, value_col, 
                    group_col=group_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            elif dist_chart_type == "Density Plot":
                fig = visualization_utils.create_density_plot(
                    df, value_col,
                    color_col=color_col,
                    title=title,
                    template=theme
                )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Save button for dashboard
            if st.button("Add to Dashboard", key="add_dist_chart"):
                if 'visualizations' not in st.session_state:
                    st.session_state.visualizations = []
                
                # Save visualization info
                vis_info = {
                    "type": dist_chart_type,
                    "fig": fig,
                    "title": title,
                    "params": {
                        "chart_type": dist_chart_type,
                        "value_col": value_col,
                        "group_col": group_col if dist_chart_type in ["Box Plot", "Violin Plot"] else None,
                        "bins": bins if dist_chart_type == "Histogram" else None,
                        "color_col": color_col,
                        "theme": theme
                    }
                }
                
                st.session_state.visualizations.append(vis_info)
                st.success(f"Added {dist_chart_type} to dashboard!")
        
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    # Relationships Tab
    with rel_tab:
        st.subheader("Relationship Charts")
        
        rel_chart_type = st.selectbox(
            "Select relationship chart",
            options=["Correlation Heatmap", "Scatter Matrix", "Parallel Coordinates", "Radar Chart"],
            key="rel_chart_type"
        )
        
        # Options based on chart type
        if rel_chart_type == "Correlation Heatmap":
            col1, col2 = st.columns(2)
            
            with col1:
                corr_method = st.selectbox(
                    "Correlation method",
                    options=["pearson", "spearman", "kendall"],
                    key="corr_method"
                )
                
                title = st.text_input("Chart Title", value=f"Correlation Heatmap ({corr_method})", key="corr_title")
            
            with col2:
                corr_cols = st.multiselect(
                    "Select columns (numeric only)",
                    options=numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))],
                    key="corr_cols"
                )
                
                color_scale = st.selectbox(
                    "Color scale",
                    options=["RdBu_r", "Viridis", "Plasma", "Cividis", "Blues", "Reds"],
                    key="corr_colorscale"
                )
            
            if len(corr_cols) >= 2:
                try:
                    fig = visualization_utils.create_correlation_heatmap(
                        df, 
                        columns=corr_cols,
                        method=corr_method,
                        colorscale=color_scale,
                        title=title
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_corr_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Correlation Heatmap",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Correlation Heatmap",
                                "columns": corr_cols,
                                "method": corr_method,
                                "colorscale": color_scale
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Correlation Heatmap to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating correlation heatmap: {str(e)}")
            else:
                st.warning("Please select at least 2 columns for correlation analysis")
        
        elif rel_chart_type == "Scatter Matrix":
            col1, col2 = st.columns(2)
            
            with col1:
                scatter_cols = st.multiselect(
                    "Select columns (numeric recommended)",
                    options=df.columns.tolist(),
                    default=numeric_cols[:min(4, len(numeric_cols))],
                    key="scatter_matrix_cols"
                )
                
                title = st.text_input("Chart Title", value="Scatter Matrix", key="scatter_matrix_title")
            
            with col2:
                color_col = st.selectbox(
                    "Color by (categorical recommended)",
                    options=["None"] + df.columns.tolist(),
                    key="scatter_matrix_color"
                )
                color_col = None if color_col == "None" else color_col
                
                diagonal_type = st.selectbox(
                    "Diagonal plot type",
                    options=["histogram", "box", "violin", "rug"],
                    key="diagonal_type"
                )
            
            if len(scatter_cols) >= 2:
                try:
                    fig = visualization_utils.create_scatter_matrix(
                        df,
                        dimensions=scatter_cols,
                        color=color_col,
                        diagonal_visible=True,
                        title=title,
                        diagonal_type=diagonal_type
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_scattermatrix_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Scatter Matrix",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Scatter Matrix",
                                "dimensions": scatter_cols,
                                "color": color_col,
                                "diagonal_type": diagonal_type
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Scatter Matrix to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating scatter matrix: {str(e)}")
            else:
                st.warning("Please select at least 2 columns for scatter matrix")
        
        elif rel_chart_type == "Parallel Coordinates":
            col1, col2 = st.columns(2)
            
            with col1:
                parallel_cols = st.multiselect(
                    "Select columns",
                    options=df.columns.tolist(),
                    default=numeric_cols[:min(5, len(numeric_cols))],
                    key="parallel_cols"
                )
                
                title = st.text_input("Chart Title", value="Parallel Coordinates", key="parallel_title")
            
            with col2:
                color_col = st.selectbox(
                    "Color by",
                    options=df.columns.tolist(),
                    key="parallel_color"
                )
                
                color_scale = st.selectbox(
                    "Color scale",
                    options=["Viridis", "Plasma", "Inferno", "Blues", "Reds", "Greens"],
                    key="parallel_colorscale"
                )
            
            if len(parallel_cols) >= 2:
                try:
                    fig = visualization_utils.create_parallel_coordinates(
                        df,
                        dimensions=parallel_cols,
                        color=color_col,
                        colorscale=color_scale.lower(),
                        title=title
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_parallel_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Parallel Coordinates",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Parallel Coordinates",
                                "dimensions": parallel_cols,
                                "color": color_col,
                                "colorscale": color_scale.lower()
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Parallel Coordinates to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating parallel coordinates: {str(e)}")
            else:
                st.warning("Please select at least 2 columns for parallel coordinates")
        
        elif rel_chart_type == "Radar Chart":
            col1, col2 = st.columns(2)
            
            with col1:
                # For radar chart, we need a category column and multiple value columns
                category_col = st.selectbox(
                    "Category column",
                    options=categorical_cols + numeric_cols,
                    key="radar_category"
                )
                
                value_cols = st.multiselect(
                    "Value columns (numeric)",
                    options=numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))],
                    key="radar_values"
                )
                
                if len(df[category_col].unique()) > 10:
                    st.warning("Many unique categories detected. Consider selecting categories.")
                    selected_categories = st.multiselect(
                        "Select specific categories (leave empty for all)",
                        options=sorted(df[category_col].unique().tolist()),
                        key="radar_selected_categories"
                    )
                else:
                    selected_categories = df[category_col].unique().tolist()
            
            with col2:
                title = st.text_input("Chart Title", value="Radar Chart", key="radar_title")
                
                # Aggregation function for multiple values per category
                agg_func = st.selectbox(
                    "Aggregation function",
                    options=["mean", "median", "sum", "min", "max"],
                    key="radar_agg"
                )
                
                # Optional: Scale values
                scale_values = st.checkbox("Scale values (0-1)", value=True, key="radar_scale")
            
            if len(value_cols) >= 3:
                try:
                    fig = visualization_utils.create_radar_chart(
                        df,
                        category_col=category_col,
                        value_cols=value_cols,
                        selected_categories=selected_categories,
                        agg_func=agg_func,
                        scale_values=scale_values,
                        title=title
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_radar_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Radar Chart",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Radar Chart",
                                "category_col": category_col,
                                "value_cols": value_cols,
                                "selected_categories": selected_categories,
                                "agg_func": agg_func,
                                "scale_values": scale_values
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Radar Chart to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating radar chart: {str(e)}")
            else:
                st.warning("Please select at least 3 value columns for a meaningful radar chart")
    
    # Geo & Maps Tab
    with geo_tab:
        st.subheader("Geographic Visualizations")
        st.info("To create geographic visualizations, your data needs to contain geographic information like coordinates, country names, or regions.")
        
        geo_chart_type = st.selectbox(
            "Select geo chart type",
            options=["Choropleth Map", "Scatter Geo", "Bubble Map"],
            key="geo_chart_type"
        )
        
        # Check if any column might contain location data
        potential_location_cols = []
        location_keywords = ['country', 'state', 'city', 'region', 'province', 'county', 'district', 'location', 'address']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in location_keywords):
                potential_location_cols.append(col)
        
        # Check for potential coordinate columns
        potential_lat_cols = []
        potential_lon_cols = []
        
        lat_keywords = ['lat', 'latitude', 'y']
        lon_keywords = ['lon', 'long', 'longitude', 'x']
        
        for col in numeric_cols:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in lat_keywords):
                potential_lat_cols.append(col)
            if any(keyword in col_lower for keyword in lon_keywords):
                potential_lon_cols.append(col)
        
        # Options based on chart type
        if geo_chart_type == "Choropleth Map":
            col1, col2 = st.columns(2)
            
            with col1:
                location_col = st.selectbox(
                    "Location column",
                    options=df.columns.tolist(),
                    index=df.columns.tolist().index(potential_location_cols[0]) if potential_location_cols else 0,
                    key="choropleth_loc"
                )
                
                scope = st.selectbox(
                    "Map scope",
                    options=["world", "usa", "europe", "asia", "africa", "north america", "south america"],
                    key="choropleth_scope"
                )
                
                location_mode = st.selectbox(
                    "Location mode",
                    options=["ISO-3", "country names", "USA-states"],
                    key="choropleth_locmode"
                )
            
            with col2:
                value_col = st.selectbox(
                    "Value column (numeric)",
                    options=numeric_cols,
                    key="choropleth_value"
                )
                
                title = st.text_input("Chart Title", value=f"{value_col} by {location_col}", key="choropleth_title")
                
                color_scale = st.selectbox(
                    "Color scale",
                    options=["Blues", "Reds", "Greens", "Purples", "Oranges", "Viridis", "Plasma"],
                    key="choropleth_colorscale"
                )
            
            try:
                fig = visualization_utils.create_choropleth_map(
                    df,
                    location_col=location_col,
                    value_col=value_col,
                    scope=scope,
                    locationmode=location_mode,
                    colorscale=color_scale.lower(),
                    title=title
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_choropleth_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Choropleth Map",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Choropleth Map",
                            "location_col": location_col,
                            "value_col": value_col,
                            "scope": scope,
                            "locationmode": location_mode,
                            "colorscale": color_scale.lower()
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Choropleth Map to dashboard!")
            
            except Exception as e:
                st.error(f"Error creating choropleth map: {str(e)}")
                st.info("For choropleth maps, make sure your location column contains valid country codes, country names, or state names depending on your selected scope and mode.")
        
        elif geo_chart_type in ["Scatter Geo", "Bubble Map"]:
            col1, col2 = st.columns(2)
            
            with col1:
                lat_col = st.selectbox(
                    "Latitude column",
                    options=numeric_cols,
                    index=numeric_cols.index(potential_lat_cols[0]) if potential_lat_cols else 0,
                    key="geo_lat"
                )
                
                lon_col = st.selectbox(
                    "Longitude column",
                    options=numeric_cols,
                    index=numeric_cols.index(potential_lon_cols[0]) if potential_lon_cols else 0,
                    key="geo_lon"
                )
                
                if geo_chart_type == "Bubble Map":
                    size_col = st.selectbox(
                        "Size column (numeric)",
                        options=numeric_cols,
                        key="geo_size"
                    )
            
            with col2:
                title = st.text_input("Chart Title", value=geo_chart_type, key="geo_title")
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="geo_color"
                )
                color_col = None if color_col == "None" else color_col
                
                scope = st.selectbox(
                    "Map scope",
                    options=["world", "usa", "europe", "asia", "africa", "north america", "south america"],
                    key="geo_scope"
                )
            
            try:
                if geo_chart_type == "Scatter Geo":
                    fig = visualization_utils.create_scatter_geo(
                        df,
                        lat_col=lat_col,
                        lon_col=lon_col,
                        color_col=color_col,
                        scope=scope,
                        title=title
                    )
                else:  # Bubble Map
                    fig = visualization_utils.create_bubble_map(
                        df,
                        lat_col=lat_col,
                        lon_col=lon_col,
                        size_col=size_col,
                        color_col=color_col,
                        scope=scope,
                        title=title
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_geo_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    params = {
                        "chart_type": geo_chart_type,
                        "lat_col": lat_col,
                        "lon_col": lon_col,
                        "color_col": color_col,
                        "scope": scope
                    }
                    
                    if geo_chart_type == "Bubble Map":
                        params["size_col"] = size_col
                    
                    vis_info = {
                        "type": geo_chart_type,
                        "fig": fig,
                        "title": title,
                        "params": params
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success(f"Added {geo_chart_type} to dashboard!")
            
            except Exception as e:
                st.error(f"Error creating geographic visualization: {str(e)}")
                st.info("For geographic visualizations, make sure your latitude and longitude columns contain valid coordinates.")
    
    # Custom Charts Tab
    # Time Series Tab
    with time_tab:
        st.subheader("Time Series Charts")
        
        # Check for potential date/time columns
        potential_date_cols = []
        for col in df.columns:
            # Check if column name suggests it might be a date
            col_lower = col.lower()
            if any(date_term in col_lower for date_term in ['date', 'time', 'day', 'month', 'year', 'period']):
                potential_date_cols.append(col)
        
        col1, col2 = st.columns(2)
        
        with col1:
            time_chart_type = st.selectbox(
                "Select time series chart",
                options=["Line Chart", "Area Chart", "Candlestick Chart", "Time Series Decomposition"],
                key="time_chart_type"
            )
            
            if potential_date_cols:
                date_col = st.selectbox(
                    "Select date/time column",
                    options=potential_date_cols + [col for col in df.columns if col not in potential_date_cols],
                    index=0,
                    key="time_date_col"
                )
            else:
                date_col = st.selectbox(
                    "Select date/time column",
                    options=df.columns.tolist(),
                    key="time_date_col"
                )
        
        with col2:
            if time_chart_type in ["Line Chart", "Area Chart"]:
                value_col = st.selectbox("Select value column", options=numeric_cols, key="time_value_col")
                
                color_col = st.selectbox("Group by (optional)", options=["None"] + categorical_cols, key="time_color_col")
                color_col = None if color_col == "None" else color_col
                
            elif time_chart_type == "Candlestick Chart":
                if len(numeric_cols) >= 4:
                    open_col = st.selectbox("Open column", options=numeric_cols, key="candlestick_open")
                    high_col = st.selectbox("High column", options=numeric_cols, key="candlestick_high")
                    low_col = st.selectbox("Low column", options=numeric_cols, key="candlestick_low")
                    close_col = st.selectbox("Close column", options=numeric_cols, key="candlestick_close")
                else:
                    st.warning("Candlestick charts require at least 4 numeric columns (Open, High, Low, Close)")
                    open_col = high_col = low_col = close_col = None
            
            elif time_chart_type == "Time Series Decomposition":
                value_col = st.selectbox("Select value column", options=numeric_cols, key="decomp_value_col")
                period = st.number_input("Period (e.g., 12 for monthly, 7 for weekly)", min_value=2, value=12, key="decomp_period")
        
        title = st.text_input("Chart Title", value=f"{time_chart_type}", key="time_title")
        
        # Generate chart
        st.divider()
        try:
            if time_chart_type == "Line Chart":
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                fig = visualization_utils.create_line_chart(
                    df.sort_values(by=date_col), 
                    x_col=date_col, 
                    y_col=value_col,
                    color_col=color_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif time_chart_type == "Area Chart":
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                fig = visualization_utils.create_area_chart(
                    df.sort_values(by=date_col), 
                    x_col=date_col, 
                    y_col=value_col,
                    color_col=color_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif time_chart_type == "Candlestick Chart" and open_col and high_col and low_col and close_col:
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                fig = visualization_utils.create_candlestick(
                    df.sort_values(by=date_col),
                    date_col=date_col,
                    open_col=open_col,
                    high_col=high_col,
                    low_col=low_col,
                    close_col=close_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif time_chart_type == "Time Series Decomposition":
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Sort by date and create a time series
                df_sorted = df.sort_values(by=date_col).copy()
                df_sorted = df_sorted[[date_col, value_col]].dropna()
                
                if len(df_sorted) > period * 2:
                    # Set the date as index
                    ts = df_sorted.set_index(date_col)[value_col]
                    
                    # Perform decomposition
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    
                    # Check for non-numeric and handle NaN values
                    if not pd.api.types.is_numeric_dtype(ts):
                        st.error("Time series must be numeric for decomposition")
                    else:
                        # Interpolate missing values if any
                        ts = ts.interpolate(method='linear')
                        
                        try:
                            result = seasonal_decompose(ts, model='additive', period=period)
                            
                            # Create subplots
                            fig = go.Figure()
                            
                            # Original
                            fig.add_trace(go.Scatter(x=ts.index, y=ts.values, mode='lines', name='Original', line=dict(color='blue')))
                            
                            # Trend
                            fig.add_trace(go.Scatter(x=ts.index, y=result.trend, mode='lines', name='Trend', line=dict(color='red')))
                            
                            # Seasonal
                            fig.add_trace(go.Scatter(x=ts.index, y=result.seasonal, mode='lines', name='Seasonal', line=dict(color='green')))
                            
                            # Residual
                            fig.add_trace(go.Scatter(x=ts.index, y=result.resid, mode='lines', name='Residual', line=dict(color='purple')))
                            
                            fig.update_layout(
                                title=title,
                                xaxis_title='Date',
                                yaxis_title='Value',
                                legend=dict(x=0, y=1, orientation='h'),
                                height=600
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Error in decomposition: {str(e)}")
                else:
                    st.error(f"Not enough data points for decomposition. Need at least {period * 2} data points.")
            
            # Save button for dashboard
            if st.button("Add to Dashboard", key="add_time_chart"):
                if 'visualizations' not in st.session_state:
                    st.session_state.visualizations = []
                
                # Save visualization info
                vis_info = {
                    "type": time_chart_type,
                    "fig": fig,
                    "title": title,
                    "params": {
                        "chart_type": time_chart_type,
                        "date_col": date_col,
                        "value_col": value_col if time_chart_type in ["Line Chart", "Area Chart", "Time Series Decomposition"] else None,
                        "open_col": open_col if time_chart_type == "Candlestick Chart" else None,
                        "high_col": high_col if time_chart_type == "Candlestick Chart" else None,
                        "low_col": low_col if time_chart_type == "Candlestick Chart" else None,
                        "close_col": close_col if time_chart_type == "Candlestick Chart" else None,
                        "color_col": color_col if time_chart_type in ["Line Chart", "Area Chart"] else None,
                        "period": period if time_chart_type == "Time Series Decomposition" else None
                    }
                }
                
                st.session_state.visualizations.append(vis_info)
                st.success(f"Added {time_chart_type} to dashboard!")
                
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    # Hierarchical Data Tab
    with hierarchy_tab:
        st.subheader("Hierarchical Data Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hierarchy_chart_type = st.selectbox(
                "Select hierarchy chart",
                options=["Sunburst Chart", "Treemap", "Funnel Chart"],
                key="hierarchy_chart_type"
            )
        
        with col2:
            if hierarchy_chart_type in ["Sunburst Chart", "Treemap"]:
                path_cols = st.multiselect(
                    "Select path columns (order matters)",
                    options=df.columns.tolist(),
                    default=categorical_cols[:min(2, len(categorical_cols))],
                    key="hierarchy_path_cols"
                )
                
                value_col = st.selectbox(
                    "Values column (optional)",
                    options=["None"] + numeric_cols,
                    key="hierarchy_value_col"
                )
                value_col = None if value_col == "None" else value_col
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="hierarchy_color_col"
                )
                color_col = None if color_col == "None" else color_col
            
            elif hierarchy_chart_type == "Funnel Chart":
                stage_col = st.selectbox(
                    "Stage column (categorical)",
                    options=categorical_cols,
                    key="funnel_stage_col"
                )
                
                value_col = st.selectbox(
                    "Value column",
                    options=numeric_cols,
                    key="funnel_value_col"
                )
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + categorical_cols,
                    key="funnel_color_col"
                )
                color_col = None if color_col == "None" else color_col
        
        title = st.text_input("Chart Title", value=f"{hierarchy_chart_type}", key="hierarchy_title")
        
        # Generate chart
        st.divider()
        try:
            if hierarchy_chart_type == "Sunburst Chart" and path_cols:
                fig = visualization_utils.create_sunburst(
                    df,
                    path_cols=path_cols,
                    value_col=value_col,
                    color_col=color_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif hierarchy_chart_type == "Treemap" and path_cols:
                fig = visualization_utils.create_treemap(
                    df,
                    path_cols=path_cols,
                    value_col=value_col,
                    color_col=color_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif hierarchy_chart_type == "Funnel Chart":
                fig = visualization_utils.create_funnel_chart(
                    df,
                    stage_col=stage_col,
                    value_col=value_col,
                    color_col=color_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Save button for dashboard
            if st.button("Add to Dashboard", key="add_hierarchy_chart"):
                if 'visualizations' not in st.session_state:
                    st.session_state.visualizations = []
                
                # Save visualization info
                vis_info = {
                    "type": hierarchy_chart_type,
                    "fig": fig,
                    "title": title,
                    "params": {
                        "chart_type": hierarchy_chart_type,
                        "path_cols": path_cols if hierarchy_chart_type in ["Sunburst Chart", "Treemap"] else None,
                        "stage_col": stage_col if hierarchy_chart_type == "Funnel Chart" else None,
                        "value_col": value_col,
                        "color_col": color_col
                    }
                }
                
                st.session_state.visualizations.append(vis_info)
                st.success(f"Added {hierarchy_chart_type} to dashboard!")
                
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    # Advanced Charts Tab
    with custom_tab:
        st.subheader("Advanced Charts")
        
        custom_chart_type = st.selectbox(
            "Select advanced chart type",
            options=["3D Scatter Plot", "Polar Chart", "Animated Scatter", "Waterfall Chart", "Parallel Categories", "Ridgeline Plot"],
            key="custom_chart_type"
        )
        
        # Options based on chart type
        if custom_chart_type == "3D Scatter Plot":
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis column", options=numeric_cols, key="3d_x")
                y_col = st.selectbox("Y-axis column", options=numeric_cols, key="3d_y")
                z_col = st.selectbox("Z-axis column", options=numeric_cols, key="3d_z")
                
                title = st.text_input("Chart Title", value="3D Scatter Plot", key="3d_title")
            
            with col2:
                color_col = st.selectbox("Color by (optional)", options=["None"] + df.columns.tolist(), key="3d_color")
                color_col = None if color_col == "None" else color_col
                
                size_col = st.selectbox("Size by (optional)", options=["None"] + numeric_cols, key="3d_size")
                size_col = None if size_col == "None" else size_col
            
            try:
                fig = visualization_utils.create_3d_scatter(
                    df,
                    x_col=x_col,
                    y_col=y_col,
                    z_col=z_col,
                    color_col=color_col,
                    size_col=size_col,
                    title=title
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_3d_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "3D Scatter Plot",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "3D Scatter Plot",
                            "x_col": x_col,
                            "y_col": y_col,
                            "z_col": z_col,
                            "color_col": color_col,
                            "size_col": size_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added 3D Scatter Plot to dashboard!")
                
            except Exception as e:
                st.error(f"Error creating 3D Scatter Plot: {str(e)}")
        
        elif custom_chart_type == "Polar Chart":
            col1, col2 = st.columns(2)
            
            with col1:
                r_col = st.selectbox("Radius column (numeric)", options=numeric_cols, key="polar_r")
                theta_col = st.selectbox("Angle column", options=df.columns.tolist(), key="polar_theta")
                
                title = st.text_input("Chart Title", value="Polar Chart", key="polar_title")
            
            with col2:
                color_col = st.selectbox("Color by (optional)", options=["None"] + df.columns.tolist(), key="polar_color")
                color_col = None if color_col == "None" else color_col
                
                chart_mode = st.selectbox(
                    "Chart mode",
                    options=["markers", "lines", "lines+markers"],
                    key="polar_mode"
                )
            
            try:
                # Create polar chart
                if color_col:
                    fig = px.scatter_polar(
                        df, r=r_col, theta=theta_col, color=color_col,
                        title=title
                    )
                else:
                    fig = px.scatter_polar(
                        df, r=r_col, theta=theta_col,
                        title=title
                    )
                
                fig.update_traces(mode=chart_mode)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_polar_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Polar Chart",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Polar Chart",
                            "r_col": r_col,
                            "theta_col": theta_col,
                            "color_col": color_col,
                            "chart_mode": chart_mode
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Polar Chart to dashboard!")
                
            except Exception as e:
                st.error(f"Error creating Polar Chart: {str(e)}")
        
        elif custom_chart_type == "Animated Scatter":
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis column", options=numeric_cols, key="anim_x")
                y_col = st.selectbox("Y-axis column", options=numeric_cols, key="anim_y")
                
                frame_col = st.selectbox(
                    "Animation frame column",
                    options=df.columns.tolist(),
                    key="anim_frame"
                )
                
                title = st.text_input("Chart Title", value="Animated Scatter Plot", key="anim_title")
            
            with col2:
                color_col = st.selectbox("Color by (optional)", options=["None"] + df.columns.tolist(), key="anim_color")
                color_col = None if color_col == "None" else color_col
                
                size_col = st.selectbox("Size by (optional)", options=["None"] + numeric_cols, key="anim_size")
                size_col = None if size_col == "None" else size_col
            
            try:
                # Create animated scatter plot
                if color_col and size_col:
                    fig = px.scatter(
                        df, x=x_col, y=y_col, animation_frame=frame_col,
                        color=color_col, size=size_col,
                        title=title
                    )
                elif color_col:
                    fig = px.scatter(
                        df, x=x_col, y=y_col, animation_frame=frame_col,
                        color=color_col,
                        title=title
                    )
                elif size_col:
                    fig = px.scatter(
                        df, x=x_col, y=y_col, animation_frame=frame_col,
                        size=size_col,
                        title=title
                    )
                else:
                    fig = px.scatter(
                        df, x=x_col, y=y_col, animation_frame=frame_col,
                        title=title
                    )
                
                # Improve animation settings
                fig.update_layout(
                    updatemenus=[{
                        "type": "buttons",
                        "buttons": [
                            {
                                "label": "Play",
                                "method": "animate",
                                "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]
                            },
                            {
                                "label": "Pause",
                                "method": "animate",
                                "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}]
                            }
                        ]
                    }]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_anim_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Animated Scatter",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Animated Scatter",
                            "x_col": x_col,
                            "y_col": y_col,
                            "frame_col": frame_col,
                            "color_col": color_col,
                            "size_col": size_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Animated Scatter Plot to dashboard!")
                
            except Exception as e:
                st.error(f"Error creating Animated Scatter Plot: {str(e)}")
                
        elif custom_chart_type == "Waterfall Chart":
            col1, col2 = st.columns(2)
            
            with col1:
                category_col = st.selectbox("Category column", options=df.columns.tolist(), key="waterfall_cat")
                value_col = st.selectbox("Value column", options=numeric_cols, key="waterfall_val")
                
                title = st.text_input("Chart Title", value="Waterfall Chart", key="waterfall_title")
            
            with col2:
                color_increasing = st.color_picker("Increasing color", value="#26C6DA", key="waterfall_inc_color")
                color_decreasing = st.color_picker("Decreasing color", value="#EF5350", key="waterfall_dec_color")
                color_total = st.color_picker("Total color", value="#66BB6A", key="waterfall_tot_color")
            
            try:
                # Create waterfall chart
                fig = go.Figure(go.Waterfall(
                    name="Waterfall",
                    orientation="v",
                    measure=["relative"] * (len(df) - 1) + ["total"],
                    x=df[category_col],
                    y=df[value_col],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                    increasing={"marker": {"color": color_increasing}},
                    decreasing={"marker": {"color": color_decreasing}},
                    totals={"marker": {"color": color_total}}
                ))
                
                fig.update_layout(
                    title=title,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_waterfall_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Waterfall Chart",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Waterfall Chart",
                            "category_col": category_col,
                            "value_col": value_col,
                            "color_increasing": color_increasing,
                            "color_decreasing": color_decreasing,
                            "color_total": color_total
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Waterfall Chart to dashboard!")
                
            except Exception as e:
                st.error(f"Error creating Waterfall Chart: {str(e)}")
        
        elif custom_chart_type == "Parallel Categories":
            st.write("Parallel Categories visualizes relationships between categorical variables.")
            
            cat_cols = st.multiselect(
                "Select categorical columns",
                options=categorical_cols,
                default=categorical_cols[:min(3, len(categorical_cols))],
                key="parcat_cols"
            )
            
            color_col = st.selectbox("Color by", options=["Count"] + df.columns.tolist(), key="parcat_color")
            
            title = st.text_input("Chart Title", value="Parallel Categories", key="parcat_title")
            
            if len(cat_cols) >= 2:
                try:
                    if color_col == "Count":
                        fig = px.parallel_categories(
                            df, 
                            dimensions=cat_cols,
                            title=title
                        )
                    else:
                        fig = px.parallel_categories(
                            df, 
                            dimensions=cat_cols,
                            color=color_col,
                            title=title
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_parcat_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Parallel Categories",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Parallel Categories",
                                "dimensions": cat_cols,
                                "color_col": color_col if color_col != "Count" else None
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Parallel Categories to dashboard!")
                    
                except Exception as e:
                    st.error(f"Error creating Parallel Categories: {str(e)}")
            else:
                st.warning("Please select at least 2 categorical columns for Parallel Categories.")
        
        elif custom_chart_type == "Ridgeline Plot":
            st.write("Ridgeline plots show distribution of a numeric variable for multiple categories.")
            
            value_col = st.selectbox("Value column (numeric)", options=numeric_cols, key="ridge_value")
            group_col = st.selectbox("Group by column (categorical)", options=categorical_cols, key="ridge_group")
            
            title = st.text_input("Chart Title", value="Ridgeline Plot", key="ridge_title")
            
            try:
                # Get unique categories
                categories = df[group_col].unique()
                
                # Create ridgeline plot
                fig = go.Figure()
                
                # Add traces, one for each category
                for i, category in enumerate(categories):
                    df_cat = df[df[group_col] == category]
                    
                    fig.add_trace(go.Violin(
                        x=df_cat[value_col],
                        y=[i] * len(df_cat),
                        name=str(category),
                        orientation='h',
                        side='positive',
                        width=3,
                        points=False
                    ))
                
                # Update layout
                fig.update_layout(
                    title=title,
                    yaxis=dict(
                        categoryorder='array',
                        categoryarray=list(range(len(categories))),
                        tickvals=list(range(len(categories))),
                        ticktext=categories,
                        title=group_col
                    ),
                    xaxis=dict(title=value_col),
                    height=100 + (len(categories) * 40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_ridge_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Ridgeline Plot",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Ridgeline Plot",
                            "value_col": value_col,
                            "group_col": group_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Ridgeline Plot to dashboard!")
                
            except Exception as e:
                st.error(f"Error creating Ridgeline Plot: {str(e)}")
        
        # Options based on chart type
        if custom_chart_type == "Sunburst Chart":
            st.write("Sunburst charts visualize hierarchical data using concentric circles.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # For sunburst, we need path columns (hierarchical structure)
                path_cols = st.multiselect(
                    "Select hierarchy columns (order matters)",
                    options=df.columns.tolist(),
                    key="sunburst_path"
                )
                
                title = st.text_input("Chart Title", value="Sunburst Chart", key="sunburst_title")
            
            with col2:
                value_col = st.selectbox(
                    "Value column (numeric, optional)",
                    options=["None"] + numeric_cols,
                    key="sunburst_value"
                )
                value_col = None if value_col == "None" else value_col
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="sunburst_color"
                )
                color_col = None if color_col == "None" else color_col
            
            if len(path_cols) >= 2:
                try:
                    fig = visualization_utils.create_sunburst(
                        df,
                        path_cols=path_cols,
                        value_col=value_col,
                        color_col=color_col,
                        title=title
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_sunburst_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Sunburst Chart",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Sunburst Chart",
                                "path_cols": path_cols,
                                "value_col": value_col,
                                "color_col": color_col
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Sunburst Chart to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating sunburst chart: {str(e)}")
            else:
                st.warning("Please select at least 2 hierarchical columns for sunburst chart")
        
        elif custom_chart_type == "Treemap":
            st.write("Treemaps display hierarchical data as nested rectangles.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # For treemap, we need path columns (hierarchical structure)
                path_cols = st.multiselect(
                    "Select hierarchy columns (order matters)",
                    options=df.columns.tolist(),
                    key="treemap_path"
                )
                
                title = st.text_input("Chart Title", value="Treemap", key="treemap_title")
            
            with col2:
                value_col = st.selectbox(
                    "Value column (numeric, determines rectangle size)",
                    options=["None"] + numeric_cols,
                    key="treemap_value"
                )
                value_col = None if value_col == "None" else value_col
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="treemap_color"
                )
                color_col = None if color_col == "None" else color_col
            
            if len(path_cols) >= 1:
                try:
                    fig = visualization_utils.create_treemap(
                        df,
                        path_cols=path_cols,
                        value_col=value_col,
                        color_col=color_col,
                        title=title
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save button for dashboard
                    if st.button("Add to Dashboard", key="add_treemap_chart"):
                        if 'visualizations' not in st.session_state:
                            st.session_state.visualizations = []
                        
                        vis_info = {
                            "type": "Treemap",
                            "fig": fig,
                            "title": title,
                            "params": {
                                "chart_type": "Treemap",
                                "path_cols": path_cols,
                                "value_col": value_col,
                                "color_col": color_col
                            }
                        }
                        
                        st.session_state.visualizations.append(vis_info)
                        st.success("Added Treemap to dashboard!")
                
                except Exception as e:
                    st.error(f"Error creating treemap: {str(e)}")
            else:
                st.warning("Please select at least 1 hierarchical column for treemap")
        
        elif custom_chart_type == "3D Scatter Plot":
            st.write("3D Scatter Plots show the relationship between three numeric variables.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis column", options=numeric_cols, key="scatter3d_x")
                y_col = st.selectbox("Y-axis column", options=numeric_cols, key="scatter3d_y")
                z_col = st.selectbox("Z-axis column", options=numeric_cols, key="scatter3d_z")
                
                title = st.text_input("Chart Title", value="3D Scatter Plot", key="scatter3d_title")
            
            with col2:
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="scatter3d_color"
                )
                color_col = None if color_col == "None" else color_col
                
                size_col = st.selectbox(
                    "Size by (numeric, optional)",
                    options=["None"] + numeric_cols,
                    key="scatter3d_size"
                )
                size_col = None if size_col == "None" else size_col
            
            try:
                fig = visualization_utils.create_3d_scatter(
                    df,
                    x_col=x_col,
                    y_col=y_col,
                    z_col=z_col,
                    color_col=color_col,
                    size_col=size_col,
                    title=title
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_3d_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "3D Scatter Plot",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "3D Scatter Plot",
                            "x_col": x_col,
                            "y_col": y_col,
                            "z_col": z_col,
                            "color_col": color_col,
                            "size_col": size_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added 3D Scatter Plot to dashboard!")
            
            except Exception as e:
                st.error(f"Error creating 3D scatter plot: {str(e)}")
        
        elif custom_chart_type == "Candlestick Chart":
            st.write("Candlestick charts are typically used for financial data showing open, high, low, and close values.")
            
            # Check if appropriate columns exist
            required_columns = ['open', 'high', 'low', 'close']
            has_required = all(any(req in col.lower() for col in df.columns) for req in required_columns)
            
            if not has_required:
                st.warning("Candlestick charts require columns for: open, high, low, and close values. Your data might not have these.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                date_col = st.selectbox(
                    "Date/Time column",
                    options=df.columns.tolist(),
                    key="candle_date"
                )
                
                open_col = st.selectbox(
                    "Open column",
                    options=numeric_cols,
                    key="candle_open"
                )
                
                high_col = st.selectbox(
                    "High column",
                    options=numeric_cols,
                    key="candle_high"
                )
            
            with col2:
                low_col = st.selectbox(
                    "Low column",
                    options=numeric_cols,
                    key="candle_low"
                )
                
                close_col = st.selectbox(
                    "Close column",
                    options=numeric_cols,
                    key="candle_close"
                )
                
                title = st.text_input("Chart Title", value="Candlestick Chart", key="candle_title")
            
            try:
                fig = visualization_utils.create_candlestick(
                    df,
                    date_col=date_col,
                    open_col=open_col,
                    high_col=high_col,
                    low_col=low_col,
                    close_col=close_col,
                    title=title
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_candle_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Candlestick Chart",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Candlestick Chart",
                            "date_col": date_col,
                            "open_col": open_col,
                            "high_col": high_col,
                            "low_col": low_col,
                            "close_col": close_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Candlestick Chart to dashboard!")
            
            except Exception as e:
                st.error(f"Error creating candlestick chart: {str(e)}")
        
        elif custom_chart_type == "Funnel Chart":
            st.write("Funnel charts show values through different stages of a process.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                stage_col = st.selectbox(
                    "Stage/Category column",
                    options=df.columns.tolist(),
                    key="funnel_stage"
                )
                
                value_col = st.selectbox(
                    "Value column (numeric)",
                    options=numeric_cols,
                    key="funnel_value"
                )
            
            with col2:
                title = st.text_input("Chart Title", value="Funnel Chart", key="funnel_title")
                
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=["None"] + df.columns.tolist(),
                    key="funnel_color"
                )
                color_col = None if color_col == "None" else color_col
            
            try:
                fig = visualization_utils.create_funnel_chart(
                    df,
                    stage_col=stage_col,
                    value_col=value_col,
                    color_col=color_col,
                    title=title
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save button for dashboard
                if st.button("Add to Dashboard", key="add_funnel_chart"):
                    if 'visualizations' not in st.session_state:
                        st.session_state.visualizations = []
                    
                    vis_info = {
                        "type": "Funnel Chart",
                        "fig": fig,
                        "title": title,
                        "params": {
                            "chart_type": "Funnel Chart",
                            "stage_col": stage_col,
                            "value_col": value_col,
                            "color_col": color_col
                        }
                    }
                    
                    st.session_state.visualizations.append(vis_info)
                    st.success("Added Funnel Chart to dashboard!")
            
            except Exception as e:
                st.error(f"Error creating funnel chart: {str(e)}")
    
    # Show button to go to dashboard
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Go to Dashboard", type="primary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    
    with col2:
        if st.button("Back to Data Cleaning"):
            st.session_state.current_page = "Clean Data"
            st.rerun()
