import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import logging
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Data Pipelines - BallWatch",
    layout="wide"
)

# Use the SideBarLinks function to control navigation
SideBarLinks()

# Initialize session state
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'http://api:4000/api'

# API Helper Functions
def api_get(endpoint):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        st.write("---")
        st.write("🔍 **DEBUG: GET REQUEST DETAILS**")
        st.write(f"**Full URL:** `{full_url}`")
        st.write(f"**Base URL:** `{st.session_state.api_base_url}`")
        st.write(f"**Endpoint:** `{endpoint}`")
        st.write(f"**Method:** GET")
        st.write(f"**Timeout:** 10 seconds")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(full_url, timeout=10)
        
        st.write("📡 **RESPONSE DETAILS**")
        st.write(f"**Status Code:** {response.status_code}")
        st.write(f"**Status Text:** {response.reason}")
        st.write(f"**Response Headers:** {dict(response.headers)}")
        st.write(f"**Content Type:** {response.headers.get('Content-Type', 'Unknown')}")
        st.write(f"**Content Length:** {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                st.success(f"✅ **SUCCESS:** API call completed successfully")
                st.write(f"**Response JSON Keys:** {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dictionary'}")
                return json_data
            except ValueError as json_error:
                st.error(f"❌ **JSON PARSE ERROR:** Response is not valid JSON")
                st.error(f"**JSON Error:** {str(json_error)}")
                st.error(f"**Raw Response:** {response.text[:1000]}")
                return None
        else:
            st.error(f"❌ **HTTP ERROR:** Server returned error status")
            st.error(f"**Status Code:** {response.status_code}")
            st.error(f"**Status Message:** {response.reason}")
            st.error(f"**Response Body:** {response.text[:1000]}")
            
            # Specific error code explanations
            if response.status_code == 404:
                st.error("🔍 **404 NOT FOUND:** The endpoint does not exist on the server")
                st.info("**Possible causes:** Wrong URL path, endpoint not implemented, typo in route")
            elif response.status_code == 500:
                st.error("💥 **500 INTERNAL SERVER ERROR:** Server encountered an error")
                st.info("**Possible causes:** Database error, unhandled exception in backend code")
            elif response.status_code == 403:
                st.error("🚫 **403 FORBIDDEN:** Access denied")
                st.info("**Possible causes:** Authentication required, insufficient permissions")
            elif response.status_code == 400:
                st.error("📝 **400 BAD REQUEST:** Invalid request format")
                st.info("**Possible causes:** Missing parameters, invalid JSON, wrong data format")
            
            return None
            
    except requests.exceptions.ConnectionError as e:
        st.error("🔌 **CONNECTION ERROR:** Cannot establish connection to server")
        st.error(f"**Error Type:** ConnectionError")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        
        st.info("🔧 **TROUBLESHOOTING STEPS:**")
        st.info("1. Check if the API server is running")
        st.info("2. Verify the server is listening on port 4000")
        st.info("3. Test with: `curl http://api:4000/api/system-health`")
        st.info("4. Check Docker container networking")
        st.info("5. Verify API service name 'api' is correct in Docker")
        st.info("6. Check firewall/network security groups")
        
        return None
        
    except requests.exceptions.Timeout as e:
        st.error("⏰ **TIMEOUT ERROR:** Request took longer than 10 seconds")
        st.error(f"**Error Type:** Timeout")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        
        st.info("🔧 **TROUBLESHOOTING STEPS:**")
        st.info("1. Server might be overloaded or slow")
        st.info("2. Database queries might be taking too long")
        st.info("3. Network latency issues")
        st.info("4. Try again in a few seconds")
        
        return None
        
    except requests.exceptions.HTTPError as e:
        st.error("📡 **HTTP ERROR:** Invalid HTTP response")
        st.error(f"**Error Type:** HTTPError")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        return None
        
    except requests.exceptions.RequestException as e:
        st.error("🌐 **REQUEST ERROR:** Generic request failure")
        st.error(f"**Error Type:** {type(e).__name__}")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        return None
        
    except Exception as e:
        st.error("💥 **UNEXPECTED ERROR:** Unknown error occurred")
        st.error(f"**Error Type:** {type(e).__name__}")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Python Exception:** {e.__class__.__module__}.{e.__class__.__name__}")
        
        import traceback
        st.error("**Full Traceback:**")
        st.code(traceback.format_exc())
        
        return None

def api_post(endpoint, data):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        st.write("---")
        st.write("🔍 **DEBUG: POST REQUEST DETAILS**")
        st.write(f"**Full URL:** `{full_url}`")
        st.write(f"**Base URL:** `{st.session_state.api_base_url}`")
        st.write(f"**Endpoint:** `{endpoint}`")
        st.write(f"**Method:** POST")
        st.write(f"**Content-Type:** application/json")
        st.write(f"**Timeout:** 10 seconds")
        st.write(f"**Payload Size:** {len(str(data))} characters")
        st.write(f"**Payload:** {data}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(
            full_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        st.write("📡 **RESPONSE DETAILS**")
        st.write(f"**Status Code:** {response.status_code}")
        st.write(f"**Status Text:** {response.reason}")
        st.write(f"**Response Headers:** {dict(response.headers)}")
        st.write(f"**Content Type:** {response.headers.get('Content-Type', 'Unknown')}")
        st.write(f"**Content Length:** {len(response.content)} bytes")
        
        if response.status_code in [200, 201]:
            try:
                json_data = response.json()
                st.success(f"✅ **SUCCESS:** POST request completed successfully")
                st.write(f"**Response JSON Keys:** {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dictionary'}")
                return json_data
            except ValueError as json_error:
                st.error(f"❌ **JSON PARSE ERROR:** Response is not valid JSON")
                st.error(f"**JSON Error:** {str(json_error)}")
                st.error(f"**Raw Response:** {response.text[:1000]}")
                return None
        else:
            st.error(f"❌ **HTTP ERROR:** Server returned error status")
            st.error(f"**Status Code:** {response.status_code}")
            st.error(f"**Status Message:** {response.reason}")
            st.error(f"**Response Body:** {response.text[:1000]}")
            
            # Specific error code explanations
            if response.status_code == 404:
                st.error("🔍 **404 NOT FOUND:** The endpoint does not exist on the server")
                st.info("**Possible causes:** Wrong URL path, endpoint not implemented, typo in route")
            elif response.status_code == 500:
                st.error("💥 **500 INTERNAL SERVER ERROR:** Server encountered an error")
                st.info("**Possible causes:** Database error, unhandled exception in backend code, invalid data format")
            elif response.status_code == 400:
                st.error("📝 **400 BAD REQUEST:** Invalid request format or data")
                st.info("**Possible causes:** Missing required fields, invalid JSON structure, wrong data types")
                st.info(f"**Expected fields for {endpoint}:** Check your admin_routes.py for required fields")
            elif response.status_code == 409:
                st.error("⚠️ **409 CONFLICT:** Resource conflict")
                st.info("**Possible causes:** Duplicate data, resource already exists, concurrent access issue")
            
            return None
            
    except requests.exceptions.ConnectionError as e:
        st.error("🔌 **CONNECTION ERROR:** Cannot establish connection to server")
        st.error(f"**Error Type:** ConnectionError")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        
        st.info("🔧 **TROUBLESHOOTING STEPS:**")
        st.info("1. Check if the API server is running")
        st.info("2. Verify the server is listening on port 4000")
        st.info("3. Test with: `curl -X POST -H 'Content-Type: application/json' -d '{}' http://api:4000/api/data-loads`")
        st.info("4. Check Docker container networking")
        st.info("5. Verify API service name 'api' is correct")
        
        return None
        
    except requests.exceptions.Timeout as e:
        st.error("⏰ **TIMEOUT ERROR:** Request took longer than 10 seconds")
        st.error(f"**Error Type:** Timeout")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        return None
        
    except requests.exceptions.RequestException as e:
        st.error("🌐 **REQUEST ERROR:** Generic request failure")
        st.error(f"**Error Type:** {type(e).__name__}")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        return None
        
    except Exception as e:
        st.error("💥 **UNEXPECTED ERROR:** Unknown error occurred")
        st.error(f"**Error Type:** {type(e).__name__}")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        
        import traceback
        st.error("**Full Traceback:**")
        st.code(traceback.format_exc())
        
        return None

def api_put(endpoint, data):
    full_url = f"{st.session_state.api_base_url}{endpoint}"
    try:
        st.write("---")
        st.write("🔍 **DEBUG: PUT REQUEST DETAILS**")
        st.write(f"**Full URL:** `{full_url}`")
        st.write(f"**Base URL:** `{st.session_state.api_base_url}`")
        st.write(f"**Endpoint:** `{endpoint}`")
        st.write(f"**Method:** PUT")
        st.write(f"**Content-Type:** application/json")
        st.write(f"**Timeout:** 10 seconds")
        st.write(f"**Payload Size:** {len(str(data))} characters")
        st.write(f"**Payload:** {data}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.put(
            full_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        st.write("📡 **RESPONSE DETAILS**")
        st.write(f"**Status Code:** {response.status_code}")
        st.write(f"**Status Text:** {response.reason}")
        st.write(f"**Response Headers:** {dict(response.headers)}")
        st.write(f"**Content Type:** {response.headers.get('Content-Type', 'Unknown')}")
        st.write(f"**Content Length:** {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                st.success(f"✅ **SUCCESS:** PUT request completed successfully")
                st.write(f"**Response JSON Keys:** {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dictionary'}")
                return json_data
            except ValueError as json_error:
                st.error(f"❌ **JSON PARSE ERROR:** Response is not valid JSON")
                st.error(f"**JSON Error:** {str(json_error)}")
                st.error(f"**Raw Response:** {response.text[:1000]}")
                return None
        else:
            st.error(f"❌ **HTTP ERROR:** Server returned error status")
            st.error(f"**Status Code:** {response.status_code}")
            st.error(f"**Status Message:** {response.reason}")
            st.error(f"**Response Body:** {response.text[:1000]}")
            
            # Specific error code explanations
            if response.status_code == 404:
                st.error("🔍 **404 NOT FOUND:** The resource does not exist")
                st.info("**Possible causes:** Invalid load ID, resource was deleted, wrong endpoint")
            elif response.status_code == 500:
                st.error("💥 **500 INTERNAL SERVER ERROR:** Server encountered an error")
                st.info("**Possible causes:** Database error, invalid update data, constraint violations")
            elif response.status_code == 400:
                st.error("📝 **400 BAD REQUEST:** Invalid update data")
                st.info("**Possible causes:** Missing fields, invalid status values, wrong data types")
            
            return None
            
    except requests.exceptions.ConnectionError as e:
        st.error("🔌 **CONNECTION ERROR:** Cannot establish connection to server")
        st.error(f"**Error Type:** ConnectionError")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        return None
        
    except Exception as e:
        st.error("💥 **UNEXPECTED ERROR:** Unknown error occurred during PUT")
        st.error(f"**Error Type:** {type(e).__name__}")
        st.error(f"**Error Details:** {str(e)}")
        st.error(f"**Target URL:** {full_url}")
        st.error(f"**Request Data:** {data}")
        
        import traceback
        st.error("**Full Traceback:**")
        st.code(traceback.format_exc())
        
        return None

# Main Page
st.title("Data Pipelines")
st.markdown("Manage and monitor data loads for BallWatch")

# Quick Actions Section
st.subheader("Start New Data Load")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Load Player Stats", type="primary", use_container_width=True):
        with st.spinner("Starting player stats load..."):
            result = api_post('/data-loads', {
                'load_type': 'player_stats',
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()
            else:
                st.error("Failed to start load")

with col2:
    if st.button("Load Game Data", type="primary", use_container_width=True):
        with st.spinner("Starting game data load..."):
            result = api_post('/data-loads', {
                'load_type': 'game_data', 
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()
            else:
                st.error("Failed to start load")

with col3:
    if st.button("Load Team Data", type="primary", use_container_width=True):
        with st.spinner("Starting team data load..."):
            result = api_post('/data-loads', {
                'load_type': 'team_data',
                'initiated_by': 'Mike Lewis'
            })
            if result:
                st.success(f"Load started successfully! Load ID: {result.get('load_id')}")
                st.rerun()
            else:
                st.error("Failed to start load")

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

# Fetch data loads (using backend's default 30-day filter)
loads_data = api_get('/data-loads')

if loads_data:
    loads = loads_data.get('loads', [])
    
    if loads:
        df = pd.DataFrame(loads)
        
        # Apply search filter
        if search_term:
            mask = df.apply(lambda x: search_term.lower() in str(x).lower(), axis=1)
            df = df[mask]
        
        if not df.empty:
            # Add status indicators
            df['status_display'] = df['status'].apply(
                lambda x: f"🟢 {x.upper()}" if x == 'completed' 
                else f"🔴 {x.upper()}" if x == 'failed'
                else f"🔵 {x.upper()}" if x == 'running'
                else f"🟡 {x.upper()}"
            )
            
            # Display table
            st.dataframe(
                df[['load_id', 'load_type', 'status_display', 'started_at', 'completed_at', 
                   'records_processed', 'records_failed', 'initiated_by']],
                column_config={
                    "load_id": "Load ID",
                    "load_type": "Type", 
                    "status_display": "Status",
                    "started_at": "Started",
                    "completed_at": "Completed",
                    "records_processed": st.column_config.NumberColumn("Processed"),
                    "records_failed": st.column_config.NumberColumn("Failed"),
                    "initiated_by": "Initiated By"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Handle running loads
            running_loads = df[df['status'] == 'running']
            if not running_loads.empty:
                st.info(f"⚠️ {len(running_loads)} load(s) currently running")
                
                for _, load in running_loads.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**Load #{load['load_id']}:** {load['load_type']}")
                    with col2:
                        if st.button("Mark Complete", key=f"complete_{load['load_id']}"):
                            result = api_put(f"/data-loads/{load['load_id']}", {
                                'status': 'completed',
                                'records_processed': load.get('records_processed', 0) + 100
                            })
                            if result:
                                st.success("Load marked as complete!")
                                st.rerun()
                    with col3:
                        if st.button("Mark Failed", key=f"fail_{load['load_id']}", type="secondary"):
                            result = api_put(f"/data-loads/{load['load_id']}", {
                                'status': 'failed',
                                'error_message': 'Manually marked as failed'
                            })
                            if result:
                                st.error("Load marked as failed")
                                st.rerun()
            
            # Summary metrics
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Loads", len(df))
            with col2:
                completed = len(df[df['status'] == 'completed'])
                st.metric("Completed", completed)
            with col3:
                failed = len(df[df['status'] == 'failed']) 
                st.metric("Failed", failed)
            with col4:
                if len(df) > 0:
                    success_rate = (completed / len(df)) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                else:
                    st.metric("Success Rate", "0%")
                    
        else:
            st.info("No loads found matching your criteria")
    else:
        st.info("No data loads found")
else:
    st.warning("Unable to connect to API. Using mock data for demonstration.")
    
    # Fallback mock data
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
        lambda x: f"🟢 {x.upper()}" if x == 'completed' else f"🔵 {x.upper()}"
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
health_data = api_get('/system-health')

if health_data:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('status', 'unknown')
        color = "🟢" if status == 'operational' else "🟡" if status == 'degraded' else "🔴"
        st.metric("System Status", f"{color} {status.upper()}")
    
    with col2:
        db_status = health_data.get('database_status', 'unknown')
        color = "🟢" if db_status == 'healthy' else "🔴"
        st.metric("Database", f"{color} {db_status.upper()}")
    
    with col3:
        errors = health_data.get('recent_errors_24h', 0)
        st.metric("Errors (24h)", errors)
    
    with col4:
        active_loads = health_data.get('active_data_loads', 0)
        st.metric("Active Loads", active_loads)
else:
    st.info("System health data unavailable")