from models.settings import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    session_token = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.now)

