import sys
import os
import openai
import speech_recognition as sr
import pyttsx3, pyaudio
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit


class ChatGPT(QWidget):
    def __init__(self):
        super().__init__()
        green = "#00aa00"
        btnStylesheet = f"""
            background-color: {green};
            color: #ffffff;
            padding: 5px;
            border-radius: 5px;
        """
        self.setWindowTitle("ChatGPT")
        self.setStyleSheet(f"""
            background-color: #000000;
            color: {green};
        """)
        self.layout = QVBoxLayout()
        self.question_layout = QHBoxLayout()
        self.output_layout = QVBoxLayout()
        self.input = QLineEdit()
        self.input.setStyleSheet(f"""
            border: 2px solid {green};
            border-radius: 5px;
            padding: 5px;
        """)
        self.input.setPlaceholderText("Napisz pytanie lub użyj dyktowania")
        self.ask_button = QPushButton("Zapytaj ChatGPT")
        self.ask_button.clicked.connect(self.generate_answer)
        self.ask_button.setStyleSheet(btnStylesheet)
        self.dictate_button = QPushButton("Dictate")
        self.dictate_button.setStyleSheet(btnStylesheet)
        self.dictate_button.clicked.connect(self.dictate_question)
        self.question_layout.addWidget(self.input)
        self.question_layout.addWidget(self.dictate_button)
        self.question_layout.addWidget(self.ask_button)
        self.layout.addLayout(self.question_layout)
        self.output_label = QLabel("")
        # self.output_label.setStyleSheet("max-width: 500px; word-wrap: break-word;")
        self.output_label.setWordWrap(True)
        self.output_layout.addWidget(self.output_label)
        self.layout.addLayout(self.output_layout)
        self.setLayout(self.layout)

    def dictate_question(self):
        # import openai_whisper01
        # from openai_whisper import

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("source: ", source)
            audio = recognizer.listen(source, timeout=5)

        try:
            question = recognizer.recognize_google(audio, language="pl-PL")
            self.input.setText(question)
            self.generate_answer()

        except sr.UnknownValueError:
            self.input.setText("Could not understand audio")

        except sr.RequestError as e:
            self.output_label.setText(
                f"Could not request results from Google Speech Recognition service; {e}"
            )

    def generate_answer(self):
        question = self.input.text()
        if not question:
            return
        self.input.clear()
        self.output_label.setText("Czekaj, trwa generowanie odpowiedzi...")
        answer = self.get_gpt_answer(question)
        self.output_label.setText(answer)
        self.speak(answer)

    def get_gpt_answer(self, question):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            print("Nie udało się odczytać wartości zmiennej środowiskowej OPENAI_API_KEY.")
            exit(1)
        prompt = f"Q: {question}\nA:"
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
        message = completions.choices[0].text.strip()
        return message

    def speak(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        print(voices)
        pl_voice = None
        for voice in voices:
            if "krzysztof" in voice.id.lower():
                pl_voice = voice
                break
        if not pl_voice:
            return
        engine.setProperty("voice", pl_voice.id)
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ChatGPT")
    app.setPalette(QPalette(QColor("#ffffff")))
    app.setStyle("Fusion")
    widget = ChatGPT()
    widget.resize(800, 200)
    widget.show()
    sys.exit(app.exec_())

#%%
