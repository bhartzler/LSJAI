#!/usr/bin/env python3
"""The places of LSJ's papyrus citations in the Duke Databank of Documentary Papyri (DDbDP) as PHI's
PHI 7 gives it, read through a Philology store of its DDP files (a folder with lines.at, lines.txt,
works.txt, texts.txt and texts.line: Philology-fable's Docs/STORE.md, rules 30 and 31), for
tools/snippets.py, which imports it. Standard library only; nothing of the store is written here.

The documents. A store of the DDP files holds 519 works, one a volume, and in each its documents, one a
text: texts.txt names each text's book as the DDP file's own levels d and c name it (`BGU 1`,
`PCair Zen 1`, `PMich 4—1`), and every line's citation begins with the document's own first level
(`59012 rp`, `2 rp`, `131*`, `90 dupl`), then its side, column or fragment, if any, then its line
(`59012 rp.r,2.7`, `535.r,2.48`, `110 rp.3.90`). A book is a series and its volume: its last word
when that is a number (`1`, `17A`, `4—1`) or a Roman numeral (`PSI Congr XI`), else none (`PCair Good`,
`PAberd`). A document is named by its number: the first level's first word (`59012`, `131*`); the words
after it are the DDbDP's marks (`rp` republished, `dupl` a duplicate copy), and of two texts of one
number in a volume the one without such a mark comes first.

The series. A reference names its series as Perseus wrote LSJ's abbreviation (`pap,P.Cair.Zen.:12:33`,
the print's PCair.Zen. 12.33): the Checklist of Editions (Electronic Edition C, Oates, Willis, Bagnall
and Worp, the DDbDP's own canon, the store's work `ddp9999.ddp003`) writes the same abbreviations.
A series is the store's whose letters, full stops and spaces left out, are the reference's
(`P.Cair.Zen.` is `PCair Zen`); else the one whose letters begin the reference's, where the Checklist
stars that abbreviation as entered in the Databank and only one series of the store begins so
(`P.Cair.Masp.` is `PCair Mas`, `P.Paris` is `PPar`); else none: a series the DDbDP does not hold
(the literary P.Lond.Lit. and BKT, the recipes of P.Holm.).

Another edition. The DDbDP keeps a document's text in its latest edition: under the older number stands
a pointer, one line naming the other edition (`&BGU `1,`1%6WChr `92`, BGU 1 1 = W.Chr. 92; 7,053 of
the store's texts), which is followed to the first of the editions it names that the store holds as a
text, its series by its letters. Where that fails (the Checklist calls the Chrestomathies Chrest.Wilck.
and Chrest.Mitt., the store's files ChrWilck and ChrMitt), or the series is not the store's, or holds
no document of the number, a document whose descriptors name the series and number as an earlier
edition (`PEdg 73` among those of P.Cair.Zen. 59012, `PParis 39r` of UPZ 9, `PLond 1,131,r` of SB 8
9699) is that document, when one document alone names it so; without a pointer, only where the line
cited is found there or no line is cited. Its lines are numbered as the later edition numbers them,
which the lemma check tests.

The numbers LSJ shortens. LSJ cites the Zenon papyri of Cairo and Maspero's Byzantine papyri by their
catalogue numbers less the thousands every one of them shares (PCair.Zen. 12 is 59012, PMasp. 141 is
67141): where a series' documents in the store all have five digits and the number cited is below
every one of them, it is read with the thousands of the series' lowest (59000, 67000) in front, when
that names a document of the series.

The reference. After the series, a reference gives a volume (`volume=5`; the first of three numbers,
`PSI:4:423:6`; a Roman numeral before the number where the print names the series before it, Ostr.Bodl.
i 304), a document (`document=1210`, or a number, a letter joined to it: `14a`, `61b`, `131*`), then a
side (`r`, `v`), a column (a Roman numeral, `110iii90`, `802 iv 8`) or a part (`a` to `h`), and a line.
Two numbers are a document and its line, or a volume and a document; three, a volume, a document and a
line, or a document, a column and a line; a number with a side or column after it is a document, never
a line (`2:34i`). Every reading is tried in every document it names; the first that holds the line
cited is taken, else the first that names a document. A series of one document (P.Rev., Bingen's
edition) reads the numbers as its levels: P.Rev. 38.2 is column 38, line 2. A page (`2 p.64`, `p.10`)
names no document, nor does a reference that begins with a column (`ii 20`, the document the citation
before it named): neither is resolved.

The lines. Within the document the cited line is every line whose citation ends in the line's number,
and of those the ones on the side and in the column the reference names, where it names one (BGU 8.11
is the line 11 of columns 2 and 3: the cut chooses between them by the quotation and the lemma check);
where none ends so, the document's lines, the line cited not among them (P.Cair.Zen. 59012, line 33 of
Edgar's numbering, is the DDbDP's 59012 rp.r,2.7). A side is a mark only in a text that has sides. A
volume is the reference's, else every volume of the series that holds the document, the volumes
published by 1940 (the year of the editions table's row) first, since LSJ could cite no later one; a
number the store writes with its side, part or stroke (P.Tebt. 116r and 116v, UPZ 114/1, P.Lond. 113,1)
is that document. Where two documents hold the line cited (CPR's volumes number afresh), the caller's
score chooses: resolve().

papyri.info. The DDbDP's page of a document is https://papyri.info/ddbdp/<series>;<volume>;<document>,
the series the Checklist's abbreviation in small letters without its final full stop (p.cair.zen, bgu,
o.wilck), the volume in Arabic numerals or empty, the document's number: url().
"""
import collections, os, re

DOC_MARKS = ('rp', 'dupl', 'dpl', 'trpl', 'tripl')
ROMAN = re.compile(r'^(?=[ivxlc])m*(c[md]|d?c{0,3})(x[cl]|l?x{0,3})(i[xv]|v?i{0,3})$')
VOLUME = re.compile(r'^(?:\d+[A-Z]?(?:—\d+)?|[IVXL]+)$')
LSJ_YEAR = 1940
OTHER_NUMBERING = {   # (the key's series, what LSJ prints): a key Perseus made in another edition's numbering
    ('P.Enteux.', 'PMagd.'): "Lefebvre's Magdola numbers, which Guéraud's P.Enteux. renumbered (0 of 43 found)",
}


def letters(s):
    return re.sub(r'[^A-Za-z0-9]', '', s)


def roman(s):
    """A Roman numeral in small letters as a number, or None."""
    s = s.lower()
    if not s or not ROMAN.match(s):
        return None
    v = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
    out = 0
    for k, ch in enumerate(s):
        out += -v[ch] if k + 1 < len(s) and v[s[k + 1]] > v[ch] else v[ch]
    return out


def split_book(book):
    """A book as its series and its volume ('' for none): `PCair Zen 1` is ('PCair Zen', '1')."""
    head, _, last = book.rpartition(' ')
    if head and VOLUME.match(last):
        return head, last
    return book, ''


class Papyri:
    """The DDbDP store's documents by series, volume and number, its Checklist's abbreviations, the
    descriptors' earlier editions, and the series of LSJ's references."""

    def __init__(self, store, N, editions=()):
        self.S = S = store
        path = S.path
        tl = N.u32(os.path.join(path, 'texts.line'))
        with open(os.path.join(path, 'texts.txt'), encoding='utf-8') as f:
            rows = [l.rstrip('\n').split('\t') for l in f]
        self.year, self.edition = {}, {}
        for e in editions:
            if e.get('file', '').startswith('PHI-7/DDP') and e.get('kind') == 'text':
                self.edition.setdefault(e['work'], e)
                if e.get('year', '').isdigit():
                    self.year[e['work']] = int(e['year'])
        self.book_of, self.texts = {}, []
        self.docs = collections.defaultdict(lambda: collections.defaultdict(list))   # (series, volume) -> number -> texts
        self.volumes = collections.defaultdict(list)                                # series -> [(volume, wid)]
        for k, r in enumerate(rows):
            first, last = tl[k], tl[k + 1] - 1
            if last < first:
                continue
            wid = S.work_of(first)
            if wid.startswith('ddp9999'):
                continue
            series, vol = split_book(r[0])
            top = S.raw(first)[0].split('.', 1)[0]
            number, _, marks = top.partition(' ')
            t = {'wid': wid, 'book': r[0], 'series': series, 'volume': vol, 'top': top, 'number': number,
                 'marks': marks, 'desc': r[2], 'first': first, 'last': last}
            self.texts.append(t)
            if wid not in self.book_of:
                self.book_of[wid] = (series, vol)
                self.volumes[series].append((vol, wid))
            self.docs[(series, vol)][number].append(t)
        for v in self.docs.values():
            for ts in v.values():
                ts.sort(key=lambda t: (bool(t['marks'] and any(m in t['marks'].split() for m in DOC_MARKS[1:])), t['first']))
        self.by_letters = collections.defaultdict(list)
        for series in self.volumes:
            self.by_letters[letters(series)].append(series)
        self.checklist = self._checklist()
        self.listed = {letters(a) for a in self.checklist}
        self.earlier = self._earlier()
        self.base = {}
        for series, vols in self.volumes.items():
            nums = [int(n) for v, w in vols for n in self.docs[(series, v)] if n.isdigit()]
            if nums and all(len(str(x)) == 5 for x in nums):
                self.base[series] = min(nums) // 1000 * 1000

    # ---------------------------------------------------------------- the Checklist

    def _checklist(self):
        """The Checklist's abbreviations, each with whether it is starred (entered in the Databank, or
        all its documentary volumes, `(*)`): {abbreviation: starred}; one written with its volume
        (`P.Grenf. I`) is also the series' without it, and a letter with a diaeresis (betacode `u+`) is
        written as the DDP files write it (P.Muench., P.Berl.Moeller)."""
        out = {}
        wid = 'ddp9999.ddp003'
        if wid not in self.S.works:
            return out
        first, last = self.S.works[wid][:2]
        for L in range(first, last + 1):
            t = self.S.raw(L)[1]
            t = t.replace('a+', 'ae').replace('o+', 'oe').replace('u+', 'ue')
            m = re.match(r'^@*(\(\*\)|\*)?([A-Z][A-Za-z0-9.]*(?: [A-Z][A-Za-z0-9.]*)*)(?: \(or [^)]*\))? %6', t)
            if m:
                out.setdefault(m.group(2), bool(m.group(1)))
                bare = re.sub(r' [IVX]+$', '', m.group(2))
                if bare != m.group(2):
                    out[bare] = out.get(bare, False) or bool(m.group(1))
        return out

    def series(self, abbr):
        """The store's series of a reference's abbreviation and how it was found, or (None, why)."""
        got = self.by_letters.get(letters(abbr))
        if got and len(got) == 1:
            return got[0], 'letters'
        if self.checklist.get(abbr):
            lt = letters(abbr)
            pre = [s for k, ss in self.by_letters.items() for s in ss
                   if lt.startswith(k) and len(k) >= 3 and k not in self.listed]
            if len(pre) == 1:
                return pre[0], 'prefix'
        if abbr in self.checklist:
            return None, 'checklist, not entered' if not self.checklist[abbr] else 'checklist, no series'
        return None, 'not in the checklist'

    # ---------------------------------------------------------------- earlier editions

    def _earlier(self):
        """The documents the descriptors name as earlier editions: {(letters of the series, volume or '',
        number): [texts]}, from pieces like `PEdg 73`, `PParis 63,1-7`, `PSI 4,327`, `PThead 54`."""
        out = collections.defaultdict(list)
        for t in self.texts:
            for part in t['desc'].split(' — '):
                for p in re.split(r'[;=+]', part):
                    m = re.match(r'^\s*(?:rp )?([A-Z][A-Za-z]*(?: [A-Z][a-z]+)?) ?(?:(\d+[A-Z]?),)?(\d+)([a-z]?)\b', p)
                    if m and not p.strip().startswith('cf'):
                        for num in {m.group(3) + m.group(4), m.group(3)}:
                            key = (letters(m.group(1)), m.group(2) or '', num)
                            if t not in out[key]:
                                out[key].append(t)
        return out

    # ---------------------------------------------------------------- a reference's readings

    @staticmethod
    def readings(rest, printed=''):
        """The readings of a reference after its series, best first, [(volume or None, number, marks,
        line or None)], marks a tuple of ('side', r or v), ('col', n) and ('part', letter); or why it
        names no document: `page`, `no document`. Two numbers are first a document and a line, then a
        volume and a document; three or more first a volume, a document and a line, then a document,
        its columns and a line; a letter joined to a document's number is a part of it or of its number
        (14a, 61b), a lone v a verso or the fifth column."""
        rest = rest.strip()
        if re.search(r'(?:^|[\s:\d])pp?\.\s?\d|\dp$', rest) or re.search(r'(?:^|\s)pp?\.\s?\d', printed):
            return 'page'
        vol = None
        m = re.match(r'volume=([^:]*):', rest)
        if m:
            vol, rest = m.group(1).strip() or None, rest[m.end():]
        m = re.match(r'document=([^:]*):', rest)
        if m:
            rest = m.group(1).strip() + ':' + rest[m.end():]
        m = re.match(r'\s*([ivx]+)\s?(\d+)\b', rest)
        if m and vol is None and re.match(r'^\S*[A-Za-z]\S*\s+[ivx]+\s?\d', printed):
            vol, rest = str(roman(m.group(1))), rest[m.end(1):]
        items = []                       # ['n', digits] / ['l', letters, joined to what is before] / ['s']
        for t in re.findall(r'\d+|[A-Za-z]+|\*|[^\dA-Za-z*]+', rest):
            if t.isdigit():
                items.append(['n', t])
            elif t == '*':
                if items and items[-1][0] == 'n':
                    items[-1][1] += '*'
            elif t[:1].isalpha():
                items.append(['l', t.lower(), bool(items) and items[-1][0] == 'n'])
            elif items and items[-1][0] != 's':
                items.append(['s'])
        while items and items[-1][0] == 's':
            items.pop()
        if not items or items[0][0] != 'n':
            return 'no document'
        nums, after = [], []             # after[k]: the letter items between number k and the next
        for it in items:
            if it[0] == 'n':
                nums.append(it[1])
                after.append([])
            elif it[0] == 'l':
                after[-1].append(it)

        def marks(groups):
            opts = [()]
            for g in groups:
                lo = g[1]
                if lo == 'v':
                    opts = [o + (('side', 'v'),) for o in opts] + [o + (('col', 5),) for o in opts]
                elif lo == 'r':
                    opts = [o + (('side', 'r'),) for o in opts]
                elif roman(lo) and lo not in ('c', 'd', 'l', 'm'):
                    opts = [o + (('col', roman(lo)),) for o in opts]
                elif len(lo) == 1:
                    opts = [o + (('part', lo),) for o in opts]
                else:
                    return []
            return opts

        def own(k):
            """Number k with the part letter after it (a to h) as its own number (14a, 61b, 782 a), when that
            letter is all that stands between it and the line (not the i of 1088i3, the r of 131r396)."""
            g = after[k]
            if len(g) == 1 and len(g[0][1]) == 1 and g[0][1] in 'abcdefgh':
                return nums[k] + g[0][1]
            return None

        out = []

        def add(v, k, line, extra=()):
            if line is not None and after[-1]:
                return                   # a number with letters after it (34i, 131r) is no line
            groups = after[k] + [x for j in range(k + 1, len(nums) - (1 if line is not None else 0)) for x in after[j]]
            mids = tuple(('col', int(re.sub(r'\D', '', x))) for x in nums[k + 1:len(nums) - (1 if line is not None else 0)])
            for mk in marks(groups):
                out.append((v, nums[k], extra + mids + mk, line))
            o = own(k)
            if o and len(groups) == 1:
                out.append((v, o, extra + mids, line))

        n = len(nums)
        if n == 1:
            add(vol, 0, None)
        elif n == 2:
            add(vol, 0, nums[1])
            if vol is None and not after[0]:
                add(nums[0], 1, None)
        else:
            if vol is None and not after[0]:
                add(nums[0], 1, nums[-1])
            add(vol, 0, nums[-1])
        seen, best = set(), []
        for r in out:
            if r not in seen:
                seen.add(r)
                best.append(r)
        return best

    # ---------------------------------------------------------------- documents and lines

    def volumes_of(self, series, vol):
        """The store's volumes of a series that a reference's volume names (4 is 4, 4—1 and 4—2; 17 is
        17A and 17B), or every volume of the series when it names none: [(volume, wid)]."""
        vols = self.volumes.get(series, [])
        if vol is None:
            return vols
        return [(v, w) for v, w in vols if v == vol or re.match(r'%s(?:—\d+|[A-Z])$' % re.escape(vol), v)]

    def documents(self, series, vol, number):
        """The texts that may be a document, [(text, how)], best first: the number in the volumes the
        reference names, else the number with the series' shared thousands in front (59012 for 12),
        else the texts whose number is the number and a side, a stroke or a comma after it (116r and
        116v, 114/1, 113,1); of several volumes holding it, those published by 1940 first."""
        vols = self.volumes_of(series, vol)
        out = []
        for num, how in ((number, ''), (self._thousands(series, number), 'thousands')):
            if num is None:
                continue
            for v, w in vols:
                for t in self.docs[(series, v)].get(num, ()):
                    out.append((t, how))
            if out:
                break
        if not out:
            for v, w in vols:
                for k, ts in self.docs[(series, v)].items():
                    if k.startswith(number) and re.match(r'(?:[rv]|/\d+|,.*)$', k[len(number):]):
                        out.extend((t, 'part') for t in ts)
        out.sort(key=lambda x: self.year.get(x[0]['wid'], 0) > LSJ_YEAR)
        return out

    def _thousands(self, series, number):
        base = self.base.get(series)
        m = re.match(r'(\d+)(.*)$', number)
        if base is None or not m or len(m.group(1)) > 3:
            return None
        return str(base + int(m.group(1))) + m.group(2)

    def pointer(self, t):
        """Whether a text is the DDbDP's pointer to the edition that holds the document now: one line,
        the document's book and number, `=` and the other's (`&BGU `1,`1%6WChr `92`, BGU 1 1 = W.Chr. 92;
        `&PLond `2,`415,pg `282_`283%6PAbinn `15`)."""
        if t['first'] != t['last']:
            return False
        raw = self.S.raw(t['first'])[1]
        return raw.startswith('&') and '%6' in raw

    def targets(self, t):
        """A pointer's other editions, in its order: [(series as the pointer names it, volume or '',
        number)] (`CPapJud `1,`4;PLond `7,`1947`)."""
        out = []
        for piece in self.S.raw(t['first'])[1].split('%6', 1)[1].split(';'):
            m = re.match(r'\s*&?\s*([A-Za-z]+)\s*`?(\d+[A-Z]?)?(?:\s*,\s*`?(\d+[0-9A-Za-z]*))?', piece)
            if m and m.group(2):
                out.append((m.group(1), m.group(2), m.group(3)) if m.group(3) else (m.group(1), '', m.group(2)))
        return out

    def follow(self, abbr, series, vol, number, t):
        """The text a pointer leads to: the first of its other editions the store holds as a text, the
        series by its letters (`PAbinn`), else the one text whose descriptors name the document."""
        for name, v, num in self.targets(t):
            got = self.by_letters.get(letters(name))
            if not got or len(got) != 1:
                continue
            for x, h in self.documents(got[0], v or None, num):
                if not self.pointer(x):
                    return x
        return self.elsewhere(abbr, series, vol, number, t)

    def elsewhere(self, abbr, series, vol, number, t=None):
        """The one text whose descriptors name the document (the series, by the reference's letters or
        the store's, its volume and its number) as an earlier edition, or None."""
        names = {letters(abbr)} | ({letters(series)} if series else set())
        vols = [vol or ''] + ([split_book(t['book'])[1]] if t else [])
        got = []
        for nm in names:
            for v in vols:
                for x in self.earlier.get((nm, v, number), ()):
                    if x not in got and x is not t:
                        got.append(x)
        return got[0] if len(got) == 1 else None

    def lines(self, t, marks, line):
        """The lines of text t a reference names: those whose citation ends in the line and whose levels
        between the document and the line hold every mark (a side, a column, a part; a side only where
        the text has sides: SB 8 9699, a re-edition of P.Lond. 1 131 recto, has none); where
        none ends so, those holding the marks, and where none does, every line of the text. As
        ([lines], how): `line` (one), `lines` (more: the cut chooses), `marks` or `document` (the line
        cited not among them), `all` (no line cited)."""
        rows = []
        for L in range(t['first'], t['last'] + 1):
            parts = self.S.raw(L)[0].split('.')
            rows.append((L, [x for p in parts[1:-1] for x in re.split(r'[,\s]+', p) if x], parts[-1]))
        sides = any(self._has(mids, ('side', x)) for L, mids, last in rows for x in 'rv')
        marks = [m for m in marks if m[0] != 'side' or sides]
        marked = [L for L, mids, last in rows if all(self._has(mids, m) for m in marks)]
        everything = [L for L, mids, last in rows]
        if line is None:
            return (marked, 'all') if marked else (everything, 'all')
        inside = set(marked)
        held = [L for L, mids, last in rows if last == line and L in inside]
        if held:
            return held, 'line' if len(held) == 1 else 'lines'
        if marks and marked and len(marked) < len(everything):
            return marked, 'marks'
        return everything, 'document'

    @staticmethod
    def _has(mids, mark):
        kind, v = mark
        for x in mids:
            lo = x.lower()
            if kind == 'side' and lo == v:
                return True
            if kind == 'col' and (lo == str(v) or roman(lo) == v):
                return True
            if kind == 'part' and (lo == v or lo == 'fr' + v):
                return True
        return False

    # ---------------------------------------------------------------- a citation

    FOUND = ('line', 'lines')

    def resolve(self, n, printed='', score=None):
        """A bibl's papyrus reference (`Perseus:abo:pap,PSI:5:535:48`) in the store, as a dict: status
        (`line`, `lines`, `marks`, `document`, `all`; else why not), abbr, series, and where found
        wid, text (the document's text: its book, number, first and last line), lines (the lines the
        reference names, for the cut to choose among), place (the store's key: the line's citation where
        one line is named, else the document's first level and the line cited, or the document's alone)
        and how (the steps: `letters`/`prefix` for the series, `one document`, `thousands`, `part`,
        `earlier`, `pointer`); others, the number of other texts that hold the line cited. Where two or
        more texts hold it, score (a function of a text and its lines, as the cut weighs a line: the
        quotation's words, the lexicon's forms) chooses the highest, the first of equals; without it, the
        first."""
        body = n[len('Perseus:abo:pap,'):] if n.startswith('Perseus:abo:pap,') else n
        abbr, _, rest = body.partition(':')
        out = {'abbr': abbr}
        series, how = self.series(abbr)
        out['series'] = series
        if any(abbr == a and printed.startswith(p) for a, p in OTHER_NUMBERING):
            out['status'] = 'another numbering'
            return out
        rs = self.readings(rest, printed)
        if isinstance(rs, str):
            out['status'] = rs
            return out
        cands = []                      # (text, lines, kind, line cited, steps)
        one = self._single(series) if series else None
        if one:
            t, got, kind, line = self._within(one, rest)
            cands.append((t, got, kind, line, [how, 'one document']))
        for vol, num, marks, line in (rs if not one else ()):
            found = self.documents(series, vol, num) if series else []
            for t, h in found:
                steps = [how] + ([h] if h else [])
                if self.pointer(t):
                    x = self.follow(abbr, series, vol, num, t)
                    if x is None:
                        continue
                    t, steps = x, steps + ['pointer']
                got, kind = self.lines(t, marks, line)
                cands.append((t, got, kind, line, steps))
            if not found:
                x = self.elsewhere(abbr, series, vol, num)
                if x is not None and not self.pointer(x):
                    got, kind = self.lines(x, marks, line)
                    if kind in self.FOUND or line is None:
                        cands.append((x, got, kind, line, ['earlier']))
        if not cands:
            out['status'] = ('series: ' + how) if series is None else 'no document'
            return out
        hits = [c for c in cands if c[2] in self.FOUND]
        best = hits[0] if hits else cands[0]
        if score and len({id(c[0]) for c in hits}) > 1:
            best = max(hits, key=lambda c: (score(c[0], c[1]), -hits.index(c)))
        t, got, kind, line, steps = best
        others = {id(c[0]) for c in cands if c[2] in self.FOUND and c[0] is not t}
        out.update(status=kind, wid=t['wid'], text=t, lines=got, how=[x for x in steps if x], others=len(others))
        if kind == 'line':
            out['place'] = self.S.raw(got[0])[0]
        elif line is not None:
            out['place'] = '%s.%s' % (t['top'], line)
        else:
            out['place'] = t['top']
        return out

    def _single(self, series):
        """The one text of a series of one document (P.Rev., Bingen's edition), or None."""
        ts = [t for v, w in self.volumes.get(series, []) for k, x in self.docs[(series, v)].items() for t in x]
        return ts[0] if len(ts) == 1 else None

    def _within(self, t, rest):
        """A reference's numbers as the levels of a series' one document (P.Rev. 38.2 is column 38,
        line 2): (text, lines, how, line)."""
        nums = re.findall(r'\d+', rest)
        line = nums[-1] if len(nums) > 1 else None
        marks = tuple(('col', int(x)) for x in (nums[:-1] if line else nums[:1]))
        got, kind = self.lines(t, marks, line)
        return t, got, kind, line

    def abbreviation(self, series):
        """The Checklist's abbreviation of a series of the store: the one of its letters (a starred one
        first), else the starred one whose letters begin with the series' (PPar is P.Paris), or None (the
        Chrestomathies, which the Checklist calls Chrest.Wilck. and Chrest.Mitt.)."""
        lt = letters(series)
        exact = sorted((not star, a) for a, star in self.checklist.items() if letters(a) == lt)
        if exact:
            return exact[0][1]
        pre = [a for a, star in self.checklist.items() if star and len(lt) >= 3 and letters(a).startswith(lt)]
        return pre[0] if len(pre) == 1 else None

    def url(self, t):
        """A document's page at papyri.info: https://papyri.info/ddbdp/<series>;<volume>;<number>, the
        series the Checklist's abbreviation of the text's own (the edition the lines are from) in small
        letters, its final full stop off, the volume in Arabic numerals or empty (4—1 as 4.1), the
        document's number (empty volume for a series without volumes: p.fay;;33); None where the Checklist gives the series no abbreviation or the document's number has no digit."""
        series, vol = split_book(t['book'])
        a = self.abbreviation(series)
        if a is None or not re.search(r'\d', str(t['number'])):
            return None       # a document named without a number (p.rev;;2nd) has no address here (second review, 1 Nov 2026)
        v = str(roman(vol.lower())) if vol and roman(vol.lower()) else vol
        return 'https://papyri.info/ddbdp/%s;%s;%s' % (a.lower().rstrip('.'), v.lower().replace('—', '.'), t['number'])

    def source(self, wid):
        """A volume as a preview names it: the book as the DDP file names it, its edition as the editions
        table gives it, and the Databank (`BGU 1, ed. ..., Berlin 1895 (DDbDP, PHI 7)`)."""
        series, vol = self.book_of[wid]
        e = self.edition.get(wid, {})
        ed = 'ed. %s' % e['editors'] if e.get('editors') else ''
        imprint = ' '.join(x for x in (e.get('place', ''), e.get('year', '')) if x)
        return '%s (DDbDP, PHI 7)' % ', '.join(x for x in (' '.join(x for x in (series, vol) if x), ed, imprint) if x)

    # ---------------------------------------------------------------- the text

    NOTE = re.compile(r'\{(\d*)(.*?)\}\1')

    def drawn(self, N, wid, L):
        """Line L as (citation, Unicode): the packager's drawing, with the DDbDP's own conventions (its
        Advice to Users): a backquote ends a code, so the numerals after it are text (`17 is 17, which the
        packager's drawing drops); matter in braces is a note (the scribe's spelling {4 }4, a reading
        discarded {6 }6 {7 }7, a number's figures {8 }8, the editor's note {10 }10), left out, the script
        it began in resumed after it; a line that is a note and nothing else (`vestig 3 lin`, traces of
        three lines) is drawn as its note."""
        c, t = self.S.raw(L)
        greek = self.S.works[wid][4] == 'beta-greek'

        def note(m):
            before = t[:m.start()]
            k = max(before.rfind('&'), before.rfind('$'))
            return ('&' if k >= 0 and before[k] == '&' else '$') + '\x00'

        def drawn(x):
            return re.sub(r'\s+', ' ', N.draw(x.replace('`', '\x00'), greek).replace('\x00', '')).strip()
        return c, drawn(self.NOTE.sub(note, t)) or drawn(t)


SIGNS = re.compile('[\\[\\]⟦⟧⟨⟩{}()⸢⸣⸤⸥\u0323]')


def unmarked(t):
    """A drawn papyrus line with the editor's signs taken off (brackets, parentheses, half brackets, the dot
    under a letter read with doubt), so that a word restored, written out or read in part is one word, as the
    forms table and morph spell it: Κορακησιωτικο[ῦ is Κορακησιωτικοῦ, ἡμ(ικάδια) ἡμικάδια, ἐπ̣ε̣λ̣(ευσόμενον)
    ἐπελευσόμενον. For the words the lemma check reads; the line shown keeps them."""
    return SIGNS.sub('', t)
