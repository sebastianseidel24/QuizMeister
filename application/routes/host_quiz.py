from quizmeister import app
from flask import render_template
import sqlite3

@app.route("/hostquiz/<int:quiz_id>")
def hostquiz(quiz_id):
    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT * FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz == None:
        return "Quiz nicht gefunden.", 404
    else:
        return render_template("hostquiz.html", quiz=quiz, questions=questions)