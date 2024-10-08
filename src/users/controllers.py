from crypt import methods
from datetime import timedelta

from .models import db, User
from flask import request, jsonify, make_response, Blueprint
from .. import create_app, bcrypt
from ..utils import create_response
from marshmallow import Schema, fields, ValidationError
from flask_jwt_extended import create_access_token



users_bp = Blueprint('users', __name__)

class UserSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Boolean()

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class LoginSchema(Schema):

    email = fields.Email(required=True)
    password = fields.Str(required=True)


@users_bp.route('/users/signup', methods=['POST'])

def signup():

    try:
        # logger.info("Starting user signup process")
        schema = UserSchema()
        try:
            data = schema.load(request.get_json())
            # logger.debug(f"Received user data: {data}")
        except ValidationError as e:
            # logger.warning(f"Validation error during signup: {e.messages}")
            return jsonify(e.messages), 400

        user = User()
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user._password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        user.role = data.get('role')

        # logger.info(f"Attempting to create new user with email: {user.email}")

        existing_user = User.query.filter(User.email == user.email).first()

        if existing_user:
            # logger.info(f"User with email {user.email} already exists")
            return jsonify({
                'message': 'User with this email already exists',
                'status': 409
            }), 409
        else:
            # logger.info(f"Creating new user with email: {user.email}")
            db.session.add(user)
            db.session.commit()
            # logger.info(f"User {user.email} successfully created")

            return create_response(data=user_schema.dump(user), message='User registration successful', status=201)

    except Exception as e:
        # logger.error(f"Error during user signup: {str(e)}", exc_info=True)
        return create_response(error=str(e), message='error', status=500)



@users_bp.route('/users/login', methods=['POST'])
def login():
    try:
        schema = LoginSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as e:
            return jsonify(e.messages),400

        email = data.get('email')
        existing_user = User.query.filter(User.email == email).first()

        if not existing_user:
            return jsonify({
                'message': 'User with this email does not exists',
                'status': 404
            }), 404
        else:
            password = data.get('password')
            is_valid = bcrypt.check_password_hash(existing_user._password, password)

            if not is_valid:
                return jsonify({
                    'message': 'Invalid Credentials',
                    'status': 401
                }), 401

            expires = timedelta(hours=72)
            access_token = create_access_token(identity=existing_user.id,expires_delta=expires)

            return create_response(data={'user': user_schema.dump(existing_user),
            'access_token': access_token}, message='User login successfully', status=200)

    except Exception as e:
        return create_response(error=str(e), message='error', status=500)



