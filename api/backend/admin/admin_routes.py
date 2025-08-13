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
    
    User Stories: [Mike-2.5]
    """
    try:
        current_app.logger.info('GET /system/health - Checking system health status')
        
        cursor = db.get_db().cursor()
        
        # Verify database connectivity
        cursor.execute('SELECT 1')
        db_status = 'healthy' if cursor.fetchone() else 'unhealthy'
        
        # Get recent error count (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) as error_count 
            FROM ErrorLogs 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        ''')
        recent_errors_result = cursor.fetchone()
        recent_errors = recent_errors_result['error_count'] if recent_errors_result else 0
        
        # Get active data loads
        cursor.execute('''
            SELECT COUNT(*) as active_loads 
            FROM DataLoads 
            WHERE status IN ('running', 'pending')
        ''')
        active_loads_result = cursor.fetchone()
        active_loads = active_loads_result['active_loads'] if active_loads_result else 0
        
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
    """
    Get comprehensive history of data loads with filtering options.
    
    Query Parameters:
        status: Filter by status (pending, running, completed, failed)
        load_type: Filter by type (player_stats, team_data, game_data, etc.)
        days: Number of days to look back (default: 30)
        
    User Stories: [Mike-2.5]
    """
    try:
        current_app.logger.info('GET /system/data-loads - Fetching data load history')
        
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
                source_file,
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
        loads_data = cursor.fetchall()
        
        # Get status summary statistics
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count,
                SUM(records_processed) as total_records_processed,
                SUM(records_failed) as total_records_failed
            FROM DataLoads
            WHERE started_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY status
        ''', (days,))
        
        status_summary = cursor.fetchall()
        
        response_data = {
            'data_loads': loads_data,
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
            SELECT load_id FROM DataLoads 
            WHERE load_type = %s AND status = 'running'
        ''', (load_data['load_type'],))
        
        if cursor.fetchone():
            return make_response(jsonify({
                "error": "A load of this type is already running"
            }), 409)
        
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
            "load_type": load_data['load_type'],
            "status": "pending"
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
            "status": "string" (pending, running, completed, failed),
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
        
        # Validate status if provided
        if 'status' in update_data:
            valid_statuses = ['pending', 'running', 'completed', 'failed']
            if update_data['status'] not in valid_statuses:
                return make_response(jsonify({
                    "error": f"Invalid status. Must be one of: {valid_statuses}"
                }), 400)
        
        cursor = db.get_db().cursor()
        
        # Verify load exists
        cursor.execute('SELECT load_id FROM DataLoads WHERE load_id = %s', (load_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Data load not found"}), 404)
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'status' in update_data:
            update_fields.append('status = %s')
            values.append(update_data['status'])
            
            # Set completed_at timestamp if status is final
            if update_data['status'] in ['completed', 'failed']:
                update_fields.append('completed_at = NOW()')
        
        for field in ['records_processed', 'records_failed', 'error_message']:
            if field in update_data:
                update_fields.append(f'{field} = %s')
                values.append(update_data[field])
        
        if update_fields:
            query = f"UPDATE DataLoads SET {', '.join(update_fields)} WHERE load_id = %s"
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
    
    Query Parameters:
        severity: Filter by severity (info, warning, error, critical)
        module: Filter by module/component
        resolved: Filter by resolved status (true/false)
        days: Number of days to look back (default: 7)
        
    User Stories: [Mike-2.4, Mike-2.5]
    """
    try:
        current_app.logger.info('GET /system/error-logs - Fetching error log history')
        
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
        error_logs = cursor.fetchall()
        
        # Get error summary by severity
        cursor.execute('''
            SELECT 
                severity,
                COUNT(*) as count,
                SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count
            FROM ErrorLogs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY severity
            ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1
                    WHEN 'error' THEN 2  
                    WHEN 'warning' THEN 3
                    WHEN 'info' THEN 4
                END
        ''', (days,))
        
        severity_summary = cursor.fetchall()
        
        response_data = {
            'error_logs': error_logs,
            'total_errors': len(error_logs),
            'severity_breakdown': severity_summary,
            'analysis_period_days': days
        }
        
        return make_response(jsonify(response_data), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error fetching error logs: {e}')
        return make_response(jsonify({"error": "Failed to fetch error logs"}), 500)


@admin.route('/error-logs', methods=['POST'])
def log_error():
    """
    Log a new error in the system.
    
    Expected JSON Body:
        {
            "error_type": "string" (required),
            "severity": "string" (info, warning, error, critical) (required),
            "module": "string" (required),
            "error_message": "string" (required),
            "stack_trace": "string",
            "user_id": int
        }
        
    User Stories: [Mike-2.3]
    """
    try:
        current_app.logger.info('POST /system/error-logs - Logging new system error')
        
        error_data = request.get_json()
        
        # Validate required fields
        required_fields = ['error_type', 'severity', 'module', 'error_message']
        for field in required_fields:
            if field not in error_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        # Validate severity level
        valid_severities = ['info', 'warning', 'error', 'critical']
        if error_data['severity'] not in valid_severities:
            return make_response(jsonify({
                "error": f"Invalid severity. Must be one of: {valid_severities}"
            }), 400)
        
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
            "error_id": new_error_id,
            "severity": error_data['severity']
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error logging system error: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to log error"}), 500)


# ============================================================================
# DATA VALIDATION & QUALITY ROUTES
# ============================================================================

@admin.route('/data-errors', methods=['GET'])
def get_data_errors():
    """
    Get details about data validation errors and integrity issues.
    
    Query Parameters:
        error_type: Filter by error type (duplicate, missing, invalid)
        table_name: Filter by affected table
        days: Number of days to look back (default: 7)
        
    User Stories: [Mike-2.4]
    """
    try:
        current_app.logger.info('GET /system/data-errors - Fetching data validation errors')
        
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
        data_errors = cursor.fetchall()
        
        # Get error summary by type and table
        cursor.execute('''
            SELECT 
                error_type,
                table_name,
                COUNT(*) as count,
                SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count
            FROM DataErrors
            WHERE detected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY error_type, table_name
            ORDER BY count DESC
        ''', (days,))
        
        error_summary = cursor.fetchall()
        
        response_data = {
            'data_errors': data_errors,
            'total_errors': len(data_errors),
            'error_breakdown': error_summary,
            'analysis_period_days': days
        }
        
        return make_response(jsonify(response_data), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error fetching data errors: {e}')
        return make_response(jsonify({"error": "Failed to fetch data errors"}), 500)


@admin.route('/data-cleanup', methods=['GET'])
def get_cleanup_schedule():
    """
    Get the current data cleanup schedule and execution history.
    
    User Stories: [Mike-2.6]
    """
    try:
        current_app.logger.info('GET /system/data-cleanup - Fetching cleanup schedules')
        
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
        
        # Get recent cleanup execution history
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
            'recent_cleanup_history': cleanup_history,
            'total_active_schedules': len(active_schedules)
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
            "next_run": "datetime string",
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
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'monthly']
        if cleanup_data['frequency'] not in valid_frequencies:
            return make_response(jsonify({
                "error": f"Invalid frequency. Must be one of: {valid_frequencies}"
            }), 400)
        
        cursor = db.get_db().cursor()
        
        # Calculate next run time if not provided
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
            "schedule_id": new_schedule_id,
            "cleanup_type": cleanup_data['cleanup_type'],
            "frequency": cleanup_data['frequency']
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error scheduling cleanup: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to schedule cleanup"}), 500)


@admin.route('/data-validation', methods=['GET'])
def get_validation_reports():
    """
    Get data validation reports and integrity check results.
    
    Query Parameters:
        days: Number of days to look back (default: 7)
        status: Filter by validation status (passed, failed, warning)
        
    User Stories: [Mike-2.4]
    """
    try:
        current_app.logger.info('GET /system/data-validation - Fetching validation reports')
        
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
        validation_reports = cursor.fetchall()
        
        response_data = {
            'validation_reports': validation_reports,
            'total_reports': len(validation_reports),
            'analysis_period_days': days
        }
        
        return make_response(jsonify(response_data), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error fetching validation reports: {e}')
        return make_response(jsonify({"error": "Failed to fetch validation reports"}), 500)


@admin.route('/data-validation', methods=['POST'])
def run_validation_check():
    """
    Run a comprehensive data validation check on specified tables.
    
    Expected JSON Body:
        {
            "validation_type": "string" (required),
            "table_name": "string" (required),
            "validation_rules": "object",
            "run_by": "string" (required)
        }
        
    User Stories: [Mike-2.4]
    """
    try:
        current_app.logger.info('POST /system/data-validation - Running validation check')
        
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
        
        # Execute table-specific validation logic
        if table_name == 'Players':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN first_name IS NULL OR last_name IS NULL THEN 1 ELSE 0 END) as invalid_names,
                    SUM(CASE WHEN age <= 0 OR age > 50 THEN 1 ELSE 0 END) as invalid_ages,
                    SUM(CASE WHEN current_salary < 0 THEN 1 ELSE 0 END) as invalid_salaries
                FROM Players
            ''')
            
            result = cursor.fetchone()
            total_records = result['total']
            invalid_records = result['invalid_names'] + result['invalid_ages'] + result['invalid_salaries']
            
        elif table_name == 'Teams':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN name IS NULL OR city IS NULL THEN 1 ELSE 0 END) as invalid_basic,
                    SUM(CASE WHEN conference NOT IN ('Eastern', 'Western') THEN 1 ELSE 0 END) as invalid_conference
                FROM Teams
            ''')
            
            result = cursor.fetchone()
            total_records = result['total']
            invalid_records = result['invalid_basic'] + result['invalid_conference']
            
        elif table_name == 'PlayerGameStats':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN points < 0 OR rebounds < 0 OR assists < 0 THEN 1 ELSE 0 END) as negative_stats,
                    SUM(CASE WHEN shooting_percentage > 1.0 OR shooting_percentage < 0 THEN 1 ELSE 0 END) as invalid_percentages,
                    SUM(CASE WHEN minutes_played > 48 OR minutes_played < 0 THEN 1 ELSE 0 END) as invalid_minutes
                FROM PlayerGameStats
            ''')
            
            result = cursor.fetchone()
            total_records = result['total']
            invalid_records = result['negative_stats'] + result['invalid_percentages'] + result['invalid_minutes']
            
        else:
            # Generic validation for other tables
            cursor.execute(f'SELECT COUNT(*) as total FROM {table_name}')
            result = cursor.fetchone()
            total_records = result['total']
            invalid_records = 0
        
        valid_records = total_records - invalid_records
        
        # Determine validation status
        if invalid_records == 0:
            validation_status = 'passed'
        elif invalid_records < total_records * 0.05:  # Less than 5% invalid
            validation_status = 'warning'
        else:
            validation_status = 'failed'
        
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
            validation_status,
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
            "results": {
                "status": validation_status,
                "total_records": total_records,
                "valid_records": valid_records,
                "invalid_records": invalid_records,
                "validity_percentage": round((valid_records / total_records) * 100, 2) if total_records > 0 else 0
            }
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error running validation check: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to run validation check"}), 500)


# ============================================================================
# BULK DATA OPERATIONS ROUTES
# ============================================================================

@admin.route('/bulk-operations/cleanup', methods=['POST'])
def execute_bulk_cleanup():
    """
    Execute bulk cleanup operations for data maintenance.
    
    Expected JSON Body:
        {
            "operation_type": "string" (required),
            "target_tables": ["string"] (required),
            "retention_days": int (required),
            "dry_run": boolean (default: true),
            "executed_by": "string" (required)
        }
        
    User Stories: [Mike-2.6]
    """
    try:
        current_app.logger.info('POST /system/bulk-operations/cleanup - Executing bulk cleanup')
        
        cleanup_data = request.get_json()
        
        # Validate required fields
        required_fields = ['operation_type', 'target_tables', 'retention_days', 'executed_by']
        for field in required_fields:
            if field not in cleanup_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        dry_run = cleanup_data.get('dry_run', True)
        retention_days = cleanup_data['retention_days']
        
        cursor = db.get_db().cursor()
        
        cleanup_results = []
        total_records_affected = 0
        
        # Process each target table
        for table in cleanup_data['target_tables']:
            if table in ['ErrorLogs', 'DataLoads', 'ValidationReports']:
                # Count records that would be affected
                count_query = f'''
                    SELECT COUNT(*) as count 
                    FROM {table} 
                    WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                '''
                
                cursor.execute(count_query, (retention_days,))
                count_result = cursor.fetchone()
                records_to_delete = count_result['count'] if count_result else 0
                
                if not dry_run and records_to_delete > 0:
                    # Execute actual deletion
                    delete_query = f'''
                        DELETE FROM {table} 
                        WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                    '''
                    cursor.execute(delete_query, (retention_days,))
                
                cleanup_results.append({
                    'table': table,
                    'records_affected': records_to_delete,
                    'action': 'would_delete' if dry_run else 'deleted'
                })
                
                total_records_affected += records_to_delete
        
        if not dry_run:
            db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Bulk cleanup operation completed",
            "dry_run": dry_run,
            "total_records_affected": total_records_affected,
            "cleanup_results": cleanup_results,
            "retention_policy_days": retention_days
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error executing bulk cleanup: {e}')
        if not cleanup_data.get('dry_run', True):
            db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to execute bulk cleanup"}), 500)