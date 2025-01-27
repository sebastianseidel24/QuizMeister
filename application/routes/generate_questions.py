from application import app
from flask import request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Route um Fragen mit Gemini generieren zu lassen (nach Klick auf Button)
@app.route("/generate_questions", methods=["POST"])
def process_question_generation():
    try:
        # JSON-Daten von der Anfrage lesen
        data = request.get_json()

        # Lese die Daten aus dem JSON-Objekt
        number_of_questions = data.get("numberOfQuestions")
        difficulty = data.get("difficulty")
        categories = data.get("categories")
        categories = ", ".join(categories)

        # Fragen generieren lassen
        generated_questions = generate_questions(number_of_questions, categories, difficulty)
        
        # Sende eine Antwort zurück
        return jsonify({"questions": generated_questions})

    except Exception as e:
        # Fehler abfangen und eine Fehlermeldung zurückgeben
        return jsonify({"error": f"Ein Fehler ist aufgetreten: {str(e)}"}), 400

# Gemini-API Konfiguration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")
GENERATION_CONFIG  = genai.GenerationConfig(response_mime_type="application/json")

# Mittels Gemini-API Fragen generieren lassen
def generate_questions(number_of_questions: int, categories: str, difficulty: str):
    if (number_of_questions == "1"):
        prompt = f'''
                Erstelle eine Liste, die aus genau einer kreativen Quiz-Frage für ein Pub-Quiz besteht. Die Frage muss folgende Felder enthalten:

                1. "question_id" (Typ: Integer): 0  
                2. "category" (Typ: String): Eine zufällig gewählte Kategorie aus den folgenden Optionen: {categories}.  
                3. "question_text" (Typ: String): Der Fragetext, formuliert als vollständiger Satz, ohne die Verwendung von Anführungszeichen.  
                4. "answer" (Typ: String): Die korrekte Antwort auf die Frage, ebenfalls ohne die Verwendung von Anführungszeichen.

                Zusätzliche Anforderungen:  
                - Die Frage sollten eine {difficulty} Schwierigkeit haben.
                - Nutze eine klare und präzise Sprache.
                
                Beispiel-Ausgabe:
                [{{
                    "question_id": 0,
                    "category": "Geografie",
                    "question_text": "Welches ist das größte Land der Welt nach Fläche?",
                    "answer": "Russland"
                    }}]
                '''
    else:
        prompt = f'''
                Erstelle eine Liste, die aus genau {number_of_questions} vielseitigen und kreativen Quiz-Fragen für ein Pub-Quiz besteht. Jede Frage muss folgende Felder enthalten:

                1. "question_id" (Typ: Integer): Eine fortlaufende ID, beginnend mit 0.  
                2. "category" (Typ: String): Eine zufällig gewählte Kategorie aus den folgenden Optionen: {categories}.  
                3. "question_text" (Typ: String): Der Fragetext, formuliert als vollständiger Satz, ohne die Verwendung von Anführungszeichen.  
                4. "answer" (Typ: String): Die korrekte Antwort auf die Frage, ebenfalls ohne die Verwendung von Anführungszeichen.

                Zusätzliche Anforderungen:  
                - Die Fragen sollten eine {difficulty} Schwierigkeit haben.  
                - Vermeide Wiederholungen in den Fragen oder Antworten.
                - Nutze eine klare und präzise Sprache.
                
                Beispiel-Ausgabe:
                [
                    {{
                    "question_id": 0,
                    "category": "Geografie",
                    "question_text": "Welches ist das größte Land der Welt nach Fläche?",
                    "answer": "Russland"
                    }},
                    {{
                    "question_id": 1,
                    "category": "Musik",
                    "question_text": "Welcher Künstler hat das Album Thriller veröffentlicht?",
                    "answer": "Michael Jackson"
                    }},
                    ...
                ]
                '''
    print(prompt)
    
    generated_questions = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG).text
    
    generated_questions = generated_questions[generated_questions.index("["):] # Falls die Antwort nicht mit einer Liste beginnt, wird der Anfang der Liste gesucht
    print(generated_questions)
    return(eval(generated_questions)) # Die Antwort wird in ein Python-Objekt (Liste) umgewandelt und zurückgegeben
