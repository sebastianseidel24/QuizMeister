from quizmeister import socketio
from quiz_sessions import quiz_sessions

@socketio.on("calculate_points")
def handle_calculate_points(session_code, playername, points):
    quiz_session = quiz_sessions[session_code]
    for player in quiz_session["players"]:
        if player == playername:
            quiz_session["players"][player]["points"] = points
