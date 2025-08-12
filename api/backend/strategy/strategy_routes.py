########################################################
# Strategy Blueprint - FIXED VERSION  
# Game plans, draft evaluations, and strategic planning
########################################################
from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
from datetime import datetime

strategy = Blueprint('strategy', __name__)


#------------------------------------------------------------
# Get game strategies/plans [Marcus-3.5]
@strategy.route('/game-plans', methods=['GET'])
def get_game_plans():
    """
    Get game strategies and plans.
    Query parameters:
    - team_id: team ID (required)
    - opponent_id: opponent team ID (optional)
    - game_id: specific game ID (optional)
    - status: plan status ('draft', 'active', 'archived')
    """
    try:
        current_app.logger.info('GET /game-plans handler')
        
        team_id = request.args.get('team_id', type=int)
        opponent_id = request.args.get('opponent_id', type=int)
        game_id = request.args.get('game_id', type=int)
        status = request.args.get('status')
        
        if not team_id:
            return make_response(jsonify({"error": "team_id is required"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Build query for game plans
        query = '''
            SELECT 
                gp.plan_id,
                gp.team_id,
                gp.opponent_id,
                gp.game_id,
                gp.plan_name,
                gp.offensive_strategy,
                gp.defensive_strategy,
                gp.key_matchups,
                gp.special_instructions,
                gp.status,
                gp.created_date,
                gp.updated_date,
                t.name AS team_name,
                opp.name AS opponent_name,
                g.game_date,
                g.game_time
            FROM GamePlans gp
            LEFT JOIN Teams t ON gp.team_id = t.team_id
            LEFT JOIN Teams opp ON gp.opponent_id = opp.team_id
            LEFT JOIN Game g ON gp.game_id = g.game_id
            WHERE gp.team_id = %s
        '''
        
        params = [team_id]
        
        if opponent_id:
            query += ' AND gp.opponent_id = %s'
            params.append(opponent_id)
        
        if game_id:
            query += ' AND gp.game_id = %s'
            params.append(game_id)
        
        if status:
            query += ' AND gp.status = %s'
            params.append(status)
        
        query += ' ORDER BY gp.created_date DESC'
        
        cursor.execute(query, params)
        game_plans = cursor.fetchall()
        
        response_data = {
            'game_plans': game_plans,
            'total_plans': len(game_plans),
            'filters': {
                'team_id': team_id,
                'opponent_id': opponent_id,
                'game_id': game_id,
                'status': status
            }
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching game plans: {e}')
        return make_response(jsonify({"error": "Failed to fetch game plans"}), 500)


#------------------------------------------------------------
# Create new game plan [Marcus-3.5]
@strategy.route('/game-plans', methods=['POST'])
def create_game_plan():
    """
    Create a new game plan.
    Expected JSON body:
    {
        "team_id": int (required),
        "opponent_id": int,
        "game_id": int,
        "plan_name": "string" (required),
        "offensive_strategy": "string",
        "defensive_strategy": "string",
        "key_matchups": "string",
        "special_instructions": "string",
        "status": "draft|active|archived" (default: "draft")
    }
    """
    try:
        current_app.logger.info('POST /game-plans handler')
        
        plan_data = request.get_json()
        
        # Validate required fields
        required_fields = ['team_id', 'plan_name']
        for field in required_fields:
            if field not in plan_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Insert new game plan
        query = '''
            INSERT INTO GamePlans (
                team_id, opponent_id, game_id, plan_name,
                offensive_strategy, defensive_strategy, key_matchups,
                special_instructions, status, created_date, updated_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        '''
        
        values = (
            plan_data['team_id'],
            plan_data.get('opponent_id'),
            plan_data.get('game_id'),
            plan_data['plan_name'],
            plan_data.get('offensive_strategy'),
            plan_data.get('defensive_strategy'),
            plan_data.get('key_matchups'),
            plan_data.get('special_instructions'),
            plan_data.get('status', 'draft')
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_plan_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Game plan created successfully",
            "plan_id": new_plan_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error creating game plan: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to create game plan"}), 500)


#------------------------------------------------------------
# Update existing game plan [Marcus-3.5]
@strategy.route('/game-plans/<int:plan_id>', methods=['PUT'])
def update_game_plan(plan_id):
    """
    Update an existing game plan.
    Expected JSON body (all fields optional):
    {
        "plan_name": "string",
        "offensive_strategy": "string",
        "defensive_strategy": "string",
        "key_matchups": "string",
        "special_instructions": "string",
        "status": "draft|active|archived"
    }
    """
    try:
        current_app.logger.info(f'PUT /game-plans/{plan_id} handler')
        
        plan_data = request.get_json()
        
        if not plan_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if game plan exists
        cursor.execute('SELECT plan_id FROM GamePlans WHERE plan_id = %s', (plan_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Game plan not found"}), 404)
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        allowed_fields = ['plan_name', 'offensive_strategy', 'defensive_strategy',
                         'key_matchups', 'special_instructions', 'status']
        
        for field in allowed_fields:
            if field in plan_data:
                update_fields.append(f'{field} = %s')
                values.append(plan_data[field])
        
        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
        # Always update the updated_date
        update_fields.append('updated_date = NOW()')
        
        query = f"UPDATE GamePlans SET {', '.join(update_fields)} WHERE plan_id = %s"
        values.append(plan_id)
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Game plan updated successfully",
            "plan_id": plan_id,
            "updated_fields": list(plan_data.keys())
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating game plan: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update game plan"}), 500)


#------------------------------------------------------------
# Get player rankings for draft evaluation [Andre-4.5]
@strategy.route('/draft-evaluations', methods=['GET'])
def get_draft_evaluations():
    """
    Get player rankings and draft evaluations.
    Query parameters:
    - position: filter by position
    - min_age: minimum age
    - max_age: maximum age
    - college: filter by college
    - evaluation_type: 'prospect', 'free_agent', 'trade_target'
    """
    try:
        current_app.logger.info('GET /draft-evaluations handler')
        
        position = request.args.get('position')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        college = request.args.get('college')
        evaluation_type = request.args.get('evaluation_type')
        
        cursor = db.get_db().cursor()
        
        # Get player evaluations
        query = '''
            SELECT 
                de.evaluation_id,
                de.player_id,
                p.first_name,
                p.last_name,
                p.position,
                p.age,
                p.college,
                p.height,
                p.weight,
                de.overall_rating,
                de.offensive_rating,
                de.defensive_rating,
                de.athleticism_rating,
                de.potential_rating,
                de.evaluation_type,
                de.strengths,
                de.weaknesses,
                de.scout_notes,
                de.projected_round,
                de.comparison_player,
                de.last_updated,
                t.name AS current_team,
                p.expected_salary,
                COUNT(pgs.game_id) AS games_played,
                ROUND(AVG(pgs.points), 1) AS avg_points,
                ROUND(AVG(pgs.rebounds), 1) AS avg_rebounds,
                ROUND(AVG(pgs.assists), 1) AS avg_assists
            FROM DraftEvaluations de
            JOIN Players p ON de.player_id = p.player_id
            LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
            LEFT JOIN Teams t ON tp.team_id = t.team_id
            LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
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
        
        if college:
            query += ' AND p.college = %s'
            params.append(college)
        
        if evaluation_type:
            query += ' AND de.evaluation_type = %s'
            params.append(evaluation_type)
        
        query += '''
            GROUP BY de.evaluation_id, de.player_id, p.first_name, p.last_name,
                     p.position, p.age, p.college, p.height, p.weight,
                     de.overall_rating, de.offensive_rating, de.defensive_rating,
                     de.athleticism_rating, de.potential_rating, de.evaluation_type,
                     de.strengths, de.weaknesses, de.scout_notes, de.projected_round,
                     de.comparison_player, de.last_updated, t.name, p.expected_salary
            ORDER BY de.overall_rating DESC
        '''
        
        cursor.execute(query, params)
        evaluations = cursor.fetchall()
        
        response_data = {
            'evaluations': evaluations,
            'total_evaluations': len(evaluations),
            'filters': {
                'position': position,
                'min_age': min_age,
                'max_age': max_age,
                'college': college,
                'evaluation_type': evaluation_type
            }
        }
        
        the_response = make_response(jsonify(response_data))
        the_response.status_code = 200
        return the_response
        
    except Exception as e:
        current_app.logger.error(f'Error fetching draft evaluations: {e}')
        return make_response(jsonify({"error": "Failed to fetch draft evaluations"}), 500)


#------------------------------------------------------------
# Add player evaluation [Andre-4.5]
@strategy.route('/draft-evaluations', methods=['POST'])
def add_draft_evaluation():
    """
    Add a new player evaluation for draft/scouting.
    Expected JSON body:
    {
        "player_id": int (required),
        "overall_rating": float (required, 0-100),
        "offensive_rating": float,
        "defensive_rating": float,
        "athleticism_rating": float,
        "potential_rating": float,
        "evaluation_type": "prospect|free_agent|trade_target",
        "strengths": "string",
        "weaknesses": "string",
        "scout_notes": "string",
        "projected_round": int,
        "comparison_player": "string"
    }
    """
    try:
        current_app.logger.info('POST /draft-evaluations handler')
        
        eval_data = request.get_json()
        
        # Validate required fields
        required_fields = ['player_id', 'overall_rating']
        for field in required_fields:
            if field not in eval_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
        
        # Validate rating range
        if not 0 <= eval_data['overall_rating'] <= 100:
            return make_response(jsonify({"error": "overall_rating must be between 0 and 100"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if player exists
        cursor.execute('SELECT player_id FROM Players WHERE player_id = %s', (eval_data['player_id'],))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found"}), 404)
        
        # Check for existing evaluation
        cursor.execute('''
            SELECT evaluation_id FROM DraftEvaluations 
            WHERE player_id = %s
        ''', (eval_data['player_id'],))
        
        if cursor.fetchone():
            return make_response(jsonify({"error": "Evaluation already exists for this player. Use PUT to update."}), 409)
        
        # Insert new evaluation
        query = '''
            INSERT INTO DraftEvaluations (
                player_id, overall_rating, offensive_rating, defensive_rating,
                athleticism_rating, potential_rating, evaluation_type,
                strengths, weaknesses, scout_notes, projected_round,
                comparison_player, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        '''
        
        values = (
            eval_data['player_id'],
            eval_data['overall_rating'],
            eval_data.get('offensive_rating'),
            eval_data.get('defensive_rating'),
            eval_data.get('athleticism_rating'),
            eval_data.get('potential_rating'),
            eval_data.get('evaluation_type', 'prospect'),
            eval_data.get('strengths'),
            eval_data.get('weaknesses'),
            eval_data.get('scout_notes'),
            eval_data.get('projected_round'),
            eval_data.get('comparison_player')
        )
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        new_eval_id = cursor.lastrowid
        
        return make_response(jsonify({
            "message": "Draft evaluation added successfully",
            "evaluation_id": new_eval_id
        }), 201)
        
    except Exception as e:
        current_app.logger.error(f'Error adding draft evaluation: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add draft evaluation"}), 500)


#------------------------------------------------------------
# Update player rankings [Andre-4.5]
@strategy.route('/draft-evaluations/<int:evaluation_id>', methods=['PUT'])
def update_draft_evaluation(evaluation_id):
    """
    Update existing player evaluation/rankings.
    Expected JSON body (all fields optional):
    {
        "overall_rating": float (0-100),
        "offensive_rating": float,
        "defensive_rating": float,
        "athleticism_rating": float,
        "potential_rating": float,
        "evaluation_type": "prospect|free_agent|trade_target",
        "strengths": "string",
        "weaknesses": "string",
        "scout_notes": "string",
        "projected_round": int,
        "comparison_player": "string"
    }
    """
    try:
        current_app.logger.info(f'PUT /draft-evaluations/{evaluation_id} handler')
        
        eval_data = request.get_json()
        
        if not eval_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)
        
        # Validate rating ranges if provided
        rating_fields = ['overall_rating', 'offensive_rating', 'defensive_rating',
                        'athleticism_rating', 'potential_rating']
        
        for field in rating_fields:
            if field in eval_data:
                if not 0 <= eval_data[field] <= 100:
                    return make_response(jsonify({"error": f"{field} must be between 0 and 100"}), 400)
        
        cursor = db.get_db().cursor()
        
        # Check if evaluation exists
        cursor.execute('SELECT evaluation_id FROM DraftEvaluations WHERE evaluation_id = %s', (evaluation_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Evaluation not found"}), 404)
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        allowed_fields = ['overall_rating', 'offensive_rating', 'defensive_rating',
                         'athleticism_rating', 'potential_rating', 'evaluation_type',
                         'strengths', 'weaknesses', 'scout_notes', 'projected_round',
                         'comparison_player']
        
        for field in allowed_fields:
            if field in eval_data:
                update_fields.append(f'{field} = %s')
                values.append(eval_data[field])
        
        if not update_fields:
            return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
        # Always update the last_updated timestamp
        update_fields.append('last_updated = NOW()')
        
        query = f"UPDATE DraftEvaluations SET {', '.join(update_fields)} WHERE evaluation_id = %s"
        values.append(evaluation_id)
        
        cursor.execute(query, values)
        db.get_db().commit()
        
        return make_response(jsonify({
            "message": "Draft evaluation updated successfully",
            "evaluation_id": evaluation_id,
            "updated_fields": list(eval_data.keys())
        }), 200)
        
    except Exception as e:
        current_app.logger.error(f'Error updating draft evaluation: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to update draft evaluation"}), 500)