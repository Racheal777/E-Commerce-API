from datetime import datetime


from .. import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'


    id = db.Column(db.String(50, primary_key= True, nullable = False, unique = True))
    email = db.Column(db.String(255),  nullable = False, unique = True)
    first_name = db.Column(db.String(255),  nullable = False)
    last_name =  db.Column(db.String(255),  nullable = False)
    _password =   db.Column(db.String(255),  nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.now())




    def password_hash(self, password):
        password_hashed = bcrypt.generate_password_hash(password)
        self._password = password_hashed

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password)



    def to_dict(self):
        return {c.name: str(getattr(self, c.name))  for c in self.__table__.columns}


    def __repl__(self):
        return f"f<Email: {self.email}>"