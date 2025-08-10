from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db

teams_routes = Blueprint('teams_routes', __name__)

@teams_routes.route('/teams/<team_id>/players', methods=['GET'])
def get_team_players(team_id):
    current_app.logger.info(f'GET /teams/{team_id}/players handler')
    cursor = db.get_db().cursor()

    # get current players where left_date is NULL, meaning they haven't left)
    query = '''
        SELECT DISTINCT p.player_id, p.first_name, p.last_name, p.position, 
               tp.jersey_num, tp.joined_date, p.age, p.college, p.height, p.weight
        FROM Players p 
        JOIN TeamsPlayers tp ON p.player_id = tp.player_id 
        WHERE tp.team_id = %s 
        AND tp.left_date IS NULL
        ORDER BY tp.jersey_num, p.last_name
    '''
    
    cursor.execute(query, (team_id,))
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

@teams_routes.route('/teams/<team_id>/players', methods=['POST'])
def add_team_player(team_id):
    current_app.logger.info(f'POST /teams/{team_id}/players handler')
    cursor = db.get_db().cursor()
    
    new_player = request.get_json()
    player_id = new_player.get('player_id')
    jersey_num = new_player.get('jersey_num')
    joined_date = new_player.get('joined_date')

    query = '''
        INSERT INTO TeamsPlayers (team_id, player_id, jersey_num, joined_date)
        VALUES (%s, %s, %s, %s)
    '''
    
    cursor.execute(query, (team_id, player_id, jersey_num, joined_date))
    db.get_db().commit()

    the_response = make_response(jsonify(new_player), 201)
    return the_response

@teams_routes.route('/teams/<team_id>/players/<int:player_id>', methods=['PUT'])
def update_team_player(team_id, player_id):
    current_app.logger.info(f'PUT /teams/{team_id}/players/{player_id} handler')
    cursor = db.get_db().cursor()
    
    updated_player = request.get_json()
    jersey_num = updated_player.get('jersey_num')
    left_date = updated_player.get('left_date')

    query = '''
        UPDATE TeamsPlayers 
        SET jersey_num = %s, left_date = %s 
        WHERE team_id = %s AND player_id = %s
    '''
    
    cursor.execute(query, (jersey_num, left_date, team_id, player_id))
    db.get_db().commit()

    the_response = make_response(jsonify(updated_player), 200)
    return the_response