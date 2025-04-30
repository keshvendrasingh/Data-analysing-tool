import streamlit as st
import pandas as pd
import io
import os
import numpy as np
from utils import data_processing

def show():
    st.header("Import Your Data")
    
    # Create a tabbed interface
    tab1, tab2 = st.tabs(["📤 Upload File", "📋 Sample Datasets"])
    
    with tab1:
        st.write("Upload your data file to get started. Supported formats: CSV and Excel (.xlsx, .xls)")
        
        # More compact and organized layout
        upload_col1, upload_col2 = st.columns([2, 1])
        
        with upload_col1:
            # File upload section with improved visual design
            st.markdown("### Choose a file to upload")
            uploaded_file = st.file_uploader("", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
        
        with upload_col2:
            st.markdown("### Supported formats")
            st.markdown("""
            - **CSV** (.csv)
            - **Excel** (.xlsx, .xls)
            """)
            st.markdown("Max file size: 200MB")
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing your file..."):
                    # Determine file type and read accordingly
                    file_extension = uploaded_file.name.split(".")[-1].lower()
                    
                    # Create a form for file loading options to batch state updates
                    with st.form(key="file_options_form"):
                        if file_extension == "csv":
                            # For CSV files, provide additional options
                            st.markdown("### CSV Import Options")
                            col1, col2 = st.columns(2)
                            with col1:
                                separator = st.selectbox(
                                    "Select separator",
                                    options=[",", ";", "\t", "|", " "],
                                    index=0
                                )
                            with col2:
                                encoding = st.selectbox(
                                    "Select encoding",
                                    options=["utf-8", "latin-1", "iso-8859-1", "cp1252"],
                                    index=0
                                )
                            
                            # Add header option here in the form
                            has_header = st.checkbox("First row contains column headers", value=True)
                            
                            # Submit button for form
                            options_submitted = st.form_submit_button("Load Data", type="primary")
                            
                            if options_submitted:
                                # Cache data loading to improve performance
                                @st.cache_data(ttl=600)  # Cache for 10 minutes
                                def load_csv(file, sep, enc):
                                    return pd.read_csv(file, sep=sep, encoding=enc)
                                
                                # Read CSV with selected options
                                df = load_csv(uploaded_file, separator, encoding)
                                
                                # Handle header option
                                if not has_header:
                                    # Reset column names and shift data
                                    df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
                                    new_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
                                    df = pd.concat([new_row, df]).reset_index(drop=True)
                        
                        elif file_extension in ["xlsx", "xls"]:
                            # For Excel files, let user select sheet
                            st.markdown("### Excel Import Options")
                            
                            # Cache sheet names to improve performance
                            @st.cache_data(ttl=600)
                            def get_excel_sheets(file):
                                return pd.ExcelFile(file).sheet_names
                            
                            sheet_names = get_excel_sheets(uploaded_file)
                            
                            sheet_name = st.selectbox("Select sheet", options=sheet_names)
                            
                            # Add header option here in the form
                            has_header = st.checkbox("First row contains column headers", value=True)
                            
                            # Submit button for form
                            options_submitted = st.form_submit_button("Load Data", type="primary")
                            
                            if options_submitted:
                                # Cache data loading to improve performance
                                @st.cache_data(ttl=600)
                                def load_excel(file, sheet):
                                    return pd.read_excel(file, sheet_name=sheet)
                                
                                # Read Excel with selected options
                                df = load_excel(uploaded_file, sheet_name)
                                
                                # Handle header option
                                if not has_header:
                                    # Reset column names and shift data
                                    df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
                                    new_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
                                    df = pd.concat([new_row, df]).reset_index(drop=True)
                    
                    # Check if data was loaded (options_submitted was clicked)
                    if 'df' in locals():
                        # Create expandable sections for data info to reduce scrolling
                        with st.expander("📊 Data Preview", expanded=True):
                            # Only show sample of the data for better performance
                            st.dataframe(df.head(5), use_container_width=True)
                            
                            # Add metrics for quick data overview
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Rows", df.shape[0])
                            with col2:
                                st.metric("Columns", df.shape[1])
                            with col3:
                                st.metric("Missing Values", df.isna().sum().sum())
                        
                        with st.expander("📋 Data Information", expanded=False):
                            # Use tabs for better organization of data info
                            info_tab1, info_tab2 = st.tabs(["Column Overview", "Data Types"])
                            
                            with info_tab1:
                                # Create a dataframe with column info for better display
                                column_info = []
                                for col in df.columns:
                                    unique_count = df[col].nunique()
                                    missing_count = df[col].isna().sum()
                                    missing_percent = (missing_count / len(df)) * 100
                                    
                                    column_info.append({
                                        "Column": col,
                                        "Type": str(df[col].dtype),
                                        "Unique Values": unique_count,
                                        "Missing": missing_count,
                                        "Missing %": f"{missing_percent:.1f}%"
                                    })
                                
                                st.dataframe(pd.DataFrame(column_info), use_container_width=True)
                            
                            with info_tab2:
                                # Display more detailed type information
                                type_counts = df.dtypes.value_counts().reset_index()
                                type_counts.columns = ["Data Type", "Count"]
                                
                                # Show bar chart of data types
                                st.bar_chart(type_counts.set_index("Data Type"))
                                st.dataframe(type_counts)
                        
                        # Handle null values in a more structured way
                        with st.expander("🧹 Basic Data Cleaning", expanded=True):
                            # Count and display null values
                            null_counts = df.isnull().sum()
                            
                            if null_counts.sum() > 0:
                                # Create columns with missing values
                                missing_cols = [col for col, count in zip(null_counts.index, null_counts.values) if count > 0]
                                
                                st.write(f"**Found {null_counts.sum()} missing values across {len(missing_cols)} columns**")
                                
                                # Option to handle null values
                                null_handling = st.selectbox(
                                    "How would you like to handle missing values?",
                                    options=["Keep as is", "Drop rows with any missing values", "Fill missing values with mean/mode", "Fill missing values with zeros"]
                                )
                                
                                if null_handling == "Drop rows with any missing values":
                                    original_shape = df.shape[0]
                                    df = df.dropna()
                                    st.success(f"✅ Dropped {original_shape - df.shape[0]} rows with missing values.")
                                
                                elif null_handling == "Fill missing values with mean/mode":
                                    df = data_processing.fill_missing_with_mean_mode(df)
                                    st.success("✅ Filled missing values with mean (for numeric columns) and mode (for categorical columns).")
                                
                                elif null_handling == "Fill missing values with zeros":
                                    df = df.fillna(0)
                                    st.success("✅ Filled missing values with zeros.")
                            else:
                                st.success("✅ No missing values found in your data!")
                        
                        # Save data to session state - in a more visible area
                        import_col1, import_col2 = st.columns(2)
                        
                        with import_col1:
                            if st.button("📥 Import Data & Continue", type="primary", use_container_width=True):
                                st.session_state.data = df.copy()
                                st.session_state.cleaned_data = df.copy()
                                st.session_state.transformations = []
                                st.balloons()  # Add a fun effect for successful import
                                st.success("Data imported successfully! You can now proceed to cleaning and transformation.")
                                
                                # Automatically redirect to next step
                                st.session_state.current_page = "Clean Data"
                                st.rerun()
                        
                        with import_col2:
                            if st.button("📊 Skip to Visualization", use_container_width=True):
                                st.session_state.data = df.copy()
                                st.session_state.cleaned_data = df.copy()
                                st.session_state.transformations = []
                                st.success("Data imported successfully!")
                                
                                # Automatically redirect to visualization
                                st.session_state.current_page = "Visualize"
                                st.rerun()
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Try changing the file encoding or separator, or check if your file is properly formatted.")
    
    with tab2:
        st.subheader("Don't have data? Try a sample dataset")
        st.write("Browse and load sample datasets to explore the app's capabilities")
        
        # Sample dataset descriptions
        sample_datasets = {
            "Iris Flower Dataset": {
                "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
                "description": "A classic dataset for classification. Contains measurements of 150 iris flowers from three different species.",
                "rows": 150,
                "columns": 5,
                "task": "Classification"
            },
            "Titanic Passengers": {
                "url": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
                "description": "Information about Titanic passengers and whether they survived or not.",
                "rows": 891,
                "columns": 12,
                "task": "Classification/Prediction"
            },
            "Boston Housing": {
                "url": "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv",
                "description": "Housing data for 506 census tracts in Boston, including features like crime rate and property values.",
                "rows": 506,
                "columns": 14,
                "task": "Regression"
            },
            "Car Evaluation": {
                "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data",
                "description": "Car evaluation database for classification of car acceptability based on various attributes.",
                "rows": 1728,
                "columns": 7,
                "task": "Classification"
            }
        }
        
        # Display sample datasets in a more organized way
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_sample = st.selectbox("Select a sample dataset", options=list(sample_datasets.keys()))
            
            st.metric("Rows", sample_datasets[selected_sample]["rows"])
            st.metric("Columns", sample_datasets[selected_sample]["columns"])
            st.metric("Task Type", sample_datasets[selected_sample]["task"])
            
            load_button = st.button("📥 Load Sample Dataset", type="primary", use_container_width=True)
        
        with col2:
            st.markdown(f"### {selected_sample}")
            st.write(sample_datasets[selected_sample]["description"])
            
            # Cache for sample datasets to improve performance
            @st.cache_data(ttl=3600)  # Cache for 1 hour
            def load_sample_dataset(url, dataset_name):
                df = pd.read_csv(url)
                # For car evaluation dataset, add column names
                if dataset_name == "Car Evaluation":
                    df.columns = ["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"]
                return df
            
            # Show a preview even before loading
            try:
                with st.spinner("Loading preview..."):
                    preview_df = load_sample_dataset(sample_datasets[selected_sample]["url"], selected_sample)
                    st.write("**Data Preview:**")
                    st.dataframe(preview_df.head(5), use_container_width=True)
                    
                    # Add quick action buttons below the preview
                    st.write("**Quick Actions:**")
                    
                    # First row of quick action buttons
                    quick_row1_cols = st.columns([1, 1, 1])
                    with quick_row1_cols[0]:
                        if st.button("🧹 Quick Clean", key="clean_preview", type="primary", use_container_width=True):
                            # Apply some quick automated cleaning
                            cleaned_df = preview_df.copy()
                            
                            # Drop duplicates
                            cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
                            
                            # Fill missing values
                            cleaned_df = data_processing.fill_missing_with_mean_mode(cleaned_df)
                            
                            # Try to convert object columns to numeric where possible
                            for col in cleaned_df.select_dtypes(include=['object']).columns:
                                try:
                                    cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                                except:
                                    pass
                            
                            # Save to session state
                            st.session_state.data = preview_df.copy()  # Keep original
                            st.session_state.cleaned_data = cleaned_df.copy()  # Store cleaned
                            st.session_state.transformations = ["Removed duplicates", 
                                                              "Filled missing values", 
                                                              "Converted suitable columns to numeric"]
                            
                            # Indicate cleaning has happened
                            st.success("✅ Applied quick clean! Data is ready for analysis.")
                            st.session_state.current_page = "Clean Data"
                            st.rerun()
                            
                    with quick_row1_cols[1]:
                        if st.button("🔍 Explore Dataset", key="explore_preview", use_container_width=True):
                            st.session_state.data = preview_df.copy()
                            st.session_state.cleaned_data = preview_df.copy()
                            st.session_state.transformations = []
                            st.session_state.current_page = "Clean Data"
                            st.rerun()
                            
                    with quick_row1_cols[2]:
                        if st.button("📊 Quick Visualize", key="visualize_preview", use_container_width=True):
                            st.session_state.data = preview_df.copy()
                            st.session_state.cleaned_data = preview_df.copy()
                            st.session_state.transformations = []
                            st.session_state.current_page = "Visualize"
                            st.rerun()
                    
                    # Second row of quick action buttons
                    quick_row2_cols = st.columns([1, 1, 1])
                    with quick_row2_cols[0]:
                        if st.button("📋 To Dashboard", key="dashboard_preview", use_container_width=True):
                            st.session_state.data = preview_df.copy()
                            st.session_state.cleaned_data = preview_df.copy()
                            st.session_state.transformations = []
                            st.session_state.current_page = "Dashboard"
                            st.rerun()
                            
                    with quick_row2_cols[1]:
                        if st.button("💡 Quick Insights", key="insights_preview", use_container_width=True):
                            st.session_state.data = preview_df.copy()
                            st.session_state.cleaned_data = preview_df.copy()
                            st.session_state.transformations = []
                            st.session_state.current_page = "Insights"
                            st.rerun()
                            
                    with quick_row2_cols[2]:
                        if st.button("⬇️ Load Full Dataset", key="load_full_dataset", use_container_width=True):
                            # Trigger the load button automatically
                            load_button = True
            except Exception as e:
                st.warning(f"Could not load preview: {str(e)}")
        
        if load_button:
            try:
                with st.spinner("Loading full dataset..."):
                    df = load_sample_dataset(sample_datasets[selected_sample]["url"], selected_sample)
                
                # Save data to session state
                st.session_state.data = df.copy()
                st.session_state.cleaned_data = df.copy()
                st.session_state.transformations = []
                
                st.success(f"Sample dataset '{selected_sample}' loaded successfully!")
                
                # Add quick cleaning options
                st.subheader("Quick Data Preparation")
                
                with st.expander("📊 Dataset Summary", expanded=True):
                    # Show quick stats about the dataset
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        st.metric("Total Rows", df.shape[0])
                        st.metric("Missing Values", df.isna().sum().sum())
                    with stat_col2:
                        st.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
                        st.metric("Categorical Columns", len(df.select_dtypes(include=['object']).columns))
                    with stat_col3:
                        st.metric("Duplicate Rows", df.duplicated().sum())
                        if 'class' in df.columns or 'target' in df.columns:
                            target_col = 'class' if 'class' in df.columns else 'target'
                            st.metric("Classes", df[target_col].nunique())
                
                # Quick cleaning options
                with st.expander("🧹 Quick Cleaning Options", expanded=True):
                    # Add a prominent clean button at the top
                    if st.button("🧹 Clean Dataset Now", type="primary", key="clean_full_dataset_button", use_container_width=True):
                        # Store original for comparison
                        original_df = df.copy()
                        
                        # Apply common cleaning operations
                        # 1. Remove duplicates
                        old_shape = df.shape[0]
                        df = df.drop_duplicates().reset_index(drop=True)
                        removed_dupes = old_shape - df.shape[0]
                        
                        # 2. Fill missing values with mean/mode
                        missing_before = df.isna().sum().sum()
                        df = data_processing.fill_missing_with_mean_mode(df)
                        missing_filled = missing_before - df.isna().sum().sum()
                        
                        # 3. Convert data types where possible
                        converted_cols = []
                        for col in df.select_dtypes(include=['object']).columns:
                            try:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                                converted_cols.append(col)
                            except:
                                pass
                        
                        # 4. Handle outliers with Z-score
                        num_cols = df.select_dtypes(include=['number']).columns
                        outlier_count = 0
                        for col in num_cols:
                            outliers = data_processing.detect_outliers_zscore(df[col])
                            if outliers:
                                df.loc[outliers, col] = None  # Set outliers to None
                                outlier_count += len(outliers)
                        
                        # Fill those new NaNs with mean
                        if outlier_count > 0:
                            df = data_processing.fill_missing_with_mean_mode(df)
                        
                        # Create summary of changes
                        st.success("✅ Cleaned dataset successfully!")
                        
                        # Show what was done
                        changes_col1, changes_col2 = st.columns(2)
                        with changes_col1:
                            st.write("**Changes Applied:**")
                            st.write(f"• Removed {removed_dupes} duplicate rows")
                            st.write(f"• Filled {missing_filled} missing values")
                            st.write(f"• Converted {len(converted_cols)} columns to numeric")
                            st.write(f"• Handled {outlier_count} outliers")
                        
                        with changes_col2:
                            # Show data completeness improvement
                            completeness_before = 100 - (missing_before / (original_df.shape[0] * original_df.shape[1]) * 100)
                            completeness_after = 100 - (df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
                            
                            st.metric("Data Completeness", 
                                     f"{completeness_after:.1f}%",
                                     delta=f"{completeness_after - completeness_before:.1f}%")
                            
                            st.metric("Rows", 
                                     df.shape[0], 
                                     delta=df.shape[0] - original_df.shape[0],
                                     delta_color="inverse")
                            
                        # Store transformations
                        st.session_state.transformations = [
                            f"Removed {removed_dupes} duplicate rows",
                            f"Filled {missing_filled} missing values",
                            f"Converted {len(converted_cols)} columns to numeric",
                            f"Handled {outlier_count} outliers"
                        ]
                    
                    st.write("Or adjust individual cleaning options:")
                    quick_clean_col1, quick_clean_col2 = st.columns(2)
                    
                    with quick_clean_col1:
                        if st.checkbox("Remove duplicates", value=False, key="remove_dupes"):
                            old_shape = df.shape[0]
                            df = df.drop_duplicates().reset_index(drop=True)
                            if old_shape > df.shape[0]:
                                st.info(f"Removed {old_shape - df.shape[0]} duplicate rows")
                            else:
                                st.info("No duplicates found")
                            
                        if st.checkbox("Handle missing values", value=True, key="handle_missing"):
                            missing_method = st.radio(
                                "Method:",
                                ["Fill with mean/mode", "Fill with zeros", "Drop rows with missing values"],
                                key="missing_method"
                            )
                            
                            if missing_method == "Fill with mean/mode":
                                df = data_processing.fill_missing_with_mean_mode(df)
                                st.info("Missing values filled with mean/mode")
                            elif missing_method == "Fill with zeros":
                                df = df.fillna(0)
                                st.info("Missing values filled with zeros")
                            elif missing_method == "Drop rows with missing values":
                                old_shape = df.shape[0]
                                df = df.dropna()
                                st.info(f"Dropped {old_shape - df.shape[0]} rows with missing values")
                    
                    with quick_clean_col2:
                        if st.checkbox("Auto-convert data types", value=True, key="convert_dtypes"):
                            # Try to convert object columns to numeric where possible
                            for col in df.select_dtypes(include=['object']).columns:
                                try:
                                    df[col] = pd.to_numeric(df[col], errors='coerce')
                                except:
                                    pass
                            st.info("Converted suitable columns to numeric types")
                        
                        if st.checkbox("Detect and remove outliers", value=False, key="remove_outliers"):
                            outlier_method = st.radio(
                                "Method:",
                                ["Z-score (3σ)", "IQR (1.5×IQR)"],
                                key="outlier_method"
                            )
                            
                            # Only apply to numeric columns
                            num_cols = df.select_dtypes(include=['number']).columns
                            outlier_count = 0
                            
                            if outlier_method == "Z-score (3σ)":
                                # Use Z-score method
                                for col in num_cols:
                                    outliers = data_processing.detect_outliers_zscore(df[col])
                                    if outliers:
                                        df.loc[outliers, col] = None  # Set outliers to None
                                        outlier_count += len(outliers)
                                
                                # Fill those NaNs with mean
                                df = data_processing.fill_missing_with_mean_mode(df)
                                st.info(f"Replaced {outlier_count} outliers with mean values")
                            
                            elif outlier_method == "IQR (1.5×IQR)":
                                # Use IQR method
                                for col in num_cols:
                                    outliers = data_processing.detect_outliers_iqr(df[col])
                                    if outliers:
                                        df.loc[outliers, col] = None  # Set outliers to None
                                        outlier_count += len(outliers)
                                
                                # Fill those NaNs with mean
                                df = data_processing.fill_missing_with_mean_mode(df)
                                st.info(f"Replaced {outlier_count} outliers with mean values")
                
                # Show a before/after comparison
                with st.expander("📈 Before & After Comparison", expanded=True):
                    # Calculate changes in key metrics
                    original_df = load_sample_dataset(sample_datasets[selected_sample]["url"], selected_sample)
                    
                    # Create comparison metrics
                    compare_col1, compare_col2, compare_col3 = st.columns(3)
                    
                    with compare_col1:
                        st.metric("Rows", 
                                 df.shape[0], 
                                 delta=df.shape[0] - original_df.shape[0],
                                 delta_color="inverse")
                        
                        missing_before = original_df.isna().sum().sum()
                        missing_after = df.isna().sum().sum()
                        st.metric("Missing Values", 
                                 missing_after,
                                 delta=missing_after - missing_before,
                                 delta_color="inverse")
                    
                    with compare_col2:
                        # Calculate number of outliers in original vs cleaned
                        num_outliers_original = 0
                        num_outliers_cleaned = 0
                        
                        for col in df.select_dtypes(include=['number']).columns:
                            if col in original_df.columns:
                                num_outliers_original += len(data_processing.detect_outliers_zscore(original_df[col]))
                                num_outliers_cleaned += len(data_processing.detect_outliers_zscore(df[col]))
                        
                        st.metric("Outliers", 
                                 num_outliers_cleaned,
                                 delta=num_outliers_cleaned - num_outliers_original,
                                 delta_color="inverse")
                        
                        # Calculate data completeness as percentage
                        completeness_before = 100 - (missing_before / (original_df.shape[0] * original_df.shape[1]) * 100)
                        completeness_after = 100 - (missing_after / (df.shape[0] * df.shape[1]) * 100)
                        
                        st.metric("Data Completeness", 
                                 f"{completeness_after:.1f}%",
                                 delta=f"{completeness_after - completeness_before:.1f}%",
                                 delta_color="normal")
                    
                    with compare_col3:
                        # Try to show target class distribution if applicable
                        if 'class' in df.columns or 'target' in df.columns:
                            target_col = 'class' if 'class' in df.columns else 'target'
                            
                            # Show class balance metric
                            class_counts = df[target_col].value_counts(normalize=True)
                            min_class_pct = class_counts.min() * 100
                            max_class_pct = class_counts.max() * 100
                            balance_metric = 100 - (max_class_pct - min_class_pct)
                            
                            original_class_counts = original_df[target_col].value_counts(normalize=True)
                            original_min_class_pct = original_class_counts.min() * 100
                            original_max_class_pct = original_class_counts.max() * 100
                            original_balance_metric = 100 - (original_max_class_pct - original_min_class_pct)
                            
                            st.metric("Class Balance", 
                                     f"{balance_metric:.1f}%",
                                     delta=f"{balance_metric - original_balance_metric:.1f}%",
                                     delta_color="normal")
                    
                    # Add a visual comparison of data
                    st.write("#### Sample Data Comparison")
                    
                    # Display a comparison of original and cleaned data
                    comp_tab1, comp_tab2, comp_tab3 = st.tabs(["Data Preview", "Data Types", "Data Quality"])
                    
                    with comp_tab1:
                        before_after_col1, before_after_col2 = st.columns(2)
                        
                        with before_after_col1:
                            st.write("**Original Data**")
                            st.dataframe(original_df.head(3), use_container_width=True)
                        
                        with before_after_col2:
                            st.write("**Cleaned Data**")
                            st.dataframe(df.head(3), use_container_width=True)
                    
                    with comp_tab2:
                        # Show data types changes
                        type_changes = pd.DataFrame({
                            'Column': df.columns,
                            'Original Type': [str(original_df[col].dtype) for col in df.columns if col in original_df.columns],
                            'New Type': [str(df[col].dtype) for col in df.columns if col in original_df.columns]
                        })
                        
                        # Add a column to highlight changes
                        type_changes['Changed'] = type_changes['Original Type'] != type_changes['New Type']
                        
                        # Sort to show changed columns first
                        type_changes = type_changes.sort_values('Changed', ascending=False)
                        
                        # Display the table
                        st.dataframe(type_changes, use_container_width=True)
                    
                    with comp_tab3:
                        # Calculate data quality metrics
                        st.write("**Data Quality Comparison**")
                        
                        dq_col1, dq_col2 = st.columns(2)
                        
                        with dq_col1:
                            # Create a quality chart for numeric columns
                            num_cols = df.select_dtypes(include=['number']).columns
                            if len(num_cols) > 0:
                                quality_data = []
                                for col in num_cols:
                                    if col in original_df.columns:
                                        # Calculate metrics
                                        missing_pct_before = original_df[col].isna().mean() * 100
                                        missing_pct_after = df[col].isna().mean() * 100
                                        
                                        # Count outliers
                                        outliers_before = len(data_processing.detect_outliers_zscore(original_df[col]))
                                        outliers_after = len(data_processing.detect_outliers_zscore(df[col]))
                                        
                                        outlier_pct_before = (outliers_before / original_df.shape[0]) * 100
                                        outlier_pct_after = (outliers_after / df.shape[0]) * 100
                                        
                                        # Combine metrics to a single quality score (100 - problems)
                                        quality_before = 100 - (missing_pct_before + outlier_pct_before)
                                        quality_after = 100 - (missing_pct_after + outlier_pct_after)
                                        
                                        quality_data.append({
                                            'Column': col,
                                            'Original Quality': quality_before,
                                            'New Quality': quality_after,
                                            'Improvement': quality_after - quality_before
                                        })
                                
                                quality_df = pd.DataFrame(quality_data)
                                
                                # Only show if we have data
                                if not quality_df.empty:
                                    # Sort by improvement
                                    quality_df = quality_df.sort_values('Improvement', ascending=False)
                                    
                                    # Display as a bar chart - first 5 columns
                                    subset_df = quality_df.head(5)
                                    
                                    # Create a bar chart
                                    chart_data = pd.melt(
                                        subset_df,
                                        id_vars=['Column'],
                                        value_vars=['Original Quality', 'New Quality'],
                                        var_name='Version',
                                        value_name='Quality Score'
                                    )
                                    
                                    # Plot with Streamlit
                                    st.write("**Quality Scores for Top 5 Improved Columns**")
                                    st.bar_chart(chart_data.set_index(['Column', 'Version'])['Quality Score'], use_container_width=True)
                            
                        with dq_col2:
                            # Show completeness comparison
                            st.write("**Overall Data Completeness**")
                            
                            # Calculate column-wise completeness
                            completeness_before_cols = (1 - original_df.isna().mean()) * 100
                            completeness_after_cols = (1 - df.isna().mean()) * 100
                            
                            completeness_comparison = pd.DataFrame({
                                'Column': completeness_before_cols.index,
                                'Before (%)': completeness_before_cols.values.round(1),
                                'After (%)': [completeness_after_cols[col] if col in completeness_after_cols.index else 0 
                                             for col in completeness_before_cols.index],
                                'Change (%)': [completeness_after_cols[col] - completeness_before_cols[col] 
                                              if col in completeness_after_cols.index else 0 
                                              for col in completeness_before_cols.index]
                            })
                            
                            # Sort by the change
                            completeness_comparison = completeness_comparison.sort_values('Change (%)', ascending=False)
                            
                            # Display the table
                            st.dataframe(completeness_comparison, use_container_width=True)
                
                # Update cleaned data in session state
                st.session_state.data = df.copy()
                st.session_state.cleaned_data = df.copy()
                
                # Show comprehensive navigation options
                st.subheader("Continue with this Dataset...")
                
                # First row of buttons
                action_row1_col1, action_row1_col2, action_row1_col3 = st.columns(3)
                with action_row1_col1:
                    if st.button("🧹 More Cleaning Options", type="primary", key="goto_clean_sample", use_container_width=True):
                        st.session_state.current_page = "Clean Data"
                        st.rerun()
                with action_row1_col2:
                    if st.button("📊 Visualize Data", type="primary", key="goto_visualize_sample", use_container_width=True):
                        st.session_state.current_page = "Visualize"
                        st.rerun()
                with action_row1_col3:
                    if st.button("💡 Generate Insights", type="primary", key="goto_insights_sample", use_container_width=True):
                        st.session_state.current_page = "Insights"
                        st.rerun()
                
                # Second row of buttons
                action_row2_col1, action_row2_col2, action_row2_col3 = st.columns(3)
                with action_row2_col1:
                    if st.button("📋 Create Dashboard", key="goto_dashboard_sample", use_container_width=True):
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                with action_row2_col2:
                    if st.button("📤 Export Results", key="goto_export_sample", use_container_width=True):
                        st.session_state.current_page = "Export"
                        st.rerun()
                with action_row2_col3:
                    if st.button("🔄 Try Another Dataset", key="reset_sample", use_container_width=True):
                        # Don't save the data to session state
                        if 'data' in st.session_state:
                            del st.session_state.data
                        if 'cleaned_data' in st.session_state:
                            del st.session_state.cleaned_data
                        st.session_state.transformations = []
                        st.session_state.visualizations = []
                        st.session_state.current_page = "Import Data"
                        st.rerun()
                    
            except Exception as e:
                st.error(f"Error loading sample dataset: {str(e)}")
