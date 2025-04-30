import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from components import data_import, data_cleaning, visualization, dashboard, insights, export
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo

# Set page configuration
st.set_page_config(
    page_title="InsightVista | No-Code Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css(".streamlit/style.css")
except Exception as e:
    st.write(f"Note: Custom styling not loaded. {str(e)}")

# Function to load and display SVG images
def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
    
    b64_svg = base64.b64encode(svg_content.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b64_svg}" class="svg-image">'

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = None
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = None
if 'transformations' not in st.session_state:
    st.session_state.transformations = []
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = []
if 'dashboard_items' not in st.session_state:
    st.session_state.dashboard_items = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Header with custom styling
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.markdown(render_svg("assets/logo.svg"), unsafe_allow_html=True)
    except Exception as e:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", width=80)
with col2:
    st.title("InsightVista")
    st.markdown("<p class='subtitle'>A Powerful No-Code Data Analytics Platform</p>", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    try:
        st.markdown(render_svg("assets/sidebar_banner.svg"), unsafe_allow_html=True)
    except Exception as e:
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f", use_container_width=True)
    
    st.title("Navigation")
    
    # Reset/Refresh Button
    if st.button("🔄 Refresh App", key="refresh_app", use_container_width=True, type="primary"):
        # Reset session state variables
        for key in list(st.session_state.keys()):
            if key not in ['_is_running', '_streamlit_container_height']:
                del st.session_state[key]
        
        # Reinitialize essential variables
        st.session_state.data = None
        st.session_state.cleaned_data = None
        st.session_state.transformations = []
        st.session_state.visualizations = []
        st.session_state.dashboard_items = []
        st.session_state.current_page = "Home"
        st.rerun()
    
    st.divider()
    
    # Navigation buttons with better UI
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("🏠 Home", key="home_nav", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()
    
    with nav_col2:
        if st.button("📤 Import", key="import_nav", use_container_width=True):
            st.session_state.current_page = "Import Data"
            st.rerun()
    
    # Only show these options if data is imported
    if st.session_state.data is not None:
        clean_col, vis_col = st.columns(2)
        with clean_col:
            if st.button("🧹 Clean", key="clean_nav", use_container_width=True):
                st.session_state.current_page = "Clean Data"
                st.rerun()
        with vis_col:
            if st.button("📊 Visualize", key="visualize_nav", use_container_width=True):
                st.session_state.current_page = "Visualize"
                st.rerun()
        
        dash_col, insights_col = st.columns(2)
        with dash_col:
            if st.button("📋 Dashboard", key="dashboard_nav", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
        with insights_col:
            if st.button("💡 Insights", key="insights_nav", use_container_width=True):
                st.session_state.current_page = "Insights"
                st.rerun()
        
        if st.button("📥 Export Results", key="export_nav", use_container_width=True):
            st.session_state.current_page = "Export"
            st.rerun()
    
    st.divider()
    st.caption("© 2023 InsightVista | Powered by OpenPyXL & Streamlit")

# Main content area based on the selected page
if st.session_state.current_page == "Home":
    # Hero section with banner
    try:
        st.markdown(render_svg("assets/banner.svg"), unsafe_allow_html=True)
    except Exception as e:
        st.header("Welcome to InsightVista")
    
    st.markdown("<h2 class='centered-text'>Turn Raw Data into Actionable Insights</h2>", unsafe_allow_html=True)
    st.write("""
    InsightVista is a powerful no-code data analytics platform that empowers you to:
    
    * **Import** data from CSV and Excel files with ease
    * **Clean and transform** your data with an intuitive interface
    * **Create beautiful, interactive visualizations** without coding
    * **Build custom dashboards** with drag-and-drop simplicity
    * **Discover automated insights** with AI-powered analytics
    * **Export and share** your findings with stakeholders
    
    Get started by importing your data!
    """)
    
    # Quick start button - centered with custom styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started Now", type="primary", key="get_started", use_container_width=True):
            st.session_state.current_page = "Import Data"
            st.rerun()
    
    st.divider()
    
    # Features section with custom header
    colored_header(
        label="Key Features",
        description="Everything you need for powerful data analysis",
        color_name="blue-70"
    )
    
    # Using SVG for one feature and creating a cleaner UI
    feature_cols = st.columns(3)
    with feature_cols[0]:
        try:
            st.markdown(render_svg("assets/feature_import.svg"), unsafe_allow_html=True)
        except Exception as e:
            st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3", use_container_width=True)
        st.markdown("<h3 class='feature-title'>📤 Easy Data Import</h3>", unsafe_allow_html=True)
        st.write("Import data from CSV, Excel, and other formats with just a few clicks. No coding required.")
    
    with feature_cols[1]:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", use_container_width=True)
        st.markdown("<h3 class='feature-title'>📊 Interactive Visualizations</h3>", unsafe_allow_html=True)
        st.write("Create stunning charts, graphs, and dashboards without writing a single line of code.")
    
    with feature_cols[2]:
        st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", use_container_width=True)
        st.markdown("<h3 class='feature-title'>🧠 Automated Insights</h3>", unsafe_allow_html=True)
        st.write("Leverage advanced analytics to discover patterns, trends, and insights in your data automatically.")

elif st.session_state.current_page == "Import Data":
    data_import.show()

elif st.session_state.current_page == "Clean Data":
    data_cleaning.show()

elif st.session_state.current_page == "Visualize":
    visualization.show()

elif st.session_state.current_page == "Dashboard":
    dashboard.show()

elif st.session_state.current_page == "Insights":
    insights.show()

elif st.session_state.current_page == "Export":
    export.show()
