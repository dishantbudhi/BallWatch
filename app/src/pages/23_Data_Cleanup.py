import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime, timedelta

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Data Logs Management')

BASE_URL = "http://api:4000"

def make_request(endpoint, method='GET', data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

tab1, tab2 = st.tabs(["Data Errors", "Data Cleanup"])

with tab1:
    st.header("Data Errors")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        error_type_filter = st.selectbox("Error Type", 
            ["All", "duplicate", "missing", "invalid"], key="data_error_type")
    with col2:
        table_filter = st.text_input("Table Name", key="data_table")
    with col3:
        days_filter = st.number_input("Days to look back", min_value=1, max_value=90, value=7, key="data_days")
    
    if st.button("Load Data Errors", key="load_data_errors"):
        params = f"?days={days_filter}"
        if error_type_filter != "All":
            params += f"&error_type={error_type_filter}"
        if table_filter:
            params += f"&table_name={table_filter}"
        
        endpoint = f"/system/data-errors{params}"
        
        data = make_request(endpoint)
        
        if data and 'errors' in data:
            st.session_state['data_errors'] = data['errors']
            st.success(f"Found {len(data['errors'])} data errors")
    
    if 'data_errors' in st.session_state:
        errors = st.session_state['data_errors']
        
        if errors:
            for error in errors:
                with st.expander(f"Error #{error['data_error_id']} - {error['error_type']} in {error['table_name']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Record ID:** {error['record_id']}")
                        st.write(f"**Field:** {error['field_name']}")
                        st.write(f"**Invalid Value:** {error['invalid_value']}")
                        st.write(f"**Expected Format:** {error['expected_format']}")
                        
                    with col2:
                        st.write(f"**Detected:** {error['detected_at']}")
                        st.write(f"**Resolved:** {error.get('resolved_at', 'Not resolved')}")
                        st.write(f"**Auto-fixed:** {'Yes' if error.get('auto_fixed') else 'No'}")
        else:
            st.info("No data errors found for the selected criteria")

with tab2:
    st.header("Data Cleanup Management")
    
    cleanup_tab1, cleanup_tab2 = st.tabs(["View Schedule", "Schedule Cleanup"])
    
    with cleanup_tab1:
        st.subheader("Current Cleanup Schedule")
        
        if st.button("Load Cleanup Schedule", key="load_cleanup"):
            data = make_request("/system/data-cleanup")
            
            if data:
                st.session_state['active_schedules'] = data.get('active_schedules', [])
                st.session_state['cleanup_history'] = data.get('recent_history', [])
                st.success("Cleanup data loaded successfully")
        
        if 'active_schedules' in st.session_state:
            schedules = st.session_state['active_schedules']
            
            if schedules:
                st.write("**Active Cleanup Schedules:**")
                for schedule in schedules:
                    with st.expander(f"{schedule['cleanup_type']} - {schedule['frequency']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Schedule ID:** {schedule['schedule_id']}")
                            st.write(f"**Frequency:** {schedule['frequency']}")
                            st.write(f"**Retention Days:** {schedule['retention_days']}")
                            
                        with col2:
                            st.write(f"**Next Run:** {schedule['next_run']}")
                            st.write(f"**Last Run:** {schedule.get('last_run', 'Never')}")
                            st.write(f"**Created By:** {schedule['created_by']}")
        
        if 'cleanup_history' in st.session_state:
            history = st.session_state['cleanup_history']
            
            if history:
                st.write("**Recent Cleanup History:**")
                for item in history[:5]:
                    status_text = "COMPLETED" if item['status'] == 'completed' else "FAILED"
                    st.write(f"[{status_text}] {item['cleanup_type']} - {item['started_at']} - {item.get('records_deleted', 0)} records deleted")
    
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