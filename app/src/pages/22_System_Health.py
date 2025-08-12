import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import logging
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="System Health - BallWatch",
    layout="wide"
)

# Use the SideBarLinks function to control navigation
SideBarLinks()

# Initialize session state
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'http://api:4000/api'
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

# API Helper Functions
def api_get(endpoint):
    try:
        response = requests.get(f"{st.session_state.api_base_url}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def api_post(endpoint, data):
    try:
        response = requests.post(
            f"{st.session_state.api_base_url}{endpoint}",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Page Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("System Health Dashboard")
    st.markdown("Real-time monitoring and system status")

with col2:
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh

with col3:
    if st.button("Refresh Now", use_container_width=True):
        st.rerun()

# Auto-refresh logic
if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()

st.divider()

# Fetch system health data
health_data = api_get('/admin/system-health')

if health_data:
    # System Status Overview
    st.subheader("System Status Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('status', 'unknown')
        if status == 'operational':
            st.success(f"🟢 OPERATIONAL")
            st.caption("All systems running normally")
        elif status == 'degraded':
            st.warning(f"🟡 DEGRADED")
            st.caption("Some issues detected")
        else:
            st.error(f"🔴 CRITICAL")
            st.caption("System issues present")
    
    with col2:
        db_status = health_data.get('database_status', 'unknown')
        if db_status == 'healthy':
            st.success(f"🟢 DATABASE HEALTHY")
        else:
            st.error(f"🔴 DATABASE ISSUES")
        st.caption("Database connectivity")
    
    with col3:
        errors_24h = health_data.get('recent_errors_24h', 0)
        if errors_24h == 0:
            st.success(f"0 ERRORS")
        elif errors_24h < 10:
            st.warning(f"{errors_24h} ERRORS")
        else:
            st.error(f"{errors_24h} ERRORS")
        st.caption("Last 24 hours")
    
    with col4:
        active_loads = health_data.get('active_data_loads', 0)
        if active_loads == 0:
            st.info("0 ACTIVE LOADS")
        else:
            st.info(f"{active_loads} ACTIVE LOADS")
        st.caption("Currently running")
    
    # Last update timestamp
    if health_data.get('timestamp'):
        st.caption(f"Last updated: {health_data['timestamp']}")
    
    st.divider()
    
    # System Metrics
    st.subheader("System Metrics")
    
    metrics = health_data.get('system_metrics', {})
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Players", f"{metrics.get('total_players', 0):,}")
        with col2:
            st.metric("Total Teams", metrics.get('total_teams', 0))
        with col3:
            st.metric("Total Games", f"{metrics.get('total_games', 0):,}")
        with col4:
            st.metric("Total Users", metrics.get('total_users', 0))
    
    # Last Successful Load
    last_load = health_data.get('last_successful_load')
    if last_load:
        st.success(f"✅ Last successful load: **{last_load.get('load_type', 'Unknown')}** (ID: {last_load.get('load_id', 'N/A')})")
        st.caption(f"Completed at: {last_load.get('completed_at', 'Unknown')}")
    
else:
    st.warning("Unable to connect to system health API. Showing mock data for demonstration.")
    
    # Mock data fallback
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success("🟢 OPERATIONAL")
        st.caption("All systems running normally")
    
    with col2:
        st.success("🟢 DATABASE HEALTHY")
        st.caption("Database connectivity")
    
    with col3:
        st.warning("3 ERRORS")
        st.caption("Last 24 hours")
    
    with col4:
        st.info("1 ACTIVE LOADS")
        st.caption("Currently running")

st.divider()

# Error Logs Section
st.subheader("Recent Error Logs")

# Filter controls for error logs
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    severity_filter = st.selectbox("Severity", ["All", "critical", "error", "warning", "info"])
with col2:
    days_back = st.number_input("Days back", min_value=1, max_value=30, value=7)
with col3:
    resolved_filter = st.selectbox("Status", ["All", "Resolved", "Unresolved"])

# Fetch error logs
params = {}
if severity_filter != "All":
    params['severity'] = severity_filter
if days_back:
    params['days'] = days_back
if resolved_filter == "Resolved":
    params['resolved'] = 'true'
elif resolved_filter == "Unresolved":
    params['resolved'] = 'false'

query_params = "&".join([f"{k}={v}" for k, v in params.items()])
endpoint = f"/admin/error-logs?{query_params}" if query_params else "/admin/error-logs"

error_data = api_get(endpoint)

if error_data:
    errors = error_data.get('errors', [])
    
    if errors:
        df_errors = pd.DataFrame(errors)
        
        # Add severity indicators
        df_errors['severity_display'] = df_errors['severity'].apply(
            lambda x: f"🔴 {x.upper()}" if x == 'critical'
            else f"🟠 {x.upper()}" if x == 'error'  
            else f"🟡 {x.upper()}" if x == 'warning'
            else f"🔵 {x.upper()}"
        )
        
        # Add resolution status
        df_errors['status'] = df_errors['resolved_at'].apply(
            lambda x: "✅ Resolved" if pd.notna(x) else "⚠️ Pending"
        )
        
        # Display error logs table
        st.dataframe(
            df_errors[['error_id', 'error_type', 'severity_display', 'module', 
                      'error_message', 'created_at', 'status']],
            column_config={
                "error_id": "ID",
                "error_type": "Type",
                "severity_display": "Severity", 
                "module": "Module",
                "error_message": "Message",
                "created_at": "Time",
                "status": "Status"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Error summary
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            critical_count = len(df_errors[df_errors['severity'] == 'critical'])
            st.metric("Critical", critical_count, 
                     delta=f"{critical_count} critical" if critical_count > 0 else None,
                     delta_color="inverse")
        
        with col2:
            unresolved = len(df_errors[df_errors['resolved_at'].isna()])
            st.metric("Unresolved", unresolved,
                     delta=f"{unresolved} pending" if unresolved > 0 else None,
                     delta_color="inverse")
        
        with col3:
            resolved = len(df_errors[df_errors['resolved_at'].notna()])
            st.metric("Resolved", resolved)
        
        with col4:
            if len(df_errors) > 0:
                resolution_rate = (resolved / len(df_errors)) * 100
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    else:
        st.success("✅ No errors found in the specified time period!")

else:
    # Mock error data
    st.warning("Unable to fetch error logs. Showing sample data.")
    
    mock_errors = [
        {
            'error_id': 1,
            'error_type': 'DataQuality', 
            'severity': 'warning',
            'module': 'PlayerStats',
            'error_message': 'Invalid shooting percentage detected',
            'created_at': '2025-01-25 13:45:00',
            'resolved_at': None
        },
        {
            'error_id': 2,
            'error_type': 'APITimeout',
            'severity': 'error',
            'module': 'DataIngestion', 
            'error_message': 'NBA API request timeout',
            'created_at': '2025-01-25 12:30:00',
            'resolved_at': '2025-01-25 12:35:00'
        }
    ]
    
    df_mock = pd.DataFrame(mock_errors)
    df_mock['severity_display'] = df_mock['severity'].apply(
        lambda x: f"🟡 {x.upper()}" if x == 'warning' else f"🟠 {x.upper()}"
    )
    df_mock['status'] = df_mock['resolved_at'].apply(
        lambda x: "✅ Resolved" if pd.notna(x) else "⚠️ Pending"
    )
    
    st.dataframe(
        df_mock[['error_id', 'error_type', 'severity_display', 'module',
                'error_message', 'created_at', 'status']],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# Data Validation Section
st.subheader("Data Validation")

col1, col2 = st.columns(2)

with col1:
    st.write("**Run Data Validation Check**")
    validation_type = st.selectbox("Validation Type", 
                                  ["integrity_check", "duplicate_check", "null_check"])
    table_name = st.selectbox("Table", ["Players", "Teams", "Game", "PlayerGameStats"])
    
    if st.button("Run Validation", type="primary"):
        with st.spinner("Running validation check..."):
            result = api_post('/admin/data-validation', {
                'validation_type': validation_type,
                'table_name': table_name,
                'run_by': 'Mike Lewis'
            })
            
            if result:
                status = result.get('status', 'unknown')
                if status == 'passed':
                    st.success(f"✅ Validation passed! {result.get('valid_records', 0)} records validated")
                elif status == 'warning':
                    st.warning(f"⚠️ Validation passed with warnings. {result.get('invalid_records', 0)} issues found")
                else:
                    st.error(f"❌ Validation failed. {result.get('invalid_records', 0)} issues found")
            else:
                st.error("Failed to run validation")

with col2:
    st.write("**Recent Validation Results**")
    validation_data = api_get('/admin/data-validation?days=7')
    
    if validation_data:
        reports = validation_data.get('reports', [])
        if reports:
            for report in reports[-3:]:  # Show last 3 reports
                status = report.get('status', 'unknown')
                if status == 'passed':
                    st.success(f"✅ {report.get('table_name')} - {report.get('validation_type')}")
                elif status == 'warning':
                    st.warning(f"⚠️ {report.get('table_name')} - {report.get('validation_type')}")
                else:
                    st.error(f"❌ {report.get('table_name')} - {report.get('validation_type')}")
                st.caption(f"Run on {report.get('run_date', 'Unknown')}")
        else:
            st.info("No recent validation reports")
    else:
        st.info("Validation data unavailable")

st.divider()

# System Recommendations
st.subheader("System Recommendations")

# This would normally come from the health API, but we'll provide static recommendations
recommendations = []

if health_data:
    error_count = health_data.get('recent_errors_24h', 0)
    active_loads = health_data.get('active_data_loads', 0)
    db_status = health_data.get('database_status', 'unknown')
    
    if error_count > 10:
        recommendations.append("🔴 High error rate detected. Review error logs for patterns.")
    elif error_count > 5:
        recommendations.append("🟡 Moderate error activity. Monitor for trends.")
    else:
        recommendations.append("✅ Error rate within normal parameters")
    
    if active_loads > 3:
        recommendations.append("🟡 Multiple concurrent loads detected. Monitor system resources.")
    else:
        recommendations.append("✅ Data load capacity normal")
    
    if db_status == 'healthy':
        recommendations.append("✅ Database connection stable")
    else:
        recommendations.append("🔴 Database issues detected. Check connection settings.")
else:
    recommendations = [
        "🔴 Unable to connect to system health API",
        "🟡 Check API connectivity and backend services",
        "✅ Page functionality working with mock data"
    ]

for rec in recommendations:
    if rec.startswith("🔴"):
        st.error(rec)
    elif rec.startswith("🟡"):
        st.warning(rec)
    else:
        st.success(rec)