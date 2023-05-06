import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QFont
import pyttsx3
import openai

# Ustawienia API OpenAI
model_engine = "davinci-codex-002"
openai.api_key = get_secret("openai")["api_key"]


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Inicjalizacja silnika TTS
        self.engine = pyttsx3.init()
        self.set_polish_voice()

        # Ustawienia okna
        self.setWindowTitle("ChatGPT TTS")
        self.setFixedSize(500, 200)
        self.setFont(QFont("Arial", 12))

        # Widżety
        self.label = QLabel("Napisz pytanie lub użyj dyktowania:")
        self.label.setAlignment(Qt.AlignCenter)
        self.question_input = QLineEdit()
        self.submit_button = QPushButton("Zapytaj ChatGPT")
        self.submit_button.clicked.connect(self.on_submit)
        self.output_label = QLabel("")

        # Układanie widżetów
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.question_input)
        vbox.addWidget(self.submit_button)
        vbox.addWidget(self.output_label)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(vbox)
        hbox.addStretch()

        self.setLayout(hbox)

    def set_polish_voice(self):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'pl' in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def generate_answer(self, question):
        response = openai.Completion.create(
            engine=model_engine,
            prompt=question,
            max_tokens=150,
            n=1,
            stop=["\n", "Instrukcje:"],
            temperature=0.7,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        answer = response.choices[0].text.strip()
        return answer

    def on_submit(self):
        question = self.question_input.text()
        if not question:
            return
        self.question_input.clear()
        self.output_label.setText("Czekaj, trwa generowanie odpowiedzi...")
        answer = self.generate_answer(question)
        self.output_label.setText(answer)
        self.speak(answer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

#%%
pip install pyqt5
