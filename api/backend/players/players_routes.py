from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db

players = Blueprint('players', __name__)


@players.route('/player-matchups', methods=['GET'])
def get_player_matchups():
    current_app.logger.info('GET /player-matchups handler')
    cursor = db.get_db().cursor()

    cursor.execute('SELECT * FROM PlayerMatchup')
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response