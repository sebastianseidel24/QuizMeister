from application import socketio
from flask_socketio import emit
from application.quiz_sessions import quiz_sessions
from application.quiz_sessions.calculate_leaderboard import calculateLeaderboard

# Leaderboard an Teilnehmer senden
@socketio.on("share_leaderboard")
def handle_share_leaderboard(session_code):
    quiz_session = quiz_sessions[session_code]
    
    emit("clear_leaderboard", to=session_code)
    calculateLeaderboard(session_code)
    for player in quiz_session["players"]:
        playername = player
        place = quiz_session["players"][player]["place"]
        points = quiz_session["players"][player]["points"]
        emit("send_leaderboard", (place, playername, points), to=session_code)