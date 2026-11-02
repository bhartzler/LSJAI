#!/usr/bin/env python3
"""Build the LSJAI site in docs/ from the dictionary and its corrections.

    python3 site/build.py

Reads dictionary/greatscott01.xml to greatscott86.xml, corrections/corrections.tsv,
glosses/lsj-glosses.tsv, readings/lsj-readings.txt, site/status.json and the
citation previews in docs/snippets/, and writes docs/, which GitHub Pages
serves as it is:

  index.html            the page (a copy of site/index.html)
  index/<letter>.json   the headword index, one file per first letter:
                        rows [norm, display, id, block], sorted by norm
  index/letters.json    the letter files and their row counts
  entries/<block>.json  the entries, 100 to a block in index order:
                        {id: {head, html, corr, marks}}, corr where the
                        entry has applied corrections, marks where its
                        text differs from Logeion's (see context())
  review.json           the entries with a correction, in index order:
                        [id, head, corrections, guessed, block]: the
                        correction rows and the guessed previews (below)
                        on the entry; the page's check walk is these and
                        every entry given a verdict
  snippets/<block>.json the citation previews, in the blocks of entries/:
                        {id: [{n, status, kind, urn, ref, source, at,
                        lines, form, found, tr, tr_at, tr_source}]}, n the
                        citation's number in the entry (cite_order());
                        cut from the corpora by tools/snippets.py, which
                        says what each key holds; the build reads them,
                        checks each against its entry and writes them again
                        in this build's blocks, with guess on the previews
                        the mechanical checks do not back (guessed())
  cited.json            the entries with previews, in index order:
                        [id, head, block], for the page's verdicts
  about.json            the counts, the latest corrections and the entry
                        shown when no headword is asked for
  stats.json            the numbers, by name; METHOD below says how each is made; tools/numbers.py prints them (docs/numbers.txt, on this machine only)
  status.html           the board a person reads (site/status.html), opened by
                        the page's β button; it shows board.txt
  board.txt             not written here: the project's board, written by its agent
                        (AGENTS/SKILLS/lsjai/scripts/state.py), shown on the status page, on this machine only
                        filled: the entries, corrections, citations,
                        previews, readings and glosses counted here, and
                        from site/status.json, kept by hand, the comparison
                        items read and left and the estimate of the
                        citations unmarked in the text
  fonts/                the free faces of the page's font switch and their
                        licences, copied from site/fonts/
  .nojekyll             so Pages serves the files untouched

Each entry's html marks where its text differs from LSJLogeion's at
BASE, the commit our corrections were carried onto: the build reads
that text with `git show`, so it needs the repository's history.
Standard library only; the same input gives byte-identical output.
"""
import collections, csv, difflib, glob, hashlib, json, os, re, subprocess, sys, unicodedata
from datetime import datetime
import xml.etree.ElementTree as ET
from html import unescape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, 'docs')
PAGE = os.path.join(REPO, 'site', 'index.html')
FONTS = os.path.join(REPO, 'site', 'fonts')
VENDOR = os.path.join(REPO, 'site', 'vendor')   # OpenSeadragon, the scan's viewer (BSD), with its licence
PLACES = os.path.join(REPO, 'site', 'places.json')   # each entry's place on its page of the scan: tools/book_places.py
TABLE = os.path.join(REPO, 'corrections', 'corrections.tsv')
HELD = os.path.join(REPO, 'corrections', 'held.tsv')
HEADS = os.path.join(REPO, 'corrections', 'heads.tsv')
SNIPPETS = os.path.join(REPO, 'docs', 'snippets')
STATUS = os.path.join(REPO, 'site', 'status.json')
READINGS = os.path.join(REPO, 'readings', 'lsj-readings.txt')
BASE = '5f4f476'         # LSJLogeion's commit under our corrections
FEATURED = 'n58840'      # κόμπος, shown when no headword is asked for
BLOCK = 100              # entries to a block file
FEED = 24                # rows in Latest corrections
APPLIED = ("replaced Logeion's", "carried onto Logeion's")  # in this copy's text

GREEK = 'αβγδεζηθικλμνξοπρστυφχψω'
NAMES = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu '
         'xi omicron pi rho sigma tau upsilon phi chi psi omega').split()
BETA = dict(zip('abgdezhqiklmncoprstufxyw', GREEK))
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
ENTRY = re.compile(r'<div2 [^>]*orig_id="([^"]+)"[^>]*>.*?</div2>', re.S)
PB = re.compile(r'<pb n="(\d+)"\s*/?>')
BIBL = re.compile(r'<bibl\b([^>]*)>')
PRINTED = {}   # entry id -> the printed page it begins on, from the files' <pb> elements


def norm(s):
    """What the search compares: NFD, combining marks out, lower case, one sigma.
    The page's norm() in site/index.html does the same."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not '\u0300' <= c <= '\u036f')
    return s.lower().replace('ς', 'σ')


def display(head, key):
    """The headword as the index lists it, with the key's homonym number
    (δύω2) where the key, less its number, spells the head."""
    m = re.search(r'\d+$', key)
    if m:
        spelled = ''.join(BETA.get(c, '') for c in key[:m.start()].lower())
        if spelled == ''.join(c for c in norm(head) if c in GREEK):
            return head + m.group()
    return head


# The renderer: TEI to the page's HTML. Elements not named here keep their
# text and lose their tag.
WRAP = {
    'head': ('<span class="hw">', '</span>'),
    'cit': ('<span class="q">', '</span>'),
    'quote': ('<span class="q">', '</span>'),
    'bibl': ('<cite>', '</cite>'),
    'title': ('<i>', '</i>'),
    'author': ('<span class="au">', '</span>'),
    'foreign': ('<span class="grc">', '</span>'),
    'orth': ('<b>', '</b>'),
    'i': ('<i>', '</i>'),
}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render(xml):
    out = []

    def walk(e):
        if e.tag == 'sense':
            out.append('<p class="sense l%s">' % (e.get('level') or '1'))
            if e.get('n'):
                out.append('<span class="sn">%s</span> ' % esc(e.get('n')))
            end = '</p>'
        elif e.tag == 'bibl' and e.get('resp'):      # a citation a pass of LSJAI marked: numbered after
            start, end = '<cite data-r="%s">' % esc(e.get('resp')).replace('"', '&quot;'), '</cite>'
            out.append(start)
        else:
            start, end = WRAP.get(e.tag, ('', ''))
            out.append(start)
        inner(e)
        out.append(end)

    def inner(e):
        if e.text:
            out.append(esc(e.text))
        for c in e:
            walk(c)
            if c.tail:
                out.append(esc(c.tail))

    inner(ET.fromstring(xml))
    return ''.join(out)


CITE = re.compile(r'<cite\b([^>]*)>')
ADDED = re.compile(r'<bibl\b[^>]*\sresp="[^"]*"[^>]*>(.*?)</bibl>', re.S)   # a citation a pass of LSJAI marked
BIBL_ALL = re.compile(r'<bibl\b([^>]*)>.*?</bibl>', re.S)                      # every citation, its attributes


def stamps(xml):
    """Each citation's fingerprint in cite_order's numbering (the dictionary's own first, then the marked,
    resp by resp): the first 8 hex digits of the SHA-1 of the element's bytes, as tools/snippets.py stamps
    each preview it cuts from it (cite)."""
    els = [(re.search(r'\sresp="([^"]*)"', m.group(1)), m.start(), m.group(0)) for m in BIBL_ALL.finditer(xml)]
    return [hashlib.sha1(el.encode('utf-8')).hexdigest()[:8] for r, pos, el in sorted(els, key=lambda t: (t[0].group(1) if t[0] else '', t[1]))]


def cite_order(h):
    """The citations of a rendering by number: [(n, index of its <cite> in the HTML)]. The
    dictionary's own bibls are 1 to N in their order, as the readings, the previews and the
    verdicts (cite|<entry>|<n>) number them; the bibls a pass of LSJAI marked (resp, tools/
    mark_citations.py) follow, N+1 onwards, pass by pass in the order of resp, each in its order,
    so that marking never moves a number. The page's citeOrder() does the same."""
    tags = [(m.group(1), k) for k, m in enumerate(CITE.finditer(h))]
    key = lambda t: (re.search(r'data-r="([^"]*)"', t[0]).group(1) if 'data-r=' in t[0] else '', t[1])
    return [(n, k) for n, (a, k) in enumerate(sorted(tags, key=key), 1)]


# The marks: where our text differs from Logeion's.

def isword(c):
    cat = unicodedata.category(c)
    return c == '.' or cat[0] in 'LM' or cat == 'Nd'


def chars(h):
    """The visible characters of a rendering, whitespace left out and
    entities decoded, each with its [start, end) in the HTML, whether the
    one before it ends where it starts (contig), and whether whitespace or
    a paragraph lies between the two (brk)."""
    text, span, contig, brk = [], [], [], []
    i, last, gap = 0, -1, False
    while i < len(h):
        c = h[i]
        if c == '<':
            j = h.index('>', i) + 1
            if h.startswith('<p', i) or h.startswith('</p', i):
                gap = True
        elif c == '&':
            j = h.index(';', i) + 1
        elif c.isspace():
            j, gap = i + 1, True
        else:
            j = i + 1
        if c == '&' or not (c == '<' or c.isspace()):
            text.append(unescape(h[i:j]) if c == '&' else c)
            span.append((i, j))
            contig.append(i == last)
            brk.append(gap)
            last, gap = j, False
        i = j
    return ''.join(text), span, contig, brk


TAG = re.compile(r'<(/?)[a-z][a-z0-9]*[^>]*>')


def balance(h, s, e):
    """[s, e) widened over the tags at its edges until the tags inside pair
    up, or (None, None)."""
    while True:
        open_, lost = 0, 0
        for m in TAG.finditer(h, s, e):
            if not m.group(1):
                open_ += 1
            elif open_:
                open_ -= 1
            else:
                lost += 1
        if not open_ and not lost:
            return s, e
        moved = False
        if lost and s and h[s - 1] == '>' and h[h.rindex('<', 0, s) + 1] != '/':
            s, moved = h.rindex('<', 0, s), True
        if open_ and h.startswith('</', e):
            e, moved = h.index('>', e) + 1, True
        if not moved:
            return None, None


def mark(ours, base, tally):
    """Our rendering with <mark> on each changed word and <span class="chg">
    on the changed characters. A word runs over letters, combining marks,
    digits and the dot, across tags but not across whitespace or a
    paragraph. A word that crosses a tag gets one <mark> when widening it
    over the tags at its edges pairs its tags up (<mark><cite>21.9</cite>1
    </mark>), else one for each piece contiguous in the HTML, classed jl
    and jr where they join so the page draws them as one; either way the
    markup stays well formed."""
    to, span, contig, brk = chars(ours)
    tb = chars(base)[0]
    if to == tb:
        return ours
    tally['entries'] += 1
    n = len(to)

    def grow(a, b):
        while a > 0 and not brk[a] and isword(to[a - 1]):
            a -= 1
        while b < n and not brk[b] and isword(to[b]):
            b += 1
        return a, b

    words = []                                    # [a, b, red positions]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, tb, to, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        tally[op] += 1
        if j1 < j2:
            a, b = grow(j1, j2)
            words.append([a, b, set(range(j1, j2))])
        elif n:                                   # a deletion: yellow, no red
            a = j1 - 1 if j1 > 0 else 0
            b = j1 + 1 if 0 < j1 < n and not brk[j1] else a + 1
            a, b = grow(a, b)
            words.append([a, b, set()])
        else:
            tally['unmapped'] += 1
    words.sort(key=lambda w: (w[0], w[1]))
    merged = []
    for w in words:
        if merged and w[0] < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], w[1])
            merged[-1][2] |= w[2]
        else:
            merged.append(w)
    tally['marks'] += len(merged)

    def wrap(k, m, red):                          # chars k..m-1 as one <mark>, or None
        lo, hi = balance(ours, span[k][0], span[m - 1][1])
        if lo is None:
            return None
        body, at = [], lo
        r = k
        while r < m:
            if r in red:
                s = r + 1
                while s < m and s in red and contig[s]:
                    s += 1
                body.append(ours[at:span[r][0]])
                body.append('<span class="chg">%s</span>' % ours[span[r][0]:span[s - 1][1]])
                at, r = span[s - 1][1], s
            else:
                r += 1
        body.append(ours[at:hi])
        return lo, hi, '<mark>%s</mark>' % ''.join(body)

    pieces = []                                   # (start, end, html of the piece)
    for a, b, red in merged:
        k = a
        while k < b:                              # the parts between whitespace
            m = k + 1
            while m < b and not brk[m]:
                m += 1
            one = wrap(k, m, red)
            if one:
                pieces.append(one)
            else:
                tally['split'] += 1
                parts, j = [], k
                while j < m:                      # the parts between tags
                    t = j + 1
                    while t < m and contig[t]:
                        t += 1
                    parts.append(wrap(j, t, red))
                    j = t
                for x, (lo, hi, piece) in enumerate(parts):   # jl, jr: joined left, right
                    joins = ' '.join(c for c, on in (('jl', x > 0), ('jr', x < len(parts) - 1)) if on)
                    pieces.append((lo, hi, '<mark class="%s">' % joins + piece[len('<mark>'):]))
            k = m
    for (s, e, piece), after in zip(reversed(pieces), [None] + pieces[::-1]):
        assert after is None or e <= after[0], 'marks overlap'
        ours = ours[:s] + piece + ours[e:]
    tally['pieces'] += len(pieces)
    return ours


def plain(h):
    """A rendering's text: tags out (a paragraph as a space), entities
    decoded, whitespace collapsed to single spaces."""
    return ' '.join(unescape(re.sub(r'<[^>]*>', '', re.sub(r'</?p\b[^>]*>', ' ', h))).split())


def context(ours, base):
    """Each change as {k, b, t, a, o, ob, oa}: the 22 characters before, our text,
    the 22 after, Logeion's text, and the 22 before and after it in Logeion's own
    text; the page's correction box shows the old line and the new."""
    to, tb = plain(ours), plain(base)
    kind = {'replace': 'rep', 'insert': 'ins', 'delete': 'del'}
    return [{'k': kind[op], 'b': to[max(0, j1 - 22):j1], 't': to[j1:j2], 'a': to[j2:j2 + 22], 'o': tb[i1:i2],
             'ob': tb[max(0, i1 - 22):i1], 'oa': tb[i2:i2 + 22]}
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, tb, to, autojunk=False).get_opcodes()
            if op != 'equal']


def dictionary(load):
    """[(id, xml)] for the 86 files in order, ids made unique across files."""
    out, seen, page = [], {}, 0
    for n in range(1, 87):
        text = load('greatscott%02d.xml' % n)
        events = [(m.start(), 0, int(m.group(1))) for m in PB.finditer(text)] + [(m.start(), 1, m) for m in ENTRY.finditer(text)]
        events.sort(key=lambda t: (t[0], t[1]))
        for pos, kind, val in events:
            if kind == 0:
                page = val
                continue
            m = val
            oid = m.group(1)
            seen[oid] = seen.get(oid, 0) + 1
            uid = oid if seen[oid] == 1 else '%s-%d' % (oid, seen[oid])
            out.append((uid, m.group(0)))
            PRINTED[uid] = page
        tags = len(re.findall(r'<div2\b', text))
        bare = len(re.findall(r'<div2\b(?![^>]*orig_id=)[^>]*>', text))
        if tags != bare + sum(1 for _ in ENTRY.finditer(text)):
            sys.exit('greatscott%02d.xml: an entry the build cannot delimit' % n)
    return out


def read_ours(name):   # the dictionary's files live in dictionary/ since 2 Nov 2026; Logeion's base copy keeps them at the root (read_logeion)
    with open(os.path.join(REPO, 'dictionary', name), encoding='utf-8') as f:
        return f.read()


def read_logeion(name):
    r = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (BASE, name)],
                       capture_output=True, encoding='utf-8')
    if r.returncode:
        sys.exit('git show %s:%s failed (the build needs the history): %s' % (BASE, name, r.stderr.strip()))
    return r.stdout


def when(applied):
    """'26 Oct 2026, the night of 25 Oct' -> ('26 Oct 2026', (2026, 10, 26))."""
    day = applied.split(',')[0].strip()
    d, m, y = day.split()
    return day, (int(y), MONTHS.index(m) + 1, int(d))


def corrections(ids):
    with open(TABLE, encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    head, rows = rows[0], rows[1:]
    out, tally = [], collections.Counter()
    for k, r in enumerate(rows):
        if len(r) != len(head):
            sys.exit('corrections.tsv row %d: %d fields, not %d' % (k + 2, len(r), len(head)))
        r = dict(zip(head, r))
        tally['in: ' + r['in LSJAI']] += 1
        tally['verdict: ' + r['verdict']] += 1
        tally['sure: ' + r['how sure']] += 1
        if r['in LSJAI'] not in APPLIED:
            continue
        if r['entry'] not in ids:
            sys.exit('corrections.tsv row %d: no entry %s' % (k + 2, r['entry']))
        day, date = when(r['applied'])
        out.append((date, k, r['entry'], {
            'old': r['old'], 'new': r['new'], 'when': day, 'why': r['why'],
            'src': r['evidence source'], 'quote': r['evidence quote'],
            'sure': r['how sure'], 'in': r['in LSJAI'], 'row': k + 2}))   # row: its line in corrections.tsv, the verdict's identity
    return out, len(rows), tally


def table(path):
    """The rows of a TSV with a header, its comment lines (#) left out, as dicts."""
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t', quoting=csv.QUOTE_NONE))


TREES = ('perseus', 'first1k', 'greek', 'latin', 'loeb', 'digiliblt', 'papyri', 'inscriptions', 'english', 'translations')     # docs/snippets/<tree>/, tools/snippets.py's
TRANSLATIONS = ('english', 'translations')                      # the trees of translations (english: the open ones; translations: the Loeb's, ToposText's, in .gitignore)
TEXTS = tuple(t for t in TREES if t not in TRANSLATIONS)        # the trees of texts
SHELF = ('perseus', 'first1k', 'loeb', 'digiliblt')             # the trees cut from the catalogue's TEI shelves (perseus_places), each edition checked for the word
CLOSED = ('greek', 'latin', 'papyri', 'inscriptions', 'loeb', 'digiliblt')   # the collections whose per-collection counts go to site/stats-private.json


def snippets(ids):
    """The citation previews of each tree by entry, {tree: {id: [preview]}}, as tools/snippets.py cut
    them into docs/snippets/<tree>/ (in whatever blocks), and the ids they name that are no entry here."""
    out, gone = {t: {} for t in TREES}, []
    for t in TREES:
        for path in sorted(glob.glob(os.path.join(SNIPPETS, t, '*.json'))):
            with open(path, encoding='utf-8') as f:
                for i, v in json.load(f).items():
                    if i in ids:
                        out[t][i] = sorted(v, key=lambda x: x['n'])
                    else:
                        gone.append(i)
    return out, gone


def better(x, o):
    """Whether preview x is shown before o, as the page's snippets() decides: a preview marked prefer
    first, then one the checks back (no guess) before a guess, then the earlier source and edition."""
    return (bool(x.get('prefer')), not x.get('guess')) > (bool(o.get('prefer')), not o.get('guess'))


def collated_counts():
    """The collated tree's counts (tools/collate.py): citations, those with an apparatus entry, witnesses not aligned."""
    c = {'citations': 0, 'with_text': 0, 'by_link': 0, 'variants': 0, 'unaligned': 0}
    wit, miss = collections.Counter(), collections.Counter()   # per collection: witnesses, witnesses not aligned to a line (the score of its links)
    linked = by_link()
    for path in sorted(glob.glob(os.path.join(DOCS, 'snippets', 'text', '*.json'))):
        with open(path, encoding='utf-8') as f:
            for recs in json.load(f).values():
                for r in recs:
                    c['citations'] += 1
                    if any(r.get('lines') or []):
                        c['with_text'] += 1
                        if r.get('src') in linked:   # the guard: a record of these editions carries no lines
                            raise SystemExit('docs/snippets/text carries lines of an edition given by link (%s, %s); nothing more built' % (r.get('src'), r.get('ref')))
                    else:
                        c['by_link'] += 1
                    if any(r.get('app') or []):
                        c['variants'] += 1
                    for w in r.get('ws') or []:
                        wit[w.get('src')] += 1
                        if w.get('miss'):
                            miss[w.get('src')] += 1; c['unaligned'] += 1
    for t_ in TEXTS:
        c['align_' + t_] = round(100 * (wit[t_] - miss[t_]) / wit[t_]) if wit[t_] else 0
    return c


def collate_order():
    """SOURCES as tools/collate.py defines it, read from the tool's own file."""
    with open(os.path.join(REPO, 'tools', 'collate.py'), encoding='utf-8') as f:
        return json.loads(re.search(r"^SOURCES = (\[[^\]]*\])", f.read(), re.M).group(1).replace("'", '"'))


def by_link():
    """BY_LINK as tools/collate.py defines it: the editions a record gives by its link."""
    with open(os.path.join(REPO, 'tools', 'collate.py'), encoding='utf-8') as f:
        return tuple(json.loads(re.search(r"^BY_LINK = \(([^)]*)\)", f.read(), re.M).group(1).replace("'", '"').rstrip(', ').join('[]')))


def chosen(trees):
    """The preview the page shows of each citation, {id: {n: preview}}: of every text that holds it,
    by better(), ties to the first source in the order tools/collate.py keeps (the page's order of 1 Nov
    2026, the one place since 2 Nov: the collation chooses the same edition) and the first (newest)
    edition of a source."""
    order = collate_order()
    out = {}
    for t in order:
        for i, v in trees[t].items():
            for x in v:
                o = out.setdefault(i, {}).get(x['n'])
                if o is None or better(x, o[1]):
                    out[i][x['n']] = (t, x)
    return out


def read_citations():
    """The citations with a reading and the reading's verdict, {(entry id, number): kind}: of a
    citation read more than once, the latest row of readings/lsj-readings.txt by its when."""
    out = {}
    with open(READINGS, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^entry:perseus\.1999\.04\.0057/([^/\t]+)/(\d+)\t([^\t]*)\t[^\t]*\t[^\t]*\t([^\t]*)\t', line)
            if m:
                key, at = (m.group(1), int(m.group(2))), datetime.strptime(m.group(4), '%d %b %Y %H:%M:%S %z')
                if key not in out or at >= out[key][0]:
                    out[key] = (at, m.group(3))
    return {k: v[1] for k, v in out.items()}


def guessed(p, contradicted=False):
    """Why a preview is a guess, or None: a reader read the citation and could not place it, or the
    reading was rejected (reading); or no reader has read it and either the headword's
    form was not found on the cited line (word), or the line's place is not the citation's own
    (place: Ph. 1.58 shown at 1.1, an edition numbered another way; a repaired reading differs by
    design and is read). A reading backs the line read; an open edition's line without the form that
    another edition's line has (contradicted) is another line, and the check decides (second review 2).
    The page prints the reason and the review walk visits the entry."""
    if p.get('status') == 'read':
        if p.get('kind') in ('unresolved', 'rejected'):
            return 'reading'   # a reader who could not place it backs nothing (Codex, 1 Nov 2026)
        if not (contradicted and 'found' in p and not p['found']):
            return None
    if not p.get('found'):
        return 'word'
    return None if placed(p) else 'place'


def placed(p):
    """Whether a preview's cited line stands at the place cited: its citation (at) begins with the ref's last
    word or that ends with it, digits and letters compared as parts; or, part by part, the line's citation begins with
    the place the urn names (the place in the held text's numbering: Aët. 9.28 is chapter 28 of the TLG's ninth
    book, at 28.145), a part of the line's citation that is a name and no number left out (Pindar's fragment 163
    at Incert.163.1), and a place whose last part is a page with a letter is that page, the line after it
    (Procl. in Ti. 1.3d, Diehl's page, at 1.3.32); a papyrus (urn:cts:ddp) or an inscription (urn:cts:ins) whose
    urn names its line or its document as the store cites it (59270 rp.r.5, a side with no number; 956.col. I.58)."""
    at = p['at'][1] or ''
    loc = re.findall(r'\d+|[a-z]+', p['ref'].rsplit(' ', 1)[-1].lower())   # parts: 1.2 is not 1.20, 12.3 not 2.3 (second review 7)
    flat = re.findall(r'\d+|[a-z]+', at.lower())
    if loc and flat and (loc[-len(flat):] == flat or flat[:len(loc)] == loc):
        return True
    place = p['urn'].split(':', 4)[4].split('.') if p['urn'].count(':') >= 4 else []
    if (':ddp:' in p['urn'] or ':ins:' in p['urn']) and place and at.split('.')[:len(place)] == place:
        return True                   # a papyrus or an inscription: its urn names the line, or the document, as the store cites it
    parts = [x for x in at.split('.') if re.search(r'\d', x)]
    if not place or not parts:
        return False
    if parts[:len(place)] == place:
        return True
    m = re.fullmatch(r'(\d+)[a-g]', place[-1])
    return bool(m) and parts[:-1] == place[:-1] + [m.group(1)]


METHOD = {   # how each value of stats.json is made; the build stops if a value has no line here
    'entries': 'div2 entries in dictionary/greatscott01-86.xml, homonym ids made unique',
    'corrections': "rows of corrections/corrections.tsv whose 'in LSJAI' is replaced or carried onto Logeion's",
    'corrected_entries': 'entries with at least one such row',
    'rows': 'all rows of corrections/corrections.tsv',
    'already': "rows whose 'in LSJAI' is already Logeion's",
    'kept': "rows whose 'in LSJAI' is Logeion's kept (a later Logeion edit at the same place)",
    'held': 'rows of corrections/held.tsv: established, not written in',
    'verdict_b': "rows whose verdict is B (copy B has the print)",
    'verdict_neither': "rows whose verdict is both-wrong (the print read, neither copy)",
    'sure5': "rows with 'how sure' 5", 'sure4': "rows with 'how sure' 4",
    'heads_followed': "rows of corrections/heads.tsv with status 'head followed'",
    'changed': 'entries whose XML differs from Logeion at BASE (5f4f476)',
    'items': "site/status.json: comparison items read plus left (kept by hand from the re-cut's COUNTS.json)",
    'items_read': 'site/status.json, by hand', 'items_left': 'site/status.json, by hand',
    'citations': '<cite> elements rendered from the <bibl>s, one to one (the build stops otherwise)',
    'c_tlg': "bibls whose n is Perseus:abo:tlg,…", 'c_pap': "bibls whose n is Perseus:abo:pap,…", 'c_phi': "bibls whose n is Perseus:abo:phi,…",
    'c_none': 'bibls with no n', 'c_other': 'bibls with an n of another form (stoa, malformed)',
    'unmarked': "site/status.json, by hand: the census estimate of citations in the text outside any bibl (AGENTS/SCRATCH/20261031-lsj-citation-census/estimate.json)",
    'all_citations': 'citations plus unmarked: the denominator of the citation funnel',
    'previews': 'citations with a preview the page shows: of every tree under docs/snippets/, the one better() chooses',
    'pv_perseus': 'shown previews from docs/snippets/perseus', 'pv_first1k': 'shown previews from docs/snippets/first1k',
    'pv_greek': 'shown previews from docs/snippets/greek', 'pv_latin': 'shown previews from docs/snippets/latin',
    'pv_papyri': 'shown previews from docs/snippets/papyri',
    'pv_inscriptions': 'shown previews from docs/snippets/inscriptions',
    'pv_loeb': 'shown previews from docs/snippets/loeb',
    'pv_digiliblt': 'shown previews from docs/snippets/digiliblt',
    'two_texts': 'citations with a preview in two or more editions, all text trees',
    'collated': 'citations in docs/snippets/text (tools/collate.py: this text with its witnesses and apparatus, one record a citation)',
    'with_text': 'citations in docs/snippets/text whose record carries lines',
    'by_link': 'citations in docs/snippets/text whose record carries no lines: the edition is given by its link (tools/collate.py BY_LINK)',
    'variants': 'citations whose witnesses differ from this text in a word (an apparatus entry), docs/snippets/text',
    'unaligned': 'witnesses whose text could not be aligned to a line of this text (fewer than half the words shared), docs/snippets/text',
    'held_translations': 'passages held in the translation trees (docs/snippets/english and translations), every translation',
    'agree': 'citations whose headword the lemma check finds at the place in two or more collections',
    'contradict': 'citations one collection finds the headword for and another, with a preview, does not',
    'linked': 'shown previews with a url to the text online',
    'translated': 'citations with at least one row in docs/snippets/english',
    'translations': 'rows of docs/snippets/english (every translation that places a citation)',
    'tr_two': 'citations with two or more English rows', 'tr_linked': 'citations whose first English row has a url',
    'found': "shown previews whose 'found' is set: a form of the entry's lemmas on the cited line (snippets.py's lemma check: the Philology forms table, the heads, morph)",
    'notfound': "shown previews with 'found' present and empty", 'untestable': "shown previews with no 'found' key (the lexicon has no lemma for the entry)",
    'guessed': 'shown previews whose line nothing backs: unread and the checks fail, or read and unplaced, or an open edition read elsewhere whose line lacks the form (guessed() in build.py)',
    'guessed_word': "guessed: the headword's form not on the line", 'guessed_reading': 'guessed: a reader read it and could not place it (unresolved) or the reading was rejected; the lines are where the reference points', 'guessed_place': "guessed: the line's place not the citation's own (another numbering)",
    'backed': 'previews minus guessed: the cited line backed by a check or a reading',
    'read': 'citations with a reading in readings/lsj-readings.txt (the latest by its when), counted on the cites',
    'k_verified': "reading kind verified", 'k_repaired': "reading kind repaired", 'k_scholion': "reading kind scholion",
    'k_relocated': "reading kind relocated", 'k_unresolved': "reading kind unresolved", 'k_rejected': "reading kind rejected",
    'glosses': 'rows of glosses/lsj-glosses.tsv with a gloss, for entries that exist',
    'pages': "distinct printed pages the entries begin on (the files' <pb>)",
    'placed_line': "entries in site/places.json with how l or i (found by the OCR: tools/book_places.py) or r (placed by a reader)",
    'placed_near': 'entries with how b (placed between found neighbours)',
}
for _t in TEXTS:   # the collections table and the board, one line a tree
    METHOD['held_' + _t] = 'previews held in docs/snippets/%s, every edition (shown or not)' % _t
    METHOD['rate_' + _t] = "the lemma check's rate in docs/snippets/%s: previews with a form of the headword on the cited line, of those it could test (Latin lines are untestable: morph reads Greek)" % _t
    METHOD['line_' + _t] = 'citations with a preview of the cited line in docs/snippets/%s (linked at the line)' % _t
    METHOD['word_' + _t] = 'citations with a form of the headword found on the cited line in docs/snippets/%s (linked at the word)' % _t
    METHOD['align_' + _t] = 'of the citations where docs/snippets/%s is a witness, the percent whose lines align to this text (tools/collate.py; the score of the collection\'s links)' % _t




def write(path, text, made):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    made.add(path)


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n'


def ordered(mine):
    """The entries in index order, [(norm, order, display, id)]: an entry's block is its position
    // BLOCK (tools/snippets.py cuts the previews into the same blocks)."""
    out = []
    for order, (i, xml) in enumerate(mine):
        el = ET.fromstring(xml)
        shown = display(''.join(el.find('head').itertext()).strip(), el.get('key'))
        if not shown:
            sys.exit('entry %s has no headword' % i)
        out.append((norm(shown), order, shown, i))
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def main():
    mine = dictionary(read_ours)
    base = dict(dictionary(read_logeion))
    ids = {i for i, _ in mine}
    if FEATURED not in ids:
        sys.exit('the featured entry %s is not in the dictionary' % FEATURED)
    corr, rows_in_table, corr_tally = corrections(ids)
    glosses = {}
    with open(os.path.join(REPO, 'glosses', 'lsj-glosses.tsv'), encoding='utf-8') as fh:
        gh = fh.readline().rstrip('\n').split('\t')
        for line in fh:
            if not line.strip() or line.startswith('#'):
                continue
            r = dict(zip(gh, line.rstrip('\n').split('\t')))
            if r.get('gloss'):
                glosses[r['id']] = r['gloss']
    snip, unknown = snippets(ids)
    with open(PLACES, encoding='utf-8') as f:
        places = json.load(f)
    with open(os.path.join(REPO, 'site', 'pages.json'), encoding='utf-8') as f:
        leaf_page = {v: int(k) for k, v in json.load(f).items()}   # the Archive's leaf n -> printed page
    with open(STATUS, encoding='utf-8') as f:
        status = json.load(f)
    bibls = cited_read = 0
    readings = read_citations()
    coll, kinds = collections.Counter(), collections.Counter()
    by = {}
    for date, k, i, c in corr:
        by.setdefault(i, []).append(c)

    tally = dict(entries=0, marks=0, pieces=0, split=0, replace=0, insert=0, delete=0,
                 unmapped=0, nobase=0, changed=0, marked=0, context=0, cites=0)
    rows = []                                     # (norm, order, display, id, html, marks)
    for nm, order, shown, i in ordered(mine):
        xml = mine[order][1]
        el = ET.fromstring(xml)
        h, ctx = render(xml), []
        if i not in base:
            tally['nobase'] += 1
        elif base[i] != xml and ADDED.sub(r'\1', xml) == base[i]:
            tally['marked'] += 1                  # only citations marked by rule (tools/mark_citations.py): no change
        elif base[i] != xml:
            tally['changed'] += 1
            b = render(base[i])
            ctx = context(h, b)
            h = mark(h, b, tally)
        tally['context'] += len(ctx)
        cites = len(cite_order(h))
        bibls += cites
        for k in range(1, cites + 1):
            if (i, k) in readings:
                cited_read += 1
                kinds[readings[(i, k)]] += 1
        for m in BIBL.finditer(xml):
            n_ = re.search(r'\bn="([^"]*)"', m.group(1))
            k_ = re.match(r'Perseus:abo:([a-z]+),', n_.group(1)) if n_ else None
            coll['none' if not n_ else k_.group(1) if k_ else 'other'] += 1
        if cites != sum(1 for _ in el.iter('bibl')):
            tally['cites'] += 1               # the page finds a citation by its <cite>'s order
            if any(i in snip[t] for t in TREES):
                sys.exit('entry %s: its <cite>s are not its bibls, one to one' % i)
        own = stamps(xml)                         # each citation's fingerprint, by number (second review 4)
        for t in TREES:
            if i in snip[t] and snip[t][i][-1]['n'] > cites:
                sys.exit('entry %s: a preview of citation %d, of %d (%s)' % (i, snip[t][i][-1]['n'], cites, t))
            for x in snip[t].get(i, ()) if t in TEXTS else ():   # each preview's reading is the one in force (second review 4)
                if (x.get('kind') if x.get('status') == 'read' else None) != readings.get((i, x['n'])):
                    sys.exit('entry %s: the preview of citation %d (%s) was cut before its reading in force; re-cut' % (i, x['n'], t))
                if x.get('cite') and (x['n'] > len(own) or x['cite'] != own[x['n'] - 1]):
                    sys.exit('entry %s: the preview of citation %d (%s) was cut from another citation; re-cut' % (i, x['n'], t))
        rows.append((nm, order, shown, i, h, ctx))

    made = set()
    blocks = {}
    index = {name: [] for name in NAMES + ['other']}
    where = {}
    for pos, (nm, order, shown, i, h, ctx) in enumerate(rows):
        b = pos // BLOCK
        where[i] = (shown, b)
        e = {'head': shown, 'html': h}
        if i in places:
            e['box'] = places[i]
        if i in places and places[i][0] - 1 in leaf_page:      # the page the entry's place is on
            e['page'] = leaf_page[places[i][0] - 1]
        elif PRINTED.get(i):
            e['page'] = PRINTED[i]
        if i in glosses:
            e['gloss'] = glosses[i]
        if i in by:
            e['corr'] = by[i]
        if ctx:
            e['marks'] = ctx
        blocks.setdefault(b, {})[i] = e
        letter = nm[:1]
        index[NAMES[GREEK.index(letter)] if letter and letter in GREEK else 'other'].append([nm, shown, i, b])
    for b, block in blocks.items():
        write(os.path.join(DOCS, 'entries', '%04d.json' % b), dump(block), made)
    letters = []
    for name in NAMES + ['other']:
        write(os.path.join(DOCS, 'index', name + '.json'), dump(index[name]), made)
        row = {'letter': GREEK[NAMES.index(name)]} if name in NAMES else {}
        row.update(file=name + '.json', rows=len(index[name]))
        letters.append(row)
    write(os.path.join(DOCS, 'index', 'letters.json'), dump(letters), made)
    guesses = collections.Counter()
    formed = {(i, x['n']) for t in TEXTS for i, v in snip[t].items() for x in v if x.get('found')}   # citations an edition's own check backs
    for t in TREES:
        pv = {b: {} for b in blocks}
        for nm, order, shown, i, h, ctx in rows:
            if i in snip[t]:
                if t in TEXTS:
                    for x in snip[t][i]:
                        x.pop('guess', None)
                        g = guessed(x, t in SHELF and (i, x['n']) in formed)
                        if g:
                            x['guess'] = g
                pv[where[i][1]][i] = snip[t][i]
        for b, block in pv.items():
            write(os.path.join(DOCS, 'snippets', t, '%04d.json' % b), dump(block), made)
    shown_ = chosen(snip)
    collated = collated_counts()
    for v in shown_.values():
        for t, x in v.values():
            guesses[x.get('guess', 'none')] += 1
    review = [[i, shown, len(by.get(i, [])), sum(1 for t, x in shown_.get(i, {}).values() if x.get('guess')), where[i][1]]
              for nm, order, shown, i, h, ctx in rows]
    review = [r for r in review if r[2]]          # the check walk: entries with a correction (Bruce, 31 Oct 2026)
    write(os.path.join(DOCS, 'review.json'), dump(review), made)
    translated = len({(i, x['n']) for t in TRANSLATIONS for i, v in snip[t].items() for x in v})
    cited = [[i, shown, where[i][1]] for nm, order, shown, i, h, ctx in rows if i in shown_]
    write(os.path.join(DOCS, 'cited.json'), dump(cited), made)

    latest = sorted(corr, key=lambda c: (c[0], c[1]), reverse=True)[:FEED]
    feed = [{'id': i, 'head': where[i][0], 'old': c['old'], 'new': c['new'],
             'why': c['why'], 'src': c['src'], 'when': c['when']} for date, k, i, c in latest]
    first = min(corr, key=lambda c: (c[0], c[1]))
    about = {'entries': len(rows), 'corrections': len(corr), 'since': first[3]['when'],
             'featured': {'id': FEATURED, 'head': where[FEATURED][0]}, 'feed': feed}
    write(os.path.join(DOCS, 'about.json'), dump(about), made)

    shelf, check, held = collections.Counter(), collections.Counter(), collections.Counter()
    for v in shown_.values():
        for t, x in v.values():
            shelf[t] += 1
            check['found' if x.get('found') else 'notfound' if 'found' in x else 'untestable'] += 1
            held['linked'] += bool(x.get('url'))
    texts = collections.Counter()
    for t in TREES:
        for i, v in snip[t].items():
            for x in v:
                texts[(t, i, x['n'])] += 1
    per, trs, by_tree = collections.Counter(), collections.Counter(), collections.Counter()
    for (t, i, n), k in texts.items():          # a citation's texts (every edition) and its translations
        by_tree[t] += 1
        (trs if t in TRANSLATIONS else per)[(i, n)] += k
    tr_first = {}
    for t in TRANSLATIONS:
        for i, v in snip[t].items():
            for x in v:
                tr_first.setdefault((i, x['n']), x)
    # the collections against each other (Bruce, 1 Nov 2026): a citation whose headword two or more
    # collections find at the place agrees; one that one collection finds and another does not contradicts
    hit, miss = collections.defaultdict(set), collections.defaultdict(set)
    for t in TEXTS:
        for i, v in snip[t].items():
            for x in v:
                if 'found' in x:
                    (hit if x['found'] else miss)[(i, x['n'])].add(t)
    rates, at_line, at_word = {}, {}, {}
    for t in TEXTS:                                   # the collections table and the board: per tree, the citations linked at the
        f = nf = 0                                    # line (a preview of the cited line) and at the word (the headword found on it),
        line_, word_ = set(), set()                   # and the lemma check's rate over the previews it could test
        for i, v in snip[t].items():
            for x in v:
                line_.add((i, x['n']))
                if 'found' in x:
                    f += bool(x['found']); nf += not x['found']
                    if x['found']:
                        word_.add((i, x['n']))
        rates[t] = (sum(len(v) for v in snip[t].values()), ('%d%%' % round(100.0 * f / (f + nf))) if f + nf else 'untestable')
        at_line[t], at_word[t] = len(line_), len(word_)
    agree = sum(1 for k, ts in hit.items() if len(ts) >= 2)
    contradict = sum(1 for k, ts in miss.items() if k in hit and (ts - hit[k]))
    values = {
        'entries': len(rows), 'corrections': len(corr), 'corrected_entries': len(by),
        'citations': bibls, 'previews': sum(len(v) for v in shown_.values()), 'translated': translated,
        'read': cited_read, 'glosses': sum(1 for i in glosses if i in ids),
        'items': status['comparison items read'] + status['comparison items left'],
        'items_read': status['comparison items read'], 'items_left': status['comparison items left'],
        'rows': rows_in_table, 'already': corr_tally["in: already Logeion's"], 'kept': corr_tally["in: Logeion's kept"],
        'held': len(table(HELD)), 'verdict_b': corr_tally['verdict: B'], 'verdict_neither': corr_tally['verdict: both-wrong'],
        'sure5': corr_tally['sure: 5'], 'sure4': corr_tally['sure: 4'],
        'heads_followed': sum(1 for r in table(HEADS) if r['status'] == 'head followed'),
        'changed': tally['changed'],
        'c_tlg': coll['tlg'], 'c_pap': coll['pap'], 'c_phi': coll['phi'], 'c_none': coll['none'],
        'c_other': bibls - coll['tlg'] - coll['pap'] - coll['phi'] - coll['none'],
        'unmarked': status['citations unmarked'],
        'pv_perseus': shelf['perseus'], 'pv_first1k': shelf['first1k'], 'pv_greek': shelf['greek'], 'pv_latin': shelf['latin'],
        'pv_papyri': shelf['papyri'], 'pv_inscriptions': shelf['inscriptions'], 'pv_loeb': shelf['loeb'], 'pv_digiliblt': shelf['digiliblt'],
        'agree': agree, 'contradict': contradict, 'two_texts': sum(1 for k in per.values() if k > 1),
        'collated': collated['citations'], 'with_text': collated['with_text'], 'by_link': collated['by_link'], 'variants': collated['variants'], 'unaligned': collated['unaligned'],
        **{'align_' + t_: collated['align_' + t_] for t_ in TEXTS},
        **{'held_' + t: rates[t][0] for t in TEXTS}, **{'rate_' + t: rates[t][1] for t in TEXTS},
        **{'line_' + t: at_line[t] for t in TEXTS}, **{'word_' + t: at_word[t] for t in TEXTS},
        'held_translations': sum(len(v) for t in TRANSLATIONS for v in snip[t].values()),
        'all_citations': bibls + status['citations unmarked'], 'backed': sum(len(v) for v in shown_.values()) - guesses['word'] - guesses['place'] - guesses['reading'],
        'translations': sum(len(v) for t in TRANSLATIONS for v in snip[t].values()), 'tr_two': sum(1 for k in trs.values() if k > 1),
        'linked': held['linked'], 'tr_linked': sum(1 for x in tr_first.values() if x.get('url')),
        'found': check['found'], 'notfound': check['notfound'], 'untestable': check['untestable'],
        'k_verified': kinds['verified'], 'k_repaired': kinds['repaired'], 'k_scholion': kinds['scholion'],
        'k_relocated': kinds['relocated'], 'k_unresolved': kinds['unresolved'], 'k_rejected': kinds['rejected'],
        'pages': len({p for p in PRINTED.values() if p}),
        'guessed': guesses['word'] + guesses['place'] + guesses['reading'], 'guessed_word': guesses['word'], 'guessed_place': guesses['place'], 'guessed_reading': guesses['reading'],
        'placed_line': sum(1 for i in ids if places.get(i, [''] * 6)[5] in ('l', 'i', 'r')),
        'placed_near': sum(1 for i in ids if places.get(i, [''] * 6)[5] == 'b'),
    }
    if sum(kinds.values()) != cited_read or sum(shelf.values()) != values['previews']:
        sys.exit('the stats do not add up')
    # The per-collection counts of the collections in CLOSED go to site/stats-private.json (.gitignore), which tools/numbers.py reads; stats.json carries the rest.
    private = {k: v for k, v in values.items() if (k.startswith(('pv_', 'held_', 'line_', 'word_', 'align_', 'rate_')) and k.split('_', 1)[1] in CLOSED + ('translations',))}   # every per-collection count of those collections
    public = {k: v for k, v in values.items() if k not in private}
    write(os.path.join(DOCS, 'stats.json'), json.dumps(public, indent=1, sort_keys=True) + '\n', made)
    with open(os.path.join(REPO, 'site', 'stats-private.json'), 'w', encoding='utf-8') as f:
        json.dump(private, f, indent=1, sort_keys=True)
    missing = sorted(set(values) - set(METHOD))
    if missing:
        sys.exit('METHOD says nothing of %s' % ', '.join(missing))
    values['method'] = ''.join('<tr><td>%s</td><td>%s</td><td class="n">%s</td></tr>\n' % (k, esc(METHOD[k]), '{:,}'.format(values[k]) if isinstance(values[k], int) else esc(str(values[k]))) for k in sorted(METHOD))
    with open(os.path.join(REPO, 'site', 'status.html'), encoding='utf-8') as f:
        write(os.path.join(DOCS, 'status.html'), f.read(), made)
    write(os.path.join(DOCS, '.nojekyll'), '', made)
    with open(PAGE, encoding='utf-8') as f:
        write(os.path.join(DOCS, 'index.html'), f.read(), made)
    with open(os.path.join(REPO, 'site', 'agent.html'), encoding='utf-8') as f:   # the agent's working agreement, linked from the About pane (Bruce, 2 Nov 2026)
        write(os.path.join(DOCS, 'agent.html'), f.read(), made)
    for path in sorted(glob.glob(os.path.join(FONTS, '*'))) + sorted(glob.glob(os.path.join(VENDOR, '*'))) + [os.path.join(REPO, 'site', 'pages.json')]:
        with open(path, 'rb') as f:
            data = f.read()
        out = os.path.join(DOCS, os.path.relpath(path, os.path.join(REPO, 'site'))) if path.startswith((FONTS, VENDOR)) else os.path.join(DOCS, 'pages.json')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'wb') as f:
            f.write(data)
        made.add(out)

    gone = 0
    for path in glob.glob(os.path.join(DOCS, 'corrected.json')) + glob.glob(os.path.join(DOCS, 'entries', '*.json')) + glob.glob(os.path.join(DOCS, 'index', '*.json')) + glob.glob(os.path.join(DOCS, 'snippets', '*.json')) + glob.glob(os.path.join(DOCS, 'snippets', '*', '*.json')) + glob.glob(os.path.join(DOCS, 'fonts', '*')) + glob.glob(os.path.join(DOCS, 'vendor', '*')):
        if path not in made and os.path.basename(os.path.dirname(path)) not in ('text', 'text-all'):   # docs/snippets/text and text-all are tools/collate.py's, written after every cut
            os.remove(path)
            gone += 1
    print('%d entries in %d blocks; %d letter files' % (len(rows), len(blocks), len(letters)))
    print('%d corrections applied of %d rows, on %d entries, since %s'
          % (len(corr), rows_in_table, len(by), about['since']))
    print('%d entries differ from %s in markup or text, %d in text: %d marks in %d pieces, '
          '%d words split at a tag (%d replaced, %d inserted, %d deleted spans; %d unmapped; '
          '%d without a base entry)'
          % (tally['changed'], BASE, tally['entries'], tally['marks'], tally['pieces'], tally['split'],
             tally['replace'], tally['insert'], tally['delete'], tally['unmapped'], tally['nobase']))
    print('%d changes listed for the correction box; %d entries differ only by the citations marked by rule'
          % (tally['context'], tally['marked']))
    print('%d previews shown are guesses (%d the headword not on the line, %d the place not the citation\'s, %d read but unplaced); '
          '%d entries to check in review' % (guesses['word'] + guesses['place'] + guesses['reading'], guesses['word'], guesses['place'], guesses['reading'], len(review)))
    print('%d citations, %d read; %d previews on %d entries, %d with a translation; %d entries whose '
          '<cite>s are not their bibls; %d previews of ids no entry has, left out'
          % (bibls, cited_read, values['previews'], len(shown_), translated, tally['cites'],
             len(unknown)))
    print('site/status.json: comparison items %s read, %s left; citations %s marked, %s unmarked, %s read'
          % (status['comparison items read'], status['comparison items left'], status['citations marked'],
             status['citations unmarked'], status['citations read']))
    print('%d files written, %d stale removed' % (len(made), gone))


if __name__ == '__main__':
    main()
