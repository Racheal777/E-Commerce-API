from itertools import product
from uuid import UUID

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from .models import Cart
from .. import app, db, User
from ..products.models import Product
from ..utils import create_response


@app.route('/carts', methods=['Post'])
@jwt_required()
def add_cart():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return create_response(error='Unauthorized', message="Unauthorized",
                                   status=401)

        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        user_id = user.id

        if not all([product_id, quantity]):
            return create_response(error='Missing required fields', message="Missing required fields",
                                   status=400)

        cart = Cart.query.filter_by(user_id=user.id, product_id=product_id).first()

        if cart:
            cart.quantity += quantity
            db.session.commit()
            return create_response(data=cart, message='Cart updated successfully', status=200)

        cart = Cart(
            product_id=product_id,
            quantity=quantity,
            user_id=user_id
        )

        db.session.add(cart)
        db.session.commit()
        return create_response(data=cart, message='cart added successfully', status=201)

    except Exception as e:

        app.logger.error(f"Error adding/updating cart: {str(e)}")
        return create_response(error=str(e), message="An error occurred while adding/updating cart", status=500)


@app.route('/carts', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return create_response(error='Unauthorized', message="Unauthorized",
                                   status=401)

        carts = Cart.query.options(joinedload(Cart.user)).filter_by(user_id=user.id).order_by(Cart.created_at).all()

        return create_response(data=carts, message='cart record retrieved successfully', status=200)

    except Exception as e:

        app.logger.error(f"Error retrieving cart: {str(e)}")
        return create_response(error=str(e), message="An error occurred while returning cart", status=500)


@app.route('/carts/<cart_id>', methods=['PATCH'])
@jwt_required()
def update_cart(cart_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return create_response(error='Unauthorized', message="Unauthorized",
                                   status=401)

        data = request.get_json()
        quantity = data.get('quantity')
        product_id = data.get('product_id')

        cart = Cart.query.filter_by(id=cart_id, user_id=user.id, product_id=product_id).first()

        if cart is None:
            return create_response(error="Cart not found", message="Cart not found", status=404)

        if quantity is not None:
            cart.quantity = quantity

        db.session.commit()

        return create_response(data=cart, message='cart record updated successfully', status=200)

    except Exception as e:
        app.logger.error(f"Error adding cart: {str(e)}")
        return create_response(error=str(e), message="An error occurred while updating cart", status=500)


@app.route('/carts/<string:cart_id>', methods=['DELETE'])
@jwt_required()
def delete_cart(cart_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return create_response(error='Unauthorized', message="Unauthorized",
                                   status=401)

        cart = Cart.query.filter_by(id=cart_id, user_id=user.id).first()

        if cart is None:
            return create_response(error="Cart not found", message="Cart not found", status=404)

        db.session.delete(cart)
        db.session.commit()

        return create_response(data=cart, message='cart record retrieved successfully', status=200)

    except Exception as e:

        app.logger.error(f"Error adding cart: {str(e)}")
        return create_response(error=str(e), message="An error occurred while adding cart", status=500)
