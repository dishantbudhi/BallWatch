"""General Manager blueprint - exposes draft rankings and player comparisons.
User Stories: Andre (4.1, 4.2, 4.5)
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

gm = Blueprint('gm', __name__)


@gm.route('/draft-evaluations', methods=['GET'])
def gm_draft_evaluations():
    try:
        position = request.args.get('position')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        cursor = db.get_db().cursor()
        query = '''
            SELECT de.evaluation_id, de.player_id, p.first_name, p.last_name, p.position,
                   p.age, de.overall_rating, de.potential_rating, de.evaluation_type,
                   t.name AS current_team
            FROM DraftEvaluations de
            JOIN Players p ON de.player_id = p.player_id
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
        query += ' ORDER BY de.overall_rating DESC'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return make_response(jsonify({'evaluations': rows, 'total': len(rows)}), 200)
    except Exception as e:
        current_app.logger.error(f'gm_draft_evaluations error: {e}')
        return make_response(jsonify({'error': 'Failed to fetch evaluations'}), 500)


@gm.route('/players', methods=['GET'])
def gm_get_players_age_group():
    """Players with optional age-group filters (e.g., under 25, 25-30, 30+)."""
    try:
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        cursor = db.get_db().cursor()
        query = '''
            SELECT p.player_id, p.first_name, p.last_name, p.position, p.age,
                   t.name AS current_team
            FROM Players p
            LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
            LEFT JOIN Teams t ON tp.team_id = t.team_id
            WHERE 1=1
        '''
        params = []
        if min_age is not None:
            query += ' AND p.age >= %s'
            params.append(min_age)
        if max_age is not None:
            query += ' AND p.age <= %s'
            params.append(max_age)
        query += ' ORDER BY p.age, p.last_name'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return make_response(jsonify({'players': rows, 'total': len(rows)}), 200)
    except Exception as e:
        current_app.logger.error(f'gm_get_players_age_group error: {e}')
        return make_response(jsonify({'error': 'Failed to fetch players'}), 500)


@gm.route('/player-comparisons', methods=['GET'])
def gm_player_comparisons():
    """Delegates to the same logic used in analytics comparisons for GM needs."""
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
    except Exception as e:
        current_app.logger.error(f'gm_player_comparisons error: {e}')
        return make_response(jsonify({'error': 'Failed to compare players'}), 500)


