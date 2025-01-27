from application import socketio
from application.quiz_sessions import quiz_sessions
from flask_socketio import emit

# Eine Antwort abschicken
@socketio.on("submit_answer")
def handle_answer(session_code, question_id, playername, answer):
    quiz_sessions[session_code]["players"][playername]["answers"][question_id] = {}
    quiz_sessions[session_code]["players"][playername]["answers"][question_id]["player_answer"] = answer
    quiz_sessions[session_code]["players"][playername]["answers"][question_id]["question_points"] = 0
    emit("send_answer", (question_id, playername, answer), to=session_code)