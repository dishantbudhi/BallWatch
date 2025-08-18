"""Data Engineer blueprint - proxies to system admin style endpoints under /data-engineer/*.
User Stories: Mike (2.1, 2.4, 2.6)
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

data_engineer = Blueprint('data_engineer', __name__)


@data_engineer.route('/data-loads', methods=['POST'])
def de_start_data_load():
    try:
        payload = request.get_json() or {}
        required = ['load_type', 'initiated_by']
        for f in required:
            if f not in payload:
                return make_response(jsonify({'error': f'Missing required field: {f}'}), 400)
        cursor = db.get_db().cursor()
        cursor.execute('''
            INSERT INTO SystemLogs (log_type, service_name, severity, message, source_file, user_id)
            VALUES ('data_load', %s, 'warning', 'Data load initiated', %s,
                (SELECT user_id FROM Users WHERE username = %s LIMIT 1))
        ''', (payload['load_type'], payload.get('source_file'), payload['initiated_by']))
        db.get_db().commit()
        return make_response(jsonify({'message': 'Data load initiated', 'load_id': cursor.lastrowid}), 201)
    except Exception as e:
        current_app.logger.error(f'de_start_data_load error: {e}')
        db.get_db().rollback()
        return make_response(jsonify({'error': 'Failed to start data load'}), 500)


@data_engineer.route('/data-validation', methods=['GET'])
def de_get_data_validation():
    """Alias of admin.data-errors for convenience."""
    try:
        cursor = db.get_db().cursor()
        days = request.args.get('days', 7, type=int)
        service_name = request.args.get('service_name')
        severity = request.args.get('severity')
        query = '''
            SELECT log_id as data_error_id, service_name as table_name, severity, message as error_message,
                   records_processed, records_failed, created_at as detected_at, resolved_at
            FROM SystemLogs
            WHERE (log_type = 'validation' OR log_type = 'error' OR LOWER(service_name) LIKE '%data%')
              AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        '''
        params = [days]
        if service_name:
            query += ' AND service_name = %s'
            params.append(service_name)
        if severity:
            query += ' AND (LOWER(severity) = %s OR LOWER(severity) = %s)'
            sev = severity.lower()
            params.extend([sev, 'high' if sev == 'critical' else 'medium' if sev == 'error' else 'low' if sev == 'info' else sev])
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return make_response(jsonify({'errors': rows, 'total_errors': len(rows)}), 200)
    except Exception as e:
        current_app.logger.error(f'de_get_data_validation error: {e}')
        return make_response(jsonify({'error': 'Failed to fetch data validation'}), 500)


@data_engineer.route('/error-logs', methods=['DELETE'])
def de_delete_error_logs():
    """Proxy to cleanup logs (same behavior as admin)."""
    try:
        severity = request.args.get('severity')
        service_name = request.args.get('service_name')
        older_than_days = request.args.get('older_than_days', 7, type=int)
        cursor = db.get_db().cursor()
        query = '''
            DELETE FROM SystemLogs
            WHERE (log_type IN ('error','validation') OR severity IS NOT NULL)
              AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        '''
        params = [older_than_days]
        if severity:
            query += ' AND LOWER(severity) = %s'
            params.append(severity.lower())
        if service_name:
            query += ' AND service_name = %s'
            params.append(service_name)
        cursor.execute(query, params)
        deleted = cursor.rowcount
        db.get_db().commit()
        return make_response(jsonify({'deleted_count': deleted}), 200)
    except Exception as e:
        current_app.logger.error(f'de_delete_error_logs error: {e}')
        db.get_db().rollback()
        return make_response(jsonify({'error': 'Failed to delete error logs'}), 500)


