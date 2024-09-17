from datetime import datetime


from .. import db, bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product_image = db.Column(db.String(255), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart_items = db.relationship('Cart', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')

    def __repr__(self):
        return f"<Product {self.name}>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': self.price,
            'image_url': self.product_image,
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
