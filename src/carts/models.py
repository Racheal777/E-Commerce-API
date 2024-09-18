
from datetime import datetime
from .. import db, bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', back_populates='cart_items')
    user = db.relationship('User', back_populates='cart_items')

    def __repr__(self):
        return f"<Cart {self.name}>"

