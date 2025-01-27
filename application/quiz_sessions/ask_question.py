from application import socketio
from flask_socketio import emit
import sqlite3
from application.quiz_sessions import quiz_sessions

# Frage an Teilnehmer senden
@socketio.on("ask_question")
def handle_question(session_code, quiz_id, question_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Frage-Daten laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (quiz_id, question_id))
        question = cur.fetchone()

        question_text = question[2]
        category = question[3]
        points = question[7]
        image = question[5]
    
    quiz_sessions[session_code]["current_question"] = question_id    
    emit("send_question", (question_id, question_text, category, points, image), to=session_code)
