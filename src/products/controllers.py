from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
import os

from config import upload_file
from .models import db, Product
from flask import request, jsonify, make_response
from .. import app, bcrypt, User


@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)


        if not user or not user.role:
            return jsonify({
                'message': 'Unauthorized',
                'status': 401
            }), 401

        # Handle form data
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')

        print(stock_quantity)

        # Validate data
        if not all([name, description, price, stock_quantity]):
            return jsonify({'message': 'Missing required fields'}), 400

        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
        except ValueError:
            return jsonify({'message': 'Invalid price or stock quantity'}), 400

        # Handle file upload
        if 'image' not in request.files:
            return jsonify({'message': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            image_url = upload_file(file)
        else:
            return jsonify({'message': 'Invalid file type'}), 400

        # Create product
        product = Product(
            name=name,
            slug=f"{name}-{price}".lower().replace(' ', '-'),
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            product_image=image_url
        )

        db.session.add(product)
        db.session.commit()

        return jsonify(product.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding product: {str(e)}")
        return jsonify({'message': 'An error occurred while adding the product'}), 500


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS