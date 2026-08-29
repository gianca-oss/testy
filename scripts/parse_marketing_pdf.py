#!/usr/bin/env python3
"""Estrae le domande a scelta multipla dalla dispensa di Marketing (4 corsi)."""
import re, json, io, sys

SRC = sys.argv[1]
OUT = sys.argv[2]

MODULES = [  # prefisso di capitolo nella dispensa -> modulo del quiz
    ('9',  1, 'Frey - Marketing e Sostenibilità'),
    ('18', 2, 'Scarpi - Consumer Behavior'),
    ('30', 3, 'Pedeliento - Branding'),
    ('35', 4, 'Cellino - Marketing Strategico'),
]

FOOTER = re.compile(r'^(Frey|Scarpi|Pedeliento|Cellino) - materiali d[’\']esame$')
PAGENUM = re.compile(r'^\d{1,3}$')
HEAD = re.compile(r'^(\d{1,2}(?:\.\d{1,2})+) (?=[A-ZÀ-Ù])(.*)$')
QHEAD = re.compile(r'^(\d+(?:\.\d+)+) Domanda (\d+)\.\s*(.*)$')
AHEAD = re.compile(r'^(\d+(?:\.\d+)+) Risposta corretta:\s*([A-D])\b\s*(?:-\s*(.*))?$')

def clean_join(lines):
    keep = [l for l in lines if not FOOTER.match(l.strip()) and not PAGENUM.match(l.strip())]
    txt = '\n'.join(keep).replace('\f', '\n')
    txt = re.sub(r'([a-zà-ùè])-\n([a-zà-ù])', r'\1\2', txt)   # sillabazione a fine riga
    txt = txt.replace('•', ' ')
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt

def blocks(lines, start, is_head):
    """Righe dal titolo fino al titolo numerato successivo."""
    out, i = [], start
    while i < len(lines):
        m = HEAD.match(lines[i])
        if m and is_head(lines[i]):
            j = i + 1
            while j < len(lines) and not HEAD.match(lines[j]):
                j += 1
            out.append((lines[i], lines[i+1:j]))
            i = j
        else:
            i += 1
    return out

text = io.open(SRC, encoding='utf-8').read()
lines = text.split('\n')

def chapter_of(head):
    return HEAD.match(head).group(1).split('.')[0]

questions_raw = blocks(lines, 0, lambda l: QHEAD.match(l))
answers_raw   = blocks(lines, 0, lambda l: AHEAD.match(l))

out, qid, problems = [], 0, []
for prefix, chapter, title in MODULES:
    qs = [(h, b) for h, b in questions_raw if chapter_of(h) == prefix]
    ans = [(h, b) for h, b in answers_raw if chapter_of(h) == prefix]
    assert len(qs) == len(ans), '%s: %d domande vs %d risposte' % (title, len(qs), len(ans))
    for (qh, qb), (ah, ab) in zip(qs, ans):
        m = QHEAD.match(qh)
        stem_head = m.group(3)
        body = clean_join([stem_head] + qb)
        parts = re.split(r'\s(?=([A-D])\)\s)', body)
        # re.split con gruppo restituisce [testo, 'A', 'A) ...', 'B', 'B) ...', ...]
        stem = parts[0].strip()
        opts = {}
        for k in range(1, len(parts), 2):
            letter, chunk = parts[k], parts[k+1]
            opts[letter] = re.sub(r'^[A-D]\)\s*', '', chunk).strip()
        part = int(m.group(1).split('.')[1]) - 1   # .2 = Parte I, .3 = Parte II, .4 = Parte III
        correct = AHEAD.match(ah).group(2)
        topic = (AHEAD.match(ah).group(3) or '').strip()
        expl = clean_join(ab)
        qid += 1
        rec = {'id': qid, 'chapter': chapter, 'question': stem,
               'options': opts, 'correct': correct, 'explanation': expl, 'part': part}
        if topic:
            rec['topic'] = topic
        # controlli
        if sorted(opts) != ['A','B','C','D']: problems.append((qid, 'opzioni: %s' % sorted(opts)))
        elif correct not in opts:            problems.append((qid, 'corretta %s assente' % correct))
        if len(stem) < 15:                   problems.append((qid, 'testo corto: %r' % stem))
        if len(expl) < 20:                   problems.append((qid, 'spiegazione corta'))
        for L, v in opts.items():
            if not v: problems.append((qid, 'opzione %s vuota' % L))
        out.append(rec)

chapters = [{'id': c, 'title': t, 'icon': '●'} for _, c, t in MODULES]
io.open(OUT, 'w', encoding='utf-8').write(json.dumps({'chapters': chapters, 'questions': out}, ensure_ascii=False))
print('domande estratte:', len(out))
from collections import Counter
print('per modulo:', dict(Counter(q['chapter'] for q in out)))
print('distribuzione corrette:', dict(Counter(q['correct'] for q in out)))
print('problemi:', len(problems))
for p in problems[:25]: print('  -', p)
