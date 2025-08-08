
from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db
from backend.simple.playlist import sample_playlist_data

game_plan_routes = Blueprint('game_plan_routes', __name__)

# ------------------------------------------------------------
# /gameplans returns all rows from the GamePlan table
@game_plan_routes.route('/gameplans', methods=['GET'])
def get_all_gameplans():
    current_app.logger.info('GET /gameplans handler')
    
    try:
        cursor = current_app.mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM GamePlan;")
        gameplans = cursor.fetchall()
        cursor.close()

        response = make_response(jsonify(gameplans))
        response.status_code = 200
        return response

    except Exception as e:
        current_app.logger.error(f"Error fetching gameplans: {e}")
        return make_response({"error": "Internal Server Error - Frank"}, 500)
