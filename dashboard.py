import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import visualization_utils
import json

def show():
    st.header("Your Custom Dashboard")
    
    # Check if data is available
    if st.session_state.cleaned_data is None:
        st.warning("No data available. Please import and clean data first.")
        if st.button("Go to Import Data"):
            st.session_state.current_page = "Import Data"
            st.rerun()
        return
    
    # Check if visualizations exist
    if not st.session_state.visualizations:
        st.info("You haven't created any visualizations yet. Go to the Visualize page to create charts for your dashboard.")
        if st.button("Go to Visualization"):
            st.session_state.current_page = "Visualize"
            st.rerun()
        return
    
    # Dashboard title
    if "dashboard_title" not in st.session_state:
        st.session_state.dashboard_title = "InsightVista Dashboard"
    
    # Dashboard settings
    with st.expander("Dashboard Settings"):
        st.session_state.dashboard_title = st.text_input("Dashboard Title", value=st.session_state.dashboard_title)
        
        # Layout options
        st.write("**Layout Options**")
        layout_cols = st.slider("Number of columns", min_value=1, max_value=3, value=2)
        
        # Theme
        theme = st.selectbox(
            "Color theme",
            options=["light", "dark", "streamlit"]
        )
        
        # Auto-refresh option
        refresh_option = st.checkbox("Enable auto-refresh", value=False)
        if refresh_option:
            refresh_interval = st.number_input("Refresh interval (seconds)", min_value=5, max_value=300, value=60)
    
    # Display dashboard title
    st.subheader(st.session_state.dashboard_title)
    
    # Background image for dashboard header
    st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", use_column_width=True)  # Campaign Creators business intelligence image
    
    # Display visualizations in the selected layout
    if layout_cols == 1:
        for i, vis in enumerate(st.session_state.visualizations):
            with st.container():
                st.plotly_chart(vis["fig"], use_container_width=True)
                
                # Options for this visualization
                with st.expander(f"Options for {vis['title']}"):
                    if st.button("Remove from Dashboard", key=f"remove_{i}"):
                        st.session_state.visualizations.pop(i)
                        st.rerun()
                    
                    if st.button("Move Up", key=f"up_{i}") and i > 0:
                        st.session_state.visualizations[i], st.session_state.visualizations[i-1] = st.session_state.visualizations[i-1], st.session_state.visualizations[i]
                        st.rerun()
                    
                    if st.button("Move Down", key=f"down_{i}") and i < len(st.session_state.visualizations) - 1:
                        st.session_state.visualizations[i], st.session_state.visualizations[i+1] = st.session_state.visualizations[i+1], st.session_state.visualizations[i]
                        st.rerun()
    else:
        # Create rows with the specified number of columns
        for i in range(0, len(st.session_state.visualizations), layout_cols):
            cols = st.columns(layout_cols)
            
            for j in range(layout_cols):
                idx = i + j
                if idx < len(st.session_state.visualizations):
                    with cols[j]:
                        vis = st.session_state.visualizations[idx]
                        st.plotly_chart(vis["fig"], use_container_width=True)
                        
                        # Options for this visualization
                        with st.expander(f"Options for {vis['title']}"):
                            if st.button("Remove from Dashboard", key=f"remove_{idx}"):
                                st.session_state.visualizations.pop(idx)
                                st.rerun()
                            
                            if st.button("Move Up", key=f"up_{idx}") and idx > 0:
                                st.session_state.visualizations[idx], st.session_state.visualizations[idx-1] = st.session_state.visualizations[idx-1], st.session_state.visualizations[idx]
                                st.rerun()
                            
                            if st.button("Move Down", key=f"down_{idx}") and idx < len(st.session_state.visualizations) - 1:
                                st.session_state.visualizations[idx], st.session_state.visualizations[idx+1] = st.session_state.visualizations[idx+1], st.session_state.visualizations[idx]
                                st.rerun()
    
    # Dashboard actions
    st.divider()
    st.subheader("Dashboard Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add New Visualization"):
            st.session_state.current_page = "Visualize"
            st.rerun()
    
    with col2:
        if st.button("Clear Dashboard"):
            if st.session_state.visualizations:
                confirm = st.radio("Are you sure you want to clear the dashboard?", options=["No", "Yes"])
                if confirm == "Yes":
                    st.session_state.visualizations = []
                    st.success("Dashboard cleared")
                    st.rerun()
    
    with col3:
        if st.button("Export Dashboard"):
            # Convert plotly figures to JSON for export
            dashboard_export = {
                "title": st.session_state.dashboard_title,
                "layout": layout_cols,
                "visualizations": []
            }
            
            for vis in st.session_state.visualizations:
                vis_export = {
                    "title": vis["title"],
                    "type": vis["type"],
                    "params": vis["params"]
                }
                dashboard_export["visualizations"].append(vis_export)
            
            # Convert to JSON string
            dashboard_json = json.dumps(dashboard_export, indent=2)
            
            # Display download link (this is a workaround since we can't directly download files)
            st.download_button(
                label="Download Dashboard Configuration",
                data=dashboard_json,
                file_name="dashboard_config.json",
                mime="application/json"
            )
    
    # Navigation buttons
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Go to Insights", type="primary"):
            st.session_state.current_page = "Insights"
            st.rerun()
    
    with col2:
        if st.button("Back to Visualization"):
            st.session_state.current_page = "Visualize"
            st.rerun()
