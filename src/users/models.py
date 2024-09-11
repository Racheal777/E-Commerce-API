from datetime import datetime
from .. import db, bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID



class User(db.Model):
    __tablename__ = 'users'


    id =  db.Column(UUID(as_uuid=True), primary_key=True, default=uuid, unique=True)
    email = db.Column(db.String(255),  nullable = False, unique = True)
    first_name = db.Column(db.String(255),  nullable = False)
    last_name =  db.Column(db.String(255),  nullable = False)
    _password =   db.Column(db.String(255),  nullable = False)

    created_at = db.Column(db.DateTime, default=datetime.now())
    roles = db.relationship('Role', secondary='user_roles', back_populates = 'users')




    def password_hash(self, password):
        password_hashed = bcrypt.generate_password_hash(password)
        self._password = password_hashed

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password)



    def to_dict(self):
        return {c.name: str(getattr(self, c.name))  for c in self.__table__.columns}


    def __repl__(self):
        return f"f<Email: {self.email}>"


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    users = db.relationship('User', secondary='user_roles', back_populates='roles')


#User role association model
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete = 'CASCADE'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id', ondelete='CASCADE'))


