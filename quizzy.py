from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)



# Beispiel-Datenstruktur für Quizzes und Fragen
quizzes = [
    {
        "id": 1,
        "title": "Quiz 1",
        "questions": [
            {"question": "Wie viele Kontinente gibt es?", "category": "Geografie", "answer": "7"},
            {"question": "Wer hat die Relativitätstheorie entwickelt?", "category": "Physik", "answer": "Einstein"},
        ]
    },
    {
        "id": 2,
        "title": "Quiz 2",
        "questions": [
            {"question": "Wer spielt Iron Man im Marvel-Universum?", "category": "Film & TV", "answer": "Robert Downey Jr."},
            {"question": "In welchem Jahr wurde der erste Star Wars-Film veröffentlicht?", "category": "Film & TV", "answer": "1977"},
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
        # Formulardaten abrufen
        title = request.form.get("title")
        questions = request.form.getlist("questions")
        
        # Neue Quiz-ID berechnen
        new_quiz_id = len(quizzes) + 1
        
        # Quiz-Daten erstellen
        new_quiz = {
            "id": new_quiz_id,
            "title": title,
            "questions": []
        }
        
        # Fragen und Antwortoptionen hinzufügen
        for i in range(len(questions)):
            question_text = request.form.get(f"questions[{i}][question]")
            answer = request.form.get(f"questions[{i}][answer]")
            category = request.form.get(f"questions[{i}][category]")
            
            new_quiz["questions"].append({
                "question": question_text,
                "answer": answer,
                "category": category,
            })
        
        # Neues Quiz zur Liste der Quizzes hinzufügen
        quizzes.append(new_quiz)
        
        # Umleitung zur Quiz-Übersicht
        return redirect(url_for("quizoverview"))
    
    return render_template("createquiz.html")

@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if quiz != None:
        return render_template("quiz.html", quiz=quiz)
    else:
        return "Quiz nicht gefunden.", 404

@app.route("/results/<int:quiz_id>", methods=["POST"])
def results(quiz_id):
    # Ergebnis-Berechnung hier einfügen
    return render_template("results.html")


# App starten
if __name__ == '__main__':
    app.run(debug=True)





