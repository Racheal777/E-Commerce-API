
from flask_sqlalchemy import SQLAlchemy
from dotenv import  load_dotenv
from flask import Flask
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restx import Api, Resource
# from flask_restplus import Api, resource

load_dotenv()

host = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

app = Flask(__name__)

api = Api(app, version='1.0', title='E-Commerce API',
    description='An E-commerce API',
)

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@{host}:{port}/{database}"
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

from .users.models import User
from .products.models import Product
from .carts.models import Cart
from .order.models import Order, OrderItem

from .users.controllers import  *
from .products.controllers import *
from .carts.controllers import *
from .order.controllers import *

if __name__ == 'main':
    app.run(debug=True)







