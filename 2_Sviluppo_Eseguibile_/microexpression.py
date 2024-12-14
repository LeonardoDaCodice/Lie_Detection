import cv2
import numpy as np
from tensorflow.keras.models import load_model


class MicroExpressionDetector:
    def __init__(self, model_path, sequence_length=5, frame_size=(112, 112), threshold=0.4):
        """
        Inizializza il rilevatore di microespressioni.
        :param model_path: Percorso del modello addestrato.
        :param sequence_length: Numero di frame per sequenza.
        :param frame_size: Dimensione dei frame (altezza, larghezza).
        :param threshold: Soglia di confidenza per accettare una predizione.
        """
        self.model = load_model(model_path)
        self.sequence_length = sequence_length
        self.frame_size = frame_size
        self.threshold = threshold
        self.emotion_mapping = {
            0: "Happiness",
            1: "Surprise",
            2: "Anger",
            3: "Sadness",
            4: "Fear",
            5: "Disgust",
            6: "Other",
            7: "Contempt"
        }

    def extract_frame_sequences(self, video_path):
        """
        Estrae sequenze di frame da un video.
        :param video_path: Percorso del video.
        :return: Lista di sequenze di frame.
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        sequences = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            #Utilizzare per il modello senza il finetuning.
            # Converti il frame in scala di grigi
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converti in scala di grigi
            #frame = cv2.resize(frame, self.frame_size)  # Ridimensiona a (112, 112)
            #frame = np.expand_dims(frame, axis=-1)  # Aggiungi un canale per la scala di grigi
            #frame = frame.astype("float32") / 255.0  # Normalizza i valori
            #frames.append(frame)


            #Utilizzare per il modello ottenuto con l'addestramento con il fine-tuning.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converti in RGB
            frame = cv2.resize(frame, self.frame_size)  # Ridimensiona a (112, 112)
            frame = frame.astype("float32") / 255.0  # Normalizza i valori
            frames.append(frame)
            #--------------------------------------#

            # Crea sequenze di lunghezza fissa
            if len(frames) == self.sequence_length:
                sequences.append(np.array(frames))
                frames.pop(0)

        cap.release()
        sequences = np.array(sequences)
        print(f"Forma delle sequenze estratte: {sequences.shape}")  # Debug
        return sequences

    def analyze_video_with_confidence(self, sequences):
        """
        Analizza un video e restituisce la microespressione predominante considerando la confidenza aggregata.
        :param sequences: Sequenze di frame estratte dal video.
        :return: (emozione predominante, confidenza media)
        """
        emotion_confidences = {emotion: [] for emotion in self.emotion_mapping.values()}

        for i, sequence in enumerate(sequences):
            sequence = np.expand_dims(sequence, axis=0)  # Aggiungi batch dimension
            pred = self.model.predict(sequence)
            max_confidence = np.max(pred)
            emotion = self.emotion_mapping[np.argmax(pred)]

            print(f"Sequenza {i + 1}: Emozione: {emotion}, Confidenza: {max_confidence:.2f}")

            # Registra la confidenza solo se supera la soglia
            if max_confidence >= self.threshold:
                emotion_confidences[emotion].append(max_confidence)

        # Calcola l'emozione predominante
        aggregated_confidences = {emotion: np.mean(conf) if conf else 0 for emotion, conf in
                                  emotion_confidences.items()}
        print("Confidenze aggregate:", aggregated_confidences)

        predominant_emotion = max(aggregated_confidences, key=aggregated_confidences.get)
        highest_confidence = aggregated_confidences[predominant_emotion]

        if highest_confidence > 0.0:
            print(f"Emozione predominante: {predominant_emotion}, Confidenza media: {highest_confidence:.2f}")
            return predominant_emotion, highest_confidence
        else:
            print("Nessuna microespressione rilevata.")
            return "No Microexpression", 0

    def analyze_video(self, video_path):
        """
        Analizza un video e restituisce la microespressione predominante.
        :param video_path: Percorso del video.
        :return: (emozione predominante, confidenza media)
        """
        sequences = self.extract_frame_sequences(video_path)
        if len(sequences) > 0:
            return self.analyze_video_with_confidence(sequences)
        else:
            return "No Microexpression", 0
