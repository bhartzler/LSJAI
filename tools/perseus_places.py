#!/usr/bin/env python3
"""The places of LSJ's Greek citations in the open Greek texts of Philology-masters' Perseus shelf, and
the pieces of text a preview is cut from there: the resolver of the measure of 31 Oct 2026
(perseus_coverage.py, which stays with the measure's counts outside this repository), moved here for
tools/snippets.py, which imports it. Standard library only.

The texts. A work's open texts are the rows of Catalogue/editions.txt of kind text, language grc,
source Perseus or First1K and rights 0, whose work (or `part of`) is the work: the work the
lexicon's sidecar resolves the citation's abo reference to (the TLG-E numbering, which the
catalogue's work column follows: LSJ's E. Ph., abo tlg,0006,015, is tlg0006.tlg048), else the abo
work. No file of rights other than 0 is read.

The passages. Every file is cut by its TEI, not by its refsDecl (several declare fewer levels than
they mark), into one running text (notes, heads, apparatus labels, speakers and deletions left out)
and its passages: each div with an n (a textpart) is a passage named by the n's of its divs from the
top joined by full stops (Hdt. 1.1.0, D. 18.204); each l is a line named by its n (an l without one
takes the last n plus one), by its top div and its n (Il. 3.279), and by its whole chain; each
milestone with an n (not para, card, tlnum, lnum) starts a passage of its unit, to the next of that
unit, named by its n and by its top div and its n (Pl. R. 409c, Ath. 5.207c); Whiston's chapter and
section milestones in Josephus name book.chapter.section; a Bekker page (a milestone of unit page or
a div whose n is digits and a or b) with its line milestones names page.line.

The place. A citation's locus is the abo reference after the work (3:279, 409c, 1022b:32), its parts
joined by full stops, a lone letter joined to the number before it (405:c is 405c). It resolves,
best first: exact the locus names a passage the text marks: a leaf div, a line, a milestone's
passage section the locus names a div holding smaller ones (Hdt. 4.25 holds 4.25.1 to 4.25.3) bekker
a Bekker page.line: the stretch from the line milestone at or before the line (they stand every
fifth line), else the page skip the locus names a three-level div without its middle level, where
that is unique (D.L. 7.123 is the text's 7.1.123: book, life, section) suffix the locus names a div
without the top level the text adds (Pl. R. 327 is the text's 1.327; Arist. Pol. 1252a is 1.1252a)
near-line a verse line one or two below the cited one, the cited number absent (lyric lines joined
in the text's colometry: S. Ant. 332-333 are one l, n 333) sidecar only where the abo locus finds
nothing: the place the sidecar keys in the TLG-E numbering (Mosch. 2.114 is tlg0035.tlg002:114), by
the same rules A locus with more levels than the text marks whose part before its last names a
passage (containing: Th. 1.2.3 where the text has 1.2) is not resolved: such passages held the TLG-E
word 36 times in 100. Every open file of the work is tried on its own (S. Aj. has three, one of them
numbered otherwise), and each that resolves the citation keeps its place, the newest edition first.

Philo by Mangey's page. LSJ cites Philo by the volume and page of Mangey's edition (Ph. 1.252, abo
tlg,0018,001:1:252), one id for every treatise; the First1K treatises, Cohn and Wendland's text, mark
Mangey's pages in their own text (the milestones altpage1 and altpage2, p. 252 M., and the marginal note
where a treatise begins, I p. 1 M.), and only that: no table of Mangey's pages against Cohn's sections is
used or made. Such a citation (mangey) is sought in every open Philo file (rule mangey): the passage from
the mark of its page to the next mark, in the file of its volume (mangey(), philo_volumes()); a page two
treatises share (one ends on it, the next begins) is in both, and each is a place.

The word check. A place found is not proof of the place cited: a text numbered otherwise can hold
the number (Hp. Acut. 18 is a chapter of Kühlewein's numbering, not Littré's). Where the TLG-E
preview names the form of the entry on its cited line (its `found`), the Perseus passage is tested
for that form, letters only (accents, breathings, case and elision marks off): a verse line with the
lines before and after it, a Bekker stretch with the next, any other passage alone. An edition and
rule whose citations of one abo work tested number 20 or more and hold the word fewer than half the
time are another numbering in range: none of them is kept (the measure, of the edition it chose for
each work: 34 pairs, 6,844 citations; Manetho, Aretaeus, S. Fr.).

The pieces (pieces()): of a passage whose text is a line, or more than half of it lines, its lines,
each named as the passage names its own (23.620 where the place is book.line, 620 where it is the
line), with the line before the first and the line after the last, null past the file's start or
end; a line the editor deletes (<del>, which the text leaves out) is not one, and a passage of none
has no piece (E. Andr. 671 keeps its TLG-E line). Of any other passage its sentences, each with the
place it begins in and the first place of the passage it reaches (a sentence begun in 529b and run
into 529c: 529c, the place the cited one is named by), with the sentence before the first and the
sentence after the last, cut from the running text across any section's or milestone's bound. Each
unit has its CTS passage in the file's own scheme (cts(): the refsDecl's levels, Iliad 23.620, Plato
7.529, Herodotus 5.82.1), the Scaife reader's address of it. A sentence ends at a full stop, a
question mark (; or ;) or a raised point (· or ·) followed by a space or the text's end. A place is
named as the citation names its passage: the leaf div or the milestone of the same unit, with the
cited place's levels (529c, not 7.529c; 5.82.2 under the chapter 5.82; 209 for a speech), a Bekker
page and line by the line marks (1022b.30, not the chapter 5.22).

First1K's Aristotle. Some of its files (Ross's, Prantl's, Fobes's) print Bekker's column in a marginal
note (184a, 269 a, p. 704a; b alone, the other column of the page) and his lines as lb n (every fifth):
read as a page milestone and line milestones are; the others (Bekker's Oxford reprint: Historia
animalium, Topica, De mundo, lb without n) mark no Bekker number and are not placed by one.
"""
import bisect, collections, csv, multiprocessing as mp, os, re, sys, unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
csv.field_size_limit(1 << 30)

WORK_KEY = re.compile(r'([a-z]+,[^,:]*,[^,:]*)')          # the census's work key
CTS_WORK = re.compile(r'^tlg,(\d{4}),(\d{3}[a-z]?)$')
DIVS = {'div', 'div1', 'div2', 'div3', 'div4', 'div5'}
SKIP = {'note', 'head', 'bibl', 'label', 'ref', 'speaker', 'castList', 'figure', 'fw', 'gap', 'del'}
NOT_PASSAGES = {'para', 'tlnum', 'lnum', 'line', 'card'}
BEKKER = re.compile(r'^\d+[ab]$')
WS = re.compile(r'\s+')
END = re.compile(r'[.;;··](?=\s|$)')     # a sentence's end
ELISION = dict.fromkeys((0x2019, 0x27, 0x2bc, 0x1fbd, 0x1fbf, 0x313), None)
RANK = {'exact': 0, 'section': 1, 'bekker': 2, 'skip': 3, 'suffix': 4, 'near-line': 5, 'containing': 6}
CHECKED, HELD = 20, 0.5       # the word check: a work and rule tested this often, holding the word less
PHILO, PHILO_FILES = 'tlg,0018,001', 'tlg0018.'      # LSJ's Ph. vol.page, all under one abo id; the open files
MANGEY_VOL = re.compile(r'^\s*(II|I|1|2)\.?\s*(?=[pP])')      # I p. 1 M., IIp.545M., 1. p. 163 M.
MANGEY_PAGE = re.compile(r'[pP][.,]?\s*(\d+)')
MANGEY_BARE = re.compile(r'(\d+)\s*\.?\s*M')                   # 23 Μ., 287 M.
ARISTOTLE_FILES = 'tlg0086.'  # First1K's Aristotle: Bekker's columns in marginal notes, his lines as lb n (Ross)
BEKKER_NOTE = re.compile(r'^(?:p\.\s*)?(\d{2,4})?\s*,?\s*([ab])(?:\s*\d+)?\.?$')
MANGEY_STEP = 3               # a run of Mangey's marks: each 1 to 3 pages after the one before


def local(tag):
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ''


def norm(s):
    """letters only: no accents, breathings, case or elision marks; final sigma as sigma."""
    s = unicodedata.normalize('NFD', s.lower()).translate(ELISION)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('ς', 'σ')


def words(s):
    return re.findall(r'[^\W\d_]+', norm(s))


HYPHENATED = re.compile(r'([\u0370-\u03ff\u1f00-\u1fff])[-\u2010] ([\u0370-\u03ff\u1f00-\u1fff])')


def clean(s):
    """A piece's text: one space between words, NFC, and a word its printed line broke with a hyphen
    joined, the next letter a small one (First1K keeps the edition's lines: ἐμ- πορίων is ἐμπορίων)."""
    s = unicodedata.normalize('NFC', ' '.join(s.split()))
    return HYPHENATED.sub(lambda m: m.group(1) + m.group(2) if m.group(2).islower() else m.group(0), s)


# ---------------------------------------------------------------- the TEI, cut into passages

def mangey(marks):
    """A Philo file's pages of Mangey's edition from its marks, [(position, text)] in the text's order (the
    milestones altpage1 and altpage2, p. 2M., and the marginal notes naming a page, I p. 1 M.): ([(position,
    volume or None, page)] of the marks kept, the file's volume or None). A mark names its page by the
    number after p., else by the number before M.; its volume where it begins with one (I, II, 1., 2.).
    The marks kept are the runs of two or more, each mark 1 to MANGEY_STEP pages after the one before it in
    one volume (a run of another volume is its own: De sacrificiis holds II p. 265 to 269 between I p. 167
    and its return; De aeternitate mundi holds 497 to 502 before 492 to 497, Mangey's order of the leaves),
    a run of two going back to before the page kept last no run (De ebrietate's 339, 340 after 387, misread);
    a mark between two kept ones that its number does not place (p. 1.50 M. between 149
    and 151, p. Μ.) is named by them where the marks between are as many as the pages missing. A run's
    volume is the one its marks name, else the file's: the first a kept run names."""
    parsed = []
    for pos, raw in marks:
        t = re.sub(r'l(?=\d)', '1', raw.replace('Ι', 'I').replace('Μ', 'M'))
        v = MANGEY_VOL.match(t)
        m = MANGEY_PAGE.search(t) or MANGEY_BARE.search(t)
        parsed.append((pos, {'I': 1, '1': 1, 'II': 2, '2': 2}[v.group(1)] if v else None, int(m.group(1)) if m else None))
    runs, cur, cvol = [], [], None
    for k, (pos, vol, page) in enumerate(parsed):
        if page is None:
            continue
        if cur and 1 <= page - parsed[cur[-1]][2] <= MANGEY_STEP and (vol is None or cvol is None or vol == cvol):
            cur.append(k)
            cvol = cvol or vol
            continue
        if cur:
            runs.append((cur, cvol))
        cur, cvol = [k], vol
    if cur:
        runs.append((cur, cvol))
    runs = [(r, v) for r, v in runs if len(r) >= 2]
    fvol = next((v for r, v in runs if v), None)
    kept, last = [], None       # two marks of the file's volume going back (De ebrietate's 339, 340 for 389, 390) are no run
    for r, v in runs:
        if not v or v == fvol:
            if last is not None and parsed[r[0]][2] < last and len(r) < 3:
                continue
            last = parsed[r[-1]][2]
        kept.append((r, v))
    runs = kept
    vol_of = {k: (v if v and v != fvol else None) for r, v in runs for k in r}
    page_of = {k: parsed[k][2] for k in vol_of}
    kept = sorted(vol_of)
    for a, b in zip(kept, kept[1:]):
        between = list(range(a + 1, b))
        if between and vol_of[a] == vol_of[b] and page_of[b] - page_of[a] - 1 == len(between):
            for j, k in enumerate(between):
                vol_of[k], page_of[k] = vol_of[a], page_of[a] + j + 1
    return [(parsed[k][0], vol_of[k], page_of[k]) for k in sorted(vol_of)], fvol


def mangey_key(vol, page):
    """The key of a Mangey page in a file's keys: M.252 in the file's own volume, M2.266 in another."""
    return 'M%s.%d' % (vol or '', page)


class Cut:
    def __init__(self, philo=False, aristotle=False):
        self.philo, self.marks, self.mangey_vol, self.mangey_pages = philo, [], None, []
        self.aristotle = aristotle
        self.parts, self.pos = [], 0
        self.keys = {}                 # key -> (kind, start, end)
        self.leaf, self.top = set(), set()
        self.pages = {}                # Bekker page -> line milestones
        self.open_ms = {}              # unit -> (keys, start) of the passage it is in
        self.lspans, self.bspans = [], []
        self.skips = collections.Counter()
        self.lines = self.depth = 0
        self.last_l = self.page = None
        self.family = {}               # a milestone family's chapter (Whiston_chapter) -> its n
        self.ls = []                   # every l: (start, end, its names: whole chain, top div, n)
        self.divs = []                 # every div: (start, end, chain, leaf)
        self.ms = collections.defaultdict(list)   # a milestone unit -> [(start, its names)]
        self.pbs = []                  # every page break: (start, the page printed), for a link to the page (the Loeb)

    def emit(self, s):
        if s:
            s = WS.sub(' ', s)
            self.parts.append(s)
            self.pos += len(s)

    def put(self, key, kind, a, b):
        old = self.keys.get(key)
        if old is None or (old[0] != 'div' and kind == 'div'):
            self.keys[key] = (kind, a, b)

    def close_ms(self, unit):
        o = self.open_ms.pop(unit, None)
        if o:
            for k, kind in o[0]:
                self.put(k, kind, o[1], self.pos)
            if unit == 'bekkerline':
                self.bspans.append((o[1], self.pos))

    def walk(self, el, chain):
        tag = local(el.tag)
        if self.philo and tag == 'note' and el.get('type') == 'marginal':
            t = ' '.join(''.join(el.itertext()).split())
            if re.search(r'\d\s*\.?\s*[MΜ]', t):          # I p. 1 M.: Mangey's page where a treatise begins
                self.marks.append((self.pos, t))
            return
        if self.philo and tag == 'milestone' and el.get('unit') in ('altpage1', 'altpage2'):
            self.marks.append((self.pos, el.get('n') or ''))
            return
        if self.aristotle and tag == 'note' and el.get('type') == 'marginal':
            m = BEKKER_NOTE.match(' '.join(''.join(el.itertext()).split()))
            if m and (m.group(1) or self.page):          # 184a, 269 a, p. 704a; b alone, the page's other column
                self.milestone('page', (m.group(1) or self.page[:-1]) + m.group(2), chain)
            return
        if tag == 'pb' and (el.get('n') or '').strip():
            self.pbs.append((self.pos, el.get('n').strip()))
        if tag in SKIP:
            return
        start = self.pos
        isdiv = tag in DIVS and el.get('n') is not None and el.get('type') not in ('edition', 'translation', 'commentary')
        if isdiv:
            n = el.get('n').strip()
            chain = chain + (n,)
            if len(chain) == 1:
                self.top.add(n)
            if BEKKER.match(n):
                self.page = n
                self.pages.setdefault(n, [])
        if self.aristotle and tag == 'lb' and (el.get('n') or '').strip().isdigit() and self.page:
            self.milestone('line', el.get('n').strip(), chain)      # Ross's lines of Bekker's column, every fifth
        if tag == 'milestone' and el.get('n'):
            self.milestone(el.get('unit') or '', el.get('n').strip(), chain)
        self.emit(el.text)
        for c in el:
            self.walk(c, chain)
            self.emit(c.tail)
        self.close(el, tag, start, isdiv, chain)

    def milestone(self, unit, n, chain):
        """A milestone of unit and n where the text stands (a marginal Bekker column and an lb n of First1K's
        Aristotle as a page milestone and a line one)."""
        if unit == 'line' and self.page and n.isdigit():
            self.close_ms('bekkerline')
            self.pages[self.page].append(int(n))
            self.open_ms['bekkerline'] = ([(f'{self.page}.{n}', 'bekker-line')], self.pos)
            self.ms['ms:bekkerline'].append((self.pos, (f'{self.page}.{n}',)))
        elif unit.endswith(('_chapter', '_section')) and chain:
            fam = unit.rsplit('_', 1)[0]           # Josephus: Whiston's chapters and sections
            self.close_ms(unit)
            if unit.endswith('_chapter'):
                self.family[fam] = n
                self.close_ms(fam + '_section')
                ks = [(f'{chain[0]}.{n}', 'ms:' + unit)]
            else:
                ks = [(f'{chain[0]}.{self.family.get(fam, "")}.{n}', 'ms:' + unit)]
            self.open_ms[unit] = (ks, self.pos)
            self.ms['ms:' + unit].append((self.pos, tuple(k for k, kind in ks)))
        elif unit not in NOT_PASSAGES:
            if unit == 'page' and BEKKER.match(n):
                self.page = n
                self.pages.setdefault(n, [])
            self.close_ms(unit)
            ks = [(n, 'ms:' + unit)] + ([(f'{chain[0]}.{n}', 'ms:' + unit)] if chain else [])
            self.open_ms[unit] = (ks, self.pos)
            self.ms['ms:' + unit].append((self.pos, tuple(k for k, kind in ks)))

    def close(self, el, tag, start, isdiv, chain):
        if isdiv:
            key = '.'.join(chain)
            below = any(local(d.tag) in DIVS and d.get('n') is not None for d in el.iter() if d is not el)
            self.put(key, 'div', start, self.pos)
            self.divs.append((start, self.pos, chain, not below))
            if not below:
                self.leaf.add(key)
                self.depth = max(self.depth, len(chain))
            for i in range(1, len(chain)):
                k = '.'.join(chain[i:])
                if k not in self.keys:
                    self.keys[k] = ('suffix-leaf' if not below else 'suffix', start, self.pos)
            if len(chain) == 3 and not below:
                k = f'{chain[0]}.{chain[2]}'
                self.skips[k] += 1
                if self.skips[k] == 1:
                    self.keys.setdefault('~' + k, ('skip', start, self.pos))
        if tag == 'l':
            n = (el.get('n') or '').strip()
            if not n and self.last_l is not None:
                n = str(self.last_l + 1)
            if n:
                m = re.match(r'^(\d+)', n)
                self.last_l = int(m.group(1)) if m else self.last_l
                self.lines += 1
                self.lspans.append((start, self.pos))
                self.ls.append((start, self.pos, ('.'.join(chain + (n,)), f'{chain[0]}.{n}' if chain else n, n), chain))
                self.depth = max(self.depth, len(chain) + 1)
                for k in {n, (f'{chain[0]}.{n}' if chain else n), '.'.join(chain + (n,))}:
                    if k not in self.keys or self.keys[k][0] not in ('div', 'l'):
                        self.keys[k] = ('l', start, self.pos)

    def finish(self):
        for u in list(self.open_ms):
            self.close_ms(u)
        if self.marks:          # Mangey's pages: each mark to the next; the text before the first, the page before it
            kept, self.mangey_vol = mangey(self.marks)
            self.mangey_pages = kept
            spans = [(pos, vol, page) for pos, vol, page in kept]
            if kept and kept[0][2] > 1 and ''.join(self.parts)[:kept[0][0]].strip():
                spans.insert(0, (0, kept[0][1], kept[0][2] - 1))
            for i, (pos, vol, page) in enumerate(spans):
                end = spans[i + 1][0] if i + 1 < len(spans) else self.pos
                key = mangey_key(vol, page)
                if end > pos:               # a page twice (De sacrificiis' I p. 167 on its return): the first is its place
                    self.ms['ms:mangey'].append((pos, (key,)))
                    if key not in self.keys:
                        self.keys[key] = ('ms:mangey', pos, end)
        for k, c in self.skips.items():         # a skip key two divs share names neither
            sk = self.keys.pop('~' + k, None)
            if c == 1 and sk and k not in self.keys:
                self.keys[k] = sk
        self.lspans.sort()
        self.bspans.sort()
        self.ls.sort()
        self.divs.sort(key=lambda d: (d[0], -d[1]))
        self.spans = collections.defaultdict(list)      # a div's (start, end) -> the chains of the divs there
        for s, e, chain, leaf in self.divs:
            self.spans[(s, e)].append(chain)


def edition_root(root):
    body = next((el for el in root.iter() if local(el.tag) == 'body'), None)
    if body is None:
        return root
    return next((el for el in body if local(el.tag) == 'div' and el.get('type') == 'edition'), body)


def steps(root):
    """A TEI file's CTS citation scheme, the elements its deepest cRefPattern names a level by, from the
    top: ['div', 'l'] for Homer's book and line, ['div', 'div'] for Plato's book and Stephanus page."""
    best = []
    for e in root.iter():
        if local(e.tag) == 'cRefPattern':
            got = re.findall(r"tei:(\w+)\[@n=\\?['\"]\$\d+", e.get('replacementPattern') or '')   # some files escape the quote (\')
            if len(got) > len(best):
                best = got
    return best


def cts(scheme, chain, n=None):
    """A place's CTS passage in a file's scheme: its divs' n's from the top, as many as the scheme has
    div levels, and the line's n where the scheme ends in a line; shallower where the place is (a section
    of a text cited by line, a book: Scaife opens the whole of it); '' where the scheme names other
    elements or none."""
    if not scheme or any(x not in ('div', 'l') for x in scheme):
        return ''
    d = scheme.count('div')
    parts = list(chain[:d])
    if scheme[-1] == 'l' and n and len(chain) >= d:
        parts.append(n)
    return '.'.join(parts)


def read(path):
    """A file cut: (Cut, its running text, its header's title and author and its CTS scheme), or None
    where it does not parse."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    name = os.path.basename(path)
    cut = Cut(philo=name.startswith(PHILO_FILES), aristotle=name.startswith(ARISTOTLE_FILES) and '.1st1K-' in name)
    for c in edition_root(root):
        cut.walk(c, ())
        cut.emit(c.tail)
    cut.finish()
    head = next((e for e in root.iter() if local(e.tag) == 'titleStmt'), None)
    names = {}
    for e in (head.iter() if head is not None else ()):
        if local(e.tag) in ('title', 'author') and local(e.tag) not in names:
            names[local(e.tag)] = ' '.join(''.join(e.itertext()).split())
    names['scheme'] = steps(root)
    names['urn'] = next((e.get('n') for e in root.iter() if local(e.tag) == 'div' and e.get('type') == 'edition'
                         and (e.get('n') or '').startswith('urn:cts:')), '')
    return cut, ''.join(cut.parts), names


def window(cut, text, key):
    """The text the word check reads for a passage: a line with its neighbours, a Bekker stretch with
    the next, else the passage."""
    kind, a, b = cut.keys[key]
    if kind == 'l':
        i = bisect.bisect_left(cut.lspans, (a, b))
        lo = cut.lspans[max(0, i - 1)][0]
        hi = cut.lspans[min(len(cut.lspans) - 1, i + 1)][1]
        return text[lo:hi]
    if kind == 'bekker-line':
        i = bisect.bisect_left(cut.bspans, (a, b))
        hi = cut.bspans[i + 1][1] if i + 1 < len(cut.bspans) else b
        return text[a:hi]
    return text[a:b]


def _index(path):
    """What resolve() reads of a file: its keys' kinds, leaf divs, top-level ns, Bekker pages and
    depth, whether it has lines, its header's names; of a Philo file its Mangey volume, the first and last
    page of that volume it marks, its marks and the marks kept (mangey())."""
    got = read(path)
    if got is None:
        return {'path': path, 'keys': {}, 'leaf_set': set(), 'top': [], 'pages': {}, 'lines': 0, 'depth': 0,
                'names': {}, 'error': True}
    cut, text, names = got
    own = [page for pos, vol, page in cut.mangey_pages if vol is None]      # in the text's order
    return {'path': path, 'keys': {k: v[0] for k, v in cut.keys.items()}, 'leaf_set': cut.leaf,
            'top': sorted(cut.top), 'pages': {p: sorted(set(v)) for p, v in cut.pages.items()},
            'lines': cut.lines, 'depth': cut.depth, 'names': names,
            'mangey': (cut.mangey_vol, own[0], own[-1], len(cut.marks), len(cut.mangey_pages)) if own else None}


def _check(arg):
    """The word check of one file: {tag: whether the passage holds the word} for (tag, key, word)."""
    path, items = arg
    got = read(path)
    if got is None:
        return {}
    cut, text, names = got
    out, seen = {}, {}
    for tag, key, fw in items:
        if key not in cut.keys:
            continue
        if key not in seen:
            seen[key] = set(words(window(cut, text, key)))
        out[tag] = fw in seen[key]
    return out


# ---------------------------------------------------------------- a citation's place

def abo(n):
    """A bibl's Perseus reference as the measure reads it: (the abo work key, the tlg work in CTS form or
    None, the locus's parts), or None for a reference to no tlg work."""
    n = (n or '').strip()
    if not n.startswith('Perseus:abo:tlg,'):
        return None
    body = n[len('Perseus:abo:'):]
    m = WORK_KEY.match(body)
    wk = m.group(1) if m else body
    c = CTS_WORK.match(wk)
    rest = body[len(wk):]
    return wk, (f'tlg{c.group(1)}.tlg{c.group(2)}' if c else None), locus_parts(rest[1:] if rest.startswith(':') else rest)


def locus_parts(locus):
    merged = []
    for p in (p.strip() for p in locus.split(':') if p.strip()):
        if merged and re.fullmatch(r'[a-g]', p) and merged[-1].isdigit():
            merged[-1] += p
        else:
            merged.append(p)
    return merged


def resolve(parts, idxs):
    """(how, file, key, the passage's kind) for the best of the work's files; how None when none."""
    if not parts:
        return None, None, None, None
    key = '.'.join(parts)
    best = None

    def take(how, ix, k, kind):
        nonlocal best
        if best is None or RANK[how] < RANK[best[0]]:
            best = (how, ix['path'], k, kind)

    for ix in idxs:
        keys, leaf = ix['keys'], ix['leaf_set']
        kind = keys.get(key)
        if kind:
            if kind == 'div':
                take('exact' if key in leaf else 'section', ix, key, kind)
            elif kind in ('l', 'bekker-line') or kind.startswith('ms:'):
                take('exact', ix, key, kind)
            elif kind in ('suffix-leaf', 'suffix'):
                take('suffix', ix, key, kind)
            elif kind == 'skip':
                take('skip', ix, key, kind)
        if len(parts) == 2 and BEKKER.match(parts[0]) and parts[1].isdigit() and parts[0] in ix['pages']:
            below = [x for x in ix['pages'][parts[0]] if x <= int(parts[1])]
            k = f'{parts[0]}.{below[-1]}' if below else None
            if k in keys:
                take('bekker', ix, k, keys[k])
            else:
                for k in (parts[0],) + tuple(f'{t}.{parts[0]}' for t in ix['top']):
                    if k in keys:
                        take('bekker', ix, k, keys[k])
                        break
            continue
        if ix['lines'] and parts[-1].isdigit():
            for d in (1, 2):                            # lyric lines joined in the text's colometry
                k = '.'.join(parts[:-1] + [str(int(parts[-1]) - d)])
                if keys.get(k) == 'l':
                    take('near-line', ix, k, 'l')
                    break
        if len(parts) > ix['depth'] >= 1:
            k = '.'.join(parts[:-1])
            kind = keys.get(k)
            if kind and ((kind == 'div' and k in leaf) or kind.startswith('ms:') or kind == 'suffix-leaf'):
                take('containing', ix, k, kind)
    return best if best else (None, None, None, None)


SHELVES = {'Perseus': 'Perseus/', 'First1K': 'Perseus/', 'Loeb': 'Loeb/', 'DigiLibLT': 'DigiLibLT/'}   # a source's TEI texts and their shelf folder


def open_texts(masters, every=False):
    """The open Greek texts of the Perseus shelf by the work they hold: {work: [editions.txt row]},
    a row under its work and under the work it is part of; a row's file is on the shelf as Perseus/name.
    With every: every TEI text of the catalogue, Greek or Latin, on any of SHELVES (Perseus and
    First1KGreek on the Perseus shelf, the Loeb shelf, DigiLibLT), each to its own tree."""
    out = collections.defaultdict(list)
    with open(os.path.join(masters, 'Catalogue', 'editions.txt'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            ok = (r['kind'] == 'text' and r['source'] in SHELVES and r['file'].startswith(SHELVES[r['source']])
                  and (r['language'] in ('grc', 'lat') if every else r['language'] == 'grc' and r['rights'] == '0'
                       and r['source'] in ('Perseus', 'First1K')))
            if ok:
                for w in {r['work'], r['part of']} - {''}:
                    out[w].append(r)
    return out


def year(row):
    """An edition's year for its order, the latest a catalogue row names (1908-1920 is 1920), else 0."""
    got = re.findall(r'\d{4}', row.get('year') or '')
    return max(map(int, got)) if got else 0


def mangey_cite(c):
    """A citation of Philo by Mangey's volume and page (LSJ's Ph. 1.252, abo tlg,0018,001:1:252): (volume,
    page), else None."""
    p = c['parts']
    if c['wk'] == PHILO and len(p) == 2 and p[0] in ('1', '2') and p[1].isdigit():
        return int(p[0]), int(p[1])
    return None


def philo_volumes(ixs):
    """The Mangey volume of each Philo file, {path: 1, 2 or None}, the files in the catalogue's order (the
    TLG's, Cohn and Wendland's): the one its marks name (mangey()); else, where its pages of its own volume
    run on from the file before it (its first in the text's order at or past that file's last less one), that
    file's; else, where they run into the file after it, that one's; else none (its citations are not placed by
    Mangey's page)."""
    m = {ix['path']: ix.get('mangey') for ix in ixs}
    paths = [ix['path'] for ix in ixs if m[ix['path']]]
    out = {p: m[p][0] for p in paths}
    for a, b in zip(paths, paths[1:]):
        if out[b] is None and out[a] and m[b][1] >= m[a][2] - 1:
            out[b] = out[a]
    for a, b in reversed(list(zip(paths, paths[1:]))):
        if out[a] is None and out[b] and m[a][2] <= m[b][1] + 1:
            out[a] = out[b]
    return out


def places(cits, masters, shelf, jobs=6, every=False):
    """Resolve the citations in every open text of their work (the catalogue of Philology-masters, the
    files in its Perseus shelf, shelf) and run the word check edition by edition. Each citation is a dict
    with wk (the abo work key), cwork (the work it names), parts (the abo locus), side (the sidecar's
    place in the TLG-E numbering, as parts) and fw (the TLG-E preview's found form, letters only, or
    None); each gains places, one for every edition that resolves it and whose word check keeps it, the
    newest first: {how, path, key, kind, row}. An edition's place is rejected where its rule, for the
    citations of that abo work, was tested 20 times or more and held the word fewer than half of them.
    Returns the open texts by work, each file's header names and scheme by path, and the tallies."""
    tally = collections.Counter()
    texts = open_texts(masters, every)
    for c in cits:
        c['places'] = []
    works = sorted({c['cwork'] for c in cits if c['cwork'] in texts})
    at = lambda r: os.path.join(shelf, r['file'].split('/', 1)[1]) if r['file'].startswith('Perseus/') else os.path.join(masters, r['file'])
    files = sorted({at(r) for w in works for r in texts[w]})
    philo = [] if not any(mangey_cite(c) for c in cits) else \
        sorted({(at(r), r['work']) for w, rs in texts.items() if w.startswith(PHILO_FILES) for r in rs if r['work'] == w})
    files = sorted(set(files) | {p for p, w in philo})
    with mp.Pool(jobs) as pool:
        idx = {d['path']: d for d in pool.imap_unordered(_index, files, chunksize=4)}
    tally['perseus: files read'] = len(files)
    tally['perseus: files that do not parse'] = sum(1 for d in idx.values() if d.get('error'))
    cov = [c for c in cits if c['cwork'] in texts]
    tally['perseus: citations of a work with an open text'] = len(cov)
    vols = philo_volumes([idx[p] for p, w in philo])
    for p, v in vols.items():
        idx[p]['names']['mangey'] = v
        tally['perseus: Philo files placed in Mangey\'s volume %s' % (v or 'none')] += 1
    rows = {p: r for w, rs in texts.items() for r in rs for p in [at(r)]}

    found = []                      # (citation, place)
    for c in cov:
        vp = mangey_cite(c)
        if vp:                      # Philo by Mangey's volume and page: the files of that volume marking the page
            before = len(found)
            for p, w in philo:
                for k in ((mangey_key(None, vp[1]),) if vols.get(p) == vp[0] else ()) + (mangey_key(vp[0], vp[1]),):
                    if idx[p]['keys'].get(k) == 'ms:mangey':
                        found.append((c, {'how': 'mangey', 'path': p, 'key': k, 'kind': 'ms:mangey', 'row': rows[p],
                                          'label': '%d.%d' % vp, 'work': w}))
                        break
            tally['perseus: Philo cited by Mangey\'s page'] += 1
            tally['perseus: Philo cited by Mangey\'s page, placed in %d files' % (len(found) - before)] += 1
            continue
        seen = set()
        for r in sorted(texts[c['cwork']], key=lambda r: -year(r)):
            path = at(r)
            if path in seen:
                continue
            seen.add(path)
            h, _, key, kind = resolve(c['parts'], [idx[path]])
            if not h or h == 'containing':
                sp = c['side']
                h = None
                if sp and sp != c['parts']:
                    g = resolve(sp, [idx[path]])
                    if g[0] and g[0] not in ('containing', 'near-line'):
                        h, key, kind = 'sidecar ' + g[0], g[2], g[3]
            if h:
                found.append((c, {'how': h, 'path': path, 'key': key, 'kind': kind, 'row': r}))
    jobs_ = collections.defaultdict(list)
    for i, (c, pl) in enumerate(found):
        if c['fw']:
            jobs_[pl['path']].append((i, pl['key'], c['fw']))
    got = {}
    with mp.Pool(jobs) as pool:
        for d in pool.imap_unordered(_check, sorted(jobs_.items()), chunksize=4):
            got.update(d)
    pairs = collections.defaultdict(lambda: [0, 0])
    for i, h in got.items():
        c, pl = found[i]
        p = pairs[(pl['path'], c['wk'], pl['how'])]
        p[0] += 1
        p[1] += h
    low = {k for k, (n, h) in pairs.items() if n >= CHECKED and h < HELD * n}
    for i, (c, pl) in enumerate(found):
        if (pl['path'], c['wk'], pl['how']) in low:
            tally['perseus: places rejected by the word check'] += 1
            continue
        c['places'].append(pl)
        tally['perseus: places kept, by rule: %s' % pl['how']] += 1
        if i in got:
            tally['perseus: places kept and tested by the word check'] += 1
            tally['perseus: places kept and holding the word'] += got[i]
    tally['perseus: places resolved'] = len(found)
    tally['perseus: edition, rule and work triples rejected by the word check'] = len(low)
    tally['perseus: citations with a place kept'] = sum(1 for c in cov if c['places'])
    tally['perseus: citations with places kept in two or more editions'] = sum(1 for c in cov if len(c['places']) > 1)
    return texts, {p: d['names'] for p, d in idx.items()}, tally


# ---------------------------------------------------------------- the pieces a preview is cut from

def sentences(text):
    """The running text's sentences, (start, end) of each without the spaces around it."""
    out, at = [], 0
    for e in [m.end() for m in END.finditer(text)] + [len(text)]:
        s = at
        while s < e and text[s].isspace():
            s += 1
        if s < e:
            out.append((s, e))
        at = e
    return out


def dropped(cut, key, a, b):
    """How many top levels a key leaves off the div it names (the text's 1.327 cited as 327: one)."""
    parts = key.split('.')
    d = next((chain for chain in cut.spans.get((a, b), ()) if list(chain[-len(parts):]) == parts), None)
    return len(d) - len(parts) if d else 0


def namer(cut, key, kind, a, b, memo):
    """How the places of a passage's family are named, as the citation names its own: (the starts of
    the family's places, their names), the family the leaf divs (with the cited place's levels: its
    top levels dropped for a suffix, the middle one for a skip) or the milestones of the cited unit (by n,
    or by top div and n, as the key), a Bekker stretch's by its line marks (1022b.30), as LSJ cites it."""
    if kind.startswith('ms:') or kind == 'bekker-line':     # a Bekker stretch's sentences by its line marks
        kind = 'ms:bekkerline' if kind == 'bekker-line' else kind
        marks = cut.ms.get(kind, [])
        own = next((names for pos, names in marks if pos == a and key in names), None)
        form = (kind, own.index(key) if own else 0)
    else:
        form = ('div', 'skip' if kind == 'skip' else dropped(cut, key, a, b) if kind in ('suffix', 'suffix-leaf') else 0)
    if form not in memo:
        if form[0] == 'div':
            leaves = [(s, chain) for s, e, chain, leaf in cut.divs if leaf]
            drop = form[1]

            def name(chain):
                if drop == 'skip':
                    return f'{chain[0]}.{chain[2]}' if len(chain) == 3 else '.'.join(chain)
                return '.'.join(chain[drop:]) if len(chain) > drop else '.'.join(chain)
            memo[form] = ([s for s, chain in leaves], [name(chain) for s, chain in leaves])
        else:
            marks, j = cut.ms.get(kind, []), form[1]
            memo[form] = ([pos for pos, names in marks], [names[min(j, len(names) - 1)] for pos, names in marks])
    return memo[form]


def _pieces(arg):
    """The pieces of one file's passages: {key: piece} (pieces()); a Philo file's Mangey pages named by
    volume and page (1.252) where its volume is known."""
    path, keys, vol = arg
    got = read(path)
    if got is None:
        return path, {}
    cut, text, names = got
    if vol:
        cut.ms['ms:mangey'] = [(pos, tuple('%s.%s' % (k[1:].split('.')[0] or vol, k.split('.')[1]) for k in ks))
                               for pos, ks in cut.ms['ms:mangey']]
    out, sents, memo = {}, None, {}
    pb_at = [p for p, n in cut.pbs]
    page_at = lambda p: cut.pbs[bisect.bisect_right(pb_at, p) - 1][1] if pb_at and bisect.bisect_right(pb_at, p) else None
    lstarts = [x[0] for x in cut.ls]
    leaves = [(d[0], d[2]) for d in cut.divs if d[3]]
    lstarts_d = [x[0] for x in leaves]
    for key in keys:
        if key not in cut.keys:
            continue
        kind, a, b = cut.keys[key]
        lo = bisect.bisect_left(lstarts, a)
        if kind == 'l':
            while lo < len(cut.ls) and cut.ls[lo][:2] != (a, b):
                lo += 1
            hi = lo + 1
        else:
            hi = lo
            while hi < len(cut.ls) and cut.ls[hi][1] <= b:
                hi += 1
        inside = sum(x[1] - x[0] for x in cut.ls[lo:hi])
        if hi <= len(cut.ls) and (kind == 'l' or (hi > lo and inside * 2 > len(text[a:b].strip()))):
            if kind == 'l':                              # a line: its neighbours named as it is
                j = next((k for k, x in enumerate(cut.ls[lo][2]) if x == key), 2)
                at = lambda ns: ns[j]
            else:                    # a passage of lines: each by its whole chain, less the levels the key drops
                drop = dropped(cut, key, a, b)
                at = lambda ns: '.'.join(ns[0].split('.')[drop:]) or ns[0]
            said = lambda k: clean(text[cut.ls[k][0]:cut.ls[k][1]])
            units = [(at(cut.ls[k][2]), said(k), cts(names['scheme'], cut.ls[k][3], cut.ls[k][2][2]))
                     for k in range(lo, hi) if said(k)]
            if not units:                # a line the editor deletes (<del>, printed in brackets) has no text here
                continue
            k0, k1 = lo - 1, hi
            while k0 >= 0 and not said(k0):
                k0 -= 1
            while k1 < len(cut.ls) and not said(k1):
                k1 += 1
            out[key] = {'verse': True, 'units': units, 'before': (at(cut.ls[k0][2]), said(k0)) if k0 >= 0 else None,
                        'after': (at(cut.ls[k1][2]), said(k1)) if k1 < len(cut.ls) else None,
                        'pages': [page_at(cut.ls[k][0]) for k in range(lo, hi) if said(k)]}
            continue
        if sents is None:
            sents = sentences(text)
            ends = [e for s, e in sents]
            starts = [s for s, e in sents]
        i0 = bisect.bisect_right(ends, a)             # the first sentence ending past the passage's start
        i1 = bisect.bisect_left(starts, b)            # the first beginning at or past its end
        while i1 > i0 and not text[max(a, sents[i1 - 1][0]):min(b, sents[i1 - 1][1])].strip():
            i1 -= 1
        while i0 < i1 and not text[max(a, sents[i0][0]):min(b, sents[i0][1])].strip():
            i0 += 1
        if i0 >= i1:
            continue
        starts_, names_ = namer(cut, key, kind, a, b, memo)

        def place(p):
            k = bisect.bisect_right(starts_, p) - 1
            return names_[k] if k >= 0 else (names_[0] if names_ else key)

        def passage(p):                             # the CTS passage of the leaf div a place stands in
            k = bisect.bisect_right(lstarts_d, p) - 1
            return cts(names['scheme'], leaves[k][1]) if k >= 0 else ''

        def sentence(k, cited=False):
            if not 0 <= k < len(sents):
                return None
            s, e = sents[k]
            return (place(max(s, a)) if cited else place(s), clean(text[s:e]))
        out[key] = {'verse': False,
                    'units': [sentence(k) + (sentence(k, True)[0], passage(max(sents[k][0], a))) for k in range(i0, i1)],
                    'before': sentence(i0 - 1), 'after': sentence(i1),
                    'pages': [page_at(max(sents[k][0], a)) for k in range(i0, i1)]}
    return path, out


def pieces(wants, jobs=6, vols=None):
    """For {path: [key]} the pieces of each passage, {(path, key): piece}, a piece {verse, units,
    before, after}: in verse units its lines [(name, text)], in prose its sentences [(the place it
    begins in, text, the place in the passage it reaches first)]; before and after the unit before the
    first and after the last, (name, text), or None. vols: a Philo file's Mangey volume by path (places()'s
    names[path]['mangey']), which names its pages."""
    out, vols = {}, vols or {}
    with mp.Pool(jobs) as pool:
        for path, got in pool.imap_unordered(_pieces, sorted((p, sorted(k), vols.get(p)) for p, k in wants.items()), chunksize=2):
            for key, piece in got.items():
                out[(path, key)] = piece
    return out
