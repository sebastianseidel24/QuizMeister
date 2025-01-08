import sqlite3
import os
import bcrypt
import random
import string
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, emit
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Konstanten
UPLOAD_FOLDER = "static\\FileUploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# .env laden
load_dotenv()

app = Flask(__name__)

# Configs
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# async_mode auf "eventlet" setzen
async_mode = "eventlet"

# SocketIO konfigurieren
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*", ping_interval=10, ping_timeout=20)

# Prüfen ob Dateiname für Bild-Uplad erlaubt ist
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login anfordern
@app.before_request
def require_login():
    # Routen ohne Login
    allowed_routes = ["register", "login", "static"]
    if "username" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))


@app.route("/")
def index():
    username = session["username"]
    return render_template("index.html", username=username)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Passwort hashen
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Benutzer in die Datenbank einfügen
        try:
            with sqlite3.connect("quizzy.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                            (username, hashed_password))
                con.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Benutzername bereits vergeben.", 400

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect("quizzy.db") as con:
            cur = con.cursor()
            cur.execute("SELECT rowid, password FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

            if user and bcrypt.checkpw(password.encode("utf-8"), user[1]):
                session["user_id"] = user[0]
                session["username"] = username
                return redirect(url_for("index"))
            else:
                return "Falscher Benutzername oder Passwort.", 401

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/quizoverview")
def quizoverview():
    user_id = session["user_id"]

    with sqlite3.connect("quizzy.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM quizzes WHERE user_id = (?)", (user_id,))
        quizzes = cur.fetchall()
    
    return render_template("quizoverview.html", quizzes=quizzes)



@app.route("/createquiz", methods=["GET", "POST"])
def createquiz():

    if request.method == "POST":
        try:  
            # Titel abrufen
            title = request.form.get("title")        
            user_id = session["user_id"]
            
            with sqlite3.connect("quizzy.db") as con:
                cur = con.cursor()

                #Quiz zu Datenbank hinzfügen
                cur.execute("INSERT INTO quizzes (title, user_id) VALUES (?,?)", (title, user_id))
                con.commit()
                msg1 = "Quiz zu Datenbank hinzugefügt"

                #Quiz ID abrufen
                current_row = cur.lastrowid
                cur.execute("SELECT quiz_id FROM quizzes WHERE rowid = (?)", (current_row,))
                quiz = cur.fetchone()
                quiz_id = quiz[0]
            
            # Fragen und Antwortoptionen hinzufügen
            i = 0
            while f"questions[{i}][question]" in request.form:                
                question_id = i + 1
                question_text = request.form.get(f"questions[{i}][question]")
                category = request.form.get(f"questions[{i}][category]")
                description = request.form.get(f"questions[{i}][description]")
                answer = request.form.get(f"questions[{i}][answer]")
                points = request.form.get(f"questions[{i}][points]")
                
                image = request.files[f"questions[{i}][image]"]
                if image.filename != "" and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                else:
                    filename = None

                cur.execute("INSERT INTO questions (question_id, quiz_id, question, category, description, image, answer, points) VALUES (?,?,?,?,?,?,?,?)", (question_id, quiz_id, question_text, category, description, filename, answer, points))
                con.commit()
                msg2 = f"{i + 1} Fragen zur Datenbank hinzugefügt"

                i += 1

            #Anzahl Fragen zu Quiz-DB hinzufügen
            cur.execute("UPDATE quizzes SET number_of_questions = (?) WHERE quiz_id = (?)", (question_id, quiz_id))
            con.commit()

        except Exception as e:
            con.rollback()
            print(type(e).__name__, e)
            msg1 = "Fehler beim Hinzufügen des Quizzes zur Datenbank"
            msg2 = "Fehler beim Hinufügen der Fragen zur Datenbank"

        finally:
            con.close()
            print(msg1 + " | " + msg2)

            # Umleitung zur Quiz-Übersicht
            return redirect(url_for("quizoverview"))

    return render_template("createquiz.html")



@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):

    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT * FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz != None and quiz[3] == session["user_id"]:
        
        # Prüfen ob Session bereits existiert
        session_active = False
        for quiz_session in quiz_sessions:
            if quiz_sessions[quiz_session]["quiz_id"] == quiz_id:
                session_active = True
                return render_template("quiz.html", quiz=quiz, questions=questions, session_active=session_active)
        
        return render_template("quiz.html", quiz=quiz, questions=questions, session_active=session_active)
    else:
        return "Quiz nicht gefunden oder keine Zugriffsberechtigung.", 404


@app.route("/editquiz/<int:quiz_id>", methods=["GET", "POST"])
def editquiz(quiz_id):

    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT * FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz == None:
        return "Quiz nicht gefunden.", 404
    else:
        if request.method == "POST":
            try:  
                # (Neuen) Titel abrufen
                title = request.form.get("title")

                with sqlite3.connect("quizzy.db") as con:
                    cur = con.cursor()

                    # Quiz-Titel in Datenbank updaten
                    cur.execute("UPDATE quizzes SET title = (?) WHERE quiz_id = (?)", (title, quiz_id))
                    con.commit()
                    msg1 = f"Quiz-Titel '{title}' in Datenbank bearbeitet"

                # Alle Fragen löschen und wieder hinzufügen
                cur.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
                msg2 = "Alle Fragen gelöscht"
                question_id = 0
                
                if "questions[0][question]" in request.form:
                    i = 0
                    while f"questions[{i}][question]" in request.form:
                        question_id = i + 1
                        question_text = request.form.get(f"questions[{i}][question]")
                        category = request.form.get(f"questions[{i}][category]")
                        description = request.form.get(f"questions[{i}][description]")
                        answer = request.form.get(f"questions[{i}][answer]")
                        points = request.form.get(f"questions[{i}][points]")

                        filename = request.form.get(f"questions[{i}][image-filename]")
                        if filename == "None":
                            filename = None
                        
                        if f"questions[{i}][image]" in request.files:
                            image = request.files[f"questions[{i}][image]"]
                            if image.filename != "" and allowed_file(image.filename):
                                filename = secure_filename(image.filename)
                                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            else:
                                filename = None

                        cur.execute("INSERT INTO questions (question_id, quiz_id, question, category, description, image, answer, points) VALUES (?,?,?,?,?,?,?,?)", (question_id, quiz_id, question_text, category, description, filename, answer, points))
                        con.commit()
                        msg2 = f"Alle alten Fragen gelöscht und {i + 1} Fragen zur Datenbank hinzugefügt"

                        i += 1

                # Anzahl Fragen in Quiz-DB updaten
                cur.execute("UPDATE quizzes SET number_of_questions = (?) WHERE quiz_id = (?)", (question_id, quiz_id))
                con.commit()
                
            except Exception as e:
                con.rollback()
                print("An exception occurred:", type(e).__name__, e)
                msg1 = "Fehler beim Bearbeiten des Quizzes in der Datenbank"
                msg2 = "Fehler beim Bearbeiten der Fragen in der Datenbank"

            finally:
                con.close()
                print(msg1 + " | " + msg2)

                # Umleitung zur Quiz-Übersicht
                return redirect(url_for("quizoverview"))
        
        return render_template("editquiz.html", quiz=quiz, questions=questions)


# Quiz löschen
@app.route('/delete_quiz', methods=['POST'])
def delete_quiz():
    quiz_id = request.form['quiz_id']
    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        cur.execute("DELETE FROM questions WHERE quiz_id = (?)", (quiz_id,))
        con.commit()
        print(f"Quiz '{quiz_id}' aus Datenbank entfernt.")
    return redirect(url_for('quizoverview'))


# Fragen mit Gemini generieren lassen
@app.route("/generate_questions", methods=["POST"])
def process_question_generation():
    try:
        # JSON-Daten von der Anfrage lesen
        data = request.get_json()

        # Lese die Daten aus dem JSON-Objekt
        number_of_questions = data.get("numberOfQuestions")
        difficulty = data.get("difficulty")
        categories = data.get("categories")
        categories = ", ".join(categories)

        # Fragen generieren lassen
        generated_questions = generate_questions(number_of_questions, categories, difficulty)
        
        # Sende eine Antwort zurück
        return jsonify({"questions": generated_questions})

    except Exception as e:
        # Fehler abfangen und eine Fehlermeldung zurückgeben
        return jsonify({"error": f"Ein Fehler ist aufgetreten: {str(e)}"}), 400

# Gemini-API Konfiguration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")
GENERATION_CONFIG  = genai.GenerationConfig(response_mime_type="application/json")

# Mittels Gemini-API Fragen generieren lassen
def generate_questions(number_of_questions: int, categories: str, difficulty: str):
    if (number_of_questions == "1"):
        prompt = f'''
                Erstelle eine Liste, die aus genau einer kreativen Quiz-Frage für ein Pub-Quiz besteht. Die Frage muss folgende Felder enthalten:

                1. "question_id" (Typ: Integer): 0  
                2. "category" (Typ: String): Eine zufällig gewählte Kategorie aus den folgenden Optionen: {categories}.  
                3. "question_text" (Typ: String): Der Fragetext, formuliert als vollständiger Satz, ohne die Verwendung von Anführungszeichen.  
                4. "answer" (Typ: String): Die korrekte Antwort auf die Frage, ebenfalls ohne die Verwendung von Anführungszeichen.

                Zusätzliche Anforderungen:  
                - Die Frage sollten eine {difficulty} Schwierigkeit haben.
                - Nutze eine klare und präzise Sprache.
                
                Beispiel-Ausgabe:
                [{{
                    "question_id": 0,
                    "category": "Geografie",
                    "question_text": "Welches ist das größte Land der Welt nach Fläche?",
                    "answer": "Russland"
                    }}]
                '''
    else:
        prompt = f'''
                Erstelle eine Liste, die aus genau {number_of_questions} vielseitigen und kreativen Quiz-Fragen für ein Pub-Quiz besteht. Jede Frage muss folgende Felder enthalten:

                1. "question_id" (Typ: Integer): Eine fortlaufende ID, beginnend mit 0.  
                2. "category" (Typ: String): Eine zufällig gewählte Kategorie aus den folgenden Optionen: {categories}.  
                3. "question_text" (Typ: String): Der Fragetext, formuliert als vollständiger Satz, ohne die Verwendung von Anführungszeichen.  
                4. "answer" (Typ: String): Die korrekte Antwort auf die Frage, ebenfalls ohne die Verwendung von Anführungszeichen.

                Zusätzliche Anforderungen:  
                - Die Fragen sollten eine {difficulty} Schwierigkeit haben.  
                - Vermeide Wiederholungen in den Fragen oder Antworten.
                - Nutze eine klare und präzise Sprache.
                
                Beispiel-Ausgabe:
                [
                    {{
                    "question_id": 0,
                    "category": "Geografie",
                    "question_text": "Welches ist das größte Land der Welt nach Fläche?",
                    "answer": "Russland"
                    }},
                    {{
                    "question_id": 1,
                    "category": "Musik",
                    "question_text": "Welcher Künstler hat das Album Thriller veröffentlicht?",
                    "answer": "Michael Jackson"
                    }},
                    ...
                ]
                '''
    print(prompt)
    
    generated_questions = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG).text
    
    generated_questions = generated_questions[generated_questions.index("["):] # Falls die Antwort nicht mit einer Liste beginnt, wird der Anfang der Liste gesucht
    print(generated_questions)
    return(eval(generated_questions)) # Die Antwort wird in ein Python-Objekt (Liste) umgewandelt und zurückgegeben

# Sessions-Logik

# Speichern der laufenden Quiz-Sessions
quiz_sessions = {}

# quiz_sessions = {<Quiz-Session-ID>: {                             # Dictionary für jede Quiz-Session mit Quiz-Session-ID als Key
#     "quiz_id": <Quiz-ID>,                                         # ID des Quizzes
#     "quiz_name": <Quiz-Name>,                                     # Name des Quizzes
#     "host": <Host-Name>,                                          # Host der Session (repräsentiert durch Benutzername)
#     "players": {<Spielername>: {                                  # Dictionary der teilnehmenden Spieler mit Benutzername als Key
#             "points": <Punkte>,                                   # Aktuelle Punktzahl
#             "place": <Platzierung>,                               # Aktuelle Platzierung
#             "answers": {<Question-ID>: {"player_answer": <Antwort>, "question_points":<Punkte>}}     # Antworten und gesammelte Punkte zu den Fragen
#         }},
# }}

# Speichert die Zuordnung der Clients zu den Rooms
user_room_map = {}


@app.route("/hostquiz/<int:quiz_id>")
def hostquiz(quiz_id):
    with sqlite3.connect("quizzy.db") as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT * FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz == None:
        return "Quiz nicht gefunden.", 404
    else:
        return render_template("hostquiz.html", quiz=quiz, questions=questions)



@app.route("/playquiz")
def playquiz():
    return render_template("playquiz.html")

@socketio.on("connect")
def handle_connect():
    print("Teilnehmer verbunden: " + session["username"])
    
@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in user_room_map:
        room = user_room_map.pop(sid, None)  # Room-Zuordnung entfernen
        print(f"Teilnehmer {session['username']} aus Room {room} getrennt.")
    else:
        print(f"Teilnehmer {session['username']} hat Verbindung getrennt.")
    
# Reconnect    
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
            print(f"Teilnehmer {username} wurde nach Wiederverbindung Room {room} zugeordnet.")
            return

    # Kein zugeordneter Room gefunden
    emit("room_not_found", {"username": username}, broadcast=False)
    print(f"Keine Room-Zuordnung für Teilnehmer {username} gefunden.")

# Funktion zum Generieren eines zufälligen Session-Codes
def generate_session_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))


@socketio.on("host_session")
def handle_host_session(quiz_id):
    # Prüfen ob Session bereits läuft und ob aktueller User der Host ist
    session_active = False
    for quiz_session in quiz_sessions:
        if quiz_sessions[quiz_session]["quiz_id"] == quiz_id and quiz_sessions[quiz_session]["host"] == session["username"]:
            session_active = True
            session_code = quiz_session    
    
    # Quiz Namen abrufen
    with sqlite3.connect('quizzy.db') as con:
            cur = con.cursor()
            cur.execute("SELECT title FROM quizzes WHERE quiz_id = (?)", (quiz_id,))
            quiz = cur.fetchone()
            quiz_name = quiz[0]
    
    if not session_active:
        # Session-Code generieren
        session_code = generate_session_code()

        # Neue Quiz-Session erstellen
        quiz_sessions[session_code] = {}
        quiz_session = quiz_sessions[session_code]
        quiz_session["quiz_id"] = quiz_id
        quiz_session["quiz_name"] = quiz_name
        quiz_session["host"] = session["username"]
        quiz_session["players"] = {}
        
        print(f"Host hat Room '{session_code}' für Quiz '{quiz_name}' mit ID {quiz_id} erstellt.")
        players_answers = None
        
    else:
        players_answers = {}
        quiz_session = quiz_sessions[session_code]
        for player, answers in quiz_session["players"].items():
            players_answers[player] = []
            for question_id, answer_values in answers["answers"].items():
                players_answers[player].append({
                    "question_id": question_id,
                    "player_answer": answer_values['player_answer'],
                    "question_points": answer_values['question_points']
                })

        print(players_answers)
        print(f"Host hat Room '{session_code}' für Quiz '{quiz_name}' mit ID {quiz_id} wieder betreten.")
        
    # Host tritt dem Room bei (auch bei Wiedereinstieg)
    join_room(session_code)
    print(quiz_sessions)
    emit("session_created", {"session_code": session_code, "players_answers": players_answers}, broadcast=False)



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


@socketio.on("ask_question")
def handle_question(session_code, quiz_id, question_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Frage-Daten laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (quiz_id, question_id))
        question = cur.fetchone()

        question_text = question[2]
        category = question[3]
        points = question[7]
        image = question[5]
        
    emit("send_question", (question_id, question_text, category, points, image), to=session_code)

    
@socketio.on("submit_answer")
def handle_answer(session_code, question_id, playername, answer):
    quiz_sessions[session_code]["players"][playername]["answers"][question_id] = {}
    quiz_sessions[session_code]["players"][playername]["answers"][question_id]["player_answer"] = answer
    quiz_sessions[session_code]["players"][playername]["answers"][question_id]["question_points"] = 0
    emit("send_answer", (question_id, playername, answer), to=session_code)


@socketio.on("share_correct_answer")
def handle_share_answer(session_code, quiz_id, question_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Frage-Daten laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (quiz_id, question_id))
        question = cur.fetchone()
        
        question_text = question[2]
        category = question[3]
        points = question[7]
        image = question[5]
        answer = question[6]
        
    emit("send_correct_answer", (question_id, question_text, category, points, image, answer), to=session_code)


@socketio.on("update_points")
def handle_update_points(session_code, playername, question_id, points_to_add):
    quiz_session = quiz_sessions[session_code]
    quiz_session["players"][playername]["answers"][question_id].update({"question_points": points_to_add})
    
    

@socketio.on("calculate_points")
def handle_calculate_points(session_code, playername, points):
    quiz_session = quiz_sessions[session_code]
    for player in quiz_session["players"]:
        if player == playername:
            quiz_session["players"][player]["points"] = points


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
    


def calculateLeaderboard(session_code):
    # Sortiere Spieler nach Punkten absteigend
    quiz_session = quiz_sessions[session_code]
    
    # Spieler aus dem Dictionary extrahieren und sortieren
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


# App starten
if __name__ == '__main__':
    socketio.run(app, debug=True)