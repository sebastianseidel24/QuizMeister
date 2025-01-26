# Speichern der laufenden Quiz-Sessions
quiz_sessions = {}

# quiz_sessions = {<Quiz-Session-ID>: {                             # Dictionary für jede Quiz-Session mit Quiz-Session-ID als Key
#     "quiz_id": <Quiz-ID>,                                         # ID des Quizzes
#     "quiz_name": <Quiz-Name>,                                     # Name des Quizzes
#     "host": <Host-Name>,                                          # Host der Session (repräsentiert durch Benutzername)
#     "current_question": <Aktuelle-Frage-ID>,                      # ID der aktuellen Frage	
#     "players": {<Spielername>: {                                  # Dictionary der teilnehmenden Spieler mit Benutzername als Key
#             "points": <Punkte>,                                   # Aktuelle Punktzahl
#             "place": <Platzierung>,                               # Aktuelle Platzierung
#             "answers": {<Question-ID>: {"player_answer": <Antwort>, "question_points":<Punkte>}}     # Antworten und gesammelte Punkte zu den Fragen
#         }},
# }}

# Speichert die Zuordnung der Clients zu den Rooms
user_room_map = {}