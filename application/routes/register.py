from quizmeister import app
from flask import render_template, request, redirect, url_for, flash
import sqlite3
import bcrypt

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Passwort hashen
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Benutzer in die Datenbank einfügen
        try:
            with sqlite3.connect("quizzy.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                            (username, hashed_password))
                con.commit()
            flash("Registrierung erfolgreich! Du kannst dich jetzt anmelden.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Benutzername bereits vergeben. Bitte wähle einen anderen Namen.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")
