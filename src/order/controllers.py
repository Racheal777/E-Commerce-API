
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import Order, OrderItem
from marshmallow import Schema, fields,  ValidationError
from .. import app, create_response, User, db
from ..carts.controllers import get_total
from ..products.models import Product


class OrderItemSchema(Schema):
    id = fields.UUID(dump_only=True)
    product_id = fields.UUID(required=True)
    quantity = fields.Integer(required=True )
    price_at_time = fields.Float(dump_only=True)



class OrderSchema(Schema):
    id = fields.UUID(dump_only=True)
    order_date = fields.Date(dump_only=True)
    order_number = fields.Integer(dump_only=True)
    customer_mobile = fields.String(required=True )
    customer_email = fields.Email(required=True)
    customer_name = fields.String(required=True, )
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


@app.route('/orders', methods=['POST'])
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
            customer_email=data['customer_email'],
            customer_name=data['customer_name'],
            note=data.get('note'),
            has_delivery=data['has_delivery'],
            country=data['country'],
            region=data['region'],
            city=data.get('city'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            user_id=user.id,
            order_number = generate_order_number()
        )

        db.session.add(new_order)
        print(f' product {new_order}')
        # db.session.flush()

        sub_total = 0
        print(f' product {sub_total}')
        for item in data['items']:
            product = Product.query.get(item['product_id'])
            print(f' product {product}')
            if not product:
                db.session.rollback()
                return create_response(error=f"Product with id {item['product_id']} not found", message="Product not found", status=404)

            if product.stock_quantity < item['quantity']:
                print(f' product {product}')
                db.session.rollback()
                return create_response(error=f"Insufficient stock for product {product.name}", message="Insufficient stock", status=400)

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price_at_time=product.price
            )
            db.session.add(order_item)
            product.stock_quantity -= item['quantity']

            sub_total += product.price * item['quantity']

            print(f' sub {sub_total}')

        new_order.sub_total = sub_total
        print(f' sub {new_order.sub_total}')


        new_order.total_amount_due = sub_total + new_order.delivery_fee
        print(f' sub {new_order.total_amount_due}')
        db.session.commit()

        return create_response(data={"order_id": str(new_order.id), "order_number": new_order.order_number},
                               message="Order created successfully", status=201)

    except Exception as e:
        db.session.rollback()
        return create_response(error=str(e), message="An error occurred", status=500)



def generate_order_number():
    last_order = Order.query.order_by(Order.id.desc()).first()
    if last_order:
        return f"ORD-{int(last_order.order_number.split('-')[1]) + 1:06d}"
    return "ORD-000001"