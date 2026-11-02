#!/usr/bin/env python3
"""The places of LSJ's inscription citations in PHI's Greek Inscriptions, read through a Philology store
of its INS files (a folder with lines.at, lines.txt, works.txt, texts.txt and texts.line: Philology-fable's
Docs/STORE.md, rules 30 and 31), for tools/snippets.py, which imports it. Standard library only;
nothing of the store is written here.

The documents. The store holds 985 works, one a PHI book (`IG II²`, `IG XII,9`, `Syll.³`, `SEG`), and in
each its documents, one a text: texts.txt names each text's book, its number in the book (its reference:
`956`, `1:414` in SEG, `5[2]` the second text PHI keeps under one number), its descriptors, its PHI number,
PHI's note and PHI's "See also" (rules 31); every line's citation begins with the document's reference,
then its face, column or fragment, if any, then its line (`956.col. II.90`, `161.face B.100`, `72.col.
III.20`). A number is a reference less a bracketed count (`5[2]` is 5); of the texts of one number, the
one without a count comes first.

The citations. LSJ cites an inscription by its corpus, then the printed numbers: a volume or fascicle
where the corpus has them, the document's number, a face (A, B) or a column (a small Roman numeral, or the
number before the line in the Gortyn code and the Heraclea tables), and a line (`IG 2(2).956.58`,
`IG 11(2).161 B 100`, `SIG 827 i 9`, `Leg.Gort. 3.20`). The Perseus text writes an edition's raised number
in parentheses (`2(2)` is II²) or flat (`42(1)` is IV²,1; `12.418` in IPE is I² 418), and some 1s as Greek
capital iotas (`ΙΙ(2)` is 11(2), IG XI,2, whose numbers 105 to 289 only Delos's fascicle holds). A label
with no corpus takes the previous label's corpus and volume (labels()).

Where a citation's document is found, in this order:
  - the book the corpus is: IG's volumes and fascicles as PHI names them (`IG II²`, `IG IV²,1`, `IG IX,1²`,
    `IG XII,9`; IG XI's fascicles 2 and 4 share one numbering, so `IG 11.1300` is XI,4's), the Délos, Olympia,
    SEG, Delphi (FD III), Pergamon, TAM, MAMA, IosPE I², Wünsch's Attic curse tablets (IG III App.), and the
    books PHI keeps under the corpus's own name (`Syll.³`, `OGIS`, `CIG`, `SGDI II`, `IGR I`); the Gortyn
    code is IC IV 72, its columns I to XII, the Heraclea tables IG XIV 645, its tables I and II;
  - else the text whose descriptors, "See also" or note name the corpus and the number as PHI writes
    them (`SIG(3) 306`, `Syll.³ 205`, `OGIS 2.720`, `IGR IV 1076`, `SEG 4, 470`, `IG I² 32` among the texts
    of IG I³, `IG III,2 3544` among those of IG II²), a piece after `cf.` excepted: one text alone where the
    line cited is found there or no line is cited (another edition may number its lines otherwise); of two
    or more (PHI keeps one stone under two books, McCabe's and the corpus's), those that hold the line
    cited, the caller's score choosing; a journal (`BCH 11.161`) by its volume, or year, and page, the one
    text PHI's references place on that page;
  - a text of one line that sends the reader to another edition (`See IG I(3).404`) is that edition's
    text where the store holds it, else none.
Editio maior IG I to III, and every number PHI names nowhere, stay unresolved: no concordance is here.

The lines. Within the document the cited line is every line whose citation ends in the line's number, and
of those the ones on the face and in the column the citation names, where it names one; where none ends
so, the document's lines (the line cited not among them: another edition's numbering); a citation with no
line is its document. Where several lines or documents hold it, the caller's score chooses: resolve().

The page. A document's page at PHI is https://epigraphy.packhum.org/text/<its PHI number>: url().
"""
import collections, os, re

ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI',
         12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV', 16: 'XVI'}
ARABIC = {v: k for k, v in ROMAN.items()}
NUMBER = r'(\d+[a-z]?)(?![\da-z])'

# LSJ's corpora: its title -> the store's books, in order, and the key PHI's cross references name it by
BOOKS = {
    'SIG': (('Syll.³',), 'Syll.³'), 'OGI': (('OGIS',), 'OGIS'), 'CIG': (('CIG',), 'CIG'),
    'GDI': (('SGDI II',), 'SGDI'), 'Epigr.Gr.': (('Kaibel, EG',), 'Kaibel'), 'Schwyzer': ((), 'DGE'),
    'Michel': ((), 'Michel'), 'LW': ((), 'LW'), 'Inscr.Cos': ((), 'Paton-Hicks'), 'Inscr.Magn.': ((), 'IMagn'),
    'Inscr.Prien.': ((), 'IvPriene'), 'Inscr.Délos': (('ID',), 'ID'), 'Inscr.Olymp.': (('IvO',), 'IvO'),
    'BMus.Inscr.': (('GIBM II', 'GIBM IV,2'), 'GIBM'), 'Inscr.Perg.': (('IvP I', 'IvP II'), 'IvP'),
    'Tab.Defix.': (('IG III App.',), None), 'Tab.Defix.Aud.': ((), 'DT'),
}
VOLUMED = {   # cited volume.number: the store's book of a volume, and the key PHI names the volume by
    'IGRom.': ({1: ('IGR I', 'IGR I,5'), 3: ('IGR III',), 4: ('IGR IV',)}, 'IGR'),
    'MAMA': ({v: ('MAMA %s' % ROMAN[v],) for v in range(1, 11)}, 'MAMA'),
    'TAM': ({v: ('TAM %s' % ROMAN[v],) for v in range(1, 4)}, 'TAM'),
    'CIL': ({3: ('CIL III',)}, 'CIL'),
}

# How PHI names a corpus in a text's descriptors, See also and note: a key, then a volume where the
# corpus restarts its numbers by volume, then the number
XREF = (
    ('Syll.³', r'(?:Syll|SIG)\.?\s?(?:\(3\)|³|3)\.?\s?(?:[1-4]\.(?=\d))?', False),
    ('OGIS', r'OGIS?\s?(?:(?:II?|[12])[.,]\s?(?=\d))?', False),
    ('CIG', r'CIG\s?(?:(?:I{1,3}|IV|[1-4])[.,]\s?(?=\d))?', False),
    ('SGDI', r'S?GDI\s?(?:(?:I{1,3}|IV|[1-4])(?:,\s?\d)?\s(?=\d))?', False),
    ('Kaibel', r'Kaibel,?\s?(?:Epigr\.?\s?[Gg]r\.?|EG)?\s?', False),
    ('DGE', r'(?:Schwyzer,?\s?(?:DGEEP|DGE)?|DGE(?:EP)?)\s?(?:\(1923\)\s?)?', False),
    ('Michel', r'Michel(?:,\s?Recueil)?\s?', False),
    ('LW', r'(?:LW|Le\s?Bas[-–]Wadd(?:ington)?\.?)\s?', False),
    ('Paton-Hicks', r'Paton[-–]Hicks\s?(?:\(1891\)\s?)?', False),
    ('IMagn', r'I\.?\s?Magn\.?\s?', False),
    ('IvPriene', r'(?:IvPriene|I\.?\s?Priene(?![²\d]))\s?(?:\(1906\)\s?)?', False),
    ('DT', r'(?:Defix\.\s?Tab\.|Audollent,?\s?(?:DT|Defix\.?\s?Tab\.?)?|DT)\s?', False),
    ('GIBM', r'GIBM\s?(?:(?:I{1,3}|IV|[1-4])(?:[.,]\s?[12])?(?:\s?\(\d{4}\))?[.,]?\s?(?:Nr\.\s?)?(?=\d))?', False),
    ('IvP', r'IvP\s?(?:I{1,3}\s)?', False),
    ('IvO', r'IvO\s?', False),
    ('ID', r'ID\s?', False),
    ('IGR', r'IGRR?\s?(I{1,3}|IV|[134])(?:[.,]\s?|\s)', True),
    ('MAMA', r'MAMA\s?(I{1,3}|IV|VI{0,3}|IX|X|\d+)(?:[.,]\s?|\s)', True),
    ('TAM', r'TAM\s?(I{1,3}|[123])(?:,\s?\d)?(?:[.,]\s?|\s)', True),
    ('CIL', r'CIL\s?(I{1,3}|IV|VI{0,3}|IX|X{1,3}|XIV|\d+)(?:[.,]\s?|\s)', True),
    ('IosPE', r'IosPE\s?(I²|I{1,2}|IV)\s', True),
    ('Milet', r'Milet\s?I,?\s?(\d)[.,]?\s?', True),
    ('SEG', r'SEG\s?(\d+)(?:[.,:]\s?)', True),
    ('FD III', r'FD\s?(?:III|3)[,.:\s]\s?(\d)[.,:]\s?', True),
    ('IG', r'IG\s?(I²|I³|II²|II|III|I|IV²,\s?1|IV|V,\s?[12]|VII|IX,\s?1²|IX,\s?[12]|XI,\s?[24]|XII,\s?\d|XII\sSuppl\.|XIV)(?:,\s?[123])?\s', True),
)
XREF_RE = [(k, re.compile(r'(?<![A-Za-z.])' + p + NUMBER), v) for k, p, v in XREF]

# The journals, cited by volume (or year) and page: LSJ's title -> how PHI names it, and whether by year
JOURNALS = {
    'BCH': (r'BCH', False), 'Ath.Mitt.': (r'(?:AM|MDAI\s?\(A\)|Ath\.\s?Mitt\.|AthMitt)', False), 'JHS': (r'JHS', False),
    'Hermes': (r'Hermes', False), 'Rev.Phil.': (r'(?:RPh|Rev\.\s?Phil\.)(?:\s?\(\d\))?', False), 'AJA': (r'AJA', False),
    'BSA': (r'A?BSA', False), 'JRS': (r'JRS', False), 'Klio': (r'Klio', False), 'Hesperia': (r'Hesperia', False),
    'Rev.Ét.Gr.': (r'(?:REG|Rev\.\s?[ÉE]t\.\s?[Gg]r\.)', False), 'Jahresh.': (r'(?:J[ÖO]AI|ÖJh|Jahresh\.)', False),
    'Berl.Sitzb.': (r'(?:SBBerlin|Sber\.?\s?Berlin|SB\s?Berlin|Sitzb\.?\s?Berl(?:in)?\.?)', True),
    'Ἀρχ.Ἐφ.': (r'(?:ArchEph|Arch\.\s?Eph\.|AEph)', True),
    'Abh.Berl.Akad.': (r'(?:AbhBerlin|Abh\.\s?Berlin|Abh\.\s?Berl\.\s?Akad\.)', True),
}
BY_VOLUME = r'\s?(\d+)(?:\.\d{4}|\s?\(\d{4}(?:[/-]\d+)?\))?[.,]?\s?(?:p\.\s?)?(\d+)(?:\s?[-–]\s?(\d+))?(?!\d)'
BY_YEAR = r'\s?(?:\((\d{4})(?:[.,](\d))?\)|(\d{4}))[.,:]?\s?(?:p\.\s?)?(\d+)(?:\s?[-–]\s?(\d+))?(?!\d)'
JOURNAL_RE = [(k, re.compile(r'(?<![A-Za-z.])' + p + (BY_YEAR if y else BY_VOLUME)), y) for k, (p, y) in JOURNALS.items()]
KNOWN = set(BOOKS) | set(VOLUMED) | set(JOURNALS) | {'IG', 'Supp.Epigr.', 'Leg.Gort.', 'Tab.Heracl.', 'IPE', 'Delph.', 'Milet.'}


def number_of(ref):
    """A reference's number: less a bracketed count (`5[2]` is 5) and PHI's marks after a space (`1957b (Add)`)."""
    return re.sub(r'\[\d+\]$', '', ref).split(' (')[0].strip()


def split_cit(c, ref):
    """A line's citation as its levels after the document and its line: `956.col. II.90` is (['col. II'], '90')."""
    rest = c[len(ref) + 1:] if c.startswith(ref + '.') else c.partition('.')[2]
    parts = re.split(r'\.(?! )', rest)
    return parts[:-1], parts[-1]


class Inscriptions:
    """The Greek Inscriptions store's documents by book and number, and by the corpora PHI's own references name."""

    def __init__(self, store, N, editions=()):
        self.S = S = store
        path = S.path
        tl = N.u32(os.path.join(path, 'texts.line'))
        with open(os.path.join(path, 'texts.txt'), encoding='utf-8') as f:
            rows = [l.rstrip('\n').split('\t') for l in f]
        self.edition = {}
        for e in editions:
            if e.get('file', '').startswith('PHI-7/INS') and e.get('kind') == 'text':
                self.edition.setdefault(e['work'], e)
        self.book_of, self.texts = {}, []
        self.docs = collections.defaultdict(lambda: collections.defaultdict(list))   # book -> number -> texts
        for k, r in enumerate(rows):
            first, last = tl[k], tl[k + 1] - 1
            if last < first or not r[0]:
                continue
            r = (r + [''] * 6)[:6]
            wid = S.work_of(first)
            t = {'wid': wid, 'book': r[0], 'ref': r[1], 'number': number_of(r[1]), 'desc': r[2], 'phi': r[3],
                 'note': r[4], 'xrefs': r[5], 'first': first, 'last': last}
            self.texts.append(t)
            self.book_of.setdefault(wid, r[0])
            self.docs[r[0]][t['number']].append(t)
            lead = re.match(r'(\d+[a-z]?)(?=[,\s]|$)', t['number'])
            if lead and lead.group(1) != t['number']:
                self.docs[r[0]]['part ' + lead.group(1)].append(t)
        for v in self.docs.values():
            for ts in v.values():
                ts.sort(key=lambda t: (t['ref'] != t['number'], t['first']))
        self.pointers = self._pointers(N)
        self.named = self._named()

    def _pointers(self, N):
        """PHI's pointers: a text of one line that sends the reader to another edition (`See IG I(3).404`,
        `See V. Ch. Petrakos, Hoi epigraphes tou Oropou, no. 129`), {id(text): the text it names, or None}: the
        book whose name begins the pointer (an edition's number in parentheses raised: I(3) is I³), then its
        number, where the store holds that document."""
        books = sorted(self.docs, key=len, reverse=True)
        out = {}
        for t in self.texts:
            if t['last'] != t['first']:
                continue
            said = N.draw(self.S.raw(t['first'])[1], True)
            m = re.match(r'^\W*(?:See|Cf\.|cf\.|Vide|Siehe)\s+(.*)$', said)
            if not m:
                continue
            target = re.sub(r'\((\d)\)', lambda x: {'2': '²', '3': '³'}.get(x.group(1), x.group(0)), m.group(1))
            got = None
            for b in books:
                if target.startswith(b) and re.match(r'^[\s.,]+(\d+[a-z]?)(?![\da-z])', target[len(b):]):
                    n = re.match(r'^[\s.,]+(\d+[a-z]?)', target[len(b):]).group(1)
                    got = next((x for x in self.docs[b].get(n, ()) if x['last'] > x['first'] or x['first'] == x['last'] and id(x) not in out), None)
                    break
            out[id(t)] = got
        return out

    def real(self, ts):
        """Texts with each pointer replaced by the text it names, one that names none left out, in order."""
        out = []
        for t in ts:
            t = self.pointers.get(id(t), t) if id(t) in self.pointers else t
            if t is not None and t not in out:
                out.append(t)
        return out

    # ---------------------------------------------------------------- PHI's cross references

    def _named(self):
        """The texts PHI's descriptors, See also and note name by another corpus's number: {(key, volume or
        '', number): [texts]}; a piece after `cf.` names a text compared, not this one."""
        out = collections.defaultdict(list)
        for t in self.texts:
            for piece in re.split(r' — |\||;', '%s — %s — %s' % (t['desc'], t['xrefs'], t['note'])):
                for key, rx, volumed in XREF_RE:
                    for m in rx.finditer(piece):
                        if re.search(r'\bcf\.\s*$', piece[:m.start()]):
                            continue
                        vol = self._volume(key, m.group(1)) if volumed else ''
                        k = (key, vol, m.group(m.lastindex))
                        if t not in out[k]:
                            out[k].append(t)
            for piece in re.split(r' — |\||;', '%s %s — %s — %s' % (t['book'], t['ref'], t['desc'], t['xrefs'])):
                for key, rx, by_year in JOURNAL_RE:      # a journal's volume (or year) and pages; a book of one, its own
                    for m in rx.finditer(piece):
                        if re.search(r'\bcf\.\s*$', piece[:m.start()]):
                            continue
                        if by_year:
                            vol = (m.group(1) + ('.' + m.group(2) if m.group(2) else '')) if m.group(1) else m.group(3)
                            a, b = m.group(4), m.group(5)
                        else:
                            vol, a, b = m.group(1), m.group(2), m.group(3)
                        lo = int(a)
                        hi = int(b) if b else lo
                        if b and hi < lo:            # 112-13 is 112 to 113
                            hi = int(a[:len(a) - len(b)] + b)
                        for page in range(lo, (hi if 0 <= hi - lo <= 30 else lo) + 1):
                            k = (key, vol, str(page))
                            if t not in out[k]:
                                out[k].append(t)
        return out

    @staticmethod
    def _volume(key, v):
        v = re.sub(r'\s+(?!Suppl)', '', v)
        if key == 'IG':
            return 'IG ' + v
        if key in ('IosPE', 'SEG', 'Milet', 'FD III'):
            return v
        return str(ARABIC.get(v, v))

    def elsewhere(self, key, vol, number):
        """The texts PHI names by a corpus's number: [texts] (the caller takes one alone)."""
        return self.real(self.named.get((key, vol, number), ()))

    # ---------------------------------------------------------------- a label's printed numbers

    @staticmethod
    def plain(s):
        """A label's printed numbers as digits: a Greek capital iota among them is a 1 (`ΙΙ(2)` is 11(2))."""
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r'(?:(?<=^)|(?<=[\s(.\d]))Ι+(?=[\s(.\dΙ]|$)', lambda m: '1' * len(m.group()), s)
        return s

    def ig_volume(self, rest):
        """IG's volume at the start of a citation: (the store's books, PHI's key for the volume, the rest) or
        None. `2(2)` is II², `42(1)` IV²,1, `92(1)` IX,1², `12(9)` XII,9, `11` XI (its fascicles 2 and 4
        share a numbering), `1(2)` I² (IG I³ holds most of it), `3` and `2` and `1` the editio maior."""
        m = re.match(r'^(\d+)\s?(?:\((\d+)\))?(?:\s?\((\d+)\))?\s?(Suppl\.)?[.\s]\s?(?=\d)', rest)
        if not m:
            return None
        vol, p1, p2, sup = m.group(1), m.group(2), m.group(3), m.group(4)
        after = rest[m.end():]
        flat = re.fullmatch(r'([49])2', vol) if p1 else re.fullmatch(r'(2)2', vol)
        if flat:                          # a raised 2 printed flat: 42(1) is IV²,1, 22 II²
            vol, p1, p2 = flat.group(1), '2', p1
        v = int(vol)
        if v not in ROMAN or v > 14:
            return None
        R = ROMAN[v]
        if v in (1, 2, 3) and p1 == '2' and not p2:
            name = 'IG %s²' % R
        elif v == 4 and p1 == '2' and p2:
            name = 'IG IV²,%s' % p2
        elif v == 9 and p1 == '2' and p2 == '1':
            name = 'IG IX,1²'
        elif p1 and not p2:
            name = 'IG %s,%s' % (R, p1)
        elif not p1:
            name = 'IG %s' % R + (' Suppl.' if sup else '')
        else:
            return None
        if name == 'IG XII':              # XII has no volume without a fascicle: a raised 2 printed flat, I²
            name = 'IG I²'
        books = ['IG XI,2', 'IG XI,4'] if name == 'IG XI' else [name]
        if name == 'IG IX,1²':            # its fascicle 1 (Aetolia, 1932), the store's references 1:N
            after = re.sub(r'^(\d+)', r'1:\1', after)
        return books, name, after

    @staticmethod
    def readings(rest):
        """A citation's numbers after its corpus and volume as readings, best first: [(number, marks, line)],
        marks a tuple of ('face', A), ('col', n) and ('part', a). `161 B 100` is 161, face B, line 100; `827 i 9`
        827, column i, line 9; `27a70` 27a line 70 or 27 part a line 70; `1.20` 1 line 20; `1145 iii 15`."""
        rest = rest.strip().rstrip('.,;')
        m = re.match(r'^(\d+)([a-z]?)(?:\s?([A-D](?:[a-z]|\s?[ivx]+)?)\s|\s?([ivx]+)\s|\s?([A-D])(?=\d)|([a-z]))?[.\s]?\s?(\d+)?$', rest)
        if not m:
            m2 = re.match(r'^(\d+)([a-z]?)\b', rest)
            return [(m2.group(1) + m2.group(2), (), None)] + ([(m2.group(1), (('part', m2.group(2)),), None)] if m2.group(2) else []) if m2 else []
        num, suf, face, col, face2, joined, line = m.groups()
        marks = ()
        if face or face2:
            f = (face or face2).replace(' ', '')
            fm = re.match(r'^([A-D])([a-z]?)([ivx]*)$', f)
            marks = (('face', fm.group(1)),) + ((('part', fm.group(2)),) if fm.group(2) else ()) + ((('col', small(fm.group(3))),) if fm.group(3) else ())
        elif col:
            marks = (('col', small(col)),)
        out = []
        if joined:                         # 27a70: a part joined to the number, or its column (322i10)
            if small(joined):
                out.append((num, (('col', small(joined)),), line))
            out += [(num + joined, (), line), (num, (('part', joined),), line)]
        elif suf:
            out += [(num + suf, marks, line), (num, marks + (('part', suf),), line)]
        else:
            out.append((num, marks, line))
        return out

    # ---------------------------------------------------------------- documents and lines

    def documents(self, books, number):
        """The texts of a number in the books named, in order: the number itself, else its texts in parts
        (`56,A`, `400,Ib`)."""
        out = []
        for b in books:
            out += self.docs.get(b, {}).get(number, [])
        if not out:
            for b in books:
                out += self.docs.get(b, {}).get('part ' + number, [])
        return self.real(out)

    def lines(self, t, marks, line):
        """The lines of text t a citation names: those whose citation ends in the line and whose levels hold
        every mark (a face, a column, a part); where none ends so, those holding the marks, and where none
        does, every line of the text. As ([lines], how): `line` (one), `lines` (more: the cut chooses),
        `marks` or `document` (the line cited not among them), `all` (no line cited)."""
        rows = []
        for L in range(t['first'], t['last'] + 1):
            mids, last = split_cit(self.S.raw(L)[0], t['ref'])
            rows.append((L, mids, last))
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
            w = re.sub(r'^(?:col|face|frg|fr|side|tab|fasc)\.?\s*', '', x.strip(), flags=re.I).split(' ')[0]
            if kind == 'face' and w.upper() == v.upper():
                return True
            if kind == 'col' and (w == str(v) or ARABIC.get(w.upper()) == v):
                return True
            if kind == 'part' and w.lower() == v:
                return True
        return False

    # ---------------------------------------------------------------- a citation

    FOUND = ('line', 'lines')

    def where(self, corpus, rest):
        """A citation's candidate places, best first: [(books, key, volume, readings)], or why none: `no number`,
        `not a corpus here`, `volume not in the store`."""
        rest = re.sub(r'\s?No\.\s?', '.', re.sub(r'^\(add\.\)\s?', '', self.plain(rest))).lstrip('.')
        if corpus == 'IG':
            v = self.ig_volume(rest)
            if not v:
                return 'no volume' if re.match(r'^\d', rest) else 'no number'
            books, key, after = v
            return [(books, 'IG', key, self.readings(after))]
        if corpus == 'Leg.Gort.':
            m = re.match(r'^(\d+)\.(\d+)$', rest)
            return [(['IC IV'], None, None, [('72', (('col', int(m.group(1))),), m.group(2))])] if m else 'no number'
        if corpus == 'Tab.Heracl.':
            m = re.match(r'^(\d)\.(\d+)$', rest)
            return [(['IG XIV'], None, None, [('645', (('col', int(m.group(1))),), m.group(2))])] if m else 'no number'
        if corpus == 'Supp.Epigr.':
            m = re.match(r'^(\d+)\.(.+)$', rest)
            if not m:
                return 'no number'
            return [(['SEG'], 'SEG', m.group(1), [('%s:%s' % (m.group(1), n), mk, l) for n, mk, l in self.readings(m.group(2))])]
        if corpus == 'Delph.':
            m = re.match(r'^3\s?\((\d)\)\.?\s?(.+)$', rest)
            if not m:
                return 'no number'
            return [(['FD III'], 'FD III', m.group(1), [('%s:%s' % (m.group(1), n), mk, l) for n, mk, l in self.readings(m.group(2))])]
        if corpus == 'IPE':
            m = re.match(r'^(1)(?:\((2)\)|(2))\.(.+)$', rest) or re.match(r'^([124])\.(.+)$', rest)
            if not m:
                return 'no number'
            if m.lastindex == 4:
                return [(['IosPE I²'], 'IosPE', 'I²', self.readings(m.group(4)))]
            return [([], 'IosPE', ROMAN[int(m.group(1))], self.readings(m.group(2)))]
        if corpus == 'Milet.':
            m = re.match(r'^(?:1\s?\((\d)\)|(\d))\.(.+)$', rest)
            if not m:
                return 'no number'
            return [([], 'Milet', m.group(1) or m.group(2), self.readings(m.group(3)))]
        if corpus in VOLUMED:
            vols, key = VOLUMED[corpus]
            m = re.match(r'^(\d+)(?:\s?\(\d\))?\.(.+)$', rest)
            if not m:
                return 'no number'
            v = int(m.group(1))
            return [(list(vols.get(v, ())), key, str(v), self.readings(m.group(2)))]
        if corpus in JOURNALS:                # a volume (or year) and a page, PHI's references alone
            m = re.match(r'^(\d{4})\s?\((\d)\)\.(\d+)', rest) or re.match(r'^(\d+)()\.(\d+)', rest)
            if not m:
                return 'no number'
            vol = m.group(1) + ('.' + m.group(2) if m.group(2) else '')
            return [([], corpus, vol, [(m.group(3), (), None)])]
        if corpus in BOOKS:
            books, key = BOOKS[corpus]
            if corpus == 'Tab.Defix.Aud.' or rest.startswith('Aud.'):
                books, key, rest = (), 'DT', re.sub(r'^Aud\.\s?', '', rest)
            rs = self.readings(rest)
            return [(list(books), key, '', rs)] if rs else 'no number'
        return 'not a corpus here'

    def resolve(self, corpus, rest, score=None):
        """A label's citation (its corpus and its printed numbers) in the store, as a dict: status (`line`,
        `lines`, `marks`, `document`, `all`; else why not), and where found wid, text (its book, number, first
        and last line), lines (the lines the citation names, for the cut to choose among), place (the line's
        citation where one line is named, else the document's reference and the line cited, or the reference
        alone), how (`book` or `named`: the corpus's own book, or PHI's reference to the corpus) and others,
        the number of other texts that hold the line cited. Where two or more texts hold it, score (a
        function of a text and its lines, as the cut weighs a line) chooses the highest, the first of equals."""
        out = {'corpus': corpus}
        got = self.where(corpus, rest)
        if isinstance(got, str):
            out['status'] = got
            return out
        cands, why = [], 'no document'
        for books, key, vol, rs in got:
            if not rs:
                why = 'no number'
            for number, marks, line in rs:
                for t in self.documents(books, number):
                    ls, kind = self.lines(t, marks, line)
                    cands.append((t, ls, kind, line, 'book'))
        if not any(c[2] in self.FOUND for c in cands):
            seen = {id(c[0]) for c in cands}
            for books, key, vol, rs in got:
                for number, marks, line in (rs if key else ()):
                    named = [t for t in self.elsewhere(key, vol or '', number.split(':')[-1]) if id(t) not in seen]   # SEG 4:449 as SEG 4, 449
                    for t in named:          # one text alone, its line found or none cited; of more, those holding the line
                        ls, kind = self.lines(t, marks, line)
                        if kind in self.FOUND or (len(named) == 1 and line is None):
                            cands.append((t, ls, kind, line, 'named' if len(named) == 1 else 'named, the line held'))
                            seen.add(id(t))
                    if len(named) > 1 and not any(c[2] in self.FOUND for c in cands):
                        why = 'two or more texts name it'
                    elif len(named) == 1 and not cands:
                        why = 'named, the line cited not there'
        if not cands:
            out['status'] = why
            return out
        hits = [c for c in cands if c[2] in self.FOUND]
        best = hits[0] if hits else cands[0]
        if score and len({id(c[0]) for c in hits}) > 1:
            best = max(hits, key=lambda c: (score(c[0], c[1]), -hits.index(c)))
        t, ls, kind, line, how = best
        others = {id(c[0]) for c in hits if c[0] is not t}
        out.update(status=kind, wid=t['wid'], text=t, lines=ls, how=[how], others=len(others))
        if kind == 'line':
            out['place'] = self.S.raw(ls[0])[0]
        elif line is not None:
            out['place'] = '%s.%s' % (t['ref'], line)
        else:
            out['place'] = t['ref']
        return out

    # ---------------------------------------------------------------- the entry's labels

    def labels(self, xb, spans):
        """The inscription citations among an entry's labels: {its start: (corpus, printed numbers)}. spans are
        the entry's bibls in order, (start, the element's bytes). A label's corpus is its <title>'s, where it
        is one of LSJ's corpora here; a label with none whose text begins with a number, or `ib.` and a
        number, takes the previous label's corpus and volume, where that bibl is the one before it and
        nothing but punctuation, `cf.`, `al.` and a parenthesis (a place, a date) stands between them, or
        anything after `ib.`; the volume is IG's and the corpora's that number by volume, unless it prints
        its own (`12(1).694`)."""
        out, prev, prev_end = {}, None, None
        for b, el in spans:
            s = el.decode('utf-8')
            head = re.match(r'<bibl\b([^>]*)>(.*)</bibl>$', s, re.S)
            attrs, inner = head.group(1), head.group(2)
            if ' resp="' not in attrs or ' n="' in attrs:
                prev, prev_end = None, b + len(el)
                continue
            tm = re.match(r'\s*<title>([^<]*)</title>\s*(.*)$', inner, re.S)
            text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', tm.group(2) if tm else inner)).strip()
            got = None
            if tm and tm.group(1).strip() in KNOWN:
                got = (tm.group(1).strip(), text)
            elif not tm and prev:
                gap = re.sub(r'<[^>]+>', '', xb[prev_end:b].decode('utf-8'))
                ib = re.match(r'^ib\.\s?(?=[\dΙ])', text)
                quiet = not re.search(r'[^\W\d_]', re.sub(r'\([^()]*\)|\b(?:cf|al|ib)\.|\band\b', '', gap))
                if ib or (quiet and re.match(r'^[\dΙ]', text)):
                    body = self.plain(text[ib.end():] if ib else text)
                    got = (prev[0], self.inherit(prev, body))
            out_b = got
            if got:
                out[b] = got
            prev, prev_end = (out_b if out_b else None), b + len(el)
        return out

    def inherit(self, prev, body):
        """A continuation's numbers read with the previous label's: one number after a citation that names a
        line is another line of its document (`Leg.Gort. 3.40, 44`, `IG 2(2).1672.200, 205`); else, where the
        corpus numbers by volume and the continuation prints none of its own, the previous label's volume in
        front (`IG 2(2).956.58, 1006.12`; IG's own is a volume in parentheses or a first number up to 14)."""
        corpus, before = prev
        before = self.plain(before)
        got = self.where(corpus, before)
        lined = not isinstance(got, str) and bool(got[0][3]) and got[0][3][0][2] is not None
        if re.fullmatch(r'\d+', body) and lined and re.search(r'\d$', before):
            return re.sub(r'\d+$', body, before)
        if corpus == 'IG':
            own = re.match(r'^\d+\s?\(\d+\)', body) or (
                re.match(r'^(\d+)\.\d', body) and int(re.match(r'\d+', body).group()) <= 14)
            vol = re.match(r'^(\d+\s?(?:\(\d+\))?(?:\s?\(\d+\))?)[.\s]', before)
            return body if own or not vol else '%s.%s' % (vol.group(1), body)
        if corpus in VOLUMED or corpus in ('Supp.Epigr.', 'IPE', 'Milet.', 'Delph.'):
            vol = re.match(r'^(\d+(?:\s?\(\d\))?)\.', before)
            n = len(re.findall(r'\d+', body))
            return body if not vol or n >= 3 or re.match(r'^\d+\s?\(\d\)', body) else '%s.%s' % (vol.group(1), body)
        return body

    # ---------------------------------------------------------------- where a preview links and what it names

    def url(self, t):
        """A document's page at PHI: https://epigraphy.packhum.org/text/<its PHI number>, or None without one."""
        return 'https://epigraphy.packhum.org/text/%s' % t['phi'] if t['phi'].isdigit() else None

    def source(self, wid):
        """A book as a preview names it: PHI's name, its edition as the editions table gives it, and the
        collection (`IG II², ed. Johannes Kirchner, Berlin 1913 (PHI Greek Inscriptions)`)."""
        e = self.edition.get(wid, {})
        ed = 'ed. %s' % e['editors'] if e.get('editors') else ''
        imprint = ' '.join(x for x in (e.get('place', ''), e.get('year', '')) if x)
        return '%s (PHI Greek Inscriptions)' % ', '.join(x for x in (self.book_of[wid], ed, imprint) if x)


def small(s):
    """A small Roman numeral as a number, or None."""
    s = s.lower()
    if not s or not re.fullmatch(r'[ivxl]+', s):
        return None
    v = {'i': 1, 'v': 5, 'x': 10, 'l': 50}
    out = 0
    for k, ch in enumerate(s):
        out += -v[ch] if k + 1 < len(s) and v[s[k + 1]] > v[ch] else v[ch]
    return out
