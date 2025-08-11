from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db

games_routes = Blueprint('games', __name__)


@games_routes.route('/games', methods=['GET'])
def get_games():
    try:
        current_app.logger.info('GET /games handler')
        cursor = db.get_db().cursor()

        cursor.execute('SELECT * FROM Game')
        theData = cursor.fetchall()
        
        the_response = make_response(jsonify(theData))
        the_response.status_code = 200
        return the_response
    except Exception as e:
        current_app.logger.error(f'Error fetching games: {e}')
        return make_response(jsonify({"error": "Failed to fetch games"}), 500)

@games_routes.route('/games', methods=['POST'])
def create_game():
    try:
        current_app.logger.info('POST /games handler')
        cursor = db.get_db().cursor()

        new_game = request.get_json()
        date = new_game.get('date')
        season = new_game.get('season')
        is_playoff = new_game.get('is_playoff')
        home_team_id = new_game.get('home_team_id')
        away_team_id = new_game.get('away_team_id')
        home_score = new_game.get('home_score', 0)
        away_score = new_game.get('away_score', 0)

        if not date or not season or not home_team_id or not away_team_id:
            return make_response(jsonify({"error": "Missing required fields"}), 400)
        
        query = '''
            INSERT INTO Game (date, season, is_playoff, home_team_id, away_team_id, home_score, away_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        current_app.logger.info(f'Executing query: {query}')

        cursor.execute(query, (date, season, is_playoff, home_team_id, away_team_id, home_score, away_score))
        db.get_db().commit()

        the_response = make_response(jsonify(new_game), 201)
        return the_response
    except Exception as e:
        current_app.logger.error(f'Error creating game: {e}')
        return make_response(jsonify({"error": "Failed to create game"}), 500)

@games_routes.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    try:
        cursor = db.get_db().cursor()
        current_app.logger.info(f'PUT /games/{game_id} handler')

        updated_game = request.get_json()
        date = updated_game.get('date')
        season = updated_game.get('season')
        is_playoff = updated_game.get('is_playoff')
        home_team_id = updated_game.get('home_team_id')
        away_team_id = updated_game.get('away_team_id')
        home_score = updated_game.get('home_score')
        away_score = updated_game.get('away_score')
        if not date or not season or not home_team_id or not away_team_id:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        query = '''
            UPDATE Game
            SET date = %s, season = %s, is_playoff = %s, home_team_id = %s, away_team_id = %s, home_score = %s, away_score = %s
            WHERE game_id = %s
        '''
        current_app.logger.info(f'Executing query: {query}')

        cursor.execute(query, (date, season, is_playoff, home_team_id, away_team_id, home_score, away_score, game_id))
        db.get_db().commit()

        the_response = make_response(jsonify(updated_game), 200)
        return the_response
    except Exception as e:
        current_app.logger.error(f'Error updating game: {e}')
        return make_response(jsonify({"error": "Failed to update game"}), 500)