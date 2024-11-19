import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)



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

        #Anzahl Fragen in Quiz
        #cur.execute("COUNT * WHERE ")
    
    return render_template("quizoverview.html", quizzes=quizzes)



@app.route("/createquiz", methods=["GET", "POST"])
def createquiz():

    if request.method == "POST":
        try:  
            # Titel abrufen
            title = request.form.get("title")

            with sqlite3.connect('quizzy.db') as con:
                cur = con.cursor()

                cur.execute("INSERT INTO quizzes (title) VALUES (?)", (title,))
                con.commit()
                msg1 = "Quiz zu Datenbank hinzugefügt"

                #Neue Quiz ID erstellen
                new_quiz_id = cur.lastrowid

            # Fragen und Antwortoptionen hinzufügen
            i = 0
            while f"questions[{i}][question]" in request.form:
                qid = i + 1
                question_text = request.form.get(f"questions[{i}][question]")
                category = request.form.get(f"questions[{i}][category]")
                description = request.form.get(f"questions[{i}][description]")
                answer = request.form.get(f"questions[{i}][answer]")
                points = request.form.get(f"questions[{i}][points]")

                cur.execute("INSERT INTO questions (question_id, quiz_id, question, category, description, answer, points) VALUES (?,?,?,?,?,?,?)", (qid, new_quiz_id, question_text, category, description, answer, points))
                con.commit()
                msg2 = f"{i + 1} Fragen zur Datenbank hinzugefügt"

                i += 1
        except:
            con.rollback()
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
        cur.execute("SELECT * FROM quizzes WHERE rowid = (?)", (quiz_id,))
        quiz = cur.fetchone()

        # Fragen des Quizzes laden
        cur.execute('SELECT * FROM questions WHERE quiz_id = (?)', (quiz_id,))
        questions = cur.fetchall()

    if quiz != None:
        return render_template("quiz.html", quiz=quiz, questions=questions)
    else:
        return "Quiz nicht gefunden.", 404



@app.route("/results/<int:quiz_id>", methods=["POST"])
def results(quiz_id):
    # Ergebnis-Berechnung hier einfügen
    return render_template("results.html")


# App starten
if __name__ == '__main__':
    app.run(debug=True)