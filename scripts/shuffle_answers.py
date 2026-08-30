#!/usr/bin/env python3
"""Rimescola le opzioni di ogni domanda perché la lettera corretta sia
distribuita in parti uguali fra A, B, C e D, senza sequenze prevedibili.

Le spiegazioni che citano le opzioni ("la C è", "(D)", "le opzioni C e D")
vengono riscritte con la nuova numerazione. Le domande in cui una lettera è
contenuto e non riferimento (classi energetiche, analisi ABC) restano intatte:
riscriverle falsificherebbe il testo.

    python3 scripts/shuffle_answers.py public/data/marketing.json
"""
import json, re, sys, random
from collections import Counter

SEED = 20260830
LETTERS = 'ABCD'
# lettera isolata: esclude A+ , A++ , sigle e parole
ISOLATA = re.compile(r'(?<![A-Za-zÀ-ù+0-9])([A-D])(?![A-Za-zÀ-ù+0-9])')
# la lettera segue una parola che la rende contenuto, non riferimento a un'opzione
CONTENUTO = re.compile(r'(class[ei]|categor|vitamin|serie|allegato|tabella|figura|gruppo'
                       r'|livello|fascia|tipo|modello|piano|punto|lettera)\s*$', re.I)


def intoccabile(q):
    """Vero se una lettera A-D compare come contenuto invece che come riferimento."""
    for v in q['options'].values():
        if ISOLATA.search(v):
            return True
    e = q['explanation']
    for m in ISOLATA.finditer(e):
        if CONTENUTO.search(e[max(0, m.start() - 30):m.start()].strip()):
            return True
    return False


def quote(n, rng):
    """n domande divise il più equamente possibile fra le quattro lettere."""
    base, resto = divmod(n, 4)
    extra = rng.sample(LETTERS, resto)
    return {L: base + (1 if L in extra else 0) for L in LETTERS}


def sequenza(mobili, fisse, rng):
    """Permutazione casuale delle lettere previste dalle quote.

    Casuale davvero: assegnarle scegliendo ogni volta la più in ritardo darebbe
    quote perfette ma una successione quasi ciclica, cioè indovinabile."""
    target = quote(len(mobili) + len(fisse), rng)
    conteggio = Counter(fisse)
    pool = []
    for L in LETTERS:
        pool += [L] * max(0, target[L] - conteggio[L])
    while len(pool) > len(mobili):                       # le fisse hanno gia' coperto una quota
        pool.remove(Counter(pool).most_common(1)[0][0])
    while len(pool) < len(mobili):
        c = Counter(pool) + conteggio
        pool.append(min(LETTERS, key=lambda L: (c[L], rng.random())))
    rng.shuffle(pool)
    # una domanda con tre opzioni non può ricevere la D: scambia con una compatibile
    for i, q in enumerate(mobili):
        if pool[i] in q['options']:
            continue
        for j in rng.sample(range(len(mobili)), len(mobili)):
            if pool[j] in q['options'] and pool[i] in mobili[j]['options']:
                pool[i], pool[j] = pool[j], pool[i]
                break
    return pool


def rimescola(path):
    rng = random.Random(SEED)
    data = json.load(open(path, encoding='utf-8'))
    qs = data['questions']
    toccate = 0
    for ch in sorted({q['chapter'] for q in qs}):
        mod = [q for q in qs if q['chapter'] == ch]
        mobili = [q for q in mod if not intoccabile(q)]
        fisse = [q['correct'] for q in mod if intoccabile(q)]
        for q, nuova in zip(mobili, sequenza(mobili, fisse, rng)):
            lettere = sorted(q['options'])
            distrattori = [L for L in lettere if L != q['correct']]
            rng.shuffle(distrattori)
            libere = [L for L in lettere if L != nuova]
            mappa = {q['correct']: nuova}
            for vecchia, posto in zip(distrattori, libere):
                mappa[vecchia] = posto
            q['options'] = {mappa[L]: q['options'][L] for L in lettere}
            q['correct'] = nuova
            q['explanation'] = ISOLATA.sub(lambda m: mappa.get(m.group(1), m.group(1)), q['explanation'])
            toccate += 1
    # le opzioni vanno scritte in ordine alfabetico: il quiz le mostra nell'ordine del file
    for q in qs:
        q['options'] = {L: q['options'][L] for L in sorted(q['options'])}
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    print('%s: %d domande rimescolate, %d lasciate intatte' % (path, toccate, len(qs) - toccate))


for p in sys.argv[1:]:
    rimescola(p)
