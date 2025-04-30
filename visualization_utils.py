import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

def create_bar_chart(df, x_col, y_col, color_col=None, title=None, is_horizontal=False, template="plotly"):
    """
    Create a bar chart using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        is_horizontal (bool): Whether to create a horizontal bar chart
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    if is_horizontal:
        fig = px.bar(
            df, y=x_col, x=y_col,
            color=color_col,
            title=title,
            template=template,
            orientation='h'
        )
    else:
        fig = px.bar(
            df, x=x_col, y=y_col,
            color=color_col,
            title=title,
            template=template
        )
    
    return fig

def create_line_chart(df, x_col, y_col, color_col=None, title=None, template="plotly"):
    """
    Create a line chart using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.line(
        df, x=x_col, y=y_col,
        color=color_col,
        title=title,
        template=template
    )
    
    return fig

def create_pie_chart(df, label_col, value_col, title=None, template="plotly"):
    """
    Create a pie chart using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        label_col (str): Column for slice labels
        value_col (str): Column for slice values
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    # Group by label column and sum values
    grouped_df = df.groupby(label_col)[value_col].sum().reset_index()
    
    fig = px.pie(
        grouped_df, names=label_col, values=value_col,
        title=title,
        template=template
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, color_col=None, title=None, template="plotly"):
    """
    Create a scatter plot using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter(
        df, x=x_col, y=y_col,
        color=color_col,
        title=title,
        template=template
    )
    
    return fig

def create_bubble_chart(df, x_col, y_col, size_col, color_col=None, title=None, template="plotly"):
    """
    Create a bubble chart using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        size_col (str): Column for bubble size
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter(
        df, x=x_col, y=y_col,
        size=size_col,
        color=color_col,
        title=title,
        template=template
    )
    
    return fig

def create_area_chart(df, x_col, y_col, color_col=None, title=None, template="plotly"):
    """
    Create an area chart using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.area(
        df, x=x_col, y=y_col,
        color=color_col,
        title=title,
        template=template
    )
    
    return fig

def create_histogram(df, value_col, bins=20, color_col=None, title=None, template="plotly"):
    """
    Create a histogram using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        value_col (str): Column for values
        bins (int): Number of bins
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.histogram(
        df, x=value_col,
        color=color_col,
        nbins=bins,
        title=title,
        template=template
    )
    
    return fig

def create_box_plot(df, value_col, group_col=None, color_col=None, title=None, template="plotly"):
    """
    Create a box plot using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        value_col (str): Column for values
        group_col (str, optional): Column for grouping
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.box(
        df, y=value_col, x=group_col,
        color=color_col,
        title=title,
        template=template,
        points="all"  # Show all points
    )
    
    return fig

def create_violin_plot(df, value_col, group_col=None, color_col=None, title=None, template="plotly"):
    """
    Create a violin plot using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        value_col (str): Column for values
        group_col (str, optional): Column for grouping
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.violin(
        df, y=value_col, x=group_col,
        color=color_col,
        title=title,
        template=template,
        box=True,  # Show box plot inside the violin
        points="all"  # Show all points
    )
    
    return fig

def create_density_plot(df, value_col, color_col=None, title=None, template="plotly"):
    """
    Create a density plot (KDE) using Plotly Express.
    
    Args:
        df (DataFrame): Input DataFrame
        value_col (str): Column for values
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        template (str): Plotly template name
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.density_contour(
        df, x=value_col,
        color=color_col,
        title=title,
        template=template
    )
    
    # Add histogram on the marginal
    fig.update_traces(histnorm="probability density")
    
    return fig

def create_correlation_heatmap(df, columns=None, method="pearson", colorscale="RdBu_r", title=None):
    """
    Create a correlation heatmap.
    
    Args:
        df (DataFrame): Input DataFrame
        columns (list, optional): List of columns to include in the correlation matrix
        method (str): Correlation method (pearson, spearman, kendall)
        colorscale (str): Colorscale for the heatmap
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    # Select columns if specified
    if columns is not None:
        df_corr = df[columns].copy()
    else:
        df_corr = df.select_dtypes(include=[np.number]).copy()
    
    # Calculate correlation matrix
    corr_matrix = df_corr.corr(method=method)
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        text_auto=True,
        color_continuous_scale=colorscale,
        title=title or f"Correlation Matrix ({method})"
    )
    
    return fig

def create_scatter_matrix(df, dimensions, color=None, diagonal_visible=True, title=None, diagonal_type="histogram"):
    """
    Create a scatter matrix.
    
    Args:
        df (DataFrame): Input DataFrame
        dimensions (list): List of columns to include
        color (str, optional): Column for color encoding
        diagonal_visible (bool): Whether to show diagonal plots
        title (str, optional): Chart title
        diagonal_type (str): Type of plot to show on diagonal ('histogram', 'box', 'violin', 'rug')
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter_matrix(
        df, dimensions=dimensions,
        color=color,
        title=title,
        opacity=0.7
    )
    
    # Customize diagonal plots
    if diagonal_visible:
        if diagonal_type == "histogram":
            pass  # Default is histogram
        else:
            # Hide default histograms
            for i in range(len(dimensions)):
                fig.data[i*len(dimensions) + i].visible = False
                
                # Add custom diagonal plots
                for i, dim in enumerate(dimensions):
                    row, col = i+1, i+1
                    
                    if diagonal_type == "box":
                        fig.add_trace(
                            go.Box(y=df[dim], name=dim),
                            row=row, col=col
                        )
                    elif diagonal_type == "violin":
                        fig.add_trace(
                            go.Violin(y=df[dim], name=dim, box_visible=True),
                            row=row, col=col
                        )
                    elif diagonal_type == "rug":
                        fig.add_trace(
                            go.Box(y=df[dim], name=dim, boxpoints='all', jitter=0.7, pointpos=0),
                            row=row, col=col
                        )
    else:
        # Hide diagonal plots
        for i in range(len(dimensions)):
            fig.data[i*len(dimensions) + i].visible = False
    
    return fig

def create_parallel_coordinates(df, dimensions, color, colorscale="viridis", title=None):
    """
    Create a parallel coordinates plot.
    
    Args:
        df (DataFrame): Input DataFrame
        dimensions (list): List of columns to include
        color (str): Column for color encoding
        colorscale (str): Colorscale for the color encoding
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    # Create dimensions list
    dim_list = []
    
    for dim in dimensions:
        dim_dict = {
            "label": dim,
            "values": df[dim]
        }
        
        # Add range for numeric columns
        if pd.api.types.is_numeric_dtype(df[dim]):
            dim_dict["range"] = [df[dim].min(), df[dim].max()]
        
        dim_list.append(dim_dict)
    
    # Create figure
    fig = go.Figure(data=
        go.Parcoords(
            line=dict(
                color=df[color],
                colorscale=colorscale,
                showscale=True
            ),
            dimensions=dim_list
        )
    )
    
    # Update layout
    fig.update_layout(
        title=title or "Parallel Coordinates Plot"
    )
    
    return fig

def create_radar_chart(df, category_col, value_cols, selected_categories=None, agg_func='mean', scale_values=True, title=None):
    """
    Create a radar chart.
    
    Args:
        df (DataFrame): Input DataFrame
        category_col (str): Column with categories
        value_cols (list): List of columns with values
        selected_categories (list, optional): List of categories to include
        agg_func (str): Aggregation function for multiple values per category
        scale_values (bool): Whether to scale values to 0-1 range
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    # Filter categories if specified
    if selected_categories:
        df_radar = df[df[category_col].isin(selected_categories)].copy()
    else:
        df_radar = df.copy()
    
    # Aggregate data
    df_agg = df_radar.groupby(category_col)[value_cols].agg(agg_func).reset_index()
    
    # Scale values if requested
    if scale_values:
        for col in value_cols:
            min_val = df_agg[col].min()
            max_val = df_agg[col].max()
            if max_val > min_val:
                df_agg[col] = (df_agg[col] - min_val) / (max_val - min_val)
    
    # Create radar chart
    fig = go.Figure()
    
    # Add a trace for each category
    for i, category in enumerate(df_agg[category_col]):
        values = df_agg.loc[i, value_cols].tolist()
        # Close the loop by repeating the first value
        values.append(values[0])
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=value_cols + [value_cols[0]],  # Close the loop
            fill='toself',
            name=str(category)
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1] if scale_values else None
            )
        ),
        title=title or "Radar Chart",
        showlegend=True
    )
    
    return fig

def create_choropleth_map(df, location_col, value_col, scope="world", locationmode="ISO-3", colorscale="Blues", title=None):
    """
    Create a choropleth map.
    
    Args:
        df (DataFrame): Input DataFrame
        location_col (str): Column with location names/codes
        value_col (str): Column with values
        scope (str): Map scope (world, usa, europe, asia, africa, north america, south america)
        locationmode (str): Mode for interpreting locations (ISO-3, country names, USA-states)
        colorscale (str): Colorscale for the map
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.choropleth(
        df,
        locations=location_col,
        color=value_col,
        scope=scope,
        locationmode=locationmode,
        color_continuous_scale=colorscale,
        title=title or f"{value_col} by {location_col}"
    )
    
    return fig

def create_scatter_geo(df, lat_col, lon_col, color_col=None, scope="world", title=None):
    """
    Create a scatter geo plot.
    
    Args:
        df (DataFrame): Input DataFrame
        lat_col (str): Column with latitude
        lon_col (str): Column with longitude
        color_col (str, optional): Column for color encoding
        scope (str): Map scope
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter_geo(
        df,
        lat=lat_col,
        lon=lon_col,
        color=color_col,
        scope=scope,
        title=title or "Geographic Scatter Plot"
    )
    
    return fig

def create_bubble_map(df, lat_col, lon_col, size_col, color_col=None, scope="world", title=None):
    """
    Create a bubble map.
    
    Args:
        df (DataFrame): Input DataFrame
        lat_col (str): Column with latitude
        lon_col (str): Column with longitude
        size_col (str): Column for bubble size
        color_col (str, optional): Column for color encoding
        scope (str): Map scope
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter_geo(
        df,
        lat=lat_col,
        lon=lon_col,
        size=size_col,
        color=color_col,
        scope=scope,
        title=title or "Geographic Bubble Map"
    )
    
    return fig

def create_sunburst(df, path_cols, value_col=None, color_col=None, title=None):
    """
    Create a sunburst chart.
    
    Args:
        df (DataFrame): Input DataFrame
        path_cols (list): List of columns defining the hierarchical path
        value_col (str, optional): Column for values
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.sunburst(
        df,
        path=path_cols,
        values=value_col,
        color=color_col,
        title=title or "Sunburst Chart"
    )
    
    return fig

def create_treemap(df, path_cols, value_col=None, color_col=None, title=None):
    """
    Create a treemap.
    
    Args:
        df (DataFrame): Input DataFrame
        path_cols (list): List of columns defining the hierarchical path
        value_col (str, optional): Column for values
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.treemap(
        df,
        path=path_cols,
        values=value_col,
        color=color_col,
        title=title or "Treemap"
    )
    
    return fig

def create_3d_scatter(df, x_col, y_col, z_col, color_col=None, size_col=None, title=None):
    """
    Create a 3D scatter plot.
    
    Args:
        df (DataFrame): Input DataFrame
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        z_col (str): Column for z-axis
        color_col (str, optional): Column for color encoding
        size_col (str, optional): Column for point size
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = px.scatter_3d(
        df,
        x=x_col,
        y=y_col,
        z=z_col,
        color=color_col,
        size=size_col,
        title=title or "3D Scatter Plot"
    )
    
    return fig

def create_candlestick(df, date_col, open_col, high_col, low_col, close_col, title=None):
    """
    Create a candlestick chart.
    
    Args:
        df (DataFrame): Input DataFrame
        date_col (str): Column with dates
        open_col (str): Column with opening values
        high_col (str): Column with high values
        low_col (str): Column with low values
        close_col (str): Column with closing values
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    fig = go.Figure(data=[go.Candlestick(
        x=df[date_col],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col]
    )])
    
    # Update layout
    fig.update_layout(
        title=title or "Candlestick Chart",
        xaxis_title=date_col,
        yaxis_title="Price",
        xaxis_rangeslider_visible=True
    )
    
    return fig

def create_funnel_chart(df, stage_col, value_col, color_col=None, title=None):
    """
    Create a funnel chart.
    
    Args:
        df (DataFrame): Input DataFrame
        stage_col (str): Column with stage names
        value_col (str): Column with values
        color_col (str, optional): Column for color encoding
        title (str, optional): Chart title
        
    Returns:
        Figure: Plotly figure object
    """
    # Group by stage and sum values
    grouped_df = df.groupby(stage_col)[value_col].sum().reset_index()
    
    # Sort by value in descending order
    grouped_df = grouped_df.sort_values(value_col, ascending=False)
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=grouped_df[stage_col],
        x=grouped_df[value_col],
        textinfo="value+percent initial"
    ))
    
    # Update layout
    fig.update_layout(
        title=title or "Funnel Chart",
    )
    
    return fig
