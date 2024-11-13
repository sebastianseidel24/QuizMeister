import sqlite3

con = sqlite3.connect('quizzy.db')
print("Connected to database succesfully")

# con.execute('CREATE TABLE quizzes (title TEXT NOT NULL)')
# print("Tabelle quizzes erstellt")

# con.execute('CREATE TABLE questions (question_id INTEGER, quiz_id INTEGER, question TEXT NOT NULL, category TEXT NOT NULL, description TEXT, answer TEXT NOT NULL, points FLOAT)')
# print("Tabelle questions erstellt")

# con.execute('DROP TABLE questions')
# con.execute('DROP TABLE quizzes')

con.execute('DELETE FROM quizzes')
print("Daten von quizzes gelöscht")
con.execute('DELETE FROM questions')
print("Daten von questions gelöscht")
con.commit()
# try:
#     con.execute('DELETE FROM quizzes WHERE quiz_id=3')
#     print("Gelöscht")
# except:
#     print("Löschen nicht möglich")

con.close()