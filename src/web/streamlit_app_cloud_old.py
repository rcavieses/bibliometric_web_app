#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streamlit web application for bibliometric analysis with Firebase integration.
Provides user authentication, secure API key management, and interactive analysis.
"""

import os
import sys
import json
import time
import tempfile
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Add the src directory to the Python path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Import the core modules
from config.config_manager import PipelineConfig
from core.pipeline_executor import PipelineExecutor
from web.auth_utils import (
    initialize_firebase_admin, sign_in_with_email_password, 
    signup_with_email_password, sign_out, ensure_auth_valid, 
    get_user_document, is_admin, reset_password
)

# Initialize Firebase with local credentials
@st.cache_resource
def initialize_firebase():
    """Initialize Firebase Admin SDK using local credentials file"""
    if not firebase_admin._apps:
        try:
            cred_path = os.path.join("secrets", "firebase_credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                return True
            else:
                st.error("Firebase credentials file not found in secrets directory")
                return False
        except Exception as e:
            st.error(f"Error initializing Firebase: {str(e)}")
            return False
    return True

# Firebase helper functions
def get_firestore_db():
    """Get Firestore database instance"""
    if initialize_firebase():
        return firestore.client()
    return None

def get_user_document(user_id):
    """Get user document from Firestore"""
    db = get_firestore_db()
    if db:
        return db.collection('users').document(user_id)
    return None

def get_api_key(service_name):
    """Get API key from local file"""
    try:
        key_paths = {
            'anthropic': os.path.join("secrets", "anthropic-apikey"),
            'sciencedirect': os.path.join("secrets", "sciencedirect_apikey.txt")
        }
        
        if service_name not in key_paths:
            return None
            
        key_path = key_paths[service_name]
        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                return f.read().strip()
    except Exception as e:
        st.error(f"Error loading API key for {service_name}: {str(e)}")
    return None

def log_api_usage(service_name, user_id):
    """Log API usage in Firestore"""
    db = get_firestore_db()
    if db:
        usage_ref = db.collection('api_usage').document()
        usage_ref.set({
            'service': service_name,
            'user_id': user_id,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

def log_search(user_id, search_params):
    """Log search parameters in Firestore"""
    db = get_firestore_db()
    if db:
        search_ref = db.collection('search_logs').document()
        search_ref.set({
            'user_id': user_id,
            'params': search_params,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

def save_results_to_firebase(user_id, results_name, results_data):
    """Save results to Firestore"""
    db = get_firestore_db()
    if db:
        # Convert to JSON string if needed
        if not isinstance(results_data, str):
            results_data = json.dumps(results_data)
        
        results_ref = db.collection('users').document(user_id).collection('results').document(results_name)
        results_ref.set({
            'data': results_data,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

def get_user_results(user_id):
    """Get user's saved results from Firestore"""
    db = get_firestore_db()
    if db:
        results = db.collection('users').document(user_id).collection('results').stream()
        return {doc.id: doc.to_dict() for doc in results}
    return {}

# Authentication functions
# User signup function is now handled by auth_utils.py
# The signup_user function has been replaced by signup_with_email_password

# Authentication functions are now handled by auth_utils.py
# The verify_user function has been replaced by sign_in_with_email_password

# Pipeline execution helpers
def run_pipeline(config):
    """Run the bibliometric analysis pipeline with the given configuration"""
    executor = PipelineExecutor(config)
    success = executor.execute_pipeline()
    return success, executor.get_execution_summary()

def setup_pipeline_config(search_params):
    """Create pipeline configuration from search parameters"""
    # Create temp directory for domain files if needed
    temp_dir = os.path.join(tempfile.gettempdir(), 'bibliometric_analysis')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create domain CSV files
    domain_files = {}
    for i, domain in enumerate(['domain1', 'domain2', 'domain3']):
        if domain in search_params and search_params[domain]:
            domain_path = os.path.join(temp_dir, f"Domain{i+1}.csv")
            with open(domain_path, 'w', encoding='utf-8') as f:
                for term in search_params[domain].split('\n'):
                    if term.strip():
                        f.write(f"{term.strip()}\n")
            domain_files[f"domain{i+1}_path"] = domain_path
    
    # Set up API keys - pass directly, the functions will get them from secrets
    api_keys = {}
    # We don't need to create temp files anymore as the API loading functions can read from secrets
    # Just use placeholder paths to maintain compatibility
    api_keys["anthropic_api_path"] = "anthropic-apikey"
    api_keys["sciencedirect_api_path"] = "sciencedirect_apikey.txt"
    
    # Create configuration
    config_params = {
        'max_results': int(search_params.get('max_results', 100)),
        'year_start': int(search_params.get('year_start', 2008)),
        'output_dir': os.path.join(temp_dir, 'outputs'),
        'figures_dir': os.path.join(temp_dir, 'figures'),
        **domain_files,
        **api_keys
    }
    
    # Add optional parameters
    if search_params.get('year_end'):
        config_params['year_end'] = int(search_params['year_end'])
    
    if search_params.get('email'):
        config_params['email'] = search_params['email']
    
    # Create the config object
    return PipelineConfig(**config_params)

# Streamlit UI components
def render_login_page():
    """Render the login/signup page"""
    st.title("Bibliometric Analysis - Login")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if email and password:
                user_id, message = sign_in_with_email_password(email, password)
                if user_id:
                    st.success(message)
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both email and password")
    
    with tab2:
        display_name = st.text_input("Display Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        
        if st.button("Sign Up", key="signup_button"):
            if display_name and email and password and password_confirm:
                if password == password_confirm:
                    user_id, message = signup_with_email_password(email, password, display_name)
                    if user_id:
                        st.success(message)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Passwords do not match")
            else:
                st.warning("Please fill in all fields")
    
    with tab3:
        email = st.text_input("Email", key="reset_email")
        
        if st.button("Send Reset Link", key="reset_button"):
            if email:
                success, message = reset_password(email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter your email address")

def render_search_page():
    """Render the search configuration page"""
    st.title("Bibliometric Analysis - Search Configuration")
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Search Parameters")
            max_results = st.number_input("Max Results per Source", min_value=10, max_value=1000, value=100, step=10)
            year_start = st.number_input("Start Year", min_value=1900, max_value=datetime.now().year, value=2008)
            year_end = st.number_input("End Year (optional)", min_value=1900, max_value=datetime.now().year, value=datetime.now().year)
            email = st.text_input("Email (for Crossref API)")
        
        with col2:
            st.subheader("Workflow Options")
            search_only = st.checkbox("Run Only Search Phase")
            analysis_only = st.checkbox("Run Only Analysis Phase")
            report_only = st.checkbox("Run Only Report Phase")
            generate_pdf = st.checkbox("Generate PDF Report")
        
        st.subheader("Domain Terms")
        tab1, tab2, tab3 = st.tabs(["Domain 1", "Domain 2", "Domain 3"])
        
        with tab1:
            domain1 = st.text_area(
                "Enter terms (one per line):", 
                value="artificial intelligence\nmachine learning\ndeep learning\nneural networks",
                height=150,
                key="domain1"
            )
        
        with tab2:
            domain2 = st.text_area(
                "Enter terms (one per line):", 
                value="forecast\nprediction\nforecasting\ntime series",
                height=150,
                key="domain2"
            )
        
        with tab3:
            domain3 = st.text_area(
                "Enter terms (one per line):", 
                value="fishery\nfisheries\nfish stock\naquaculture",
                height=150,
                key="domain3"
            )
        
        submitted = st.form_submit_button("Run Analysis")
        
        if submitted:
            # Collect search parameters
            search_params = {
                'max_results': max_results,
                'year_start': year_start,
                'year_end': year_end,
                'email': email,
                'domain1': domain1,
                'domain2': domain2,
                'domain3': domain3,
                'search_only': search_only,
                'analysis_only': analysis_only,
                'report_only': report_only,
                'generate_pdf': generate_pdf
            }
            
            # Log search parameters
            log_search(st.session_state["user_id"], search_params)
            
            # Update user's search count
            user_doc = get_user_document(st.session_state["user_id"])
            if user_doc:
                user_doc.update({
                    'search_count': firestore.Increment(1),
                    'last_search': firestore.SERVER_TIMESTAMP
                })
            
            # Set up pipeline config
            config = setup_pipeline_config(search_params)
            
            # Store parameters in session state for the execution page
            st.session_state['search_params'] = search_params
            st.session_state['pipeline_config'] = config
            st.session_state['page'] = 'execution'
            
            st.experimental_rerun()

def render_execution_page():
    """Render the pipeline execution page with progress tracking"""
    st.title("Bibliometric Analysis - Execution")
    
    if 'pipeline_config' not in st.session_state or 'search_params' not in st.session_state:
        st.error("Missing configuration. Please go back to the search page.")
        st.button("Back to Search", on_click=lambda: st.session_state.update({'page': 'search'}))
        return
    
    config = st.session_state['pipeline_config']
    search_params = st.session_state['search_params']
    
    # Display search parameters
    with st.expander("Search Parameters", expanded=False):
        st.json(search_params)
    
    # Progress placeholder
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Execute pipeline in the main thread (for simplicity)
    # In a production app, you would use background jobs
    status_text.text("Starting pipeline execution...")
    
    # Define phase names and weights for progress calculation
    phases = [
        ("Search", 0.2),
        ("Integration", 0.1),
        ("Domain Analysis", 0.2),
        ("Classification", 0.3),
        ("Analysis Generation", 0.1),
        ("Report Generation", 0.1)
    ]
    
    try:
        # Mock execution for demonstration
        # In a real app, you would call run_pipeline(config) and track progress
        for i, (phase_name, weight) in enumerate(phases):
            # Skip phases based on user options
            if search_params.get('search_only') and i > 0:
                continue
            if search_params.get('analysis_only') and (i < 2 or i > 4):
                continue
            if search_params.get('report_only') and i < 5:
                continue
            
            status_text.text(f"Executing {phase_name} phase...")
            
            # Simulate phase execution
            for j in range(10):
                # Calculate progress
                phase_progress = j / 10
                overall_progress = sum([w for _, w in phases[:i]]) + (phase_progress * weight)
                progress_bar.progress(min(overall_progress, 1.0))
                time.sleep(0.2)  # Simulate work
        
        # Complete the progress
        progress_bar.progress(1.0)
        status_text.text("Pipeline execution completed successfully!")
        
        # Save results to Firebase
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_results_to_firebase(
            st.session_state["user_id"],
            f"analysis_results_{timestamp}",
            {"search_params": search_params, "timestamp": timestamp}
        )
        
        # Show success message and provide results view option
        st.success("Analysis completed! Your results have been saved.")
        if st.button("View Results"):
            st.session_state['page'] = 'results'
            st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error executing pipeline: {str(e)}")
        st.button("Back to Search", on_click=lambda: st.session_state.update({'page': 'search'}))

def render_results_page():
    """Render the results visualization page"""
    st.title("Bibliometric Analysis - Results")
    
    # Get user's saved results
    user_results = get_user_results(st.session_state["user_id"])
    
    if not user_results:
        st.warning("No saved results found. Run an analysis first.")
        st.button("Back to Search", on_click=lambda: st.session_state.update({'page': 'search'}))
        return
    
    # Allow user to select which result to view
    result_options = list(user_results.keys())
    selected_result = st.selectbox("Select Result", result_options)
    
    if selected_result:
        result_data = user_results[selected_result]
        timestamp = result_data.get('timestamp', datetime.now())
        
        st.subheader(f"Results from {timestamp}")
        
        # Display tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Publication Trends", "Domain Distribution", "Top Journals", "Classification"])
        
        with tab1:
            st.subheader("Publications by Year")
            # In a real app, you would load and display actual visualization data
            chart_data = pd.DataFrame({
                'Year': list(range(2008, 2023)),
                'Publications': [10, 15, 22, 27, 31, 36, 48, 52, 65, 72, 85, 93, 112, 125, 130]
            })
            st.line_chart(chart_data, x="Year", y="Publications")
        
        with tab2:
            st.subheader("Domain Distribution")
            domain_data = pd.DataFrame({
                'Domain': ["AI/ML", "Forecasting", "Fisheries", "AI+Forecasting", "AI+Fisheries", "Forecasting+Fisheries", "All Three"],
                'Count': [250, 180, 120, 80, 60, 40, 25]
            })
            st.bar_chart(domain_data, x="Domain", y="Count")
        
        with tab3:
            st.subheader("Top Journals")
            journals_data = pd.DataFrame({
                'Journal': ["Nature", "Science", "PLOS ONE", "Scientific Reports", "Fisheries Research"],
                'Articles': [28, 25, 22, 20, 18]
            })
            st.bar_chart(journals_data, x="Journal", y="Articles")
        
        with tab4:
            st.subheader("Model Classification")
            model_data = pd.DataFrame({
                'Model': ["Neural Networks", "Random Forest", "Support Vector Machines", "Decision Trees", "Other"],
                'Count': [45, 32, 25, 18, 30]
            })
            st.pie_chart(model_data)
        
        # Download options
        st.subheader("Download Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "Download Data (CSV)",
                data=result_data.get('data', "{}"),
                file_name=f"bibliometric_results_{timestamp.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                "Download Report (MD)",
                data=result_data.get('data', "{}"),
                file_name=f"bibliometric_report_{timestamp.strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        
        with col3:
            st.download_button(
                "Download Visualizations (ZIP)",
                data=result_data.get('data', "{}"),
                file_name=f"bibliometric_figures_{timestamp.strftime('%Y%m%d')}.zip",
                mime="application/zip"
            )

def render_profile_page():
    """Render the user profile page"""
    st.title("User Profile")
    
    # Get user information
    user_doc = get_user_document(st.session_state["user_id"])
    if not user_doc:
        st.error("Could not retrieve user information")
        return
    
    user_data = user_doc.get().to_dict()
    
    # Display user information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account Information")
        st.write(f"**Name:** {user_data.get('display_name', 'N/A')}")
        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
        st.write(f"**Role:** {user_data.get('role', 'user')}")
        st.write(f"**Joined:** {user_data.get('created_at', 'N/A')}")
        
        # Edit profile button
        if st.button("Edit Profile"):
            st.session_state['edit_profile'] = True
    
    with col2:
        st.subheader("Usage Statistics")
        st.write(f"**Searches:** {user_data.get('search_count', 0)}")
        st.write(f"**Last Search:** {user_data.get('last_search', 'Never')}")
        
        # Display API quota information
        api_quotas = {
            "Anthropic API": {"used": 150, "limit": 500, "reset": "April 30, 2025"},
            "Science Direct API": {"used": 75, "limit": 200, "reset": "April 15, 2025"}
        }
        
        st.subheader("API Usage")
        for api, quota in api_quotas.items():
            st.write(f"**{api}:**")
            st.progress(quota['used'] / quota['limit'])
            st.write(f"{quota['used']} of {quota['limit']} calls used (resets {quota['reset']})")
    
    # Edit profile form (conditionally displayed)
    if st.session_state.get('edit_profile', False):
        st.subheader("Edit Profile")
        
        with st.form("profile_form"):
            display_name = st.text_input("Display Name", value=user_data.get('display_name', ''))
            email = st.text_input("Email", value=user_data.get('email', ''), disabled=True)
            
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                # Update user profile in Firestore
                user_doc.update({
                    'display_name': display_name
                })
                st.success("Profile updated successfully!")
                st.session_state['edit_profile'] = False
                time.sleep(1)
                st.experimental_rerun()
    
    # Recent searches
    st.subheader("Recent Searches")
    
    db = get_firestore_db()
    if db:
        # Get recent searches for this user
        searches = db.collection('search_logs') \
                    .where('user_id', '==', st.session_state["user_id"]) \
                    .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                    .limit(5) \
                    .stream()
        
        for search in searches:
            search_data = search.to_dict()
            params = search_data.get('params', {})
            timestamp = search_data.get('timestamp', datetime.now())
            
            with st.expander(f"Search on {timestamp}"):
                domains = []
                if params.get('domain1'):
                    domains.append("Domain 1")
                if params.get('domain2'):
                    domains.append("Domain 2")
                if params.get('domain3'):
                    domains.append("Domain 3")
                
                st.write(f"**Domains:** {', '.join(domains)}")
                st.write(f"**Max Results:** {params.get('max_results', 'N/A')}")
                st.write(f"**Year Range:** {params.get('year_start', 'N/A')} - {params.get('year_end', 'N/A')}")
                
                # Add button to rerun this search
                if st.button("Rerun Search", key=f"rerun_{search.id}"):
                    st.session_state['search_params'] = params
                    st.session_state['page'] = 'search'
                    st.experimental_rerun()
    else:
        st.warning("Could not retrieve search history")

def render_api_settings_page():
    """Render the API settings page"""
    st.title("API Settings")
    
    # Verify user is authenticated
    if not ensure_auth_valid():
        st.error("Please log in to access API settings")
        return
        
    # Check if user has admin privileges
    if not is_admin():
        st.warning("You need administrator privileges to manage API keys.")
        return
    
    # Get Firestore database
    db = get_firestore_db()
    if not db:
        st.error("Could not connect to database")
        return