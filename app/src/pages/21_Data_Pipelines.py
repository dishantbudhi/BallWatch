import os
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from modules.nav import SideBarLinks
from modules import api_client

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Data Pipelines - Data Engineer",
    layout="wide"
)

SideBarLinks()

st.title("Data Pipelines — Data Engineer")
st.caption("Monitor, manage, and troubleshoot data loads for the analytics platform.")
st.write("")

# API base URL (supports env override)
if 'api_base_url' not in st.session_state:
    def _default_api_base():
        env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
        if env:
            return env
        try:
            if os.path.exists('/.dockerenv'):
                return 'http://api:4000'
        except Exception:
            pass
        return 'http://localhost:4000'
    st.session_state.api_base_url = _default_api_base()

# Replace local api helpers with centralized ones

def api_get(endpoint):
    try:
        return api_client.api_get(endpoint)
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def api_post(endpoint, data):
    try:
        return api_client.api_post(endpoint, data)
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def api_put(endpoint, data):
    try:
        return api_client.api_put(endpoint, data)
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def _parse_endpoint_with_query(endpoint: str):
    import urllib.parse
    from typing import Dict, Any
    if not endpoint:
        return endpoint, {}
    parsed = urllib.parse.urlparse(endpoint)
    path = parsed.path
    qs = urllib.parse.parse_qs(parsed.query)
    params = {k: v[0] for k, v in qs.items()}
    return path, params


def call_get_raw(endpoint: str, params=None, timeout=10):
    try:
        path, p = _parse_endpoint_with_query(endpoint)
        merged = {**(p or {}), **(params or {})}
        full = f"{st.session_state.api_base_url}{path}"
        resp = requests.get(full, params=merged or None, timeout=timeout)
        if resp.status_code in (200, 201):
            return resp.json()
        logger.warning('GET %s returned %s', full, resp.status_code)
        # Show details in UI when debug mode is active to help debugging
        try:
            if st.session_state.get('debug_mode', False):
                st.error(f"GET {full} returned {resp.status_code}: {resp.text}")
        except Exception:
            # Avoid raising UI errors from logging
            pass
    except Exception as e:
        logger.exception('Exception in call_get_raw(%s): %s', endpoint, e)
    return None


def call_post_raw(endpoint: str, data=None, timeout=10):
    try:
        path, _ = _parse_endpoint_with_query(endpoint)
        full = f"{st.session_state.api_base_url}{path}"
        resp = requests.post(full, json=data, timeout=timeout)
        if resp.status_code in (200, 201):
            return resp.json()
        logger.warning('POST %s returned %s', full, resp.status_code)
        try:
            # production behavior: do not surface raw API responses in UI
            if st.session_state.get('debug_mode', False):
                st.error(f"POST {full} returned {resp.status_code}: {resp.text}")
        except Exception:
            pass
    except Exception as e:
        logger.exception('Exception in call_post_raw(%s): %s', endpoint, e)
    return None


def call_put_raw(endpoint: str, data=None, timeout=10):
    try:
        path, _ = _parse_endpoint_with_query(endpoint)
        full = f"{st.session_state.api_base_url}{path}"
        resp = requests.put(full, json=data, timeout=timeout)
        if resp.status_code in (200, 201):
            return resp.json()
        logger.warning('PUT %s returned %s', full, resp.status_code)
        # production behavior: do not surface raw API responses in UI
    except Exception as e:
        logger.exception('Exception in call_put_raw(%s): %s', endpoint, e)
    return None

# Debug mode UI removed from this page

# Main Page
st.markdown("")

# System Health Check
st.subheader("System Health")
health_data = api_get('/system/health')

if health_data:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('overall_status', 'unknown').upper()
        status_color = "HEALTHY" if status == "HEALTHY" else "WARNING" if status == "WARNING" else "CRITICAL"
        st.metric("System Status", status_color)
    with col2:
        db_status = health_data.get('database_status', 'unknown').upper()
        st.metric("Database", db_status)
    with col3:
        errors = health_data.get('recent_errors_24h', 0)
        st.metric("Errors (24h)", errors)
    with col4:
        active = health_data.get('active_data_loads', 0)
        st.metric("Active Loads", active)
else:
    st.warning("Unable to fetch system health data")

st.divider()

# Data Load History
st.subheader("Data Load History")

# Enhanced Filters
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    status_filter = st.selectbox("Status", ["All", "completed", "running", "failed", "pending"])
with col2:
    load_type_filter = st.selectbox("Load Type", ["All", "NBA API", "ESPN Feed", "Draft API", "Contract API", "Analytics Engine"])
with col3:
    days_filter = st.number_input("Days back", min_value=1, max_value=90, value=7)
with col4:
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()

# Fetch data loads
endpoint = f'/system/data-loads?days={days_filter}'
if status_filter != "All":
    endpoint += f'&status={status_filter}'
if load_type_filter != "All":
    endpoint += f'&load_type={load_type_filter}'

loads_data = api_get(endpoint)

# Flexible extractor to handle different API shapes
def _extract_loads(resp):
    if not resp:
        return None
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for k in ('data_loads', 'loads', 'results', 'data', 'items'):
            if k in resp and resp[k] is not None:
                return resp[k]
        # some endpoints may return the list at top-level under other keys
        # fall back to trying to find a list value
        for v in resp.values():
            if isinstance(v, list):
                return v
    return None

loads = _extract_loads(loads_data)

# Debug information removed: rely on logging for troubleshooting

if loads and len(loads) > 0:
    # ensure loads is a list of dicts
    # Normalize fields (accept created_at as started_at fallback)
    for l in loads:
        if 'started_at' not in l and 'created_at' in l:
            l['started_at'] = l.get('created_at')
        if 'completed_at' not in l and 'resolved_at' in l:
            l['completed_at'] = l.get('resolved_at')
        # normalize load_type naming differences
        l['load_type'] = l.get('load_type') or l.get('service_name')
        # ensure numeric duration exists
        if 'duration_seconds' not in l:
            try:
                l['duration_seconds'] = int(l.get('duration_seconds') or 0)
            except Exception:
                l['duration_seconds'] = 0

    loads_list = loads
    df = pd.DataFrame(loads_list)
    
    if not df.empty:
        # Format status with better display
        def format_status(status):
            status_icons = {
                'completed': 'COMPLETED',
                'running': 'RUNNING',
                'failed': 'FAILED',
                'pending': 'PENDING'
            }
            return status_icons.get(status, str(status).upper())
        
        # Some rows may have status derived differently; ensure column exists
        if 'status' not in df.columns:
            df['status'] = df.get('severity', pd.Series(['pending'] * len(df))).apply(lambda x: str(x))
        df['status_display'] = df['status'].apply(format_status)
        
        # Format dates with proper fallbacks - fix the ambiguous Series evaluation
        # Use fillna() and combine_first() instead of 'or' operator
        if 'started_at' not in df.columns:
            if 'created_at' in df.columns:
                df['started_at'] = df['created_at']
            else:
                df['started_at'] = pd.NaT
        
        df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce').dt.strftime('%m/%d %H:%M')
        
        # Handle completed_at column similarly
        if 'completed_at' not in df.columns:
            if 'resolved_at' in df.columns:
                df['completed_at'] = df['resolved_at']
            else:
                df['completed_at'] = None
        
        df['completed_at'] = df['completed_at'].apply(
            lambda x: pd.to_datetime(x, errors='coerce').strftime('%m/%d %H:%M') if pd.notna(x) and x else 'In Progress'
        )
        
        # Format duration - ensure duration_seconds column exists
        if 'duration_seconds' not in df.columns:
            df['duration_seconds'] = 0
        
        df['duration_display'] = df['duration_seconds'].apply(
            lambda x: f"{int(x//60)}m {int(x%60)}s" if pd.notna(x) and x != 0 else 'N/A'
        )

        # Ensure all required columns exist with defaults
        required_columns = ['load_id', 'load_type', 'status_display', 'started_at', 'completed_at', 
                           'duration_display', 'records_processed', 'records_failed', 'initiated_by']
        
        for col in required_columns:
            if col not in df.columns:
                if col in ['records_processed', 'records_failed']:
                    df[col] = 0
                elif col == 'initiated_by':
                    df[col] = 'system'
                else:
                    df[col] = 'N/A'

        # Display enhanced table
        display_columns = [col for col in required_columns if col in df.columns]
        st.dataframe(
            df[display_columns],
            column_config={
                "load_id": st.column_config.NumberColumn("Load ID", width="small"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Enhanced Summary metrics
        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Loads", len(df))
        with col2:
            completed = len(df[df['status'] == 'completed']) if 'status' in df.columns else 0
            st.metric("Completed", completed)
        with col3:
            running = len(df[df['status'] == 'running']) if 'status' in df.columns else 0
            st.metric("Running", running)
        with col4:
            failed = len(df[df['status'] == 'failed']) if 'status' in df.columns else 0
            st.metric("Failed", failed)
        with col5:
            total_processed = df.get('records_processed', pd.Series([0])).sum()
            st.metric("Total Records", f"{int(total_processed):,}")
        
        # Success rate
        if len(df) > 0:
            success_rate = (completed / len(df)) * 100 if len(df) > 0 else 0
            st.info(f"**Success Rate:** {success_rate:.1f}% ({completed}/{len(df)} loads completed successfully)")

        # Running loads with progress
        running_loads = df[df['status'] == 'running']
        if not running_loads.empty:
            st.subheader("Currently Running Loads")
            for _, load in running_loads.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Load #{load['load_id']}** - {load['load_type']}")
                        st.caption(f"Started: {load['started_at']} | Duration: {load['duration_display']}")
                    with col2:
                        st.write(f"**Records:** {load['records_processed']:,}")
                    with col3:
                        if st.button("View Details", key=f"details_{load['load_id']}"):
                            st.info(f"Load details would be shown for ID {load['load_id']}")
            
            st.info("Page will auto-refresh every 30 seconds for running loads")
        
        # Failed loads with enhanced details
        failed_loads = df[df['status'] == 'failed']
        if not failed_loads.empty:
            st.subheader("Failed Loads")
            for _, load in failed_loads.iterrows():
                with st.expander(f"Load #{load['load_id']} - {load['load_type']} | Failed: {load['records_failed']} records"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Load Details:**")
                        st.write(f"- **Type:** {load['load_type']}")
                        st.write(f"- **Started:** {load['started_at']}")
                        st.write(f"- **Duration:** {load['duration_display']}")
                        st.write(f"- **Source:** {load.get('source_file', 'N/A')}")
                        
                        if load.get('error_message'):
                            st.error(f"**Error:** {load['error_message']}")
                    
                    with col2:
                        st.write("**Processing Summary:**")
                        st.write(f"- **Processed:** {load['records_processed']:,} records")
                        st.write(f"- **Failed:** {load['records_failed']:,} records")
                        if load['records_processed'] > 0:
                            error_rate = (load['records_failed'] / (load['records_processed'] + load['records_failed'])) * 100
                            st.write(f"- **Error Rate:** {error_rate:.1f}%")
                        
                        st.divider()
                        
                        # Action buttons
                        button_col1, button_col2 = st.columns(2)
                        with button_col1:
                            if st.button(f"Mark Resolved", key=f"resolve_{load['load_id']}"):
                                result = api_put(f"/system/data-loads/{load['load_id']}", {
                                    'status': 'completed',
                                    'resolved_by': st.session_state.get('username', 'system'),
                                    'resolution_notes': 'Manually marked as resolved'
                                })
                                if result:
                                    st.success("Marked as resolved")
                                    st.rerun()
                        
                        with button_col2:
                            if st.button(f"Retry Load", key=f"retry_{load['load_id']}"):
                                result = api_post('/system/data-loads', {
                                    'load_type': load['load_type'],
                                    'source_file': load.get('source_file'),
                                    'initiated_by': st.session_state.get('username', 'system')
                                })
                                if result:
                                    st.success(f"New load started: ID {result.get('load_id')}")
                                    st.rerun()
    else:
        st.info("No data loads found for the selected criteria.")

else:
    st.info("No data loads found. Try adjusting your filters or check system connectivity.")

