import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys


# Funzione per determinare se la persona sta mentendo
def determine_truth(sentiment, sentiment_confidence, microexpression, microexpression_confidence):
    # Definizione delle categorie di emozioni
    negative_emotions = ["sadness", "fear", "anger", "disgust", "contempt"]
    positive_emotions = ["joy", "surprise", "happiness"]
    other_emotions = ["other", "neutral"]  # Emozioni non determinabili

    # Normalizza i valori per confronti insensibili alla maiuscola/minuscola
    sentiment = sentiment.lower() if sentiment else None
    microexpression = microexpression.lower() if microexpression else None

    # Controllo per emozioni "Other" o non rilevate
    if not sentiment or not microexpression:
        return "Non è possibile stabilire se la persona sta mentendo a causa di una confidenza troppo bassa o all'assenza di emozine."
    if sentiment in other_emotions or microexpression in other_emotions:
        return "Non è possibile stabilire se la persona sta mentendo a causa di una confidenza troppo bassa o all'assenza di emozione."

    # Determina se le emozioni corrispondono
    sentiment_is_negative = sentiment in negative_emotions
    sentiment_is_positive = sentiment in positive_emotions

    microexpression_is_negative = microexpression in negative_emotions
    microexpression_is_positive = microexpression in positive_emotions

    # Verifica la corrispondenza delle emozioni
    if (sentiment_is_negative and microexpression_is_negative) or \
       (sentiment_is_positive and microexpression_is_positive):
        return "La persona sta dicendo la verità."
    else:
        return "La persona potrebbe star mentendo."


def load_heavy_dependencies():
    global sentiment_analyzer, MicroExpressionDetector, microexpression_detector
    try:
        update_status("Caricamento delle dipendenze in corso...")
        from sentiment_analysis import SentimentAnalyzer
        from microexpression import MicroExpressionDetector

        if hasattr(sys, "_MEIPASS"):  # Percorso in modalità eseguibile
            model_path = os.path.join(sys._MEIPASS, "models", "samm_micro_expression_model_best_3D.keras")
        else:  # Percorso durante lo sviluppo
            model_path = "models/samm_micro_expression_model_best_3D.keras"

        print(f"Percorso modello: {model_path}")  # Aggiungi un log per il percorso del modello

        sentiment_analyzer = SentimentAnalyzer()
        if os.path.exists(model_path):
            microexpression_detector = MicroExpressionDetector(model_path=model_path)
            update_status("Modelli caricati con successo!")
        else:
            update_status("Errore: Modello non trovato.")
    except Exception as e:
        update_status(f"Errore durante il caricamento: {e}")

# Funzione per aggiornare lo stato dell'interfaccia
def update_status(message):
    analysis_status.set(message)
    root.update_idletasks()


# Funzione per analizzare un video
def analyze_video():
    if not microexpression_detector:
        messagebox.showerror("Errore", "Attendi il caricamento delle dipendenze...")
        return

    # Reset dello stato prima di avviare il caricamento di un nuovo video
    reset_state()

    video_path = filedialog.askopenfilename(title="Carica un video", filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if not video_path:
        messagebox.showwarning("Attenzione", "Nessun video selezionato.")
        return

    # Mostra il nome del video selezionato
    video_name.set(f"Video selezionato: {os.path.basename(video_path)}")

    # Aggiorna l'area di output con il nome del video
    result_output.insert(tk.END, f"Analizzando il video: {os.path.basename(video_path)}\n")
    result_output.insert(tk.END, "-" * 50 + "\n")  # Linea separatrice per migliorare la leggibilità

    # Aggiorna lo stato dell'analisi
    update_status("Analisi in corso...")

    # Avvia i thread per le analisi
    threading.Thread(target=analyze_sentiment, args=(video_path,)).start()
    threading.Thread(target=analyze_microexpressions, args=(video_path,)).start()



# Funzione per analizzare il sentiment
def analyze_sentiment(video_path):
    global sentiment_result, sentiment_confidence, transcript
    try:
        update_status("Analizzando il sentiment dell'audio...")
        transcript, sentiment_result, sentiment_confidence = sentiment_analyzer.process_video_audio(video_path)
        result_output.insert(tk.END, f"\nAudio trascritto in Testo:\n{transcript}\n\n")
        result_output.insert(tk.END, f"Sentiment dell'audio: {sentiment_result} (Confidenza: {sentiment_confidence * 100:.2f}%)\n")
        check_analysis_completion()
    except Exception as e:
        result_output.insert(tk.END, f"\nErrore durante l'analisi del sentiment: {e}\n")
        update_status("Errore durante l'analisi del sentiment.")

# Funzione per analizzare le microespressioni
def analyze_microexpressions(video_path):
    global microexpression_result, microexpression_confidence
    try:
        update_status("Analizzando le microespressioni...")
        microexpression_result, microexpression_confidence = microexpression_detector.analyze_video(video_path)

        if microexpression_confidence > 0:
            result_output.insert(tk.END, f"Microespressione: {microexpression_result} (Confidenza: {microexpression_confidence * 100:.2f}%)\n")
        else:
            result_output.insert(tk.END, f"Microespressione: {microexpression_result} (Confidenza troppo bassa)\n")

        check_analysis_completion()
    except Exception as e:
        result_output.insert(tk.END, f"\nErrore durante l'analisi delle microespressioni: {e}\n")
        update_status("Errore durante l'analisi delle microespressioni.")


# Funzione per verificare se entrambe le analisi sono complete
def check_analysis_completion():
    global sentiment_result, microexpression_result
    if sentiment_result is not None and microexpression_result is not None:
        if sentiment_result == "Non rilevato" or microexpression_confidence == 0.0:
            result = "Non è possibile stabilire se la persona sta mentendo o meno a causa di una confidenza troppo bassa o all'assenza di emozione.."
        else:
            result = determine_truth(sentiment_result, sentiment_confidence, microexpression_result, microexpression_confidence)

        # Inserisci il risultato e applica il colore
        start_index = result_output.index(tk.END)
        result_output.insert(tk.END, f"\nConclusione: {result}\n")
        end_index = result_output.index(tk.END)

        if "verità" in result.lower():
            result_output.tag_add("truth", start_index, end_index)
            result_output.tag_config("truth", foreground="green")
        else:
            result_output.tag_add("lie", start_index, end_index)
            result_output.tag_config("lie", foreground="red")

        # Aggiorna lo stato
        update_status("Analisi completata.")

# Funzione per salvare i risultati in un file
def save_results():
    results = result_output.get("1.0", tk.END).strip()
    if not results:
        messagebox.showwarning("Attenzione", "Nessun risultato da salvare.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(results)
        messagebox.showinfo("Successo", "Risultati salvati con successo.")


# Funzione per resettare lo stato dell'applicazione
def reset_state():
    global sentiment_result, microexpression_result, transcript, sentiment_confidence, microexpression_confidence

    # Reset variabili globali
    sentiment_result = None
    microexpression_result = None
    transcript = ""
    sentiment_confidence = 0.0
    microexpression_confidence = 0.0

    # Reset interfaccia
    result_output.delete("1.0", tk.END)  # Ripulisci l'area di output
    video_name.set("Nessun video selezionato.")  # Reset nome video
    update_status("Pronto per una nuova analisi.")  # Aggiorna lo stato



# Inizializza l'interfaccia
root = tk.Tk()
root.title("Analisi Video: Sentiment & Microespressioni")
root.geometry("700x700")

# Variabili globali
analysis_status = tk.StringVar()
analysis_status.set("Inizializzazione...")
video_name = tk.StringVar()
video_name.set("Nessun video selezionato.")
microexpression_detector = None
sentiment_result = None
microexpression_result = None

# Layout superiore
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

btn_analyze_video = tk.Button(frame_top, text="Carica e Analizza Video", command=analyze_video)
btn_analyze_video.grid(row=0, column=1, padx=5)

btn_save_results = tk.Button(frame_top, text="Salva Risultati", command=save_results)
btn_save_results.grid(row=0, column=2, padx=5)

label_status = tk.Label(root, textvariable=analysis_status, fg="black", font=("Arial", 12, "bold"))
label_status.pack(pady=5)

# Area di output
frame_output = tk.Frame(root)
frame_output.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(frame_output)
scrollbar.pack(side="right", fill="y")

result_output = tk.Text(frame_output, wrap="word", yscrollcommand=scrollbar.set, state="normal", height=25)
result_output.pack(fill="both", expand=True)
scrollbar.config(command=result_output.yview)

# Avvia il caricamento delle dipendenze in un thread separato
threading.Thread(target=load_heavy_dependencies, daemon=True).start()

# Avvio dell'interfaccia
root.mainloop()
