
from flask_sqlalchemy import SQLAlchemy
from dotenv import  load_dotenv
from flask import Flask
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_mail import Mail
from task import make_celery
import mailings


load_dotenv()

host = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port = os.getenv('DB_PORT')

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

app = Flask(__name__)

mail = Mail(app)
api = Api(app, version='1.0', title='E-Commerce API',description='An E-commerce API')

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@{host}:{port}/{database}"
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'


db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
jwt = JWTManager(app)



import mailings
celery = make_celery(app)
celery.conf.update(app.config)

celery.autodiscover_tasks(['mailings'])

celery.conf.broker_connection_retry_on_startup = True

from .users.models import User
from .products.models import Product
from .carts.models import Cart
from .order.models import Order, OrderItem
import mailings

from .users.controllers import  *
from .products.controllers import *
from .carts.controllers import *
from .order.controllers import *

if __name__ == 'main':
    app.run(debug=True)







