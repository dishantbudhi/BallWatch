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

SideBarLinks()

if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'http://api:4000'
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

def api_get(endpoint):
    try:
        full_url = f"{st.session_state.api_base_url}{endpoint}"
        response = requests.get(full_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code} for {endpoint}")
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {endpoint}")
        st.error("Cannot connect to server")
        return None
    except Exception as e:
        logger.error(f"Error for {endpoint}: {str(e)}")
        st.error(f"Error: {str(e)}")
        return None

def api_post(endpoint, data):
    try:
        full_url = f"{st.session_state.api_base_url}{endpoint}"
        response = requests.post(
            full_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code} for {endpoint}")
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {endpoint}")
        st.error("Cannot connect to server")
        return None
    except Exception as e:
        logger.error(f"Error for {endpoint}: {str(e)}")
        st.error(f"Error: {str(e)}")
        return None

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

if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()

st.divider()

health_data = api_get('/system/health')

if health_data:
    st.subheader("System Status Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('overall_status', 'unknown')
        if status == 'operational':
            st.success("OPERATIONAL")
            st.caption("All systems running normally")
        elif status == 'degraded':
            st.warning("DEGRADED")
            st.caption("Some issues detected")
        else:
            st.error("CRITICAL")
            st.caption("System issues present")
    
    with col2:
        db_status = health_data.get('database_status', 'unknown')
        if db_status == 'healthy':
            st.success("DATABASE HEALTHY")
        else:
            st.error("DATABASE ISSUES")
        st.caption("Database connectivity")
    
    with col3:
        errors_24h = health_data.get('recent_errors_24h', 0)
        if errors_24h == 0:
            st.success("0 ERRORS")
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
    
    if health_data.get('health_check_timestamp'):
        st.caption(f"Last updated: {health_data['health_check_timestamp']}")
    
    st.divider()
    
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
    
    last_load = health_data.get('last_successful_load')
    if last_load:
        st.success(f"Last successful load: **{last_load.get('load_type', 'Unknown')}** (ID: {last_load.get('load_id', 'N/A')})")
        st.caption(f"Completed at: {last_load.get('completed_at', 'Unknown')}")
    
else:
    st.warning("Unable to connect to system health API. Showing mock data for demonstration.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success("OPERATIONAL")
        st.caption("All systems running normally")
    
    with col2:
        st.success("DATABASE HEALTHY")
        st.caption("Database connectivity")
    
    with col3:
        st.warning("3 ERRORS")
        st.caption("Last 24 hours")
    
    with col4:
        st.info("1 ACTIVE LOADS")
        st.caption("Currently running")

st.divider()

st.subheader("Recent Error Logs")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    severity_filter = st.selectbox("Severity", ["All", "critical", "error", "warning", "info"])
with col2:
    days_back = st.number_input("Days back", min_value=1, max_value=30, value=7)
with col3:
    resolved_filter = st.selectbox("Status", ["All", "Resolved", "Unresolved"])

params = []
endpoint = f"/system/error-logs?days={days_back}"
if severity_filter != "All":
    endpoint += f"&severity={severity_filter}"
if resolved_filter == "Resolved":
    endpoint += "&resolved=true"
elif resolved_filter == "Unresolved":
    endpoint += "&resolved=false"

error_data = api_get(endpoint)

if error_data:
    errors = error_data.get('error_logs', [])
    
    if errors:
        df_errors = pd.DataFrame(errors)
        
        df_errors['severity_display'] = df_errors['severity'].apply(
            lambda x: f"CRITICAL" if x == 'critical'
            else f"ERROR" if x == 'error'  
            else f"WARNING" if x == 'warning'
            else f"INFO"
        )
        
        df_errors['status'] = df_errors['resolved_at'].apply(
            lambda x: "RESOLVED" if pd.notna(x) else "PENDING"
        )
        
        if 'created_at' in df_errors.columns:
            df_errors['created_at'] = pd.to_datetime(df_errors['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            df_errors[['error_id', 'error_type', 'severity_display', 'module', 
                      'error_message', 'created_at', 'status']],
            column_config={
                "error_id": st.column_config.NumberColumn("ID", width="small"),
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
        st.success("No errors found in the specified time period.")

else:
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
        lambda x: f"WARNING" if x == 'warning' else f"ERROR"
    )
    df_mock['status'] = df_mock['resolved_at'].apply(
        lambda x: "RESOLVED" if pd.notna(x) else "PENDING"
    )
    
    st.dataframe(
        df_mock[['error_id', 'error_type', 'severity_display', 'module',
                'error_message', 'created_at', 'status']],
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("Data Validation")

col1, col2 = st.columns(2)

with col1:
    st.write("**Run Data Validation Check**")
    validation_type = st.selectbox("Validation Type", 
                                  ["integrity_check", "duplicate_check", "null_check"])
    table_name = st.selectbox("Table", ["Players", "Teams", "Game", "PlayerGameStats"])
    
    if st.button("Run Validation", type="primary"):
        with st.spinner("Running validation check..."):
            result = api_post('/system/data-validation', {
                'validation_type': validation_type,
                'table_name': table_name,
                'run_by': 'Mike Lewis'
            })
            
            if result:
                results = result.get('results', {})
                status = results.get('status', 'unknown')
                total_records = results.get('total_records', 0)
                valid_records = results.get('valid_records', 0)
                invalid_records = results.get('invalid_records', 0)
                validity_percentage = results.get('validity_percentage', 0)
                
                if status == 'passed':
                    st.success(f"Validation passed! {valid_records}/{total_records} records are valid ({validity_percentage}%)")
                elif status == 'warning':
                    st.warning(f"Validation passed with warnings. {invalid_records} issues found in {total_records} records")
                elif status == 'failed':
                    st.error(f"Validation failed. {invalid_records} issues found in {total_records} records")
                else:
                    st.info(f"Validation completed with status: {status}")
            else:
                st.error("Failed to run validation")

with col2:
    st.write("**Recent Validation Results**")
    validation_data = api_get('/system/data-validation?days=7')
    
    if validation_data:
        reports = validation_data.get('validation_reports', [])
        if reports:
            for report in reports[-3:]:
                status = report.get('status', 'unknown')
                table_name = report.get('table_name', 'Unknown')
                validation_type = report.get('validation_type', 'Unknown')
                
                if status == 'passed':
                    st.success(f"{table_name} - {validation_type}")
                elif status == 'warning':
                    st.warning(f"{table_name} - {validation_type}")
                else:
                    st.error(f"{table_name} - {validation_type}")
                st.caption(f"Run on {report.get('run_date', 'Unknown')}")
        else:
            st.info("No recent validation reports")
    else:
        st.info("Validation data unavailable")

st.divider()

st.subheader("System Recommendations")

recommendations = []

if health_data:
    error_count = health_data.get('recent_errors_24h', 0)
    active_loads = health_data.get('active_data_loads', 0)
    db_status = health_data.get('database_status', 'unknown')
    
    if error_count > 10:
        recommendations.append(("error", "High error rate detected. Review error logs for patterns."))
    elif error_count > 5:
        recommendations.append(("warning", "Moderate error activity. Monitor for trends."))
    else:
        recommendations.append(("success", "Error rate within normal parameters"))
    
    if active_loads > 3:
        recommendations.append(("warning", "Multiple concurrent loads detected. Monitor system resources."))
    else:
        recommendations.append(("success", "Data load capacity normal"))
    
    if db_status == 'healthy':
        recommendations.append(("success", "Database connection stable"))
    else:
        recommendations.append(("error", "Database issues detected. Check connection settings."))
else:
    recommendations = [
        ("error", "Unable to connect to system health API"),
        ("warning", "Check API connectivity and backend services"),
        ("success", "Page functionality working with mock data")
    ]

for rec_type, message in recommendations:
    if rec_type == "error":
        st.error(message)
    elif rec_type == "warning":
        st.warning(message)
    else:
        st.success(message)