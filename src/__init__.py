
from flask_sqlalchemy import SQLAlchemy
from dotenv import  load_dotenv
from flask import Flask
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

load_dotenv()



host = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@{host}:{port}/{database}"
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)


from .users.models import User
from .products.models import Product

from .users.controllers import  *
from .products.controllers import *

if __name__ == 'main':
    app.run(debug=True)







