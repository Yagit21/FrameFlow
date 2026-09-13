from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "uevhasdhavd7e"
    
    #Storing SQLite database in the project folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mocap.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Connect SQLAlchemy to this Flask application
    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes)
    
    from .auth import auth
    app.register_blueprint(auth)
    
    #Import models
    from . import models

    #Create database tables
    with app.app_context():
        db.create_all()

    return app