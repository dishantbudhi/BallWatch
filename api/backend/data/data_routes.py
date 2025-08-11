########################################################
# Data Validation Blueprint
# Returns validation reports and runs validation checks
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from datetime import datetime
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
data_validation = Blueprint('data_validation', __name__)

#------------------------------------------------------------
# Get validation reports
# This route returns historical validation reports and current data quality status
@data_validation.route('/data-validation', methods=['GET'])
def get_validation_reports():
    """
    Returns data validation reports showing data quality issues
    Query parameters:
    - limit: number of recent reports to return (default: 50)
    - error_type: filter by specific error type (optional)
    """
    current_app.logger.info('GET /data-validation route')
    
    limit = request.args.get('limit', 50, type=int)
    error_type = request.args.get('error_type', None)
    
    cursor = db.get_db().cursor()
    
    # Get recent validation errors with details
    base_query = '''
        SELECT 
            el.error_id,
            el.timestamp,
            el.error_type,
            el.error_message,
            el.service_component,
            dl.data_source,
            dl.load_date,
            dl.status as load_status
        FROM ErrorLogs el
        LEFT JOIN DataErrors de ON el.error_id = de.error_id
        LEFT JOIN DataLoads dl ON de.load_id = dl.load_id
        WHERE el.service_component IN ('DataValidation', 'DataQuality', 'DataIntegrity')
    '''
    
    query_params = []
    
    # Add error type filter if provided
    if error_type:
        base_query += ' AND el.error_type = %s'
        query_params.append(error_type)
    
    base_query += ' ORDER BY el.timestamp DESC LIMIT %s'
    query_params.append(limit)
    
    cursor.execute(base_query, query_params)
    validation_errors = cursor.fetchall()
    
    # Get summary statistics of data quality issues
    cursor.execute('''
        SELECT 
            error_type,
            COUNT(*) as error_count,
            MAX(timestamp) as latest_occurrence
        FROM ErrorLogs 
        WHERE service_component IN ('DataValidation', 'DataQuality', 'DataIntegrity')
        AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY error_type
        ORDER BY error_count DESC
    ''')
    error_summary = cursor.fetchall()
    
    # Get current data quality metrics
    cursor.execute('''
        SELECT 
            'shooting_percentage_invalid' as metric_name,
            COUNT(*) as issue_count,
            'PlayerGameStats' as table_name
        FROM PlayerGameStats 
        WHERE shooting_percentage > 1.0 OR shooting_percentage < 0
        
        UNION ALL
        
        SELECT 
            'negative_stats' as metric_name,
            COUNT(*) as issue_count,
            'PlayerGameStats' as table_name
        FROM PlayerGameStats 
        WHERE points < 0 OR rebounds < 0 OR assists < 0
        
        UNION ALL
        
        SELECT 
            'invalid_minutes' as metric_name,
            COUNT(*) as issue_count,
            'PlayerGameStats' as table_name
        FROM PlayerGameStats 
        WHERE minutes_played > 48 OR minutes_played < 0
        
        UNION ALL
        
        SELECT 
            'missing_player_info' as metric_name,
            COUNT(*) as issue_count,
            'Players' as table_name
        FROM Players 
        WHERE first_name IS NULL OR last_name IS NULL OR position IS NULL
    ''')
    current_issues = cursor.fetchall()
    
    response_data = {
        'validation_reports': {
            'recent_errors': validation_errors,
            'error_summary_last_7_days': error_summary,
            'current_data_issues': current_issues
        },
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_errors_returned': len(validation_errors),
            'error_type_filter': error_type,
            'limit_applied': limit
        }
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Run validation checks
# This route triggers new validation checks and returns immediate results
@data_validation.route('/data-validation', methods=['POST'])
def run_validation_check():
    """
    Runs comprehensive data validation checks and logs any issues found
    Request body (optional):
    {
        "validation_types": ["data_quality", "data_integrity", "referential_integrity"],
        "table_focus": "PlayerGameStats"  // optional - focus on specific table
    }
    """
    current_app.logger.info('POST /data-validation route')
    
    # Get request parameters
    request_data = request.get_json() or {}
    validation_types = request_data.get('validation_types', ['data_quality', 'data_integrity'])
    table_focus = request_data.get('table_focus', None)
    
    cursor = db.get_db().cursor()
    validation_results = []
    errors_logged = 0
    
    # Data Quality Checks
    if 'data_quality' in validation_types:
        # Check for invalid shooting percentages
        cursor.execute('''
            SELECT COUNT(*) as invalid_count
            FROM PlayerGameStats 
            WHERE shooting_percentage > 1.0 OR shooting_percentage < 0
        ''')
        invalid_shooting = cursor.fetchone()
        
        if invalid_shooting['invalid_count'] > 0:
            # Log the error
            cursor.execute('''
                INSERT INTO ErrorLogs (error_type, error_message, service_component)
                VALUES ('DataQuality', %s, 'DataValidation')
            ''', (f"Found {invalid_shooting['invalid_count']} invalid shooting percentages",))
            errors_logged += 1
            
        validation_results.append({
            'check_type': 'shooting_percentage_validation',
            'table': 'PlayerGameStats',
            'issues_found': invalid_shooting['invalid_count'],
            'status': 'FAIL' if invalid_shooting['invalid_count'] > 0 else 'PASS'
        })
        
        # Check for negative stats
        cursor.execute('''
            SELECT COUNT(*) as invalid_count
            FROM PlayerGameStats 
            WHERE points < 0 OR rebounds < 0 OR assists < 0
        ''')
        negative_stats = cursor.fetchone()
        
        if negative_stats['invalid_count'] > 0:
            cursor.execute('''
                INSERT INTO ErrorLogs (error_type, error_message, service_component)
                VALUES ('DataQuality', %s, 'DataValidation')
            ''', (f"Found {negative_stats['invalid_count']} records with negative stats",))
            errors_logged += 1
            
        validation_results.append({
            'check_type': 'negative_stats_validation',
            'table': 'PlayerGameStats',
            'issues_found': negative_stats['invalid_count'],
            'status': 'FAIL' if negative_stats['invalid_count'] > 0 else 'PASS'
        })
        
        # Check for invalid minutes played
        cursor.execute('''
            SELECT COUNT(*) as invalid_count
            FROM PlayerGameStats 
            WHERE minutes_played > 48 OR minutes_played < 0
        ''')
        invalid_minutes = cursor.fetchone()
        
        if invalid_minutes['invalid_count'] > 0:
            cursor.execute('''
                INSERT INTO ErrorLogs (error_type, error_message, service_component)
                VALUES ('DataQuality', %s, 'DataValidation')
            ''', (f"Found {invalid_minutes['invalid_count']} records with invalid minutes played",))
            errors_logged += 1
            
        validation_results.append({
            'check_type': 'minutes_played_validation',
            'table': 'PlayerGameStats',
            'issues_found': invalid_minutes['invalid_count'],
            'status': 'FAIL' if invalid_minutes['invalid_count'] > 0 else 'PASS'
        })
    
    # Data Integrity Checks
    if 'data_integrity' in validation_types:
        # Check for duplicate game entries
        cursor.execute('''
            SELECT COUNT(*) as duplicate_count
            FROM (
                SELECT date, home_team_id, away_team_id, COUNT(*) as cnt
                FROM Game 
                GROUP BY date, home_team_id, away_team_id 
                HAVING cnt > 1
            ) duplicates
        ''')
        duplicate_games = cursor.fetchone()
        
        if duplicate_games['duplicate_count'] > 0:
            cursor.execute('''
                INSERT INTO ErrorLogs (error_type, error_message, service_component)
                VALUES ('DataIntegrity', %s, 'DataValidation')
            ''', (f"Found {duplicate_games['duplicate_count']} duplicate game entries",))
            errors_logged += 1
            
        validation_results.append({
            'check_type': 'duplicate_games_check',
            'table': 'Game',
            'issues_found': duplicate_games['duplicate_count'],
            'status': 'FAIL' if duplicate_games['duplicate_count'] > 0 else 'PASS'
        })
        
        # Check for missing player information
        cursor.execute('''
            SELECT COUNT(*) as missing_info_count
            FROM Players 
            WHERE first_name IS NULL OR last_name IS NULL OR position IS NULL
        ''')
        missing_player_info = cursor.fetchone()
        
        if missing_player_info['missing_info_count'] > 0:
            cursor.execute('''
                INSERT INTO ErrorLogs (error_type, error_message, service_component)
                VALUES ('DataIntegrity', %s, 'DataValidation')
            ''', (f"Found {missing_player_info['missing_info_count']} players with missing required information",))
            errors_logged += 1
            
        validation_results.append({
            'check_type': 'missing_player_info_check',
            'table': 'Players',
            'issues_found': missing_player_info['missing_info_count'],
            'status': 'FAIL' if missing_player_info['missing_info_count'] > 0 else 'PASS'
        })
    
    # Calculate overall status
    total_issues = sum(result['issues_found'] for result in validation_results)
    overall_status = 'FAIL' if total_issues > 0 else 'PASS'
    
    response_data = {
        'validation_run': {
            'timestamp': datetime.now().isoformat(),
            'validation_types': validation_types,
            'table_focus': table_focus,
            'overall_status': overall_status,
            'total_issues_found': total_issues,
            'errors_logged': errors_logged
        },
        'validation_results': validation_results,
        'summary': {
            'checks_performed': len(validation_results),
            'checks_passed': len([r for r in validation_results if r['status'] == 'PASS']),
            'checks_failed': len([r for r in validation_results if r['status'] == 'FAIL'])
        }
    }
    
    db.get_db().commit()  # Commit the error logs
    
    status_code = 200 if overall_status == 'PASS' else 422
    the_response = make_response(jsonify(response_data))
    the_response.status_code = status_code
    return the_response