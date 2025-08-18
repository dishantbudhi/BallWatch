"""Head Coach blueprint - exposes opponent reports, lineup configurations, and game plans.
User Stories: Marcus (3.1, 3.4, 3.5)
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

coach = Blueprint('coach', __name__)


@coach.route('/opponent-reports', methods=['GET'])
def coach_opponent_reports():
    try:
        team_id = request.args.get('team_id', type=int)
        opponent_id = request.args.get('opponent_id', type=int)
        last_n_games = request.args.get('last_n_games', 10, type=int)
        if not team_id or not opponent_id:
            return make_response(jsonify({'error': 'team_id and opponent_id are required'}), 400)
        cursor = db.get_db().cursor()
        cursor.execute('''
            SELECT g.game_id, g.game_date, g.home_team_id, g.away_team_id,
                   g.home_score, g.away_score
            FROM Game g
            WHERE ((g.home_team_id = %s AND g.away_team_id = %s) OR
                   (g.home_team_id = %s AND g.away_team_id = %s))
              AND g.status = 'completed'
            ORDER BY g.game_date DESC LIMIT %s
        ''', (team_id, opponent_id, opponent_id, team_id, last_n_games))
        games = cursor.fetchall()
        return make_response(jsonify({'head_to_head': games, 'total_games': len(games)}), 200)
    except Exception as e:
        current_app.logger.error(f'coach_opponent_reports error: {e}')
        return make_response(jsonify({'error': 'Failed to fetch opponent report'}), 500)


@coach.route('/lineup-configurations', methods=['GET'])
def coach_lineups():
    try:
        team_id = request.args.get('team_id', type=int)
        if not team_id:
            return make_response(jsonify({'error': 'team_id is required'}), 400)
        cursor = db.get_db().cursor()
        cursor.execute('''
            SELECT lc.lineup_id,
                   GROUP_CONCAT(CONCAT(p.first_name, ' ', p.last_name) ORDER BY pl.position_in_lineup SEPARATOR ', ') AS lineup,
                   lc.plus_minus, lc.offensive_rating, lc.defensive_rating
            FROM LineupConfiguration lc
            JOIN PlayerLineups pl ON lc.lineup_id = pl.lineup_id
            JOIN Players p ON pl.player_id = p.player_id
            WHERE lc.team_id = %s
            GROUP BY lc.lineup_id, lc.plus_minus, lc.offensive_rating, lc.defensive_rating
            ORDER BY lc.plus_minus DESC
            LIMIT 10
        ''', (team_id,))
        rows = cursor.fetchall()
        return make_response(jsonify({'lineups': rows, 'total': len(rows)}), 200)
    except Exception as e:
        current_app.logger.error(f'coach_lineups error: {e}')
        return make_response(jsonify({'error': 'Failed to fetch lineups'}), 500)


@coach.route('/game-plans', methods=['POST'])
def coach_create_game_plan():
    try:
        data = request.get_json() or {}
        required = ['team_id', 'plan_name']
        for f in required:
            if f not in data:
                return make_response(jsonify({'error': f'Missing required field: {f}'}), 400)
        cursor = db.get_db().cursor()
        cursor.execute('''
            INSERT INTO GamePlans (team_id, opponent_id, game_id, plan_name, offensive_strategy,
                                   defensive_strategy, key_matchups, special_instructions, status,
                                   created_date, updated_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s,'draft'), NOW(), NOW())
        ''', (
            data['team_id'], data.get('opponent_id'), data.get('game_id'), data['plan_name'],
            data.get('offensive_strategy'), data.get('defensive_strategy'), data.get('key_matchups'),
            data.get('special_instructions'), data.get('status')
        ))
        db.get_db().commit()
        return make_response(jsonify({'message': 'Game plan created', 'plan_id': cursor.lastrowid}), 201)
    except Exception as e:
        current_app.logger.error(f'coach_create_game_plan error: {e}')
        db.get_db().rollback()
        return make_response(jsonify({'error': 'Failed to create game plan'}), 500)


