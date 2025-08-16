"""Basketball blueprint - players, teams, and games endpoints."""

from flask import Blueprint, request, jsonify, make_response, current_app
from datetime import datetime, timedelta
from backend.db_connection import db

# Create the Basketball Blueprint
basketball = Blueprint('basketball', __name__)


# ============================================================================
# PLAYER MANAGEMENT ROUTES
# ============================================================================

@basketball.route('/players', methods=['GET'])
def get_players():
    """
    Get all players with optional filters.

    Query Parameters:
        position: Filter by position (PG, SG, SF, PF, C)
        min_age: Minimum age filter
        max_age: Maximum age filter
        team_id: Filter by team ID
        min_salary: Minimum salary filter
        max_salary: Maximum salary filter

    User Stories: [Johnny-1.2, Johnny-1.3, Andre-4.1, Andre-4.4]
    """
    try:
        current_app.logger.info('GET /basketball/players - Fetching players with filters')

        # Extract query parameters
        position = request.args.get('position')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        team_id = request.args.get('team_id', type=int)
        min_salary = request.args.get('min_salary', type=float)
        max_salary = request.args.get('max_salary', type=float)

        cursor = db.get_db().cursor()

        # Build dynamic query with filters
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

        # Apply filters dynamically
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
        players_data = cursor.fetchall()

        return make_response(jsonify({
            'players': players_data,
            'total_count': len(players_data),
            'filters_applied': {
                'position': position,
                'age_range': f"{min_age}-{max_age}" if min_age or max_age else None,
                'team_id': team_id,
                'salary_range': f"${min_salary}-${max_salary}" if min_salary or max_salary else None
            }
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching players: {e}')
        return make_response(jsonify({"error": "Failed to fetch players"}), 500)


@basketball.route('/players', methods=['POST'])
def add_player():
    """
    Add a new player profile to the system.

    Expected JSON Body:
        {
            "first_name": "string" (required),
            "last_name": "string" (required),
            "position": "string" (required),
            "age": int (required),
            "years_exp": int,
            "college": "string",
            "current_salary": float,
            "expected_salary": float,
            "height": "string",
            "weight": int
        }

    User Stories: [Mike-2.2]
    """
    try:
        current_app.logger.info('POST /basketball/players - Adding new player')

        player_data = request.get_json()

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'position', 'age']
        for field in required_fields:
            if field not in player_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        cursor = db.get_db().cursor()

        # Insert new player
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

        new_player_id = cursor.lastrowid

        return make_response(jsonify({
            "message": "Player added successfully",
            "player_id": new_player_id,
            "player_name": f"{player_data['first_name']} {player_data['last_name']}"
        }), 201)

    except Exception as e:
        current_app.logger.error(f'Error adding player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add player"}), 500)


@basketball.route('/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    """
    Update player information.

    Expected JSON Body (all fields optional):
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

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info(f'PUT /basketball/players/{player_id} - Updating player')

        player_data = request.get_json()

        if not player_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        cursor = db.get_db().cursor()

        # Check if player exists
        cursor.execute('SELECT player_id FROM Players WHERE player_id = %s', (player_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found"}), 404)

        # Build dynamic update query for Players table
        update_fields = []
        values = []

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

        # Handle team assignment separately
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
            "player_id": player_id,
            "updated_fields": list(player_data.keys())
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error updating player: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update player"}), 500)


@basketball.route('/players/<int:player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    """
    Get player's performance statistics.

    Query Parameters:
        season: Optional season filter
        game_type: Optional game type filter ('regular', 'playoff')

    User Stories: [Johnny-1.1, Johnny-1.3, Johnny-1.4, Andre-4.3]
    """
    try:
        current_app.logger.info(f'GET /basketball/players/{player_id}/stats - Fetching player stats')

        season = request.args.get('season')
        game_type = request.args.get('game_type')

        cursor = db.get_db().cursor()

        # Get comprehensive player statistics
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
        stats_data = cursor.fetchone()

        if not stats_data:
            return make_response(jsonify({"error": "Player not found"}), 404)

        # Get recent games performance
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
            'player_stats': stats_data,
            'recent_games': recent_games,
            'filters': {
                'season': season,
                'game_type': game_type
            }
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching player stats: {e}')
        return make_response(jsonify({"error": "Failed to fetch player stats"}), 500)


@basketball.route('/players/<int:player_id>/stats', methods=['PUT'])
def update_player_stats(player_id):
    """
    Update or add player statistics for a specific game.

    Expected JSON Body:
        {
            "game_id": int (required),
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

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info(f'PUT /basketball/players/{player_id}/stats - Updating stats')

        stats_data = request.get_json()

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
            # Update existing statistics
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
            # Insert new statistics
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


# ============================================================================
# TEAM MANAGEMENT ROUTES
# ============================================================================

@basketball.route('/teams', methods=['GET'])
def get_teams():
    """
    Get all teams with optional filters and roster information.

    Query Parameters:
        conference: Filter by conference ('Eastern', 'Western')
        division: Filter by division
        city: Filter by city

    User Stories: [Johnny-1.2]
    """
    try:
        current_app.logger.info('GET /basketball/teams - Fetching teams')

        conference = request.args.get('conference')
        division = request.args.get('division')
        city = request.args.get('city')

        cursor = db.get_db().cursor()

        # Get teams with roster statistics
        query = '''
            SELECT
                t.team_id,
                t.name,
                t.city,
                t.arena,
                t.conference,
                t.division,
                t.coach,
                t.championships,
                t.founded_year,
                t.offensive_system,
                t.defensive_system,
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
            GROUP BY t.team_id, t.name, t.city, t.arena,
                     t.conference, t.division, t.coach,
                     t.championships, t.founded_year, t.offensive_system, t.defensive_system
            ORDER BY t.conference, t.division, t.name
        '''

        cursor.execute(query, params)
        teams_data = cursor.fetchall()

        return make_response(jsonify({
            'teams': teams_data,
            'total_count': len(teams_data),
            'filters_applied': {
                'conference': conference,
                'division': division,
                'city': city
            }
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching teams: {e}')
        return make_response(jsonify({"error": "Failed to fetch teams"}), 500)


@basketball.route('/teams/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    """
    Get detailed information for a specific team.

    User Stories: [Marcus-3.3, Andre-4.2]
    """
    try:
        current_app.logger.info(f'GET /basketball/teams/{team_id} - Fetching team details')

        cursor = db.get_db().cursor()

        # Get comprehensive team details
        query = '''
            SELECT
                t.team_id, t.name, t.city, t.conference, t.division, t.coach,
                t.arena, t.founded_year, t.championships, t.offensive_system,
                t.defensive_system,
                COUNT(DISTINCT tp.player_id) AS roster_size,
                ROUND(AVG(p.age), 1) AS avg_player_age,
                SUM(p.current_salary) AS total_salary,
                ROUND(AVG(p.current_salary), 0) AS avg_salary
            FROM Teams t
            LEFT JOIN TeamsPlayers tp ON t.team_id = tp.team_id AND tp.left_date IS NULL
            LEFT JOIN Players p ON tp.player_id = p.player_id
            WHERE t.team_id = %s
            GROUP BY t.team_id, t.name, t.city, t.conference, t.division, t.coach,
                t.arena, t.founded_year, t.championships, t.offensive_system,
                t.defensive_system
        '''


        cursor.execute(query, (team_id,))
        team_data = cursor.fetchone()

        if not team_data:
            return make_response(jsonify({"error": "Team not found"}), 404)

        # Get recent games performance
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
            'team_details': team_data,
            'recent_games': recent_games
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching team details: {e}')
        return make_response(jsonify({"error": "Failed to fetch team"}), 500)


@basketball.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    """
    Update team information.

    Expected JSON Body (all fields optional):
        {
            "name": "string",
            "city": "string",
            "arena": "string",
            "conference": "string",
            "division": "string",
            "coach": "string",
            "offensive_system": "string",
            "defensive_system": "string"
        }

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info(f'PUT /basketball/teams/{team_id} - Updating team')

        team_data = request.get_json()

        if not team_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        cursor = db.get_db().cursor()

        # Build dynamic update query
        update_fields = []
        values = []

        allowed_fields = ['name', 'city', 'arena', 'conference',
                         'division', 'coach', 'offensive_system', 'defensive_system']

        for field in allowed_fields:
            if field in team_data:
                update_fields.append(f'{field} = %s')
                values.append(team_data[field])

        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)

        query = f"UPDATE Teams SET {', '.join(update_fields)} WHERE team_id = %s"
        values.append(team_id)

        cursor.execute(query, values)

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


@basketball.route('/teams/<int:team_id>/players', methods=['GET'])
def get_team_players(team_id):
    """
    Get current team roster with detailed player information.

    Query Parameters:
        position: Filter by position (PG, SG, SF, PF, C)
        include_stats: If 'true', include player statistics

    User Stories: [Marcus-3.3, Andre-4.2]
    """
    try:
        current_app.logger.info(f'GET /basketball/teams/{team_id}/players - Fetching roster')

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
        roster_data = cursor.fetchall()

        # Get team name for context
        cursor.execute('SELECT name FROM Teams WHERE team_id = %s', (team_id,))
        team_info = cursor.fetchone()

        response_data = {
            'team_id': team_id,
            'team_name': team_info['name'] if team_info else None,
            'roster_size': len(roster_data),
            'players': roster_data,
            'includes_stats': include_stats,
            'position_filter': position
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching team roster: {e}')
        return make_response(jsonify({"error": "Failed to fetch team roster"}), 500)


@basketball.route('/teams/<int:team_id>/players', methods=['POST'])
def add_team_player(team_id):
    """
    Add a player to team roster.

    Expected JSON Body:
        {
            "player_id": int (required),
            "jersey_num": int (required),
            "joined_date": "YYYY-MM-DD" (required)
        }

    User Stories: [Mike-2.2]
    """
    try:
        current_app.logger.info(f'POST /basketball/teams/{team_id}/players - Adding player to roster')

        roster_data = request.get_json()
        player_id = roster_data.get('player_id')
        jersey_num = roster_data.get('jersey_num')
        joined_date = roster_data.get('joined_date')

        if not player_id or jersey_num is None or not joined_date:
            return make_response(jsonify({
                "error": "Missing required fields: player_id, jersey_num, joined_date"
            }), 400)

        cursor = db.get_db().cursor()

        # Validate player exists
        cursor.execute('SELECT player_id FROM Players WHERE player_id = %s', (player_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found"}), 404)

        # Check jersey number availability
        cursor.execute('''
            SELECT player_id FROM TeamsPlayers
            WHERE team_id = %s AND jersey_num = %s AND left_date IS NULL
        ''', (team_id, jersey_num))
        if cursor.fetchone():
            return make_response(jsonify({
                "error": f"Jersey number {jersey_num} is already taken"
            }), 409)

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
        current_app.logger.error(f'Error adding player to roster: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add player to roster"}), 500)


@basketball.route('/teams/<int:team_id>/players/<int:player_id>', methods=['PUT'])
def update_team_player(team_id, player_id):
    """
    Update player's status on team (jersey number, left date, etc.).

    Expected JSON Body (all fields optional):
        {
            "jersey_num": int,
            "left_date": "YYYY-MM-DD",
            "status": "active|injured|suspended"
        }

    User Stories: [Mike-2.1, Johnny-1.6]
    """
    try:
        current_app.logger.info(f'PUT /basketball/teams/{team_id}/players/{player_id} - Updating player status')

        update_data = request.get_json()

        if not update_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        cursor = db.get_db().cursor()

        # Verify player-team association exists
        cursor.execute('''
            SELECT * FROM TeamsPlayers
            WHERE team_id = %s AND player_id = %s AND left_date IS NULL
        ''', (team_id, player_id))

        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found on this team"}), 404)

        # Build dynamic update query
        update_fields = []
        values = []

        if 'jersey_num' in update_data:
            jersey_num = update_data['jersey_num']
            # Check if new jersey number is available
            cursor.execute('''
                SELECT player_id FROM TeamsPlayers
                WHERE team_id = %s AND jersey_num = %s AND player_id != %s AND left_date IS NULL
            ''', (team_id, jersey_num, player_id))
            if cursor.fetchone():
                return make_response(jsonify({
                    "error": f"Jersey number {jersey_num} is already taken"
                }), 409)
            update_fields.append('jersey_num = %s')
            values.append(jersey_num)

        if 'left_date' in update_data:
            update_fields.append('left_date = %s')
            values.append(update_data['left_date'])

        if 'status' in update_data:
            update_fields.append('status = %s')
            values.append(update_data['status'])

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
            "updated_fields": list(update_data.keys())
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error updating player status: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update player status"}), 500)


# ============================================================================
# GAME MANAGEMENT ROUTES
# ============================================================================

@basketball.route('/games', methods=['GET'])
def get_games():
    """
    Get games list with optional filters.

    Query Parameters:
        team_id: Filter by team (home or away)
        start_date: Filter games from this date (YYYY-MM-DD)
        end_date: Filter games until this date (YYYY-MM-DD)
        season: Filter by season
        game_type: Filter by game type ('regular', 'playoff')
        status: Filter by status ('scheduled', 'in_progress', 'completed')

    User Stories: [Johnny-1.5, Marcus-3.6]
    """
    try:
        current_app.logger.info('GET /basketball/games - Fetching games schedule')

        # Extract query parameters
        team_id = request.args.get('team_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        season = request.args.get('season')
        game_type = request.args.get('game_type')
        status = request.args.get('status')

        cursor = db.get_db().cursor()

        # Build comprehensive games query
        query = '''
            SELECT
                g.game_id,
                g.game_date,
                TIME_FORMAT(g.game_time, '%%H:%%i:%%s') AS game_time,
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
                    WHEN g.home_score > g.away_score THEN ht.name
                    WHEN g.away_score > g.home_score THEN at.name
                    ELSE NULL
                END AS winner
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE 1=1
        '''

        params = []

        # Apply filters dynamically
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

        query += ' ORDER BY g.game_date DESC'

        cursor.execute(query, params)
        games_data = cursor.fetchall()

        # Calculate summary statistics
        completed_games = len([g for g in games_data if g['status'] == 'completed'])
        scheduled_games = len([g for g in games_data if g['status'] == 'scheduled'])
        in_progress_games = len([g for g in games_data if g['status'] == 'in_progress'])

        response_data = {
            'games': games_data,
            'summary': {
                'total_games': len(games_data),
                'completed_games': completed_games,
                'scheduled_games': scheduled_games,
                'in_progress_games': in_progress_games
            },
            'filters_applied': {
                'team_id': team_id,
                'date_range': f"{start_date} to {end_date}" if start_date or end_date else None,
                'season': season,
                'game_type': game_type,
                'status': status
            }
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching games: {e}')
        return make_response(jsonify({"error": "Failed to fetch games"}), 500)


@basketball.route('/games', methods=['POST'])
def create_game():
    """
    Create a new game.

    Expected JSON Body:
        {
            "game_date": "YYYY-MM-DD" (required),
            "game_time": "HH:MM:SS" (optional),
            "home_team_id": int (required),
            "away_team_id": int (required),
            "season": "string" (required),
            "game_type": "regular|playoff" (default: "regular"),
            "status": "scheduled|in_progress|completed" (default: "scheduled"),
            "venue": "string" (optional),
            "attendance": int (optional)
        }

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info('POST /basketball/games - Creating new game')

        game_data = request.get_json()

        # Validate required fields
        required_fields = ['game_date', 'home_team_id', 'away_team_id', 'season']
        for field in required_fields:
            if field not in game_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        # Business logic validations
        if game_data['home_team_id'] == game_data['away_team_id']:
            return make_response(jsonify({"error": "Home and away teams must be different"}), 400)

        # Validate enums
        valid_game_types = ['regular', 'playoff']
        if 'game_type' in game_data and game_data['game_type'] not in valid_game_types:
            return make_response(jsonify({
                "error": f"Invalid game_type. Must be one of: {valid_game_types}"
            }), 400)

        valid_statuses = ['scheduled', 'in_progress', 'completed']
        if 'status' in game_data and game_data['status'] not in valid_statuses:
            return make_response(jsonify({
                "error": f"Invalid status. Must be one of: {valid_statuses}"
            }), 400)

        cursor = db.get_db().cursor()

        # Verify both teams exist
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
            return make_response(jsonify({
                "error": "Game already exists for these teams on this date"
            }), 409)

        # Insert new game
        query = '''
            INSERT INTO Game (
                game_date, game_time, home_team_id, away_team_id,
                home_score, away_score, season, game_type, status, venue, attendance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        values = (
            game_data['game_date'],
            game_data.get('game_time'),
            game_data['home_team_id'],
            game_data['away_team_id'],
            game_data.get('home_score', 0),
            game_data.get('away_score', 0),
            game_data['season'],
            game_data.get('game_type', 'regular'),
            game_data.get('status', 'scheduled'),
            game_data.get('venue'),
            game_data.get('attendance')
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


@basketball.route('/games/<int:game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Get detailed information for a specific game including player stats.

    User Stories: [Johnny-1.5, Marcus-3.6]
    """
    try:
        current_app.logger.info(f'GET /basketball/games/{game_id} - Fetching game details')

        cursor = db.get_db().cursor()

        # Get comprehensive game details
        query = '''
            SELECT
                g.game_id,
                g.game_date,
                TIME_FORMAT(g.game_time, '%%H:%%i:%%s') AS game_time,
                g.home_team_id,
                g.away_team_id,
                g.home_score,
                g.away_score,
                g.season,
                g.game_type,
                g.status,
                g.attendance,
                g.venue,
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

        # Get player statistics for this game
        cursor.execute('''
            SELECT
                pgs.player_id,
                pgs.game_id,
                pgs.points,
                pgs.rebounds,
                pgs.assists,
                pgs.steals,
                pgs.blocks,
                pgs.turnovers,
                pgs.shooting_percentage,
                pgs.three_point_percentage,
                pgs.free_throw_percentage,
                pgs.plus_minus,
                pgs.minutes_played,
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
            'game_details': game_data,
            'home_team_stats': home_team_stats,
            'away_team_stats': away_team_stats,
            'total_players': len(player_stats)
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching game details: {e}')
        return make_response(jsonify({"error": "Failed to fetch game details"}), 500)


@basketball.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """
    Update game information and scores.

    Expected JSON Body (all fields optional):
        {
            "game_date": "YYYY-MM-DD",
            "game_time": "HH:MM:SS",
            "home_score": int,
            "away_score": int,
            "season": "string",
            "game_type": "regular|playoff",
            "status": "scheduled|in_progress|completed",
            "venue": "string",
            "attendance": int
        }

    User Stories: [Mike-2.1]
    """
    try:
        current_app.logger.info(f'PUT /basketball/games/{game_id} - Updating game')

        game_data = request.get_json()

        if not game_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        cursor = db.get_db().cursor()

        # Verify game exists
        cursor.execute('SELECT game_id FROM Game WHERE game_id = %s', (game_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Game not found"}), 404)

        # Validate enum fields
        if 'game_type' in game_data:
            valid_game_types = ['regular', 'playoff']
            if game_data['game_type'] not in valid_game_types:
                return make_response(jsonify({
                    "error": f"Invalid game_type. Must be one of: {valid_game_types}"
                }), 400)

        if 'status' in game_data:
            valid_statuses = ['scheduled', 'in_progress', 'completed']
            if game_data['status'] not in valid_statuses:
                return make_response(jsonify({
                    "error": f"Invalid status. Must be one of: {valid_statuses}"
                }), 400)

        # Validate score values
        for score_field in ['home_score', 'away_score']:
            if score_field in game_data and game_data[score_field] < 0:
                return make_response(jsonify({
                    "error": f"{score_field} cannot be negative"
                }), 400)

        if 'attendance' in game_data and game_data['attendance'] < 0:
            return make_response(jsonify({"error": "Attendance cannot be negative"}), 400)

        # Build dynamic update query
        update_fields = []
        values = []

        allowed_fields = ['game_date', 'game_time', 'home_score', 'away_score',
                         'season', 'game_type', 'status', 'venue', 'attendance']

        for field in allowed_fields:
            if field in game_data:
                update_fields.append(f'{field} = %s')
                values.append(game_data[field])

        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)

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


@basketball.route('/games/upcoming', methods=['GET'])
def get_upcoming_games():
    """
    Get upcoming games for the next specified days.

    Query Parameters:
        days: Number of days to look ahead (default: 7)
        team_id: Filter by specific team

    User Stories: [Johnny-1.5, Marcus-3.6]
    """
    try:
        current_app.logger.info('GET /basketball/games/upcoming - Fetching upcoming games')

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
                TIME_FORMAT(g.game_time, '%%H:%%i:%%s') AS game_time,
                g.home_team_id,
                g.away_team_id,
                ht.name AS home_team_name,
                at.name AS away_team_name,
                g.venue,
                g.game_type,
                g.status
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE g.game_date BETWEEN %s AND %s
            AND g.status IN ('scheduled', 'in_progress')
        '''

        params = [today, end_date]

        if team_id:
            query += ' AND (g.home_team_id = %s OR g.away_team_id = %s)'
            params.extend([team_id, team_id])

        query += ' ORDER BY g.game_date, g.game_time'

        cursor.execute(query, params)
        upcoming_games = cursor.fetchall()

        response_data = {
            'upcoming_games': upcoming_games,
            'date_range': {
                'start': str(today),
                'end': str(end_date),
                'days_ahead': days
            },
            'total_games': len(upcoming_games)
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching upcoming games: {e}')
        return make_response(jsonify({"error": "Failed to fetch upcoming games"}), 500)


@basketball.route('/teams/<int:team_id>/schedule', methods=['GET'])
def get_team_schedule(team_id):
    """
    Get a specific team's schedule with win/loss records.

    Query Parameters:
        season: Optional season filter
        status: Optional status filter

    User Stories: [Marcus-3.6, Johnny-1.5]
    """
    try:
        current_app.logger.info(f'GET /basketball/teams/{team_id}/schedule - Fetching team schedule')

        season = request.args.get('season')
        status = request.args.get('status')

        cursor = db.get_db().cursor()

        # Verify team exists
        cursor.execute('SELECT team_id, name FROM Teams WHERE team_id = %s', (team_id,))
        team_info = cursor.fetchone()

        if not team_info:
            return make_response(jsonify({"error": "Team not found"}), 404)

        query = '''
            SELECT
                g.game_id,
                g.game_date,
                TIME_FORMAT(g.game_time, '%%H:%%i:%%s') AS game_time,
                g.home_team_id,
                g.away_team_id,
                CASE
                    WHEN g.home_team_id = %s THEN 'Home'
                    ELSE 'Away'
                END AS home_away,
                CASE
                    WHEN g.home_team_id = %s THEN at.name
                    ELSE ht.name
                END AS opponent,
                g.home_score,
                g.away_score,
                CASE
                    WHEN g.status = 'completed' THEN
                        CASE
                            WHEN (g.home_team_id = %s AND g.home_score > g.away_score) OR
                                 (g.away_team_id = %s AND g.away_score > g.home_score) THEN 'W'
                            ELSE 'L'
                        END
                    ELSE NULL
                END AS result,
                g.season,
                g.game_type,
                g.status,
                g.venue
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE (g.home_team_id = %s OR g.away_team_id = %s)
        '''

        params = [team_id, team_id, team_id, team_id, team_id, team_id]

        if season:
            query += ' AND g.season = %s'
            params.append(season)
        if status:
            query += ' AND g.status = %s'
            params.append(status)

        query += ' ORDER BY g.game_date DESC'

        cursor.execute(query, params)
        schedule = cursor.fetchall()

        # Calculate team record
        completed_games = [g for g in schedule if g['result'] is not None]
        wins = len([g for g in completed_games if g['result'] == 'W'])
        losses = len([g for g in completed_games if g['result'] == 'L'])

        response_data = {
            'team_id': team_id,
            'team_name': team_info['name'],
            'schedule': schedule,
            'record': {
                'wins': wins,
                'losses': losses,
                'games_played': len(completed_games),
                'win_percentage': round((wins / len(completed_games)) * 100, 1) if completed_games else 0
            },
            'filters': {
                'season': season,
                'status': status
            }
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching team schedule: {e}')
        return make_response(jsonify({"error": "Failed to fetch team schedule"}), 500)


@basketball.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """
    Delete a game (admin function).
    This will cascade delete all related player stats.

    User Stories: [Mike-2.3] (Data cleanup)
    """
    try:
        current_app.logger.info(f'DELETE /basketball/games/{game_id} - Deleting game')

        cursor = db.get_db().cursor()

        # Verify game exists
        cursor.execute('SELECT game_id FROM Game WHERE game_id = %s', (game_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Game not found"}), 404)

        # Delete the game (cascades to PlayerGameStats)
        cursor.execute('DELETE FROM Game WHERE game_id = %s', (game_id,))
        db.get_db().commit()

        return make_response(jsonify({
            "message": "Game deleted successfully",
            "game_id": game_id
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error deleting game: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to delete game"}), 500)