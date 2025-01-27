from application import socketio
import random
import string
import sqlite3
from flask_socketio import join_room, emit
from flask import session
from application.quiz_sessions import quiz_sessions

# Funktion zum Generieren eines zufälligen Session-Codes
def generate_session_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# Eine Quiz-Session erstellen
@socketio.on("host_session")
def handle_host_session(quiz_id):
    # Prüfen ob Session bereits läuft und ob aktueller User der Host ist
    session_active = False
    for quiz_session in quiz_sessions:
        if quiz_sessions[quiz_session]["quiz_id"] == quiz_id and quiz_sessions[quiz_session]["host"] == session["username"]:
            session_active = True
            session_code = quiz_session    
    
    # Quiz Namen abrufen
    with sqlite3.connect('quizzy.db') as con:
            cur = con.cursor()
            cur.execute("SELECT title FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
            quiz = cur.fetchone()
            quiz_name = quiz[0]
    
    if not session_active:
        # Session-Code generieren
        session_code = generate_session_code()

        # Neue Quiz-Session erstellen
        quiz_sessions[session_code] = {}
        quiz_session = quiz_sessions[session_code]
        quiz_session["quiz_id"] = quiz_id
        quiz_session["quiz_name"] = quiz_name
        quiz_session["host"] = session["username"]
        quiz_session["current_question"] = None
        quiz_session["players"] = {}
        
        print(f"Host hat Room '{session_code}' für Quiz '{quiz_name}' mit ID {quiz_id} erstellt.")
        players_answers = None
        
    else:
        players_answers = {}
        quiz_session = quiz_sessions[session_code]
        for player, answers in quiz_session["players"].items():
            players_answers[player] = []
            for question_id, answer_values in answers["answers"].items():
                players_answers[player].append({
                    "question_id": question_id,
                    "player_answer": answer_values['player_answer'],
                    "question_points": answer_values['question_points']
                })

        print(players_answers)
        print(f"Host hat Room '{session_code}' für Quiz '{quiz_name}' mit ID {quiz_id} wieder betreten.")
        
    # Host tritt dem Room bei (auch bei Wiedereinstieg)
    join_room(session_code)
    print(quiz_sessions)
    emit("session_created", {"session_code": session_code, "players_answers": players_answers}, broadcast=False)

