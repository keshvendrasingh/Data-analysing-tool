import streamlit as st
import pandas as pd
import io
import plotly.io as pio
import json
import datetime
import base64

def show():
    st.header("Export Your Results")
    
    # Check if data is available
    if st.session_state.cleaned_data is None:
        st.warning("No data available. Please import and clean data first.")
        if st.button("Go to Import Data"):
            st.session_state.current_page = "Import Data"
            st.rerun()
        return
    
    # Display the data image
    st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3", use_column_width=True)  # Lukas Blazek business intelligence image
    
    df = st.session_state.cleaned_data
    
    # Create tabs for different export options
    data_tab, charts_tab, report_tab = st.tabs([
        "📁 Export Data", 
        "📊 Export Charts", 
        "📝 Generate Report"
    ])
    
    # Export Data Tab
    with data_tab:
        st.subheader("Export Your Data")
        
        # Show data preview
        st.write("**Data Preview:**")
        st.dataframe(df.head(5))
        
        # Format options
        st.write("**Export Format Options:**")
        export_format = st.selectbox(
            "Select export format",
            options=["CSV", "Excel", "JSON", "HTML", "Pickle"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Options for CSV
            if export_format == "CSV":
                delimiter = st.selectbox(
                    "Delimiter",
                    options=[",", ";", "\t", "|"],
                    index=0
                )
                
                encoding = st.selectbox(
                    "Encoding",
                    options=["utf-8", "latin-1", "iso-8859-1", "cp1252"],
                    index=0
                )
                
                include_index = st.checkbox("Include row index", value=False)
            
            # Options for Excel
            elif export_format == "Excel":
                sheet_name = st.text_input("Sheet name", value="InsightVista_Data")
                include_index = st.checkbox("Include row index", value=False)
            
            # Options for JSON
            elif export_format == "JSON":
                orient = st.selectbox(
                    "JSON orientation",
                    options=["records", "columns", "index", "split", "table"],
                    index=0
                )
                
                indent = st.checkbox("Pretty print (indent)", value=True)
            
            # Options for HTML
            elif export_format == "HTML":
                include_index = st.checkbox("Include row index", value=True)
                table_id = st.text_input("Table ID", value="insight_vista_table")
                
            # Options for Pickle
            elif export_format == "Pickle":
                compression = st.selectbox(
                    "Compression",
                    options=["None", "gzip", "bz2", "zip", "xz"],
                    index=0
                )
                compression = None if compression == "None" else compression
        
        with col2:
            # Additional options
            st.write("**Selection Options:**")
            
            # Option to export all data or just a subset
            export_option = st.radio(
                "What data to export?",
                options=["All data", "Current page of data", "Selected columns"]
            )
            
            # If selected columns option is chosen
            if export_option == "Selected columns":
                selected_columns = st.multiselect(
                    "Select columns to export",
                    options=df.columns.tolist(),
                    default=df.columns.tolist()
                )
            else:
                selected_columns = df.columns.tolist()
            
            # If current page option is chosen
            if export_option == "Current page of data":
                rows_per_page = st.number_input("Rows per page", min_value=1, max_value=1000, value=100)
                page_number = st.number_input("Page number", min_value=1, max_value=max(1, len(df) // rows_per_page + 1), value=1)
                
                start_idx = (page_number - 1) * rows_per_page
                end_idx = min(start_idx + rows_per_page, len(df))
                
                export_df = df.iloc[start_idx:end_idx][selected_columns]
            else:
                export_df = df[selected_columns]
        
        # Generate export
        if st.button("Generate Export", type="primary"):
            try:
                if export_format == "CSV":
                    buffer = io.StringIO()
                    export_df.to_csv(buffer, sep=delimiter, index=include_index, encoding=encoding)
                    buffer.seek(0)
                    export_data = buffer.getvalue()
                    file_extension = "csv"
                    mime_type = "text/csv"
                
                elif export_format == "Excel":
                    buffer = io.BytesIO()
                    export_df.to_excel(buffer, sheet_name=sheet_name, index=include_index, engine="xlsxwriter")
                    buffer.seek(0)
                    export_data = buffer.getvalue()
                    file_extension = "xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                elif export_format == "JSON":
                    indent_value = 4 if indent else None
                    export_data = export_df.to_json(orient=orient, indent=indent_value)
                    file_extension = "json"
                    mime_type = "application/json"
                
                elif export_format == "HTML":
                    export_data = export_df.to_html(index=include_index, table_id=table_id)
                    file_extension = "html"
                    mime_type = "text/html"
                
                elif export_format == "Pickle":
                    buffer = io.BytesIO()
                    export_df.to_pickle(buffer, compression=compression)
                    buffer.seek(0)
                    export_data = buffer.getvalue()
                    file_extension = "pkl"
                    mime_type = "application/octet-stream"
                
                # Generate filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"insightvista_export_{timestamp}.{file_extension}"
                
                # Offer download button
                if export_format in ["CSV", "JSON", "HTML"]:
                    st.download_button(
                        label=f"Download {export_format} File",
                        data=export_data,
                        file_name=filename,
                        mime=mime_type
                    )
                else:  # Excel and Pickle are binary
                    st.download_button(
                        label=f"Download {export_format} File",
                        data=export_data,
                        file_name=filename,
                        mime=mime_type
                    )
                
                # Display success message
                st.success(f"Export generated successfully! Click the download button above to save the {export_format} file.")
                
            except Exception as e:
                st.error(f"Error generating export: {str(e)}")
    
    # Export Charts Tab
    with charts_tab:
        st.subheader("Export Your Charts")
        
        # Check if visualizations exist
        if not st.session_state.visualizations:
            st.info("You haven't created any visualizations yet. Go to the Visualize page to create charts for export.")
            if st.button("Go to Visualization"):
                st.session_state.current_page = "Visualize"
                st.rerun()
        else:
            # Select chart to export
            chart_options = [f"{i+1}. {vis['title']}" for i, vis in enumerate(st.session_state.visualizations)]
            selected_chart = st.selectbox("Select chart to export", options=chart_options)
            chart_index = int(selected_chart.split('.')[0]) - 1
            
            # Show selected chart
            st.plotly_chart(st.session_state.visualizations[chart_index]["fig"], use_container_width=True)
            
            # Export format options
            export_format = st.selectbox(
                "Select image format",
                options=["PNG", "JPEG", "SVG", "PDF", "HTML"],
                index=0,
                key="chart_export_format"
            )
            
            # Image quality and sizing
            col1, col2 = st.columns(2)
            
            with col1:
                width = st.number_input("Width (pixels)", min_value=400, max_value=2000, value=800)
                if export_format in ["PNG", "JPEG"]:
                    scale = st.number_input("Scale factor", min_value=1, max_value=5, value=2)
                else:
                    scale = 1
            
            with col2:
                height = st.number_input("Height (pixels)", min_value=300, max_value=2000, value=600)
                if export_format == "JPEG":
                    quality = st.slider("JPEG Quality", min_value=10, max_value=100, value=90)
                else:
                    quality = 90
            
            # Generate chart export
            if st.button("Export Chart", key="export_chart_button"):
                try:
                    fig = st.session_state.visualizations[chart_index]["fig"]
                    chart_title = st.session_state.visualizations[chart_index]["title"]
                    
                    # Sanitize title for filename
                    sanitized_title = "".join([c if c.isalnum() else "_" for c in chart_title])
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{sanitized_title}_{timestamp}"
                    
                    if export_format == "PNG":
                        img_bytes = pio.to_image(
                            fig, format="png", width=width, height=height, scale=scale
                        )
                        mime_type = "image/png"
                        file_ext = "png"
                    
                    elif export_format == "JPEG":
                        img_bytes = pio.to_image(
                            fig, format="jpeg", width=width, height=height, scale=scale, quality=quality
                        )
                        mime_type = "image/jpeg"
                        file_ext = "jpg"
                    
                    elif export_format == "SVG":
                        img_bytes = pio.to_image(
                            fig, format="svg", width=width, height=height
                        )
                        mime_type = "image/svg+xml"
                        file_ext = "svg"
                    
                    elif export_format == "PDF":
                        img_bytes = pio.to_image(
                            fig, format="pdf", width=width, height=height
                        )
                        mime_type = "application/pdf"
                        file_ext = "pdf"
                    
                    elif export_format == "HTML":
                        html_str = pio.to_html(
                            fig, include_plotlyjs="cdn", full_html=True, 
                            config={"responsive": True}
                        )
                        mime_type = "text/html"
                        file_ext = "html"
                        img_bytes = html_str.encode()
                    
                    # Offer download button
                    st.download_button(
                        label=f"Download {chart_title} as {export_format}",
                        data=img_bytes,
                        file_name=f"{filename}.{file_ext}",
                        mime=mime_type
                    )
                    
                    st.success(f"Chart exported successfully! Click the download button above to save the file.")
                    
                except Exception as e:
                    st.error(f"Error exporting chart: {str(e)}")
            
            # Export all charts
            st.divider()
            st.subheader("Export All Charts")
            
            export_all_format = st.selectbox(
                "Select format for all charts",
                options=["PNG", "PDF", "HTML"],
                index=0,
                key="export_all_format"
            )
            
            if st.button("Export All Charts", key="export_all_button"):
                try:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    if export_all_format == "HTML":
                        # Generate a full HTML report with all charts
                        html_parts = ["<html><head><title>InsightVista Chart Export</title>",
                                     "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
                                     "<style>body {font-family: Arial, sans-serif; margin: 20px;}",
                                     ".chart-container {margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;}",
                                     "h1 {color: #4F8BF9;} h2 {color: #4F8BF9;}</style></head><body>",
                                     f"<h1>InsightVista Chart Export</h1><p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"]
                        
                        for i, vis in enumerate(st.session_state.visualizations):
                            html_parts.append(f"<div class='chart-container'><h2>{vis['title']}</h2>")
                            chart_html = pio.to_html(vis["fig"], include_plotlyjs=False, full_html=False)
                            html_parts.append(chart_html)
                            html_parts.append("</div>")
                        
                        html_parts.append("</body></html>")
                        html_report = "".join(html_parts)
                        
                        # Offer download
                        st.download_button(
                            label="Download All Charts as HTML Report",
                            data=html_report,
                            file_name=f"insightvista_charts_{timestamp}.html",
                            mime="text/html"
                        )
                    
                    elif export_all_format == "PDF":
                        st.warning("Exporting multiple charts to a single PDF is currently in development. Please export individual charts or use the HTML report option.")
                    
                    elif export_all_format == "PNG":
                        st.warning("Exporting all charts as individual PNG files is currently in development. Please export charts individually.")
                    
                    st.success("Export completed! Click the download button above to save your charts.")
                    
                except Exception as e:
                    st.error(f"Error exporting all charts: {str(e)}")
    
    # Generate Report Tab
    with report_tab:
        st.subheader("Generate Complete Report")
        
        # Report options
        st.write("**Report Content Options:**")
        
        include_data_profile = st.checkbox("Include Data Profile", value=True)
        include_visualizations = st.checkbox("Include Visualizations", value=True)
        include_insights = st.checkbox("Include Insights", value=True)
        
        # Report metadata
        st.write("**Report Metadata:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_title = st.text_input("Report Title", value="InsightVista Data Analysis Report")
            author_name = st.text_input("Author/Company Name", value="")
        
        with col2:
            date_format = st.selectbox(
                "Date Format",
                options=["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY", "Month DD, YYYY"],
                index=0
            )
            
            # Convert date format selection to strftime format
            date_format_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
                "Month DD, YYYY": "%B %d, %Y"
            }
            
            today_date = datetime.datetime.now().strftime(date_format_map[date_format])
            report_date = st.text_input("Report Date", value=today_date)
        
        # Report format
        report_format = st.selectbox(
            "Report Format",
            options=["HTML", "PDF"],
            index=0
        )
        
        # Generate the report
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                try:
                    report_html = []
                    
                    # Report header
                    report_html.append(f"""
                    <html>
                    <head>
                        <title>{report_title}</title>
                        <script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 30px; line-height: 1.6; color: #333; }}
                            .header {{ text-align: center; margin-bottom: 40px; }}
                            .section {{ margin-top: 30px; margin-bottom: 30px; }}
                            .section-title {{ color: #4F8BF9; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                            th, td {{ text-align: left; padding: 12px; }}
                            th {{ background-color: #f2f2f2; }}
                            tr:nth-child(even) {{ background-color: #f9f9f9; }}
                            .chart-container {{ margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                            .insight-box {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4F8BF9; margin-bottom: 20px; }}
                            .footer {{ margin-top: 50px; text-align: center; font-size: 0.9em; color: #777; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>{report_title}</h1>
                            <p>Generated on {report_date}</p>
                            {f"<p>By {author_name}</p>" if author_name else ""}
                        </div>
                    """)
                    
                    # Table of contents
                    report_html.append("""
                        <div class="section">
                            <h2 class="section-title">Table of Contents</h2>
                            <ol>
                    """)
                    
                    toc_items = []
                    toc_count = 1
                    
                    if include_data_profile:
                        toc_items.append(f"<li><a href='#section-{toc_count}'>Data Overview</a></li>")
                        toc_count += 1
                    
                    if include_visualizations and st.session_state.visualizations:
                        toc_items.append(f"<li><a href='#section-{toc_count}'>Data Visualizations</a></li>")
                        toc_count += 1
                    
                    if include_insights:
                        toc_items.append(f"<li><a href='#section-{toc_count}'>Data Insights</a></li>")
                        toc_count += 1
                    
                    report_html.append("".join(toc_items))
                    report_html.append("</ol></div>")
                    
                    # Section counter
                    section_count = 1
                    
                    # Data Profile section
                    if include_data_profile:
                        report_html.append(f"""
                            <div class="section" id="section-{section_count}">
                                <h2 class="section-title">1. Data Overview</h2>
                                <p>This section provides an overview of the dataset used in this analysis.</p>
                                
                                <h3>Dataset Summary</h3>
                                <ul>
                                    <li><strong>Rows:</strong> {df.shape[0]:,}</li>
                                    <li><strong>Columns:</strong> {df.shape[1]}</li>
                                    <li><strong>Numeric Columns:</strong> {len(df.select_dtypes(include=np.number).columns)}</li>
                                    <li><strong>Categorical Columns:</strong> {len(df.select_dtypes(exclude=np.number).columns)}</li>
                                    <li><strong>Missing Values:</strong> {df.isna().sum().sum():,} ({df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100:.2f}%)</li>
                                </ul>
                                
                                <h3>Data Preview</h3>
                        """)
                        
                        # Add data preview
                        data_preview = df.head(5).to_html(index=True, classes="table table-striped")
                        report_html.append(data_preview)
                        
                        # Add column information
                        report_html.append("<h3>Column Information</h3>")
                        
                        # Create DataFrame with column info
                        column_info = []
                        for col in df.columns:
                            col_type = str(df[col].dtype)
                            missing = df[col].isna().sum()
                            missing_pct = missing / len(df) * 100
                            unique = df[col].nunique()
                            unique_pct = unique / len(df) * 100
                            
                            column_info.append({
                                "Column": col,
                                "Type": col_type,
                                "Missing Values": f"{missing:,} ({missing_pct:.2f}%)",
                                "Unique Values": f"{unique:,} ({unique_pct:.2f}%)"
                            })
                        
                        column_df = pd.DataFrame(column_info)
                        column_table = column_df.to_html(index=False, classes="table table-striped")
                        report_html.append(column_table)
                        
                        report_html.append("</div>")
                        section_count += 1
                    
                    # Visualizations section
                    if include_visualizations and st.session_state.visualizations:
                        report_html.append(f"""
                            <div class="section" id="section-{section_count}">
                                <h2 class="section-title">2. Data Visualizations</h2>
                                <p>This section contains the visualizations created during the analysis.</p>
                        """)
                        
                        # Add each visualization
                        for i, vis in enumerate(st.session_state.visualizations):
                            report_html.append(f"""
                                <div class="chart-container">
                                    <h3>{vis['title']}</h3>
                            """)
                            
                            # Convert Plotly figure to HTML
                            chart_html = pio.to_html(vis["fig"], include_plotlyjs=False, full_html=False)
                            report_html.append(chart_html)
                            
                            # Add visualization description if available
                            vis_type = vis["type"]
                            report_html.append(f"<p><em>Chart type: {vis_type}</em></p>")
                            
                            report_html.append("</div>")
                        
                        report_html.append("</div>")
                        section_count += 1
                    
                    # Insights section
                    if include_insights:
                        report_html.append(f"""
                            <div class="section" id="section-{section_count}">
                                <h2 class="section-title">3. Data Insights</h2>
                                <p>This section highlights key insights and findings from the data analysis.</p>
                        """)
                        
                        # Numeric insights
                        if len(df.select_dtypes(include=np.number).columns) > 0:
                            report_html.append("<h3>Numeric Column Insights</h3>")
                            
                            # Get basic stats
                            numeric_df = df.select_dtypes(include=np.number)
                            for col in numeric_df.columns[:5]:  # Limit to first 5 numeric columns
                                report_html.append(f"""
                                    <div class="insight-box">
                                        <h4>{col}</h4>
                                        <ul>
                                            <li>Range: {numeric_df[col].min():.2f} to {numeric_df[col].max():.2f}</li>
                                            <li>Average: {numeric_df[col].mean():.2f}</li>
                                            <li>Median: {numeric_df[col].median():.2f}</li>
                                            <li>Standard Deviation: {numeric_df[col].std():.2f}</li>
                                        </ul>
                                """)
                                
                                # Add distribution information
                                skewness = numeric_df[col].skew()
                                if abs(skewness) < 0.5:
                                    report_html.append("<p>The distribution is approximately symmetric.</p>")
                                elif skewness < 0:
                                    report_html.append("<p>The distribution is negatively skewed (left-tailed).</p>")
                                else:
                                    report_html.append("<p>The distribution is positively skewed (right-tailed).</p>")
                                
                                report_html.append("</div>")
                        
                        # Categorical insights
                        categorical_df = df.select_dtypes(exclude=np.number)
                        if not categorical_df.empty:
                            report_html.append("<h3>Categorical Column Insights</h3>")
                            
                            for col in categorical_df.columns[:5]:  # Limit to first 5 categorical columns
                                # Skip if too many unique values
                                if categorical_df[col].nunique() > 20:
                                    continue
                                    
                                value_counts = categorical_df[col].value_counts().head(5)
                                value_percents = categorical_df[col].value_counts(normalize=True).head(5) * 100
                                
                                report_html.append(f"""
                                    <div class="insight-box">
                                        <h4>{col}</h4>
                                        <p>Top values:</p>
                                        <ul>
                                """)
                                
                                for val, count, pct in zip(value_counts.index, value_counts, value_percents):
                                    report_html.append(f"<li>{val}: {count:,} ({pct:.1f}%)</li>")
                                
                                report_html.append(f"""
                                        </ul>
                                        <p>This column has {categorical_df[col].nunique()} unique values.</p>
                                    </div>
                                """)
                        
                        # Correlation insights
                        if len(df.select_dtypes(include=np.number).columns) >= 2:
                            report_html.append("<h3>Correlation Insights</h3>")
                            
                            # Calculate correlations
                            corr_matrix = df.select_dtypes(include=np.number).corr()
                            
                            # Find strong correlations
                            strong_correlations = []
                            for i in range(len(corr_matrix.columns)):
                                for j in range(i):
                                    if abs(corr_matrix.iloc[i, j]) > 0.7:  # Threshold for strong correlation
                                        strong_correlations.append({
                                            'col1': corr_matrix.columns[i],
                                            'col2': corr_matrix.columns[j],
                                            'corr': corr_matrix.iloc[i, j]
                                        })
                            
                            if strong_correlations:
                                report_html.append("<div class='insight-box'>")
                                report_html.append("<h4>Strong Correlations</h4>")
                                report_html.append("<ul>")
                                
                                for corr in strong_correlations:
                                    direction = "positive" if corr['corr'] > 0 else "negative"
                                    report_html.append(f"<li><strong>{corr['col1']}</strong> and <strong>{corr['col2']}</strong> have a {direction} correlation of {corr['corr']:.2f}</li>")
                                
                                report_html.append("</ul>")
                                report_html.append("</div>")
                            else:
                                report_html.append("<p>No strong correlations found in the numeric columns.</p>")
                        
                        report_html.append("</div>")
                    
                    # Footer
                    report_html.append(f"""
                            <div class="footer">
                                <p>Generated by InsightVista - No-Code Data Analytics Platform</p>
                                <p>Report created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                        </body>
                        </html>
                    """)
                    
                    # Join all HTML parts
                    full_report = "".join(report_html)
                    
                    # Provide download option
                    if report_format == "HTML":
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Download HTML Report",
                            data=full_report,
                            file_name=f"insightvista_report_{timestamp}.html",
                            mime="text/html"
                        )
                        
                        st.success("Report generated successfully! Click the download button above to save the report.")
                    
                    elif report_format == "PDF":
                        st.warning("PDF report generation is currently in development. Please use HTML format instead.")
                
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
    
    # Navigation buttons
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Over", type="primary"):
            st.session_state.current_page = "Home"
            st.rerun()
    
    with col2:
        if st.button("Back to Insights"):
            st.session_state.current_page = "Insights"
            st.rerun()
