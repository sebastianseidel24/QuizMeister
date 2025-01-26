from quizmeister import app
from flask import render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename


# Prüfen ob Dateiname für Bild-Uplad erlaubt ist
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ein Quiz erstellen
@app.route("/createquiz", methods=["GET", "POST"])
def create_quiz():

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

