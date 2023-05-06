import sys
import os
import openai
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
        # OpenAI Whisper ASR
        from openai.api import API
        from openai.models import ASR

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            print("Nie udało się odczytać wartości zmiennej środowiskowej OPENAI_API_KEY.")
            exit(1)
        client = API(api_key)
        model_id = "whisper-0206"
        lang = "pl"
        sample_rate = 44100
        with sr.Microphone() as source:
            print("Say something!")
            audio = recognizer.listen(source, timeout=5)
            raw_audio = audio.get_raw_data(convert_rate=sample_rate, convert_width=2)
            response = client.tasks.create(
                model=model_id, inputs={"audio": raw_audio}, data={"language": lang}
            )
            question = response.choices[0].text
            print(question)

            self.input.setText(question)
            self.generate_answer()

    def generate_answer(self):
        question = self.input.text()
        if not question:
            return
        self.input.clear()
        self.output_label.setText("Czekaj, trwa generowanie odpowiedzi...")
        answer = self.get_gpt_answer(question)
        self.output_label.setText(answer)
        self.speak

#%%
