from googletrans import Translator
from transformers import pipeline
import speech_recognition as sr
import moviepy as mp

class SentimentAnalyzer:
    def __init__(self, model_name="j-hartmann/emotion-english-distilroberta-base"):
        """
        Inizializza il modello di sentiment analysis e il traduttore.
        :param model_name: Nome del modello Hugging Face.
        """
        self.emotion_pipeline = pipeline("text-classification", model=model_name, return_all_scores=True)
        self.translator = Translator()

    def transcribe_audio(self, video_path):
        """
        Estrae l'audio da un video e lo trascrive in testo.
        :param video_path: Percorso del video.
        :return: Testo trascritto (stringa).
        """
        try:
            # Estrai audio dal video
            video = mp.VideoFileClip(video_path)
            audio_path = "temp_audio.wav"
            video.audio.write_audiofile(audio_path)

            # Utilizza SpeechRecognition per la trascrizione
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="it-IT")

                return text
        except Exception as e:
            print(f"Errore nella trascrizione audio: {e}")
            return None

    def translate_text(self, text):
        """
        Traduci il testo dall'italiano all'inglese.
        :param text: Testo in italiano.
        :return: Testo tradotto in inglese.
        """
        try:
            return self.translator.translate(text, src="it", dest="en").text
        except Exception as e:
            print(f"Errore nella traduzione: {e}")
            return None

    def analyze_sentiment(self, text):
        """
        Analizza il sentimento di un testo.
        :param text: Testo da analizzare.
        :return: Emozione predominante e confidenza.
        """
        try:
            results = self.emotion_pipeline(text)
            sorted_results = sorted(results[0], key=lambda x: x["score"], reverse=True)
            dominant_emotion = sorted_results[0]["label"]
            confidence = sorted_results[0]["score"]
            return dominant_emotion, confidence
        except Exception as e:
            print(f"Errore nell'analisi del sentimento: {e}")
            return None, 0

    def process_video_audio(self, video_path):
        """
        Elabora l'audio di un video e restituisce la trascrizione e l'analisi del sentimento.
        :param video_path: Percorso del video.
        :return: Trascrizione, emozione predominante, confidenza.
        """
        # Trascrivi l'audio
        transcript = self.transcribe_audio(video_path)
        if not transcript:
            return "Nessuna trascrizione disponibile", "Non rilevato", 0.0

        # Traduci il testo
        translated_text = self.translate_text(transcript)
        if not translated_text:
            return transcript, "Errore nella traduzione del testo", 0.0

        # Analizza il sentimento
        emotion, confidence = self.analyze_sentiment(translated_text)
        return transcript, emotion, confidence

