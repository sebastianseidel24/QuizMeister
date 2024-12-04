import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
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



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/quizoverview")
def quizoverview():

    with sqlite3.connect('quizzy.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT rowid, * FROM quizzes")
        quizzes = cur.fetchall()
    
    return render_template("quizoverview.html", quizzes=quizzes)



@app.route("/createquiz", methods=["GET", "POST"])
def createquiz():

    if request.method == "POST":
        try:  
            # Titel abrufen
            title = request.form.get("title")

            #Brauche ich hier "with", obwohl ich es am Ende eh schließe?????????????????
            
            
            with sqlite3.connect('quizzy.db') as con:
                cur = con.cursor()

                #Quiz zu Datenbank hinzfügen
                cur.execute("INSERT INTO quizzes (title) VALUES (?)", (title,))
                con.commit()
                msg1 = "Quiz zu Datenbank hinzugefügt"

                #Neue Quiz ID erstellen
                new_quiz_id = cur.lastrowid
            
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
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    filename = None

                cur.execute("INSERT INTO questions (question_id, quiz_id, question, category, description, image, answer, points) VALUES (?,?,?,?,?,?,?,?)", (question_id, new_quiz_id, question_text, category, description, filename, answer, points))
                con.commit()
                msg2 = f"{i + 1} Fragen zur Datenbank hinzugefügt"

                i += 1

            #Anzahl Fragen zu Quiz-DB hinzufügen
            cur.execute("UPDATE quizzes SET number_of_questions = (?) WHERE title = (?)", (question_id, title))
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

    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT rowid, * FROM quizzes WHERE rowid = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz != None:
        return render_template("quiz.html", quiz=quiz, questions=questions)
    else:
        return "Quiz nicht gefunden.", 404


@app.route("/editquiz/<int:quiz_id>", methods=["GET", "POST"])
def editquiz(quiz_id):

    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT rowid, * FROM quizzes WHERE rowid = (?)", (quiz_id,))
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

                with sqlite3.connect('quizzy.db') as con:
                    cur = con.cursor()

                    # Quiz-Titel in Datenbank updaten
                    cur.execute("UPDATE quizzes SET title = (?) WHERE rowid = (?)", (title, quiz_id))
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
                cur.execute("UPDATE quizzes SET number_of_questions = (?) WHERE title = (?)", (question_id, title))
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
sessions = [{"session_id": "1234", "players": {}}]


# @app.route('/joinquiz', methods=["GET", "POST"])
# def joinquiz():
#     if request.method == "POST":
#         session_id = request.form.get("session_id")
#         playername = request.form.get("playername")
#         for session in sessions:
#             if session_id == session["session_id"]:
#                 session["players"].append(playername)
#                 print(f"{playername} ist Session {session_id} beigetreten.")
#                 print(sessions)
#                 return redirect(url_for("playquiz", session_id=session_id, playername=playername))
#             else:
#                 print("Beitritt zur Session fehlgeschlagen.")
#     return render_template("joinquiz.html")


@app.route('/hostquiz/<int:quiz_id>')
def hostquiz(quiz_id):
    with sqlite3.connect('quizzy.db') as con:
        cur = con.cursor()

        # Quiz-Daten laden
        cur.execute("SELECT rowid, * FROM quizzes WHERE rowid = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute("SELECT * FROM questions WHERE quiz_id = (?)", (quiz_id,))
        questions = cur.fetchall()

    if quiz == None:
        return "Quiz nicht gefunden.", 404
    else:
        return render_template("hostquiz.html", quiz=quiz, questions=questions)



@app.route('/playquiz')
def playquiz():
    return render_template("playquiz.html")



@socketio.on("connect")
def handle_connect():
    print("Teilnehmer verbunden: " + request.sid)
    
    
    
@socketio.on("host_session")
def handle_host_session(session_id):
    session_unavailable = False
    for session in sessions:
        if session_id == session["session_id"]:
            print(f"Session {session_id} existiert bereits.")
            session_unavailable = True
    if(session_unavailable == False):
        sessions.append({"session_id": session_id, "players": {}})
        print(f"Host hat Session {session_id} erstellt.")
        print(sessions)



@socketio.on("player_join")
def handle_player_join(session_id, playername):
    session_unavailable = True
    player_id = request.sid
    for session in sessions:
        if session_id == session["session_id"]:
            session["players"][player_id] = playername
            session_unavailable = False
            print(f"{playername} mit ID: {player_id} ist Session {session_id} beigetreten.")
            print(sessions)
            emit("new_player", (session_id, playername), broadcast=True)
    if(session_unavailable):   
        emit("session_unavailable", session_id, broadcast=False)
        print(f"Beitritt von {playername} zu Session {session_id} fehlgeschlagen.")


    
@socketio.on("submit_answer")
def handle_answer(playername, answer):
    
    emit("send_answer", (playername, answer), broadcast=True)

# @app.route("/results/<int:quiz_id>", methods=["POST"])
# def results(quiz_id):
#     # Ergebnis-Berechnung hier einfügen
#     return render_template("results.html")

# App starten
if __name__ == '__main__':
    socketio.run(app, debug=True)