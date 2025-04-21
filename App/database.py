from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

def get_migrate(app):
    return Migrate(app, db)

def create_db():
    db.create_all()
    
def init_db(app):
    db.init_app(app)

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('App.config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register Blueprints HERE
    from App.views.user import student_views  # Adjust the import path
    app.register_blueprint(student_views, url_prefix='/student')

    return app