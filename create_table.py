import sqlite3

conn = sqlite3.connect('quizzy.db')
print("Connected to database succesfully")

# conn.execute('CREATE TABLE quizzes (title TEXT NOT NULL)')
# print("Tabelle quizzes erstellt")

# conn.execute('CREATE TABLE questions (question_id INTEGER, quiz_id INTEGER, question TEXT NOT NULL, category TEXT NOT NULL, description TEXT, answer TEXT NOT NULL, points FLOAT)')
# print("Tabelle questions erstellt")

# conn.execute('DROP TABLE questions')
# conn.execute('DROP TABLE quizzes')
x = conn.execute('SELECT COUNT(*) FROM quizzes')
x.fetchone()
print(x)

# try:
#     conn.execute('DELETE FROM quizzes WHERE quiz_id=3')
#     print("Gelöscht")
# except:
#     print("Löschen nicht möglich")

conn.close()