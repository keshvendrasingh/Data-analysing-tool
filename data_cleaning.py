import streamlit as st
import pandas as pd
import numpy as np
from utils import data_processing

def show():
    st.header("Clean & Transform Data")
    
    # Check if data is available
    if st.session_state.data is None:
        st.warning("No data available. Please import data first.")
        if st.button("Go to Import Data"):
            st.session_state.current_page = "Import Data"
            st.rerun()
        return
    
    # Display current data
    st.subheader("Current Data Preview")
    st.dataframe(st.session_state.cleaned_data.head(10))
    
    # Data info
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Rows:** {st.session_state.cleaned_data.shape[0]}")
        st.write(f"**Columns:** {st.session_state.cleaned_data.shape[1]}")
    with col2:
        st.write("**Transformations applied:** ", len(st.session_state.transformations))
    
    # Tabs for different data cleaning operations
    clean_tab, transform_tab, filter_tab, advanced_tab = st.tabs([
        "🧹 Basic Cleaning", 
        "🔄 Transformation", 
        "🔍 Filter & Sort", 
        "⚙️ Advanced"
    ])
    
    # Basic Cleaning Tab
    with clean_tab:
        st.subheader("Basic Data Cleaning")
        
        # Handle missing values
        st.write("**Handle Missing Values**")
        
        # Show columns with missing values
        df = st.session_state.cleaned_data
        null_counts = df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]
        
        if len(cols_with_nulls) > 0:
            st.write("Columns with missing values:")
            for col, count in zip(cols_with_nulls.index, cols_with_nulls.values):
                st.write(f"- {col}: {count} missing values ({(count/len(df)*100):.2f}%)")
            
            # Select column to handle
            selected_col = st.selectbox(
                "Select column to handle missing values",
                options=cols_with_nulls.index.tolist()
            )
            
            # Choose method for handling missing values
            method = st.selectbox(
                "Select method to handle missing values",
                options=["Drop rows", "Fill with mean", "Fill with median", "Fill with mode", "Fill with zero", "Fill with custom value"]
            )
            
            if method == "Drop rows":
                if st.button("Apply - Drop Rows"):
                    original_shape = df.shape[0]
                    df = df.dropna(subset=[selected_col])
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Dropped rows with missing values in column '{selected_col}'")
                    st.success(f"Dropped {original_shape - df.shape[0]} rows with missing values in column '{selected_col}'")
                    st.rerun()
            
            elif method == "Fill with mean" and pd.api.types.is_numeric_dtype(df[selected_col]):
                if st.button("Apply - Fill with Mean"):
                    mean_value = df[selected_col].mean()
                    df[selected_col] = df[selected_col].fillna(mean_value)
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Filled missing values in column '{selected_col}' with mean ({mean_value:.2f})")
                    st.success(f"Filled missing values in column '{selected_col}' with mean ({mean_value:.2f})")
                    st.rerun()
            
            elif method == "Fill with median" and pd.api.types.is_numeric_dtype(df[selected_col]):
                if st.button("Apply - Fill with Median"):
                    median_value = df[selected_col].median()
                    df[selected_col] = df[selected_col].fillna(median_value)
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Filled missing values in column '{selected_col}' with median ({median_value:.2f})")
                    st.success(f"Filled missing values in column '{selected_col}' with median ({median_value:.2f})")
                    st.rerun()
            
            elif method == "Fill with mode":
                if st.button("Apply - Fill with Mode"):
                    mode_value = df[selected_col].mode()[0]
                    df[selected_col] = df[selected_col].fillna(mode_value)
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Filled missing values in column '{selected_col}' with mode ({mode_value})")
                    st.success(f"Filled missing values in column '{selected_col}' with mode ({mode_value})")
                    st.rerun()
            
            elif method == "Fill with zero":
                if st.button("Apply - Fill with Zero"):
                    df[selected_col] = df[selected_col].fillna(0)
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Filled missing values in column '{selected_col}' with zero")
                    st.success(f"Filled missing values in column '{selected_col}' with zero")
                    st.rerun()
            
            elif method == "Fill with custom value":
                custom_value = st.text_input("Enter custom value")
                if st.button("Apply - Fill with Custom Value"):
                    try:
                        # Try to convert to the same type as the column
                        if pd.api.types.is_numeric_dtype(df[selected_col]):
                            custom_value = float(custom_value)
                        df[selected_col] = df[selected_col].fillna(custom_value)
                        st.session_state.cleaned_data = df
                        st.session_state.transformations.append(f"Filled missing values in column '{selected_col}' with custom value ({custom_value})")
                        st.success(f"Filled missing values in column '{selected_col}' with custom value ({custom_value})")
                        st.rerun()
                    except ValueError:
                        st.error("Invalid value for this column type")
        else:
            st.write("✅ No missing values found in the dataset!")
        
        # Remove duplicates
        st.divider()
        st.write("**Handle Duplicate Rows**")
        
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            st.write(f"Found {duplicate_count} duplicate rows in the dataset.")
            if st.button("Remove Duplicate Rows"):
                original_shape = df.shape[0]
                df = df.drop_duplicates().reset_index(drop=True)
                st.session_state.cleaned_data = df
                st.session_state.transformations.append(f"Removed {original_shape - df.shape[0]} duplicate rows")
                st.success(f"Removed {original_shape - df.shape[0]} duplicate rows")
                st.rerun()
        else:
            st.write("✅ No duplicate rows found in the dataset!")

    # Transformation Tab
    with transform_tab:
        st.subheader("Data Transformation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Column Operations**")
            
            # Rename column
            st.write("Rename Column")
            cols = st.session_state.cleaned_data.columns.tolist()
            col_to_rename = st.selectbox("Select column to rename", options=cols, key="rename_col")
            new_name = st.text_input("Enter new column name")
            
            if st.button("Rename Column"):
                if new_name and new_name != col_to_rename and new_name not in cols:
                    df = st.session_state.cleaned_data.copy()
                    df = df.rename(columns={col_to_rename: new_name})
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Renamed column '{col_to_rename}' to '{new_name}'")
                    st.success(f"Renamed column '{col_to_rename}' to '{new_name}'")
                    st.rerun()
                else:
                    st.error("Please enter a valid and unique column name")
            
            # Drop column
            st.write("Drop Column")
            col_to_drop = st.selectbox("Select column to drop", options=cols, key="drop_col")
            
            if st.button("Drop Column"):
                df = st.session_state.cleaned_data.copy()
                df = df.drop(columns=[col_to_drop])
                st.session_state.cleaned_data = df
                st.session_state.transformations.append(f"Dropped column '{col_to_drop}'")
                st.success(f"Dropped column '{col_to_drop}'")
                st.rerun()
        
        with col2:
            st.write("**Data Type Conversion**")
            
            # Convert column type
            cols = st.session_state.cleaned_data.columns.tolist()
            col_to_convert = st.selectbox("Select column to convert", options=cols, key="convert_col")
            
            target_type = st.selectbox(
                "Convert to type",
                options=["string", "integer", "float", "boolean", "datetime"]
            )
            
            if st.button("Convert Column Type"):
                df = st.session_state.cleaned_data.copy()
                try:
                    if target_type == "string":
                        df[col_to_convert] = df[col_to_convert].astype(str)
                    elif target_type == "integer":
                        df[col_to_convert] = df[col_to_convert].astype(int)
                    elif target_type == "float":
                        df[col_to_convert] = df[col_to_convert].astype(float)
                    elif target_type == "boolean":
                        df[col_to_convert] = df[col_to_convert].astype(bool)
                    elif target_type == "datetime":
                        df[col_to_convert] = pd.to_datetime(df[col_to_convert])
                    
                    st.session_state.cleaned_data = df
                    st.session_state.transformations.append(f"Converted column '{col_to_convert}' to {target_type}")
                    st.success(f"Converted column '{col_to_convert}' to {target_type}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error converting column: {str(e)}")
        
        st.divider()
        
        # Numerical transformations
        st.write("**Numerical Transformations**")
        
        numeric_cols = st.session_state.cleaned_data.select_dtypes(include=np.number).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                num_col = st.selectbox("Select numeric column", options=numeric_cols, key="num_transform_col")
                
                transform_type = st.selectbox(
                    "Select transformation",
                    options=["Normalization (0-1)", "Standardization (z-score)", "Log transform", "Square root", "Create bins"]
                )
            
            with col2:
                if transform_type == "Create bins":
                    num_bins = st.number_input("Number of bins", min_value=2, max_value=20, value=5)
                    bin_labels = st.text_input("Bin labels (comma-separated, leave empty for default)", "")
                
                if st.button("Apply Transformation"):
                    df = st.session_state.cleaned_data.copy()
                    
                    if transform_type == "Normalization (0-1)":
                        min_val = df[num_col].min()
                        max_val = df[num_col].max()
                        df[f"{num_col}_normalized"] = (df[num_col] - min_val) / (max_val - min_val)
                        st.session_state.cleaned_data = df
                        st.session_state.transformations.append(f"Normalized column '{num_col}' (0-1 scale)")
                        st.success(f"Created normalized column '{num_col}_normalized'")
                    
                    elif transform_type == "Standardization (z-score)":
                        mean_val = df[num_col].mean()
                        std_val = df[num_col].std()
                        df[f"{num_col}_standardized"] = (df[num_col] - mean_val) / std_val
                        st.session_state.cleaned_data = df
                        st.session_state.transformations.append(f"Standardized column '{num_col}' (z-score)")
                        st.success(f"Created standardized column '{num_col}_standardized'")
                    
                    elif transform_type == "Log transform":
                        # Check if column has values <= 0
                        if (df[num_col] <= 0).any():
                            st.error("Cannot apply log transform to values <= 0")
                        else:
                            df[f"{num_col}_log"] = np.log(df[num_col])
                            st.session_state.cleaned_data = df
                            st.session_state.transformations.append(f"Applied log transform to column '{num_col}'")
                            st.success(f"Created log-transformed column '{num_col}_log'")
                    
                    elif transform_type == "Square root":
                        # Check if column has negative values
                        if (df[num_col] < 0).any():
                            st.error("Cannot apply square root to negative values")
                        else:
                            df[f"{num_col}_sqrt"] = np.sqrt(df[num_col])
                            st.session_state.cleaned_data = df
                            st.session_state.transformations.append(f"Applied square root transform to column '{num_col}'")
                            st.success(f"Created square root column '{num_col}_sqrt'")
                    
                    elif transform_type == "Create bins":
                        if bin_labels and len(bin_labels.split(',')) != num_bins:
                            st.error(f"Number of labels ({len(bin_labels.split(','))}) doesn't match number of bins ({num_bins})")
                        else:
                            labels = bin_labels.split(',') if bin_labels else None
                            df[f"{num_col}_bins"] = pd.cut(df[num_col], bins=num_bins, labels=labels)
                            st.session_state.cleaned_data = df
                            st.session_state.transformations.append(f"Created {num_bins} bins for column '{num_col}'")
                            st.success(f"Created binned column '{num_col}_bins'")
                    
                    st.rerun()
        else:
            st.info("No numeric columns found in the dataset")

    # Filter Tab
    with filter_tab:
        st.subheader("Filter & Sort Data")
        
        # Filter data
        st.write("**Filter Data**")
        
        cols = st.session_state.cleaned_data.columns.tolist()
        filter_col = st.selectbox("Select column to filter on", options=cols, key="filter_col")
        
        # Get column data type
        col_dtype = st.session_state.cleaned_data[filter_col].dtype
        
        # Different filter options based on data type
        if pd.api.types.is_numeric_dtype(col_dtype):
            # For numeric columns
            min_val = float(st.session_state.cleaned_data[filter_col].min())
            max_val = float(st.session_state.cleaned_data[filter_col].max())
            
            filter_type = st.selectbox(
                "Filter type",
                options=["Range", "Greater than", "Less than", "Equal to"]
            )
            
            if filter_type == "Range":
                min_filter, max_filter = st.slider(
                    "Select range",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val)
                )
                
                if st.button("Apply Range Filter"):
                    df = st.session_state.cleaned_data.copy()
                    filtered_df = df[(df[filter_col] >= min_filter) & (df[filter_col] <= max_filter)]
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' for values between {min_filter} and {max_filter}")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
            
            elif filter_type == "Greater than":
                threshold = st.number_input("Greater than value", value=min_val)
                
                if st.button("Apply Greater Than Filter"):
                    df = st.session_state.cleaned_data.copy()
                    filtered_df = df[df[filter_col] > threshold]
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' for values > {threshold}")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
            
            elif filter_type == "Less than":
                threshold = st.number_input("Less than value", value=max_val)
                
                if st.button("Apply Less Than Filter"):
                    df = st.session_state.cleaned_data.copy()
                    filtered_df = df[df[filter_col] < threshold]
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' for values < {threshold}")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
            
            elif filter_type == "Equal to":
                unique_values = st.session_state.cleaned_data[filter_col].dropna().unique()
                if len(unique_values) <= 20:  # Show dropdown for small number of unique values
                    value = st.selectbox("Select value", options=sorted(unique_values))
                else:  # Show input for large number of unique values
                    value = st.number_input("Enter value", value=float(min_val))
                
                if st.button("Apply Equal To Filter"):
                    df = st.session_state.cleaned_data.copy()
                    filtered_df = df[df[filter_col] == value]
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' for values = {value}")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
        
        else:
            # For categorical/text columns
            unique_values = st.session_state.cleaned_data[filter_col].dropna().unique()
            
            if len(unique_values) <= 50:  # Show checkboxes for reasonable number of values
                st.write(f"Select values to include from column '{filter_col}':")
                
                selected_values = []
                # Create checkboxes in columns for better layout
                cols = st.columns(3)
                for i, value in enumerate(sorted(unique_values)):
                    col_idx = i % 3
                    with cols[col_idx]:
                        if st.checkbox(str(value), value=True, key=f"check_{filter_col}_{i}"):
                            selected_values.append(value)
                
                if st.button("Apply Category Filter"):
                    df = st.session_state.cleaned_data.copy()
                    filtered_df = df[df[filter_col].isin(selected_values)]
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' to include {len(selected_values)} categories")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
            
            else:
                # For columns with many unique values, use text search
                search_term = st.text_input(f"Search in column '{filter_col}'")
                match_type = st.radio("Match type", options=["Contains", "Starts with", "Ends with", "Exact match"])
                
                if st.button("Apply Text Filter"):
                    df = st.session_state.cleaned_data.copy()
                    
                    if match_type == "Contains":
                        filtered_df = df[df[filter_col].astype(str).str.contains(search_term, na=False)]
                    elif match_type == "Starts with":
                        filtered_df = df[df[filter_col].astype(str).str.startswith(search_term, na=False)]
                    elif match_type == "Ends with":
                        filtered_df = df[df[filter_col].astype(str).str.endswith(search_term, na=False)]
                    else:  # Exact match
                        filtered_df = df[df[filter_col].astype(str) == search_term]
                    
                    st.session_state.cleaned_data = filtered_df
                    st.session_state.transformations.append(f"Filtered column '{filter_col}' with text search '{search_term}' ({match_type})")
                    st.success(f"Applied filter: {len(filtered_df)} rows remaining")
                    st.rerun()
        
        st.divider()
        
        # Sort data
        st.write("**Sort Data**")
        
        cols = st.session_state.cleaned_data.columns.tolist()
        sort_col = st.selectbox("Select column to sort by", options=cols, key="sort_col")
        sort_order = st.radio("Sort order", options=["Ascending", "Descending"])
        
        if st.button("Apply Sorting"):
            df = st.session_state.cleaned_data.copy()
            is_ascending = sort_order == "Ascending"
            df = df.sort_values(by=sort_col, ascending=is_ascending)
            st.session_state.cleaned_data = df
            order_text = "ascending" if is_ascending else "descending"
            st.session_state.transformations.append(f"Sorted data by column '{sort_col}' in {order_text} order")
            st.success(f"Data sorted by '{sort_col}' in {order_text} order")
            st.rerun()

    # Advanced Tab
    with advanced_tab:
        st.subheader("Advanced Operations")
        
        # Group By and Aggregate
        st.write("**Group By & Aggregate**")
        
        cols = st.session_state.cleaned_data.columns.tolist()
        numeric_cols = st.session_state.cleaned_data.select_dtypes(include=np.number).columns.tolist()
        
        group_cols = st.multiselect("Select columns to group by", options=cols, key="group_cols")
        
        if group_cols:
            agg_options = {}
            
            st.write("Select aggregation functions for numeric columns:")
            
            for col in numeric_cols:
                if col not in group_cols:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{col}**")
                    
                    with col2:
                        agg_funcs = st.multiselect(
                            "Aggregation functions",
                            options=["mean", "sum", "min", "max", "count", "std"],
                            key=f"agg_{col}"
                        )
                        if agg_funcs:
                            agg_options[col] = agg_funcs
            
            if agg_options and st.button("Apply Grouping"):
                try:
                    df = st.session_state.cleaned_data.copy()
                    grouped_df = df.groupby(group_cols).agg(agg_options).reset_index()
                    
                    # Flatten the column names if needed
                    if isinstance(grouped_df.columns, pd.MultiIndex):
                        grouped_df.columns = ['_'.join(col).strip() for col in grouped_df.columns.values]
                    
                    st.session_state.cleaned_data = grouped_df
                    st.session_state.transformations.append(f"Grouped data by {', '.join(group_cols)} with {len(agg_options)} aggregations")
                    st.success("Grouping operation applied successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error applying grouping: {str(e)}")
        
        st.divider()
        
        # Create new column from expression
        st.write("**Create New Column from Expression**")
        
        new_col_name = st.text_input("New column name")
        
        # Display available columns as reference
        if st.expander("Available Columns"):
            for col in st.session_state.cleaned_data.columns:
                st.code(f"df['{col}']")
        
        expression = st.text_area("Enter Python expression (use df for the dataframe)")
        
        if st.button("Create Column") and new_col_name and expression:
            try:
                df = st.session_state.cleaned_data.copy()
                
                # Execute expression in a safe way
                # This is a simplified approach - in production you might want more safeguards
                local_vars = {"df": df, "np": np}
                result = eval(expression, {"__builtins__": {}}, local_vars)
                
                df[new_col_name] = result
                st.session_state.cleaned_data = df
                st.session_state.transformations.append(f"Created new column '{new_col_name}' from expression")
                st.success(f"Created new column '{new_col_name}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating column: {str(e)}")
    
    # Show transformations history
    st.divider()
    with st.expander("Transformation History"):
        if st.session_state.transformations:
            for i, transform in enumerate(st.session_state.transformations):
                st.write(f"{i+1}. {transform}")
        else:
            st.write("No transformations applied yet")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Reset All Transformations"):
            st.session_state.cleaned_data = st.session_state.data.copy()
            st.session_state.transformations = []
            st.success("Reset all transformations")
            st.rerun()
    
    with col2:
        if st.button("Proceed to Visualization", type="primary"):
            st.session_state.current_page = "Visualize"
            st.rerun()
    
    with col3:
        if st.button("Back to Import"):
            st.session_state.current_page = "Import Data"
            st.rerun()
