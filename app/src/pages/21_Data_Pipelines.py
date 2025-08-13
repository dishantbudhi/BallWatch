import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import logging
import time
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Data Pipelines - BallWatch",
    layout="wide"
)

SideBarLinks()

if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'http://api:4000/'

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

def api_get(endpoint):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        if st.session_state.debug_mode:
            with st.expander("Debug Info", expanded=False):
                st.write(f"**GET Request:** `{full_url}`")
                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data
            except ValueError:
                logger.error(f"Invalid JSON response from {endpoint}")
                return None
        else:
            logger.error(f"API Error {response.status_code} for {endpoint}: {response.text[:200]}")
            
            if response.status_code == 404:
                st.error(f"Endpoint not found: {endpoint}")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Server error occurred')
                    st.error(f"Server Error: {error_msg}")
                except:
                    st.error("Server error occurred. Please try again later.")
            elif response.status_code == 403:
                st.error("Access denied. Please check your permissions.")
            elif response.status_code == 400:
                st.error("Invalid request. Please check your input.")
            
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {endpoint}")
        st.error("Cannot connect to server. Please check if the API is running.")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error for {endpoint}")
        st.error("Request timed out. Please try again.")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")
        return None

def api_post(endpoint, data):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        if st.session_state.debug_mode:
            with st.expander("Debug Info", expanded=False):
                st.write(f"**POST Request:** `{full_url}`")
                st.write(f"**Payload:** {data}")
                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(
            full_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            try:
                json_data = response.json()
                return json_data
            except ValueError:
                logger.error(f"Invalid JSON response from {endpoint}")
                return None
        else:
            logger.error(f"API Error {response.status_code} for {endpoint}: {response.text[:200]}")
            
            if response.status_code == 404:
                st.error(f"Endpoint not found: {endpoint}")
            elif response.status_code == 500:
                st.error("Server error occurred. Please check the backend logs.")
            elif response.status_code == 400:
                st.error("Invalid request data. Please check your input.")
            elif response.status_code == 409:
                st.error("A data load of this type is already running.")
            
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {endpoint}")
        st.error("Cannot connect to server. Please check if the API is running.")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error for {endpoint}")
        st.error("Request timed out. Please try again.")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")
        return None

def api_put(endpoint, data):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        if st.session_state.debug_mode:
            with st.expander("Debug Info", expanded=False):
                st.write(f"**PUT Request:** `{full_url}`")
                st.write(f"**Payload:** {data}")
                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.put(
            full_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data
            except ValueError:
                logger.error(f"Invalid JSON response from {endpoint}")
                return None
        else:
            logger.error(f"API Error {response.status_code} for {endpoint}: {response.text[:200]}")
            
            if response.status_code == 404:
                st.error("Resource not found.")
            elif response.status_code == 500:
                st.error("Server error occurred. Please try again.")
            elif response.status_code == 400:
                st.error("Invalid update data.")
            
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {endpoint}")
        st.error("Cannot connect to server.")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {str(e)}")
        st.error("An unexpected error occurred.")
        return None

# Main Page
st.title("Data Pipelines")
st.markdown("Manage and monitor data loads for BallWatch")

# Add debug mode toggle in sidebar
with st.sidebar:
    st.divider()
    st.session_state.debug_mode = st.checkbox("Debug Mode", value=st.session_state.debug_mode)
    if st.session_state.debug_mode:
        st.info("Debug mode enabled - verbose error details will be shown")

# Quick Actions Section
st.subheader("Start New Data Load")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Load Player Stats", type="primary", use_container_width=True):
        with st.spinner("Starting player stats load..."):
            result = api_post('/system/data-loads', {
                'load_type': 'player_stats',
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()

with col2:
    if st.button("Load Game Data", type="primary", use_container_width=True):
        with st.spinner("Starting game data load..."):
            result = api_post('/system/data-loads', {
                'load_type': 'game_data', 
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()

with col3:
    if st.button("Load Team Data", type="primary", use_container_width=True):
        with st.spinner("Starting team data load..."):
            result = api_post('/system/data-loads', {
                'load_type': 'team_data',
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()

st.divider()

# Data Loads History Section
st.subheader("Data Load History")

# Filters
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    search_term = st.text_input("Search loads", placeholder="Filter by load type or user...")
with col2:
    status_filter = st.selectbox("Status", ["All", "pending", "running", "completed", "failed"])
with col3:
    days_filter = st.number_input("Days back", min_value=1, max_value=365, value=7)
with col4:
    if st.button("Refresh", use_container_width=True):
        st.rerun()

# Fetch data loads
with st.spinner("Loading data..."):
    endpoint = f'/system/data-loads?days={days_filter}'
    if status_filter != "All":
        endpoint += f'&status={status_filter}'
    
    loads_data = api_get(endpoint)

if loads_data:
    loads = loads_data.get('loads', [])
    
    if st.session_state.debug_mode:
        with st.expander("Debug: Raw API Response"):
            st.json(loads_data)
    
    if loads:
        df = pd.DataFrame(loads)
        
        # Apply search filter
        if search_term:
            mask = df.apply(lambda x: search_term.lower() in str(x).lower(), axis=1)
            df = df[mask]
        
        if not df.empty:
            # Convert datetime strings to more readable format
            if 'started_at' in df.columns:
                df['started_at'] = pd.to_datetime(df['started_at']).dt.strftime('%Y-%m-%d %H:%M')
            if 'completed_at' in df.columns:
                df['completed_at'] = pd.to_datetime(df['completed_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Add status indicators
            df['status_display'] = df['status'].apply(
                lambda x: f"COMPLETED" if x == 'completed' 
                else f"FAILED" if x == 'failed'
                else f"RUNNING" if x == 'running'
                else f"PENDING"
            )
            
            # Display table with better column configuration
            st.dataframe(
                df[['load_id', 'load_type', 'status_display', 'started_at', 'completed_at', 
                   'records_processed', 'records_failed', 'initiated_by']],
                column_config={
                    "load_id": st.column_config.NumberColumn("Load ID", width="small"),
                    "load_type": "Type",
                    "status_display": "Status",
                    "started_at": "Started",
                    "completed_at": "Completed",
                    "records_processed": st.column_config.NumberColumn("Processed", format="%d"),
                    "records_failed": st.column_config.NumberColumn("Failed", format="%d"),
                    "initiated_by": "Initiated By"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Handle running loads with auto-refresh
            running_loads = df[df['status'] == 'running']
            if not running_loads.empty:
                st.info(f"{len(running_loads)} load(s) currently running. Page will auto-refresh.")
                time.sleep(2)
                st.rerun()
            
            # Summary metrics
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Loads", len(df))
            with col2:
                completed_loads = len(df[df['status'] == 'completed'])
                st.metric("Completed", completed_loads)
            with col3:
                failed_loads = len(df[df['status'] == 'failed'])
                st.metric("Failed", failed_loads, delta=f"-{failed_loads}" if failed_loads > 0 else None)
            with col4:
                total_processed = df['records_processed'].sum() if 'records_processed' in df.columns else 0
                st.metric("Total Records", f"{total_processed:,}")
                    
        else:
            st.info(f"No data loads found matching your filters.")
    else:
        st.info("No data loads found in the database. Start a new load using the buttons above.")
        
        # Show what's in the response for debugging
        if st.session_state.debug_mode:
            st.write("API Response keys:", list(loads_data.keys()))
else:
    # Show a simple warning without all the debug details
    st.warning("Unable to connect to the API server")
    
    # Add a helpful expander with troubleshooting steps
    with st.expander("Troubleshooting Steps"):
        st.markdown("""
        1. **Check if the API server is running**
           - For Docker: `docker-compose ps`
           - For local: Check the terminal running Flask
        
        2. **Verify the DataLoads table exists**
           ```sql
           CREATE TABLE IF NOT EXISTS DataLoads (
               load_id INT AUTO_INCREMENT PRIMARY KEY,
               load_type VARCHAR(50) NOT NULL,
               status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
               started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               completed_at TIMESTAMP NULL,
               records_processed INT DEFAULT 0,
               records_failed INT DEFAULT 0,
               error_message TEXT,
               source_file VARCHAR(255),
               initiated_by VARCHAR(100)
           );
           ```
        
        3. **Check Flask logs for errors**
           - Docker: `docker-compose logs api`
           - Local: Check Flask terminal output
        """)
    
    # Show demo data
    st.info("Showing demo data for visualization purposes")
    
    mock_data = [
        {
            'load_id': 1,
            'load_type': 'player_stats', 
            'status': 'completed',
            'started_at': '2025-01-25 02:00:00',
            'completed_at': '2025-01-25 02:15:30',
            'records_processed': 450,
            'records_failed': 0,
            'initiated_by': 'system'
        },
        {
            'load_id': 2,
            'load_type': 'game_data',
            'status': 'running', 
            'started_at': '2025-01-25 14:30:00',
            'completed_at': None,
            'records_processed': 234,
            'records_failed': 0,
            'initiated_by': 'Mike Lewis'
        }
    ]
    
    df = pd.DataFrame(mock_data)
    df['status_display'] = df['status'].apply(
        lambda x: f"COMPLETED" if x == 'completed' else f"RUNNING"
    )
    
    st.dataframe(
        df[['load_id', 'load_type', 'status_display', 'started_at', 'completed_at', 
           'records_processed', 'records_failed', 'initiated_by']],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# System Health Check
st.subheader("System Health Status")

with st.spinner("Checking system health..."):
    health_data = api_get('/system/health')

if health_data:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('status', 'unknown')
        st.metric("System Status", status.upper())
    
    with col2:
        db_status = health_data.get('database_status', 'unknown')
        st.metric("Database", db_status.upper())
    
    with col3:
        errors = health_data.get('recent_errors_24h', 0)
        st.metric("Errors (24h)", errors)
    
    with col4:
        active_loads = health_data.get('active_data_loads', 0)
        st.metric("Active Loads", active_loads)
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("System Status", "OFFLINE")
    with col2:
        st.metric("Database", "UNKNOWN")
    with col3:
        st.metric("Errors (24h)", "N/A")
    with col4:
        st.metric("Active Loads", "N/A")