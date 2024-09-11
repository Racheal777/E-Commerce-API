from crypt import methods

from models import db, User, Roles
from flask import request, jsonify, make_response
from .. import create_app, app
from marshmallow import Schema, fields, ValidationError


class UserSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)



@app.route('/users/signup', methods=['POST'])
def Signup():
    try:
        schema = UserSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as e:
            return jsonify(e.messages),400

        user = User()
        user.email = data.get('email')
        user.first_name = data.get('firstName')
        user.last_name = data.get('lastName')
        user._password = data.get('password')

        existing_user = User.query.filter(User.email == user.email).first()

        if not existing_user:
            return jsonify({
                'message': 'User with this email already exists',
                'status': 409
            }), 409
        else:
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201

    except Exception as e:
        return jsonify({'errors': str(e)}), 500