const $ = (s) => document.querySelector(s);

const state = {
  questions: [],
  chapters: [],
  current: 0,
  answers: [],
  score: 0,
};

async function init() {
  const res = await fetch('/api/chapters');
  const data = await res.json();
  state.chapters = data.chapters;

  const sel = $('#chapter-select');
  data.chapters.forEach(ch => {
    const opt = document.createElement('option');
    opt.value = ch.id;
    opt.textContent = `${ch.icon} ${ch.title}`;
    sel.appendChild(opt);
  });

  loadStats();
}

$('#start-btn').addEventListener('click', startQuiz);
$('#next-btn').addEventListener('click', nextQuestion);
$('#quit-btn').addEventListener('click', () => showScreen('home'));
$('#retry-btn').addEventListener('click', () => showScreen('home'));
$('#review-btn').addEventListener('click', toggleReview);
$('#reset-stats-btn').addEventListener('click', resetStats);

async function startQuiz() {
  const chapter = $('#chapter-select').value;
  const countVal = $('#count-select').value;
  const count = countVal === 'all' ? '' : countVal;

  const params = new URLSearchParams();
  if (chapter !== 'all') params.set('chapter', chapter);
  if (count) params.set('count', count);

  const res = await fetch(`/api/questions?${params}`);
  const data = await res.json();

  state.questions = data.questions;
  state.current = 0;
  state.answers = [];
  state.score = 0;

  if (state.questions.length === 0) {
    alert('Nessuna domanda disponibile per questa selezione.');
    return;
  }

  showScreen('quiz');
  renderQuestion();
}

function renderQuestion() {
  const q = state.questions[state.current];
  const total = state.questions.length;
  const chapter = state.chapters.find(c => c.id === q.chapter);

  $('#q-counter').textContent = `${state.current + 1} / ${total}`;
  $('#progress-fill').style.width = `${((state.current + 1) / total) * 100}%`;
  $('#q-chapter').textContent = chapter ? `${chapter.icon} ${chapter.title}` : '';
  $('#q-text').textContent = q.question;
  $('#next-btn').style.display = 'none';

  const container = $('#options-container');
  container.innerHTML = '';

  document.querySelectorAll('.explanation').forEach(el => el.remove());

  Object.entries(q.options).forEach(([letter, text]) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.innerHTML = `<span class="option-letter">${letter}</span>${text}`;
    btn.addEventListener('click', () => selectAnswer(letter, btn));
    container.appendChild(btn);
  });
}

function selectAnswer(letter, btn) {
  if (btn.classList.contains('disabled')) return;
  const q = state.questions[state.current];
  const isCorrect = letter === q.correct;

  if (isCorrect) state.score++;
  state.answers.push({ questionId: q.id, selected: letter, correct: q.correct, isCorrect });

  const buttons = document.querySelectorAll('.option-btn');
  buttons.forEach(b => {
    b.classList.add('disabled');
    const bLetter = b.querySelector('.option-letter').textContent;
    if (bLetter === q.correct) b.classList.add('correct');
    if (bLetter === letter && !isCorrect) b.classList.add('wrong');
  });

  const explanation = document.createElement('div');
  explanation.className = 'explanation';
  explanation.textContent = q.explanation;
  $('#options-container').after(explanation);

  if (state.current < state.questions.length - 1) {
    $('#next-btn').style.display = 'block';
  } else {
    setTimeout(showResults, 1200);
  }
}

function nextQuestion() {
  state.current++;
  renderQuestion();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showResults() {
  const total = state.questions.length;
  const pct = Math.round((state.score / total) * 100);

  let emoji, message;
  if (pct >= 90) { emoji = '🏆'; message = 'Eccellente! Padronanza totale del materiale.'; }
  else if (pct >= 75) { emoji = '🎯'; message = 'Ottimo lavoro! Buona preparazione.'; }
  else if (pct >= 60) { emoji = '📚'; message = 'Discreto, ma c\'è margine di miglioramento.'; }
  else if (pct >= 40) { emoji = '💪'; message = 'Serve più studio. Non mollare!'; }
  else { emoji = '📖'; message = 'Ripassare il materiale e riprovare.'; }

  $('#results-emoji').textContent = emoji;
  $('#results-score').textContent = `${pct}%`;
  $('#results-detail').textContent = `${state.score} su ${total} risposte corrette`;
  $('#results-message').textContent = message;
  $('#review-section').style.display = 'none';

  renderBreakdown();
  saveStats(pct);
  showScreen('results');
}

function renderBreakdown() {
  const chapterMap = {};
  state.answers.forEach((ans, i) => {
    const q = state.questions[i];
    if (!chapterMap[q.chapter]) chapterMap[q.chapter] = { correct: 0, total: 0 };
    chapterMap[q.chapter].total++;
    if (ans.isCorrect) chapterMap[q.chapter].correct++;
  });

  const entries = Object.keys(chapterMap)
    .sort((a, b) => parseInt(a) - parseInt(b))
    .map(id => {
      const ch = state.chapters.find(c => c.id === parseInt(id));
      return { id, chapter: ch, ...chapterMap[id] };
    });

  if (entries.length <= 1) {
    $('#chapter-breakdown').style.display = 'none';
    return;
  }

  const list = $('#breakdown-list');
  list.innerHTML = '';

  entries.forEach(e => {
    const pct = Math.round((e.correct / e.total) * 100);
    const level = pct >= 70 ? 'high' : pct >= 40 ? 'mid' : 'low';
    const label = e.chapter ? e.chapter.title : `Cap. ${e.id}`;
    const shortLabel = label.length > 18 ? label.slice(0, 17) + '…' : label;

    const row = document.createElement('div');
    row.className = 'breakdown-row';
    row.innerHTML = `
      <span class="breakdown-label" title="${label}">${shortLabel}</span>
      <div class="breakdown-bar-wrap"><div class="breakdown-bar level-${level}" style="width:${pct}%"></div></div>
      <span class="breakdown-pct">${pct}%</span>
      <span class="breakdown-count">${e.correct}/${e.total}</span>
    `;
    list.appendChild(row);
  });

  $('#chapter-breakdown').style.display = 'block';
}

function toggleReview() {
  const section = $('#review-section');
  if (section.style.display === 'none') {
    section.style.display = 'block';
    renderReview();
    section.scrollIntoView({ behavior: 'smooth' });
  } else {
    section.style.display = 'none';
  }
}

function renderReview() {
  const list = $('#review-list');
  list.innerHTML = '';

  state.answers.forEach((ans, i) => {
    const q = state.questions[i];
    const div = document.createElement('div');
    div.className = `review-item ${ans.isCorrect ? 'review-correct' : 'review-wrong'}`;

    let html = `<div class="review-q">${i + 1}. ${q.question}</div>`;

    if (ans.isCorrect) {
      html += `<div class="review-answer"><span class="label correct-text">✓ Corretta:</span> ${ans.correct}) ${q.options[ans.correct]}</div>`;
    } else {
      html += `<div class="review-answer"><span class="label wrong-text">✗ La tua risposta:</span> ${ans.selected}) ${q.options[ans.selected]}</div>`;
      html += `<div class="review-answer"><span class="label correct-text">✓ Risposta corretta:</span> ${ans.correct}) ${q.options[ans.correct]}</div>`;
    }

    html += `<div class="review-explanation">${q.explanation}</div>`;
    div.innerHTML = html;
    list.appendChild(div);
  });
}

function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(`#${name}-screen`).classList.add('active');
  window.scrollTo({ top: 0 });
}

function saveStats(pct) {
  const stats = JSON.parse(localStorage.getItem('emba-quiz-stats') || '{"scores":[],"total":0}');
  stats.scores.push(pct);
  stats.total++;
  localStorage.setItem('emba-quiz-stats', JSON.stringify(stats));
  loadStats();
}

function resetStats() {
  if (!confirm('Cancellare tutte le statistiche?')) return;
  localStorage.removeItem('emba-quiz-stats');
  $('#stats-card').style.display = 'none';
}

function loadStats() {
  const stats = JSON.parse(localStorage.getItem('emba-quiz-stats') || '{"scores":[],"total":0}');
  if (stats.total > 0) {
    $('#stats-card').style.display = 'block';
    $('#stat-total').textContent = stats.total;
    const avg = Math.round(stats.scores.reduce((a, b) => a + b, 0) / stats.scores.length);
    $('#stat-avg').textContent = `${avg}%`;
    $('#stat-best').textContent = `${Math.max(...stats.scores)}%`;
  }
}

init();
