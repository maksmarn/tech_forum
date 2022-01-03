from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Handler 1
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    elif request.method == "POST":
        name = request.form.get("your-name")
        return f"Hello {name}!"


# Handler 2
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
        
        print(username)
        print(password)
        print(repeat)
        
        return redirect(url_for('index'))


# Handler 3
@app.route('/about')
def about():
    return 'Something about me'


# This is just a regular way to run some Python files safely
if __name__ == '__main__':
    app.run()
