import speech_recognition as sr
import pyttsx3
# from openai import openai_secret_manager
import openai
import tkinter as tk
import os

engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Krzysztof')
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    print("Nie udało się odczytać wartości zmiennej środowiskowej OPENAI_API_KEY.")
    exit(1)
openai.api_key = api_key
model_engine = "text-davinci-003"


# Definicja funkcji, która będzie czytać tekst na głos
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Definicja funkcji, która będzie rozpoznawać mowę i zwracać tekst
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Rozpocznij dyktowanie...")
        audio = r.listen(source)

    try:
        print("Rozpoznawanie...")
        text = r.recognize_google(audio, language='pl-PL')
        print("Tekst rozpoznany: " + text)
        return text
    except sr.UnknownValueError:
        print("Nie udało się rozpoznać mowy.")
        return ""
    except sr.RequestError as e:
        print("Błąd połączenia z serwerem Google; {0}".format(e))
        return ""


# Definicja funkcji, która wywoła API OpenAI i pobierze odpowiedź
def generate_answer(question):
    response = openai.Completion.create(
        engine=model_engine,
        prompt=(f"Q: {question}\nA:"),
        temperature=0.7,
        max_tokens=150,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0,
    )

    answer = response.choices[0].text.strip()
    return answer


# Definicja funkcji, która zostanie wywołana po wciśnięciu przycisku
def ask_question():
    # Odczytanie pytania z pola tekstowego
    question = question_entry.get()

    # Wywołanie API OpenAI i pobranie odpowiedzi
    answer = generate_answer(question)

    # Wyświetlenie odpowiedzi w polu tekstowym i odczytanie jej na głos
    answer_text.delete(1.0, tk.END)
    answer_text.insert(tk.END, answer)
    speak(answer)


# Konfiguracja interfejsu użytkownika
root = tk.Tk()
root.title("ChatGPT")

# Pole tekstowe do wprowadzenia pytania
question_label = tk.Label(root, text="Wpisz pytanie lub użyj dyktowania:")
question_label.pack()
question_entry = tk.Entry(root, width=50)
question_entry.pack()

# Przycisk do wysłania pytania
ask_button = tk.Button(root, text="Zapytaj ChatGPT", command=ask_question)
ask_button.pack()

# Pole tekstowe do wyświetlenia odpowiedzi
answer_label = tk.Label(root, text="Odpowiedź:")
answer_label.pack()
answer_text = tk.Text(root, height=10)
answer_text.pack()

root.mainloop()

#%%
