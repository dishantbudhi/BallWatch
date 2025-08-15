import os
import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
from datetime import datetime, timedelta
from modules import api_client

# Ensure Streamlit page config is set before any other st.* calls
st.set_page_config(page_title='Data Cleanup - Data Engineer', layout='wide')

# Sidebar/navigation
SideBarLinks()

st.title('Data Cleanup & Validation — Data Engineer')
st.caption('Inspect and resolve data validation errors and schedule cleanup tasks.')

# ensure session state has api_base_url
api_client.ensure_api_base()


def call_get_raw(endpoint: str, params=None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def call_post_raw(endpoint: str, data=None, timeout=5):
    return api_client.api_post(endpoint, data=data, timeout=timeout)


def get_data_errors(params=None):
    return call_get_raw('/system/data-errors', params)


def get_cleanup_schedule():
    return call_get_raw('/system/data-cleanup')


def schedule_cleanup(data):
    return call_post_raw('/system/data-cleanup', data)


# High-level request dispatcher used by UI actions
def make_request(endpoint, method='GET', data=None):
    if endpoint.startswith('/system/data-errors') and method == 'GET':
        return get_data_errors(data)
    if endpoint.startswith('/system/data-cleanup'):
        if method == 'GET':
            return get_cleanup_schedule()
        if method == 'POST':
            return schedule_cleanup(data)
    return None


# --- Page UI ---

tab1, tab2 = st.tabs(["Data Errors", "Data Cleanup"])

with tab1:
    st.header("Data Errors")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Update to use severity levels from SystemLogs
        severity_filter = st.selectbox("Severity", 
            ["All", "error", "warning", "critical"], key="data_severity")
    with col2:
        # Use service_name instead of table_name for filtering
        service_filter = st.selectbox("Service/Component", 
            ["All", "Performance Metrics", "Data Consistency", "Foreign Key Check", 
             "Data Range Check", "Duplicate Check", "Business Logic", "Schema Integrity",
             "Data Quality", "Constraint Check", "Referential Check", "Data Freshness"], 
            key="data_service")
    with col3:
        days_filter = st.number_input("Days to look back", min_value=1, max_value=90, value=7, key="data_days")
    
    if st.button("Load Data Errors", key="load_data_errors"):
        params = f"?days={days_filter}"
        if severity_filter != "All":
            params += f"&severity={severity_filter}"
        if service_filter != "All":
            params += f"&service_name={service_filter}"
        
        endpoint = f"/system/data-errors{params}"
        
        data = make_request(endpoint)
        
        if data and 'errors' in data:
            st.session_state['data_errors'] = data['errors']
            st.success(f"Found {len(data['errors'])} data errors")
            
            # Add debug info
            if st.session_state.get('debug_mode', False):
                with st.expander("🔍 Debug: API Response"):
                    st.write("**Full Response:**")
                    st.json(data)
                    if data['errors']:
                        st.write("**Sample Error Record:**")
                        st.json(data['errors'][0])
    
    # Update the display section:
    if 'data_errors' in st.session_state:
        errors = st.session_state['data_errors']
        
        if errors:
            st.write(f"**Showing {len(errors)} data validation errors:**")
            
            for error in errors:
                error_id = error.get('data_error_id', 'N/A')
                severity = error.get('severity', 'unknown')
                table_name = error.get('table_name', 'unknown')
                
                # Use color coding for severity
                severity_color = "🔴" if severity == "critical" else "🟡" if severity == "error" else "🟠"
                
                with st.expander(f"{severity_color} Error #{error_id} - {severity.upper()} in {table_name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Service/Component:** {error.get('table_name', 'N/A')}")
                        st.write(f"**Error Message:** {error.get('error_message', 'N/A')}")
                        st.write(f"**Severity:** {error.get('severity', 'N/A').upper()}")
                        st.write(f"**Records Processed:** {error.get('records_processed', 'N/A')}")
                        st.write(f"**Records Failed:** {error.get('records_failed', 'N/A')}")
                        
                    with col2:
                        st.write(f"**Detected At:** {error.get('detected_at', 'N/A')}")
                        resolved_status = "✅ Resolved" if error.get('resolved_at') else "❌ Unresolved"
                        st.write(f"**Status:** {resolved_status}")
                        if error.get('resolved_at'):
                            st.write(f"**Resolved At:** {error.get('resolved_at', 'N/A')}")
                            st.write(f"**Resolved By:** {error.get('resolved_by', 'N/A')}")
                        if error.get('resolution_notes'):
                            st.write(f"**Resolution Notes:** {error.get('resolution_notes', 'N/A')}")
                        
                        # Add action buttons for unresolved errors
                        if not error.get('resolved_at'):
                            if st.button(f"Mark as Resolved", key=f"resolve_{error_id}"):
                                st.info("Resolution functionality would go here")
        else:
            st.info("No data validation errors found for the selected criteria")
    else:
        st.info("Click 'Load Data Errors' to fetch validation errors from the system")

with tab2:
    st.header("Data Cleanup Management")
    
    cleanup_tab1, cleanup_tab2 = st.tabs(["View Schedule", "Schedule Cleanup"])
    
    with cleanup_tab1:
        st.subheader("Current Cleanup Schedule")
        
        if st.button("Load Cleanup Schedule", key="load_cleanup"):
            data = make_request("/system/data-cleanup")
            
            if data:
                # backend uses 'active_schedules' and may return 'recent_cleanup_history'
                st.session_state['active_schedules'] = data.get('active_schedules', [])
                # support both possible keys for recent history for backward compatibility
                st.session_state['cleanup_history'] = data.get('recent_history', data.get('recent_cleanup_history', []))
                st.success("Cleanup data loaded successfully")
        
        if 'active_schedules' in st.session_state:
            schedules = st.session_state['active_schedules']
            
            if schedules:
                st.write("**Active Cleanup Schedules:**")
                for schedule in schedules:
                    with st.expander(f"{schedule.get('cleanup_type', schedule.get('service_name', 'Unknown'))} - {schedule.get('frequency', schedule.get('message', 'N/A'))}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Schedule ID:** {schedule.get('schedule_id', 'N/A')}")
                            st.write(f"**Frequency:** {schedule.get('frequency', schedule.get('message', 'N/A'))}")
                            st.write(f"**Retention Days:** {schedule.get('retention_days', 'N/A')}")
                            
                        with col2:
                            st.write(f"**Next Run:** {schedule.get('next_run', schedule.get('last_run', 'N/A'))}")
                            st.write(f"**Last Run:** {schedule.get('last_run', 'Never')}")
                            # created_by may be stored as user_id; fall back gracefully
                            st.write(f"**Created By:** {schedule.get('created_by', schedule.get('user_id', 'N/A'))}")

        if 'cleanup_history' in st.session_state:
            history = st.session_state['cleanup_history']
            
            if history:
                st.write("**Recent Cleanup History:**")
                for item in history[:5]:
                    status_text = "COMPLETED" if item.get('status', '') == 'completed' else "FAILED"
                    st.write(f"[{status_text}] {item.get('cleanup_type', item.get('service_name', 'Unknown'))} - {item.get('started_at', item.get('created_at', 'N/A'))} - {item.get('records_deleted', item.get('records_deleted', 0))} records deleted")
    
    with cleanup_tab2:
        st.subheader("Schedule New Cleanup")
        
        with st.form("schedule_cleanup_form"):
            cleanup_type = st.text_input("Cleanup Type*", placeholder="e.g., old_logs, temp_files")
            frequency = st.selectbox("Frequency*", ["daily", "weekly", "monthly"])
            retention_days = st.number_input("Retention Days*", min_value=1, max_value=365, value=30,
                                           help="How many days of data to keep")
            next_run_date = st.date_input("Next Run Date", value=datetime.now().date() + timedelta(days=1))
            created_by = st.text_input("Created By*", placeholder="Your username")
            
            if st.form_submit_button("Schedule Cleanup"):
                if cleanup_type and frequency and retention_days and created_by:
                    next_run_datetime = datetime.combine(next_run_date, datetime.min.time())
                    
                    cleanup_data = {
                        "cleanup_type": cleanup_type,
                        "frequency": frequency,
                        "retention_days": retention_days,
                        "next_run": next_run_datetime.isoformat(),
                        "created_by": created_by
                    }
                    
                    result = make_request("/system/data-cleanup", method='POST', data=cleanup_data)
                    
                    if result:
                        st.success(f"Cleanup scheduled successfully! Schedule ID: {result.get('schedule_id')}")
                        st.rerun()
                else:
                    st.error("Please fill in all required fields marked with *")

try:
    del st.session_state['debug_mode']
except Exception:
    pass