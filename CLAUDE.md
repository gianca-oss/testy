# testy — `emba-quiz`

**Questo progetto è `testy` (repo GitHub: `gianca-oss/testy`). NON è quizzy.**

## Cos'è
Quiz statico a risposta multipla per lo studio degli esami EMBA. L'utente si autovaluta
rispondendo alle domande; c'è una sezione "Da ripassare" che mostra le risposte sbagliate.
Corsi presenti: Marketing (389 domande, 4 moduli - Frey, Scarpi, Pedeliento, Cellino) e
Organizzazione e Lavoro (915 domande, 7 moduli). Le domande di Marketing sono estratte
dalla dispensa d'esame con `scripts/parse_marketing_pdf.py` (testo del PDF via pdfminer):
sono le domande dei "Test di autoverifica" del docente, non domande generate.

## Struttura
- App statica servita da un piccolo `server.js` Express (solo `express.static`).
- Tutto il frontend è in `public/` (`index.html`, `sw.js`, manifest, icone).
- Le domande stanno in `public/data/`: `courses.json` è l'indice dei corsi, un file
  JSON per corso contiene `chapters` e `questions`. Unica fonte di verità: il browser
  li carica via `fetch`, non c'è copia inline né build step.
- Multi-corso: con un solo corso il selettore in home resta nascosto. Errori da
  ripassare e statistiche sono salvati per corso (`...-v1:<id corso>` in localStorage);
  `legacyStorage: true` fa leggere anche le vecchie chiavi globali.
- **Nessuna cartella `api/`, nessun RAG, nessuna chiamata a modelli.**

## Aggiungere un corso
Metti `public/data/<slug>.json` con `{chapters, questions}` e aggiungi la voce in
`public/data/courses.json`. Non serve toccare `index.html`.

## Da non confondere
Esiste un progetto separato `quizzy` (`~/GitHub/quizzy`, repo `gianca-oss/Quizzy`):
è un assistente OCR/RAG che fotografa le domande e trova le risposte via Claude API.
Sono due app diverse in due repo diversi — l'unico legame è che trattano lo stesso
esame. Se il lavoro richiesto riguarda OCR, embeddings, question-bank o la pipeline
`api/`, sei nella cartella sbagliata: quello è quizzy.
