from application import app
from flask import render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
from application.routes.create_quiz import allowed_file

# Ein Quiz bearbeiten
@app.route("/editquiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):

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
                return redirect(url_for("quiz_overview"))
        
        return render_template("editquiz.html", quiz=quiz, questions=questions)
