from quizmeister import socketio
from flask_socketio import emit, join_room
from flask import session, request
from quiz_sessions import quiz_sessions, user_room_map
import sqlite3

# Reconnect eines Teilnehmers
@socketio.on("reconnect_to_room")
def handle_reconnect_to_room():
    sid = request.sid
    username = session["username"]

    # Prüfen, ob es eine alte Room-Zuordnung für diesen Teilnehmer gibt
    for room, data in quiz_sessions.items():
        if username in data["players"]:
            join_room(room)
            user_room_map[sid] = room
            emit("reconnected_to_room", {"room": room, "username": username}, broadcast=False)
            
            # ggf. aktuelle Frage erneut senden, wenn noch nicht beantwortet
            if data["current_question"] is not None and data["players"][username]["answers"].get(data["current_question"]) is None:
                question_id = data["current_question"]
                with sqlite3.connect('quizzy.db') as con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (data["quiz_id"], question_id))
                    question = cur.fetchone()
                    question_text = question[2]
                    category = question[3]
                    points = question[7]
                    image = question[5]
                emit("send_question", (question_id, question_text, category, points, image), broadcast=False)
            
            print(f"Teilnehmer {username} wurde nach Wiederverbindung Room {room} zugeordnet.")
            return

    # Kein zugeordneter Room gefunden
    emit("room_not_found", {"username": username}, broadcast=False)
    print(f"Keine Room-Zuordnung für Teilnehmer {username} gefunden.")
