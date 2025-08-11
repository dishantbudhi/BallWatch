########################################################
# Admin Blueprint
# System monitoring, data management, and error handling
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from flask import redirect
from flask import url_for
import json
from backend.db_connection import db
from datetime import datetime, timedelta

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
admin = Blueprint('admin', __name__)


#------------------------------------------------------------
# Get system health status [Mike-2.5]
@admin.route('/system-health', methods=['GET'])
def get_system_health():
    """
    Get current system health status including database connectivity,
    recent errors, and performance metrics.
    """
    current_app.logger.info('GET /system-health route')
    
    try:
        cursor = db.get_db().cursor()
        
        # Check database connectivity
        cursor.execute('SELECT 1')
        db_status = 'healthy' if cursor.fetchone() else 'unhealthy'
        
        # Get recent error count
        cursor.execute('''
            SELECT COUNT(*) as error_count 
            FROM ErrorLogs 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        ''')
        recent_errors = cursor.fetchone()['error_count']
        
        # Get active data loads
        cursor.execute('''
            SELECT COUNT(*) as active_loads 
            FROM DataLoads 
            WHERE status IN ('running', 'pending')
        ''')
        active_loads = cursor.fetchone()['active_loads']
        
        # Get last successful data load
        cursor.execute('''
            SELECT load_id, load_type, completed_at 
            FROM DataLoads 
            WHERE status = 'completed'
            ORDER BY completed_at DESC 
            LIMIT 1
        ''')
        last_successful_load = cursor.fetchone()
        
        # Get system metrics
        cursor.execute('''
            SELECT 
                (SELECT COUNT(*) FROM Players) as total_players,
                (SELECT COUNT(*) FROM Teams) as total_teams,
                (SELECT COUNT(*) FROM Game) as total_games,
                (SELECT COUNT(*) FROM Users) as total_users
        ''')
        system_metrics = cursor.fetchone()
        
        response_data = {
            'status': 'operational' if db_status == 'healthy' and recent_errors < 10 else 'degraded',
            'database_status': db_status,
            'recent_errors_24h': recent_errors,
            'active_data_loads': active_loads,
            'last_successful_load': last_successful_load,
            'system_metrics': system_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error checking system health: {e}')
        return make_response(jsonify({
            "status": "error",
            "error": "Failed to check system health",
            "timestamp": datetime.now().isoformat()
        }), 500)


#------------------------------------------------------------
# Get data load history [Mike-2.5]
@admin.route('/data-loads', methods=['GET'])
def get_data_loads():
    """
    Get history of data loads with optional filters.
    Query parameters:
    - status: filter by status (pending, running, completed, failed)
    - load_type: filter by type (player_stats, team_data, game_data, etc.)
    - days: number of days to look back (default: 30)
    """
    current_app.logger.info('GET /data-loads route')
    
    status = request.args.get('status')
    load_type = request.args.get('load_type')
    days = request.args.get('days', 30, type=int)
    
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT 
            load_id,
            load_type,
            status,
            started_at,
            completed_at,
            records_processed,
            records_failed,
            error_message,
            initiated_by,
            TIMESTAMPDIFF(SECOND, started_at, IFNULL(completed_at, NOW())) as duration_seconds
        FROM DataLoads
        WHERE started_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    '''
    
    params = [days]
    
    if status:
        query += ' AND status = %s'
        params.append(status)
    
    if load_type:
        query += ' AND load_type = %s'
        params.append(load_type)
    
    query += ' ORDER BY started_at DESC'
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Get summary statistics
    cursor.execute('''
        SELECT 
            status,
            COUNT(*) as count
        FROM DataLoads
        WHERE started_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY status
    ''', (days,))
    
    status_summary = cursor.fetchall()
    
    response_data = {
        'loads': theData,
        'total_count': len(theData),
        'status_summary': status_summary,
        'filter_days': days
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Start new data load [Mike-2.1]
@admin.route('/data-loads', methods=['POST'])
def start_data_load():
    """
    Start a new data load process.
    Expected JSON body:
    {
        "load_type": "string" (required),
        "source_file": "string",
        "initiated_by": "string" (required)
    }
    """
    current_app.logger.info('POST /data-loads route')
    
    try:
        load_data = request.get_json()
        
        # Validate required fields
        if 'load_type' not in load_data or 'initiated_by' not in load_data:
            return make_response(jsonify({"error": "Missing required fields: load_type and initiated_by"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check for existing running loads of the same type
        cursor.execute('''
            SELECT load_id FROM DataLoads 
            WHERE load_type = %s AND status = 'running'
        ''', (load_data['load_type'],))
        
        if cursor.fetchone():
            return make_response(jsonify({"error": "A load of this type is already running"}), 409)
        
        # Insert new data load
        query = '''
            INSERT INTO DataLoads (
                load_type, status, started_at, source_file, initiated_by
            ) VALUES (%s, 'pending', NOW(), %s, %s)
        '''
        
        values = (
            load_data['load_type'],
            load_data.get('source_file'),
            load_data['initiated_by']
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_load_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Data load initiated successfully",
            "load_id": new_load_id,
            "status": "pending"
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error starting data load: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to start data load"}), 500)


#------------------------------------------------------------
# Update data load status [Mike-2.1]
@admin.route('/data-loads/<int:load_id>', methods=['PUT'])
def update_data_load(load_id):
    """
    Update the status of a data load.
    Expected JSON body:
    {
        "status": "string" (pending, running, completed, failed),
        "records_processed": int,
        "records_failed": int,
        "error_message": "string"
    }
    """
    current_app.logger.info(f'PUT /data-loads/{load_id} route')
    
    try:
        update_data = request.get_json()
        
        if not update_data:
            return make_response(jsonify({"error": "No update data provided"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'status' in update_data:
            update_fields.append('status = %s')
            values.append(update_data['status'])
            
            # Set completed_at if status is completed or failed
            if update_data['status'] in ['completed', 'failed']:
                update_fields.append('completed_at = NOW()')
        
        if 'records_processed' in update_data:
            update_fields.append('records_processed = %s')
            values.append(update_data['records_processed'])
        
        if 'records_failed' in update_data:
            update_fields.append('records_failed = %s')
            values.append(update_data['records_failed'])
        
        if 'error_message' in update_data:
            update_fields.append('error_message = %s')
            values.append(update_data['error_message'])
        
        if update_fields:
            query = f"UPDATE DataLoads SET {', '.join(update_fields)} WHERE load_id = %s"
            values.append(load_id)
            cursor.execute(query, values)
            db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Data load updated successfully",
            "load_id": load_id
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating data load: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update data load"}), 500)


#------------------------------------------------------------
# Get error logs [Mike-2.4, Mike-2.5]
@admin.route('/error-logs', methods=['GET'])
def get_error_logs():
    """
    Get error log history with optional filters.
    Query parameters:
    - severity: filter by severity (info, warning, error, critical)
    - module: filter by module/component
    - resolved: filter by resolved status (true/false)
    - days: number of days to look back (default: 7)
    """
    current_app.logger.info('GET /error-logs route')
    
    severity = request.args.get('severity')
    module = request.args.get('module')
    resolved = request.args.get('resolved')
    days = request.args.get('days', 7, type=int)
    
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT 
            error_id,
            error_type,
            severity,
            module,
            error_message,
            stack_trace,
            user_id,
            created_at,
            resolved_at,
            resolved_by,
            resolution_notes
        FROM ErrorLogs
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    '''
    
    params = [days]
    
    if severity:
        query += ' AND severity = %s'
        params.append(severity)
    
    if module:
        query += ' AND module = %s'
        params.append(module)
    
    if resolved is not None:
        if resolved.lower() == 'true':
            query += ' AND resolved_at IS NOT NULL'
        else:
            query += ' AND resolved_at IS NULL'
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Get error summary
    cursor.execute('''
        SELECT 
            severity,
            COUNT(*) as count
        FROM ErrorLogs
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY severity
    ''', (days,))
    
    severity_summary = cursor.fetchall()
    
    response_data = {
        'errors': theData,
        'total_count': len(theData),
        'severity_summary': severity_summary,
        'filter_days': days
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Log new error [Mike-2.3]
@admin.route('/error-logs', methods=['POST'])
def log_error():
    """
    Log a new error in the system.
    Expected JSON body:
    {
        "error_type": "string" (required),
        "severity": "string" (info, warning, error, critical) (required),
        "module": "string" (required),
        "error_message": "string" (required),
        "stack_trace": "string",
        "user_id": int
    }
    """
    current_app.logger.info('POST /error-logs route')
    
    try:
        error_data = request.get_json()
        
        # Validate required fields
        required_fields = ['error_type', 'severity', 'module', 'error_message']
        for field in required_fields:
            if field not in error_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        # Validate severity level
        valid_severities = ['info', 'warning', 'error', 'critical']
        if error_data['severity'] not in valid_severities:
            return make_response(jsonify({"error": f"Invalid severity. Must be one of: {valid_severities}"}), 400)
        
        cursor = db.get_db().cursor()
        
        query = '''
            INSERT INTO ErrorLogs (
                error_type, severity, module, error_message, 
                stack_trace, user_id, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
        '''
        
        values = (
            error_data['error_type'],
            error_data['severity'],
            error_data['module'],
            error_data['error_message'],
            error_data.get('stack_trace'),
            error_data.get('user_id')
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_error_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Error logged successfully",
            "error_id": new_error_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error logging error: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to log error"}), 500)


#------------------------------------------------------------
# Update error status [Mike-2.3]
@admin.route('/error-logs/<int:error_id>', methods=['PUT'])
def update_error_log(error_id):
    """
    Update the status of an error log (mark as resolved).
    Expected JSON body:
    {
        "resolved": boolean,
        "resolved_by": "string",
        "resolution_notes": "string"
    }
    """
    current_app.logger.info(f'PUT /error-logs/{error_id} route')
    
    try:
        update_data = request.get_json()
        
        if not update_data:
            return make_response(jsonify({"error": "No update data provided"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build update query
        update_fields = []
        values = []
        
        if 'resolved' in update_data and update_data['resolved']:
            update_fields.append('resolved_at = NOW()')
            
            if 'resolved_by' in update_data:
                update_fields.append('resolved_by = %s')
                values.append(update_data['resolved_by'])
            
            if 'resolution_notes' in update_data:
                update_fields.append('resolution_notes = %s')
                values.append(update_data['resolution_notes'])
        
        if update_fields:
            query = f"UPDATE ErrorLogs SET {', '.join(update_fields)} WHERE error_id = %s"
            values.append(error_id)
            cursor.execute(query, values)
            db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Error log updated successfully",
            "error_id": error_id
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating error log: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update error log"}), 500)


#------------------------------------------------------------
# Purge old error logs [Mike-2.6]
@admin.route('/error-logs', methods=['DELETE'])
def purge_error_logs():
    """
    Purge old error logs from the system.
    Query parameters:
    - days: delete logs older than this many days (required, min: 30)
    - severity: only delete logs of this severity or lower
    """
    current_app.logger.info('DELETE /error-logs route')
    
    days = request.args.get('days', type=int)
    severity = request.args.get('severity')
    
    if not days or days < 30:
        return make_response(jsonify({"error": "Days parameter required and must be at least 30"}), 400)
    
    try:
        cursor = db.get_db().cursor()
        
        # Build delete query
        query = 'DELETE FROM ErrorLogs WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)'
        params = [days]
        
        if severity:
            # Delete only logs of specified severity or lower
            severity_levels = {'info': 1, 'warning': 2, 'error': 3, 'critical': 4}
            if severity in severity_levels:
                query += ' AND severity IN (%s'
                params.append('info')
                if severity_levels[severity] >= 2:
                    query += ', %s'
                    params.append('warning')
                if severity_levels[severity] >= 3:
                    query += ', %s'
                    params.append('error')
                query += ')'
        
        cursor.execute(query, params)
        deleted_count = cursor.rowcount
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Error logs purged successfully",
            "deleted_count": deleted_count
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error purging error logs: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to purge error logs"}), 500)


#------------------------------------------------------------
# Get data error details [Mike-2.4]
@admin.route('/data-errors', methods=['GET'])
def get_data_errors():
    """
    Get details about data validation errors.
    Query parameters:
    - error_type: filter by error type (duplicate, missing, invalid)
    - table_name: filter by affected table
    - days: number of days to look back (default: 7)
    """
    current_app.logger.info('GET /data-errors route')
    
    error_type = request.args.get('error_type')
    table_name = request.args.get('table_name')
    days = request.args.get('days', 7, type=int)
    
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT 
            data_error_id,
            error_type,
            table_name,
            record_id,
            field_name,
            invalid_value,
            expected_format,
            detected_at,
            resolved_at,
            auto_fixed
        FROM DataErrors
        WHERE detected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    '''
    
    params = [days]
    
    if error_type:
        query += ' AND error_type = %s'
        params.append(error_type)
    
    if table_name:
        query += ' AND table_name = %s'
        params.append(table_name)
    
    query += ' ORDER BY detected_at DESC'
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Get error summary by table
    cursor.execute('''
        SELECT 
            table_name,
            error_type,
            COUNT(*) as count
        FROM DataErrors
        WHERE detected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            AND resolved_at IS NULL
        GROUP BY table_name, error_type
    ''', (days,))
    
    error_summary = cursor.fetchall()
    
    response_data = {
        'errors': theData,
        'total_count': len(theData),
        'error_summary': error_summary,
        'filter_days': days
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Remove resolved data errors [Mike-2.3]
@admin.route('/data-errors', methods=['DELETE'])
def remove_resolved_errors():
    """
    Remove resolved data errors from the system.
    Query parameters:
    - days: remove errors resolved more than this many days ago (default: 30)
    """
    current_app.logger.info('DELETE /data-errors route')
    
    days = request.args.get('days', 30, type=int)
    
    try:
        cursor = db.get_db().cursor()
        
        query = '''
            DELETE FROM DataErrors 
            WHERE resolved_at IS NOT NULL 
                AND resolved_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        '''
        
        cursor.execute(query, (days,))
        deleted_count = cursor.rowcount
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Resolved data errors removed successfully",
            "deleted_count": deleted_count
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error removing data errors: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to remove data errors"}), 500)


#------------------------------------------------------------
# Get cleanup schedule [Mike-2.6]
@admin.route('/data-cleanup', methods=['GET'])
def get_cleanup_schedule():
    """
    Get the current data cleanup schedule and history.
    """
    current_app.logger.info('GET /data-cleanup route')
    
    cursor = db.get_db().cursor()
    
    # Get active cleanup schedules
    cursor.execute('''
        SELECT 
            schedule_id,
            cleanup_type,
            frequency,
            next_run,
            last_run,
            retention_days,
            is_active,
            created_by,
            created_at
        FROM CleanupSchedule
        WHERE is_active = 1
        ORDER BY next_run
    ''')
    
    active_schedules = cursor.fetchall()
    
    # Get recent cleanup history
    cursor.execute('''
        SELECT 
            history_id,
            schedule_id,
            cleanup_type,
            started_at,
            completed_at,
            records_deleted,
            status,
            error_message
        FROM CleanupHistory
        WHERE started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        ORDER BY started_at DESC
        LIMIT 20
    ''')
    
    cleanup_history = cursor.fetchall()
    
    response_data = {
        'active_schedules': active_schedules,
        'recent_history': cleanup_history
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Schedule data cleanup [Mike-2.6]
@admin.route('/data-cleanup', methods=['POST'])
def schedule_cleanup():
    """
    Schedule a new data cleanup job.
    Expected JSON body:
    {
        "cleanup_type": "string" (required),
        "frequency": "string" (daily, weekly, monthly) (required),
        "retention_days": int (required),
        "next_run": "datetime string",
        "created_by": "string" (required)
    }
    """
    current_app.logger.info('POST /data-cleanup route')
    
    try:
        cleanup_data = request.get_json()
        
        # Validate required fields
        required_fields = ['cleanup_type', 'frequency', 'retention_days', 'created_by']
        for field in required_fields:
            if field not in cleanup_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'monthly']
        if cleanup_data['frequency'] not in valid_frequencies:
            return make_response(jsonify({"error": f"Invalid frequency. Must be one of: {valid_frequencies}"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check for existing active schedule of the same type
        cursor.execute('''
            SELECT schedule_id FROM CleanupSchedule 
            WHERE cleanup_type = %s AND is_active = 1
        ''', (cleanup_data['cleanup_type'],))
        
        if cursor.fetchone():
            return make_response(jsonify({"error": "An active schedule for this cleanup type already exists"}), 409)
        
        # Calculate next run if not provided
        if 'next_run' not in cleanup_data:
            if cleanup_data['frequency'] == 'daily':
                next_run = datetime.now() + timedelta(days=1)
            elif cleanup_data['frequency'] == 'weekly':
                next_run = datetime.now() + timedelta(weeks=1)
            else:  # monthly
                next_run = datetime.now() + timedelta(days=30)
            cleanup_data['next_run'] = next_run.isoformat()
        
        query = '''
            INSERT INTO CleanupSchedule (
                cleanup_type, frequency, next_run, retention_days, 
                is_active, created_by, created_at
            ) VALUES (%s, %s, %s, %s, 1, %s, NOW())
        '''
        
        values = (
            cleanup_data['cleanup_type'],
            cleanup_data['frequency'],
            cleanup_data['next_run'],
            cleanup_data['retention_days'],
            cleanup_data['created_by']
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_schedule_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Cleanup scheduled successfully",
            "schedule_id": new_schedule_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error scheduling cleanup: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to schedule cleanup"}), 500)


#------------------------------------------------------------
# Update cleanup schedule [Mike-2.6]
@admin.route('/data-cleanup/<int:schedule_id>', methods=['PUT'])
def update_cleanup_schedule(schedule_id):
    """
    Update an existing cleanup schedule.
    Expected JSON body (all fields optional):
    {
        "frequency": "string",
        "next_run": "datetime string",
        "retention_days": int,
        "is_active": boolean
    }
    """
    current_app.logger.info(f'PUT /data-cleanup/{schedule_id} route')
    
    try:
        update_data = request.get_json()
        
        if not update_data:
            return make_response(jsonify({"error": "No update data provided"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'frequency' in update_data:
            valid_frequencies = ['daily', 'weekly', 'monthly']
            if update_data['frequency'] not in valid_frequencies:
                return make_response(jsonify({"error": f"Invalid frequency. Must be one of: {valid_frequencies}"}), 400)
            update_fields.append('frequency = %s')
            values.append(update_data['frequency'])
        
        if 'next_run' in update_data:
            update_fields.append('next_run = %s')
            values.append(update_data['next_run'])
        
        if 'retention_days' in update_data:
            update_fields.append('retention_days = %s')
            values.append(update_data['retention_days'])
        
        if 'is_active' in update_data:
            update_fields.append('is_active = %s')
            values.append(1 if update_data['is_active'] else 0)
        
        if update_fields:
            query = f"UPDATE CleanupSchedule SET {', '.join(update_fields)} WHERE schedule_id = %s"
            values.append(schedule_id)
            cursor.execute(query, values)
            db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Cleanup schedule updated successfully",
            "schedule_id": schedule_id
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating cleanup schedule: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update cleanup schedule"}), 500)


#------------------------------------------------------------
# Get data validation reports [Mike-2.4]
@admin.route('/data-validation', methods=['GET'])
def get_validation_reports():
    """
    Get data validation reports and integrity check results.
    Query parameters:
    - days: number of days to look back (default: 7)
    - status: filter by validation status (passed, failed, warning)
    """
    current_app.logger.info('GET /data-validation route')
    
    days = request.args.get('days', 7, type=int)
    status = request.args.get('status')
    
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT 
            validation_id,
            validation_type,
            table_name,
            status,
            total_records,
            valid_records,
            invalid_records,
            validation_rules,
            error_details,
            run_date,
            run_by
        FROM ValidationReports
        WHERE run_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
    '''
    
    params = [days]
    
    if status:
        query += ' AND status = %s'
        params.append(status)
    
    query += ' ORDER BY run_date DESC'
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Get validation summary
    cursor.execute('''
        SELECT 
            table_name,
            COUNT(*) as validation_count,
            SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warnings
        FROM ValidationReports
        WHERE run_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY table_name
    ''', (days,))
    
    validation_summary = cursor.fetchall()
    
    response_data = {
        'reports': theData,
        'total_count': len(theData),
        'summary': validation_summary,
        'filter_days': days
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Run data validation check [Mike-2.4]
@admin.route('/data-validation', methods=['POST'])
def run_validation_check():
    """
    Run a data validation check on specified tables.
    Expected JSON body:
    {
        "validation_type": "string" (required),
        "table_name": "string" (required),
        "validation_rules": "object",
        "run_by": "string" (required)
    }
    """
    current_app.logger.info('POST /data-validation route')
    
    try:
        validation_data = request.get_json()
        
        # Validate required fields
        required_fields = ['validation_type', 'table_name', 'run_by']
        for field in required_fields:
            if field not in validation_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Perform validation based on table_name
        table_name = validation_data['table_name']
        validation_type = validation_data['validation_type']
        
        # Example validation: check for null values in required fields
        if table_name == 'Players':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN first_name IS NULL OR last_name IS NULL THEN 1 ELSE 0 END) as invalid
                FROM Players
            ''')
        elif table_name == 'Teams':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN name IS NULL OR city IS NULL THEN 1 ELSE 0 END) as invalid
                FROM Teams
            ''')
        else:
            # Generic count for other tables
            cursor.execute(f'SELECT COUNT(*) as total, 0 as invalid FROM {table_name}')
        
        result = cursor.fetchone()
        total_records = result['total']
        invalid_records = result['invalid']
        valid_records = total_records - invalid_records
        
        # Determine status
        if invalid_records == 0:
            status = 'passed'
        elif invalid_records < total_records * 0.05:  # Less than 5% invalid
            status = 'warning'
        else:
            status = 'failed'
        
        # Insert validation report
        query = '''
            INSERT INTO ValidationReports (
                validation_type, table_name, status, total_records, 
                valid_records, invalid_records, validation_rules, 
                run_date, run_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        '''
        
        values = (
            validation_type,
            table_name,
            status,
            total_records,
            valid_records,
            invalid_records,
            json.dumps(validation_data.get('validation_rules', {})),
            validation_data['run_by']
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_validation_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Validation check completed",
            "validation_id": new_validation_id,
            "status": status,
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error running validation check: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to run validation check"}), 500)