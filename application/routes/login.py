from flask import flash, redirect, render_template, request, session, url_for
from quizmeister import app
import bcrypt
import sqlite3

# Login anfordern
@app.before_request
def require_login():
    # Routen ohne Login
    allowed_routes = ["register", "login", "static"]
    if "username" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))
    
# Login
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
                flash("Falscher Benutzername oder Passwort. Bitte erneut versuchen.", "danger")
                return redirect(url_for("login"))

    return render_template("login.html")