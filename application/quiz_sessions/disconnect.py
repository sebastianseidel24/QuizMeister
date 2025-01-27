from application import socketio
from flask import session, request
from application.quiz_sessions import user_room_map

# Teilnehmer trennen
@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in user_room_map:
        room = user_room_map.pop(sid, None)  # Room-Zuordnung entfernen
        print(f"Teilnehmer {session['username']} aus Room {room} getrennt.")
    else:
        print(f"Teilnehmer {session['username']} hat Verbindung getrennt.")