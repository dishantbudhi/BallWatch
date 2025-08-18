"""Superfan blueprint - proxies key endpoints under /superfan/*.
User Stories: Johnny (1.1, 1.2, 1.4)
"""

from flask import Blueprint, request, jsonify, make_response
from backend.db_connection import db

superfan = Blueprint('superfan', __name__)


@superfan.route('/players', methods=['GET'])
def sf_get_players():
    try:
        cursor = db.get_db().cursor()
        position = request.args.get('position')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        team_id = request.args.get('team_id', type=int)
        min_salary = request.args.get('min_salary', type=float)
        max_salary = request.args.get('max_salary', type=float)

        query = '''
            SELECT p.player_id, p.first_name, p.last_name, p.position, p.age,
                   p.years_exp, p.college, p.current_salary, p.expected_salary,
                   p.height, p.weight, t.name AS current_team, t.team_id
            FROM Players p
            LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
            LEFT JOIN Teams t ON tp.team_id = t.team_id
            WHERE 1=1
        '''
        params = []
        if position:
            query += ' AND p.position = %s'
            params.append(position)
        if min_age is not None:
            query += ' AND p.age >= %s'
            params.append(min_age)
        if max_age is not None:
            query += ' AND p.age <= %s'
            params.append(max_age)
        if team_id:
            query += ' AND t.team_id = %s'
            params.append(team_id)
        if min_salary is not None:
            query += ' AND p.current_salary >= %s'
            params.append(min_salary)
        if max_salary is not None:
            query += ' AND p.current_salary <= %s'
            params.append(max_salary)

        query += ' ORDER BY p.last_name, p.first_name'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return make_response(jsonify({'players': rows, 'total_count': len(rows)}), 200)
    except Exception:
        return make_response(jsonify({'error': 'Failed to fetch players'}), 500)


@superfan.route('/players/<int:player_id>/stats', methods=['GET'])
def sf_get_player_stats(player_id):
    try:
        season = request.args.get('season')
        game_type = request.args.get('game_type')
        cursor = db.get_db().cursor()
        query = '''
            SELECT p.player_id, p.first_name, p.last_name, p.position,
                   COUNT(pgs.game_id) AS games_played,
                   ROUND(AVG(pgs.points), 1) AS avg_points,
                   ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                   ROUND(AVG(pgs.assists), 1) AS avg_assists,
                   ROUND(AVG(pgs.plus_minus), 1) AS avg_plus_minus
            FROM Players p
            LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            LEFT JOIN Game g ON pgs.game_id = g.game_id
            WHERE p.player_id = %s
        '''
        params = [player_id]
        if season:
            query += ' AND g.season = %s'
            params.append(season)
        if game_type:
            query += ' AND g.game_type = %s'
            params.append(game_type)
        query += ' GROUP BY p.player_id, p.first_name, p.last_name, p.position'
        cursor.execute(query, params)
        stats = cursor.fetchone()
        return make_response(jsonify({'player_stats': stats}), 200)
    except Exception:
        return make_response(jsonify({'error': 'Failed to fetch player stats'}), 500)


@superfan.route('/player-comparisons', methods=['GET'])
def sf_player_comparisons():
    try:
        player_ids_param = request.args.get('player_ids', '')
        season = request.args.get('season')
        player_ids = [int(pid) for pid in player_ids_param.split(',') if pid.strip().isdigit()]
        if len(player_ids) < 2:
            return make_response(jsonify({"error": "Provide at least two player_ids"}), 400)
        cursor = db.get_db().cursor()
        placeholders = ','.join(['%s'] * len(player_ids))
        params = list(player_ids)
        query = f'''
            SELECT p.player_id, p.first_name, p.last_name, p.position,
                   ROUND(AVG(pgs.points), 1) AS avg_points,
                   ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                   ROUND(AVG(pgs.assists), 1) AS avg_assists,
                   COUNT(pgs.game_id) AS games_played
            FROM Players p
            LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            LEFT JOIN Game g ON pgs.game_id = g.game_id
            WHERE p.player_id IN ({placeholders})
        '''
        if season:
            query += ' AND g.season = %s'
            params.append(season)
        query += ' GROUP BY p.player_id, p.first_name, p.last_name, p.position'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return make_response(jsonify({'players': rows, 'total': len(rows)}), 200)
    except Exception:
        return make_response(jsonify({'error': 'Failed to compare players'}), 500)


