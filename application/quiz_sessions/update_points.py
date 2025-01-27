from application import socketio
from application.quiz_sessions import quiz_sessions

# Punkte aktualisieren
@socketio.on("update_points")
def handle_update_points(session_code, playername, question_id, points_to_add):
    quiz_session = quiz_sessions[session_code]
    quiz_session["players"][playername]["answers"][question_id].update({"question_points": points_to_add})