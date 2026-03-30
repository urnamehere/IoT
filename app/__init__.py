"""IoT Security Research Learning Tool - Flask Application Factory."""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        from config import Config
        app.config.from_object(Config)

    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from app.routes import main
    app.register_blueprint(main)

    from app.content_loader import content
    app.register_blueprint(content)

    with app.app_context():
        db.create_all()

    return app
