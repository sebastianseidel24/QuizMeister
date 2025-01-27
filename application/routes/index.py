from application import app
from flask import render_template, session

# Startseite
@app.route("/")
def index():
    username = session["username"]
    return render_template("index.html", username=username)