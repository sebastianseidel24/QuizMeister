from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

# Umgebungsvariablen laden
load_dotenv()

# Flask-App initialisieren
app = Flask(__name__)

# Configs
app.config["UPLOAD_FOLDER"] = "application\\static\\FileUploads"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# SocketIO konfigurieren
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*", ping_interval=10, ping_timeout=20)

# Routen importieren
import application.routes.index
import application.routes.login
import application.routes.register
import application.routes.logout
import application.routes.create_quiz
import application.routes.delete_quiz
import application.routes.quiz
import application.routes.edit_quiz
import application.routes.generate_questions
import application.routes.host_quiz
import application.routes.play_quiz
import application.routes.quiz_overview

# Socket-Events importieren
import application.quiz_sessions.ask_question
import application.quiz_sessions.calculate_leaderboard
import application.quiz_sessions.calculate_points
import application.quiz_sessions.connect
import application.quiz_sessions.disconnect
import application.quiz_sessions.end_session
import application.quiz_sessions.host_session
import application.quiz_sessions.player_join
import application.quiz_sessions.reconnect
import application.quiz_sessions.share_correct_answer
import application.quiz_sessions.share_leaderboard
import application.quiz_sessions.submit_answer
import application.quiz_sessions.update_points