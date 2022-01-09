from models.settings import db
from datetime import datetime


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    text = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")  # Not a real field, just shows a relationship with the user model
    created = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def create(cls, title, text, author):
        topic = cls(title=title, text=text, author=author)
        db.add(topic)
        db.commit()
        
        return topic
