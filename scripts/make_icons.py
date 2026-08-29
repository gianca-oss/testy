#!/usr/bin/env python3
"""Genera le icone PWA con due lettere (es. MK), nello stile delle precedenti:
fondo #17181B, lettere bianche in SF Pro Bold, stessa altezza maiuscola e
stessa spaziatura misurate sulle icone originali.

    python3 scripts/make_icons.py MK
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

LETTERS = (sys.argv[1] if len(sys.argv) > 1 else 'MK').upper()
OUT = os.path.join(os.path.dirname(__file__), '..', 'public')

BG = (23, 24, 27, 255)          # #17181B, come --ink e il theme-color
FG = (255, 255, 255, 255)
FONT = '/System/Library/Fonts/SFNS.ttf'
WEIGHT = 'Bold'
CAP = 169 / 512                 # altezza maiuscola / lato, dalle icone originali
CAP_MASKABLE = 124 / 512        # più piccola: deve stare nell'area sicura
TRACK = 14 / 169                # spaziatura extra fra le lettere, in altezze maiuscole

TARGETS = [('icon-192.png', 192, CAP), ('icon-512.png', 512, CAP),
           ('apple-touch-icon.png', 180, CAP), ('icon-maskable-512.png', 512, CAP_MASKABLE)]


def draw_text(size_px, text, font_size, tracking):
    """Disegna il testo su una tela di servizio e restituisce l'immagine ritagliata."""
    f = ImageFont.truetype(FONT, font_size)
    f.set_variation_by_name(WEIGHT)
    pad = font_size * 2
    im = Image.new('L', (pad * 4, pad * 3), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for ch in text:
        d.text((x, pad), ch, font=f, fill=255)
        x += d.textlength(ch, font=f) + tracking
    return im.crop(im.getbbox())


def cap_height(font_size):
    """Altezza di una lettera piatta: è la maiuscola vera, senza le sporgenze delle tonde."""
    return draw_text(0, 'H', font_size, 0).height


def render(path, side, cap_ratio):
    cap = round(side * cap_ratio)
    fs = cap * 2
    for _ in range(20):                      # cerca il corpo che dà quella maiuscola
        h = cap_height(fs)
        if h == cap:
            break
        fs = max(8, round(fs * cap / max(1, h)))
    glyphs = draw_text(side, LETTERS, fs, round(cap * TRACK))
    icon = Image.new('RGBA', (side, side), BG)
    layer = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    pos = ((side - glyphs.width) // 2, (side - glyphs.height) // 2)
    layer.paste(Image.new('RGBA', glyphs.size, FG), pos, glyphs)
    icon = Image.alpha_composite(icon, layer)
    icon.save(os.path.join(OUT, path))
    print('%-24s %dx%d  maiuscola %d px, testo %dx%d' % (path, side, side, cap, glyphs.width, glyphs.height))


for name, side, ratio in TARGETS:
    render(name, side, ratio)
