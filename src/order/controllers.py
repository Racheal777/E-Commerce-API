import os

from datetime import datetime
from dotenv import load_dotenv
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..task import send_order_email, send_payment_email
from .models import Order, OrderItem
from marshmallow import Schema, fields,  ValidationError
from .. import   db

from ..products.models import Product
import requests

from ..users.models import User
from ..utils import create_response

load_dotenv()



orders_bp = Blueprint('orders', __name__)

class OrderItemSchema(Schema):
    id = fields.UUID(dump_only=True)
    product_id = fields.UUID(required=True)
    quantity = fields.Integer(required=True )


class OrderSchema(Schema):
    id = fields.UUID(dump_only=True)
    order_date = fields.Date(dump_only=True)
    order_number = fields.Integer(dump_only=True)
    customer_mobile = fields.String(required=True )
    customer_email = fields.Email()
    customer_name = fields.String()
    note = fields.String(allow_none=True)
    sub_total = fields.Float(dump_only=True)
    total_amount_due = fields.Float(dump_only=True)
    amount_paid = fields.Float()
    payment_status = fields.String(dump_only=True)
    has_delivery = fields.Boolean(required=True)
    is_fulfilled = fields.Boolean(dump_only=True)
    delivery_fee = fields.Float()
    country = fields.String(required=True)
    region = fields.String(required=True)
    city = fields.String()
    longitude = fields.String()
    latitude = fields.String()
    user_id = fields.UUID()
    order_status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    items = fields.Nested(OrderItemSchema, many=True, required=True, )

orders = OrderSchema()


@orders_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return create_response(error='Unauthorized', message="Unauthorized", status=401)

        schema = OrderSchema()
        try:
            data = schema.load(request.get_json())
            print(f"cus {data}")
        except ValidationError as e:
            return create_response(error=str(e), message="Bad request", status=400)

        new_order = Order(
            customer_mobile=data['customer_mobile'],
            customer_email=user.email,
            customer_name=f"{user.first_name} {user.last_name}",
            note=data.get('note'),
            has_delivery=data['has_delivery'],
            delivery_fee = data.get('delivery_fee'),
            country=data['country'],
            region=data['region'],
            city=data.get('city'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            user_id=user.id,

        )

        db.session.add(new_order)

        try:
            db.session.flush()


        except Exception as e:

            db.session.rollback()
            return create_response(error=str(e),message="An error occurred while creating the order", status=500)

        sub_total = 0


        for item in data['items']:

            product_id = item['product_id']


            product = Product.query.filter(Product.id == product_id).first()

            if not product:
                print(f' product stock {product.stock_quantity}')

                return create_response(error=f"Product with id {item['product_id']} not found", message="Product not found", status=404)

            if product.stock_quantity < item['quantity']:

                return create_response(error=f"Insufficient stock for product {product.name}", message="Insufficient stock", status=400)

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],

            )
            db.session.add(order_item)
            product.stock_quantity -= item['quantity']
            sub_total += product.price * item['quantity']

        new_order.sub_total = sub_total

        new_order.total_amount_due = sub_total + new_order.delivery_fee
        db.session.commit()

        # send_order_email.delay(new_order.id, new_order.customer_email)

        response, status = checkout(new_order.id)
        payment_data = response.json


        return create_response(data={"order_id": str(new_order.id), "order_number": new_order.order_number, 'payment': payment_data['data']},
                               message="Order created successfully", status=201)

    except Exception as e:
        db.session.rollback()
        return create_response(error=str(e), message="An error occurred", status=500)





def checkout(order_id):
    try:
        order = Order.query.filter(Order.id == order_id).first()
        if not order:
            return jsonify({
                "error": "Order not found",
                "message": "The specified order does not exist",
                "status": 404
            }), 404

        headers = {
            "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET')}"

        }
        data = {
            "amount": int(round(order.total_amount_due) * 100),
            "currency": "GHS",
            "email": order.customer_email,


        }

        try:
            transaction = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)

            response = transaction.json()
            auth = response['data']
            order.payment_reference = auth['reference']

            db.session.commit()
            return jsonify({
                "data": auth,
                "message": "success",
                "status": 200
            }), 200

        except requests.RequestException as e:
            return jsonify({
                "error": str(e),
                "message": "Error while trying to make payment",
                "status": 500
            }), 500

    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An unexpected error occurred",
            "status": 500
        }), 500



@orders_bp.route('/paystack/callback', methods=['POST'])
def callback_payment():
    try:
        payload = request.json
        if not payload or 'event' not in payload:
            return jsonify({'status': 'failed', 'message': 'Invalid payload'}), 400

        ref = payload['data']['reference']


        url = f'https://api.paystack.co/transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET')}"

        }

        try:
            transaction = requests.get(url,  headers=headers)

            response = transaction.json()
            verification = response['data']

            if verification['data']['status'] == 'success':
                order = Order.query.filter_by(payment_reference=ref).first()

                if order and order.order_status == 'pending':
                    order.payment_status = 'success'
                    order.amount_paid = verification['data']['amount'] / 100
                    db.session.commit()

                    # send_payment_email.delay(order.id, order.customer_email)

                    return jsonify({'status': 'success', 'message': 'Payment verified and order updated'}), 200
                else:
                    return jsonify({'status': 'failed', 'message': 'Order not found'}), 404
            else:
                return jsonify({'status': 'failed', 'message': 'Payment verification failed'}), 400



        except Exception as e:
            db.session.rollback()
            return jsonify({'status': str(e), 'message': 'An unexpected error occurred'}), 500


    except Exception as e:
        db.session.rollback()
        return jsonify({'status': str(e), 'message': 'An unexpected error occurred'}), 500




@orders_bp.route('/update-order/<order_number>',  methods = ['PATCH'])
def update_order(order_number):
    try:
        order = Order.query.filter(Order.order_number == order_number).first()

        data = request.get_json()
        status = data.get('status')

        order.order_status = status
        order.is_fulfilled = True
        order.updated_at = datetime.utcnow

        db.session.commit()

        return create_response(data=order, message='successfully updated the order', status=200)

    except Exception as e:
        db.session.rollback()
        return create_response(error=str(e), message="An error occurred", status=500)











