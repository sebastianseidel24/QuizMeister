from application import app, socketio

# App starten
if __name__ == '__main__':
    socketio.run(app, debug=True)