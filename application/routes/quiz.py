from quizmeister import app
from flask import render_template, session
import sqlite3
from application.quiz_sessions import quiz_sessions

@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):

    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT * FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz != None and quiz[3] == session["user_id"]:
        
        # Prüfen ob Session bereits existiert
        session_active = False
        for quiz_session in quiz_sessions:
            if quiz_sessions[quiz_session]["quiz_id"] == quiz_id:
                session_active = True
                return render_template("quiz.html", quiz=quiz, questions=questions, session_active=session_active)
        
        return render_template("quiz.html", quiz=quiz, questions=questions, session_active=session_active)
    else:
        return "Quiz nicht gefunden oder keine Zugriffsberechtigung.", 404