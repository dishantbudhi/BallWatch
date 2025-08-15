"""
BallWatch Basketball Analytics Platform
=======================================
System Administration Blueprint

System monitoring, data management, error handling, and maintenance
operations for data engineers and system administrators.

Author: StatPadders Team
Course: CS 3200 - Summer 2 2025
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
from datetime import datetime, timedelta
import json

# --- New helper: normalize severity values used across routes ---
def _normalize_severity(raw):
    """Map various severity representations in the database to the canonical
    set used by the backend/frontend: ('critical','error','warning','info').

    The sample data used in the provided inserts uses values like 'high',
    'medium', 'low' in the severity column and sometimes stores what we'd
    expect as a severity in the log_type column. This helper provides a
    consistent mapping so the UI and status logic work correctly.
    """
    if not raw:
        return 'info'
    r = str(raw).lower()
    if r in ('critical', 'crit'):
        return 'critical'
    if r in ('error', 'err'):
        return 'error'
    if r in ('warning', 'warn'):
        return 'warning'
    if r in ('info', 'information'):
        return 'info'
    # legacy/sample mappings
    if r in ('high',):
        return 'critical'
    if r in ('medium',):
        return 'error'
    if r in ('low',):
        return 'info'
    # fallback
    return r

# Create the Admin Blueprint
admin = Blueprint('admin', __name__)


# ============================================================================
# SYSTEM HEALTH & MONITORING ROUTES
# ============================================================================

@admin.route('/health', methods=['GET'])
def get_system_health():
    """
    Get comprehensive system health status including database connectivity,
    recent errors, and performance metrics.
    """
    try:
        current_app.logger.info('GET /system/health - Checking system health status')

        cursor = db.get_db().cursor()

        # Verify database connectivity
        cursor.execute('SELECT 1')
        db_status = 'healthy' if cursor.fetchone() else 'unhealthy'

        # Get recent error count (last 24 hours)
        # Be tolerant of sample data where severity or log_type may use alternate values
        cursor.execute('''
            SELECT COUNT(*) as error_count
            FROM SystemLogs
            WHERE (log_type IN ('error','validation') OR severity IN ('error','critical','high','medium'))
              AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        ''')
        recent_errors_result = cursor.fetchone()
        recent_errors = recent_errors_result['error_count'] if recent_errors_result else 0

        # Get active data loads - be permissive and look for rows that clearly indicate a load
        cursor.execute('''
            SELECT COUNT(*) as active_loads
            FROM SystemLogs
            WHERE (log_type = 'data_load'
                   OR LOWER(service_name) LIKE '%data%'
                   OR LOWER(service_name) LIKE '%feed%'
                   OR LOWER(message) LIKE '%load%')
              AND resolved_at IS NULL
        ''')
        active_loads_result = cursor.fetchone()
        active_loads = active_loads_result['active_loads'] if active_loads_result else 0

        # Get last successful data load - look for explicit data_load records or messages that contain 'completed' or 'processed'
        cursor.execute('''
            SELECT log_id, service_name, message, created_at, resolved_at
            FROM SystemLogs
            WHERE (log_type = 'data_load' OR LOWER(message) LIKE '%completed%' OR LOWER(message) LIKE '%processed%')
            ORDER BY IFNULL(resolved_at, created_at) DESC
            LIMIT 1
        ''')
        last_successful_load_raw = cursor.fetchone()

        last_successful_load = None
        if last_successful_load_raw:
            last_successful_load = {
                'load_id': last_successful_load_raw.get('log_id'),
                'load_type': last_successful_load_raw.get('service_name'),
                'message': last_successful_load_raw.get('message'),
                'completed_at': last_successful_load_raw.get('resolved_at') or last_successful_load_raw.get('created_at')
            }

        # Get system metrics
        cursor.execute('''
            SELECT
                (SELECT COUNT(*) FROM Players) as total_players,
                (SELECT COUNT(*) FROM Teams) as total_teams,
                (SELECT COUNT(*) FROM Game) as total_games,
                (SELECT COUNT(*) FROM Users) as total_users
        ''')
        system_metrics = cursor.fetchone()

        # Determine overall system status
        overall_status = 'operational'
        if db_status != 'healthy':
            overall_status = 'critical'
        elif recent_errors > 10:
            overall_status = 'degraded'
        elif active_loads > 5:
            overall_status = 'warning'

        response_data = {
            'overall_status': overall_status,
            'database_status': db_status,
            'recent_errors_24h': recent_errors,
            'active_data_loads': active_loads,
            'last_successful_load': last_successful_load,
            'system_metrics': system_metrics,
            'health_check_timestamp': datetime.now().isoformat()
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error checking system health: {e}')
        return make_response(jsonify({
            "overall_status": "error",
            "error": "Failed to check system health",
            "timestamp": datetime.now().isoformat()
        }), 500)


# ============================================================================
# DATA LOAD MANAGEMENT ROUTES
# ============================================================================

@admin.route('/data-loads', methods=['GET'])
def get_data_loads():
    try:
        current_app.logger.info('GET /system/data-loads - Fetching data loads')

        status = request.args.get('status')
        days = request.args.get('days', 7, type=int)
        load_type = request.args.get('load_type')

        cursor = db.get_db().cursor()

        # Simplified and more inclusive query to match sample data
        query = '''
            SELECT
                log_id as load_id,
                COALESCE(service_name, 'Unknown Service') as load_type,
                CASE
                    WHEN severity IN ('info','low') AND resolved_at IS NOT NULL THEN 'completed'
                    WHEN severity IN ('error','critical','high') THEN 'failed'
                    WHEN severity IN ('warning','medium') AND resolved_at IS NULL THEN 'running'
                    WHEN severity IN ('warning','medium') AND resolved_at IS NOT NULL THEN 'completed'
                    ELSE 'pending'
                END as status,
                severity,
                created_at as started_at,
                resolved_at as completed_at,
                IFNULL(records_processed, 0) as records_processed,
                IFNULL(records_failed, 0) as records_failed,
                message as error_message,
                source_file,
                (SELECT username FROM Users WHERE user_id = SystemLogs.user_id) as initiated_by,
                TIMESTAMPDIFF(SECOND, created_at, IFNULL(resolved_at, NOW())) as duration_seconds
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
              AND (log_type IN ('data_load', 'error', 'warning', 'info') 
                   OR service_name IS NOT NULL 
                   OR records_processed > 0)
        '''

        params = [days]

        # Simplified status filtering
        if status and status != 'All':
            if status == 'completed':
                query += ' AND ((severity IN ("info","low") AND resolved_at IS NOT NULL) OR (severity IN ("warning","medium") AND resolved_at IS NOT NULL))'
            elif status == 'failed':
                query += ' AND severity IN ("error","critical","high")'
            elif status == 'running':
                query += ' AND severity IN ("warning","medium") AND resolved_at IS NULL'
            elif status == 'pending':
                query += ' AND severity NOT IN ("info","low","warning","medium","error","critical","high")'

        if load_type and load_type != 'All':
            query += ' AND service_name LIKE %s'
            params.append(f'%{load_type}%')

        query += ' ORDER BY created_at DESC LIMIT 100'

        cursor.execute(query, params)
        loads_data = cursor.fetchall()

        # Post-process to ensure consistent data format
        for row in loads_data:
            row['severity'] = _normalize_severity(row.get('severity'))
            # Ensure load_type has a value
            if not row.get('load_type') or row['load_type'] == 'Unknown Service':
                row['load_type'] = row.get('service_name', 'System Process')

        # Get status summary with more inclusive criteria
        cursor.execute('''
            SELECT
                CASE
                    WHEN severity IN ('info','low') AND resolved_at IS NOT NULL THEN 'completed'
                    WHEN severity IN ('warning','medium') AND resolved_at IS NOT NULL THEN 'completed'
                    WHEN severity IN ('error','critical','high') THEN 'failed'
                    WHEN severity IN ('warning','medium') AND resolved_at IS NULL THEN 'running'
                    ELSE 'pending'
                END as status,
                COUNT(*) as count
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
              AND (log_type IN ('data_load', 'error', 'warning', 'info') 
                   OR service_name IS NOT NULL 
                   OR records_processed > 0)
            GROUP BY 1
        ''', (days,))

        status_summary = cursor.fetchall()

        response_data = {
            'loads': loads_data,
            'total_loads': len(loads_data),
            'status_summary': status_summary,
            'analysis_period_days': days
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching data loads: {e}')
        return make_response(jsonify({"error": "Failed to fetch data loads"}), 500)


@admin.route('/data-loads', methods=['POST'])
def start_data_load():
    """
    Start a new data load process.

    Expected JSON Body:
        {
            "load_type": "string" (required),
            "source_file": "string",
            "initiated_by": "string" (required)
        }

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info('POST /system/data-loads - Starting new data load')

        load_data = request.get_json()

        # Validate required fields
        required_fields = ['load_type', 'initiated_by']
        for field in required_fields:
            if field not in load_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        cursor = db.get_db().cursor()

        # Check for existing running loads of the same type
        cursor.execute('''
            SELECT log_id FROM SystemLogs
            WHERE log_type = 'data_load' AND service_name = %s AND resolved_at IS NULL
        ''', (load_data['load_type'],))

        if cursor.fetchone():
            return make_response(jsonify({
                "error": "A load of this type is already running"
            }), 409)

        # Insert new data load
        query = '''
            INSERT INTO SystemLogs (
                log_type, service_name, severity, message, source_file, user_id
            ) VALUES ('data_load', %s, 'warning', 'Data load initiated', %s, 
                (SELECT user_id FROM Users WHERE username = %s LIMIT 1))
        '''

        values = (
            load_data['load_type'],
            load_data.get('source_file'),
            load_data['initiated_by']
        )

        cursor.execute(query, values)
        db.get_db().commit()

        return make_response(jsonify({
            "message": "Data load initiated successfully",
            "load_id": cursor.lastrowid,
            "load_type": load_data['load_type'],
            "status": "running"
        }), 201)

    except Exception as e:
        current_app.logger.error(f'Error starting data load: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to start data load"}), 500)


@admin.route('/data-loads/<int:load_id>', methods=['PUT'])
def update_data_load(load_id):
    """
    Update the status and metrics of a data load.

    Expected JSON Body:
        {
            "status": "string" (completed, failed),
            "records_processed": int,
            "records_failed": int,
            "error_message": "string"
        }

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info(f'PUT /system/data-loads/{load_id} - Updating data load status')

        update_data = request.get_json()

        if not update_data:
            return make_response(jsonify({"error": "No update data provided"}), 400)

        cursor = db.get_db().cursor()

        # Verify load exists
        cursor.execute("SELECT log_id FROM SystemLogs WHERE log_id = %s AND log_type = 'data_load'", (load_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Data load not found"}), 404)

        # Build dynamic update query
        update_fields = []
        values = []

        if 'status' in update_data:
            status = update_data['status']
            if status == 'completed':
                update_fields.append("severity = 'info'")
                update_fields.append("message = 'Data load completed successfully'")
            elif status == 'failed':
                update_fields.append("severity = 'error'")
                if 'error_message' in update_data:
                    update_fields.append("message = %s")
                    values.append(update_data['error_message'])
                else:
                    update_fields.append("message = 'Data load failed'")
            update_fields.append('resolved_at = NOW()')


        for field in ['records_processed', 'records_failed']:
            if field in update_data:
                update_fields.append(f'{field} = %s')
                values.append(update_data[field])

        if update_fields:
            query = f"UPDATE SystemLogs SET {', '.join(update_fields)} WHERE log_id = %s"
            values.append(load_id)
            cursor.execute(query, values)
            db.get_db().commit()

        return make_response(jsonify({
            "message": "Data load updated successfully",
            "load_id": load_id,
            "updated_fields": list(update_data.keys())
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error updating data load: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update data load"}), 500)


# ============================================================================
# ERROR LOGGING & MANAGEMENT ROUTES
# ============================================================================

@admin.route('/error-logs', methods=['GET'])
def get_error_logs():
    """
    Get error log history with comprehensive filtering options.
    """
    try:
        current_app.logger.info('GET /system/error-logs - Fetching error log history')

        severity = request.args.get('severity')
        service_name = request.args.get('service_name')
        resolved = request.args.get('resolved')
        days = request.args.get('days', 7, type=int)

        cursor = db.get_db().cursor()

        # Fixed query to match actual SystemLogs schema
        query = '''
            SELECT
                log_id,
                log_id as data_error_id,
                service_name,
                service_name as table_name,
                severity,
                log_type,
                message,
                created_at as detected_at,
                created_at,
                resolved_at,
                records_processed,
                records_failed,
                user_id,
                resolved_by,
                resolution_notes,
                error_rate_pct,
                response_time,
                source_file
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        '''

        params = [days]

        # Fixed: Double the % characters to escape them properly
        query += '''
            AND (
                log_type IN ('error', 'validation', 'warning') 
                OR severity IN ('error', 'critical', 'high', 'medium', 'warning')
                OR message LIKE '%%error%%'
                OR message LIKE '%%fail%%'
                OR message LIKE '%%timeout%%'
                OR message LIKE '%%exception%%'
                OR records_failed > 0
                OR error_rate_pct > 0
            )
        '''

        # Fixed severity filtering
        if severity and severity != 'All':
            if severity == 'critical':
                query += ' AND (severity IN ("critical", "high") OR log_type = "critical")'
            elif severity == 'error':
                query += ' AND (severity IN ("error", "medium") OR log_type = "error")'
            elif severity == 'warning':
                query += ' AND (severity = "warning" OR log_type = "warning")'
            elif severity == 'info':
                query += ' AND (severity IN ("info", "low") OR log_type = "info")'

        if service_name and service_name != 'All':
            query += ' AND service_name = %s'
            params.append(service_name)

        if resolved is not None:
            if resolved.lower() == 'true':
                query += ' AND resolved_at IS NOT NULL'
            else:
                query += ' AND resolved_at IS NULL'

        query += ' ORDER BY created_at DESC LIMIT 200'

        current_app.logger.debug(f'Executing query with {len(params)} parameters')
        current_app.logger.debug(f'Query: {query}')
        current_app.logger.debug(f'Parameters: {params}')

        cursor.execute(query, params)
        error_logs = cursor.fetchall()

        # Normalize data for frontend
        for log in error_logs:
            # Map severity to standard values
            raw_severity = log.get('severity', 'info')
            log['severity'] = _normalize_severity(raw_severity)
            
            # Ensure required fields exist with defaults
            log['service_name'] = log.get('service_name') or 'System'
            log['table_name'] = log.get('service_name') or 'System'
            log['error_message'] = log.get('message') or 'No message'
            log['record_id'] = log.get('user_id')  # Map user_id to record_id for frontend
            
            # Format timestamps
            if log.get('created_at'):
                log['detected_at'] = log['created_at']

        # Get summary statistics - also fix the LIKE clauses here
        cursor.execute('''
            SELECT
                CASE
                    WHEN severity IN ('critical','high') OR log_type = 'critical' THEN 'critical'
                    WHEN severity IN ('error','medium') OR log_type = 'error' THEN 'error'
                    WHEN severity = 'warning' OR log_type = 'warning' THEN 'warning'
                    WHEN severity IN ('info','low') OR log_type = 'info' THEN 'info'
                    ELSE 'info'
                END as severity_group,
                COUNT(*) as count,
                SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
              AND (
                log_type IN ('error', 'validation', 'warning') 
                OR severity IN ('error', 'critical', 'high', 'medium', 'warning')
                OR message LIKE '%%error%%'
                OR message LIKE '%%fail%%'
                OR message LIKE '%%timeout%%'
                OR message LIKE '%%exception%%'
                OR records_failed > 0
                OR error_rate_pct > 0
              )
            GROUP BY 1
            ORDER BY
                CASE severity_group
                    WHEN 'critical' THEN 1
                    WHEN 'error' THEN 2
                    WHEN 'warning' THEN 3
                    WHEN 'info' THEN 4
                END
        ''', (days,))

        severity_summary = cursor.fetchall()

        response_data = {
            'error_logs': error_logs,
            'errors': error_logs,  # Provide both keys for frontend flexibility
            'total_errors': len(error_logs),
            'severity_breakdown': severity_summary,
            'analysis_period_days': days
        }

        current_app.logger.info(f'Returning {len(error_logs)} error logs')
        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching error logs: {e}')
        import traceback
        current_app.logger.error(f'Full traceback: {traceback.format_exc()}')
        return make_response(jsonify({"error": "Failed to fetch error logs", "details": str(e)}), 500)


# ============================================================================
# DATA VALIDATION & QUALITY ROUTES
# ============================================================================

@admin.route('/data-errors', methods=['GET'])
def get_data_errors():
    """
    Get data validation errors with filtering options.
    """
    try:
        current_app.logger.info('GET /system/data-errors - Fetching data validation errors')

        # Convert days parameter to integer with proper error handling
        days_param = request.args.get('days', '7')
        try:
            days = int(days_param)
        except (ValueError, TypeError):
            days = 7
        
        severity = request.args.get('severity')
        service_name = request.args.get('service_name')
        table_name = request.args.get('table_name')  # Support both parameter names

        cursor = db.get_db().cursor()

        # Query to get data validation errors from SystemLogs
        query = '''
            SELECT
                log_id as data_error_id,
                log_id,
                service_name,
                service_name as table_name,
                severity,
                log_type as error_type,
                message as error_message,
                message,
                created_at as detected_at,
                created_at,
                resolved_at,
                resolved_by,
                resolution_notes,
                records_processed,
                records_failed,
                error_rate_pct,
                response_time,
                source_file,
                user_id
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
              AND (
                log_type IN ('validation', 'data_quality', 'constraint', 'error')
                OR severity IN ('error', 'critical', 'high', 'medium', 'warning')
                OR message LIKE '%%validation%%'
                OR message LIKE '%%constraint%%'
                OR message LIKE '%%duplicate%%'
                OR message LIKE '%%invalid%%'
                OR message LIKE '%%quality%%'
                OR records_failed > 0
                OR error_rate_pct > 0
              )
        '''

        params = [days]

        # Add severity filter
        if severity and severity != 'All':
            if severity == 'critical':
                query += ' AND (severity IN ("critical", "high") OR log_type = "critical")'
            elif severity == 'error':
                query += ' AND (severity IN ("error", "medium") OR log_type = "error")'
            elif severity == 'warning':
                query += ' AND (severity = "warning" OR log_type = "warning")'

        # Add service/table filter (support both parameter names)
        filter_service = service_name or table_name
        if filter_service and filter_service != 'All':
            query += ' AND service_name LIKE %s'
            params.append(f'%{filter_service}%')

        query += ' ORDER BY created_at DESC LIMIT 100'

        current_app.logger.debug(f'Executing data-errors query with {len(params)} parameters')
        current_app.logger.debug(f'Parameters: {params}')

        cursor.execute(query, params)
        data_errors = cursor.fetchall()

        # Process results for frontend compatibility
        for error in data_errors:
            # Normalize severity
            raw_severity = error.get('severity', 'info')
            error['severity'] = _normalize_severity(raw_severity)
            
            # Ensure required fields exist
            error['service_name'] = error.get('service_name') or 'System'
            error['table_name'] = error.get('service_name') or 'System'
            error['error_message'] = error.get('message') or error.get('error_message') or 'No message'
            
            # Map fields for frontend compatibility
            if not error.get('data_error_id'):
                error['data_error_id'] = error.get('log_id')

        # Get summary statistics
        cursor.execute('''
            SELECT
                CASE
                    WHEN severity IN ('critical','high') OR log_type = 'critical' THEN 'critical'
                    WHEN severity IN ('error','medium') OR log_type = 'error' THEN 'error'
                    WHEN severity = 'warning' OR log_type = 'warning' THEN 'warning'
                    ELSE 'info'
                END as severity_group,
                COUNT(*) as count,
                SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count
            FROM SystemLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
              AND (
                log_type IN ('validation', 'data_quality', 'constraint', 'error')
                OR severity IN ('error', 'critical', 'high', 'medium', 'warning')
                OR message LIKE '%%validation%%'
                OR message LIKE '%%constraint%%'
                OR message LIKE '%%duplicate%%'
                OR message LIKE '%%invalid%%'
                OR message LIKE '%%quality%%'
                OR records_failed > 0
                OR error_rate_pct > 0
              )
            GROUP BY 1
        ''', (days,))

        severity_summary = cursor.fetchall()

        response_data = {
            'data_errors': data_errors,
            'errors': data_errors,  # Provide both keys for frontend flexibility
            'error_logs': data_errors,  # Additional compatibility
            'total_errors': len(data_errors),
            'severity_breakdown': severity_summary,
            'analysis_period_days': days
        }

        current_app.logger.info(f'Returning {len(data_errors)} data validation errors')
        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching data errors: {e}')
        import traceback
        current_app.logger.error(f'Full traceback: {traceback.format_exc()}')
        return make_response(jsonify({"error": "Failed to fetch data errors", "details": str(e)}), 500)


@admin.route('/data-cleanup', methods=['GET'])
def get_cleanup_schedule():
    """
    Get the current data cleanup schedule and execution history.

    User Stories: [Mike-2.6]
    """
    try:
        current_app.logger.info('GET /system/data-cleanup - Fetching cleanup schedules')

        cursor = db.get_db().cursor()

        # Get active cleanup schedules (as recurring logs)
        cursor.execute('''
            SELECT
                log_id as schedule_id,
                service_name as cleanup_type,
                message as frequency,
                created_at as last_run,
                user_id as created_by,
                created_at
            FROM SystemLogs
            WHERE log_type = 'cleanup'
            ORDER BY created_at DESC
        ''')

        schedules = cursor.fetchall()


        response_data = {
            'active_schedules': schedules,
            'recent_cleanup_history': schedules,
            'total_active_schedules': len(schedules)
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching cleanup schedules: {e}')
        return make_response(jsonify({"error": "Failed to fetch cleanup schedules"}), 500)


@admin.route('/data-cleanup', methods=['POST'])
def schedule_cleanup():
    """
    Schedule a new data cleanup job.

    Expected JSON Body:
        {
            "cleanup_type": "string" (required),
            "frequency": "string" (daily, weekly, monthly) (required),
            "retention_days": int (required),
            "created_by": "string" (required)
        }

    User Stories: [Mike-2.6]
    """
    try:
        current_app.logger.info('POST /system/data-cleanup - Scheduling new cleanup job')

        cleanup_data = request.get_json()

        # Validate required fields
        required_fields = ['cleanup_type', 'frequency', 'retention_days', 'created_by']
        for field in required_fields:
            if field not in cleanup_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        cursor = db.get_db().cursor()

        # Get user_id from username, or use a default if not found
        user_lookup_query = '''
            SELECT user_id FROM Users WHERE username = %s LIMIT 1
        '''
        cursor.execute(user_lookup_query, (cleanup_data['created_by'],))
        user_result = cursor.fetchone()
        
        # Use the found user_id, or default to 1 (assuming there's a system user)
        user_id = user_result['user_id'] if user_result else 1

        # Insert cleanup schedule
        query = '''
            INSERT INTO SystemLogs (
                log_type, service_name, severity, message, user_id, records_processed
            ) VALUES ('cleanup', %s, 'info', %s, %s, %s)
        '''

        cleanup_message = f"Scheduled {cleanup_data['frequency']} cleanup with {cleanup_data['retention_days']} days retention";
        
        values = (
            cleanup_data['cleanup_type'],
            cleanup_message,
            user_id,
            cleanup_data['retention_days']  # Store retention_days in records_processed field
        )

        cursor.execute(query, values)
        db.get_db().commit()

        new_schedule_id = cursor.lastrowid

        current_app.logger.info(f'Cleanup scheduled successfully: ID {new_schedule_id}, Type: {cleanup_data["cleanup_type"]}')

        return make_response(jsonify({
            "message": "Cleanup scheduled successfully",
            "schedule_id": new_schedule_id,
            "cleanup_type": cleanup_data['cleanup_type'],
            "frequency": cleanup_data['frequency'],
            "retention_days": cleanup_data['retention_days'],
            "created_by": cleanup_data['created_by'],
            "user_id": user_id
        }), 201)

    except Exception as e:
        current_app.logger.error(f'Error scheduling cleanup: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to schedule cleanup", "details": str(e)}), 500)