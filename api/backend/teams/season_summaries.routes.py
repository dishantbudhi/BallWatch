########################################################
# Season Summaries Blueprint
# Returns league-wide statistics and player leaders
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
season_summaries = Blueprint('season_summaries', __name__)

#------------------------------------------------------------
# Get league leaders for various statistical categories
# This route allows users to specify a category to get leaders
@season_summaries.route('/season-summaries', methods=['GET'])
def get_season_leaders():
    """
    Returns league leaders based on the 'category' parameter
    Categories: points, rebounds, assists, blocks, steals, shooting_pct
    """
    current_app.logger.info('GET /season-summaries route')
    
    # Get the category from query parameters (default to points)
    category = request.args.get('category', 'points')
    limit = request.args.get('limit', 10, type=int)  # Top 10 by default
    
    cursor = db.get_db().cursor()
    
    # Different SQL based on category requested
    if category == 'points':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.points), 1) AS avg_points,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_points DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'rebounds':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_rebounds DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'assists':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.assists), 1) AS avg_assists,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_assists DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'blocks':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.blocks), 1) AS avg_blocks,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_blocks DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'steals':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.steals), 1) AS avg_steals,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_steals DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'shooting_pct':
        cursor.execute('''
            SELECT 
                p.player_id,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                p.position,
                ROUND(AVG(pgs.shooting_percentage), 3) AS avg_shooting_pct,
                COUNT(pgs.game_id) AS games_played
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
                AND pgs.shooting_percentage IS NOT NULL
            GROUP BY p.player_id, p.first_name, p.last_name, t.name, p.position
            HAVING games_played >= 5
            ORDER BY avg_shooting_pct DESC
            LIMIT %s
        ''', (limit,))
        
    elif category == 'all':
        # Return top 5 leaders in each major category
        cursor.execute('''
            (SELECT 
                'Points' AS category,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                ROUND(AVG(pgs.points), 1) AS stat_value
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name
            HAVING COUNT(pgs.game_id) >= 5
            ORDER BY stat_value DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'Rebounds' AS category,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                ROUND(AVG(pgs.rebounds), 1) AS stat_value
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name
            HAVING COUNT(pgs.game_id) >= 5
            ORDER BY stat_value DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'Assists' AS category,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                ROUND(AVG(pgs.assists), 1) AS stat_value
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name
            HAVING COUNT(pgs.game_id) >= 5
            ORDER BY stat_value DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'Blocks' AS category,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                ROUND(AVG(pgs.blocks), 1) AS stat_value
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name
            HAVING COUNT(pgs.game_id) >= 5
            ORDER BY stat_value DESC
            LIMIT 5)
            
            UNION ALL
            
            (SELECT 
                'Steals' AS category,
                p.first_name,
                p.last_name,
                t.name AS team_name,
                ROUND(AVG(pgs.steals), 1) AS stat_value
            FROM Players p
            JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            JOIN Teams t ON t.team_id = pgs.team_id
            WHERE p.player_status = 'Active'
            GROUP BY p.player_id, p.first_name, p.last_name, t.name
            HAVING COUNT(pgs.game_id) >= 5
            ORDER BY stat_value DESC
            LIMIT 5)
        ''')
        
    else:
        # Invalid category
        return make_response(jsonify({'error': 'Invalid category. Use: points, rebounds, assists, blocks, steals, shooting_pct, or all'}), 400)
    
    theData = cursor.fetchall()
    
    # Return the data as JSON
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#------------------------------------------------------------
# Get a specific player's season summary
# Useful for detailed player cards
@season_summaries.route('/season-summaries/player/<int:player_id>', methods=['GET'])
def get_player_season_summary(player_id):
    """
    Get comprehensive season stats for a specific player
    Shows all their averages and totals for the current season
    """
    current_app.logger.info(f'GET /season-summaries/player/{player_id} route')
    
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT 
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            p.age,
            t.name AS team_name,
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
        JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
        JOIN Teams t ON t.team_id = pgs.team_id
        WHERE p.player_id = %s
        GROUP BY p.player_id, p.first_name, p.last_name, p.position, p.age, t.name
    ''', (player_id,))
    
    theData = cursor.fetchall()
    
    if not theData:
        return make_response(jsonify({'error': 'Player not found or no stats available'}), 404)
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response