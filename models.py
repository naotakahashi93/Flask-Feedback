from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username =  db.Column(db.String(20), primary_key=True, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    # feedback = db.relationship("Feedback",backref="user")

    @classmethod
    def register(cls, username, pwd, email, first, last):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username, hashed pwd, emai, first and last name
        return cls(username=username, password=hashed_utf8, email=email, first_name=first, last_name=last)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Return user if valid; else return False."""
        u = User.query.filter_by(username=username).first() ## checking db and filtering by the username that was passed in and getitng the first query

        if u and bcrypt.check_password_hash(u.password, pwd): ## checking to see if the "u" exists AND if the hashed pw from the "u" matches the pwd they typed in
            # return user instance if true
            return u 
        else:
            return False


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title =  db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey("users.username"), nullable=False) ## foreign key from usernames in the users table
    
    user = db.relationship("User", backref="feedback") ## setting up relationship between users and feedback models, you can access .user on a Feedback instance and backref so we can access .feedback in a Users instance

