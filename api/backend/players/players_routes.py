########################################################
# Players Blueprint
# Returns player information, comparisons, and statistics
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
players = Blueprint('players', __name__)


#------------------------------------------------------------
# Get player comparison data
# This route allows users to specify multiple player IDs
# and returns their comparison data side-by-side.
@players.route('/player-comparisons', methods=['GET'])
def get_player_comparison():
    """
    Get side-by-side comparison data for multiple players.
    Query parameters:
    - player_ids: comma-separated list of player IDs (required)
    - season: optional season filter (default: all seasons)
    """
    current_app.logger.info('GET /player-comparisons route')
    
    # Get player IDs from query parameters
    player_ids_param = request.args.get('player_ids', '')
    season = request.args.get('season', None)
    
    if not player_ids_param:
        return make_response(jsonify({"error": "No player IDs provided. Use ?player_ids=1,2,3"}), 400)
    
    # Parse comma-separated player IDs
    try:
        player_ids = [int(pid.strip()) for pid in player_ids_param.split(',')]
    except ValueError:
        return make_response(jsonify({"error": "Invalid player ID format. Use comma-separated integers."}), 400)
    
    if len(player_ids) < 2:
        return make_response(jsonify({"error": "At least 2 player IDs required for comparison"}), 400)
    
    cursor = db.get_db().cursor()
    
    # Build the query with placeholders for player IDs
    placeholders = ','.join(['%s'] * len(player_ids))
    
    base_query = f'''
        SELECT 
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            p.age,
            p.years_exp,
            p.college,
            p.current_salary,
            p.expected_salary,
            t.name AS current_team,
            COUNT(pgs.game_id) AS games_played,
            ROUND(AVG(pgs.points), 1) AS avg_points,
            ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
            ROUND(AVG(pgs.assists), 1) AS avg_assists,
            ROUND(AVG(pgs.steals), 1) AS avg_steals,
            ROUND(AVG(pgs.blocks), 1) AS avg_blocks,
            ROUND(AVG(pgs.shooting_percentage), 3) AS avg_shooting_pct,
            ROUND(AVG(pgs.plus_minus), 1) AS avg_plus_minus,
            ROUND(AVG(pgs.minutes_played), 1) AS avg_minutes,
            SUM(pgs.points) AS total_points,
            MAX(pgs.points) AS season_high_points
        FROM Players p
        LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
        LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
        LEFT JOIN Teams t ON tp.team_id = t.team_id
        LEFT JOIN Game g ON pgs.game_id = g.game_id
        WHERE p.player_id IN ({placeholders})
    '''
    
    # Add season filter if provided
    if season:
        base_query += ' AND g.season = %s'
        query_params = player_ids + [season]
    else:
        query_params = player_ids
    
    base_query += '''
        GROUP BY p.player_id, p.first_name, p.last_name, p.position, p.age, 
                 p.years_exp, p.college, p.current_salary, p.expected_salary, t.name
        ORDER BY p.player_id
    '''
    
    cursor.execute(base_query, query_params)
    theData = cursor.fetchall()
    
    # Check if all requested players were found
    found_player_ids = [row['player_id'] for row in theData]
    missing_players = [pid for pid in player_ids if pid not in found_player_ids]
    
    response_data = {
        'players': theData,
        'comparison_count': len(theData),
        'season_filter': season if season else 'All seasons'
    }
    
    # Add warning for missing players
    if missing_players:
        response_data['warnings'] = [f"Player(s) not found: {missing_players}"]
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response