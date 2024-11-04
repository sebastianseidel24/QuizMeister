from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)



# Beispiel-Datenstruktur für Quizzes und Fragen
quizzes = [
    {
        "id": 1,
        "title": "Quiz 1",
        "questions": [
            {"question": "Wie viele Kontinente gibt es?", "category": "Geografie", "options": ["5", "6", "7", "8"], "answer": "7"},
            {"question": "Wer hat die Relativitätstheorie entwickelt?", "category": "Physik", "options": ["Newton", "Einstein", "Tesla", "Bohr"], "answer": "Einstein"},
        ]
    },
    {
        "id": 2,
        "title": "Quiz 2",
        "questions": [
            {"question": "Wer spielt Iron Man im Marvel-Universum?", "category": "Film & TV", "options": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo", "Chris Hemsworth"], "answer": "Robert Downey Jr."},
            {"question": "In welchem Jahr wurde der erste Star Wars-Film veröffentlicht?", "category": "Film & TV", "options": ["1977", "1980", "1983", "1985"], "answer": "1977"},
        ]
    },
]

#Seiten
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quizoverview")
def quizoverview():
    return render_template("quizoverview.html", quizzes=quizzes)

@app.route("/createquiz", methods=["GET", "POST"])
def createquiz():
    if request.method == "POST":
        # Quiz-Erstellungscode hier hinzufügen
        return redirect(url_for("quizoverview"))
    return render_template("createquiz.html")

@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if quiz:
        return render_template("quiz.html", quiz=quiz)
    return "Quiz nicht gefunden.", 404

@app.route("/results/<int:quiz_id>", methods=["POST"])
def results(quiz_id):
    # Ergebnis-Berechnung hier einfügen
    return render_template("results.html")


# App starten
if __name__ == '__main__':
    app.run(debug=True)





