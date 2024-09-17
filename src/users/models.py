from datetime import datetime
from email.policy import default

from .. import db, bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    _password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Boolean(), default = False, nullable =False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('Cart', back_populates='user')
    orders = db.relationship('Order', back_populates='user')


    def to_dict(self):
        return {
            'id': str(self.id),
            'firstname': self.first_name,
            'lastname': self.last_name,
            'email': self.email,
            'role': self.role
        }

    def __repr__(self):
        return f"<User: {self.email}>"


