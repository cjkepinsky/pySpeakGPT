import sys
import os
import openai
import speech_recognition as sr
import pyttsx3, pyaudio
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper as w
import queue
import tempfile
import os
import threading
import click
import torch
import numpy as np


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
        # self.output_label.setStyleSheet("max-width: 500px; word-wrap: break-word;")
        self.output_label.setWordWrap(True)
        self.output_layout.addWidget(self.output_label)
        self.layout.addLayout(self.output_layout)
        self.setLayout(self.layout)

    # while True:
    #     print(result_queue.get())

    def dictate_question(self):
        energy = 300
        pause = 0.8
        dynamic_energy = False
        english = False
        save_file = False
        verbose = True
        temp_dir = None

        audio_model = w.load_model('base')
        audio_queue = queue.Queue()
        result_queue = queue.Queue()

        threading.Thread(target=self.record_audio,
                         args=(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir)).start()
        threading.Thread(target=self.transcribe_forever,
                         args=(audio_queue, result_queue, audio_model, english, verbose, save_file)).start()

        history = ""

        while True:
            try:
                q = result_queue.get()
                q = q['text']
                history += q
                self.output_label.setText(history)
                # self.input.setPlaceholderText(q)
                # print("q: ", q['text'])
                # self.generate_answer(q)
                answer = self.get_gpt_answer(q)
                history += answer
                self.output_label.setText(history)
                self.speak(answer)
            except queue.Empty:
                continue

    def speak(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        pl_voice = None
        for voice in voices:
            if "pl-PL" in voice.id:
            # if "zosia" in voice.id.lower():
                pl_voice = voice
                break
        if not pl_voice:
            return
        engine.setProperty("voice", pl_voice.id)
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()

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

    def record_audio(self, audio_queue, energy, pause, dynamic_energy, save_file, temp_dir):
        # load the speech recognizer and set the initial energy threshold and pause threshold
        r = sr.Recognizer()
        r.energy_threshold = energy
        r.pause_threshold = pause
        r.dynamic_energy_threshold = dynamic_energy

        with sr.Microphone(sample_rate=16000) as source:
            print("Say something!")
            i = 0
            while True:
                # get and save audio to wav file
                audio = r.listen(source)
                if save_file:
                    data = io.BytesIO(audio.get_wav_data())
                    audio_clip = AudioSegment.from_file(data)
                    filename = os.path.join(temp_dir, f"temp{i}.wav")
                    audio_clip.export(filename, format="wav")
                    audio_data = filename
                else:
                    torch_audio = torch.from_numpy(
                        np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                    audio_data = torch_audio

                audio_queue.put_nowait(audio_data)
                i += 1

    def transcribe_forever(self, audio_queue, result_queue, audio_model, english, verbose, save_file):
        while True:
            audio_data = audio_queue.get()
            if english:
                result = audio_model.transcribe(audio_data, language='english')
            else:
                result = audio_model.transcribe(audio_data, language='polish')

            if not verbose:
                predicted_text = result["text"]
                result_queue.put_nowait("You said: " + predicted_text)
            else:
                result_queue.put_nowait(result)

            if save_file:
                os.remove(audio_data)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ChatGPT")
    app.setPalette(QPalette(QColor("#ffffff")))
    app.setStyle("Fusion")
    widget = ChatGPT()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())
    # app.exec()

# %%
