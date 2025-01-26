from quizmeister import socketio
from flask_socketio import emit
from quiz_sessions import quiz_sessions
from flask import url_for

# Eine Quiz-Session beenden
@socketio.on("end_session")
def handle_end_session(session_code):
    quiz_session = quiz_sessions[session_code]
    quiz_id = quiz_session["quiz_id"]
    quiz_name = quiz_session["quiz_name"]
    redirect_url = url_for("quiz", quiz_id=quiz_id)
    
    # Session beenden
    emit("session_ended", redirect_url, to=session_code)
    quiz_sessions.pop(session_code)
    print(f"Session {session_code} für Quiz '{quiz_name}' mit ID {quiz_id} beendet.")
    print(quiz_sessions)
