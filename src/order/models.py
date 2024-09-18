from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .. import db
import uuid

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates= "order_items")


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_date = db.Column(db.Date(), nullable=False, default=datetime.utcnow().date)
    order_number = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    customer_mobile = db.Column(db.String(), nullable=False)
    customer_email = db.Column(db.String(), nullable=False)
    customer_name = db.Column(db.String(), nullable=False)
    note = db.Column(db.Text())
    sub_total = db.Column(db.Float())
    total_amount_due = db.Column(db.Float())
    amount_paid = db.Column(db.Float())
    payment_status = db.Column(db.String(), default='pending', nullable=False)
    has_delivery = db.Column(db.Boolean(), default=False, nullable=False)
    is_fulfilled = db.Column(db.Boolean(), default=False, nullable=False)
    delivery_fee = db.Column(db.Float(), default=0.0, nullable=False)
    country = db.Column(db.String(), nullable=False)
    region = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    longitude = db.Column(db.String())
    latitude = db.Column(db.String())
    payment_reference = db.Column(db.String(255), unique=True, nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    order_status = db.Column(db.String(), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    user = relationship('User', back_populates='orders')

    def formatted_order_number(self):
        return f"ORD{self.order_number:04d}"

    def __repr__(self):
        return f"<Order {self.order_number}>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_date': self.order_date.isoformat(),
            'order_number': self.order_number,
            'customer_mobile': self.customer_mobile,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'note': self.note,
            'sub_total': self.sub_total,
            'total_amount_due': self.total_amount_due,
            'amount_paid': self.amount_paid,
            'payment_status': self.payment_status,
            'has_delivery': self.has_delivery,
            'is_fulfilled': self.is_fulfilled,
            'delivery_fee': self.delivery_fee,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'user_id': str(self.user_id),
            'order_status': self.order_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }