from quizmeister import app
from flask import redirect, url_for, session

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
