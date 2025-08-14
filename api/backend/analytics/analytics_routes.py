########################################################
# Analytics Blueprint
# Handles performance analytics, player matchups, and statistical comparisons
# for the BallWatch basketball analytics platform
########################################################

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object for analytics-related routes
analytics = Blueprint('analytics', __name__)


#------------------------------------------------------------
# Get player matchup analysis [Marcus-3.2]
@analytics.route('/player-matchups', methods=['GET'])
def get_player_matchups():
    """
    Get comprehensive matchup analysis between two players.

    Query parameters:
    - player1_id: first player ID (required)
    - player2_id: second player ID (required)
    - season: optional season filter

    Returns:
        JSON: Head-to-head matchup data and performance comparison
    """
    try:
        current_app.logger.info('GET /player-matchups handler started')

        # Extract and validate parameters
        player1_id = request.args.get('player1_id', type=int)
        player2_id = request.args.get('player2_id', type=int)
        season = request.args.get('season')

        if not player1_id or not player2_id:
            return make_response(jsonify({
                "error": "Both player1_id and player2_id are required"
            }), 400)

        cursor = db.get_db().cursor()

        # Use PlayerMatchup table (bridge) to find recorded matchups between two players.
        # We build two SELECTs and UNION them so we capture when either player was listed as
        # the offensive or defensive participant in the PlayerMatchup table, and normalize
        # the output so player1 refers to the first player_id provided and player2 to the second.
        season_clause = ''
        matchup_query = '''
            SELECT
                g.game_id,
                g.game_date,
                ht.name AS home_team,
                at.name AS away_team,
                COALESCE(pgs_off.points, 0) AS player1_points,
                COALESCE(pgs_off.rebounds, 0) AS player1_rebounds,
                COALESCE(pgs_off.assists, 0) AS player1_assists,
                COALESCE(pgs_def.points, 0) AS player2_points,
                COALESCE(pgs_def.rebounds, 0) AS player2_rebounds,
                COALESCE(pgs_def.assists, 0) AS player2_assists,
                CASE
                    WHEN (tp1.team_id = g.home_team_id AND g.home_score > g.away_score) OR
                         (tp1.team_id = g.away_team_id AND g.away_score > g.home_score) THEN 1
                    ELSE 0
                END AS player1_win
            FROM PlayerMatchup pm
            JOIN Game g ON pm.game_id = g.game_id
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            LEFT JOIN PlayerGameStats pgs_off ON pm.game_id = pgs_off.game_id AND pgs_off.player_id = pm.offensive_player_id
            LEFT JOIN PlayerGameStats pgs_def ON pm.game_id = pgs_def.game_id AND pgs_def.player_id = pm.defensive_player_id
            JOIN Players p1 ON pm.offensive_player_id = p1.player_id
            JOIN Players p2 ON pm.defensive_player_id = p2.player_id
            JOIN TeamsPlayers tp1 ON p1.player_id = tp1.player_id AND tp1.joined_date <= g.game_date AND (tp1.left_date IS NULL OR tp1.left_date >= g.game_date)
            JOIN TeamsPlayers tp2 ON p2.player_id = tp2.player_id AND tp2.joined_date <= g.game_date AND (tp2.left_date IS NULL OR tp2.left_date >= g.game_date)
            WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s
        '''

        # second select swaps offensive/defensive so player1 always maps to the first requested id
        matchup_query += '''
            UNION ALL
            SELECT
                g.game_id,
                g.game_date,
                ht.name AS home_team,
                at.name AS away_team,
                COALESCE(pgs_def.points, 0) AS player1_points,
                COALESCE(pgs_def.rebounds, 0) AS player1_rebounds,
                COALESCE(pgs_def.assists, 0) AS player1_assists,
                COALESCE(pgs_off.points, 0) AS player2_points,
                COALESCE(pgs_off.rebounds, 0) AS player2_rebounds,
                COALESCE(pgs_off.assists, 0) AS player2_assists,
                CASE
                    WHEN (tp2.team_id = g.home_team_id AND g.home_score > g.away_score) OR
                         (tp2.team_id = g.away_team_id AND g.away_score > g.home_score) THEN 1
                    ELSE 0
                END AS player1_win
            FROM PlayerMatchup pm
            JOIN Game g ON pm.game_id = g.game_id
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            LEFT JOIN PlayerGameStats pgs_off ON pm.game_id = pgs_off.game_id AND pgs_off.player_id = pm.offensive_player_id
            LEFT JOIN PlayerGameStats pgs_def ON pm.game_id = pgs_def.game_id AND pgs_def.player_id = pm.defensive_player_id
            JOIN Players p1 ON pm.offensive_player_id = p1.player_id
            JOIN Players p2 ON pm.defensive_player_id = p2.player_id
            JOIN TeamsPlayers tp1 ON p1.player_id = tp1.player_id AND tp1.joined_date <= g.game_date AND (tp1.left_date IS NULL OR tp1.left_date >= g.game_date)
            JOIN TeamsPlayers tp2 ON p2.player_id = tp2.player_id AND tp2.joined_date <= g.game_date AND (tp2.left_date IS NULL OR tp2.left_date >= g.game_date)
            WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s
        '''

        # Build params: first SELECT expects (player1, player2), second SELECT expects (player2, player1)
        params = [player1_id, player2_id, player2_id, player1_id]

        # Apply season filter to both SELECTs if provided
        if season:
            season_clause = ' AND g.season = %s'
            # inject season filter into both WHEREs by replacing the trailing WHERE lines
            matchup_query = matchup_query.replace('\n        WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s\n        ', '\n        WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s' + season_clause + '\n        ')
            matchup_query = matchup_query.replace('\n            WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s\n        ', '\n            WHERE pm.offensive_player_id = %s AND pm.defensive_player_id = %s' + season_clause + '\n        ')
            params.extend([season, season])

        # After UNION the table alias 'g' is out of scope for ORDER BY; use the unioned column name
        matchup_query += ' ORDER BY game_date DESC'

        cursor.execute(matchup_query, params)
        matchup_games = cursor.fetchall()

        # Calculate aggregated comparison statistics
        if matchup_games:
            player1_avg_points = sum(g['player1_points'] for g in matchup_games) / len(matchup_games)
            player2_avg_points = sum(g['player2_points'] for g in matchup_games) / len(matchup_games)
            player1_wins = sum(g['player1_win'] for g in matchup_games)
            player2_wins = len(matchup_games) - player1_wins
        else:
            player1_avg_points = player2_avg_points = 0
            player1_wins = player2_wins = 0

        response_data = {
            'matchup_games': matchup_games,
            'total_matchups': len(matchup_games),
            'summary': {
                'player1': {
                    'id': player1_id,
                    'avg_points': round(player1_avg_points, 1),
                    'head_to_head_wins': player1_wins
                },
                'player2': {
                    'id': player2_id,
                    'avg_points': round(player2_avg_points, 1),
                    'head_to_head_wins': player2_wins
                }
            }
        }

        current_app.logger.info(f'Successfully analyzed matchup between players {player1_id} and {player2_id}')
        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:
        current_app.logger.error(f'Error in get_player_matchups: {str(e)}')
        return make_response(jsonify({"error": "Failed to fetch player matchups"}), 500)


#------------------------------------------------------------
# Get opponent analysis and scouting report [Marcus-3.1]
@analytics.route('/opponent-reports', methods=['GET'])
def get_opponent_reports():
    """
    Get comprehensive opponent team analysis and scouting information.

    Query parameters:
    - team_id: your team ID (required)
    - opponent_id: opponent team ID (required)
    - last_n_games: number of recent games to analyze (default: 10)

    Returns:
        JSON: Complete opponent analysis with key players and performance trends
    """
    try:
        current_app.logger.info('GET /opponent-reports handler started')

        # Extract and validate parameters
        team_id = request.args.get('team_id', type=int)
        opponent_id = request.args.get('opponent_id', type=int)
        last_n_games = request.args.get('last_n_games', 10, type=int)

        if not team_id or not opponent_id:
            return make_response(jsonify({
                "error": "Both team_id and opponent_id are required"
            }), 400)

        cursor = db.get_db().cursor()

        # Get opponent team information
        opponent_info_query = '''
            SELECT
                t.team_id, t.name, t.city, t.conference, t.division, t.coach, t.arena,
                t.founded_year, t.championships, t.offensive_system, t.defensive_system,
                COUNT(DISTINCT tp.player_id) AS roster_size,
                ROUND(AVG(p.age), 1) AS avg_age
            FROM Teams t
            LEFT JOIN TeamsPlayers tp ON t.team_id = tp.team_id AND tp.left_date IS NULL
            LEFT JOIN Players p ON tp.player_id = p.player_id
            WHERE t.team_id = %s
            GROUP BY t.team_id, t.name, t.city, t.conference, t.division, t.coach, t.arena,
                t.founded_year, t.championships, t.offensive_system, t.defensive_system
        '''

        cursor.execute(opponent_info_query, (opponent_id,))
        opponent_info = cursor.fetchone()

        if not opponent_info:
            return make_response(jsonify({"error": "Opponent team not found"}), 404)

        # Get recent head-to-head history
        head_to_head_query = '''
            SELECT
                g.game_id,
                g.game_date,
                g.home_team_id,
                g.away_team_id,
                g.home_score,
                g.away_score,
                CASE
                    WHEN (g.home_team_id = %s AND g.home_score > g.away_score) OR
                         (g.away_team_id = %s AND g.away_score > g.home_score) THEN 'W'
                    ELSE 'L'
                END AS your_team_result
            FROM Game g
            WHERE ((g.home_team_id = %s AND g.away_team_id = %s) OR
                   (g.home_team_id = %s AND g.away_team_id = %s))
            AND g.status = 'completed'
            ORDER BY g.game_date DESC
            LIMIT %s
        '''

        cursor.execute(head_to_head_query,
                      (team_id, team_id, team_id, opponent_id, opponent_id, team_id, last_n_games))
        head_to_head = cursor.fetchall()

        # Get opponent's recent performance
        recent_performance_query = '''
            SELECT
                g.game_id,
                g.game_date,
                CASE
                    WHEN g.home_team_id = %s THEN g.home_score
                    ELSE g.away_score
                END AS opponent_score,
                CASE
                    WHEN g.home_team_id = %s THEN g.away_score
                    ELSE g.home_score
                END AS other_team_score,
                CASE
                    WHEN g.home_team_id = %s THEN at.name
                    ELSE ht.name
                END AS vs_team
            FROM Game g
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
            WHERE (g.home_team_id = %s OR g.away_team_id = %s)
            AND g.status = 'completed'
            ORDER BY g.game_date DESC
            LIMIT %s
        '''

        cursor.execute(recent_performance_query,
                      (opponent_id, opponent_id, opponent_id, opponent_id, opponent_id, last_n_games))
        recent_games = cursor.fetchall()

        # Get opponent's key players
        key_players_query = '''
            SELECT
                p.player_id,
                p.first_name,
                p.last_name,
                p.position,
                COUNT(pgs.game_id) AS games_played,
                ROUND(AVG(pgs.points), 1) AS avg_points,
                ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                ROUND(AVG(pgs.assists), 1) AS avg_assists
            FROM Players p
            JOIN TeamsPlayers tp ON p.player_id = tp.player_id
            LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            WHERE tp.team_id = %s AND tp.left_date IS NULL
            GROUP BY p.player_id, p.first_name, p.last_name, p.position
            HAVING games_played > 0
            ORDER BY avg_points DESC
            LIMIT 5
        '''

        cursor.execute(key_players_query, (opponent_id,))
        key_players = cursor.fetchall()

        # Calculate performance statistics
        if recent_games:
            avg_points_scored = sum(g['opponent_score'] for g in recent_games) / len(recent_games)
            avg_points_allowed = sum(g['other_team_score'] for g in recent_games) / len(recent_games)
            wins = sum(1 for g in recent_games if g['opponent_score'] > g['other_team_score'])
            win_percentage = (wins / len(recent_games)) * 100
        else:
            avg_points_scored = avg_points_allowed = win_percentage = 0

        response_data = {
            'opponent_info': opponent_info,
            'head_to_head_history': head_to_head,
            'recent_performance': {
                'games': recent_games,
                'avg_points_scored': round(avg_points_scored, 1),
                'avg_points_allowed': round(avg_points_allowed, 1),
                'win_percentage': round(win_percentage, 1),
                'last_n_games': len(recent_games)
            },
            'key_players': key_players
        }

        current_app.logger.info(f'Successfully generated opponent report for team {opponent_id}')
        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:
        current_app.logger.error(f'Error in get_opponent_reports: {str(e)}')
        return make_response(jsonify({"error": "Failed to fetch opponent report"}), 500)


#------------------------------------------------------------
# Get lineup effectiveness analysis [Marcus-3.4]
@analytics.route('/lineup-configurations', methods=['GET'])
def get_lineup_configurations():
    """
    Get lineup effectiveness analysis for strategic decision making.

    Query parameters:
    - team_id: team ID (required)
    - min_games: minimum games played together (default: 5)
    - season: optional season filter

    Returns:
        JSON: Lineup effectiveness data with performance metrics
    """
    try:
        current_app.logger.info('GET /lineup-configurations handler started')

        # Extract and validate parameters
        team_id = request.args.get('team_id', type=int)
        min_games = request.args.get('min_games', 5, type=int)
        season = request.args.get('season')

        if not team_id:
            return make_response(jsonify({"error": "team_id is required"}), 400)

        cursor = db.get_db().cursor()

        # FIX: Corrected query to ensure all players in a lineup belong to the selected team.
        lineup_query = '''
            SELECT
                lc.lineup_id,
                GROUP_CONCAT(CONCAT(p.first_name, ' ', p.last_name) ORDER BY pl.position_in_lineup SEPARATOR ', ') AS lineup,
                lc.plus_minus,
                lc.offensive_rating,
                lc.defensive_rating
            FROM LineupConfiguration lc
            JOIN PlayerLineups pl ON lc.lineup_id = pl.lineup_id
            JOIN Players p ON pl.player_id = p.player_id
            WHERE lc.team_id = %s
            GROUP BY lc.lineup_id, lc.plus_minus, lc.offensive_rating, lc.defensive_rating
            HAVING SUM(
                CASE WHEN pl.player_id IN (
                    SELECT player_id FROM TeamsPlayers WHERE team_id = %s AND left_date IS NULL
                ) THEN 0 ELSE 1 END
            ) = 0
            ORDER BY lc.plus_minus DESC
            LIMIT 10;
        '''

        cursor.execute(lineup_query, [team_id, team_id])
        lineup_stats = cursor.fetchall()

        response_data = {
            'team_id': team_id,
            'lineup_effectiveness': lineup_stats,
            'filters': {
                'min_games': min_games,
                'season': season
            }
        }

        current_app.logger.info(f'Successfully retrieved lineup configurations for team {team_id}')
        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:
        current_app.logger.error(f'Error in get_lineup_configurations: {str(e)}')
        return make_response(jsonify({"error": "Failed to fetch lineup configurations"}), 500)


#------------------------------------------------------------
# Get season performance summaries [Marcus-3.6]
@analytics.route('/season-summaries', methods=['GET'])
def get_season_summaries():
    """
    Get comprehensive season performance summaries for teams or players.

    Query parameters:
    - entity_type: 'team' or 'player' (required)
    - entity_id: team_id or player_id (required)
    - season: specific season (optional, defaults to current)

    Returns:
        JSON: Season summary with key performance indicators
    """
    try:
        current_app.logger.info('GET /season-summaries handler started')

        # Extract and validate parameters
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        season = request.args.get('season')

        if not entity_type or not entity_id:
            return make_response(jsonify({
                "error": "entity_type and entity_id are required"
            }), 400)

        if entity_type not in ['team', 'player']:
            return make_response(jsonify({
                "error": "entity_type must be 'team' or 'player'"
            }), 400)

        cursor = db.get_db().cursor()

        if entity_type == 'team':
            # Get comprehensive team season summary
            team_summary_query = '''
                SELECT
                    t.name AS team_name,
                    COUNT(DISTINCT g.game_id) AS games_played,
                    SUM(CASE
                        WHEN (g.home_team_id = %s AND g.home_score > g.away_score) OR
                             (g.away_team_id = %s AND g.away_score > g.home_score) THEN 1
                        ELSE 0
                    END) AS wins,
                    SUM(CASE
                        WHEN (g.home_team_id = %s AND g.home_score < g.away_score) OR
                             (g.away_team_id = %s AND g.away_score < g.home_score) THEN 1
                        ELSE 0
                    END) AS losses,
                    ROUND(AVG(CASE
                        WHEN g.home_team_id = %s THEN g.home_score
                        ELSE g.away_score
                    END), 1) AS avg_points_scored,
                    ROUND(AVG(CASE
                        WHEN g.home_team_id = %s THEN g.away_score
                        ELSE g.home_score
                    END), 1) AS avg_points_allowed
                FROM Teams t
                JOIN Game g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
                WHERE t.team_id = %s AND g.status = 'completed'
            '''

            params = [entity_id] * 7

            if season:
                team_summary_query += ' AND g.season = %s'
                params.append(season)

            team_summary_query += ' GROUP BY t.name'

            cursor.execute(team_summary_query, params)
            summary = cursor.fetchone()

        else:  # entity_type == 'player'
            # Get comprehensive player season summary
            player_summary_query = '''
                SELECT
                    p.first_name,
                    p.last_name,
                    p.position,
                    t.name AS team_name,
                    COUNT(pgs.game_id) AS games_played,
                    ROUND(AVG(pgs.points), 1) AS avg_points,
                    ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                    ROUND(AVG(pgs.assists), 1) AS avg_assists,
                    ROUND(AVG(pgs.steals), 1) AS avg_steals,
                    ROUND(AVG(pgs.blocks), 1) AS avg_blocks,
                    ROUND(AVG(pgs.plus_minus), 1) AS avg_plus_minus,
                    ROUND(AVG(pgs.minutes_played), 1) AS avg_minutes,
                    SUM(pgs.points) AS total_points,
                    MAX(pgs.points) AS season_high,
                    MIN(pgs.points) AS season_low
                FROM Players p
                LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
                LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
                LEFT JOIN Teams t ON tp.team_id = t.team_id
                LEFT JOIN Game g ON pgs.game_id = g.game_id
                WHERE p.player_id = %s
            '''

            params = [entity_id]

            if season:
                player_summary_query += ' AND g.season = %s'
                params.append(season)

            player_summary_query += ' GROUP BY p.player_id, p.first_name, p.last_name, p.position, t.name'

            cursor.execute(player_summary_query, params)
            summary = cursor.fetchone()

        response_data = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'season': season if season else 'current',
            'summary': summary
        }

        current_app.logger.info(f'Successfully generated season summary for {entity_type} {entity_id}')
        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:
        current_app.logger.error(f'Error in get_season_summaries: {str(e)}')
        return make_response(jsonify({"error": "Failed to fetch season summary"}), 500)