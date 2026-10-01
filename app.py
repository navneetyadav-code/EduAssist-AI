import os
from flask import Flask, render_template
from extensions import db
from dotenv import load_dotenv

load_dotenv(override=True)

def create_app():
    # Initialize Flask app. We point static_folder to 'assets' and template_folder to 'views'
    app = Flask(__name__, static_folder='assets', template_folder='views')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this-in-production')
    
    # Database config: use SQLite in the local folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_dir = os.path.join(basedir, 'database')
    os.makedirs(db_dir, exist_ok=True)  # Auto-create the database folder if missing
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Optimize SQLite for concurrency: Wait up to 20 seconds instead of throwing "locked" errors instantly
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'timeout': 20
        }
    }
    
    # Configure cross-origin cookies so GitHub Pages can remember the user's session
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True

    # Initialize extensions
    db.init_app(app)
    
    # Enable CORS so GitHub Pages can make requests to this backend
    from flask_cors import CORS
    CORS(app, supports_credentials=True)

    # Enable WAL (Write-Ahead Logging) mode for SQLite to allow simultaneous readers and writers
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        # Only run this if the connection is actually SQLite (so it won't crash when you switch to MySQL later)
        if type(dbapi_connection).__module__ == "sqlite3":
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    # Import models here so they are registered with SQLAlchemy
    import models

    # Register blueprints
    from routes_api import api
    from routes_admin import admin_bp
    
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
