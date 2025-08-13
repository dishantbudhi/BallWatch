"""
BallWatch Basketball Analytics Platform
=======================================
CS 3200 - Summer 2 2025
Team: StatPadders

Flask REST API Entry Point
Provides comprehensive basketball analytics for teams and fans through 
data-driven insights, player statistics, and strategic analysis.

Author: StatPadders Team
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Database connection
from backend.db_connection import db

# Basketball Analytics API Route Blueprints
from backend.core.basketball_routes import basketball
from backend.analytics.analytics_routes import analytics
from backend.strategy.strategy_routes import strategy
from backend.admin.admin_routes import admin


def create_app():
    """
    Create and configure the BallWatch Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load environment configuration
    load_dotenv()
    _configure_app(app)
    
    # Initialize database connection
    _initialize_database(app)
    
    # Register API blueprints
    _register_blueprints(app)
    
    # Log application setup completion
    _log_startup_info(app)
    
    return app


def _configure_app(app):
    """Configure Flask application settings."""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # MySQL Database Configuration
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER', '').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD', '').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST', 'localhost').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT', '3306').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME', 'BallWatch').strip()


def _initialize_database(app):
    """Initialize database connection with the Flask app."""
    app.logger.info('🏀 Initializing BallWatch database connection...')
    try:
        db.init_app(app)
        app.logger.info('✅ Database connection established successfully')
    except Exception as e:
        app.logger.error(f'❌ Database connection failed: {e}')
        raise


def _register_blueprints(app):
    """Register all API blueprints with the Flask application."""
    app.logger.info('📋 Registering BallWatch API blueprints...')
    
    # Core Basketball Analytics Routes with specific prefixes
    blueprints = [
        (basketball, '/basketball', 'Core Basketball Operations (Players, Teams, Games)'),
        (analytics, '/analytics', 'Performance Analytics & Comparisons'),
        (strategy, '/strategy', 'Game Plans & Draft Evaluations'),
        (admin, '/system', 'System Administration & Data Management')
    ]
    
    for blueprint, prefix, description in blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)
        app.logger.info(f'  ✓ {blueprint.name} ({prefix}): {description}')


def _log_startup_info(app):
    """Log application startup information and available endpoints."""
    app.logger.info('🎯 BallWatch API routes registered successfully!')
    app.logger.info('=' * 60)
    app.logger.info('📊 BALLWATCH BASKETBALL ANALYTICS API')
    app.logger.info('=' * 60)
    
    # Core Functionality Routes
    app.logger.info('🏀 CORE BASKETBALL ROUTES:')
    app.logger.info('   📋 Players:')
    app.logger.info('      GET    /basketball/players              - Get all players with filters')
    app.logger.info('      POST   /basketball/players              - Add new player profile')
    app.logger.info('      PUT    /basketball/players/{id}         - Update player information')
    app.logger.info('      GET    /basketball/players/{id}/stats   - Get player performance stats')
    app.logger.info('      PUT    /basketball/players/{id}/stats   - Update player game statistics')
    
    app.logger.info('   🏟️  Teams:')
    app.logger.info('      GET    /basketball/teams                - Get all teams with filters')
    app.logger.info('      GET    /basketball/teams/{id}           - Get specific team details')
    app.logger.info('      PUT    /basketball/teams/{id}           - Update team information')
    app.logger.info('      GET    /basketball/teams/{id}/players   - Get team roster')
    app.logger.info('      POST   /basketball/teams/{id}/players   - Add player to roster')
    app.logger.info('      PUT    /basketball/teams/{id}/players/{pid} - Update player status')
    
    app.logger.info('   🏆 Games:')
    app.logger.info('      GET    /basketball/games                - Get games schedule/results')
    app.logger.info('      POST   /basketball/games                - Create new game')
    app.logger.info('      GET    /basketball/games/{id}           - Get game details & stats')
    app.logger.info('      PUT    /basketball/games/{id}           - Update game scores/info')
    app.logger.info('      GET    /basketball/games/upcoming       - Get upcoming games')
    
    # Analytics & Intelligence Routes  
    app.logger.info('📈 ANALYTICS & INSIGHTS:')
    app.logger.info('   🔬 Performance Analytics:')
    app.logger.info('      GET    /analytics/player-comparisons   - Side-by-side player analysis')
    app.logger.info('      GET    /analytics/player-matchups      - Head-to-head matchup data')
    app.logger.info('      GET    /analytics/opponent-reports     - Opponent scouting reports')
    app.logger.info('      GET    /analytics/lineup-configurations- Lineup effectiveness analysis')
    app.logger.info('      GET    /analytics/season-summaries     - Season performance summaries')
    
    # Strategic Planning Routes
    app.logger.info('   🎯 Strategic Planning:')
    app.logger.info('      GET    /strategy/game-plans           - Get strategic game plans')
    app.logger.info('      POST   /strategy/game-plans           - Create new game plan')
    app.logger.info('      PUT    /strategy/game-plans/{id}      - Update game plan')
    app.logger.info('      GET    /strategy/draft-evaluations    - Get player draft rankings')
    app.logger.info('      POST   /strategy/draft-evaluations    - Add player evaluation')
    app.logger.info('      PUT    /strategy/draft-evaluations/{id} - Update player rankings')
    
    # System Administration Routes
    app.logger.info('⚙️  SYSTEM ADMINISTRATION:')
    app.logger.info('   🩺 System Health:')
    app.logger.info('      GET    /system/health        - Get system status & metrics')
    app.logger.info('      GET    /system/data-loads           - Get data load history')
    app.logger.info('      POST   /system/data-loads           - Start new data load')
    app.logger.info('      PUT    /system/data-loads/{id}      - Update load status')
    
    app.logger.info('   🔍 Error Management:')
    app.logger.info('      GET    /system/error-logs           - Get error log history')  
    app.logger.info('      POST   /system/error-logs           - Log new system error')
    app.logger.info('      GET    /system/data-errors          - Get data validation errors')
    app.logger.info('      GET    /system/data-cleanup         - Get cleanup schedules')
    app.logger.info('      POST   /system/data-cleanup         - Schedule data cleanup')
    app.logger.info('      GET    /system/data-validation      - Get validation reports')
    app.logger.info('      POST   /system/data-validation      - Run validation checks')
    
    app.logger.info('=' * 60)
    app.logger.info('🚀 BallWatch API Server Ready!')
    app.logger.info('   💡 Transforming NBA analytics into actionable insights')
    app.logger.info('   👥 Serving: Superfans | Data Engineers | Coaches | GMs')
    app.logger.info('=' * 60)


if __name__ == '__main__':
    # Create and run the application
    application = create_app()
    application.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 4000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )