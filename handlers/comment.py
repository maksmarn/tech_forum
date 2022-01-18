from flask import render_template, request, redirect, Blueprint, url_for

from models.settings import db
from models.topic import Topic
from models.user import User
from models.comment import Comment

from utils.redis_helper import create_csrf_token, validate_csrf

comment_handlers = Blueprint("comment", __name__)


# The handler only accepts post requests because the html form for creating
# a new comment will be in another (existing) HTML template.
@comment_handlers.route("/topic/<topic_id>/create-comment", methods=["POST"])
def comment_create(topic_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    
    if not user:
        return redirect(url_for("auth.login"))
    
    # CSRF from HTML
    csrf = request.form.get("csrf")
    
    if validate_csrf(csrf, user.username):
        text = request.form.get("text")
        
        # Query the topic object from the database
        topic = db.query(Topic).get(int(topic_id))
        
        # Create a Comment object
        comment = Comment.create(topic=topic, text=text, author=user)
        
        return redirect(url_for('topic.topic_details', topic_id=topic_id, csrf_token=create_csrf_token(user.username)))
    else:
        return "Your CSRF token is invalid!"
    

@comment_handlers.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def comment_edit(comment_id):
    comment = db.query(Comment).get(int(comment_id))

    
    if request.method == "GET":
        return render_template("comment/comment_edit.html", comment=comment)

    elif request.method == "POST":
        text = request.form.get("text")
        
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        
        if not user:
            return redirect(url_for('auth.login'))
        
        elif comment.author.id != user.id:
            "You can't edit other people's comments!"
            
        else:
            comment.text = text
            db.add(comment)
            db.commit()
            
            return redirect(url_for('topic.index'))
        

@comment_handlers.route("/comment/<comment_id>/delete", methods=["GET", "POST"])
def comment_delete(comment_id):
    comment = db.query(Comment).get(int(comment_id))

    
    if request.method == "GET":
        return render_template("comment/comment_delete.html", comment=comment)

    elif request.method == "POST":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        
        if not user:
            return redirect(url_for('auth.login'))
        
        elif comment.author.id != user.id:
            return "You can't delete other people's comments!"
        
        else:
            db.delete(comment)
            db.commit()
            
            return redirect(url_for('topic.index'))
    