########################################################
# Players Blueprint
# Returns player information, comparisons, and statistics
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from flask import redirect
from flask import url_for
import json
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
players = Blueprint('players', __name__)


#------------------------------------------------------------
# Get all players or filter by position, age, etc.
# [Johnny-1.2, Johnny-1.3, Andre-4.1, Andre-4.4]
@players.route('/players', methods=['GET'])
def get_players():
    """
    Get all players with optional filters.
    Query parameters:
    - position: filter by position (e.g., 'PG', 'SG', 'SF', 'PF', 'C')
    - min_age: minimum age filter
    - max_age: maximum age filter
    - team_id: filter by team ID
    - min_salary: minimum salary filter
    - max_salary: maximum salary filter
    """
    current_app.logger.info('GET /players route')
    
    # Get filter parameters
    position = request.args.get('position')
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    team_id = request.args.get('team_id', type=int)
    min_salary = request.args.get('min_salary', type=float)
    max_salary = request.args.get('max_salary', type=float)
    
    cursor = db.get_db().cursor()
    
    # Build the query with optional filters
    query = '''
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
            p.height,
            p.weight,
            t.name AS current_team,
            t.team_id
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
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Add new player profile [Mike-2.2]
@players.route('/players', methods=['POST'])
def add_player():
    """
    Add a new player profile.
    Expected JSON body:
    {
        "first_name": "string",
        "last_name": "string",
        "position": "string",
        "age": int,
        "years_exp": int,
        "college": "string",
        "current_salary": float,
        "expected_salary": float,
        "height": "string",
        "weight": int
    }
    """
    current_app.logger.info('POST /players route')
    
    try:
        player_data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'position', 'age']
        for field in required_fields:
            if field not in player_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        cursor = db.get_db().cursor()
        
        query = '''
            INSERT INTO Players (
                first_name, last_name, position, age, years_exp, 
                college, current_salary, expected_salary, height, weight
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        values = (
            player_data['first_name'],
            player_data['last_name'],
            player_data['position'],
            player_data['age'],
            player_data.get('years_exp', 0),
            player_data.get('college'),
            player_data.get('current_salary', 0),
            player_data.get('expected_salary', 0),
            player_data.get('height'),
            player_data.get('weight')
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        # Get the newly created player ID
        new_player_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Player added successfully",
            "player_id": new_player_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error adding player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add player"}), 500)


#------------------------------------------------------------
# Update player info (status, team, salary) [Mike-2.1]
@players.route('/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    """
    Update player information.
    Expected JSON body (all fields optional):
    {
        "position": "string",
        "age": int,
        "years_exp": int,
        "current_salary": float,
        "expected_salary": float,
        "team_id": int,
        "height": "string",
        "weight": int
    }
    """
    current_app.logger.info(f'PUT /players/{player_id} route')
    
    try:
        player_data = request.get_json()
        
        if not player_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        # Update Players table fields
        player_fields = ['position', 'age', 'years_exp', 'current_salary', 
                        'expected_salary', 'height', 'weight']
        
        for field in player_fields:
            if field in player_data:
                update_fields.append(f'{field} = %s')
                values.append(player_data[field])
        
        if update_fields:
            query = f"UPDATE Players SET {', '.join(update_fields)} WHERE player_id = %s"
            values.append(player_id)
            cursor.execute(query, values)
        
        # Handle team update separately
        if 'team_id' in player_data:
            new_team_id = player_data['team_id']
            
            # End current team association
            cursor.execute('''
                UPDATE TeamsPlayers 
                SET left_date = CURDATE() 
                WHERE player_id = %s AND left_date IS NULL
            ''', (player_id,))
            
            # Create new team association
            cursor.execute('''
                INSERT INTO TeamsPlayers (team_id, player_id, joined_date)
                VALUES (%s, %s, CURDATE())
            ''', (new_team_id, player_id))
        
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Player updated successfully",
            "player_id": player_id
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update player"}), 500)


#------------------------------------------------------------
# Get player's performance stats 
# [Johnny-1.1, Johnny-1.3, Johnny-1.4, Andre-4.3]
@players.route('/players/<int:player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    """
    Get player's performance statistics.
    Query parameters:
    - season: optional season filter
    - game_type: optional game type filter ('regular', 'playoff')
    """
    current_app.logger.info(f'GET /players/{player_id}/stats route')
    
    season = request.args.get('season')
    game_type = request.args.get('game_type')
    
    cursor = db.get_db().cursor()
    
    # Build the query
    query = '''
        SELECT 
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            COUNT(pgs.game_id) AS games_played,
            ROUND(AVG(pgs.points), 1) AS avg_points,
            ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
            ROUND(AVG(pgs.assists), 1) AS avg_assists,
            ROUND(AVG(pgs.steals), 1) AS avg_steals,
            ROUND(AVG(pgs.blocks), 1) AS avg_blocks,
            ROUND(AVG(pgs.turnovers), 1) AS avg_turnovers,
            ROUND(AVG(pgs.shooting_percentage), 3) AS avg_shooting_pct,
            ROUND(AVG(pgs.three_point_percentage), 3) AS avg_three_point_pct,
            ROUND(AVG(pgs.free_throw_percentage), 3) AS avg_free_throw_pct,
            ROUND(AVG(pgs.plus_minus), 1) AS avg_plus_minus,
            ROUND(AVG(pgs.minutes_played), 1) AS avg_minutes,
            SUM(pgs.points) AS total_points,
            SUM(pgs.rebounds) AS total_rebounds,
            SUM(pgs.assists) AS total_assists,
            MAX(pgs.points) AS season_high_points,
            MIN(pgs.points) AS season_low_points
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
    theData = cursor.fetchone()
    
    if not theData:
        return make_response(jsonify({"error": "Player not found"}), 404)
    
    # Get recent games
    cursor.execute('''
        SELECT 
            g.game_id,
            g.game_date,
            g.home_team_id,
            g.away_team_id,
            ht.name AS home_team,
            at.name AS away_team,
            pgs.points,
            pgs.rebounds,
            pgs.assists,
            pgs.minutes_played
        FROM PlayerGameStats pgs
        JOIN Game g ON pgs.game_id = g.game_id
        JOIN Teams ht ON g.home_team_id = ht.team_id
        JOIN Teams at ON g.away_team_id = at.team_id
        WHERE pgs.player_id = %s
        ORDER BY g.game_date DESC
        LIMIT 10
    ''', (player_id,))
    
    recent_games = cursor.fetchall()
    
    response_data = {
        'stats': theData,
        'recent_games': recent_games
    }
    
    the_response = make_response(jsonify(response_data))
    the_response.status_code = 200
    return the_response


#------------------------------------------------------------
# Update player stats [Mike-2.1]
@players.route('/players/<int:player_id>/stats', methods=['PUT'])
def update_player_stats(player_id):
    """
    Update or add player statistics for a specific game.
    Expected JSON body:
    {
        "game_id": int,
        "points": int,
        "rebounds": int,
        "assists": int,
        "steals": int,
        "blocks": int,
        "turnovers": int,
        "shooting_percentage": float,
        "three_point_percentage": float,
        "free_throw_percentage": float,
        "plus_minus": int,
        "minutes_played": int
    }
    """
    current_app.logger.info(f'PUT /players/{player_id}/stats route')
    
    try:
        stats_data = request.get_json()
        
        # Validate required fields
        if 'game_id' not in stats_data:
            return make_response(jsonify({"error": "game_id is required"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if stats already exist for this player and game
        cursor.execute('''
            SELECT * FROM PlayerGameStats 
            WHERE player_id = %s AND game_id = %s
        ''', (player_id, stats_data['game_id']))
        
        existing_stats = cursor.fetchone()
        
        if existing_stats:
            # Update existing stats
            update_fields = []
            values = []
            
            stat_fields = ['points', 'rebounds', 'assists', 'steals', 'blocks',
                          'turnovers', 'shooting_percentage', 'three_point_percentage',
                          'free_throw_percentage', 'plus_minus', 'minutes_played']
            
            for field in stat_fields:
                if field in stats_data:
                    update_fields.append(f'{field} = %s')
                    values.append(stats_data[field])
            
            if update_fields:
                query = f'''
                    UPDATE PlayerGameStats 
                    SET {', '.join(update_fields)}
                    WHERE player_id = %s AND game_id = %s
                '''
                values.extend([player_id, stats_data['game_id']])
                cursor.execute(query, values)
        else:
            # Insert new stats
            query = '''
                INSERT INTO PlayerGameStats (
                    player_id, game_id, points, rebounds, assists, steals, blocks,
                    turnovers, shooting_percentage, three_point_percentage,
                    free_throw_percentage, plus_minus, minutes_played
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            values = (
                player_id,
                stats_data['game_id'],
                stats_data.get('points', 0),
                stats_data.get('rebounds', 0),
                stats_data.get('assists', 0),
                stats_data.get('steals', 0),
                stats_data.get('blocks', 0),
                stats_data.get('turnovers', 0),
                stats_data.get('shooting_percentage', 0),
                stats_data.get('three_point_percentage', 0),
                stats_data.get('free_throw_percentage', 0),
                stats_data.get('plus_minus', 0),
                stats_data.get('minutes_played', 0)
            )
            
            cursor.execute(query, values)
        
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Player stats updated successfully",
            "player_id": player_id,
            "game_id": stats_data['game_id']
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating player stats: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update player stats"}), 500)


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


#------------------------------------------------------------
# Get player matchups data
# This route returns all player matchup information
@players.route('/player-matchups', methods=['GET'])
def get_player_matchups():
    """
    Get all player matchup data from the PlayerMatchup table.
    Returns a list of all player matchups.
    """
    try:
        current_app.logger.info('GET /player-matchups handler')
        cursor = db.get_db().cursor()
        cursor.execute('SELECT * FROM PlayerMatchup')
        theData = cursor.fetchall()
        
        the_response = make_response(jsonify(theData))
        the_response.status_code = 200
        return the_response
    except Exception as e:
        current_app.logger.error(f'Error fetching player matchups: {e}')
        return make_response(jsonify({"error": "Failed to fetch player matchups"}), 500)
