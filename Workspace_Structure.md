# Struttura della Cartella del Workspace

La struttura del workspace e' organizzata come segue:

## Cartella Principale: `Lie_Detection`

### Sottocartelle

1. **Notebook_Scripts**

   - Nuova cartella contenente notebook dedicati al preprocessing e all'analisi:
     - **SAMM_Preprocessing_and_Training.ipynb**: Notebook per il preprocessing del dataset SAMM e l'addestramento del modello.
     - **Sentiment_Analysis_Testo.ipynb**: Notebook per l'analisi del sentimento nei testi.

2. **\_Sviluppo_Eseguibile\_**

   - Nuova cartella contenente il codice Python per l'integrazione dei modelli e l'analisi dei video:
     - **main.py**: Punto di avvio principale del sistema.
     - **microexpression.py**: Script per l'analisi delle microespressioni facciali.
     - **sentiment_analysis.py**: Script per l'analisi del sentimento del testo.

3. **Modelli_Ai\_&_Eseguibili**

   - Contiene 3 sottocartelle, ognuna delle quali include un modello addestrato con una specifica architettura e il relativo eseguibile:
     - `CNN3D_LSTM`
       - Modello addestrato con architettura CNN3D_LSTM
       - File eseguibile associato al modello
     - `CNN3D_LSTM_Finetuning_ResNet50`
       - Modello addestrato con architettura CNN3D_LSTM_Finetuning di ResNet50
       - File eseguibile associato al modello
     - `CNN3D_No_Finetuning`
       - Modello addestrato con architettura CNN3D_No_Finetuning
       - File eseguibile associato al modello

4. **Risultati_Dei_Test**

   - Contiene 26 sottocartelle, ognuna rappresentante un video testato. Ogni sottocartella include:
     - 3 file `.txt` che contengono i risultati ottenuti sottoponendo il video al test utilizzando i 3 eseguibili corrispondenti ai diversi modelli:
       - Risultati del modello `CNN3D_LSTM`
       - Risultati del modello `CNN3D_LSTM_Finetuning_ResNet50`
       - Risultati del modello `CNN3D_No_Finetuning`
   - Inoltre, include i seguenti file generali:
     - **Domande.txt**: File di testo contenente le domande sottoposte ai soggetti durante i test.
     - **Risultati.xlsx**: File Excel che riassume i risultati in maniera tabellare.
       - Contiene 3 fogli di lavoro:
         - `CNN3D`
           - Risultati ottenuti con l'eseguibile che implementa il modello `CNN3D`
         - `CNN3D_LSTM`
           - Risultati ottenuti con l'eseguibile che implementa il modello `CNN3D_LSTM`
         - `CNN3D+Fine_Tuning`
           - Risultati ottenuti con l'eseguibile che implementa il modello `CNN3D_LSTM_Finetuning_ResNet50`

### File nella Directory Principale

1. **Schema.png**
   - Immagine contenente uno schema che riassume i processi eseguiti dal sistema:
     - Input: Video
     - Elaborazione tramite i modelli
     - Output: Risultati delle analisi delle microespressioni.

---
