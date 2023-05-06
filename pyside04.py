import sys
import os
import openai
import pyttsx3
from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
# import io
# from pydub import AudioSegment
# import whisper as w
# import queue
# import tempfile
# import threading
# import torch
# import numpy as np
import speech_recognition as sr


class SpeechRecognitionWorker(QObject):
    recognized = Signal(str)

    def __init__(self):
        super().__init__()

        self.r = sr.Recognizer()
        self.r.energy_threshold = 300
        self.r.pause_threshold = 0.8
        self.r.dynamic_energy_threshold = False

        with sr.Microphone(sample_rate=16000) as source:
            self.source = source

    def run(self):
        while True:
            audio = self.r.listen(self.source, timeout=None)
            try:
                question = self.r.recognize_google(audio, language="pl-PL")
                self.recognized.emit(question)
            except sr.UnknownValueError:
                pass


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
        self.setWindowTitle("Speak GPT")
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
        self.output_label.setWordWrap(True)
        self.output_layout.addWidget(self.output_label)
        self.layout.addLayout(self.output_layout)
        self.setLayout(self.layout)

        self.speech_recognition_worker = SpeechRecognitionWorker()
        self.speech_recognition_worker_thread = QThread()
        self.speech_recognition_worker.moveToThread(self.speech_recognition_worker_thread)
        self.speech_recognition_worker.recognized.connect(self.on_recognized)
        self.speech_recognition_worker_thread.started.connect(self.speech_recognition_worker.run)
        self.speech_recognition_worker_thread.start()

    def on_recognized(self, question):
        self.input.setText(question)
        self.generate_answer()

    def dictate_question(self):
        question = self.input.text()
        if question:
            self.generate_answer()
        self.input.setText("Czekaj, trwa rozpoznawanie mowy...")


    def generate_answer(self, question):
        # question = self.input.text()
        if not question:
            return
        # self.input.clear()
        # self.output_label.setText("Czekaj, trwa generowanie odpowiedzi...")
        answer = self.get_gpt_answer(question)
        # print("answer: ", answer)
        self.output_label.setText(self.output_label.getText() + answer)
        # self.speak(answer)


    def get_gpt_answer(self, question):
        # openai.api_key = os.environ["OPENAI_API_KEY"]
        # prompt = f"Q: {question}\nA:"
        # completions = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {
        #             "role": "user"
        #             , "content": question
        #         }
        #     ]
        #     # max_tokens=1024,
        #     # n=1,
        #     # stop=None,
        #     # temperature=0.7,
        # )
        print("Q: ", question)

        import os
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            print("Nie udało się odczytać wartości zmiennej środowiskowej OPENAI_API_KEY.")
            exit(1)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=0.9,
            max_tokens=1060,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )

        print("A: ", response.choices[0].text)

        # print("message: ", completions.choices[0].message.content)
        # message = completions.choices[0].message.content.strip()
        return response.choices[0].text

    def speak(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        pl_voice = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ChatGPT")
    app.setPalette(QPalette(QColor("#ffffff")))
    app.setStyle("Fusion")
    widget = ChatGPT()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())

#%%

#%%
