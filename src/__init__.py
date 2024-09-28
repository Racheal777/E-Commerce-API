
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_mail import Mail
from dotenv import load_dotenv
import os


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()
api = Api(version='1.0', title='E-Commerce API', description='An E-commerce API')

def create_app():
    app = Flask(__name__)


    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.getenv('USERNAME')}:{os.getenv('PASSWORD')}@{os.getenv('HOSTNAME')}:{os.getenv('DB_PORT')}/{os.getenv('DATABASE')}"
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['broker_url'] = 'amqp://guest:guest@localhost:5672//'
    app.config['result_backend'] = 'rpc://'



    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    api.init_app(app)


    # Initialize Celery
    # init_celery(app)
    from .task import init_celery
    init_celery(app)

    # Import and register blueprints
    from .users.controllers import users_bp
    from .products.controllers import products_bp
    from .carts.controllers import carts_bp
    from .order.controllers import orders_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(orders_bp)




    return app

# Import models

from .users.models import User
from .products.models import Product
from .carts.models import Cart
from .order.models import Order, OrderItem



# if __name__ == 'main':
#     app.run(debug=True)
