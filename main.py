import uuid
import os
import smartninja_redis
from flask import Flask, render_template, request, redirect, url_for, make_response
from models.user import User
from models.settings import db
from models.topic import Topic
from handlers.auth import auth_handlers

redis = smartninja_redis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)
app.register_blueprint(auth_handlers)

db.create_all()


@app.route('/')
def index():
    # Check if the user is authenticated based on the session_token
    session_token = request.cookies.get("session_token")
    
    # Query.first() returns the first of a potentially larger set, or None
    # if there were no results.
    user = db.query(User).filter_by(session_token=session_token).first()
    
    # Get all the topics from the db
    topics = db.query(Topic).all()
    
    return render_template("index.html", user=user, topics=topics)


@app.route("/topic-create", methods=["GET", "POST"])
def topic_create():
    # Get the current user (author)
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    
    if not user:
            return redirect(url_for('login'))
        
    if request.method == "GET":
        # Create a csrf token
        csrf_token = str(uuid.uuid4())
        
        # Store the csrf token into Redis for that specific user
        redis.set(name=csrf_token, value=user.username)
        # Senc the csrf token into the html template
        return render_template("topic_create.html", user=user, csrf_token=csrf_token)
    
    elif request.method == "POST":
        # CSRF from HTML
        csrf = request.form.get("csrf")
        # Username value stored under the csrf name from redis
        redis_csrf_username = redis.get(name=csrf).decode()
        
        if redis_csrf_username and redis_csrf_username == user.username:               
            title = request.form.get("title")
            text = request.form.get("text")
                    
            # Create a topic object
            topic = Topic.create(title=title, text=text, author=user)
            
            return redirect(url_for('index'))
        
        else:
            return "The CSRF token is invalid!"


@app.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    
    return render_template("topic_details.html", topic=topic, user=user)


@app.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    
    if request.method == "GET":
        return render_template("topic_edit.html", topic=topic)
    
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        
        if not user:
            return redirect(url_for('login'))
        
        elif topic.author.id != user.id:
            return "You can't edit other people's posts!"
        
        else:
            # Update the topic
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()
            
            return redirect(url_for('topic_details', topic_id=topic_id))
        

@app.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    
    if request.method == "GET":
        return render_template("topic_delete.html", topic=topic)
    
    elif request.method == "POST":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        
        if not user:
            return redirect(url_for('login'))
        
        elif topic.author.id != user.id:
            return "You can't delete other people's posts!"
        
        else:
            db.delete(topic)
            db.commit()
            
            return redirect(url_for('index'))

# This is just a regular way to run some Python files safely
if __name__ == '__main__':
    app.run()
