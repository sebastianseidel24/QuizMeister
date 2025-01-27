from application import socketio
from flask_socketio import emit
import sqlite3
from application.quiz_sessions import quiz_sessions

# Korrekte Antwort an Teilnehmer senden
@socketio.on("share_correct_answer")
def handle_share_answer(session_code, quiz_id, question_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Frage-Daten laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (quiz_id, question_id))
        question = cur.fetchone()
        
        question_text = question[2]
        category = question[3]
        points = question[7]
        image = question[5]
        answer = question[6]
    
    quiz_sessions[session_code]["current_question"] = None    
    emit("send_correct_answer", (question_id, question_text, category, points, image, answer), to=session_code)
