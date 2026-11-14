"""ASCII art and animations for the terminal version.

Every animation is a list of frames; a frame is a list of ANSI strings, one per row, all frames the same height.
Animations play at FPS. `launch()` is a port of the ASCII launch on the page (index.html, section 14).
"""
import math, random

FPS = 10
E = '\033['

BLUE, ORANGE, GREEN, YELLOW, PINK = (79, 127, 255), (255, 106, 46), (46, 230, 166), (255, 212, 59), (255, 79, 139)
GREY, STRAW, WHITE, DIM, FAINT = (140, 146, 160), (242, 193, 78), (233, 236, 242), (96, 100, 112), (58, 61, 70)
RED = (255, 72, 72)
HULL_C, SHADE_C, WIN_C = (242, 238, 230), (154, 146, 136), (127, 166, 255)


def mix(a, b, t): return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))


class Canvas:
    """A grid of (glyph, colour) cells; spaces are transparent unless the canvas has a background."""

    def __init__(s, w, h, bg=None):
        s.w, s.h, s.bg = w, h, bg
        s.g = [[(' ', None)] * w for _ in range(h)]

    def put(s, x, y, ch, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.g[y][x] = (ch, c)

    def text(s, x, y, txt, c):
        for i, ch in enumerate(txt): s.put(x + i, y, ch, c)

    def art(s, x, y, block, c):
        for j, line in enumerate(block.split('\n')):
            for i, ch in enumerate(line):
                if ch != ' ': s.put(x + i, y + j, ch, c)

    def rows(s):
        out = []
        for row in s.g:
            if s.bg is None:
                while row and row[-1][0] == ' ': row = row[:-1]
            buf, cur = [E + '48;2;%d;%d;%dm' % s.bg] if s.bg else [], None
            for ch, c in row:
                if ch != ' ' and c != cur:
                    buf.append(E + '38;2;%d;%d;%dm' % c); cur = c
                buf.append(ch)
            out.append(''.join(buf) + (E + '0m' if buf else ''))
        return out


def bar(n, w):
    """A horizontal bar of n (float) cells out of w, with eighth blocks at the tip."""
    full = int(n); part = int((n - full) * 8)
    return '█' * full + ('▏▎▍▌▋▊▉'[part - 1] if part and full < w else '')


def typed(s, n): return s[:max(0, n)]


# ----------------------------------------------------------------------------------------- the launch
# Port of the page's launch (index.html, section 14): fire, dust and smoke particles splatted into heat and
# density grids; density picks the glyph and one of six orange shades. Rates and vertical speeds scale with the grid.
LAUNCH_BG = (7, 8, 11)
# seconds; T_FILL1 is when the smoke fills the frame (the TUI intro ends there)
LOOP_S, T_IGN, T_LIFT, T_FILL0, T_FILL1, T_FADE0, T_FADE1 = 13, 1.0, 2.4, 5.0, 7.0, 12.0, 13.0
LAUNCH_COL = [(138, 58, 10), (184, 73, 12), (226, 97, 15), (255, 125, 26), (255, 160, 53), (255, 201, 77)]
_RK_BIG = ['    ^    ', '   /$\\   ', '  /$$$\\  ', '  |$$$|  ', '  |$o$|  ', '  |$$$|  ', '  |$$$|  ', '  |===|  ',
           '  |$$$|  ', ' /|$$$|\\ ', '/_|___|_\\', '   \\_/   ']
_RK_SMALL = ['  ^  ', ' /$\\ ', ' |o| ', ' |=| ', '/|_|\\', ' \\_/ ']
_SR, _FR = ' .:-=+*#%@', " .'^*#@"


def launch(C=68, R=18, A=2.0, seed=7919):
    """One loop of the launch (pad, ignition, liftoff, smoke that fills the frame, fade) at FPS. Returns frames."""
    rng = random.Random(seed); rr = rng.random
    def rnd(a, b): return a + rr() * (b - a)
    def cl(v, a, b): return a if v < a else b if v > b else v
    def sgn(): return -1 if rr() < .5 else 1
    def n_of(rate): k = int(rate); return k + (rr() < rate - k)
    big = R >= 30
    RK = _RK_BIG if big else _RK_SMALL
    RH, RW, BO = len(RK), len(RK[0]), (2 if big else 1)
    G = R - max(2, round(R * .13)); CX = C // 2; K = C / 96; KY = R / 44; AR = K * KY; SX = RW / 9
    TH = 14 if big else max(4, round(G * .4)); TX = CX - RW // 2 - 5
    ARM = (CX - RW // 2 + BO - 1) - (TX + 3) + 1; ARMY = (G - round(TH * .64), G - round(TH * .36))
    stars = [(rng.randrange(C), rng.randrange(max(1, G - TH - 3)), rr() * 6.28, rnd(.8, 2.3)) for _ in range(round(.011 * C * G))]
    gap = max(10, round(16 * K))
    ridge = []
    for x in range(C):
        h = round(1.2 + 1.4 * math.sin(x * .19) + .9 * math.sin(x * .071 + 1.3))
        ridge.append(0 if abs(x - CX) < gap else int(cl(h, 0, 3)) if big else int(h >= 3))
    tex = [[rng.choice(".,-`'") if rr() < .24 - (y - G) * .02 else ' ' for x in range(C)] for y in range(G + 1, R)]
    KER = []
    for r in range(4 if big else 3):
        k, rx = [], math.ceil(r * A)
        for dy in range(-r, r + 1):
            for dx in range(-rx, rx + 1):
                w = (1 - math.hypot(dx / A, dy) / (r + 1)) / (1 + .6 * r)
                if w > 0: k.append((dx, dy, w))
        KER.append(k)
    NK = len(KER) - 1
    P = []  # [x, y, vx, vy, life, max, type (0 smoke, 1 fire, 2 fire along the ground), strength]

    def thr(T): return 0 if T < T_IGN else cl((T - T_IGN) / .9, 0, 1)
    def ry(T): return G - 1 if T < T_LIFT else (G - 1) - (G + RH - 2) * min((T - T_LIFT) / 4, 1.3) ** 2.3
    def smoke(x, y, vx, vy, l, s): return [x, y, vx, vy, l, l, 0, s]

    def step(T, dt):
        th, yb = thr(T), ry(T)
        if T < T_IGN:
            for _ in range(n_of(10 * dt)):
                s = sgn(); P.append(smoke(CX + s * rnd(2, 4) * SX, G - RH // 2 + rnd(-1, 1), s * rnd(1, 4), rnd(-1.2, .4) * KY, 1.8, .6))
        if th > 0 and yb > -3:
            for _ in range(n_of(260 * th * KY * dt)):
                l = rnd(.15, .4); P.append([CX + rnd(-1.6, 1.6) * SX, yb + 1, rnd(-3, 3), rnd(22, 42) * KY, l, l, 1, 1])
            if yb > G - (RH + 6):
                for _ in range(n_of(200 * th * AR * dt)):
                    P.append(smoke(CX + rnd(-4, 4) * SX, G - 1 - rnd(0, 2 * KY), sgn() * rnd(4, .5 * C), -rnd(.5, 7) * KY, rnd(4, 7), 1.2))
            if T > T_LIFT:
                for _ in range(n_of(70 * KY * dt)):
                    P.append(smoke(CX + rnd(-1.5, 1.5) * SX, yb + 1 + rnd(0, 3 * KY), rnd(-6, 6), rnd(-.5, 3) * KY, rnd(4.5, 6.2), 1))
            if yb < RH + 6:
                k = cl(1 - yb / (RH + 6), 0, 1)
                for _ in range(n_of(150 * k * KY * dt)):
                    P.append(smoke(CX + rnd(-6, 6) * SX, yb - rnd(0, RH - 1), rnd(-5, 5), rnd(-1.5, 1.2) * KY, rnd(3, 5), 1.1))
        if T_LIFT + .2 < T < T_FILL1:
            for _ in range(n_of(130 * K * max(KY, .75) * dt)):
                P.append(smoke(CX + rnd(-3, 3) * SX, rnd(max(0, yb - 4 * KY), G - 2), sgn() * rnd(2, .35 * C), rnd(-2, 1) * KY, rnd(4.5, 5.5), .9))
        fx, fy, ff = .45 ** dt, .55 ** dt, .25 ** dt
        keep = []
        for p in P:
            p[0] += p[2] * dt; p[1] += p[3] * dt; p[4] -= dt
            if p[6] == 1:
                if p[1] >= G - 1:
                    p[1] = G - 1; p[6] = 2; p[3] = -rnd(0, 3) * KY; p[2] = sgn() * rnd(12, .35 * C); p[4] = p[5] = rnd(.3, .8)
            elif p[6] == 2: p[2] *= ff
            else:
                p[2] *= fx; p[3] *= fy; p[3] -= .7 * KY * dt
                if p[1] > G - 1: p[1] = G - 1; p[3] = -abs(p[3]) * .2
            if p[4] > 0 and -8 < p[0] < C + 8 and -8 < p[1] < R: keep.append(p)
        P[:] = keep[-4500:]

    def render(T):
        ch = [[' '] * C for _ in range(R)]; lv = [[-1] * C for _ in range(R)]
        def put(x, y, c, l):
            if 0 <= x < C and 0 <= y < R: ch[y][x] = c; lv[y][x] = l
        for sx, sy, ph, sp in stars:
            v = math.sin(T * sp + ph)
            if v > -.2: put(sx, sy, '+' if v > .7 else '.', 1 if v > .7 else 0)
        for x in range(C):
            h = ridge[x]
            if h:
                n = ridge[x + 1] if x + 1 < C else 0; p = ridge[x - 1] if x else 0
                c = '^' if p < h and n < h else '/' if n > h else '\\' if p > h else '\\' if n < h else '/' if p < h else '-'
                put(x, G - h, c, 0)
        th, yb0 = thr(T), ry(T)
        glow = th * cl(1 - (G - 1 - yb0) / (RH + 8), 0, 1) if th > 0 else 0
        for x in range(C):
            d, l = abs(x - CX), 1
            if glow > 0 and d < (8 + 22 * K) * glow and rr() < .85: l = 5 if d < 6 * glow + 2 else 4 if d < 14 * glow else 3
            put(x, G, '_', l)
        for j, row in enumerate(tex):
            for x, c in enumerate(row):
                if c != ' ': put(x, G + 1 + j, c, 0)
        put(TX + 1, G - TH - 3, '*', 5 if math.sin(T * 6) > 0 else 2); put(TX + 1, G - TH - 2, '|', 2)
        put(TX, G - TH - 1, '/', 2); put(TX + 1, G - TH - 1, '^', 2); put(TX + 2, G - TH - 1, '\\', 2)
        for y in range(G - TH, G):
            put(TX, y, '|', 2); put(TX + 1, y, 'X' if y % 2 else '+', 1); put(TX + 2, y, '|', 2)
        for i in range(round(ARM * cl(1 - (T - .4) / .5, 0, 1))):
            for ay in ARMY: put(TX + 3 + i, ay, '=', 2)
        pw = RW // 2 + 3
        put(CX - pw, G, '[', 3); put(CX + pw, G, ']', 3)
        for x in range(CX - pw + 1, CX + pw): put(x, G, '=', 4 if glow > .5 else 3)
        D = [[0.0] * C for _ in range(R)]; H = [[0.0] * C for _ in range(R)]
        for p in P:
            f = cl(p[4] / p[5], 0, 1); xi, yi = round(p[0]), round(p[1])
            if p[6]:
                if 0 <= xi < C and 0 <= yi < R: H[yi][xi] += f * 1.4 + .2
                continue
            a = p[7] * f ** .8
            for dx, dy, w in KER[min(NK, int((1 - f) * (NK + 1.5)))]:
                x, y = xi + dx, yi + dy
                if 0 <= x < C and 0 <= y < R: D[y][x] += a * w
        for y in range(G):
            for x in range(C):
                d, h = D[y][x], H[y][x]
                if d > .07: ch[y][x] = _SR[min(9, 1 + int(d * 2.6))]; lv[y][x] = 0 if d < .2 else 1 if d < .6 else 2 if d < 1.4 else 3
                if h > .15: ch[y][x] = _FR[min(6, 1 + int(h * 2.2))]; lv[y][x] = 3 if h < .7 else 4 if h < 1.6 else 5
        yb = round(yb0)
        sh = (sgn() if rr() < .45 else 0) if T_IGN < T < 3.4 else 0
        v = cl((yb - 1) / (RH + 3), 0, 1) if yb < RH + 4 else 1
        x0 = CX - RW // 2 + sh
        if v > 0:
            for r, row in enumerate(RK):
                y = yb - RH + 1 + r
                if not 0 <= y < G: continue
                for c, k in enumerate(row):
                    if k == ' ' or (v < 1 and rr() > v): continue
                    if k == '$': put(x0 + c, y, ' ', -1)
                    else: put(x0 + c, y, k, 5 if k in 'o^' else 3 if k == '=' else 4)
            if th > 0:
                FL = RH * .75
                for i in range(round(FL * .33 + th * FL + rnd(0, FL * .25))):
                    y = yb + 1 + i
                    if y >= G or y < 0: continue
                    w = max(0, round((2.6 if big else 1.6) - i * (.28 if big else .3) + rnd(-.5, .5)))
                    for d in range(-w, w + 1):
                        if v < 1 and rr() > v: continue
                        ad = abs(d)
                        c = ('@' if i < 3 or i % 3 == 2 else '#') if ad == 0 else "'" if ad == w else '%' if ad == 1 else '*'
                        put(CX + d + sh, y, c, 5 if (ad == 0 and i % 3 == 2) or i < 3 else 4 if i < 7 else 3)
        op = cl(T_FADE1 - T, 0, 1) if T > T_FADE0 else cl(T / .5, 0, 1) if T < .5 else 1
        cv = Canvas(C, R, LAUNCH_BG)
        if op < .04: return cv.rows()
        for y in range(R):
            for x in range(C):
                if lv[y][x] < 0 or ch[y][x] == ' ': continue
                c = mix(LAUNCH_BG, LAUNCH_COL[lv[y][x]], op)
                cv.g[y][x] = (ch[y][x], tuple(min(255, q // 6 * 6 + 3) for q in c))
        return cv.rows()

    frames, DT, sub, T = [], 1 / 30, 30 // FPS, 0.0
    for _ in range(round(LOOP_S * FPS)):
        frames.append(render(T))
        for _ in range(sub): T += DT; step(T, DT)
    return frames


# ----------------------------------------------------------------------------------------- one per section
def about():
    path = [(4, 6, 'São Gabriel'), (6, 6), (8, 6), (10, 5), (12, 5), (14, 4), (16, 3, 'Porto Alegre'), (18, 3), (20, 3), (22, 3),
            (24, 3), (26, 2), (28, 2), (30, 1), (32, 1), (34, 0, 'São Paulo')]
    labels = {'São Gabriel': [(4, 7), 'home · rice & cattle'], 'Porto Alegre': [(18, 4), '2024 · alone, mid-year'],
              'São Paulo': [(36, 0), None]}
    frames = []
    n = len(path)
    for f in range(2 * n + 30):
        k = min(f // 2, n - 1)
        cv = Canvas(46, 9)
        for i, p in enumerate(path):
            x, y = p[0], p[1]
            if len(p) == 3:
                on = i <= k
                cv.put(x, y, '◆' if on else '◇', BLUE if on else DIM)
                (lx, ly), sub = labels[p[2]]
                if p[2] == 'São Paulo':
                    cv.text(lx, ly, 'São Paulo', WHITE if on else DIM); cv.text(lx, ly + 1, '2026 · now', BLUE if on else FAINT)
                else:
                    cv.text(lx, ly, p[2], WHITE if on else DIM); cv.text(lx, ly + 1, sub, GREY if on else FAINT)
            else:
                cv.put(x, y, '●' if i == k else '·', WHITE if i == k else BLUE if i < k else FAINT)
        frames.append(cv.rows())
    return frames


def sincra():
    nodes = [(2, 'surgery'), (14, 'audit'), (26, 'insurer'), (40, 'payout')]
    status = ['in surgery', 'internal audit', 'stuck at the insurer', 'paid']
    frames = []
    seq = list(range(2, 26)) + [26] * 18 + list(range(27, 41)) + [40] * 22
    for f, pos in enumerate(seq):
        cv = Canvas(46, 7)
        stage = max(i for i, (x, _) in enumerate(nodes) if x <= pos)
        for i, (x, name) in enumerate(nodes):
            cv.text(x - len(name) // 2 if i else 0, 0, name, WHITE if i == stage else GREY if i < stage else DIM)
        cv.text(2, 2, '─' * 39, FAINT); cv.text(2, 2, '─' * (pos - 2), BLUE)
        for i, (x, _) in enumerate(nodes): cv.put(x, 2, '●' if x <= pos else '○', BLUE if x <= pos else DIM)
        stuck = pos == 26 and f % 6 < 3
        cv.put(pos, 2, '●' if not stuck else '◌', YELLOW)
        days = min(47, f * 47 // 56)
        cv.text(0, 3, 'R$ 12.400', YELLOW); cv.text(10, 3, ' · ' + status[stage] + (' · day %d' % days if stage < 3 else ' ✓'),
                                                    GREEN if stage == 3 else GREY)
        cv.text(0, 5, 'sincra', BLUE); cv.text(7, 5, 'predicts', GREY)
        conf = min(87, f * 2); b = bar(conf / 100 * 16, 16)
        cv.text(16, 5, b, BLUE); cv.text(16 + len(b), 5, '░' * (16 - len(b)), FAINT)
        cv.text(33, 5, '%2d%% · day 47' % conf, WHITE if conf == 87 else GREY)
        frames.append(cv.rows())
    return frames


def rockets_mini():
    rocket = ['  /\\  ', ' |  | ', ' |()| ', ' |  | ', '/|__|\\']
    stars = [(3, 1), (11, 0), (19, 2), (30, 1), (41, 0), (44, 3), (7, 4), (36, 4)]
    frames = []
    rx, ground = 20, 8
    for f in range(52):
        cv = Canvas(46, 10)
        for i, (x, y) in enumerate(stars):
            tw = (f + i * 3) % 12
            cv.put(x, y, '+' if tw < 2 else '.', WHITE if tw < 2 else DIM)
        cv.text(0, ground + 1, '_' * 46, (74, 60, 51))
        cv.text(rx - 4, ground, '/' + '=' * 13 + '\\', (106, 93, 84))
        for y in range(3, ground): cv.text(rx + 9, y, '|' + ('/' if y & 1 else '\\') + '|', (106, 93, 84))
        cv.put(rx + 10, 2, '*' if f % 12 < 2 else '.', PINK if f % 12 < 2 else (106, 93, 84))
        u = f - 12
        y0 = ground - 5 - (int(0.06 * u * u) if u > 0 else 0)
        if f < 6:
            for j, line in enumerate(rocket):
                for i, ch in enumerate(line):
                    if ch != ' ': cv.put(rx + i, y0 + j, '!<>-_\\/[]{}=+*^?#%'[(i * 7 + j * 5 + f * 3) % 18] if (i + j + f) % 6 > f else ch, ORANGE)
        elif y0 > -6:
            for j, line in enumerate(rocket):
                for i, ch in enumerate(line):
                    if ch != ' ': cv.put(rx + i, y0 + j, ch, WIN_C if ch in '()' else HULL_C if i < 3 else SHADE_C)
        if 8 <= f < 50:
            fl = ['\\||/', ' || ', ' :: ', " '' "][:2 + (f % 3)]
            for j, line in enumerate(fl):
                if y0 + 5 + j >= ground:
                    w = 4 - j + f % 2
                    for dx in range(-w, w + 1): cv.put(rx + 2 + dx, ground, '*' if not dx else '=' if abs(dx) < w - 1 else '~', YELLOW if abs(dx) < 2 else ORANGE)
                    break
                for i, ch in enumerate(line):
                    if ch != ' ': cv.put(rx + 1 + i, y0 + 5 + j, ch, YELLOW if j == 0 else ORANGE if j < 2 else (226, 64, 31))
        if f >= 10:
            spread = min(20, (f - 10) * 1.2); fade = max(0, (f - 34) / 14)
            for k in range(int(spread)):
                for side in (-1, 1):
                    x = rx + 2 + side * (k + 2)
                    g = 'o' if k < spread * .4 else ':' if k < spread * .75 else '.'
                    if (k * 13 + f) % 7 / 7 > fade: cv.put(x, ground - (1 if k % 3 == 0 and k < spread * .6 else 0), g, mix((160, 150, 140), (60, 56, 52), k / 22 + fade))
        frames.append(cv.rows())
    return frames


def ai():
    frames = []
    def jobrow(cv, y, label, p, final, mark, col):
        cv.text(0, y, label, GREY); w = 20
        b = bar(p / 100 * w, w); cv.text(7, y, b, col); cv.text(7 + len(b), y, '░' * (w - len(b)), FAINT)
        cv.text(28, y, '%3d%%' % p, WHITE if p == final else GREY)
        if p == final and mark: cv.text(33, y, mark, RED if '✕' in mark else GREEN)
    plan = [('job 1', 70, '✕ 20:00 cap'), ('job 2', 70, '✕ from zero'), ('job 3', 70, '✕ from zero')]
    for f in range(130):
        cv = Canvas(46, 8)
        cv.text(0, 0, 'ONIA 2025', GREEN); cv.text(10, 0, '· gold · 1 of 28 among 716,000+', GREY)
        t = f
        for j, (lab, fin, mark) in enumerate(plan):
            start = j * 16
            if t >= start: jobrow(cv, 2 + j, lab, min(fin, (t - start) * 6), fin, mark, GREEN if j == 0 else (36, 160, 120))
        line = "+ YOLO(last).train(resume=True)"
        if t >= 52:
            cv.text(0, 5, 'what if', DIM); cv.text(8, 5, typed(line, (t - 52) * 2), YELLOW)
            if (t - 52) * 2 < len(line) and f % 4 < 2: cv.put(8 + (t - 52) * 2, 5, '▌', YELLOW)
        if t >= 72: jobrow(cv, 6, 'job 4', min(95, 70 + (t - 72) * 2), 95, '✓ Beijing', GREEN)
        frames.append(cv.rows())
    return frames


def voluntaria():
    heart = ['  .:::.   .:::.  ', ' ::::::: ::::::: ', ' :::::::::::::::', "  ':::::::::::'", "    ':::::::'", "      ':::'", "        '"]
    big = [' .:::::.  .:::::. ', ':::::::::::::::::: ', ":::::::::::::::::: ", " '::::::::::::::' ", "   ':::::::::::'", "     ':::::::'", "       ':'"]
    stats = [(170, '+', 'volunteers'), (20, '', 'NGOs'), (80, '+', 'blood donors'), (6300, '', 'Braille printer')]
    frames = []
    for f in range(70):
        cv = Canvas(46, 8)
        beat = f % 10 in (0, 2)
        for j, line in enumerate(big if beat else heart):
            for i, ch in enumerate(line):
                if ch != ' ': cv.put(i + (0 if beat else 1), j, ch, PINK if beat else (226, 64, 110))
        q = min(1, f / 24)
        q = 1 - (1 - q) ** 3
        for j, (n, plus, lab) in enumerate(stats):
            v = round(n * q)
            num = ('R$%s' % format(v, ',')) if n == 6300 else '%d%s' % (v, plus)
            row = 1 + j + (j == 3)
            cv.text(20, row, num.rjust(8), YELLOW); cv.text(29, row, lab, GREY)
        cv.text(21, 7, 'Porto Alegre · 2024–2025', DIM)
        frames.append(cv.rows())
    return frames


def audience():
    pages = [('@seusiriqueijo', 183, 'crab'), ('@gatinhoajude', 83, 'cat'), ('@inteligenciai', 50, 'AI')]
    frames = []
    for f in range(72):
        cv = Canvas(46, 8)
        q = 1 - (1 - min(1, f / 16)) ** 3
        for j, (h, k, _) in enumerate(pages):
            cv.text(0, j, h, PINK if j == 0 else GREY)
            b = bar(k / 183 * 22 * q, 22); cv.text(16, j, b, PINK if j == 0 else (180, 70, 110))
            cv.text(40, j, ('%dK' % round(k * q)).rjust(5), WHITE)
        cv.text(0, 4, '7.2M reached in 30 days · all three sold', DIM)
        x = f if f < 36 else 71 - f
        legs = ',,,,' if f % 2 else "''''"
        cv.text(x, 6, '(\\/)(°' + legs + '°)(\\/)', (255, 106, 46))
        cv.text(0, 7, ''.join('~' if (i + f) % 9 == 0 else '.' if (i * 7) % 5 == 0 else '_' for i in range(46)), (120, 104, 80))
        frames.append(cv.rows())
    return frames


def data():
    vals = [2.1, 2.6, 2.4, 3.1, 3.4, 3.2, 3.9, 4.2, 4.0, 4.6, 5.1, 5.6]
    months = 'JFMAMJJASOND'
    H, top = 5, 6.0
    frames = []
    for f in range(70):
        cv = Canvas(46, 8)
        cv.text(0, 0, 'RBS Group · Q4 sales forecast', WHITE)
        for i, v in enumerate(vals):
            fc = i >= 9
            start = i * 2 if not fc else 26 + (i - 9) * 4
            q = 0 if f < start else min(1, (f - start) / 8)
            h = v / top * H * (1 - (1 - q) ** 2) * 8
            x = 2 + i * 3
            for r in range(H):
                cell = h - r * 8
                ch = '█' if cell >= 8 else ' ▁▂▃▄▅▆▇'[int(cell)] if cell > 0 else ''
                if ch.strip():
                    cv.text(x, 1 + H - 1 - r, ch * 2, GREEN if fc else BLUE)
            cv.put(x, 1 + H, months[i], GREEN if fc else DIM)
        cv.text(38, 2, 'forecast', GREEN if f >= 26 else FAINT)
        cv.text(38, 3, 'Oct–Dec', GREEN if f >= 26 else FAINT)
        if f >= 44: cv.text(38, 5, '★ won', YELLOW if f % 8 < 6 else WHITE)
        cv.text(0, 7, 'Geração Caldeira · 200 of ~18,000', DIM)
        frames.append(cv.rows())
    return frames


def flying():
    face = [" .-'''-. ", '/       \\', '|       |', '\\       /', " '-...-' "]
    dirs = [(0, -1, '|'), (1, -1, '/'), (2, -1, '/'), (2, 0, '─'), (2, 1, '\\'), (1, 1, '\\'), (0, 1, '|'), (-1, 1, '/'),
            (-2, 1, '/'), (-2, 0, '─'), (-2, -1, '\\'), (-1, -1, '\\')]
    frames = []
    for f in range(80):
        cv = Canvas(46, 8)
        ph = f / 80 * 2 * math.pi
        alt = 4500 + 400 * math.sin(ph); spd = 105 + 6 * math.sin(ph * 3); hdg = (32 + f * 4.5) % 360
        gauges = [('ALT', alt / 1000 * 12 / 10, '%s ft' % format(int(alt // 10 * 10), ',')), ('SPD', (spd - 60) / 100 * 12, '%d kt' % spd),
                  ('HDG', hdg / 30, '%03d°' % hdg)]
        for g, (name, a, read) in enumerate(gauges):
            gx = 1 + g * 15
            for j, line in enumerate(face):
                for i, ch in enumerate(line):
                    if ch != ' ': cv.put(gx + i, j, ch, GREY)
            cx, cy = gx + 4, 2
            dx, dy, ch = dirs[int(round(a)) % 12]
            cv.put(cx, cy, 'o', WHITE); cv.put(cx + dx, cy + dy, ch, ORANGE)
            if abs(dx) == 2: cv.put(cx + dx // 2, cy + (dy if dy else 0), ch if dy else '─', ORANGE)
            cv.text(gx + 4 - len(name) // 2, 5, name, DIM)
            cv.text(gx + 4 - len(read) // 2, 6, read, WHITE)
        cv.text(0, 7, 'cardboard cockpit → co-pilot, May 2024', BLUE if f % 40 < 38 else WHITE)
        frames.append(cv.rows())
    return frames


def side():
    pop = [' .-"""-. ', '/       \\', '|       |', '|       |', '|       |', "'-.___.-'", '   | |   ', '   | |   ', "   '-'   "]
    quests = [('markets', 'age 12 · a stock chart'), ('popsicles', 'R$2,000 · banned at school'), ('Step Up', '32 English lessons'),
              ('Advogado Rural', 'a lawyer reaches farmers'), ('Farroupilha AI', 'grades essays')]
    frames = []
    for f in range(100):
        cv = Canvas(46, 9)
        for j, line in enumerate(pop):
            for i, ch in enumerate(line):
                if ch == ' ': continue
                c = STRAW if j >= 6 else PINK if (j + (f // 5)) % 3 else (255, 140, 175)
                cv.put(i, j, ch, c)
        cv.put(2, 2, '▖', WHITE)
        d = f % 20
        if d < 9: cv.put(6, 5 + d // 2 if d < 8 else 8, "'" if d < 4 else '.' if d < 8 else '_', PINK)
        q = (f // 20) % len(quests)
        name, sub = quests[q]
        n = (f % 20) * 3
        cv.text(13, 2, 'side quest %d/%d' % (q + 1, len(quests)), DIM)
        cv.text(13, 3, typed(name, n), WHITE); cv.text(13, 4, typed(sub, n - len(name)), GREY)
        for k in range(len(quests)): cv.put(13 + k * 2, 6, '●' if k == q else '·', PINK if k == q else DIM)
        frames.append(cv.rows())
    return frames


def farm():
    cow = ['^__^', '(oo)\\_______', '(__)\\       )\\/\\', '    ||----w |', '    ||     ||']
    frames = []
    for f in range(60):
        cv = Canvas(46, 8)
        rays = ['\\ | /', '- O -', '/ | \\'] if f % 10 < 5 else [' \\|/ ', '-(O)-', ' /|\\ ']
        for j, line in enumerate(rays):
            for i, ch in enumerate(line):
                if ch != ' ': cv.put(38 + i, j, ch, YELLOW)
        for j, line in enumerate(cow):
            if j == 1 and f % 30 in (12, 13): line = '(--)\\_______'
            if j == 2 and f % 6 < 3: line = line[:-3] + '/\\/'
            for i, ch in enumerate(line):
                if ch != ' ': cv.put(4 + i, 1 + j, ch, WHITE if j < 3 or ch in '|w' else GREY)
        for x in range(46):
            w = math.sin(x * .45 - f * .5)
            cv.put(x, 6, ',' if w > .3 else "'" if w < -.3 else '"', STRAW)
            cv.put(x, 7, '/' if w > .3 else '\\' if w < -.3 else '|', (120, 170, 80))
        frames.append(cv.rows())
    return frames


def honors():
    medal = ['\\\\   //', ' \\\\ // ', '  )=(  ', ".'   '.", '/  ★  \\', '| 1st |', "\\     /", " '._.' "]
    lst = ['ONIA gold', 'OBA gold', 'ONIA ambassador', 'BRICS speaker', 'Caldeira fellow', 'book preface', 'solver #76',
           '"Alamar" top 1%', 'top 5 clipping']
    frames = []
    glint = [(1, 3), (0, 4), (1, 5), (2, 6), (4, 6), (5, 5), (6, 4), (5, 3)]
    for f in range(54):
        cv = Canvas(46, 9)
        for j, line in enumerate(medal):
            for i, ch in enumerate(line):
                if ch == ' ': continue
                cv.put(1 + i, j, ch, (BLUE if i < 3 else PINK) if j < 2 else YELLOW)
        g = f % 18
        if g < len(glint): gx, gy = glint[g]; cv.put(1 + gx, gy, '*', WHITE)
        k = min(9, f // 3 + 1)
        cv.text(12, 0, '%d honors' % k, YELLOW)
        for i, h in enumerate(lst[:k]):
            cv.text(12 if i < 5 else 30, 2 + i % 5, '▸ ' + h, WHITE if i == k - 1 else GREY)
        frames.append(cv.rows())
    return frames


def timeline():
    years = [('2017', 'films', '3 summers, 3 films'), ('2020', 'markets', 'stocks at 12'), ('2022', 'rockets', 'built from fireworks'),
             ('2023', '316K', 'crab, cat, AI'), ('2024', 'move', 'Porto Alegre, alone'), ('2025', 'gold', 'ONIA, OBA, BRICS'),
             ('2026', 'Sincra', 'São Paulo')]
    frames = []
    for f in range(len(years) * 12 + 10):
        k = min(len(years) - 1, f // 12)
        cv = Canvas(46, 6)
        cv.text(0, 1, '─' * 44, FAINT); cv.text(0, 1, '─' * (k * 7 + 2), BLUE)
        for i, (y, w, d) in enumerate(years):
            x = i * 7
            cv.text(x, 0, y, WHITE if i == k else GREY if i < k else DIM)
            cv.put(x + 1, 1, '●' if i <= k else '○', YELLOW if i == k else BLUE if i < k else DIM)
        y, w, d = years[k]
        n = (f - k * 12) * 3 if f < len(years) * 12 else 99
        cv.text(k * 7, 2, '▲', YELLOW)
        cv.text(0, 4, typed(w, n), WHITE); cv.text(len(w) + 1, 4, typed('· ' + d, n - len(w)), GREY)
        frames.append(cv.rows())
    return frames


def press():
    items = [('RBS TV', 'Jul 2026', 'The Morro da Cruz art school, part-funded through Voluntaria+'),
             ('ZERO HORA', 'Jul 2026', 'Porto Alegre gets a graffiti and visual arts school'),
             ('BRASIL DE FATO', 'Jul 2026', "Students make a cultural space's renovation possible"),
             ('SBT RS', 'Oct 2025', 'InovaTec and Voluntaria+ on SBT'), ('RBS TV', 'Aug 2025', 'National Volunteering Day, featuring Voluntaria+'),
             ('CORREIO DO POVO', 'Jul 2024', 'Solidarity actions mobilize students')]
    import textwrap
    frames = []
    for f in range(len(items) * 22):
        q, n = f // 22, (f % 22) * 4
        o, d, h = items[q]
        cv = Canvas(46, 8)
        cv.text(0, 0, '┌' + '─' * 42 + '┐', GREY)
        for y in range(1, 7): cv.put(0, y, '│', GREY); cv.put(43, y, '│', GREY)
        cv.text(0, 7, '└' + '─' * 42 + '┘', GREY)
        cv.text(2, 1, o, WHITE); cv.text(41 - len(d), 1, d, DIM); cv.text(1, 2, '═' * 42, GREY)
        for j, line in enumerate(textwrap.wrap(h, 38)[:2]): cv.text(2, 3 + j, typed(line, n - j * 38), WHITE)
        cv.text(2, 5, '▓' * 10, FAINT); cv.text(14, 5, '░' * 27, FAINT); cv.text(14, 6, '░' * 20, FAINT)
        cv.text(2, 6, '%d/%d' % (q + 1, len(items)), DIM)
        frames.append(cv.rows())
    return frames


def films():
    names = ['BATATINHA 1', 'BATATINHA 2', 'BATATINHA 3', 'GUERRA FRIA', 'FOGUETE 7/2023', 'PEDRAS DO INFINITO']
    cellw = 22
    strip = ''.join(('│ ' + n).ljust(cellw) for n in names)
    L = len(strip)
    frames = []
    for f in range(L // 2):
        off = f * 2
        cv = Canvas(46, 6)
        seq = (strip * 3)[off:off + 46]
        holes = ''.join('■' if (i + off) % 4 == 0 else ' ' for i in range(46))
        cv.text(0, 0, holes, FAINT); cv.text(0, 4, holes, FAINT)
        for i, ch in enumerate(seq):
            cv.put(i, 2, ch, GREY if ch == '│' else ORANGE)
            if ch == '│': cv.put(i, 1, '│', GREY); cv.put(i, 3, '│', GREY)
            elif (strip * 3)[off + i - 2:off + i] == '│ ': cv.text(i, 3, '▶ YouTube', DIM)
        cv.put(0, 5, '●', RED if f % 10 < 5 else FAINT); cv.text(2, 5, 'Filmes Pedro · before all of this', DIM)
        frames.append(cv.rows())
    return frames


def ask():
    qn = 'who is Pedro Veríssimo?'
    ans = ['A builder from São Gabriel, Brazil.', 'Rockets, an AI gold, 316K followers,', 'and now Sincra. Ask me more.']
    frames = []
    for f in range(110):
        cv = Canvas(46, 9)
        cv.text(0, 0, '╭' + '─' * 26 + '╮', GREY); cv.text(0, 1, '│ ' + typed(qn, f * 2).ljust(24) + ' │', GREY)
        cv.text(2, 1, typed(qn, f * 2), WHITE); cv.text(0, 2, '╰' + '─' * 26 + '╯', GREY)
        t = f - 16
        if t > 0:
            cv.text(6, 3, '╭' + '─' * 38 + '╮', GREEN)
            for j in range(3): cv.put(6, 4 + j, '│', GREEN); cv.put(45, 4 + j, '│', GREEN)
            cv.text(6, 7, '╰' + '─' * 38 + '╯', GREEN)
            if t < 12: cv.text(8, 4, ['●  ·  ·', '·  ●  ·', '·  ·  ●'][(t // 2) % 3], GREEN)
            else:
                n = (t - 12) * 3
                for j, line in enumerate(ans): cv.text(8, 4 + j, typed(line, n - sum(len(a) for a in ans[:j])), WHITE)
        cv.text(0, 8, 'llms.txt → ChatGPT · Claude · Grok · Perplexity', DIM)
        frames.append(cv.rows())
    return frames


def contact():
    env = ['┌─────────────────────┐', '│╲                   ╱│', '│  ╲               ╱  │', '│    ╲───────────╱    │',
           '│                     │', '└─────────────────────┘']
    msg = 'hi pedro, saw the rocket...'
    frames = []
    for f in range(80):
        cv = Canvas(46, 8)
        for j, line in enumerate(env):
            for i, ch in enumerate(line):
                if ch != ' ': cv.put(i, j, ch, BLUE if j < 4 and ch in '╲╱─' and j else GREY)
        cv.text(26, 1, 'say hello.', WHITE); cv.text(26, 2, 'I answer.', BLUE)
        n = max(0, f - 8)
        cv.text(0, 7, '> ' + typed(msg, n), WHITE)
        if f % 6 < 3: cv.put(2 + min(n, len(msg)), 7, '▌', BLUE)
        frames.append(cv.rows())
    return frames


ART = {'about': about, 'sincra': sincra, 'rockets': rockets_mini, 'ai': ai, 'voluntaria': voluntaria, 'audience': audience,
       'data': data, 'flying': flying, 'side': side, 'farm': farm, 'honors': honors, 'timeline': timeline, 'press': press,
       'films': films, 'ask': ask, 'contact': contact}
# the frame the static (curl) page shows
POSTER = {'about': -1, 'sincra': -1, 'rockets': 0, 'ai': -1, 'voluntaria': -1, 'audience': 30, 'data': -1, 'flying': 0, 'side': 30,
          'farm': 0, 'honors': -1, 'timeline': -1, 'press': 21, 'films': 0, 'ask': -1, 'contact': 40}
