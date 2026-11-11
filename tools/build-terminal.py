#!/usr/bin/env python3
"""Builds the terminal version of the site: `curl -sL pedroverissimo.vercel.app`.

Writes terminal.txt (the menu), t/<page>.txt (one per section), go.sh (the interactive version, from
tools/terminal-tui.sh and the art in tools/terminal_art.py) and the curl routes in vercel.json.
Run from the repo root:  python3 tools/build-terminal.py
"""
import json, os, random, re, textwrap
import terminal_art as ART

SITE = 'pedroverissimo.vercel.app'
W = 72
E = '\033['
R = E + '0m'
B = lambda s: E + '1m' + s + R
D = lambda s: E + '2m' + s + R
def C(rgb):
    f = lambda s: E + '38;2;%d;%d;%dm' % rgb + s + R
    f.rgb = rgb
    return f
BLUE, ORANGE, GREEN, YELLOW, PINK, GREY, STRAW = C((79, 127, 255)), C((255, 106, 46)), C((46, 230, 166)), C((255, 212, 59)), C((255, 79, 139)), C((140, 146, 160)), C((242, 193, 78))

def vis(s): return len(re.sub(r'\033\[[0-9;]*m', '', s))
def wrap(text, ind=2, width=W):
    out = []
    for para in text.strip().split('\n'):
        out += textwrap.wrap(para, width - ind, break_on_hyphens=False) or ['']
    return '\n'.join(' ' * ind + l for l in out)
def rule(col=D, ch='─'): return '  ' + col(ch * (W - 2))
def kv(rows, col=D):
    w = max(len(k) for k, _ in rows); out = []
    for k, v in rows:
        lines = textwrap.wrap(v, W - w - 4, break_on_hyphens=False) or ['']
        out.append('  ' + col(k.ljust(w)) + '  ' + lines[0])
        out += [' ' * (w + 4) + l for l in lines[1:]]
    return '\n'.join(out)
def bullets(items, col):
    out = []
    for it in items:
        lines = textwrap.wrap(it, W - 6, break_on_hyphens=False)
        out.append('  ' + col('▸') + ' ' + lines[0])
        out += ['    ' + l for l in lines[1:]]
    return '\n'.join(out)
def section(title, col): return '  ' + col(B(title.upper())) + ' ' + D('─' * (W - 3 - len(title)))

BANNER = """████████    ██████████  ████████    ████████      ██████
██      ██  ██          ██      ██  ██      ██  ██      ██
██      ██  ██          ██      ██  ██      ██  ██      ██
████████    ████████    ██      ██  ████████    ██      ██
██          ██          ██      ██  ██  ██      ██      ██
██          ██          ██      ██  ██    ██    ██      ██
██          ██████████  ████████    ██      ██    ██████""".split('\n')

CODE = """import argparse
+import os
from ultralytics import YOLO

def train(data_yaml, epochs, batch_size, img_size):
    # YOLOv8n (nano) para rapidez em 20 minutos
+    last = 'runs/detect/exp/weights/last.pt'
+    if os.path.exists(last): return YOLO(last).train(resume=True)
    model = YOLO('yolov8n.yaml')
    model.train(data=data_yaml, epochs=epochs, batch=batch_size,
                imgsz=img_size, workers=4, name='exp',
                save_period=1,    # checkpoint cada época
                patience=10)      # early stop"""

# --------------------------------------------------------------------------- pages
P = []  # (slug, title, color, one-liner, body, anchor on the web page)
def page(slug, title, col, line, body, anchor=None): P.append((slug, title, col, line, body, anchor or slug))

page('about', 'About', BLUE, 'Who, where from, how I got here.', lambda: '\n\n'.join([
    wrap("I'm Pedro Veríssimo, a builder from São Gabriel, a town of about 60,000 people in the far south of Brazil. When something grabs my attention, I go all the way, until there's something I can point to."),
    kv([('from', 'São Gabriel, RS, fifth generation of rice and cattle farmers'),
        ('route', 'São Gabriel → Porto Alegre (2024) → São Paulo (2026) → ???'),
        ('now', 'tech co-founder of Sincra · Link School of Business'),
        ('speaks', 'Portuguese, English (C2, self-taught by 16), Spanish')]),
    wrap("In 2024 I moved to Porto Alegre on my own, in the middle of a school year, because that was the only window I had. Most of what's on these pages happened after that move."),
]))

page('sincra', 'Sincra', BLUE, 'What I am building now.', lambda: '\n\n'.join([
    '  ' + B('"Doctors shouldn\'t pay interest on money that\'s already theirs."'),
    wrap("In Brazil a surgeon can wait months to be paid for an operation, and the hospital often can't tell where that money is stuck: internal audit, the insurer, a missing signature. Sincra rebuilds every procedure's path from surgery to payout and predicts how much each doctor will receive, when, and with what confidence."),
    '  ' + BLUE('01 connect') + D('  →  ') + BLUE('02 rebuild') + D('  →  ') + BLUE('03 predict') + D('  →  ') + BLUE('04 show') + D('  →  ') + BLUE('05 advance'),
    kv([('role', 'tech co-founder, one of three: product and engineering'),
        ('history', 'started as shift scheduling; changed thesis at Link\'s Startup School'),
        ('web', 'https://sincra.app')]),
]))

page('rockets', 'Rockets', ORANGE, 'Built from fireworks up. São Gabriel, 2022–2023.', lambda: '\n\n'.join([
    wrap("No lab, no club, no budget: YouTube (BPS.space did most of the teaching) and a lot of launches that didn't go to plan. I started by taking fireworks apart and mounting them in cardboard tubes. The first ones exploded; after enough iterations they flew."),
    bullets(['Home-mixed solid propellant, and a static fire on a kitchen scale to read thrust.',
             'An Arduino flight computer reading an accelerometer and driving servos.',
             'Parachute recovery, and cameras on board to film each flight.',
             'Eleven rockets built. One pad fire. One flew in a corkscrew. I kept every clip.'], ORANGE),
    kv([('film', 'Foguete 7/2023, the documentary: https://youtu.be/FnTpVjeVxYo')]),
]))

page('ai', 'AI Olympiad', GREEN, 'Gold at the 1st National AI Olympiad (ONIA), 2025.', lambda: '\n\n'.join([
    '  ' + GREEN(B('716,000+')) + D(' participants   ') + GREEN(B('28')) + D(' golds   ') + GREEN(B('1')) + D(' of them mine'),
    wrap("The rounds went from theory and ethics, to building models in Python, to a final where I built a computer-vision algorithm for competing robots, trained on Santos Dumont II, Brazil's national supercomputer."),
    '  ' + D('┌─ train.py · + the lines I never wrote ' + '─' * (W - 44) + '┐') + '\n' + '\n'.join('  ' + (YELLOW('│+') + YELLOW(l[1:]) if l[:1] == '+' else D('│ ') + GREEN(l)) for l in CODE.split('\n')) + '\n  ' + D('└' + '─' * (W - 4) + '┘'),
    wrap("The one that got away: the selection for the international team trained on jobs capped at 20 minutes. My script saved a checkpoint every epoch and never loaded one, so every job started from zero. My model stalled near 70% when it could have reached about 95%. One missing line of code between me and Beijing."),
    kv([('code', 'github.com/peddrof/ONIA-Project/blob/main/pedro.fonseca3/train.py'), ('after', 'named ambassador for the 2026 edition')]),
]), anchor='onia')

page('voluntaria', 'Voluntaria+', YELLOW, 'Volunteers meet NGOs. Porto Alegre, 2024–2025.', lambda: '\n\n'.join([
    wrap("At InovaTec, my school's student innovation club, I found lots of ambition and almost no one who could build. As head of technology I rebuilt the platform from scratch, and a team of four launched it in about four months."),
    '  ' + YELLOW(B('170+')) + D(' volunteers   ') + YELLOW(B('20')) + D(' NGOs   ') + YELLOW(B('80+')) + D(' blood donors   ') + YELLOW(B('R$6,300')) + D(' Braille printer'),
    wrap("Covered by RBS TV, SBT, Zero Hora, Brasil de Fato and Correio do Povo. In July 2026 the students I trained used it to help fund an art school in Morro da Cruz."),
    kv([('web', 'https://voluntariamais.com.br')]),
]))

page('audience', 'Audience', PINK, 'Three Instagram pages, 316,000 followers. All sold.', lambda: '\n\n'.join([
    wrap("My feed kept serving the same repeatable formats with millions of views, so I tried to reverse-engineer them. The first two pages went nowhere. Then a crab took off."),
    kv([('@seusiriqueijo', '183K  the most famous crab in Brazil'),
        ('@gatinhoajude', ' 83K  a cat drinking water; one reel: 340,088 accounts'),
        ('@inteligenciai', ' 50K  about AI')], PINK),
    wrap("7.2 million accounts reached in one 30-day window. My benchmark: the two biggest accounts that started copying me. I couldn't monetize, so I sold all three, for R$1,200, R$800 and R$160. Lesson: sell before you build."),
]))

page('data', 'Data & stage', BLUE, 'A forecast that won, and a talk in Brasília. 2025.', lambda: '\n\n'.join([
    section('Geração Caldeira', BLUE),
    wrap("200 selected from about 18,000. Our final project, a predictive sales panel for RBS Group's fourth quarter, won. I turned down an internship offer to keep building."),
    section('II BRICS Forum', BLUE),
    wrap('Twenty minutes in Brasília, for diplomats and young leaders: "The Youth Perspective: innovation starts small."'),
]))

page('flying', 'Flying', BLUE, 'From a cardboard cockpit to the real one.', lambda: '\n\n'.join([
    wrap("As a kid I built near full-scale cockpits out of cardboard, every instrument drawn by hand. In May 2024, during the floods, with the roads closed and a family emergency in Porto Alegre, I flew in as co-pilot on a small plane found through a friend of a friend."),
    kv([('since', 'ANAC private pilot ground school done · 10 hours flown')]),
]))

page('side', 'Side quests', PINK, 'Smaller things, each one finished.', lambda: '\n\n'.join([
    bullets(['Markets, age 12 (2020): the pandemic, a stock chart, and advice nobody asked for. In 2026, presenting at B3 with my Link class.',
             'Popsicles, age 14 (2022): sold at school until the principal banned it for "causing disorder". Moved to the sidewalk at pickup time. R$2,000 in a few months.',
             'Step Up (2025): an NGO teaching English to low-income students. 32 lessons as a mentor, then operations and the tracking system. stepuplearning.com.br',
             'Advogado Rural: a publishing platform for a rural lawyer, so he reaches farmers directly. advogadorural.com',
             'Farroupilha AI: an essay-grading assistant for my school, OCR plus a language model.'], PINK),
]))

page('farm', 'Farm', STRAW, 'Five generations of rice and cattle.', lambda: '\n\n'.join([
    wrap("My family has worked the land in Rio Grande do Sul for five generations. When I'm home I'm in the corral for the vaccinations and on the combine for the harvest."),
]))

page('honors', 'Honors', YELLOW, 'Nine, in one list.', lambda: bullets([
    'Gold medal, 1st National AI Olympiad (ONIA), 2025: one of 28 among 716,000+.',
    'ONIA ambassador, 2026 edition.',
    'Gold medal, Brazilian Astronomy Olympiad (OBA), 2025: top 150 in Brazil.',
    'Invited speaker, II BRICS Forum, Brasília, Sep 2025.',
    'Geração Caldeira fellow, 2025: 200 of about 18,000, final project won.',
    'Preface of Colégio Farroupilha\'s 9th-grade book, 2025.',
    'Solver #76, Paralelo 1155, Dec 2023.',
    '"Alamar" distinction, military school: top 1% for grades and conduct.',
    'Top five, clipping competition.'], YELLOW))

def timeline():
    rows = [('2026', 'move', 'São Paulo, Link School of Business. Co-founds Sincra.'),
            ('2026', 'win', 'Voluntaria+, run by the students I trained, helps fund an art school.'),
            ('2025', 'win', 'Gold at ONIA and OBA. BRICS Forum. Caldeira project wins.'),
            ('2025', 'build', 'Step Up, Farroupilha AI, Advogado Rural.'),
            ('2024', 'build', 'Voluntaria+.'),
            ('2024', 'move', 'Porto Alegre, alone, mid-year. Co-pilot during the floods.'),
            ('2023', 'win', 'Paralelo 1155, solver #76. The "Alamar".'),
            ('2023', 'build', 'The crab, the cat and the AI page.'),
            ('2022', 'build', 'Rockets.'),
            ('2022', 'learn', 'Popsicles, at 14.'),
            ('2020', 'learn', 'The stock market at 12.'),
            ('2017', 'build', 'A murder-mystery trilogy, one film per summer.')]
    col = {'build': BLUE, 'win': YELLOW, 'move': ORANGE, 'learn': GREEN}
    tag = {'build': '+ build', 'win': '★ win  ', 'move': '→ move ', 'learn': '∴ learn'}
    out, last = [], None
    for y, l, t in rows:
        ls = textwrap.wrap(t, W - 19)
        out.append('  ' + (B(y) if y != last else '    ') + '  ' + D('│') + ' ' + col[l](tag[l]) + '  ' + ls[0])
        out += ['        ' + D('│') + ' ' * 10 + x for x in ls[1:]]
        last = y
    return '\n'.join(out)
page('timeline', 'Changelog', GREY, 'Everything, on one track. Newest first.', timeline)

page('press', 'Press', GREY, 'In the news.', lambda: '\n'.join('  ' + D(d) + '  ' + B(o) + '\n  ' + ' ' * 8 + h for d, o, h in [
    ('Jul 2026', 'RBS TV', 'The Morro da Cruz art school, part-funded through Voluntaria+'),
    ('Jul 2026', 'Zero Hora', 'Porto Alegre gets a graffiti and visual arts school'),
    ('Jul 2026', 'Brasil de Fato', 'Students make a cultural space\'s renovation possible'),
    ('Oct 2025', 'SBT RS', 'InovaTec and Voluntaria+ on SBT'),
    ('Aug 2025', 'RBS TV', 'National Volunteering Day, featuring Voluntaria+'),
    ('Aug 2025', 'Colégio Farroupilha', 'Student-built platform connects volunteers with NGOs'),
    ('Jul 2024', 'Correio do Povo', 'Solidarity actions mobilize students')]))

page('films', 'Filmes Pedro', ORANGE, 'Before all of this: films. Now on YouTube.', lambda: kv([
    ('Batatinha 1', 'https://youtu.be/_12PqCGbdgI'), ('Batatinha 2', 'https://youtu.be/MT8nUVmGwXw'),
    ('Batatinha 3', 'https://youtu.be/tap-1_KABF4'), ('Guerra Fria', 'https://youtu.be/R73Zr48ojcc'),
    ('Foguete 7/2023', 'https://youtu.be/FnTpVjeVxYo'), ('Pedras do Infinito', 'https://youtu.be/CC7_vhzHMnY')], ORANGE), anchor='beyond')

page('ask', 'Ask an AI', GREEN, 'Ask your own AI anything about me.', lambda: '\n\n'.join([
    wrap("I wrote a long plain-text file about myself for AI assistants. Hand it to yours and ask away:"),
    '  ' + GREEN('$') + ' curl -sL ' + SITE + '/llms.txt',
    wrap('Or paste this into ChatGPT, Claude, Grok, Perplexity or Meta AI:'),
    '  ' + D('"Read https://' + SITE + '/llms.txt') + '\n  ' + D(' and tell me who Pedro is."'),
]), anchor='talk')

page('contact', 'Contact', BLUE, 'Say hello. I answer.', lambda: kv([
    ('email', 'pedrovverissimo1@gmail.com'), ('linkedin', 'https://www.linkedin.com/in/pvverissimo'),
    ('github', 'https://github.com/peddrof'), ('web', 'https://' + SITE)]))

# buttons on each page of the interactive version, after prev / menu / next
ACTIONS = {
    'sincra': [('↗ sincra.app', 'url:https://sincra.app')],
    'rockets': [('▶ launch again', 'replay'), ('↗ the film', 'url:https://youtu.be/FnTpVjeVxYo')],
    'ai': [('↗ the code', 'url:https://github.com/peddrof/ONIA-Project')],
    'voluntaria': [('↗ voluntariamais', 'url:https://voluntariamais.com.br')],
    'films': [('▶ Batatinha 1', 'url:https://youtu.be/_12PqCGbdgI')],
    'ask': [('↗ llms.txt', 'url:https://' + SITE + '/llms.txt')],
    'contact': [('@ email', 'url:mailto:pedrovverissimo1@gmail.com'), ('↗ linkedin', 'url:https://www.linkedin.com/in/pvverissimo'),
                ('↗ github', 'url:https://github.com/peddrof')],
}

# --------------------------------------------------------------------------- art
ARTS = {slug: fn() for slug, fn in ART.ART.items()}
LAUNCH = ART.launch()
def poster(slug): return LAUNCH[40] if slug == 'rockets' else ARTS[slug][ART.POSTER[slug]]

# --------------------------------------------------------------------------- render
PV = 'pv(){ curl -sL ' + SITE + '/$1; }'
GO = 'curl -sL ' + SITE + '/go | bash'
def head(slug, i, col):
    h = '  ' + col('▌') + B('pedro veríssimo') + D('  ~/' + slug)
    return h + ' ' * max(1, W - vis(h) - 5) + D('%02d/%02d' % (i + 1, len(P)))

def boxed(lines, col):
    out = ['  ' + col('┌' + '─' * (W - 4) + '┐')]
    out += ['  ' + col('│') + ' ' + l + ' ' * (W - 6 - vis(l)) + ' ' + col('│') for l in lines]
    return out + ['  ' + col('└' + '─' * (W - 4) + '┘')]

def frame(slug, i, title, col, line, body):
    n = len(P)
    prev_, next_ = P[i - 1][0], P[(i + 1) % n][0]
    nav = '  ' + D('←') + ' pv ' + prev_ + D('   →') + ' pv ' + B(next_) + D('   ⌂') + ' pv' + D('   ?') + ' pv help'
    return '\n'.join(['', head(slug, i, col), rule(), '', '  ' + col(B(title.upper())), '  ' + D(line), '',
                      *['  ' + r for r in poster(slug)], '', body(), '', rule(), nav,
                      '  ' + D('no pv yet? paste this once:'), '  ' + PV,
                      '  ' + D('▶ watch it move:') + ' ' + GREEN(GO), ''])

def menu():
    out = ['']
    out += ['  ' + BLUE(l) for l in BANNER]
    out += ['', '  ' + B('Pedro Veríssimo') + '  ' + D('·') + '  builder from São Gabriel, Brazil',
            '  ' + BLUE('tech co-founder of Sincra') + '  ' + D('·') + '  São Paulo, UTC−3', '']
    out += boxed([GREEN(B('▶ NEW')) + '  ' + B('the interactive version') + D('  ·  the launch, art, buttons, mouse'),
                  '  ' + GREEN(GO)], GREEN) + ['']
    out.append(section('menu', BLUE))
    for i, (slug, title, col, line, _, _a) in enumerate(P):
        out.append('  ' + D('%02d' % (i + 1)) + '  ' + col(slug.ljust(11)) + D(line[:W - 19]))
    out += ['', section('how to move around', GREEN),
            '  1. define a tiny helper, once:', '     ' + GREEN(PV),
            '  2. then jump anywhere:        ' + GREEN('pv rockets') + D('   ·   ') + GREEN('pv ai') + D('   ·   ') + GREEN('pv'),
            '  ' + D('   (or the long way: curl -sL ' + SITE + '/rockets)'), '',
            '  ' + D('Every page ends with prev / next. Start with ') + B('pv about') + D('.'),
            '  ' + D('The full version has a launch, a farm and a wall of flaps. Type 1155.'), '']
    return '\n'.join(out)

os.makedirs('t', exist_ok=True)
for f in os.listdir('t'):
    if f.endswith('.txt'): os.remove(os.path.join('t', f))
for i, (slug, title, col, line, body, _a) in enumerate(P):
    open('t/%s.txt' % slug, 'w').write(frame(slug, i, title, col, line, body))
m = menu()
open('terminal.txt', 'w').write(m)
open('t/help.txt', 'w').write(m)

# --------------------------------------------------------------------------- the interactive version (go.sh)
MW, SCR = 76, '!<>-_\\/[]{}=+*^?#%'
WHITE_, MAGENTA = C(ART.WHITE), C((255, 61, 242))
def rgbs(rgb): return '%d;%d;%d' % rgb
U, UIX, FI, AS, AN, AH, AW, ALP = [], {}, [], [], [], [], [], []
def anim(frames, loop=True):
    AS.append(len(FI)); AN.append(len(frames)); AH.append(len(frames[0])); ALP.append(1 if loop else 0)
    AW.append(max(vis(r) for f in frames for r in f))
    for f in frames:
        for row in f:
            if row not in UIX: UIX[row] = len(U); U.append(row)
            FI.append(UIX[row])
    return len(AS) - 1

def resolve(text, paint, n, seed):
    """text resolving out of noise over n frames, one row each; paint(s, done) colours it"""
    rng = random.Random(seed); th = [rng.random() * .9 for _ in text]
    return [[paint(''.join(ch if ch == ' ' or th[i] < k / (n - 1) else rng.choice(SCR) for i, ch in enumerate(text)), k == n - 1)]
            for k in range(n)]

def banner_anim():
    tag = ['  ' + B('Pedro Veríssimo') + '  ' + D('·') + '  builder from São Gabriel, Brazil',
           '  ' + BLUE('tech co-founder of Sincra') + '  ' + D('·') + '  São Paulo, UTC−3']
    rng = random.Random(1155); w = max(len(l) for l in BANNER)
    th = [[rng.random() * .7 + x / w * .3 for x in range(w)] for _ in BANNER]
    frames = []
    for k in range(14):
        q = k / 13; cv = ART.Canvas(w + 2, len(BANNER))
        for y, line in enumerate(BANNER):
            for x, ch in enumerate(line):
                if ch == ' ': continue
                d = q - th[y][x]
                g = '█' if d > .12 or k == 13 else '▓' if d > .06 else '▒' if d > 0 else '░' if d > -.08 else ' '
                cv.put(x + 1, y, g, ART.mix(ART.BLUE, (163, 140, 255), x / w))
        frames.append(cv.rows() + [''] + tag)
    return frames

def overlay(lines, col, bg, w, typed=0):
    """a box on its own background; with typed > 0 the text types in at that many characters per frame"""
    total = sum(len(t) for t, _ in lines); frames = []
    for k in range(total // typed + 12 if typed else 1):
        cv = ART.Canvas(w, len(lines) + 2, bg)
        cv.text(0, 0, '┌' + '─' * (w - 2) + '┐', col); cv.text(0, len(lines) + 1, '└' + '─' * (w - 2) + '┘', col)
        left = k * typed if typed else total
        for j, (t, c) in enumerate(lines):
            cv.put(0, j + 1, '│', col); cv.put(w - 1, j + 1, '│', col)
            cv.text(2, j + 1, t[:max(0, left)], c)
            if 0 <= left < len(t): cv.put(2 + left, j + 1, '▌', col)
            left -= len(t)
        frames.append(cv.rows())
    return frames

def tui():
    n = len(P); out = {}
    launch = anim(LAUNCH)
    PL, PS, PN, PH, PC, PA, PSL, PVA, ML, MSL, MD, MDS, MDN = ([] for _ in range(13))
    BL, BW, BA, BS, BN = [], [], [], [], []
    for i, (slug, title, col, line, body, anchor) in enumerate(P):
        rgb = col.rgb; prev_, next_ = P[i - 1][0], P[(i + 1) % n][0]
        pv = anim(ARTS[slug]); hero = launch if slug == 'rockets' else pv
        t = anim(resolve(title.upper(), lambda s, done: col(B(s)) if done else col(s), 8, slug), loop=False)
        lines = ['@a%d t' % t, '  ' + D(line), ''] + ['@a%d %d' % (hero, r) for r in range(AH[hero])] + [''] + body().split('\n') + ['']
        PS.append(len(PL)); PN.append(len(lines)); PL += lines
        PH.append(head(slug, i, col)); PC.append(rgbs(rgb)); PA.append(anchor); PSL.append(slug); PVA.append(pv)
        btns = [('‹ ' + prev_, 'prev'), ('≡ menu', 'menu'), (next_ + ' ›', 'next'), ('', '|')] + ACTIONS.get(slug, []) + [('↗ web', 'web')]
        assert sum(len(l) + 3 if a != '|' else 2 for l, a in btns) <= W, slug
        BS.append(len(BL)); BN.append(len(btns))
        for l, a in btns: BL.append(l); BW.append(len(l)); BA.append(a)
        item = '%02d  %s' % (i + 1, slug.ljust(11))
        ML.append(' ' + D('%02d' % (i + 1)) + '  ' + col(slug.ljust(11)) + ' ' * 12)
        bg = ART.mix((10, 11, 15), rgb, .2)
        MSL.append(E + '48;2;%sm' % rgbs(bg) + E + '38;2;%sm▌' % rgbs(rgb) + E + '1;38;2;233;236;242m' + item + ' ' +
                   E + '22;38;2;%sm›' % rgbs(rgb) + ' ' * 8 + R + '  ')
        md = [col(B(title.upper())), ''] + [WHITE_(l) for l in textwrap.wrap(line, 46)] + ['', D('↵ open   ·   %02d/%02d' % (i + 1, n))]
        MDS.append(len(MD)); MDN.append(len(md)); MD += md
    name = 'pedro veríssimo · builder from São Gabriel, Brazil'
    cap = [[D(name[:max(0, (k - 24) * 2)])] for k in range(24 + len(name) // 2 + 2)]
    egg = overlay([('> paralelo 1155 · solver nº 00076', MAGENTA.rgb), ('', ART.WHITE),
                   ('You typed the number. About 90 people have', ART.WHITE), ('solved the riddle since 2019. I was the 76th.', ART.WHITE),
                   ('', ART.WHITE), ('any key to close', ART.DIM)], MAGENTA.rgb, (14, 6, 16), 52, typed=3)
    keys = [('keys', ART.WHITE), ('', ART.WHITE), ('↑ ↓   j k    move, scroll', ART.GREY), ('← →   h l    previous, next page', ART.GREY),
            ('↵            open, press a button', ART.GREY), ('tab          next button', ART.GREY), ('esc   m      back to the menu', ART.GREY),
            ('o            open it on the web', ART.GREY), ('r            replay the animation', ART.GREY), ('q            quit', ART.GREY),
            ('', ART.WHITE), ('the mouse works: click, scroll', ART.BLUE), ('and there is a number to type', ART.DIM)]
    hlp = overlay(keys, ART.BLUE, (12, 14, 22), 40)
    menu_btns = [('↵ open', 'open'), ('▶ launch', 'launch'), ('↗ website', 'web'), ('? keys', 'help'), ('q quit', 'quit')]
    mhead = ' ' + BLUE('▌') + B('pedro veríssimo') + D('  ~')
    out.update(SITE=SITE, CW=W, MW=MW, MINC=MW + 2, MINR=22, NP=n, LAUNCH=launch, INTRO_END=round(ART.T_FILL1 * ART.FPS) + 2,
               CAPTION=anim(cap, loop=False), BANNER=anim(banner_anim(), loop=False), EGG=anim(egg, loop=False), HELP=anim(hlp),
               SKIP=D('any key to skip · q to quit'),
               BYE='\n  ' + B('thanks for stopping by.') + '  ' + D('pedrovverissimo1@gmail.com · ' + SITE) + '\n',
               MHEAD=mhead + ' ' * (MW - vis(mhead) - 33) + D('builder · São Gabriel → São Paulo'),
               MRULE=' ' + D('─' * (MW - 1)), RULE=rule(), RULE_S='  ' + D('─' * (W - 11)),
               MHINT=' ' + D('↑↓ choose   ↵ open   r relaunch   o website   ? keys   q quit'),
               PHINT='  ' + D('←→ pages   ↑↓ scroll   tab ↵ buttons   esc menu   ? keys   q quit'),
               U=U, FI=FI, AS=AS, AN=AN, AH=AH, AW=AW, ALP=ALP, PL=PL, PS=PS, PN=PN, PH=PH, PC=PC, PA=PA, PSL=PSL, PVA=PVA,
               ML=ML, MSL=MSL, MD=MD, MDS=MDS, MDN=MDN, BL=BL, BW=BW, BA=BA, BS=BS, BN=BN,
               MBL=[l for l, _ in menu_btns], MBW=[len(l) for l, _ in menu_btns], MBA=[a for _, a in menu_btns])
    return out

def sh(v):
    if isinstance(v, int): return str(v)
    return "$'" + v.replace('\\', '\\\\').replace("'", "\\'").replace('\033', '\\e').replace('\n', '\\n') + "'"
def emit(data):
    out = []
    for k, v in data.items():
        if isinstance(v, list): out.append('  %s=(\n%s\n  )' % (k, '\n'.join(sh(x) for x in v)))
        else: out.append('  %s=%s' % (k, sh(v)))
    return '\n'.join(out)

go = open('tools/terminal-tui.sh').read().replace('@@DATA@@', emit(tui()))
open('go.sh', 'w').write(go)
os.chmod('go.sh', 0o755)

# --------------------------------------------------------------------------- vercel routes
UAS = ['curl/', 'Wget/', 'HTTPie/', 'xh/']
slugs = [p[0] for p in P] + ['help']
TXT = {'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'public, max-age=0, must-revalidate'}
routes = [{'src': '/go(\\.sh)?/?', 'dest': '/go.sh', 'headers': TXT}]
for ua in UAS:
    has = [{'type': 'header', 'key': 'user-agent', 'value': {'pre': ua}}]
    routes.append({'src': '/', 'has': has, 'dest': '/terminal.txt', 'headers': TXT})
    routes.append({'src': '/(%s)/?' % '|'.join(slugs), 'has': has, 'dest': '/t/$1.txt', 'headers': TXT})
    routes.append({'src': '/onia/?', 'has': has, 'dest': '/t/ai.txt', 'headers': TXT})
# browsers that follow a terminal link land on the right part of the page
for slug, *_r, anchor in P:
    routes.append({'src': '/%s/?' % slug, 'status': 308, 'headers': {'Location': '/#%s' % anchor}})
routes.append({'src': '/help/?', 'status': 308, 'headers': {'Location': '/'}})
routes.append({'src': '/', 'headers': {'Vary': 'User-Agent'}, 'continue': True})
json.dump({'$schema': 'https://openapi.vercel.sh/vercel.json', 'routes': routes}, open('vercel.json', 'w'), indent=2)
print('pages:', len(P), '· routes:', len(routes))
