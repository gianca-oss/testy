# testy — `emba-quiz`

**Questo progetto è `testy` (repo GitHub: `gianca-oss/testy`). NON è quizzy.**

## Cos'è
Quiz statico a risposta multipla per lo studio dell'esame EMBA "Organizzazione e Lavoro".
L'utente si autovaluta rispondendo alle domande; c'è una sezione "Da ripassare" che
mostra le risposte sbagliate.

## Struttura
- App statica servita da un piccolo `server.js` Express (~49 righe).
- Tutto il frontend è in `public/` (`index.html`, `sw.js`, manifest, icone).
- Le domande sono nell'`index.html` / dati statici. **Nessuna cartella `api/`, nessun
  RAG, nessuna chiamata a modelli.**

## Da non confondere
Esiste un progetto separato `quizzy` (`~/GitHub/quizzy`, repo `gianca-oss/Quizzy`):
è un assistente OCR/RAG che fotografa le domande e trova le risposte via Claude API.
Sono due app diverse in due repo diversi — l'unico legame è che trattano lo stesso
esame. Se il lavoro richiesto riguarda OCR, embeddings, question-bank o la pipeline
`api/`, sei nella cartella sbagliata: quello è quizzy.
