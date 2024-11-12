from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    username = db.Column(db.Text,
                         nullable=False,
                         unique=True)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    @classmethod
    def register(cls, username, pwd):

        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, pwd):

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False
        
class Outfit(db.Model):
    __tablename__ = "outfits"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.Text,
                     nullable=False)
    
    outfit_desc = db.Column(db.JSON,
                            nullable=False)
    
    image_url = db.Column(db.Text,
                          nullable=False)
    
    user = db.relationship("User", backref="outfits")