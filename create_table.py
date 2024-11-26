import sqlite3

con = sqlite3.connect('quizzy.db')
print("Connected to database succesfully")

# con.execute('CREATE TABLE quizzes (title TEXT NOT NULL)')
# print("Tabelle quizzes erstellt")

# con.execute('CREATE TABLE questions (quiz_id INTEGER NOT NULL, question_id INTEGER NOT NULL, question TEXT NOT NULL, category TEXT NOT NULL, description TEXT, image TEXT, answer TEXT NOT NULL, points NUMERIC NOT NULL, PRIMARY KEY (quiz_id, question_id))')
# print("Tabelle questions erstellt")

# con.execute('DROP TABLE questions')
# con.execute('DROP TABLE quizzes')

#Tabelleninhalte löschen
# con.execute('DELETE FROM quizzes')
# print("Daten von quizzes gelöscht")
# con.execute('DELETE FROM questions')
# print("Daten von questions gelöscht")
# con.commit()

# con.row_factory = sqlite3.Row
# cur = con.cursor()
# cur.execute("SELECT * FROM questions WHERE quiz_id = 2")
# #quiz = cur.fetchall()
# for row in cur.fetchall():
#     print(row[0])
#     print(row[1])
#     print(row[2])
#     print(row[3])
#     print(row[4])
#     print(row[5])
#     print(row[6])

# try:
#     con.execute('DELETE FROM quizzes WHERE quiz_id=3')
#     print("Gelöscht")
# except:
#     print("Löschen nicht möglich")

# con.execute("ALTER TABLE quizzes ADD number_of_questions INTEGER")

cur = con.cursor()
quiz_id = 1
question_id = 4
question_text = "Frage 4"
category = "Geschichte"
description = "Beschreibung 4"
answer = "Antwort 4"
points = 2

cur.execute("""INSERT INTO questions (question_id, quiz_id, question, category, description, answer, points) 
            VALUES (?,?,?,?,?,?,?) 
            ON CONFLICT (quiz_id, question_id) 
            DO UPDATE SET question = ?, category = ?, description = ?, answer = ?, points = ?;""", 
            (question_id, quiz_id, question_text, category, description, answer, points, question_text, category, description, answer, points))
            
con.commit()
print("Das hat geklappt")


con.close()