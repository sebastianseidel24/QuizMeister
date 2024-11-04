from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quizoverview")
def quizoverview():
    return render_template("quizoverview.html")

@app.route("/createquiz")
def createquiz():
    return render_template("createquiz.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == '__main__':
    app.run(debug=True)
