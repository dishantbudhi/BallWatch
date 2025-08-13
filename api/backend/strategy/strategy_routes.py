"""
BallWatch Basketball Analytics Platform
=======================================
Strategic Planning Blueprint

Game plans, draft evaluations, and strategic planning tools
for coaches and general managers making data-driven decisions.

Author: StatPadders Team
Course: CS 3200 - Summer 2 2025
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
from datetime import datetime

# Create the Strategy Blueprint
strategy = Blueprint('strategy', __name__)


# ============================================================================
# GAME PLANNING & STRATEGY ROUTES
# ============================================================================

@strategy.route('/game-plans', methods=['GET'])
def get_game_plans():
    """
    Get game strategies and tactical plans.

    Query Parameters:
        team_id: Team ID (required)
        opponent_id: Opponent team ID (optional)
        game_id: Specific game ID (optional)
        status: Plan status ('draft', 'active', 'archived')

    User Stories: [Marcus-3.5]
    """
    try:
        current_app.logger.info('GET /strategy/game-plans - Fetching strategic game plans')

        team_id = request.args.get('team_id', type=int)
        opponent_id = request.args.get('opponent_id', type=int)
        game_id = request.args.get('game_id', type=int)
        status = request.args.get('status')

        if not team_id:
            return make_response(jsonify({"error": "team_id is required"}), 400)

        cursor = db.get_db().cursor()

        # Build comprehensive game plans query
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

        # Apply optional filters
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

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching game plans: {e}')
        return make_response(jsonify({"error": "Failed to fetch game plans"}), 500)


@strategy.route('/game-plans', methods=['POST'])
def create_game_plan():
    """
    Create a new strategic game plan.

    Expected JSON Body:
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

    User Stories: [Marcus-3.5]
    """
    try:
        current_app.logger.info('POST /strategy/game-plans - Creating new game plan')

        plan_data = request.get_json()

        # Validate required fields
        required_fields = ['team_id', 'plan_name']
        for field in required_fields:
            if field not in plan_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        # Validate status if provided
        valid_statuses = ['draft', 'active', 'archived']
        if 'status' in plan_data and plan_data['status'] not in valid_statuses:
            return make_response(jsonify({
                "error": f"Invalid status. Must be one of: {valid_statuses}"
            }), 400)

        cursor = db.get_db().cursor()

        # Verify team exists
        cursor.execute('SELECT team_id FROM Teams WHERE team_id = %s', (plan_data['team_id'],))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Team not found"}), 404)

        # Insert new strategic game plan
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
            "plan_id": new_plan_id,
            "plan_name": plan_data['plan_name'],
            "status": plan_data.get('status', 'draft')
        }), 201)

    except Exception as e:
        current_app.logger.error(f'Error creating game plan: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to create game plan"}), 500)


@strategy.route('/game-plans/<int:plan_id>', methods=['PUT'])
def update_game_plan(plan_id):
    """
    Update an existing strategic game plan.

    Expected JSON Body (all fields optional):
        {
            "plan_name": "string",
            "offensive_strategy": "string",
            "defensive_strategy": "string",
            "key_matchups": "string",
            "special_instructions": "string",
            "status": "draft|active|archived"
        }

    User Stories: [Marcus-3.5]
    """
    try:
        current_app.logger.info(f'PUT /strategy/game-plans/{plan_id} - Updating game plan')

        plan_data = request.get_json()

        if not plan_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        # Validate status if provided
        if 'status' in plan_data:
            valid_statuses = ['draft', 'active', 'archived']
            if plan_data['status'] not in valid_statuses:
                return make_response(jsonify({
                    "error": f"Invalid status. Must be one of: {valid_statuses}"
                }), 400)

        cursor = db.get_db().cursor()

        # Verify game plan exists
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

        # Always update the timestamp
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


# ============================================================================
# DRAFT EVALUATION & SCOUTING ROUTES
# ============================================================================

@strategy.route('/draft-evaluations', methods=['GET'])
def get_draft_evaluations():
    """
    Get player rankings and comprehensive draft evaluations.

    Query Parameters:
        position: Filter by position
        min_age: Minimum age filter
        max_age: Maximum age filter
        college: Filter by college
        evaluation_type: 'prospect', 'free_agent', 'trade_target'

    User Stories: [Andre-4.5]
    """
    try:
        current_app.logger.info('GET /strategy/draft-evaluations - Fetching draft evaluations')

        position = request.args.get('position')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        college = request.args.get('college')
        evaluation_type = request.args.get('evaluation_type')

        cursor = db.get_db().cursor()

        # Get comprehensive player evaluations with performance data
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
                p.current_salary,
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
                     de.comparison_player, de.last_updated, t.name, p.expected_salary, p.current_salary
            ORDER BY de.overall_rating DESC
        '''

        cursor.execute(query, params)
        evaluations = cursor.fetchall()

        response_data = {
            'evaluations': evaluations,
            'total_evaluations': len(evaluations),
            'filters': {
                'position': position,
                'age_range': f"{min_age}-{max_age}" if min_age or max_age else None,
                'college': college,
                'evaluation_type': evaluation_type
            }
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error fetching draft evaluations: {e}')
        return make_response(jsonify({"error": "Failed to fetch draft evaluations"}), 500)


@strategy.route('/draft-evaluations', methods=['POST'])
def add_draft_evaluation():
    """
    Add a new player evaluation for draft/scouting purposes.

    Expected JSON Body:
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

    User Stories: [Andre-4.5]
    """
    try:
        current_app.logger.info('POST /strategy/draft-evaluations - Adding player evaluation')

        eval_data = request.get_json()

        # Validate required fields
        required_fields = ['player_id', 'overall_rating']
        for field in required_fields:
            if field not in eval_data:
                return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)

        # Validate rating ranges
        if not 0 <= eval_data['overall_rating'] <= 100:
            return make_response(jsonify({
                "error": "overall_rating must be between 0 and 100"
            }), 400)

        # Validate evaluation type
        valid_types = ['prospect', 'free_agent', 'trade_target']
        if 'evaluation_type' in eval_data and eval_data['evaluation_type'] not in valid_types:
            return make_response(jsonify({
                "error": f"Invalid evaluation_type. Must be one of: {valid_types}"
            }), 400)

        cursor = db.get_db().cursor()

        # Verify player exists
        cursor.execute('SELECT player_id FROM Players WHERE player_id = %s', (eval_data['player_id'],))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Player not found"}), 404)

        # Check for existing evaluation
        cursor.execute('''
            SELECT evaluation_id FROM DraftEvaluations
            WHERE player_id = %s
        ''', (eval_data['player_id'],))

        if cursor.fetchone():
            return make_response(jsonify({
                "error": "Evaluation already exists for this player. Use PUT to update."
            }), 409)

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
            "evaluation_id": new_eval_id,
            "player_id": eval_data['player_id'],
            "overall_rating": eval_data['overall_rating']
        }), 201)

    except Exception as e:
        current_app.logger.error(f'Error adding draft evaluation: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to add draft evaluation"}), 500)


@strategy.route('/draft-evaluations/<int:evaluation_id>', methods=['PUT'])
def update_draft_evaluation(evaluation_id):
    """
    Update existing player evaluation and rankings.

    Expected JSON Body (all fields optional):
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

    User Stories: [Andre-4.5]
    """
    try:
        current_app.logger.info(f'PUT /strategy/draft-evaluations/{evaluation_id} - Updating evaluation')

        eval_data = request.get_json()

        if not eval_data:
            return make_response(jsonify({"error": "No data provided for update"}), 400)

        # Validate rating ranges if provided
        rating_fields = ['overall_rating', 'offensive_rating', 'defensive_rating',
                        'athleticism_rating', 'potential_rating']

        for field in rating_fields:
            if field in eval_data:
                if not 0 <= eval_data[field] <= 100:
                    return make_response(jsonify({
                        "error": f"{field} must be between 0 and 100"
                    }), 400)

        # Validate evaluation type
        if 'evaluation_type' in eval_data:
            valid_types = ['prospect', 'free_agent', 'trade_target']
            if eval_data['evaluation_type'] not in valid_types:
                return make_response(jsonify({
                    "error": f"Invalid evaluation_type. Must be one of: {valid_types}"
                }), 400)

        cursor = db.get_db().cursor()

        # Verify evaluation exists
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

        # Always update the timestamp
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


@strategy.route('/draft-evaluations/<int:evaluation_id>', methods=['DELETE'])
def delete_draft_evaluation(evaluation_id):
    """
    Delete a draft evaluation.

    User Stories: [Andre-4.5] (Evaluation management)
    """
    try:
        current_app.logger.info(f'DELETE /strategy/draft-evaluations/{evaluation_id} - Removing evaluation')

        cursor = db.get_db().cursor()

        # Verify evaluation exists
        cursor.execute('SELECT evaluation_id FROM DraftEvaluations WHERE evaluation_id = %s', (evaluation_id,))
        if not cursor.fetchone():
            return make_response(jsonify({"error": "Evaluation not found"}), 404)

        # Delete the evaluation
        cursor.execute('DELETE FROM DraftEvaluations WHERE evaluation_id = %s', (evaluation_id,))
        db.get_db().commit()

        return make_response(jsonify({
            "message": "Draft evaluation deleted successfully",
            "evaluation_id": evaluation_id
        }), 200)

    except Exception as e:
        current_app.logger.error(f'Error deleting draft evaluation: {e}')
        db.get_db().rollback()
        return make_response(jsonify({"error": "Failed to delete draft evaluation"}), 500)


@strategy.route('/contract-analysis', methods=['GET'])
def get_contract_analysis():
    """
    Get contract efficiency analysis for roster management.

    Query Parameters:
        team_id: Optional team filter
        position: Optional position filter
        min_salary: Minimum salary threshold

    User Stories: [Andre-4.6] (Contract efficiency metrics)
    """
    try:
        current_app.logger.info('GET /strategy/contract-analysis - Analyzing contract efficiency')

        team_id = request.args.get('team_id', type=int)
        position = request.args.get('position')
        min_salary = request.args.get('min_salary', type=float)

        cursor = db.get_db().cursor()

        # Get contract efficiency metrics
        query = '''
            SELECT
                p.player_id,
                p.first_name,
                p.last_name,
                p.position,
                p.current_salary,
                p.expected_salary,
                t.name AS current_team,
                COUNT(pgs.game_id) AS games_played,
                ROUND(AVG(pgs.points + pgs.rebounds + pgs.assists), 1) AS total_production,
                ROUND(AVG(pgs.points + pgs.rebounds + pgs.assists) / (p.current_salary / 1000000), 2) AS production_per_million,
                CASE
                    WHEN p.current_salary > p.expected_salary * 1.15 THEN 'Overpaid'
                    WHEN p.current_salary < p.expected_salary * 0.85 THEN 'Bargain'
                    ELSE 'Fair Value'
                END AS contract_assessment,
                ROUND(((p.expected_salary - p.current_salary) / p.current_salary) * 100, 1) AS value_percentage
            FROM Players p
            LEFT JOIN TeamsPlayers tp ON p.player_id = tp.player_id AND tp.left_date IS NULL
            LEFT JOIN Teams t ON tp.team_id = t.team_id
            LEFT JOIN PlayerGameStats pgs ON p.player_id = pgs.player_id
            WHERE p.current_salary > 0
        '''

        params = []

        if team_id:
            query += ' AND t.team_id = %s'
            params.append(team_id)
        if position:
            query += ' AND p.position = %s'
            params.append(position)
        if min_salary:
            query += ' AND p.current_salary >= %s'
            params.append(min_salary)

        query += '''
            GROUP BY p.player_id, p.first_name, p.last_name, p.position,
                     p.current_salary, p.expected_salary, t.name
            HAVING games_played >= 5
            ORDER BY production_per_million DESC
        '''

        cursor.execute(query, params)
        contract_analysis = cursor.fetchall()

        response_data = {
            'contract_analysis': contract_analysis,
            'total_analyzed': len(contract_analysis),
            'filters': {
                'team_id': team_id,
                'position': position,
                'min_salary': min_salary
            }
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        current_app.logger.error(f'Error analyzing contracts: {e}')
        return make_response(jsonify({"error": "Failed to analyze contracts"}), 500)