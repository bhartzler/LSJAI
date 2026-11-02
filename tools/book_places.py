#!/usr/bin/env python3
"""Where each printed page and each entry stand in the Internet Archive's scan of the ninth edition
(greekenglishlexi12lidd): site/pages.json, {printed page: leaf}, the leaf counted from 0 as the Archive's
page/n<leaf> counts it (its image is the scan's file leaf + 1); and site/places.json, {entry id: [file,
x, y, w, h, how]}, the image file the entry stands on and its region there in the scan's pixels, from
its headword's line to the next entry's in the column; how is l (its first line found), i (found inside
another's paragraph), b (placed between found neighbours by the share of the text before it), p (only
its page known) or r (placed by a reader). site/build.py gives each entry its place; the page opens the
scan there. A reader's place is final: a row whose how is r is kept as it is when the program runs again.

    python3 -I tools/book_places.py --ocr <greekenglishlexi12lidd_djvu.xml> [--columns <columns.jsonl>]

Reads the Archive's OCR of the scan (the item's _djvu.xml, every word with its box on its leaf) and the
files' <pb> (site/build.py's PRINTED: the page an entry begins on). Standard library only.

The pages. Every page of the text carries two running heads, the first entry that begins a paragraph on
the page and the last entry on it, and its number at the top centre. A leaf is matched to a page when its
heads match the page's first and last entries and its number agrees (two of the three); the matches kept
are the longest chain in which page and leaf both rise and the leaves between pages never shrink. Between
two matches the pages follow at the same distance; where the distance grows, leaves are bound in that are
no page of the text (the parts' Addenda and the second volume's title), and the pages between go where
their entries' headwords begin the leaf's lines. The Addenda et Corrigenda, pages 2043 to 2111, follow
page 2042 without a break. The leaves bound in are printed.

The places. A leaf's lines are read column by column (the columns split just before the right column's
first line, the running heads above the first full line left out), and an entry's first line is indented
beyond its column's margin. The lines are matched to the page's entries in the dictionary's order by the
headword's letters (accents, case and sigma's form off, the OCR's micro sign read as mu), the best monotone
matching (dynamic programming): an indented line at a similarity of 0.45 or more, any line at 0.75 or more;
where two headwords have the same letters (εἰ, εἶ, εἷ), the accents the OCR kept on the line break the tie.
The OCR reads many bold headwords in Latin letters (ἔχω as exw, παρά as mapa, ἄν as av): a line whose first
word has a Latin letter is matched with each Latin letter standing for the Greek ones it is read for (LOOK,
counted from the scan itself), at 0.75 or more; one that reads as none of the page's headwords is a Latin
word (cf., v., Pass.) and begins no entry. A line whose first word is a headword of the page exactly is
that entry's, or its homographs', and no other's. A match stands only where it
keeps to the flow of the text: an entry begins as many pixels after the one before as that one's
characters take in print (the columns' height over the characters they hold), within 200 pixels and three
tenths of the distance, and the longest chain of matches that keeps to it stands; so a line deep in an
entry's own text that begins with its headword (λόγος, pages long) is refused. Then each entry in order
takes its place after the previous entry's: a line, or a dashed word that ends its headword (an entry
printed inside another's paragraph, ἀνάβρασις as -ᾱσις), near where the text puts it, each weighed by its
similarity less a tenth for every line away from that point, the earliest within a tenth of the best; a
line not indented needs 0.85, and one that a neighbour not yet placed fits better is left to it. Between
two found entries, as many indented lines left as entries are given out one each, in order, where each
stands near its place. Any other entry is placed by its share of the text between its found neighbours.
The previous page's leaf is read too, after its last found line (an entry whose <pb> gives it to the page
after the one it begins on), and so is the next page's when that page has no <pb> (its entries are given
to the page before).
"""
import argparse, collections, difflib, importlib.util, json, os, re, sys, unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'site', 'places.json')
MAP = os.path.join(REPO, 'site', 'pages.json')
ADDENDA = (2043, 2111)   # the Addenda et Corrigenda's printed pages, after the text's last page
ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
ap.add_argument('--ocr', required=True, help="the scan's OCR, greekenglishlexi12lidd_djvu.xml")
ap.add_argument('--columns', help='also write the columns read, one a line (JSON), for a reading package')
args = ap.parse_args()
spec = importlib.util.spec_from_file_location('build', os.path.join(REPO, 'site', 'build.py'))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


def pages(path):
    """The OCR's leaves in order: {leaf, w, h, lines: [[x0, y0, x1, y1, struct, [(x0, y0, x1, y1, conf, word)]]]}."""
    out = []
    for ev, el in ET.iterparse(path, events=('end',)):
        if el.tag == 'OBJECT':
            lines = []
            for L in el.iter('LINE'):
                ws = []
                for w in L.iter('WORD'):
                    l, b, r, t = map(int, w.get('coords').split(',')[:4])
                    ws.append((l, t, r, b, int(w.get('x-confidence') or 0), w.text or ''))
                if ws:
                    lines.append([min(w[0] for w in ws), min(w[1] for w in ws), max(w[2] for w in ws),
                                  max(w[3] for w in ws), L.get('x-struct') or '', ws])
            out.append({'leaf': el.get('usemap', '').rsplit('_', 1)[-1].split('.')[0], 'w': int(el.get('width')),
                        'h': int(el.get('height')), 'lines': lines})
            el.clear()
    return out


def letters(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return ''.join(c for c in s if 'α' <= c <= 'ω' or c == 'ς').replace('ς', 'σ')


# The Latin letters the OCR reads for a bold Greek headword (ἔχω as exw, παρά as mapa, ἄν as av), each with
# the Greek letters it stands for: counted from the lines the found entries fix (between two found entries
# in a column, the indented lines whose first word has no Greek letter, one to one with the entries not
# found between them, 1,168 of them as long as their headword), a Greek letter kept where it is at least
# 8 of its Latin letter's cases and 8% of them. The case tells: A is λ, E ξ, S δ, O θ.
LOOK = {'A': 'λα', 'B': 'β', 'C': 'ζ', 'E': 'εξ', 'G': 'α', 'H': 'η', 'K': 'κ', 'L': 'ζι', 'M': 'μ', 'O': 'θο',
        'P': 'ρ', 'S': 'δ', 'T': 'τπ', 'V': 'νυ', 'W': 'ψ', 'X': 'χλ', 'a': 'α', 'c': 'σ', 'd': 'οαφδλ', 'e': 'ε',
        'h': 'λ', 'i': 'ιυ', 'k': 'κ', 'l': 'ζι', 'm': 'π', 'n': 'η', 'o': 'οσ', 'p': 'ρμ', 'r': 'τιπλ', 's': 'σ',
        't': 'ιτ', 'u': 'υι', 'v': 'νυ', 'w': 'ω', 'x': 'κχ', 'y': 'γη'}


def reading(s):
    """The letters as the OCR read them: the Greek as letters() keeps them, and the Latin, its case kept."""
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c if c.isascii() else c.lower() for c in s
                   if c.isascii() and c.isalpha() or 'α' <= c.lower() <= 'ω').replace('ς', 'σ')


def marks(s):
    """Each letter letters() keeps, with the accents, breathings, iota subscript and diaeresis on it."""
    out = []
    for c in unicodedata.normalize('NFKD', s.lower()):
        if 'α' <= c <= 'ω':
            out.append('σ' if c == 'ς' else c)
        elif out and c in '\u0300\u0301\u0308\u0313\u0314\u0342\u0345':
            out[-1] = out[-1][0] + ''.join(sorted(out[-1][1:] + c))
    return out


class Head(str):
    """A headword's letters (letters()), with its marks() beside them for the tie-break (εἰ, εἶ)."""
    def __new__(cls, head):
        h = str.__new__(cls, letters(head))
        h.marks = marks(head)
        return h


def same(c, g):
    """Whether letter c of a line can be headword letter g: the same letter, or a Latin one read for it."""
    return c == g or g in LOOK.get(c, '')


def exact(e, x):
    """Whether candidate line x's first word is headword e's letters exactly (a Latin one by LOOK)."""
    w = x['word']
    return w == e if not x['look'] else len(w) == len(e) and all(same(c, g) for c, g in zip(w, e))


def alike(e, s):
    """difflib's ratio for a reading with Latin letters, each matching the Greek it stands for (LOOK): twice
    the longest common sequence over the two lengths."""
    if len(e) < 2 or not s or not any(same(s[j], e[0]) and same(s[j + 1], e[1]) or len(e) > 2 and same(s[j], e[1])
                                 and same(s[j + 1], e[2]) for j in range(min(3, len(s) - 1))):
        return 0.0
    prev = [0] * (len(s) + 1)
    for g in e:
        cur = [0]
        for j, c in enumerate(s):
            cur.append(prev[j] + 1 if same(c, g) else max(prev[j + 1], cur[j]))
        prev = cur
    return 2 * prev[-1] / (len(e) + len(s))


def like(a, b):
    if not a or not b:
        return 0.0
    m = difflib.SequenceMatcher(None, a, b)
    return m.ratio() if m.real_quick_ratio() >= 0.5 and m.quick_ratio() >= 0.5 else 0.0


def edge(pg):
    """The top of the leaf's first full line: the running heads and the page number stand above it."""
    W = pg['w']
    return min((l[1] for l in pg['lines'] if l[2] - l[0] > 0.28 * W and len(l[5]) >= 4), default=0)


def top(pg):
    """The leaf's running heads, left and right (the Greek words above its first full line), and the
    numbers at its top centre."""
    W, H, e = pg['w'], pg['h'], edge(pg)
    ws = [w for l in pg['lines'] for w in l[5] if w[3] < e + 5 and w[1] < 0.12 * H]
    mid = lambda w: (w[0] + w[2]) / 2
    left = letters(' '.join(w[5] for w in sorted(ws) if mid(w) < 0.35 * W and len(letters(w[5])) >= 3))
    right = letters(' '.join(w[5] for w in sorted(ws) if mid(w) > 0.65 * W and len(letters(w[5])) >= 3))
    nums = {w[5].strip('.,;:’\'"“”‘·()[]') for w in ws if 0.3 * W < mid(w) < 0.7 * W}
    return left, right, nums


mine = B.dictionary(B.read_ours)
heads, size = {}, {}
for uid, xml in mine:
    try:
        el = ET.fromstring(xml)
        h = el.find('head')
        heads[uid] = ''.join(h.itertext()) if h is not None else ''
        size[uid] = len(' '.join(''.join(el.itertext()).split()))
    except ET.ParseError:
        heads[uid] = ''
        size[uid] = len(re.sub(r'<[^>]+>', '', xml))
P = pages(args.ocr)
readers = {}     # the rows a reader placed (how r): final, kept as they are
if os.path.exists(OUT):
    with open(OUT, encoding='utf-8') as f:
        readers = {u: v for u, v in json.load(f).items() if v[5] == 'r'}
by_page = collections.defaultdict(list)
for uid, xml in mine:
    if B.PRINTED.get(uid):
        by_page[B.PRINTED[uid]].append(uid)
tally = collections.Counter()


def leaves():
    """{printed page: leaf} from the running heads and page numbers, and the leaves bound in."""
    last = max(by_page)
    first = {p: [letters(heads[u]) for u in us[:10]] for p, us in by_page.items()}
    final = {p: [letters(heads[u]) for u in us[-10:]] for p, us in by_page.items()}
    found = []
    for n, pg in enumerate(P):
        lh, rh, nums = top(pg)
        sc = sorted(((max([like(lh, e) for e in first[p]] or [0]) + max([like(rh, e) for e in final[p]] or [0])
                      + (str(p) in nums), p) for p in range(max(1, n - 150), min(last, n) + 1) if p in by_page),
                    reverse=True)
        if sc and sc[0][0] >= 1.9 and (len(sc) == 1 or sc[0][0] - sc[1][0] >= 0.25):
            found.append((n, sc[0][1]))
    # the longest chain: page and leaf rising, the distance between them never shrinking
    best, back = [1] * len(found), [-1] * len(found)
    for b, (nb, pb) in enumerate(found):
        for a in range(max(0, b - 300), b):
            na, pa = found[a]
            if na < nb and pa < pb and na - pa <= nb - pb and best[a] + 1 > best[b]:
                best[b], back[b] = best[a] + 1, a
    k = max(range(len(found)), key=best.__getitem__)
    chain = []
    while k >= 0:
        chain.append(found[k])
        k = back[k]
    chain.reverse()
    tally['pages matched by their heads'] = len(chain)

    def shows(n, p):
        starts = {letters(' '.join(w[5] for w in l[5][:2]))[:5] for l in P[n]['lines']}
        return sum(letters(heads[u])[:5] in starts for u in by_page.get(p, ()) if len(letters(heads[u])) >= 5)
    m = {}
    n0, p0 = chain[0]
    for p in range(1, p0):
        m[p] = p + n0 - p0
    for (n0, p0), (n1, p1) in zip(chain, chain[1:]):
        o0, o1 = n0 - p0, n1 - p1
        gap = list(range(p0 + 1, p1))
        s = len(gap) if o0 == o1 else max(range(len(gap) + 1), key=lambda s: sum(
            shows(p + (o0 if j < s else o1), p) for j, p in enumerate(gap)))
        m[p0] = n0
        for j, p in enumerate(gap):
            m[p] = p + (o0 if j < s else o1)
    n1, p1 = chain[-1]
    for p in range(p1, ADDENDA[1] + 1):
        m[p] = p + n1 - p1
    taken = set(m.values())
    bound = [n for n in range(m[1], m[ADDENDA[1]]) if n not in taken]
    runs = []
    for n in bound:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    for a, b in runs:
        before = max(p for p in m if m[p] < a)
        text = ' '.join(w[5] for l in sorted(P[a]['lines'], key=lambda l: l[1])[:2] for w in l[5])[:60]
        print('bound in\tfiles %04d-%04d, between pages %d and %d\t%s' % (a + 1, b + 1, before, before + 1, text))
    odd = [p for p in range(ADDENDA[0], ADDENDA[1] + 1) if not re.search('ADDENDA|CORRIGENDA', ' '.join(
        w[5] for l in P[m[p]]['lines'] if l[1] < 0.12 * P[m[p]]['h'] for w in l[5]).upper())]
    if odd:
        print('Addenda pages whose leaf does not say so: %s' % odd)
    return m


leaf = leaves()
with open(MAP, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps({str(p): leaf[p] for p in sorted(leaf)}, separators=(',', ':')) + '\n')

LAYOUT = {}


def layout(n):
    """Leaf n's two columns: {lines, row, margin, right, top, foot, full}, the running heads left out; row
    gives each line the top of the printed line it belongs to (the OCR cuts some printed lines in two)."""
    if n in LAYOUT:
        return LAYOUT[n]
    pg = P[n]
    W, e = pg['w'], edge(pg)
    lines = [l for l in pg['lines'] if l[4] != 'header' and l[3] > e - 20 and l[2] - l[0] > 20]
    # the columns: split just before the right column's first start, after the widest gap between the full
    # lines' starts (the OCR cuts some printed lines in two, and the left column's second half starts far in)
    xs = sorted(l[0] for l in lines if l[2] - l[0] > 0.25 * W)
    gaps = [(b - a, b) for a, b in zip(xs, xs[1:]) if 0.1 * W < (a + b) / 2 < 0.9 * W]
    split = max(gaps)[1] - 30 if gaps and max(gaps)[0] > 0.15 * W else W / 2
    cols = []
    for c, ls in enumerate(([l for l in lines if l[0] < split], [l for l in lines if l[0] >= split])):
        ls.sort(key=lambda l: l[1])
        row, t0 = {}, None
        for l in ls:
            if t0 is None or l[1] - t0 > 15:
                t0 = l[1]
            row[id(l)] = t0
        full = sorted(l[0] for l in ls if l[2] - l[0] > 0.25 * W)
        t = min((l[1] for l in ls), default=0)
        cols.append({'lines': ls, 'row': row, 'full': bool(full), 'top': t, 'foot': max((l[3] for l in ls), default=t),
                     'margin': full[len(full) // 5] if full else (0 if c == 0 else split),
                     'right': sorted(l[2] for l in ls)[int(0.8 * len(ls))] if full else (split if c == 0 else W)})
    LAYOUT[n] = cols
    return cols


# the pixels a character takes in print (the columns' height over the characters they hold), and a line's
cols = [c for p in by_page if leaf.get(p, len(P)) < len(P) for c in layout(leaf[p])]
K = sum(c['foot'] - c['top'] for c in cols) / sum(size[u] for us in by_page.values() for u in us)
PITCH = sorted(b[1] - a[1] for c in cols for a, b in zip(c['lines'], c['lines'][1:]) if 20 < b[1] - a[1] < 80)
PITCH = PITCH[len(PITCH) // 2]


def tol(d):
    return 200 + 0.3 * K * abs(d)


def fits(e, x):
    """How well candidate x begins headword e: a line by its first letters, a dashed word by ending e."""
    if x['kind'] == 'i':
        return 0.9 if len(e) >= 4 and e.endswith(x['tail']) else 0.0
    lead = x['lead']
    if x['look']:                 # a headword read in Latin letters: the look-alikes match, and 0.75 is needed
        r = alike(e, lead[:len(e) + 2])
        return r if r >= 0.75 else 0.0
    if not e or (e[:2] not in lead[:4] and e[1:3] not in lead[:4]):
        return 0.0
    r = difflib.SequenceMatcher(None, e, lead[:len(e) + 2]).ratio()
    if not ((x['indent'] and r >= 0.45 and x['s']) or r >= 0.75):
        return 0.0
    if lead.startswith(e) and hasattr(e, 'marks'):
        # the letters the same (εἰ, εἶ, εἷ): the accents the OCR kept break the tie, at most 0.02
        r += 0.02 * sum(a == b for a, b in zip(e.marks, x['marks'])) / len(e)
    return r


out = {}
claimed = {}    # leaf -> (column, printed line) of the last place found on it
carry = None    # the previous page's last found entry: (leaf, column, printed line, x, characters from it to that page's end)
for printed, uids in sorted(by_page.items()):
    n = leaf.get(printed)
    if n is None or n >= len(P):
        tally['no page in the scan'] += len(uids)
        continue
    # the leaves read: the one before after its last found line, this one, the next when its page has no <pb>
    slots = []
    if leaf.get(printed - 1) not in (None, n) and leaf[printed - 1] in claimed:
        slots.append((0, leaf[printed - 1]))
    slots.append((1, n))
    if printed + 1 not in by_page and leaf.get(printed + 1) not in (None, n) and leaf[printed + 1] < len(P):
        slots.append((2, leaf[printed + 1]))
    segs, r0 = {}, 0      # the reading order: the columns' printed lines on one axis, r; a place is (r, x)
    for s, nn in slots:
        for c, col in enumerate(layout(nn)):
            segs[s, c] = (r0, nn, col)
            r0 += col['foot'] - col['top']
    end, start = r0, segs[1, 0][0]
    E = [Head(heads[u]) for u in uids]
    cands = []
    for (s, c), (base, nn, col) in segs.items():
        for l in col['lines']:
            row = col['row'][id(l)]
            if s == 0 and (c, row) <= claimed[nn]:
                continue
            r = base + row - col['top']
            k = next((j for j, w in enumerate(l[5]) if re.search(r'[^\W\d_]', w[5])), None)
            word = l[5][k][5] if k is not None else ''
            x = {'kind': 'l', 'key': (r, l[0]), 'r': r, 's': s, 'n': nn, 'c': c, 'row': row, 'x': l[0], 'y': l[1],
                 'h': l[3] - l[1], 'indent': col['margin'] + 22 <= l[0] <= col['margin'] + 95, 'look': False,
                 'lead': letters(' '.join(w[5] for w in l[5][:3])), 'marks': marks(' '.join(w[5] for w in l[5][:3])),
                 'word': letters(word)}
            if col['full'] and re.search('[A-Za-z]', word):
                # a word in Latin letters: a bold headword the OCR read so (exw for ἔχω) when it reads as one of
                # the page's headwords, else a Latin word (cf., v., Pass.), which begins no headword's line
                x['lead'], x['look'] = reading(word + (l[5][k + 1][5] if word.endswith('-') and k + 1 < len(l[5]) else '')), True
                x['word'] = x['lead']
                if any(fits(e, x) for e in E):
                    cands.append(x)
            elif x['lead'] and col['full'] and letters(word):
                cands.append(x)
            for w in l[5]:
                if re.match(r'^[\-—–«»"\'‘’]*[-—–]', w[5]) and len(letters(w[5])) >= 3:
                    cands.append({'kind': 'i', 'key': (r, w[0]), 'r': r, 's': s, 'n': nn, 'c': c, 'row': row,
                                  'x': w[0], 'y': w[1], 'h': w[3] - w[1], 'tail': letters(w[5])})
    cands.sort(key=lambda x: x['key'])
    S = [x for x in cands if x['kind'] == 'l']
    C = [0]
    for u in uids:
        C.append(C[-1] + size[u])
    m, k = len(E), len(S)
    # a line whose first word is a headword of the page exactly is that entry's (or its homographs') only,
    # so that alike neighbours (τριτεῖα, τριτεία, τρίτευμα) cannot each take the next one's line
    for x in S:
        x['reads'] = {i for i in range(m) if exact(E[i], x)}
    # the best monotone matching of the page's entries to its lines
    best = [[0.0] * (k + 1) for _ in range(m + 1)]
    move = [[None] * (k + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(k - 1, -1, -1):
            sc = fits(E[i], S[j]) if i in S[j]['reads'] or not S[j]['reads'] else 0
            opts = [(best[i + 1][j], 'e'), (best[i][j + 1], 's')]
            if sc:
                opts.append((best[i + 1][j + 1] + sc, 'm'))
            best[i][j], move[i][j] = max(opts)
        best[i][k], move[i][k] = best[i + 1][k], 'e'
    for j in range(k - 1, -1, -1):
        best[m][j], move[m][j] = best[m][j + 1], 's'
    i = j = 0
    first = {}
    while i < m and j < k:
        mv = move[i][j]
        if mv == 'm':
            first[i] = S[j]
            i += 1
            j += 1
        elif mv == 'e':
            i += 1
        else:
            j += 1
    # the matches that keep to the flow of the text, the previous page's last found entry among them
    nodes = []
    if carry and (0, carry[1]) in segs and segs[0, carry[1]][1] == carry[0]:
        base, nn, col = segs[0, carry[1]]
        nodes.append((-1, (base + carry[2] - col['top'], carry[3]), -carry[4], 1.0))
    nodes += [(i, x['key'], C[i], min(1.0, fits(E[i], x))) for i, x in sorted(first.items())]   # the accents' tie-break left out
    val, back = [w for *_, w in nodes], [-1] * len(nodes)
    for b, (ib, kb, cb, wb) in enumerate(nodes):
        for a in range(b):
            ia, ka, ca, wa = nodes[a]
            if ka < kb and abs(kb[0] - ka[0] - K * (cb - ca)) <= tol(cb - ca) and val[a] + wb > val[b]:
                val[b], back[b] = val[a] + wb, a
    keep = {}
    b = max(range(len(nodes)), key=val.__getitem__) if nodes else -1
    while b >= 0:
        keep[nodes[b][0]] = nodes[b]
        b = back[b]
    tally['first pass refused for its place'] += sum(1 for i in first if i not in keep)
    # each entry: the earliest acceptable place after the previous entry's, near where the text puts it
    origin = (keep[-1][1], keep[-1][2]) if -1 in keep else None
    anchors = sorted(i for i in keep if i >= 0)

    def expect(i, a, b):
        """Where entry i should stand: (r, characters to the nearer point) from points a before and b after, (place, C)."""
        if a and b and b[1] > a[1]:
            return a[0][0] + (b[0][0] - a[0][0]) * (C[i] - a[1]) / (b[1] - a[1]), min(C[i] - a[1], b[1] - C[i])
        if a:
            return a[0][0] + K * (C[i] - a[1]), C[i] - a[1]
        if b:
            return b[0][0] - K * (b[1] - C[i]), b[1] - C[i]
        return None, 0
    placed, used, prev, last, counted = {}, set(), origin, -1, set()
    for i in range(m):
        nxt = next((a for a in anchors if a > i), None)
        lo = prev[0] if prev else (-1, 0)
        hi = first[nxt]['key'] if nxt is not None else (end, 0)
        r_exp, d = expect(i, prev, (first[nxt]['key'], C[nxt]) if nxt is not None else None)
        rivals = list(range(last + 1, i)) + list(range(i + 1, min(m, i + 6, nxt if nxt is not None else m)))
        options = []
        for x in cands:
            if not lo < x['key'] < hi or id(x) in used:
                continue
            f = fits(E[i], x)
            if not f or x.get('reads') and i not in x['reads']:
                continue
            own = i in keep and x is first[i]
            if not own and x['kind'] == 'l' and not x['indent'] and f < 0.85:
                continue                     # a line not indented: only a near-certain reading of the headword
            if r_exp is not None and abs(x['r'] - r_exp) > tol(d) and not own:
                continue                     # far from where the text puts it: inside another entry, or its own
            if any(fits(E[q], x) > f for q in rivals):
                continue                     # it begins a neighbour not yet placed better
            options.append((f - 0.1 * abs(x['r'] - r_exp) / PITCH if r_exp is not None else f, x))
        # weighed by where the text puts it (a tenth a line away), the earliest within a tenth of the best
        pick = next((x for v, x in options if v >= max(options, key=lambda t: t[0])[0] - 0.1), None)
        if pick:
            placed[i] = pick
            used.add(id(pick))
            prev, last = (pick['key'], C[i]), i
            if i in keep and pick is not first[i]:
                tally['first pass moved'] += 1
    # between two found entries, as many indented lines left as entries: one each, in order, each near its place
    found = sorted(placed)
    for a, b in zip([-1] + found, found + [m]):
        gap = list(range(a + 1, b))
        if not gap:
            continue
        ta = placed[a]['key'] if a >= 0 else (start - 1, 0)
        tb = placed[b]['key'] if b < m else (end, 0)
        free = [x for x in S if x['indent'] and x['s'] and id(x) not in used and ta < x['key'] < tb]
        if len(free) != len(gap):
            continue
        pa = (placed[a]['key'], C[a]) if a >= 0 else origin
        pb = (placed[b]['key'], C[b]) if b < m else None
        near = [expect(i, pa, pb) for i in gap]
        if all(r is None or abs(x['r'] - r) <= tol(d) for x, (r, d) in zip(free, near)):
            for i, x in zip(gap, free):
                placed[i] = x
                used.add(id(x))
                counted.add(i)                   # a line by count, not by its headword: about here (second review 6)
                tally['line, by count between found ones'] += 1
    # the rest: by its share of the text between its found neighbours
    found = sorted(placed)
    order = sorted(segs.items(), key=lambda t: t[1][0])
    for i, u in enumerate(uids):
        x = placed.get(i)
        if x:
            r, how = x['r'], 'between' if i in counted else 'line' if x['kind'] == 'l' else 'inline'
        else:
            a = max((q for q in found if q < i), default=None)
            b = min((q for q in found if q > i), default=None)
            r, _ = expect(i, (placed[a]['key'], C[a]) if a is not None else origin,
                          (placed[b]['key'], C[b]) if b is not None else None)
            if r is None:
                out[u] = [int(P[n]['leaf']), 0, 0, P[n]['w'], P[n]['h'], 'p']
                tally['page'] += 1
                continue
            r, how = min(max(r, start), end - 1), 'between'
        (s, c), (base, nn, col) = ((x['s'], x['c']), segs[x['s'], x['c']]) if x else \
            [t for t in order if t[1][0] <= r and t[1][2]['lines']][-1]
        y = x['y'] if x else col['top'] + r - base
        h = x['h'] if x else 40
        # the entry's region: from its first line to the next found entry's in the column, at most the column's foot
        nxt = [placed[q]['y'] for q in found if q > i and placed[q]['n'] == nn and placed[q]['c'] == c and placed[q]['y'] > y]
        bottom = min(nxt) if nxt else col['foot']
        x0, x1 = col['margin'] - 15, col['right'] + 15
        out[u] = [int(P[nn]['leaf']), max(0, int(x0)), max(0, int(y - 12)), int(x1 - x0), int(max(h + 24, bottom - y + 12)), how[0]]
        tally[how] += 1
        if how == 'line' and x['look']:
            tally['line, its headword read in Latin letters'] += 1
        if nn != n:
            tally['on the leaf before' if s == 0 else 'on the leaf after'] += 1
    for x in placed.values():
        claimed[x['n']] = max(claimed.get(x['n'], (-1, -1)), (x['c'], x['row']))
    carry = None
    if found:
        x = placed[found[-1]]
        carry = (x['n'], x['c'], x['row'], x['x'], C[m] - C[found[-1]])
    tally['pages'] += 1
out.update(readers)
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps({u: out[u] for u in sorted(out)}, separators=(',', ':')) + '\n')
for k in sorted(tally):
    print('%s\t%d' % (k, tally[k]))
print('entries placed\t%d' % len(out))
print('in the file, by how\t%s' % ', '.join('%s %d' % kv for kv in sorted(collections.Counter(v[5] for v in out.values()).items())))
if args.columns:
    # each column read: its printed lines in order (the OCR's pieces of one printed line joined), each with
    # its box, whether it is indented as an entry's first line is, and its text as the OCR read it
    with open(args.columns, 'w', encoding='utf-8', newline='\n') as f:
        for n in sorted(LAYOUT):
            for c, col in enumerate(LAYOUT[n]):
                rows = collections.defaultdict(list)
                for l in col['lines']:
                    rows[col['row'][id(l)]].append(l)
                lines = []
                for t in sorted(rows):
                    ls = sorted(rows[t], key=lambda l: l[0])
                    lines.append([ls[0][0], min(l[1] for l in ls), max(l[2] for l in ls), max(l[3] for l in ls),
                                  col['margin'] + 22 <= ls[0][0] <= col['margin'] + 95,
                                  ' '.join(w[5] for l in ls for w in l[5])])
                f.write(json.dumps({'file': int(P[n]['leaf']), 'col': c, 'margin': col['margin'], 'lines': lines},
                                   ensure_ascii=False, separators=(',', ':')) + '\n')
