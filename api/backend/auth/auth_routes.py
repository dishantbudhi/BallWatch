"""Auth blueprint - demo authentication endpoints."""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

auth = Blueprint('auth', __name__)


@auth.route('/users', methods=['GET'])
def get_users():
    """
    Get users with optional role filter.
    Query params:
        role: filter by role
    Returns JSON: {'users': [...], 'total': int}
    """
    try:
        current_app.logger.info('GET /auth/users - Fetching users')

        role = request.args.get('role')
        cursor = db.get_db().cursor()

        query = '''
            SELECT user_id, username, email, role, created_at, is_active, team_id
            FROM Users
            WHERE 1=1
        '''

        params = []
        if role:
            query += ' AND role = %s'
            params.append(role)

        query += ' ORDER BY username'

        cursor.execute(query, params)
        users = cursor.fetchall()

        return make_response(jsonify({'users': users, 'total': len(users)}), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching users (auth): {e}')
        return make_response(jsonify({"error": "Failed to fetch users"}), 500)


@auth.route('/login', methods=['POST'])
def login():
    """
    Demo login endpoint. Expects JSON: { 'username': <str>, 'password': <str> }
    Returns user profile if username exists.
    """
    try:
        current_app.logger.info('POST /auth/login - Login attempt')

        data = request.get_json() or {}
        username = data.get('username')

        if not username:
            return make_response(jsonify({"error": "username is required"}), 400)

        cursor = db.get_db().cursor()
        cursor.execute('''
            SELECT user_id, username, email, role, created_at, is_active, team_id
            FROM Users
            WHERE username = %s
            LIMIT 1
        ''', (username,))

        user = cursor.fetchone()
        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify({'user': user}), 200)

    except Exception as e:
        current_app.logger.error(f'Error in auth.login: {e}')
        return make_response(jsonify({"error": "Failed to authenticate"}), 500)


@auth.route('/users/<int:user_id>/assign-team', methods=['PUT'])
def assign_team(user_id):
    """Assign a team to a user. Only allowed for users with role head_coach or general_manager.
    Expects JSON: { 'team_id': <int> }
    """
    try:
        data = request.get_json() or {}
        team_id = data.get('team_id')
        if team_id is None:
            return make_response(jsonify({'error': 'team_id is required'}), 400)

        cursor = db.get_db().cursor()
        # verify user exists and has proper role
        cursor.execute('SELECT role FROM Users WHERE user_id = %s LIMIT 1', (user_id,))
        user = cursor.fetchone()
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        role = (user.get('role') or '').lower()
        if role not in ('head_coach', 'general_manager', 'coach', 'gm'):
            return make_response(jsonify({'error': 'User role not allowed to be assigned a team'}), 403)

        # verify team exists
        cursor.execute('SELECT team_id FROM Teams WHERE team_id = %s LIMIT 1', (team_id,))
        team = cursor.fetchone()
        if not team:
            return make_response(jsonify({'error': 'Team not found'}), 404)

        # perform update
        cursor.execute('UPDATE Users SET team_id = %s WHERE user_id = %s', (team_id, user_id))
        db.get_db().commit()

        # return updated user row
        cursor.execute('SELECT user_id, username, email, role, created_at, is_active, team_id FROM Users WHERE user_id = %s LIMIT 1', (user_id,))
        updated = cursor.fetchone()
        return make_response(jsonify({'user': updated}), 200)

    except Exception as e:
        current_app.logger.error(f'Error in auth.assign_team: {e}')
        return make_response(jsonify({'error': 'Failed to assign team'}), 500)
