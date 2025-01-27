from application import socketio
from flask_socketio import emit
from application.quiz_sessions import quiz_sessions

# Hilfsfunktion, um das Leaderboard zu berechnen
def calculateLeaderboard(session_code):
    quiz_session = quiz_sessions[session_code]
    
    # Spieler aus dem Dictionary extrahieren und nach Punkten absteigend sortieren
    sorted_players = sorted(
        quiz_session["players"].items(),
        key=lambda item: item[1]["points"],
        reverse=True
    )

    # Aktualisiere die Plätze basierend auf der Sortierung
    current_place = 1
    for i, (player_name, player_data) in enumerate(sorted_players):
        if i > 0 and player_data["points"] == sorted_players[i-1][1]["points"]:
            # Spieler mit gleichen Punkten haben denselben Platz
            player_data["place"] = sorted_players[i-1][1]["place"]
        else:
            # Ansonsten: Platz entsprechend der Position setzen
            player_data["place"] = current_place
        current_place += 1

    # Zurück in das ursprüngliche Dictionary schreiben
    quiz_session["players"] = dict(sorted_players)


# Leaderboard berechnen
@socketio.on("calculate_leaderboard")
def handle_calc_leaderboard(session_code):
    quiz_session = quiz_sessions[session_code]
    calculateLeaderboard(session_code)
    print(quiz_session)
    # Sende das Leaderboard-Update für jeden Spieler einzeln
    for player in quiz_session["players"]:
        playername = player
        place = quiz_session["players"][player]["place"]
        points = quiz_session["players"][player]["points"]
        emit("update_leaderboard", (place, playername, points), to=session_code)