from application import socketio
from flask import session

# Teilnehmer verbindet sich
@socketio.on("connect")
def handle_connect():
    print("Teilnehmer verbunden: " + session["username"])