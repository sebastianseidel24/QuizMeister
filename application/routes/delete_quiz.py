from application import app
from flask import request, redirect, url_for
import sqlite3

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
    return redirect(url_for('quiz_overview'))
