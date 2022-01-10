import hashlib
import uuid
from flask import make_response, redirect, url_for, request, render_template, Blueprint
from models.settings import db
from models.user import User

auth_handlers = Blueprint("auth", __name__)


@auth_handlers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    
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
                response = make_response(redirect(url_for('topic.index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')
                
                return response
            else:
                return "The password you entered is incorrect!"
            
            
@auth_handlers.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    
    elif request.method == "POST":
        email_address = request.form.get("email-address")
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")
        
        if password != repeat:
            return "The two entered passwords don't match. Please try again."
        
        user = User(username=username,
                    password_hash=hashlib.sha256(password.encode()).hexdigest(), 
                    session_token=str(uuid.uuid4()),
                    email_address=email_address)
        db.add(user)  # Add to the transaction (user is not yet in the database)
        db.commit()  # Commit the transaction into the database
        
        # Save the user's session token into a cookie
        # HttpOnly and SameSite settings in a cookie provide greater security
        # against attacks. httponly=True means that cookie cannot be accessed via
        # Javascript. samesite='Strict' demands that that the cookie sender and
        # receiver are on the same site. Thirdly you can also add secure=True, which
        # would mean cookies can only be sent via HTTPS. But beware that this would
        # mean cookies would not work on localhost, because your localhost uses HTTP.
        response = make_response(redirect(url_for("topic.index")))
        response.set_cookie("session_token", user.session_token, httponly=True,
                            samesite='Strict')
        
        return response