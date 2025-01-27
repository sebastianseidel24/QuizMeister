from application import app
from flask import render_template

# An einem Quiz teilnehmen
@app.route("/playquiz")
def play_quiz():
    return render_template("playquiz.html")