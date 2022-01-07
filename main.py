import hashlib
import uuid
from flask import Flask, render_template, request, redirect, url_for, make_response
from models.user import User
from models.settings import db
from models.topic import Topic

app = Flask(__name__)

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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Get password hash out of password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Get user from the db by his/her username and password
        user = db.query(User).filter_by(username=username).first()
        
        if not user:
            return "This user doesn't exist!"
        
        else:
            # If the user exists, check if the password hashes match
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())
                db.add(user)
                db.commit()
                
                # Save the user's session token into a cookie
                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')
                
                return response
            else:
                return "The password you entered is incorrect!"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")
        
        if password != repeat:
            return "The two entered passwords don't match. Please try again."
        
        user = User(username=username,
                    password_hash=hashlib.sha256(password.encode()).hexdigest(), 
                    session_token=str(uuid.uuid4()))
        db.add(user)  # Add to the transaction (user is not yet in the database)
        db.commit()  # Commit the transaction into the database
        
        # Save the user's session token into a cookie
        # HttpOnly and SameSite settings in a cookie provide greater security
        # against attacks. httponly=True means that cookie cannot be accessed via
        # Javascript. samesite='Strict' demands that that the cookie sender and
        # receiver are on the same site. Thirdly you can also add secure=True, which
        # would mean cookies can only be sent via HTTPS. But beware that this would
        # mean cookies would not work on localhost, because your localhost uses HTTP.
        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", user.session_token, httponly=True,
                            samesite='Strict')
        
        return response


@app.route("/topic-create", methods=["GET", "POST"])
def topic_create():
    # Get the current user (author)
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if request.method == "GET":
        return render_template("topic_create.html", user=user)
    
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        
        # Only logged in users can create a topic
        if not user:
            return redirect(url_for('login'))
        
        # Create a topic object
        topic = Topic.create(title=title, text=text, author=user)
        
        return redirect(url_for('index'))


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

# This is just a regular way to run some Python files safely
if __name__ == '__main__':
    app.run()
