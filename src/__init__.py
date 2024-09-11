
from flask_sqlalchemy import SQLAlchemy
from dotenv import  load_dotenv
from flask import Flask
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

load_dotenv()



host = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')

app = Flask(__name__)

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from src.users.models import User, UserRoles, Roles

    return app







