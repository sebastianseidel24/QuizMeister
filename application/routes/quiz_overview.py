from application import app
from flask import render_template, session
import sqlite3

# Von User erstellte Quiz anzeigen
@app.route("/quizoverview")
def quiz_overview():
    user_id = session["user_id"]

    with sqlite3.connect("quizzy.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM quizzes WHERE user_id = (?)", (user_id,))
        quizzes = cur.fetchall()
    
    return render_template("quizoverview.html", quizzes=quizzes)
