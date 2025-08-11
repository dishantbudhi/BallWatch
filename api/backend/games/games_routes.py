########################################################
# Games Blueprint
# Game scheduling, scores, and management
########################################################
from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
from datetime import datetime, timedelta

games = Blueprint('games', __name__)


#------------------------------------------------------------
# Get games list/schedule [Johnny-1.5, Marcus-3.6]
@games.route('/games', methods=['GET'])
def get_games():
    """
    Get games list with optional filters.
    Query parameters:
    - team_id: filter by team (home or away)
    - start_date: filter games from this date (YYYY-MM-DD)
    - end_date: filter games until this date (YYYY-MM-DD)
    - season: filter by season
    - game_type: filter by game type ('regular', 'playoff')
    - status: filter by status ('scheduled', 'in_progress', 'completed')
    """
    try:
        current_app.logger.info('GET /games handler')
        
        # Get filter parameters
        team_id = request.args.get('team_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        season = request.args.get('season')
        game_type = request.args.get('game_type')
        status = request.args.get('status')
        
        cursor = db.get_db().cursor()
        
        # Build the query with optional filters
        query = '''
            SELECT 
                g.game_id,
                g.game_date,
                g.game_time,
                g.home_team_id,
                g.away_team_id,
                ht.name AS home_team_name,
                ht.city AS home_team_city,
                at.name AS away_team_name,
                at.city AS away_team_city,
                g.home_score,
                g.away_score,
                g.season,
                g.game_type,
                g.status,
                g.attendance,
                g.venue,
                CASE 
                    WHEN g.status = 'completed' AND g.home_score > g.away_score THEN ht.name
                    WHEN g.status = 'completed' AND g.away_score > g.home_score THEN at.name
                    ELSE NULL
                END AS winner
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE 1=1
        '''
        
        params = []
        
        if team_id:
            query += ' AND (g.home_team_id = %s OR g.away_team_id = %s)'
            params.extend([team_id, team_id])
        
        if start_date:
            query += ' AND g.game_date >= %s'
            params.append(start_date)
        
        if end_date:
            query += ' AND g.game_date <= %s'
            params.append(end_date)
        
        if season:
            query += ' AND g.season = %s'
            params.append(season)
        
        if game_type:
            query += ' AND g.game_type = %s'
            params.append(game_type)
        
        if status:
            query += ' AND g.status = %s'
            params.append(status)
        
        query += ' ORDER BY g.game_date DESC, g.game_time DESC'
        
        cursor.execute(query, params)
        theData = cursor.fetchall()
        
        # Get summary statistics
        completed_games = [g for g in theData if g['status'] == 'completed']
        scheduled_games = [g for g in theData if g['status'] == 'scheduled']
        
        response_data = {
            'games': theData,
            'total_games': len(theData),
            'completed_games': len(completed_games),
            'scheduled_games': len(scheduled_games),
            'filters_applied': {
                'team_id': team_id,
                'start_date': start_date,
                'end_date': end_date,
                'season': season,
                'game_type': game_type,
                'status': status
            }
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching games: {e}')
        return make_response(jsonify({"error": "Failed to fetch games"}), 500)


#------------------------------------------------------------
# Create new game [Mike-2.1]
@games.route('/games', methods=['POST'])
def create_game():
    """
    Create a new game.
    Expected JSON body:
    {
        "game_date": "YYYY-MM-DD" (required),
        "game_time": "HH:MM:SS" (required),
        "home_team_id": int (required),
        "away_team_id": int (required),
        "season": "string" (required),
        "game_type": "regular|playoff" (default: "regular"),
        "venue": "string",
        "status": "scheduled|in_progress|completed" (default: "scheduled")
    }
    """
    try:
        current_app.logger.info('POST /games handler')
        
        game_data = request.get_json()
        
        # Validate required fields
        required_fields = ['game_date', 'game_time', 'home_team_id', 'away_team_id', 'season']
        for field in required_fields:
            if field not in game_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        # Validate teams exist and are different
        if game_data['home_team_id'] == game_data['away_team_id']:
            return make_response(jsonify({"error": "Home and away teams must be different"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if both teams exist
        cursor.execute('SELECT team_id FROM Teams WHERE team_id IN (%s, %s)', 
                      (game_data['home_team_id'], game_data['away_team_id']))
        
        if cursor.rowcount != 2:
            return make_response(jsonify({"error": "One or both teams not found"}), 404)
        
        # Check for duplicate game
        cursor.execute('''
            SELECT game_id FROM Game 
            WHERE game_date = %s 
            AND home_team_id = %s 
            AND away_team_id = %s
        ''', (game_data['game_date'], game_data['home_team_id'], game_data['away_team_id']))
        
        if cursor.fetchone():
            return make_response(jsonify({"error": "Game already exists for these teams on this date"}), 409)
        
        # Insert new game
        query = '''
            INSERT INTO Game (
                game_date, game_time, home_team_id, away_team_id, 
                season, game_type, venue, status, home_score, away_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        values = (
            game_data['game_date'],
            game_data['game_time'],
            game_data['home_team_id'],
            game_data['away_team_id'],
            game_data['season'],
            game_data.get('game_type', 'regular'),
            game_data.get('venue'),
            game_data.get('status', 'scheduled'),
            0,  # Initial home_score
            0   # Initial away_score
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_game_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Game created successfully",
            "game_id": new_game_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error creating game: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to create game"}), 500)


#------------------------------------------------------------
# Update game info/scores [Mike-2.1]
@games.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """
    Update game information and scores.
    Expected JSON body (all fields optional):
    {
        "game_date": "YYYY-MM-DD",
        "game_time": "HH:MM:SS",
        "home_score": int,
        "away_score": int,
        "status": "scheduled|in_progress|completed",
        "attendance": int,
        "venue": "string"
    }
    """
    try:
        current_app.logger.info(f'PUT /games/{game_id} handler')
        
        game_data = request.get_json()
        
        if not game_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if game exists
        cursor.execute('SELECT game_id FROM Game WHERE game_id = %s', (game_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Game not found"}), 404)
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        allowed_fields = ['game_date', 'game_time', 'home_score', 'away_score', 
                         'status', 'attendance', 'venue']
        
        for field in allowed_fields:
            if field in game_data:
                update_fields.append(f'{field} = %s')
                values.append(game_data[field])
        
        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
        # Add validation for scores
        if 'home_score' in game_data and game_data['home_score'] < 0:
            return make_response(jsonify({"error": "Home score cannot be negative"}), 400)
        
        if 'away_score' in game_data and game_data['away_score'] < 0:
            return make_response(jsonify({"error": "Away score cannot be negative"}), 400)
        
        query = f"UPDATE Game SET {', '.join(update_fields)} WHERE game_id = %s"
        values.append(game_id)
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Game updated successfully",
            "game_id": game_id,
            "updated_fields": list(game_data.keys())
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating game: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update game"}), 500)


#------------------------------------------------------------
# Get specific game details
@games.route('/games/<int:game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Get detailed information for a specific game including player stats.
    """
    try:
        current_app.logger.info(f'GET /games/{game_id} handler')
        
        cursor = db.get_db().cursor()
        
        # Get game details
        query = '''
            SELECT 
                g.*,
                ht.name AS home_team_name,
                ht.city AS home_team_city,
                ht.coach AS home_team_coach,
                at.name AS away_team_name,
                at.city AS away_team_city,
                at.coach AS away_team_coach
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE g.game_id = %s
        '''
        
        cursor.execute(query, (game_id,))
        game_data = cursor.fetchone()
        
        if not game_data:
            return make_response(jsonify({"error": "Game not found"}), 404)
        
        # Get player stats for this game
        cursor.execute('''
            SELECT 
                pgs.*,
                p.first_name,
                p.last_name,
                p.position,
                tp.team_id,
                t.name AS team_name
            FROM PlayerGameStats pgs
            JOIN Players p ON pgs.player_id = p.player_id
            JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
            JOIN Teams t ON tp.team_id = t.team_id
            WHERE pgs.game_id = %s
            ORDER BY tp.team_id, pgs.points DESC
        ''', (game_id,))
        
        player_stats = cursor.fetchall()
        
        # Separate stats by team
        home_team_stats = [stat for stat in player_stats if stat['team_id'] == game_data['home_team_id']]
        away_team_stats = [stat for stat in player_stats if stat['team_id'] == game_data['away_team_id']]
        
        response_data = {
            'game': game_data,
            'home_team_stats': home_team_stats,
            'away_team_stats': away_team_stats,
            'total_players': len(player_stats)
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching game details: {e}')
        return make_response(jsonify({"error": "Failed to fetch game details"}), 500)


#------------------------------------------------------------
# Get upcoming games schedule
@games.route('/games/upcoming', methods=['GET'])
def get_upcoming_games():
    """
    Get upcoming games for the next specified days.
    Query parameters:
    - days: number of days to look ahead (default: 7)
    - team_id: filter by specific team
    """
    try:
        current_app.logger.info('GET /games/upcoming handler')
        
        days = request.args.get('days', 7, type=int)
        team_id = request.args.get('team_id', type=int)
        
        cursor = db.get_db().cursor()
        
        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        query = '''
            SELECT 
                g.game_id,
                g.game_date,
                g.game_time,
                g.home_team_id,
                g.away_team_id,
                ht.name AS home_team_name,
                at.name AS away_team_name,
                g.venue,
                g.game_type
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE g.game_date BETWEEN %s AND %s
            AND g.status = 'scheduled'
        '''
        
        params = [today, end_date]
        
        if team_id:
            query += ' AND (g.home_team_id = %s OR g.away_team_id = %s)'
            params.extend([team_id, team_id])
        
        query += ' ORDER BY g.game_date, g.game_time'
        
        cursor.execute(query, params)
        theData = cursor.fetchall()
        
        response_data = {
            'upcoming_games': theData,
            'date_range': {
                'start': str(today),
                'end': str(end_date)
            },
            'total_games': len(theData)
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching upcoming games: {e}')
        return make_response(jsonify({"error": "Failed to fetch upcoming games"}), 500)