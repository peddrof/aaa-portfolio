"""ASCII art and animations for the terminal version.

Every animation is a list of frames; a frame is a list of ANSI strings, one per row, all frames the same height.
Animations play at FPS. `launch()` is a port of the canvas launch on the page (index.html, section 14).
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
# Grid of glyphs; smoke is particles splatted into a density field, glyph = density (edges pick a slope
# glyph from the gradient), colour = light from the flame. World units are column widths, y = row * A.
_STOPS = [(0, '#1A0E2A'), (.1, '#3B1450'), (.2, '#7A1A5A'), (.3, '#B8263F'), (.4, '#E2401F'), (.5, '#FF5A1F'), (.6, '#FF7A1A'),
          (.7, '#FF9A1A'), (.8, '#FFB31A'), (.88, '#FFCB3A'), (.94, '#FFE28A'), (1, '#FFF8EA')]
_hx = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
_NR = 40
_COL = []
for _i in range(_NR):
    _t = _i / (_NR - 1); _j = 0
    while _j < len(_STOPS) - 2 and _STOPS[_j + 1][0] < _t: _j += 1
    (_p0, _c0), (_p1, _c1) = _STOPS[_j], _STOPS[_j + 1]
    _COL.append(mix(_hx(_c0), _hx(_c1), (_t - _p0) / (_p1 - _p0)))
def _add(c): _COL.append(_hx(c)); return len(_COL) - 1
HULL, SHADE, WIN, PNK, VIO, STEEL, GND, HUD, STAR = map(_add, ['#F2EEE6', '#9A9288', '#7FA6FF', '#FF4F8B', '#A38CFF', '#6A5D54', '#4A3C33', '#7D786F', '#C9C2B6'])

def _cl(v): return 0.0 if v < 0 else 1.0 if v > 1 else v
def _ri(v): return round(_cl(v) * (_NR - 1))
def _ss(v): v = _cl(v); return v * v * (3 - 2 * v)

RK = [['    ^    ', '    w    '], ["   /'\\   ", '   ewe   '], ['  /___\\  ', '  eeeee  '], ['  | o |  ', '  w b s  '], ['  |   |  ', '  w   s  '],
      ['  |===|  ', '  waaas  '], [' /|   |\\ ', ' ew   se '], ['/_|___|_\\', 'eewssssee'], ['   /_\\   ', '   ggg   ']]
_RH = len(RK)
_RKS = [(s.find(s.strip()[0]), len(s.rstrip()) - 1) for s, _ in RK]
_RKC = {'w': HULL, 's': SHADE, 'e': _ri(.56), 'a': _ri(.85), 'b': WIN, 'g': STEEL}
_SMG, _EDG, _SCR, _FP = ' .:-=+*o%#@', '(/~\\)/-\\', '!<>-_\\/[]{}=+*^?#%', ['|||', '\\|/', '<*>', '/|\\', '(|||)', '\\|/']
_PM = list(range(256))
_s = 1234567
for _i in range(255, 0, -1):
    _s = _s * 16807 % 2147483647; _k = _s % (_i + 1); _PM[_i], _PM[_k] = _PM[_k], _PM[_i]
_PM = _PM + _PM

def _vn(x, y):
    xi, yi = math.floor(x), math.floor(y); u, v = x - xi, y - yi; X, Y = xi & 255, yi & 255
    s, r = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
    A, B, C_, D = _PM[_PM[X] + Y], _PM[_PM[X + 1] + Y], _PM[_PM[X] + Y + 1], _PM[_PM[X + 1] + Y + 1]
    return (A + (B - A) * s + (C_ - A) * r + (A - B - C_ + D) * s * r) / 255

def _fbm(x, y): return _vn(x, y) * .55 + _vn(x * 2.1 + 19, y * 2.1 + 7) * .3 + _vn(x * 4.3 + 3, y * 4.3 + 41) * .15

def _hsh(i):
    M = 0xFFFFFFFF
    h = ((i ^ 0x9E3779B9) * 0x85EBCA6B) & M; h ^= h >> 13; h = (h * 0xC2B2AE35) & M; h ^= h >> 16
    return h / 4294967296

LAUNCH_BG = (7, 8, 11)
LOOP_S, T_IGN, T_LIFT, T_FILL0, T_FILL1, T_FADE0, T_FADE1 = 12.2, 2, 2.6, 6.4, 9, 9.5, 11.5


def launch(C=68, R=18, A=2.0, seed=7919):
    """One loop of the launch (pad, liftoff, ground cloud, fill, clear) at FPS. Returns frames."""
    hz = round(R * .8); xc = C >> 1; top0 = hz - 1 - _RH; ACC = 2 * (top0 + _RH + 4) / (3.4 * 3.4); N = C * R
    HS = [_hsh(i) for i in range(N)]
    VG = [0.0] * N
    for y in range(R):
        for x in range(C):
            ex, ey = (x + .5) / C * 2 - 1, (y + .5) / R * 2 - 1
            VG[y * C + x] = (_ss(min(x + .5, C - x - .5) / (C * .14)) * _ss((y + .5) / (R * .2)) * _ss((R - y - .5) / (R * .1))
                             * _ss((1.34 - math.hypot(ex, ey)) / .42))
    rng, fl = random.Random(seed), random.Random(seed * 3)
    rnd, frnd = rng.random, fl.random
    parts, sparks = [], []
    st = {'T': 0.0}

    def spawn(x, y, vx, vy, r, m, h, gr):
        if len(parts) < 1800: parts.append([x, y, vx, vy, r, m, h, gr, 0.0, rnd() * 2, rnd() * 50])

    def rocket_top(t):
        u = t - T_LIFT
        return top0 - .5 * ACC * u * u if u > 0 else top0

    def step(dt):
        st['T'] += dt; t = st['T']; u = t - T_LIFT
        noz = rocket_top(t) + _RH; vR = ACC * u * A if u > 0 else 0; xe = xc + .5; deck = (hz - 1) * A; fade = t > T_FADE0
        if .8 < t < T_IGN and rnd() < .45: spawn(xc - 2.5, (top0 + 5.5) * A, -(1 + rnd() * 2), rnd() * 1.2, .4, .12, .35, 0)
        if t >= T_IGN and noz > -10:
            ramp = _cl((t - T_IGN) / .3)
            if (noz + 3) * A >= deck:
                for _ in range(round(4 * ramp)):
                    s = -1 if rnd() < .5 else 1; up = rnd() < .25
                    spawn(xe + s * rnd() * 2, deck - rnd() * A, s * (1 + rnd() * 4 if up else 3 + rnd() * 10),
                          -(2 + rnd() * 5) if up else (rnd() - .7) * 6, .8 + rnd() * .8, .8 + rnd() * .3, 1, 1)
            if u > 0:
                for _ in range(7):
                    spawn(xe + (rnd() - .5) * 1.2, (noz + 1 + rnd() * 2) * A, (-1 if rnd() < .5 else 1) * (2.5 + rnd() * 4.5),
                          22 + rnd() * 10 - vR, .6 + rnd() * .5, .8, 1, 0)
            if t < T_LIFT + 1.2:
                for _ in range(3):
                    sparks.append([xe + (rnd() - .5) * 4, deck - rnd() * A, (rnd() - .5) * 46, -(8 + rnd() * 34), 0.0, .35 + rnd() * .6, rnd()])
        for i in range(len(parts) - 1, -1, -1):
            p = parts[i]; p[8] += dt; x, y, gr, h = p[0], p[1], p[7], p[6]
            n1 = _vn(x * .11 + p[10], y * .11 - t * .7) - .5; n2 = _vn(x * .11 + 71, y * .11 + p[10] - t * .7) - .5
            p[2] += n1 * 14 * dt
            p[3] += (n2 * (7 if gr else 12) - (.3 + 2.5 * h if gr else 1.1 + 4 * h)) * dt
            p[2] *= math.exp(-(.5 if gr else .35) * dt); p[3] *= math.exp(-(1.2 if gr else 1.5) * dt)
            p[0] += p[2] * dt; p[1] += p[3] * dt
            floor = (hz - 1 + p[9]) * A
            if p[1] > floor:
                if not p[7]:
                    p[7] = 1
                    s = (-1 if rnd() < .5 else 1) if abs(p[0] - xe) < .6 else (1 if p[0] > xe else -1)
                    p[2] += s * min(12, abs(p[3])) * (.4 + .5 * rnd())
                p[1] = floor; p[3] = -abs(p[3]) * .12
            p[4] += dt * (1.6 * math.exp(-p[8] * .9) + .4 if p[7] else 1.4 * math.exp(-p[8] * .9) + 1.3)
            p[6] *= math.exp(-dt * 2.4); p[5] *= math.exp(-dt * (1.5 if fade else .1))
            if p[5] < .02 or p[0] < -30 or p[0] > C + 30 or p[1] < -40: parts.pop(i)
        for i in range(len(sparks) - 1, -1, -1):
            s = sparks[i]; s[4] += dt; s[3] += 50 * dt; s[0] += s[2] * dt; s[1] += s[3] * dt
            if s[4] > s[5] or s[1] > (hz + .3) * A: sparks.pop(i)

    def render():
        t = st['T']; u = t - T_LIFT; rt = round(rocket_top(t)); noz = rt + _RH; eng = T_IGN <= t < T_FILL1
        IF = _cl((t - T_IGN) / .15) * (.85 + .15 * frnd()) if eng and noz > -14 else 0
        fx, fy = xc + .5, min(noz + 2, hz - 1) * A
        def lit(x, y):
            dx, dy = x + .5 - fx, (y + .5) * A - fy
            return IF / (1 + (dx * dx + dy * dy) / 160)
        CH, CI, AL, MK = [None] * N, [0] * N, [0.0] * N, [0] * N
        DEN, HT, DD, NZ = [0.0] * N, [0.0] * N, [0.0] * N, [0.0] * N
        def put(x, y, ch, ci, al, m):
            if 0 <= x < C and 0 <= y < R:
                i = y * C + x; CH[i] = ch; CI[i] = ci; AL[i] = al
                if m: MK[i] = m
        for y in range(hz - 1):
            for x in range(C):
                i = y * C + x; h = HS[i]
                if h < .016:
                    k = h / .016
                    put(x, y, '.' if k < .72 else '+' if k < .9 else '*', PNK if k > .95 else VIO if k > .86 else STAR,
                        (.18 + .42 * (.5 + .5 * math.sin(t * (1.2 + k * 2.6) + i))) * VG[i], 4)
        for y in range(hz, R):
            for x in range(C):
                i = y * C + x; h = HS[i]
                if y == hz: c = '_'
                elif h < .04 + .12 * (y - hz) / (R - hz): c = ".,'`"[int(h * 997) & 3]
                else: continue
                l = lit(x, y)
                put(x, y, c, _ri(.4 + .6 * l) if l > .1 else GND, _cl((.7 if y == hz else .4) + l) * VG[i], 3)
        for x in range(xc - 7, xc + 11):
            l = lit(x, hz - 1)
            put(x, hz - 1, '/' if x == xc - 7 else '\\' if x == xc + 10 else '=', _ri(.45 + .55 * l) if l > .15 else STEEL, 1, 2)
        tx = xc + 6
        for y in range(top0 + 1, hz - 1):
            l = lit(tx + 1, y); c = _ri(.4 + .55 * l) if l > .18 else STEEL
            put(tx, y, '|', c, .9, 2); put(tx + 1, y, '/' if y & 1 else '\\', c, .6, 2); put(tx + 2, y, '|', c, .9, 2)
        put(tx, top0, '-', STEEL, .9, 2); put(tx + 1, top0, '+', STEEL, .9, 2); put(tx + 2, top0, '-', STEEL, .9, 2)
        bl = t % 1.2 < .18
        put(tx + 1, top0 - 1, '*' if bl else '.', PNK if bl else STEEL, 1 if bl else .5, 2)
        arm = 3 if t < T_IGN else max(0, 3 - math.floor((t - T_IGN) / .12))
        for k in range(arm): put(tx - 1 - k, top0 + 4, '=', STEEL, .9, 2)
        if noz > 0:
            asm = t / .7 if t < .7 else 1
            for r in range(_RH):
                y = rt + r
                if y < 0 or y >= R: continue
                s, cm = RK[r]
                for k in range(_RKS[r][0], _RKS[r][1] + 1):
                    x = xc - 4 + k; ch = s[k]
                    if ch == ' ': put(x, y, ' ', 0, 0, 1); continue
                    ci, g = _RKC[cm[k]], ch
                    if asm < 1 and HS[(r * 9 + k) * 131 % N] > asm:
                        g = _SCR[int(frnd() * len(_SCR))]; ci = _ri(.55 + frnd() * .45)
                    elif IF and r >= _RH - 4 and ci in (HULL, SHADE):
                        l = lit(x, y)
                        if l > .4: ci = _ri(.62 + .38 * l)
                    put(x, y, g, ci, 1, 1)
        for p in parts:
            r = p[4]; rr = r / A; ir = 1 / (r * r); py = p[1] / A
            x0, x1 = max(0, math.floor(p[0] - r)), min(C - 1, math.ceil(p[0] + r))
            y0, y1 = max(0, math.floor(py - rr)), min(R - 1, math.ceil(py + rr))
            for y in range(y0, y1 + 1):
                dy = (y + .5) * A - p[1]; dy2 = dy * dy
                for x in range(x0, x1 + 1):
                    dx = x + .5 - p[0]; q = (dx * dx + dy2) * ir
                    if q < 1:
                        w = p[5] * (1 - q) * (1 - q); i = y * C + x; DEN[i] += w; HT[i] += w * p[6]
        F = 0 if t < T_FILL0 else _ss((t - T_FILL0) / (T_FILL1 - T_FILL0))
        K = 0 if t < T_FADE0 else _cl((t - T_FADE0) / (T_FADE1 - T_FADE0))
        for y in range(R):
            hN = (hz - y) / hz
            for x in range(C):
                i = y * C + x; D = DEN[i]
                if D < .004 and F <= 0: continue
                nz = NZ[i] = _fbm(x * .085, y * A * .085 + t * .45); nb = _vn(x * .07 + 9, y * A * .07 + t * .3)
                d = (1 - math.exp(-D * .5)) * (.35 + 1.1 * nz) * (.35 + .9 * _ss((nb - .2) / .5))
                if F > 0:
                    fd = _cl((F * 1.6 - .3 - hN) / .3 + (nz - .5) * 1.8) * (.2 + .55 * nz + .3 * nb); d = 1 - (1 - _cl(d)) * (1 - fd)
                if K > 0: d *= 1 - _ss(K * 1.9 - .7 * nb - .2 * HS[i])
                DD[i] = _cl(d)
        gl = .12 if T_IGN < t < T_FADE0 else 0
        for y in range(1, R - 1):
            hN = (hz - y) / hz; bg = gl * _cl(1 - (hz - y) / 9)
            for x in range(1, C - 1):
                i = y * C + x; v = VG[i]; d = DD[i] * (.45 + .55 * v)
                if d < .05: continue
                m = MK[i]
                if (m == 1 and d < .92) or (m == 2 and d < .35): continue
                ko = .35 if MK[i - 1] == 1 or MK[i + 1] == 1 else 1
                gx = (DD[i + 1] - DD[i - 1]) * .5; gy = (DD[i + C] - DD[i - C]) * .5 / A; g2 = gx * gx + gy * gy
                if d < .55 and g2 > .012: ch = _EDG[round(math.atan2(gy, gx) / (math.pi / 4)) & 7]
                else: ch = _SMG[min(len(_SMG) - 1, max(1, int(d * (len(_SMG) - .01) + (HS[i] - .5) * .9)))]
                lx, ly = fx - x - .5, fy - (y + .5) * A; ln = math.hypot(lx, ly) or 1; gn = math.sqrt(g2) or 1
                lam = .5 - .5 * (gx * lx + gy * ly) / (gn * ln) if g2 > 1e-5 else .5
                D = DEN[i]; hh = HT[i] / D if D > .01 else 0
                lt = .28 + .62 * lit(x, y) * (.35 + .9 * lam) + .35 * hh + .1 * d + bg + (NZ[i] - .5) * .3
                if F > 0: lt = max(lt, (.3 + .35 * _cl(1 - hN) + .3 * NZ[i]) * F)
                put(x, y, ch, _ri(lt * (1 - .55 * K)), _cl(.3 + d * 1.3) * v * ko, 0)
        if IF and noz < R:
            sp = _cl((t - T_IGN) / .35); L = round(5 + min(3, (ACC * u if u > 0 else 0) * .15) + frnd() * 2)
            for k in range(L + 3):
                y = noz + k
                if y < 0: continue
                if y >= hz - 1:
                    if k < L:
                        s = k / L; W = round(1 + 9 * sp * (1 - s))
                        for dx in range(-W, W + 1):
                            I = (1 - abs(dx) / (W + 1)) * (1 - s * .6)
                            put(xc + dx, hz - 1, ('=' if I > .6 else '~' if I > .38 else '-') if dx else '*', _ri(.5 + .5 * I), _cl(.5 + I), 5)
                    break
                if k >= L:
                    for dx in range(-2, 3):
                        if frnd() < .4 * (1 - (k - L) / 3): put(xc + dx, y, ":'.`"[int(frnd() * 4)], _ri(.48 + .25 * frnd()), .6, 5)
                    continue
                ty = k if k < 2 else 2 + ((k - 2) & 3); cy = 0 if k < 2 else (k - 2) >> 2; pat = _FP[ty]; n = len(pat); I = 1 - k / L * .55
                for j in range(n):
                    g = pat[j]; off = abs(j - (n - 1) / 2)
                    if g in '<>': ci = PNK
                    elif g == '*': g = ('.' if cy > 1 else '+') if cy else '*'; ci = _NR - 1
                    else:
                        if g == '|' and frnd() < (.45 if cy else .12): g = ':' if cy else '!'
                        elif g in '()' and frnd() < .2: g = '{' if g == '(' else '}'
                        ci = _ri(.78 + .22 * I if off < .5 else .6 + .3 * I if off < 1.5 else .5 + .3 * I)
                    put(xc - ((n - 1) >> 1) + j, y, g, ci, _cl(.45 + .65 * I), 5)
        for s in sparks:
            q = 1 - s[4] / s[5]; x = math.floor(s[0]); y = math.floor(s[1] / A)
            if x < 0 or x >= C or y < 0 or y >= R or MK[y * C + x] == 1: continue
            put(x, y, '*' if q > .6 else "'" if q > .3 else '.', PNK if s[6] < .25 else _ri(.75 + .25 * q), _cl(q * 1.4), 0)
        if 1.9 < u < 2.7:
            e = math.sin(math.pi * (u - 1.9) / .8)
            for j in range(3, 11):
                y = rt + j; al = e * (1 - j / 11)
                put(xc - j, y, '/', VIO if j % 3 else PNK, al, 0); put(xc + j, y, '\\', VIO if j % 3 else PNK, al, 0)
        tt = t - T_LIFT; sec = math.ceil(-tt) if tt < 0 else math.floor(tt)
        lab = 'T%s00:%02d' % ('-' if tt < 0 else '+', sec)
        if t < T_FADE0:
            for k, ch in enumerate(lab): put(2 + k, 1, ch, _ri(.6) if 0 <= tt < 1.5 else HUD, .85, 0)
        cv = Canvas(C, R, LAUNCH_BG)
        for i in range(N):
            ch = CH[i]
            if not ch or ch == ' ' or AL[i] < .04: continue
            # the page adds a bloom pass; a little extra alpha stands in for it
            c = mix(LAUNCH_BG, _COL[CI[i]], min(1, AL[i] * 1.12))
            cv.g[i // C][i % C] = (ch, tuple(min(255, v // 6 * 6 + 3) for v in c))
        return cv.rows()

    frames, DT, sub = [], 1 / 30, 30 // FPS
    for f in range(round(LOOP_S * FPS)):
        frames.append(render())
        for _ in range(sub): step(DT)
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
