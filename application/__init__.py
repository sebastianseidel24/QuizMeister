from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

# Umgebungsvariablen laden
load_dotenv()

app = Flask(__name__)

# Configs
app.config["UPLOAD_FOLDER"] = "..\\static\\FileUploads"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# SocketIO konfigurieren
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*", ping_interval=10, ping_timeout=20)
