import sqlite3

con = sqlite3.connect('quizzy.db')
print("Connected to database succesfully")

# con.execute('CREATE TABLE quizzes (title TEXT NOT NULL)')
# print("Tabelle quizzes erstellt")

# con.execute('CREATE TABLE questions (question_id INTEGER, quiz_id INTEGER, question TEXT NOT NULL, category TEXT NOT NULL, description TEXT, answer TEXT NOT NULL, points FLOAT)')
# print("Tabelle questions erstellt")

# con.execute('DROP TABLE questions')
# con.execute('DROP TABLE quizzes')

#Tabelleninhalte löschen
# con.execute('DELETE FROM quizzes')
# print("Daten von quizzes gelöscht")
# con.execute('DELETE FROM questions')
# print("Daten von questions gelöscht")
# con.commit()

con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("SELECT * FROM questions WHERE quiz_id = 2")
#quiz = cur.fetchall()
for row in cur.fetchall():
    print(row[0])
    print(row[1])
    print(row[2])
    print(row[3])
    print(row[4])
    print(row[5])
    print(row[6])

# try:
#     con.execute('DELETE FROM quizzes WHERE quiz_id=3')
#     print("Gelöscht")
# except:
#     print("Löschen nicht möglich")

con.close()