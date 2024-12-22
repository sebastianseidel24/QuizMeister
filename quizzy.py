import sqlite3
import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static\\FileUploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'thekey'
socketio = SocketIO(app)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return render_template("quiz.html", quiz=quiz, questions=questions)
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

#Sessions-Logik
quiz_session = {"quiz_id": None, "quiz_name": None, "players": []} #Quiz-Session mit QuizID, Quiz-Name und Teilnehmern; jeder Teilnehmer wird durch ein Dictionary mit SessionID, Spielername und Punkten repräsentiert


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
    print("Teilnehmer verbunden: " + request.sid)
    
@socketio.on("disconnect")
def handle_disconnect():
    print("Teilnehmer getrennt")
    
    
    
@socketio.on("host_session")
def handle_host_session(quiz_id, quiz_name):
    quiz_session["quiz_id"] = quiz_id
    quiz_session["quiz_name"] = quiz_name
    quiz_session["players"] = []
    print(f"Host hat Session für Quiz '{quiz_name}' mit ID {quiz_id} erstellt.")
    print(quiz_session)
    emit("new_session", (quiz_id, quiz_name), broadcast=True)



@socketio.on("player_join")
def handle_player_join(playername):
    try:
        if quiz_session["quiz_id"] == None:
            emit("session_unavailable", broadcast=False)
        else:
            for player in quiz_session["players"]:
                if player["playername"] == playername:
                    print("Spieler existiert bereits.")
                    emit("player_already_exists", playername, broadcast=False)
                    raise Exception
            quiz_id = quiz_session["quiz_id"]
            quiz_name = quiz_session["quiz_name"]
            points = 0
            place = len(quiz_session["players"]) + 1
            quiz_session["players"].append({"session_id": request.sid, "playername": playername, "points": points, "place": place})
            print(f"'{playername}' mit Session-ID '{request.sid}' ist Quiz '{quiz_name}' beigetreten.")
            print(quiz_session)
            emit("new_player", (quiz_id, quiz_name, playername, points, place), broadcast=True)
    except Exception as e:
        print("An exception occurred:", type(e).__name__, e)


@socketio.on("ask_question")
def handle_question(quiz_id, question_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Frage-Daten laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?) AND question_id = (?)", (quiz_id, question_id))
        question = cur.fetchone()

        question_text = question[2]
        category = question[3]
        points = question[7]
        image = question[5]
        
    emit("send_question", (question_id, question_text, category, points, image), broadcast=True)

    
@socketio.on("submit_answer")
def handle_answer(question_id, playername, answer):
    emit("send_answer", (question_id, playername, answer), broadcast=True)


@socketio.on("calculate_points")
def handle_calculate_points(playername, points):
    for player in quiz_session["players"]:
        if player["playername"] == playername:
            player["points"] = points


@socketio.on("calculate_leaderboard")
def handle_calc_leaderboard():
    calculateLeaderboard()
    print(quiz_session)
    # Sende das Leaderboard-Update für jeden Spieler einzeln
    for player in quiz_session["players"]:
        place = player["place"]
        playername = player["playername"]
        points = player["points"]
        emit("update_leaderboard", (place, playername, points), broadcast=True)
    


def calculateLeaderboard():
    # Sortiere Spieler nach Punkten absteigend
    quiz_session["players"].sort(key=lambda player: player["points"], reverse=True)

    # Aktualisiere die Plätze basierend auf der Sortierung
    current_place = 1
    for i, player in enumerate(quiz_session["players"]):
        if i > 0 and player["points"] == quiz_session["players"][i-1]["points"]:
            # Spieler mit gleichen Punkten haben denselben Platz
            player["place"] = quiz_session["players"][i-1]["place"]
        else:
            # Ansonsten: Platz entsprechend der Position setzen
            player["place"] = current_place
        current_place += 1


@socketio.on("share_leaderboard")
def handle_share_leaderboard():
    emit("clear_leaderboard", broadcast=True)
    calculateLeaderboard()
    for player in quiz_session["players"]:
        place = player["place"]
        playername = player["playername"]
        points = player["points"]
        emit("send_leaderboard", (place, playername, points), broadcast=True)


# App starten
if __name__ == '__main__':
    socketio.run(app, debug=True)