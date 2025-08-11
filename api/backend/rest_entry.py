from flask import Flask

from backend.db_connection import db

# Basketball App API Routes
from backend.players.players_routes import players
from backend.teams.teams_routes import teams
from backend.games.games_routes import games
from backend.games.game_plan_routes import gameplans
from backend.analytics.analytics_routes import analytics
from backend.strategy.strategy_routes import strategy
from backend.admin.admin_routes import admin

import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Secret key for session security
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # MySQL database configuration
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME').strip()

    # Initialize the database connection
    app.logger.info('Initializing database connection...')
    db.init_app(app)

    # Register Basketball App API Blueprints
    app.logger.info('Registering Basketball API blueprints...')
    
    # Core basketball routes - all under /api prefix
    app.register_blueprint(players,     url_prefix='/api')
    app.register_blueprint(teams,       url_prefix='/api')
    app.register_blueprint(games,       url_prefix='/api')
    #app.register_blueprint(gameplans,       url_prefix='/api')
    app.register_blueprint(analytics,   url_prefix='/api')
    app.register_blueprint(strategy,    url_prefix='/api')
    app.register_blueprint(admin,       url_prefix='/api')
    
    app.logger.info('Basketball API routes registered successfully!')
    app.logger.info('Available endpoints:')
    app.logger.info('  Core Routes:')
    app.logger.info('    - /api/players')
    app.logger.info('    - /api/players/{id}/stats')
    app.logger.info('    - /api/teams')
    app.logger.info('    - /api/teams/{id}/players')
    app.logger.info('    - /api/games')
    app.logger.info('  Analytics Routes:')
    app.logger.info('    - /api/player-comparisons')
    app.logger.info('    - /api/player-matchups')
    app.logger.info('    - /api/opponent-reports')
    app.logger.info('    - /api/lineup-configurations')
    app.logger.info('    - /api/season-summaries')
    app.logger.info('  Strategy Routes:')
    app.logger.info('    - /api/game-plans')
    app.logger.info('    - /api/draft-evaluations')
    app.logger.info('  Admin Routes:')
    app.logger.info('    - /api/system-health')
    app.logger.info('    - /api/data-loads')
    app.logger.info('    - /api/error-logs')
    app.logger.info('    - /api/data-errors')
    app.logger.info('    - /api/data-cleanup')
    app.logger.info('    - /api/data-validation')

    return app