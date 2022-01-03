from flask import Flask, render_template, request

app = Flask(__name__)

# Handler 1
@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "GET":
        return render_template("index.html")
    
    elif request.method == "POST":
        name = request.form.get("your-name")
        return f"Hello {name}!"


# Handler 2
@app.route("/second-handler", methods=["GET"])
def second_handler():
    return "Here's the second handler"


# Handler 3
@app.route('/about')
def about():
    return 'Something about me'


# This is just a regular way to run some Python files safely
if __name__ == '__main__':
    app.run()
