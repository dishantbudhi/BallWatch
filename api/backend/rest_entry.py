"""Flask REST API entry point and application factory."""

from flask import Flask
from dotenv import load_dotenv
import os
import time
import logging
import pymysql

# Database connection
from backend.db_connection import db

# Blueprints
from backend.basketball.basketball_routes import basketball
from backend.analytics.analytics_routes import analytics
from backend.strategy.strategy_routes import strategy
from backend.admin.admin_routes import admin
from backend.auth.auth_routes import auth


def wait_for_db(app, max_retries=30, retry_delay=2):
    """Wait for database to be ready before starting the application."""
    db_config = {
        'host': app.config.get('MYSQL_DATABASE_HOST', 'db'),
        'port': app.config.get('MYSQL_DATABASE_PORT', 3306),
        'user': app.config.get('MYSQL_DATABASE_USER', 'root'),
        'password': app.config.get('MYSQL_DATABASE_PASSWORD', ''),
        'database': app.config.get('MYSQL_DATABASE_DB', 'BallWatch')
    }
    
    for attempt in range(max_retries):
        try:
            # Try to connect to MySQL
            connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            connection.close()
            app.logger.info(f"✅ Database connection successful on attempt {attempt + 1}")
            return True
        except Exception as e:
            app.logger.warning(f"🔄 Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    app.logger.error("❌ Failed to connect to database after all retries")
    return False


def create_app():
    """Create and configure the BallWatch Flask application."""
    app = Flask(__name__)
    
    # Load environment configuration
    load_dotenv()
    _configure_app(app)
    
    # Wait for database to be ready
    if not wait_for_db(app):
        app.logger.error("Cannot start application without database connection")
        # Continue anyway for development, but log the error
    
    # Initialize database connection
    _initialize_database(app)
    
    # Register API blueprints
    _register_blueprints(app)
    
    # Log application setup completion
    _log_startup_info(app)
    
    return app


def _configure_app(app):
    """Configure Flask application settings."""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # MySQL Database Configuration
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER', 'root').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD', '').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST', 'db').strip()  # Use 'db' for Docker
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT', '3306').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME', 'BallWatch').strip()


def _initialize_database(app):
    """Initialize database connection with the Flask app."""
    app.logger.info('🏀 Initializing BallWatch database connection...')
    try:
        db.init_app(app)
        app.logger.info('✅ Database connection established successfully')
    except Exception as e:
        app.logger.error(f'⌠Database connection failed: {e}')
        # Don't raise the exception - let the app start anyway


def _register_blueprints(app):
    """Register all API blueprints with the Flask application."""
    app.logger.info('📋 Registering BallWatch API blueprints...')
    
    blueprints = [
        (basketball, '/basketball', 'Core Basketball Operations'),
        (analytics, '/analytics', 'Performance Analytics'),
        (strategy, '/strategy', 'Game Plans & Draft Evaluations'),
        (admin, '/system', 'System Administration'),
        (auth, '/auth', 'Authentication & User Management')
    ]
    
    for blueprint, prefix, description in blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)
        app.logger.info(f'  ✔ {blueprint.name} ({prefix}): {description}')


def _log_startup_info(app):
    """Log application startup information."""
    app.logger.info('=' * 60)
    app.logger.info('🏀 BALLWATCH BASKETBALL ANALYTICS API')
    app.logger.info('🚀 Server Ready!')
    app.logger.info('=' * 60)


if __name__ == '__main__':
    application = create_app()
    application.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 4000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )