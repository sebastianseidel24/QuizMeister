from application import socketio
from application.quiz_sessions import quiz_sessions, user_room_map
from flask_socketio import join_room, emit
from flask import request

# Spieler tritt Session bei
@socketio.on("player_join")
def handle_player_join(session_code, playername):    
    try:
        # Testen ob Session existiert
        if session_code not in quiz_sessions:
            emit("session_unavailable", broadcast=False)
        else:
            # Spieler zu Session hinzufügen
            quiz_session = quiz_sessions[session_code]
            quiz_id = quiz_session["quiz_id"]
            quiz_name = quiz_session["quiz_name"]
            
            # Neuaufname, falls noch nicht vorhanden
            if playername not in quiz_session["players"]:  
                points = 0
                place = 1
                
                quiz_session["players"][playername] = {"points": points, "place": place, "answers": {}}
                emit("new_player", (session_code, quiz_id, quiz_name, playername, points, place), to=session_code)
                
            # Spieler tritt Room bei (auch bei Wiedereinstieg)
            join_room(session_code)
            user_room_map[request.sid] = session_code  # Room-Zuordnung aktualisieren
            emit("joined_session", (session_code, quiz_id, quiz_name), broadcast=False)
            print(f"'{playername}' ist Session {session_code} und Quiz '{quiz_name}' beigetreten.")
            print(quiz_session)
            
    except Exception as e:
        print("An exception occurred:", type(e).__name__, e)
