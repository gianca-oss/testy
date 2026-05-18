const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

app.get('/api/questions', (req, res) => {
  const questionsPath = path.join(__dirname, 'data', 'questions.json');
  const data = JSON.parse(fs.readFileSync(questionsPath, 'utf-8'));

  const { chapter, count } = req.query;

  let questions = data.questions;

  if (chapter && chapter !== 'all') {
    questions = questions.filter(q => q.chapter === parseInt(chapter));
  }

  if (count) {
    const n = parseInt(count);
    questions = shuffleArray([...questions]).slice(0, n);
  } else {
    questions = shuffleArray([...questions]);
  }

  res.json({ questions, chapters: data.chapters });
});

app.get('/api/chapters', (req, res) => {
  const questionsPath = path.join(__dirname, 'data', 'questions.json');
  const data = JSON.parse(fs.readFileSync(questionsPath, 'utf-8'));
  res.json({ chapters: data.chapters });
});

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

app.listen(PORT, () => {
  console.log(`EMBA Quiz running on http://localhost:${PORT}`);
});
