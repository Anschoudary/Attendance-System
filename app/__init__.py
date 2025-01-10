from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sxcbvNm54'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'  # SQLite database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Register Blueprints (to keep routes modular)
    from .routes import main
    app.register_blueprint(main)
    migrate = Migrate(app, db)
    app.app_context().push()
    db.create_all()

    return app
