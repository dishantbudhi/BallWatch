########################################################
# Teams Blueprint
# Returns team information, rosters, and management
########################################################
from flask import Blueprint, request, jsonify, make_response, current_app, redirect, url_for
import json
from backend.db_connection import db

teams_routes = Blueprint('teams_routes', __name__)


#------------------------------------------------------------
# Get all teams [Johnny-1.2]
@teams_routes.route('/teams', methods=['GET'])
def get_teams():
    """
    Get all teams with optional filters.
    Query parameters:
    - conference: filter by conference (e.g., 'Eastern', 'Western')
    - division: filter by division
    - city: filter by city
    """
    try:
        current_app.logger.info('GET /teams handler')
        
        # Get filter parameters
        conference = request.args.get('conference')
        division = request.args.get('division')
        city = request.args.get('city')
        
        cursor = db.get_db().cursor()
        
        # Build the query with optional filters
        query = '''
            SELECT 
                t.team_id,
                t.name,
                t.city,
                t.state,
                t.arena,
                t.conference,
                t.division,
                t.coach,
                t.gm,
                t.owner,
                t.championships,
                t.founded_year,
                COUNT(DISTINCT tp.player_id) AS roster_size,
                ROUND(AVG(p.age), 1) AS avg_player_age,
                SUM(p.current_salary) AS total_salary
            FROM Teams t
            LEFT JOIN TeamsPlayers tp ON t.team_id = tp.team_id AND tp.left_date IS NULL
            LEFT JOIN Players p ON tp.player_id = p.player_id
            WHERE 1=1
        '''
        
        params = []
        
        if conference:
            query += ' AND t.conference = %s'
            params.append(conference)
        
        if division:
            query += ' AND t.division = %s'
            params.append(division)
        
        if city:
            query += ' AND t.city = %s'
            params.append(city)
        
        query += '''
            GROUP BY t.team_id, t.name, t.city, t.state, t.arena, 
                     t.conference, t.division, t.coach, t.gm, t.owner, 
                     t.championships, t.founded_year
            ORDER BY t.conference, t.division, t.name
        '''
        
        cursor.execute(query, params)
        theData = cursor.fetchall()
        
        the_response = make_response(jsonify(theData))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching teams: {e}')
        return make_response(jsonify({"error": "Failed to fetch teams"}), 500)


#------------------------------------------------------------
# Update team info (coach, systems) [Mike-2.1]
@teams_routes.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    """
    Update team information.
    Expected JSON body (all fields optional):
    {
        "name": "string",
        "city": "string",
        "state": "string",
        "arena": "string",
        "conference": "string",
        "division": "string",
        "coach": "string",
        "gm": "string",
        "owner": "string",
        "offensive_system": "string",
        "defensive_system": "string"
    }
    """
    try:
        current_app.logger.info(f'PUT /teams/{team_id} handler')
        
        team_data = request.get_json()
        
        if not team_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        # List of allowed fields to update
        allowed_fields = ['name', 'city', 'state', 'arena', 'conference', 
                         'division', 'coach', 'gm', 'owner', 
                         'offensive_system', 'defensive_system']
        
        for field in allowed_fields:
            if field in team_data:
                update_fields.append(f'{field} = %s')
                values.append(team_data[field])
        
        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
        query = f"UPDATE Teams SET {', '.join(update_fields)} WHERE team_id = %s"
        values.append(team_id)
        
        cursor.execute(query, values)
        
        # Check if team was found and updated
        if cursor.rowcount == 0:
            return make_response(jsonify({"error": "Team not found"}), 404)
        
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Team updated successfully",
            "team_id": team_id,
            "updated_fields": list(team_data.keys())
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating team: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update team"}), 500)


#------------------------------------------------------------
# Get team information by ID
@teams_routes.route('/teams/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    """
    Get detailed information for a specific team.
    """
    try:
        current_app.logger.info(f'GET /teams/{team_id} handler')
        
        cursor = db.get_db().cursor()
        
        # Get team details
        query = '''
            SELECT 
                t.*,
                COUNT(DISTINCT tp.player_id) AS roster_size,
                ROUND(AVG(p.age), 1) AS avg_player_age,
                SUM(p.current_salary) AS total_salary,
                ROUND(AVG(p.current_salary), 0) AS avg_salary
            FROM Teams t
            LEFT JOIN TeamsPlayers tp ON t.team_id = tp.team_id AND tp.left_date IS NULL
            LEFT JOIN Players p ON tp.player_id = p.player_id
            WHERE t.team_id = %s
            GROUP BY t.team_id
        '''
        
        cursor.execute(query, (team_id,))
        team_data = cursor.fetchone()
        
        if not team_data:
            return make_response(jsonify({"error": "Team not found"}), 404)
        
        # Get recent games for the team
        cursor.execute('''
            SELECT 
                g.game_id,
                g.game_date,
                g.home_team_id,
                g.away_team_id,
                ht.name AS home_team,
                at.name AS away_team,
                g.home_score,
                g.away_score,
                CASE 
                    WHEN g.home_team_id = %s AND g.home_score > g.away_score THEN 'W'
                    WHEN g.away_team_id = %s AND g.away_score > g.home_score THEN 'W'
                    ELSE 'L'
                END AS result
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE g.home_team_id = %s OR g.away_team_id = %s
            ORDER BY g.game_date DESC
            LIMIT 10
        ''', (team_id, team_id, team_id, team_id))
        
        recent_games = cursor.fetchall()
        
        response_data = {
            'team': team_data,
            'recent_games': recent_games
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching team: {e}')
        return make_response(jsonify({"error": "Failed to fetch team"}), 500)


#------------------------------------------------------------
# Get current team roster [Marcus-3.3, Andre-4.2]
@teams_routes.route('/teams/<int:team_id>/players', methods=['GET'])
def get_team_players(team_id):
    """
    Get current team roster with detailed player information.
    Query parameters:
    - position: filter by position (e.g., 'PG', 'SG', 'SF', 'PF', 'C')
    - include_stats: if 'true', include player statistics
    """
    try:
        current_app.logger.info(f'GET /teams/{team_id}/players handler')
        
        position = request.args.get('position')
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        
        cursor = db.get_db().cursor()

        # Build query based on whether stats are requested
        if include_stats:
            query = '''
                SELECT DISTINCT 
                    p.player_id, 
                    p.first_name, 
                    p.last_name, 
                    p.position, 
                    tp.jersey_num, 
                    tp.joined_date, 
                    p.age, 
                    p.years_exp,
                    p.college, 
                    p.height, 
                    p.weight,
                    p.current_salary,
                    p.expected_salary,
                    COUNT(pgs.game_id) AS games_played,
                    ROUND(AVG(pgs.points), 1) AS avg_points,
                    ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                    ROUND(AVG(pgs.assists), 1) AS avg_assists,
                    ROUND(AVG(pgs.minutes_played), 1) AS avg_minutes
                FROM Players p 
                JOIN TeamsPlayers tp ON p.player_id = tp.player_id
                LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
                WHERE tp.team_id = %s 
                AND tp.left_date IS NULL
            '''
        else:
            query = '''
                SELECT DISTINCT 
                    p.player_id, 
                    p.first_name, 
                    p.last_name, 
                    p.position, 
                    tp.jersey_num, 
                    tp.joined_date, 
                    p.age,
                    p.years_exp, 
                    p.college, 
                    p.height, 
                    p.weight,
                    p.current_salary,
                    p.expected_salary
                FROM Players p 
                JOIN TeamsPlayers tp ON p.player_id = tp.player_id 
                WHERE tp.team_id = %s 
                AND tp.left_date IS NULL
            '''
        
        params = [team_id]
        
        if position:
            query += ' AND p.position = %s'
            params.append(position)
        
        if include_stats:
            query += '''
                GROUP BY p.player_id, p.first_name, p.last_name, p.position,
                         tp.jersey_num, tp.joined_date, p.age, p.years_exp,
                         p.college, p.height, p.weight, p.current_salary, p.expected_salary
            '''
        
        query += ' ORDER BY tp.jersey_num, p.last_name'
        
        cursor.execute(query, params)
        theData = cursor.fetchall()
        
        # Get team name for context
        cursor.execute('SELECT name FROM Teams WHERE team_id = %s', (team_id,))
        team_info = cursor.fetchone()
        
        response_data = {
            'team_id': team_id,
            'team_name': team_info['name'] if team_info else None,
            'roster_size': len(theData),
            'players': theData
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching team players: {e}')
        return make_response(jsonify({"error": "Failed to fetch team players"}), 500)


#------------------------------------------------------------
# Add player to roster [Mike-2.2]
@teams_routes.route('/teams/<int:team_id>/players', methods=['POST'])
def add_team_player(team_id):
    """
    Add a player to team roster.
    Expected JSON body:
    {
        "player_id": int (required),
        "jersey_num": int (required),
        "joined_date": "YYYY-MM-DD" (required)
    }
    """
    try:
        current_app.logger.info(f'POST /teams/{team_id}/players handler')
        cursor = db.get_db().cursor()
        
        new_player = request.get_json()
        player_id = new_player.get('player_id')
        jersey_num = new_player.get('jersey_num')
        joined_date = new_player.get('joined_date')
        
        if not player_id or jersey_num is None or not joined_date:
            return make_response(jsonify({"error": "Missing required fields: player_id, jersey_num, joined_date"}), 400)

        # Check if player exists
        cursor.execute('SELECT player_id FROM Players WHERE player_id = %s', (player_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found"}), 404)
        
        # Check if jersey number is already taken on this team
        cursor.execute('''
            SELECT player_id FROM TeamsPlayers 
            WHERE team_id = %s AND jersey_num = %s AND left_date IS NULL
        ''', (team_id, jersey_num))
        if cursor.fetchone():
            return make_response(jsonify({"error": f"Jersey number {jersey_num} is already taken"}), 409)
        
        # End any existing team association for this player
        cursor.execute('''
            UPDATE TeamsPlayers 
            SET left_date = %s 
            WHERE player_id = %s AND left_date IS NULL
        ''', (joined_date, player_id))

        # Add player to the new team
        query = '''
            INSERT INTO TeamsPlayers (team_id, player_id, jersey_num, joined_date)
            VALUES (%s, %s, %s, %s)
        '''
        
        cursor.execute(query, (team_id, player_id, jersey_num, joined_date))
        db.get_db().commit()

        return make_response(jsonify({
            "message": "Player added to roster successfully",
            "team_id": team_id,
            "player_id": player_id,
            "jersey_num": jersey_num
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error adding team player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add team player"}), 500)


#------------------------------------------------------------
# Update player's status on team [Mike-2.1, Johnny-1.6]
@teams_routes.route('/teams/<int:team_id>/players/<int:player_id>', methods=['PUT'])
def update_team_player(team_id, player_id):
    """
    Update player's status on team (jersey number, left date, etc.).
    Expected JSON body (all fields optional):
    {
        "jersey_num": int,
        "left_date": "YYYY-MM-DD",
        "status": "active|injured|suspended"
    }
    """
    try:
        current_app.logger.info(f'PUT /teams/{team_id}/players/{player_id} handler')
        cursor = db.get_db().cursor()
        
        updated_player = request.get_json()
        
        if not updated_player:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        # Check if the player-team association exists
        cursor.execute('''
            SELECT * FROM TeamsPlayers 
            WHERE team_id = %s AND player_id = %s AND left_date IS NULL
        ''', (team_id, player_id))
        
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found on this team"}), 404)
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'jersey_num' in updated_player:
            jersey_num = updated_player['jersey_num']
            # Check if new jersey number is available
            cursor.execute('''
                SELECT player_id FROM TeamsPlayers 
                WHERE team_id = %s AND jersey_num = %s AND player_id != %s AND left_date IS NULL
            ''', (team_id, jersey_num, player_id))
            if cursor.fetchone():
                return make_response(jsonify({"error": f"Jersey number {jersey_num} is already taken"}), 409)
            update_fields.append('jersey_num = %s')
            values.append(jersey_num)
        
        if 'left_date' in updated_player:
            update_fields.append('left_date = %s')
            values.append(updated_player['left_date'])
        
        if 'status' in updated_player:
            # This would update a status field if it exists in your TeamsPlayers table
            # If not, you might need to add this column or handle it differently
            update_fields.append('status = %s')
            values.append(updated_player['status'])
        
        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)

        query = f'''
            UPDATE TeamsPlayers 
            SET {', '.join(update_fields)}
            WHERE team_id = %s AND player_id = %s AND left_date IS NULL
        '''
        
        values.extend([team_id, player_id])
        cursor.execute(query, values)
        
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Player status updated successfully",
            "team_id": team_id,
            "player_id": player_id,
            "updated_fields": list(updated_player.keys())
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating team player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update team player"}), 500)


#------------------------------------------------------------
# Remove player from team roster
@teams_routes.route('/teams/<int:team_id>/players/<int:player_id>', methods=['DELETE'])
def remove_team_player(team_id, player_id):
    """
    Remove a player from team roster (sets left_date to current date).
    """
    try:
        current_app.logger.info(f'DELETE /teams/{team_id}/players/{player_id} handler')
        cursor = db.get_db().cursor()
        
        # Set left_date to current date to mark player as no longer on team
        query = '''
            UPDATE TeamsPlayers 
            SET left_date = CURDATE()
            WHERE team_id = %s AND player_id = %s AND left_date IS NULL
        '''
        
        cursor.execute(query, (team_id, player_id))
        
        if cursor.rowcount == 0:
            return make_response(jsonify({"error": "Player not found on this team"}), 404)
        
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Player removed from roster successfully",
            "team_id": team_id,
            "player_id": player_id
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error removing team player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to remove team player"}), 500)