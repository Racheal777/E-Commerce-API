import uuid
from uuid import UUID
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload
from marshmallow import Schema, fields

from .models import Cart
from .. import app, db, User
from ..products.models import Product
from ..utils import create_response, sqlalchemy_obj_to_dict


class ProductSchema(Schema):
    class Meta:
        model = Product
        load_instance = True



class CartSchema(Schema):
    quantity = fields.Integer(required=True)
    product_id = fields.UUID(required=True)
    class Meta:
        model = Cart
        include_fk = True
        load_instance = True
        # fields = (
        # 'id', 'name', 'description', 'price', 'product_image', 'stock_quantity')
    product = fields.Nested(ProductSchema)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
cart_schema = CartSchema()
carts_schema = CartSchema(many=True)


def get_total(price, quantity):
    total_array = []

    total_price_per_quantity = price * quantity
    total_array.append(total_price_per_quantity)
    return round(sum(total_array), 2)


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

        carts = Cart.query.options(joinedload(Cart.product)).filter_by(user_id=user.id).order_by(Cart.created_at).all()

        result = carts_schema.dump(carts)
        overall_total = 0
        for item in result:
            if not item['product']:
                product = Product.query.get(uuid.UUID(item['product_id']))

                if product:
                    item['product'] = sqlalchemy_obj_to_dict(product)

            item_total = get_total(item['product']['price'], item['quantity'])
            item['total'] = item_total
            print(item_total)
            overall_total += item_total


        response_data = {
            'cart_items': result,
            'overall_total': overall_total
        }

        return create_response(data=response_data, message='cart record retrieved successfully', status=200)

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
