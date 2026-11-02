#!/usr/bin/env python3
"""Mark the citations the dictionary prints outside its <bibl>s, by rule: only tags are added, the
text is never touched.

    python3 -I tools/mark_citations.py --spans <spans.tsv> --items <items.jsonl> --out <dir> [--write]
    python3 -I tools/mark_citations.py --answers <marks-c.tsv> --items <items.jsonl> --key <key.tsv> --out <dir> [--write]
    python3 -I tools/mark_citations.py --names --spans <spans.tsv> --items <items.jsonl> --out <dir> [--write]
    python3 -I tools/mark_citations.py --table tools/addresses.tsv --philology <Philology-fable> --tlg <TLG-E store> --out <dir> [--write]
    python3 -I tools/mark_citations.py --check <the files before, a directory> [--moves corrections/markup.tsv]

What is marked (each new citation <bibl resp="lsjai-20261031">, with n="Perseus:abo:..." where the
rule makes one, else no n: the citation is sure, its address is not yet known):

  the sure kinds of the census of 31 Oct 2026 (the census's records,
  unmarked.py and compose.py, run again here on the files as they are):
    A1  an <author> outside every bibl, up to three title-like tokens, a number (Phot. p.3)
    T1  a <title> outside every bibl, likewise (IG 2(2).956.58, POxy. 2008.1)
    C   a bare number after a bibl, set off by a comma (Il. 14.271, 300: the 300)
    C2  the same after a new mark
    IB  ib. or l.c. with a number (ib. 6.14)
  the spans the spans night of 31 Oct 2026 ruled citations (its spans.tsv; the package's items.jsonl
  for the span's text): an author abbreviation and a number in plain text (A2), a dotted number
  with no name before it (DOT), an author or title standing with no number after it (NAME). A NAME
  mark is the name alone, or the name with what follows it when that is the rest of the reader's
  reference token for token (s.v. τμήδην; ΙΙ(2).161 ‹A› 87 for IG 11(2).161 A 87).
  Then, on the new marks only: the rest of a number the census's pattern stops short of (IG
  11.203A32, Aristid. 1.460J, a face letter in <hi>), a fascicle after a space (IG 12 (5).817, IG 9
  (I).694), a No. (Milet. 3 No.150.97), a column and line (Chr. 96 iii 5), a title right after the
  mark with no comma between (a face letter, Def. 2, Fr. 66: Euc. 1 Def. 23), an edition's number
  before a dotted number the night ruled (SIG 2 588.17), and a Ps.- before the name, inside the
  bibl as the dictionary's own have it; and a second iteration for the comma-numbers that stand
  after a new mark once it is a bibl (C). An extension that would cross an element is not made;
  a mark whose number then still runs on is not made either (residue).

The n, from the files' own table (compose.py's rule, learned from the dictionary's own bibls, never
from a new mark): a name's work where one work holds 80% of 5 or more of its bibls, else the name
and first number's, else the one work whose observed range holds the second number; the number in
that work's own segment template; a bare number or ib. takes the citation before it, its leading
numbers completed (Il. 14.271, 300 -> 14:300); a name the night ruled a citation is the citation
before what follows it, its work unknown, so no Id. or ib. after it reaches back past it to another
work (Id. Fr. 2 after Muson. Fr. 18 is not Plutarch's). A span's reader-given abo reference is used
where its work is one the dictionary's bibls name, its locus has a template of that work, and its
numbers end with the printed ones (agrees()); where it does not agree with the print the mark has
no n; where the rule and the reader both give an n and they differ, the span is residue. An
extension past the number the n was made from (a fascicle, a No., the rest of the number, Ps.-, an
edition) drops the n; a column and line keep it (the document's n is still the document). No corpus
number is made up.

Left by rule, not marked (left.tsv): a title of one or two capitals, or any title right after a
citation of the dictionary's own or one with an n (a face or column letter, a sub-locus: SIG 364 A
50, Archim. Sph.Cyl. 1 Def. 2: a part of a marked one); a hit that opens a bracket or a '=' right
after a citation (a second address: [Fr. 75.2 Pf.], (= Trag.Adesp. 373)); a number in a grammar
element (<per>3</per> sg.); a hit inside another new mark; a continuation (C2) of a span the night
did not rule a citation; the spans the night ruled otherwise. Residue (residue.tsv, the unsettled,
for a reader): a span not found again in the files, a mark that would cross an element, hold a tag
a bibl does not (a <cit>, an <i>, a <foreign>), or stand where the dictionary's bibls never stand
(in a quotation, a foreign word), marks that overlap, a name right before a hit (Aristid. Quint.
2.6: the citation may begin there), a number that runs on, a reader's malformed or unknown abo
reference, the rule and the reader disagreeing.

Numbering. A citation's number in its entry (the page's cite|<entry>|<n>, the readings' and the
previews' n) is the dictionary's own bibls first, 1 to N in byte order as before, then the bibls of
each pass of resp in the order of its value, each in byte order: N+1 onwards. The dictionary's own
keep their numbers, whatever is marked around them (site/build.py's cite_order(), the page's
citeOrder(), tools/snippets.py's BIBL).

The readers' answers (--answers: night C of 31 Oct 2026 on the residue of the rule, night C2 of 1
Nov on the second pass's). The residue was read again by AI readers, each answer a verdict on the
span and, for a citation, the citation as printed, from where it begins to where it ends (the
package's BRIEF.txt; the key says which items are the residue). On the files with the marks, each
citation or second address of certainty 4 or 5 is marked by its printed text (a second address its
own citation, with no n, as the second pass marks them), found at the span in the entry's string
over the dictionary's own bibls (where two div2s share an orig_id, in the one the span stands in).
The bibl is widened over the tags at its edges where the citation begins or ends with an element's
whole text (s.v. <foreign>βουγάϊε</foreign>), never over text; an editor's siglum after it (130.7
<editor>J.</editor>) is left outside, as the dictionary's own bibls leave it (1,418 of its 2,210
sigla stand right after a </bibl>). Where the <cit> of the quotation before closes inside the
citation (<title>IG</title> ΙΙ(2).161</cit> <title>B</title> 38), a fault of the markup, the </cit>
moves to right after the citation's bibl, as the dictionary's own close (142,519 times; never after
a siglum); where a <foreign> opened in it holds the stop or comma after it, the punctuation moves
out, as the dictionary's markup has it for a word cited after s.v., s. vv. or post (outside 50
times, inside 45; an <i>'s face letter or word never: those are held). Only tags move, and only for
the bibl they let stand; each move is listed (markup.tsv: entry, what moved, the markup from and
to, why), and --check --moves undoes them. Held (residue-c.tsv), with the reason: a bibl that would
still cross an element, stand where the dictionary's bibls never stand, hold a tag theirs never
hold (they hold <author> and <title>, and rarely <foreign>, <abbr>, <i>), overlap a bibl already
there, or end where its number runs on; a bibl of the rule's own on a part of it (Nic. ⟦Dam. Fr.
127⟧ J.) gives way, its tags out and the reader's span the label, but where it stands on the source
after in or post (Choerob. Orth. in ⟦AB 1380⟧), as the dictionary's own bibls do, the reader's
citation is marked already. The n is the reader's abo reference where the table fits it and the
print agrees, else the table's where the citation is a name and a number the rule reads (A1, T1,
A2), else none, and none where the two differ. The comma-numbers after a reader's citation are
marked as after the rule's own (C). The bibls are of the same pass, numbered after the dictionary's
own; a rerun marks and moves nothing more.

A citation quoted through another (X ap. Y), in either pass, is marked on its source after the last
ap., the quoted author outside, as the dictionary's own bibls stand (ap. <bibl> 8,571 times, X ap.
inside a bibl 3), its n the table's for the source.

The second pass (--names, 31 Oct to 1 Nov 2026), on the files with the first pass's marks, every
mark the same <bibl resp="lsjai-20261031"> and none with an n: the census's lexicon class (unmarked.py:
an <author> or <title> of LEXICA or BY_PAGE outside every bibl and every hit), a lexicon named for the
word it glosses (Hsch. closing a gloss, cf. Suid., Gloss. after a Latin equivalent), with what is printed
after it of its place (s.v. and the word, s. vv. and the words, l.c., ad loc., p. 167P., iii 283);
the second addresses the spans night ruled so, each its own citation: the content of its bracket where
that is one dotted number with an abbreviation and an editor at most ([Fr. 75.77 Pf.], [Dith. 4.3]), or
the number after a =; and a join: a first-pass mark of a name the night ruled a citation is widened to
the author right before it when the reader's reference begins with that author (Apollon. ⟦Lex. s.v.
γραπτῦς⟧), its open tag moved, its n kept. Left (left.tsv): a name before ap. (quoted through the
citation after it), before in or ad and a bibl, or right before one of the dictionary's own bibls (its
work's name outside the bibl), a name after freq. in and the like (named for its usage), and the spans
the night ruled not a citation. Residue (residue.tsv): a work cited by page or number standing alone
(BY_PAGE: Eust., Poll., Hdn.Gr., Choerob., Theognost., AB, Phryn.), a second address the rule cannot
bound, a name right before a first-pass mark the night's reference does not join it to, and what would
cross an element. Under one resp, a mark of the second pass that stands before one of the first pass's
takes its place in byte order, so first-pass marks may change number among the marks (N+1 onwards);
nothing keys those numbers yet (no preview, reading or verdict): a later pass that must keep them takes
a resp of its own, which sorts after.

The addresses (--table, 1 Nov 2026), on the files with every pass's labels: a label with no n whose name
as printed (Ps.-, the author, the title) is a row of the rule table, tools/addresses.tsv (name, work,
levels, source, note), or a bare number, ib. or Id. with a number right after such a label (no name
between them), takes the n its number names by the row: the work, and the place in the store's levels
('=N' the printed numbers are the store's levels from the first, at least N of them, '=N-M' at most M;
'kühn' Kühn's volume, its part in brackets, and page; 'p=N' a page after p.; 'F.=N' a fixed first level;
a siglum after a space dropped; a + where the store divides a level into lettered parts numbered on, as
Stob. 4.22 into 4.22a to 4.22g); a bare number shorter than the row's least takes the leading levels of
the citation before (Gal. 11.127, 130 is 11.130). Where the row names more works (Galen by Kühn's
pages), the place picks the one whose lines hold it. The rows are rulings of the work table (night B,
31 Oct 2026; source is its row) that the store and a reader's eye bore out. An n is written only where
n1_package's Store.passage, given the n as the cutter reads it (perseus_places.abo: the abo work in CTS
form, the locus as the store's levels), returns the place's lines, the place itself or the lines it
opens, never a shallower place; the rest keep no n, unresolved (no work of the row holds the place) or
skipped (a printed form the row does not read: no number, l.c., a D. not the row's, a shorter number
after a deeper one). Only the label's open tag changes, <bibl resp="lsjai-20261031"> taking its n: the
text of every entry, every label and the dictionary's own bibls stay byte-identical, and --check counts
each as a bibl added before whose n changed. labels-n.tsv lists every label a row reaches, its place, n
and result (a label with an n already is listed, not changed); addresses.json the counts by name and
the files' hashes before and after.

--check compares the files here with the files before (a directory of greatscott*.xml): every
entry's plain text byte-identical, every file the files before once the added tags are taken out
and, with --moves, the markup moves undone, every entry well-formed, its own bibls the same in the
same order, and the bibls the files before had added still there in the same order: the same but
for their n, widened to hold what they held (a join of the second pass, a reader's span over a
part), or moved onto their source after ap. Standard library only; the same inputs give the same
output.
"""
import argparse, collections, hashlib, html, json, os, re, sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 'lsjai-20261031'
FILES = ['greatscott%02d.xml' % k for k in range(1, 87)]
DIV2 = re.compile(rb'<div2\s[^>]*>.*?</div2>', re.S)
ATTR = re.compile(rb'([A-Za-z_:][A-Za-z0-9_:.-]*)\s*=\s*(["\'])(.*?)\2', re.S)
TAGB = re.compile(rb'<[^>]*>')
NAMECH = set(b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_')
PARENTS = {'sense', 'cit', 'div2'}          # where the dictionary's own bibls stand
INSIDE = {'author', 'title', 'hi'}          # the tags a new bibl may hold (hi: an italic face letter in a number, 11.154<hi>A</hi>42)
GRAMMAR = {'per', 'number', 'tns', 'mood', 'gen', 'itype', 'pos', 'gram', 'gramGrp'}
ADDED = re.compile(rb'<bibl\b[^>]*\sresp="([^"]*)"[^>]*>')


def attrs(tag):
    return {k.decode(): html.unescape(v.decode('utf-8')) for k, _, v in ATTR.findall(tag)}


def plain(raw):
    return re.sub(r'\s+', ' ', html.unescape(TAGB.sub(b'', raw).decode('utf-8', 'replace'))).strip()


def bibls(raw):
    """[(start, end)] of the complete bibls, in byte order (the readings' rule: a '<bibl' not followed
    by a name character, to the first '</bibl>' after its '>')."""
    out, i = [], 0
    while True:
        s = raw.find(b'<bibl', i)
        if s < 0:
            return out
        a = s + 5
        if a >= len(raw) or raw[a] in NAMECH or raw[a] >= 128:
            i = s + 1
            continue
        gt = raw.find(b'>', a)
        close = raw.find(b'</bibl>', gt + 1) if gt >= 0 else -1
        if close < 0:
            i = s + 1
            continue
        out.append((s, close + 7))
        i = close + 7


def own(raw, bs):
    """The dictionary's own bibls: those no pass of resp added."""
    return [(s, e) for s, e in bs if not ADDED.match(raw, s)]


def entries(data):
    for m in DIV2.finditer(data):
        raw = m.group(0)
        yield m.start(), raw, attrs(raw[:raw.find(b'>') + 1]).get('orig_id', '')


# ---------------------------------------------------------------- the entry as one string, mapped

def build(raw, bs):
    """The census's string of an entry (detect.build): every complete bibl ⟦B⟧, an <author> outside
    a bibl \\x02X\\x03, a <title> \\x04X\\x05, other tags dropped, entities read, whitespace collapsed;
    with each character's [start, end) in raw."""
    chars, spans = [], []
    ends = {s: e for s, e in bs}
    i, n = 0, len(raw)
    depth = {'author': 0, 'title': 0}
    while i < n:
        if i in ends:
            for ch in '⟦B⟧':
                chars.append(ch)
                spans.append((i, ends[i]))
            i = ends[i]
            continue
        b = raw[i]
        if b == 0x3c:                                   # a tag
            j = raw.find(b'>', i) + 1
            m = re.match(rb'<(/?)(author|title)\b', raw[i:j])
            if m:
                ch = {('', 'author'): '\x02', ('/', 'author'): '\x03', ('', 'title'): '\x04', ('/', 'title'): '\x05'}[(m.group(1).decode(), m.group(2).decode())]
                chars.append(ch)
                spans.append((i, j))
            i = j
            continue
        if b == 0x26:                                   # an entity
            j = raw.find(b';', i) + 1
            if 0 < j - i <= 12:
                t = html.unescape(raw[i:j].decode('utf-8', 'replace'))
                for ch in t:
                    chars.append(ch)
                    spans.append((i, j))
                i = j
                continue
        k = 1 if b < 0x80 else 2 if b >> 5 == 6 else 3 if b >> 4 == 14 else 4
        chars.append(raw[i:i + k].decode('utf-8', 'replace'))
        spans.append((i, i + k))
        i += k
    out, mp, white = [], [], False                       # whitespace runs to one space
    for ch, sp in zip(chars, spans):
        if re.match(r'\s', ch):
            if not white:
                out.append(' ')
                mp.append(sp)
            white = True
        else:
            out.append(ch)
            mp.append(sp)
            white = False
    return ''.join(out), mp


def census_build(raw, bs):
    """detect.build verbatim, to check build() against."""
    AUTHEL = re.compile(rb'<author[^>]*>(.*?)</author>', re.S)
    TITLEEL = re.compile(rb'<title[^>]*>(.*?)</title>', re.S)
    parts, at = [], 0
    for s, e in bs + [(len(raw), len(raw))]:
        seg = raw[at:s]
        seg = AUTHEL.sub(lambda m: b'\x02' + TAGB.sub(b'', m.group(1)) + b'\x03', seg)
        seg = TITLEEL.sub(lambda m: b'\x04' + TAGB.sub(b'', m.group(1)) + b'\x05', seg)
        seg = TAGB.sub(b'', seg)
        parts.append(html.unescape(seg.decode('utf-8', 'replace')))
        if s < len(raw):
            parts.append('⟦B⟧')
        at = e
    return re.sub(r'\s+', ' ', ''.join(parts))


def show(s):
    return s.replace('\x02', '«').replace('\x03', '»').replace('\x04', '‹').replace('\x05', '›').replace('\t', ' ')


# ---------------------------------------------------------------- the detector (census detect.py)

NUM = r'(?:[IVXL]{1,5}\.?\s?)?\d+(?:\(\d+\))?(?:[a-g]\d*)?(?:\.\d+(?:\(\d+\))?(?:[a-g]\d*)?)*'
END = r'(?![\w])(?!\s?(?:B\.\s?C|A\.\s?D))'
TOK = r'(?:\x04[^\x05]{1,40}\x05|[A-Z][A-Za-z]{0,12}\.?|[a-z]{1,6}\.|\([A-Za-z.\s]{1,12}\)|\[[A-Za-z.\s]{1,12}\])'
GAP = rf'(?P<gap>(?:\s*{TOK}){{0,3}}\s*)'
JUNK = {'id.', 'pl.', 'tm.', 'Ep.', 'Α.'}


def detector(vocab):
    auth = sorted([a for a, c in vocab.items() if c >= 5 and a.endswith('.') and len(a) >= 2 and a not in JUNK
                   and re.match(r'^[A-Z][A-Za-z.\s\[\]-]*$', a)], key=len, reverse=True)
    alt = '|'.join(re.escape(a) for a in auth)
    return re.compile(
        r'(?P<B>⟦B⟧)'
        rf'|(?P<A1>\x02(?P<a1>[^\x03]{{1,40}})\x03{GAP.replace("gap", "g1")}(?P<n1>{NUM}){END})'
        rf'|(?P<T1>\x04(?P<t1>[^\x05]{{1,40}})\x05{GAP.replace("gap", "g2")}(?P<n2>{NUM}){END})'
        rf'|(?P<A2>(?<![\w.\x02\x04])(?P<a2>{alt})(?=[\s(\[\x04]|\d){GAP.replace("gap", "g3")}(?P<n3>{NUM}){END})')


CONT = re.compile(rf'\s*,\s*(?P<n>{NUM}){END}')
IB = re.compile(rf'(?<![\w.])(?:ib\.|Ib\.|ibid\.|l\.\s?c\.)\s?(?:{TOK}\s?){{0,2}}(?P<n>{NUM}){END}')
DOT = re.compile(r'(?<![\w.(])\d+(?:\(\d+\))?\.\d+[a-z]?(?:\.\d+)*(?![\w])')


# ---------------------------------------------------------------- the table (census compose.py)

WTOK = re.compile(r'\d+|[A-Za-z]+')
ABO = re.compile(r'Perseus:abo:((?:tlg|phi|stoa),[^,:]+,[^,:]+|pap,[^:]+)(?::(.*))?$')
ABO_FORM = re.compile(r'^Perseus:abo:(?:(?:tlg|phi|stoa),\d{4},\d{3}|pap,[^:\s,]+)(?::[^\s:][^\s]*)?$')


def tokens(s):
    return WTOK.findall(s or '')


def template(locus):
    return re.sub(r'[A-Za-z]+', 'a', re.sub(r'\d+', '9', locus))


def types(tt):
    return ''.join('9' if t.isdigit() else 'a' for t in tt)


def render_tpl(tpl, tt):
    out, k = [], 0
    for ch in tpl:
        if ch in '9a':
            out.append(tt[k])
            k += 1
        else:
            out.append(ch)
    return ''.join(out)


def visible_locus(inner):
    v = plain(re.sub(rb'<(author|title)[^>]*>.*?</\1>', b'', inner, flags=re.S))
    m = re.search(r'(?:\bpp?\.\s?)?\d', v)
    if not m:
        return ''
    v = v[m.start():]
    return re.sub(r'(?:\s+(?:[A-Z][A-Za-z]*\.?|sq\.|sqq\.|al\.|codd\.|cod\.|v\.l\.))+\s*$', '', v)


def elements(inner, tag):
    return [plain(x) for x in re.findall(rb'<' + tag + rb'[^>]*>(.*?)</' + tag + rb'>', inner, re.S)]


class Table:
    """The name-to-work table, learned from the dictionary's own bibls with a Perseus abo n."""

    def __init__(self):
        self.K, self.K2 = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
        self.RANGE = collections.defaultdict(lambda: collections.defaultdict(list))
        self.TR, self.TRW = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
        self.TPL = collections.defaultdict(collections.Counter)
        self.works = set()

    def info(self, raw, s, e):
        b = raw[s:e]
        head = b[:b.find(b'>') + 1]
        inner = b[len(head):-7]
        n = attrs(head).get('n', '').strip()
        au, ti = elements(inner, b'author'), elements(inner, b'title')
        m = ABO.match(n)
        w, locus = (m.group(1), m.group(2) or '') if m else (None, '')
        return {'key': (au[0] if au else '') + '|' + (ti[0] if ti else ''), 'author': au[0] if au else '',
                'work': w, 'locus': locus, 'vt': tokens(visible_locus(inner)), 'lt': tokens(locus), 'n': n}

    def learn(self, x):
        w, key, vt, lt = x['work'], x['key'], x['vt'], x['lt']
        if not w:
            return
        self.works.add(w)
        self.K[key][w] += 1
        if vt:
            self.K2[(key, vt[0])][w] += 1
            if len(vt) > 1 and vt[1].isdigit():
                self.RANGE[(key, vt[0])][w].append(int(vt[1]))
        tr = 'same' if vt == lt else 'drop1' if vt[1:] == lt and len(vt) > 1 else None
        if tr:
            self.TR[(key, w)][tr] += 1
            self.TRW[w][tr] += 1
        self.TPL[(w, types(lt))][template(x['locus'])] += 1

    @staticmethod
    def dominant(c, least=5, share=0.8):
        t = sum(c.values())
        if t >= least:
            w, x = c.most_common(1)[0]
            if x / t >= share:
                return w
        return None

    def resolve(self, key, vt):
        E = collections.Counter()
        w = self.dominant(self.K.get(key, E))
        if w:
            return w, 'name'
        if vt:
            w = self.dominant(self.K2.get((key, vt[0]), E))
            if w:
                return w, 'name+first'
            if len(vt) > 1 and vt[1].isdigit():
                x = int(vt[1])
                inside = [w for w, xs in self.RANGE.get((key, vt[0]), {}).items() if len(xs) >= 5 and min(xs) <= x <= max(xs)]
                if len(inside) == 1:
                    return inside[0], 'range'
        if not self.K.get(key):
            return None, 'no pattern: name never printed in a bibl with an abo n'
        return None, 'ambiguous: %d bibls: %s' % (sum(self.K[key].values()), ', '.join('%s %d' % wc for wc in self.K[key].most_common(3)))

    def compose(self, key, w, vt):
        tr = (self.TR.get((key, w)) or self.TRW.get(w) or collections.Counter()).most_common(1)
        tr = tr[0][0] if tr else 'same'
        xt = vt[1:] if tr == 'drop1' and len(vt) > 1 else vt
        tpl = self.TPL.get((w, types(xt)), collections.Counter()).most_common(1)
        if not xt or not tpl:
            return None
        return 'Perseus:abo:%s:%s' % (w, render_tpl(tpl[0][0], xt))

    def fits(self, n):
        """A reader's abo n: well formed, its work one the dictionary's bibls name, its locus a template
        of that work's."""
        m = ABO.match(n)
        if not ABO_FORM.match(n) or not m or m.group(1) not in self.works:
            return False
        lt = tokens(m.group(2) or '')
        return not lt or template(m.group(2)) in self.TPL.get((m.group(1), types(lt)), {})


GAPTOK = re.compile(r'\x04([^\x05]*)\x05|(\S+)')


def gap_title(gap):
    title, via, page = [], False, False
    for m in GAPTOK.finditer(gap):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if m.group(2) in ('ap.', 'in', 'ad', 'ap'):
            via = True
        elif m.group(2) in ('p.', 'pp.'):
            page = True
        else:
            title.append(t.strip())
    return ' '.join(x for x in title if x), via, page


# ---------------------------------------------------------------- a NAME span's extent

LTOK = re.compile(r'\d+|[^\W\d_]+')
LOOK = str.maketrans('ΑΒΕΖΗΙΚΜΝΟΡΤΥΧαο', 'ABEZHIKMNOPTYXao')


def same(a, b):
    if a == b:
        return True
    fa, fb = a.translate(LOOK), b.translate(LOOK)
    if fa == fb:
        return True
    num = lambda t: re.sub('[Il]', '1', re.sub('O', '0', t))
    return re.fullmatch(r'[IlO0-9]+', fa) is not None and fb.isdigit() and num(fa) == fb


def name_extent(s, start, end, ref):
    """Where a NAME citation's mark ends: after the name, or after what follows it when that is the
    rest of the reference, token for token, with only spaces, dots, the markers and balanced
    parentheses between (never across a bibl, a comma or a semicolon)."""
    R = LTOK.findall(ref)
    nm = LTOK.findall(show(s[start:end]))
    k = -1
    for j in range(len(R) - 1, -1, -1):
        if nm and same(nm[-1], R[j]):
            k = j
            break
    if k < 0:                                          # Id. for Hsch.: the reference's leading names
        k = 0
        while k < len(R) and R[k][:1].isupper() and R[k].isalpha():
            k += 1
        k -= 1
    tail = R[k + 1:]
    if not tail:
        return end
    pos, last = end, end
    for t in tail:
        m = LTOK.search(s, pos)
        if not m:
            return end
        between = s[pos:m.start()]
        if not re.fullmatch(r'[\s.()\x02-\x05]*', between) or not same(m.group(0), t):
            return end
        pos = last = m.end()
    seg = s[end:last]
    for o, c in (('\x02', '\x03'), ('\x04', '\x05')):
        if seg.count(o) > seg.count(c):              # the last token inside a name: take its close
            m = re.match(r'[.\s]*' + c, s[last:])
            if not m:
                return end
            last += m.end()
            seg = s[end:last]
    if seg.count('(') != seg.count(')') or '⟦' in seg or seg.count('\x02') != seg.count('\x03') or seg.count('\x04') != seg.count('\x05'):
        return end
    if re.search(r'(?<![^\W\d_])[A-Za-z]{1,6}$', seg) and s[last:last + 1] == '.':
        last += 1                                    # an abbreviation's dot (J., Pf.), not a lemma's full stop
    return last


# ---------------------------------------------------------------- the rules over one entry

def spans_by_entry(spans_tsv, items_jsonl):
    items = {}
    with open(items_jsonl, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                it = json.loads(line)
                items[(it['entry'], it['span'])] = it
    out = collections.defaultdict(list)
    with open(spans_tsv, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            r = dict(zip(head, line.rstrip('\n').split('\t')))
            it = items[(r['entry'], r['span'])]
            kind = {'an author abbreviation and a number in plain text': 'A2', 'a dotted number with no name before it': 'DOT',
                    'an author or title standing with no number after it': 'NAME'}[it['kind']]
            off = int(r['span'].split(':', 1)[0])
            out[(it['file'], r['entry'])].append({'id': it['id'], 'kind': kind, 'off': off, 'text': it['text'],
                                                   'verdict': r['verdict'], 'ref': r['reference'].strip(), 'cert': r['certainty']})
    return out


def marker(text):
    return text.replace('«', '\x02').replace('»', '\x03').replace('‹', '\x04').replace('›', '\x05')


def find_span(s, sp, pat):
    """The span's place in the entry as it is now: at its offset, else the nearest place its text
    stands as the same kind."""
    t = marker(sp['text'])

    def stands(o):
        if sp['kind'] == 'A2':
            m = pat.match(s, o)
            return m.end() if m and m.group('A2') else None
        if sp['kind'] == 'DOT':
            m = DOT.match(s, o)
            return m.end() if m and m.group(0) == t else None
        return o + len(t) if s.startswith(t, o) else None

    if stands(sp['off']) is not None:
        return sp['off'], stands(sp['off']), False
    near = sorted((abs(o - sp['off']), o) for o in (m.start() for m in re.finditer(re.escape(t[:12]), s)))
    for _, o in near:
        e = stands(o)
        if e is not None:
            return o, e, True
    return None, None, False


PART = ("left: a part of the citation before it (a face letter, Def., Fr.), not joined: that citation is the dictionary's own, "
        "has an n, or the join would cross an element")
TAILS = [(r'(?:\.\d+(?:[A-Za-z]{1,3} ?\d*)?)+(?![\w])', False, '; with the rest of its number (11.203A32, 1.460J)'),
         (r' \((?:\d+|[IVX]+)\) ?(?:\.\d+[a-z]?)+(?![\w])|\((?:\d+|[IVX]+)\) (?:\.\d+[a-z]?)+(?![\w])', False,
          "; with its number's part after a space"),           # IG 12 (5).817, IG 9 (I).694
         (r' No\.\s?\d+[a-z]?(?:\.\d+[a-z]?)*(?![\w])', False, '; with its No. after it'),     # Milet. 3 No.150.97
         (r' [ivx]{1,5} \d+[a-z]?(?![\w.])', True, '; with its column and line after it')]   # PCair.Zen. 12 ii 80


def agrees(n, text):
    """Whether an abo n's locus can be the printed number: the printed digit runs the last of the
    locus's (its leading numbers may come from the citation before: 300 after Il. 14.271), the first
    of them perhaps left out as the dictionary's own n's leave it (Plu. 2.144b, 144:b)."""
    printed = re.findall(r'\d+', re.sub(r'^\D*?(?=\d)', '', text)) if re.search(r'\d', text) else []
    m = ABO.match(n)
    locus = re.findall(r'\d+', (m.group(2) or '') if m else '')
    ends = lambda p: 0 < len(p) <= len(locus) and locus[len(locus) - len(p):] == p
    return not printed or ends(printed) or ends(printed[1:])      # or the work's number left out (Plu. 2.144b: 144:b)


def save(row):
    row['saved'].append({'start': row['start'], 'end': row['end'], 'n': row['n'], 'rule': row['rule'], 'joined': len(row['joined'])})


def second_address(s, start, last_end):
    """A hit that opens a bracket or a '=' right after the citation before it."""
    if last_end is None:
        return False
    return re.fullmatch(r'\s*(?:\[\s*=?|\(\s*=|=)\s*', s[last_end:start]) is not None


def name_cited(seg, prev):
    """The citation a name the night ruled a citation stands for in the walk: the author it names
    (Id., the one before), the title, no work."""
    au, ti = re.search(r'\x02([^\x03]*)\x03', seg), re.search(r'\x04([^\x05]*)\x05', seg)
    author, title = (au.group(1).strip() if au else ''), (ti.group(1).strip() if ti else '')
    if author == 'Id.' and prev and prev['author']:
        author = prev['author']
    return {'key': author + '|' + title, 'author': author, 'work': None, 'vt': [], 'n': None}


def entry_marks(raw, oid, T, pat, spans, tally):
    """The new marks of one entry: [(start, end) in the string, kind, n or '', rule], and the residue
    and the left as rows."""
    bs = bibls(raw)
    s, mp = build(raw, bs)
    marks = [m.start() for m in re.finditer('⟦B⟧', s)]
    info = [T.info(raw, a, b) for a, b in bs]
    events, hits, covered = [], [], []
    # the census's walk (unmarked.py): PAT leftmost, its comma-numbers after it, then ib./l.c., then dotted
    pos = 0
    while True:
        m = pat.search(s, pos)
        if not m:
            break
        kind = next(g for g in ('B', 'A1', 'T1', 'A2') if m.group(g))
        end = m.end()
        if kind != 'B':
            gap = m.group({'A1': 'g1', 'T1': 'g2', 'A2': 'g3'}[kind])
            if len(gap) > 25:
                pos = m.start() + 1
                continue
            hits.append([m.start(), end, kind, m])
        head = hits[-1] if kind != 'B' else None
        while True:
            c = CONT.match(s, end)
            if not c:
                break
            hits.append([c.start('n'), c.end(), 'C' if kind == 'B' else 'C2', c, head])
            end = c.end()
        covered.append((m.start(), end))
        pos = end
    inside = lambda i: any(a <= i < b for a, b in covered)
    for m in IB.finditer(s):
        if not inside(m.start()):
            hits.append([m.start(), m.end(), 'IB', m])
            covered.append((m.start(), m.end()))
    dots = {m.start(): m for m in DOT.finditer(s) if not inside(m.start())}
    # the night's spans, found again
    sv = {}
    for sp in spans:
        a, b, moved = find_span(s, sp, pat)
        tally['spans: ' + ('found at their offset' if a is not None and not moved else 'found nearby' if a is not None else 'not found again')] += 1
        if a is None:
            yield 'residue', {'reason': 'span not found again in the files', 'kind': sp['kind'], 'start': None, 'text': sp['text'], 'n': sp['ref'], 'id': sp['id']}
            continue
        sv[(sp['kind'], a)] = (sp, b)
    for (kind, a), (sp, b) in sv.items():
        if kind in ('DOT', 'NAME'):
            hits.append([a, b, kind, None, sp])
    for h in hits:
        if h[2] == 'A2':
            h.append(sv.get(('A2', h[0]), (None,))[0])
    hits.sort(key=lambda h: h[0])

    events = [(o, 0, j) for j, o in enumerate(marks)] + [(h[0], 1, h) for h in hits]
    prev, last_end, out = None, None, []
    ok_head, named = {}, set()
    for off, isb, x in sorted(events, key=lambda e: (e[0], e[1])):
        if not isb:
            bi = info[x]
            prev = {'key': bi['key'], 'author': bi['author'], 'work': bi['work'], 'vt': bi['vt'], 'n': None}
            last_end = off + 3
            continue
        a, b, kind = x[0], x[1], x[2]
        row = {'start': a, 'end': b, 'kind': kind, 'n': '', 'rule': '', 'id': '', 'joined': [], 'saved': []}
        sp = x[4] if kind in ('A2', 'DOT', 'NAME') else None
        cur = None
        if kind in ('A1', 'T1', 'A2'):
            m = x[3]
            hk = kind
            gap = m.group({'A1': 'g1', 'T1': 'g2', 'A2': 'g3'}[hk])
            name = m.group({'A1': 'a1', 'T1': 't1', 'A2': 'a2'}[hk])
            vt = tokens(m.group({'A1': 'n1', 'T1': 'n2', 'A2': 'n3'}[hk]))
            title, via, page = gap_title(gap)
            author = name if hk != 'T1' else ''
            if hk == 'T1':
                key = '|' + (name + (' ' + title if title else ''))
            else:
                if author == 'Id.' and prev and prev['author']:
                    author = prev['author']
                key = author + '|' + title
            if page:
                vt = ['p'] + vt
            if hk == 'T1' and re.fullmatch(r'[A-Z][a-z]?', name):
                w, rule = None, 'left: a face or column letter after a citation (part of a marked one)'
            elif via:
                w, rule = None, 'ambiguous: a via (ap., in) in the gap'
            else:
                w, rule = T.resolve(key, vt)
            n = T.compose(key, w, vt) if w else None
            if w and not n:
                rule = "no pattern: number shape not in the work's n values"
            cur = {'key': key, 'author': author, 'work': w if n else None, 'vt': vt, 'n': n}
            row['n'], row['rule'] = n or '', (rule.split(':')[0] if not rule.startswith('left') else rule)
            if n:
                row['rule'] = 'by the table: ' + rule
        elif kind in ('C', 'C2', 'IB'):
            num = x[3].group('n')
            vt = tokens(num)
            if not prev:
                n, rule = None, 'no citation before it'
                cur = {'key': '', 'author': '', 'work': None, 'vt': vt, 'n': None}
            elif not prev['work']:
                n, rule = None, 'the citation before has no work'
                cur = dict(prev, vt=vt, n=None)
            else:
                pv = prev['vt']
                if len(vt) < len(pv):
                    full = pv[:len(pv) - len(vt)] + vt
                    n = T.compose(prev['key'], prev['work'], full)
                    w, rule = prev['work'], 'by the table: continuation (leading numbers from the citation before)'
                else:
                    full = vt
                    w, rule = T.resolve(prev['key'], full)
                    n = T.compose(prev['key'], w, full) if w else None
                    rule = ('by the table: continuation, ' if n else 'continuation, ') + rule.split(':')[0]
                cur = {'key': prev['key'], 'author': prev['author'], 'work': w if n else None, 'vt': full, 'n': n}
            row['n'], row['rule'] = n or '', rule
        else:                                            # DOT, NAME: the night's
            cur = {'key': '', 'author': '', 'work': None, 'vt': tokens(show(s[a:b])), 'n': None} if kind == 'DOT' else prev
            row['rule'] = 'the night'
        # the night's verdict on its spans; continuations follow their head
        if sp is not None:
            row['id'] = sp['id']
            if sp['verdict'] != 'citation':
                row['rule'] = 'left: the night ruled it ' + sp['verdict']
            else:
                ref = sp['ref']
                if kind == 'NAME':
                    b = name_extent(s, a, b, ref)
                    row['end'] = b
                rn = ref if ref.startswith('Perseus') else ''
                if rn and not T.fits(rn):
                    row['rule'] = "residue: the reader's abo reference is malformed or names a work the dictionary does not"
                elif rn and row['n'] and rn != row['n']:
                    row['rule'] = 'residue: the rule and the reader give different references'
                elif rn and not agrees(rn, show(s[a:b])):
                    row['n'], row['rule'] = '', "the night's citation, no n: its reader's abo reference does not agree with the printed number"
                elif rn:
                    row['n'], row['rule'] = rn, "the night's citation, its reader's abo reference"
                elif row['n']:
                    row['rule'] = "the night's citation, " + row['rule']
                else:
                    row['rule'] = "the night's citation, no abo reference"
                row['ref'] = ref
        if kind == 'A2' and sp is None:
            row['rule'] = 'left: an author abbreviation and a number the night did not read'
        if kind == 'C2' and x[4] is not None and not ok_head.get(id(x[4]), True):
            row['rule'] = 'left: the continuation of a span the night did not rule a citation, or of a left one'
        if kind in ('A1', 'T1') and re.search(r'[\x03\x05] ?$', s[max(0, a - 2):a]) and not row['rule'].startswith('left') \
                and a - (1 if s[a - 1] == ' ' else 0) not in named:
            row['rule'] = 'residue: a name stands right before it (the citation may begin there)'
        if kind in ('A1', 'T1', 'C', 'C2', 'IB') and second_address(s, a, last_end):
            row['rule'] = 'left: opens a bracket or a = after a citation (a second address)'
        live = not row['rule'].startswith(('left', 'residue'))
        if kind == 'T1' and (live or row['rule'].startswith('left: a face')) and last_end is not None and last_end <= a \
                and re.fullmatch(r' ?', s[last_end:a]):          # a title right after a citation, no comma: a part of it
            p = out[-1] if out and out[-1]['end'] == last_end and not out[-1]['rule'].startswith(('left', 'residue')) else None
            if p is not None and not p['n']:
                save(p)
                p['end'] = b
                p['rule'] += '; with the part after it'
                p['joined'].append(row)
                row['rule'] = 'left: joined to the new mark before it (a part of it: a face letter, Def., Fr.)'
                last_end = b
            else:
                row['rule'] = PART
            live = False
        if live and kind in ('A1', 'A2') and s[max(0, a - 4):a] == 'Ps.-' and not re.match(r'\w', s[a - 5:a - 4] or ' '):
            save(row)                                     # Ps.- inside, as the dictionary's own bibls have it; its work unknown
            row['start'] = a = a - 4
            row['n'] = ''
            row['rule'] = row['rule'].replace('by the table: ', '') + '; with Ps.- before it'
        if live and kind in ('A1', 'T1', 'C', 'C2', 'IB', 'DOT', 'A2'):
            m = re.match(r' \d+(?:\.\d+)+(?![\w])', s[row['end']:row['end'] + 20])
            if m:
                dot = sv.get(('DOT', row['end'] + 1))
                if kind == 'T1' and dot and dot[0]['verdict'] == 'citation':
                    save(row)                             # SIG 2 588.17 (SIG², 588.17 a citation by the night): one mark
                    row['end'] += m.end()
                    row['n'] = ''
                    row['rule'] = row['rule'].replace('by the table: ', '') + '; with the number after it, an edition'
                else:
                    row['rule'] = 'residue: a number after its number, past a space (SIG 2 588.17: an edition?)'
                    live = False
        if live and kind in ('A1', 'T1', 'C', 'C2', 'IB', 'DOT', 'A2', 'NAME'):
            for tail, keep, label in TAILS:
                m = re.match(tail, s[row['end']:row['end'] + 40])
                if m:
                    save(row)
                    row['end'] += m.end()
                    if not keep:
                        row['n'] = ''
                        row['rule'] = row['rule'].replace('by the table: ', '')
                    row['rule'] += label
            b = row['end']
            last_end = b
        if kind in ('A1', 'T1', 'A2'):
            ok_head[id(x)] = not row['rule'].startswith(('left', 'residue')) or row['rule'].startswith('left: joined')
        if not row['rule'].startswith(('left', 'residue')):
            last_end = row['end']
        if kind == 'NAME' and sp is not None and sp['verdict'] == 'citation':
            prev = name_cited(s[a:row['end']], prev)     # an Id. after it is this name's, not the one before it
            named.add(a + len(marker(sp['text'])))
        elif kind != 'NAME':
            prev = cur
        row['text'] = show(s[row['start']:row['end']])
        out.append(row)

    # the rows to marks: extents in raw, checks, overlaps
    taken = []
    for row in sorted(out, key=lambda r: (r['start'], -r['end'])):
        if row['rule'].startswith('left'):
            yield 'left', row
            continue
        if row['rule'].startswith('residue'):
            row['reason'] = row['rule'][len('residue: '):]
            yield 'residue', row
            continue
        a, b = row['start'], row['end']
        if any(x <= a and b <= y for x, y, _ in taken):
            outer = next(r for x, y, r in taken if x <= a and b <= y)
            row['rule'] = 'left: inside another new mark (%s), which holds it' % outer['kind']
            yield 'left', row
            continue
        if any(x < b and a < y for x, y, _ in taken):
            row['reason'] = 'overlaps another mark'
            yield 'residue', row
            continue
        bs_, be_ = mp[a][0], mp[b - 1][1]
        why = check(raw, bs_, be_)
        while why and row['saved']:                       # an extension would cross an element: the one before it
            back = row['saved'].pop()
            for r in row['joined'][back['joined']:]:
                r['rule'] = PART
            row.update({k: v for k, v in back.items() if k != 'joined'})
            row['joined'] = row['joined'][:back['joined']]
            a, b = row['start'], row['end']
            row['text'] = show(s[a:b])
            bs_, be_ = mp[a][0], mp[b - 1][1]
            why = check(raw, bs_, be_)
        if not why and re.match(r'\.\d', s[b:b + 2]):
            why = 'its number runs on past where a bibl can end'
        if why and why.startswith('left'):
            row['rule'] = why
            yield 'left', row
            continue
        if why:
            row['reason'] = why
            yield 'residue', row
            continue
        taken.append((a, b, row))
        k = on_source(s, a, b)
        if k is not None:                               # quoted through another (X ap. Y): on its source, the dictionary's way
            a, bs_ = k, mp[k][0]
            row['start'] = a
            if row['n'] and not agrees(row['n'], show(s[a:b])):
                row['n'] = ''
            if not row['n']:
                row['n'], why = table_n(s, a, b, T, pat, author_before(raw, bs_, T))
                row['n'] = row['n'] or ''
                row['rule'] = row['rule'].replace('by the table: ', '') + ('; by the table: ' + why if row['n'] else '')
            row['rule'] += '; on its source after ap.'
        row['bytes'] = (bs_, be_)
        row['text'] = show(s[a:b])                      # as marked, with what it joined
        yield 'mark', row


TAGRE = re.compile(rb'<(/?)([A-Za-z][\w:.-]*)[^>]*?(/?)>')


def check(raw, a, b):
    """Why a bibl may not stand on raw[a:b], or None: its tags must pair up and be author or title
    elements, and its parent one where the dictionary's bibls stand."""
    st = []
    for m in TAGRE.finditer(raw, a, b):
        cl, name, sc = m.group(1), m.group(2).decode(), m.group(3)
        if name not in INSIDE:
            return 'would hold a <%s>, which a bibl does not' % name
        if sc:
            continue
        if not cl:
            st.append(name)
        elif not st or st.pop() != name:
            return 'would cross an element'
    if st:
        return 'would cross an element'
    st = []
    for m in TAGRE.finditer(raw, 0, a):
        cl, name, sc = m.group(1), m.group(2).decode(), m.group(3)
        if sc:
            continue
        if not cl:
            st.append(name)
        elif st and st[-1] == name:
            st.pop()
    if st and st[-1] in GRAMMAR:
        return 'left: stands in a <%s>, a grammatical person, number or the like, not a citation' % st[-1]
    if not st or st[-1] not in PARENTS:
        return 'would stand in a <%s>, where the dictionary has no bibl' % (st[-1] if st else 'nothing')
    return None


# ---------------------------------------------------------------- the readers' answers (night C)

HOLD = INSIDE | {'foreign', 'abbr', 'i'}       # what the dictionary's own bibls hold (foreign 9, abbr 4, i 1 of 455,349), and hi
SIGLUM = re.compile(rb'\s+<editor\b[^>]*>[^<]*\Z')


def tsv_rows(path):
    with open(path, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        return [dict(zip(head, line.rstrip('\n').split('\t'))) for line in f if line.strip()]


def answers_by_entry(answers_tsv, items_jsonl, key_tsv):
    """The readers' citations of certainty 4 or 5 on the residue, by (file, entry): the item's span (its
    offset and text in the entry's string over the dictionary's own bibls) and the printed citation."""
    items = {}
    with open(items_jsonl, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                it = json.loads(line)
                items[(it['entry'], it['span'])] = it
    key = {r['id']: r for r in tsv_rows(key_tsv)}
    out = collections.defaultdict(list)
    for r in tsv_rows(answers_tsv):
        it = items[(r['entry'], r['span'])]
        k = key[it['id']]
        if k['group'] != 'residue' or r['verdict'] not in ('citation', 'second address') or r['certainty'] not in ('4', '5') \
                or not r['printed'].strip():             # night C's brief gave a second address no printed span: not placed
            continue
        out[(it['file'], r['entry'])].append({
            'id': it['id'], 'kind': k['kind'], 'was': k['reason'], 'head': it['headword'], 'span': r['span'],
            'off': int(r['span'].split(':', 1)[0]), 'text': it['text'], 'printed': r['printed'].strip(),
            'ref': r['reference'].strip(), 'cert': r['certainty'], 'verdict': r['verdict']})
    return out


def locate(cands, sp):
    """The div2 the span stands in, and its offset there: at its offset (of two div2s with one
    orig_id, the one whose head is the item's), else the nearest place its text stands."""
    t = marker(sp['text'])
    at = [c for c in cands if c['s'].startswith(t, sp['off'])]
    if at:
        return next((c for c in at if c['head'] == sp['head']), at[0]), sp['off']
    near = sorted((abs(m.start() - sp['off']), k, m.start()) for k, c in enumerate(cands) for m in re.finditer(re.escape(t), c['s']))
    return (cands[near[0][1]], near[0][2]) if near else (None, None)


def printed_at(s, off, t, p):
    """The printed citation's place in the string: where it holds the span, else where it overlaps the
    span nearest; None where it does not stand at the span."""
    hits = [m.start() for m in re.finditer(re.escape(p), s)]
    end = off + len(t)
    pick = [o for o in hits if o <= off and end <= o + len(p)] or [o for o in hits if o < end and off < o + len(p)]
    return min(pick, key=lambda o: abs(o - off)) if pick else None


def open_at(raw, a, name):
    """The open tag of name that ends at byte a, or None."""
    m = re.search(rb'<' + re.escape(name.encode()) + rb'\b[^>]*>\Z', raw[max(0, a - 400):a])
    return m.group(0) if m and not m.group(0).endswith(b'/>') else None


def unmatched_close(raw, a, b, name):
    """The byte of a close tag of name in raw[a:b] whose element opens before a, where it is the first
    such close there; else None."""
    st = []
    for m in TAGRE.finditer(raw, a, b):
        cl, nm, sc = m.group(1), m.group(2).decode(), m.group(3)
        if sc:
            continue
        if not cl:
            st.append(nm)
        elif st:
            st.pop()
        else:
            return m.start() if nm == name else None
    return None


def place(raw, a, b):
    """Where a bibl may stand for the citation on raw[a:b]: ((a, b), None), widened over the tags at its
    edges where the citation begins or ends with an element's whole text, never over text; ((a, b),
    'already') where a bibl of this pass stands there; else (None, why not)."""
    while True:
        opened, closed = [], []
        for m in TAGRE.finditer(raw, a, b):
            cl, name, sc = m.group(1), m.group(2).decode(), m.group(3)
            if sc:
                continue
            if not cl:
                opened.append(name)
            elif opened:
                if opened.pop() != name:
                    return None, 'would cross an element'
            else:
                closed.append(name)
        if opened and raw.startswith(b'</%s>' % opened[-1].encode(), b):
            b += len(opened[-1]) + 3
        elif closed and open_at(raw, a, closed[0]):
            a -= len(open_at(raw, a, closed[0]))
        elif opened:
            return None, 'would cross a <%s>, which runs on past the citation' % opened[-1]
        elif closed:
            return None, 'would cross a <%s>, which begins before the citation' % closed[0]
        else:
            break
    m = ADDED.match(raw, a)                             # a whole bibl of this pass: marked on a run before (with its siglum outside)
    if m and m.group(1).decode() == PASS and raw.find(b'</bibl>', m.end()) + 7 == b:
        return (m.end(), b - 7), 'already'
    st = []
    for m in TAGRE.finditer(raw, 0, a):
        cl, name, sc = m.group(1), m.group(2).decode(), m.group(3)
        if sc:
            continue
        if not cl:
            st.append(name)
        elif st and st[-1] == name:
            st.pop()
    while st and st[-1] not in PARENTS and st[-1] != 'bibl':     # the citation all of its parent's text
        o = open_at(raw, a, st[-1])
        if not (o and raw.startswith(b'</%s>' % st[-1].encode(), b)):
            break
        a, b = a - len(o), b + len(st.pop()) + 3
    if st and st[-1] == 'bibl':
        o = open_at(raw, a, 'bibl')
        m = ADDED.match(o) if o and raw.startswith(b'</bibl>', b) else None
        return ((a, b), 'already') if m and m.group(1).decode() == PASS else (None, 'stands inside a bibl already there')
    if not st or st[-1] not in PARENTS:
        p = st[-1] if st else 'nothing'
        if p in GRAMMAR:
            return None, 'stands in a <%s>, a grammatical person, number or the like' % p
        return None, 'would stand in a <%s>, where the dictionary has no bibl' % p
    held = sorted({m.group(2).decode() for m in TAGRE.finditer(raw, a, b)} - HOLD)
    if 'bibl' in held:
        rule = all(ADDED.match(raw, m.start()) for m in re.finditer(rb'<bibl\b', raw[:b]) if m.start() >= a)
        return None, 'would hold a citation %s, a part of this one' % ('the rule marked' if rule else "of the dictionary's own")
    if held:
        return None, "would hold a %s, which the dictionary's bibls do not" % ', a '.join('<%s>' % x for x in held)
    return (a, b), None


def author_before(raw, at, T):
    """The author the citation before byte at names, as the rule's walk carries it (for Id.): a bibl
    a pass marked that names none (a bare number, ib.) or names Id. passes on the one before it."""
    for a, b in reversed([x for x in bibls(raw) if x[1] <= at]):
        x = T.info(raw, a, b)
        if not ADDED.match(raw, a) or x['key'] != '|' and x['author'] != 'Id.':
            return x['author']
    return ''


APS = re.compile(r'(?<![\w.])ap\.\s*')


def on_source(s, a, b):
    """Where the bibl of a citation quoted through another (X ap. Y) begins: at its source after the
    last ap., the quoted author outside, as the dictionary's own bibls stand (ap. <bibl> 8,571 times,
    X ap. inside one 3); None for any other citation."""
    ms = list(APS.finditer(s, a, b))
    return ms[-1].end() if ms and a < ms[-1].start() and ms[-1].end() < b else None


def table_n(s, pa, pb, T, pat, prev_author):
    """The table's n for the citation on s[pa:pb] where it is a name and a number the rule reads (A1,
    T1, A2), and why; else (None, '')."""
    m = pat.match(s, pa)
    hk = next((g for g in ('A1', 'T1', 'A2') if m and m.group(g)), None)
    G = {'A1': ('a1', 'g1', 'n1'), 'T1': ('t1', 'g2', 'n2'), 'A2': ('a2', 'g3', 'n3')}
    if not hk or m.end() != pb or len(m.group(G[hk][1])) > 25:
        return None, ''
    name, vt = m.group(G[hk][0]), tokens(m.group(G[hk][2]))
    title, via, page = gap_title(m.group(G[hk][1]))
    if hk == 'T1':
        key = '|' + (name + (' ' + title if title else ''))
    else:
        key = (prev_author if name == 'Id.' and prev_author else name) + '|' + title
    if page:
        vt = ['p'] + vt
    if via or (hk == 'T1' and re.fullmatch(r'[A-Z][a-z]?', name)):
        return None, ''
    w, why = T.resolve(key, vt)
    n = T.compose(key, w, vt) if w else None
    return n, why if n else ''


def answer_n(s, pa, pb, T, pat, ref, prev_author):
    """The n of a reader's citation: the reader's abo reference where the table fits it and the print
    agrees with it; else the table's, where the citation is a name and a number the rule reads (A1,
    T1, A2); else none. Where the two differ, none."""
    tn, why = table_n(s, pa, pb, T, pat, prev_author)
    rn = ref if ref.startswith('Perseus') else ''
    if rn:
        if not (T.fits(rn) and agrees(rn, show(s[pa:pb]))):
            return '', "the reader's citation, no n: its abo reference does not fit the table or the print"
        if tn and tn != rn:
            return '', "the reader's citation, no n: the table and the reader give different references"
        return rn, "the reader's citation, its abo reference"
    if tn:
        return tn, "the reader's citation, by the table: " + why
    return '', "the reader's citation, no abo reference"


def answers_pass(args):
    want = answers_by_entry(args.answers, args.items, args.key)
    data = {f: open(os.path.join(REPO, 'dictionary', f), 'rb').read() for f in FILES}
    T, vocab = Table(), collections.Counter()
    for f in FILES:
        for _, raw, oid in entries(data[f]):
            for a, b in own(raw, bibls(raw)):
                T.learn(T.info(raw, a, b))
            for m in re.finditer(rb'<author[^>]*>(.*?)</author>', raw, re.S):
                vocab[plain(m.group(1))] += 1
    pat = detector(vocab)
    rows = {'mark': [], 'residue': [], 'already': [], 'cont': [], 'moves': [], 'widened': []}
    new_data = {}
    for f in FILES:
        d = data[f]
        cands = collections.defaultdict(list)
        for start, raw, oid in entries(d):
            if (f, oid) in want:
                s, mp = build(raw, own(raw, bibls(raw)))
                hm = re.search(rb'<head[^>]*>(.*?)</head>', raw, re.S)
                cands[oid].append({'start': start, 'raw': raw, 'len': len(raw), 'oid': oid, 's': s, 'mp': mp,
                                   'head': plain(hm.group(1)) if hm else '', 'ins': [], 'mine': []})
        for oid in sorted(cands):
            for sp in want[(f, oid)]:
                row = dict(file=f, entry=oid, n='', **{k: sp[k] for k in ('id', 'kind', 'was', 'head', 'span', 'printed', 'ref', 'cert', 'verdict')})
                c, off = locate(cands[oid], sp)
                p = marker(sp['printed'])
                pa = printed_at(c['s'], off, marker(sp['text']), p) if c else None
                if c is None or pa is None:
                    row['reason'] = 'span not found again in the files' if c is None else 'the printed citation does not stand at the span'
                    rows['residue'].append(row)
                    continue
                raw, s, mp, pb = c['raw'], c['s'], c['mp'], pa + len(p)
                src = on_source(s, pa, pb)                      # quoted through another: the label on its source
                lo, a, b = mp[pa][0], mp[src if src is not None else pa][0], mp[pb - 1][1]
                if raw.startswith(b'</editor>', b) and SIGLUM.search(raw, a, b) and SIGLUM.search(raw, a, b).start() > a:
                    b = SIGLUM.search(raw, a, b).start()        # its editor's siglum outside, as the dictionary's own bibls have it
                work, moved_, q = raw, [], unmatched_close(raw, lo, b, 'cit')
                if q is not None:                               # the <cit> of the quotation closes inside its citation: after it
                    work, a, b = raw[:q] + raw[q + 6:], a - 6 * (a > q), b - 6 * (b > q)
                    moved_.append(('</cit>', 'the <cit> closed inside its citation'))
                at, why = place(work, a, b)
                gone = []
                inner = [(x, y) for x, y in bibls(work) if ADDED.match(work, x) and a <= x and y - 7 <= b]
                src = next(((x, y) for x, y in inner if re.fullmatch(rb'(?:\s+[A-Z][A-Za-z.-]{0,15})?', work[y:b] if y <= b else b'' if y - 7 == b else b'x')
                            and re.search(r'(?<![\w.])(?:in|post)\s*$', plain(work[max(0, x - 80):x]))), None)     # its editor after it, outside
                if (why or '').startswith('would hold a citation the rule marked') and src:   # X in Y, X post Y: the rule's label on the
                    at, why = (work.find(b'>', src[0]) + 1, src[1] - 7), 'already'          # source after them, as the dictionary's own stand
                elif (why or '').startswith('would hold a citation the rule marked'):   # the rule's own label on a part: the reader's span instead
                    for x, y in sorted(inner, reverse=True):
                        g = work.find(b'>', x) + 1 - x
                        gone.insert(0, plain(work[x + g:y - 7]))
                        work, b = work[:x] + work[x + g:y - 7] + work[y:], b - g - 7 * (y - 7 < b)
                    at, why = place(work, a, b)
                pm = re.match(rb'[.,;:]+(?=</foreign>)', work[b:b + 12]) if (why or '').startswith('would cross a <foreign>, which runs on') else None
                if pm:                                          # a <foreign> holding the stop after it: the stop out of it
                    work = work[:b] + b'</foreign>' + pm.group(0) + work[b + pm.end() + 10:]
                    moved_.append(('</foreign>', 'the <foreign> held the %s after its citation' % ('comma' if pm.group(0) == b',' else 'stop')))
                    at, why = place(work, a, b)
                if q is not None and at and why in (None, 'already'):   # the </cit> right after the citation's bibl
                    e = at[1] + (7 if why == 'already' else 0)
                    work = work[:e] + b'</cit>' + work[e:]
                wmp = build(work, own(work, bibls(work)))[1] if moved_ or gone else mp
                if at:                                          # the label in the string
                    ks = [k for k, sp_ in enumerate(wmp) if at[0] <= sp_[0] and sp_[1] <= at[1]]
                    la, lb = ks[0], ks[-1] + 1
                    row['text'] = show(s[la:lb])
                    if not why and re.match(r'\.\d', s[lb:lb + 2]):
                        at, why = None, 'its number runs on past where a bibl can end'
                same = next((r for r in c['ins'] if at and r['bytes'] == at), None)
                if at and not why and not same and any(at[0] < x[1] and x[0] < at[1] for x in (r['bytes'] for r in c['ins'])):
                    at, why = None, "overlaps another reader's citation"
                if why and why != 'already' and (moved_ or gone):   # a move or widening is made only for the label it lets stand
                    work, moved_, gone, wmp = raw, [], [], mp
                    if q is not None:
                        why += '; the <cit> before it closes inside it too'
                if moved_:                                      # the dictionary's markup before and after, the pass's tags out
                    R, W, lo_ = strip_added(raw), strip_added(work), len(strip_added(raw[:lo]))
                    suf = next(k for k in range(len(R)) if R[len(R) - 1 - k] != W[len(W) - 1 - k])
                    while suf and any(x[lo_:len(x) - suf].rfind(b'<') > x[lo_:len(x) - suf].rfind(b'>') for x in (R, W)):
                        suf -= 1                                # the snippets end on a whole tag
                    assert len(R) == len(W)
                    rows['moves'].append({'file': f, 'entry': oid, 'what moved': ', '.join(x for x, _ in moved_), 'from': R[lo_:len(R) - suf],
                                          'to': W[lo_:len(W) - suf], 'why': '; '.join(y for _, y in moved_), 'id': sp['id']})
                if moved_ or gone:
                    assert all(r['bytes'][1] <= lo for r in c['ins']) and all(x < lo for x in c['mine'])
                    assert build(work, own(work, bibls(work)))[0] == s
                    raw, mp = c['raw'], c['mp'] = work, wmp
                if gone:
                    rows['widened'].append({'file': f, 'entry': oid, 'id': sp['id'], 'gone': ' | '.join(gone)})
                if why == 'already' or same:
                    row['rule'] = 'already marked by this pass' + (' (item %s)' % same['id'] if same else '') \
                        + (", the rule's label on its source after in or post, as the dictionary's own bibls stand" if src and not same and at == (work.find(b'>', src[0]) + 1, src[1] - 7) else '')
                    rows['already'].append(row)
                    if why == 'already':
                        c['mine'].append(at[0] - len(open_at(raw, at[0], 'bibl')))
                    continue
                if why:
                    row['reason'] = why
                    rows['residue'].append(row)
                    continue
                if sp['verdict'] == 'second address':          # its own citation, with no reference, as the second pass marks them
                    row['n'], row['rule'] = '', "the reader's second address, its own citation"
                else:
                    row['n'], row['rule'] = answer_n(s, la, lb, T, pat, sp['ref'], author_before(raw, at[0], T))
                if src is not None:
                    row['rule'] += '; on its source after ap.'
                row['bytes'] = at
                c['ins'].append(row)
                rows['mark'].append(row)
                if moved_:
                    row['rule'] += '; ' + rows['moves'][-1]['why']
                if gone:
                    row['rule'] += "; widened over the rule's own label on a part of it (%s), which is gone" % ' | '.join(gone)
        pieces, pos = [], 0
        for c in sorted((c for cs in cands.values() for c in cs if c['ins'] or c['mine']), key=lambda c: c['start']):
            new = insert(c['raw'], c['ins'])
            mine = {moved(c['ins'], x) for x in c['mine']} | {moved(c['ins'], r['bytes'][0]) for r in c['ins'] if r.get('verdict') != 'second address'}
            for _ in range(3):                          # the comma-numbers after a reader's citation (C), as after the rule's marks
                more, nbs = [], bibls(new)
                for what, row in entry_marks(new, c['oid'], T, pat, [], collections.Counter()):
                    if what == 'mark' and row['kind'] == 'C' and nbs[before_mark(new, nbs, row['bytes'][0])][0] in mine:
                        row.update(file=f, entry=c['oid'], rule="after a reader's citation: " + row['rule'])
                        more.append(row)
                if not more:
                    break
                rows['cont'].extend(more)
                mine = {moved(more, x) for x in mine} | {moved(more, r['bytes'][0]) for r in more}
                new = insert(new, more)
            pieces += [d[pos:c['start']], new]
            pos = c['start'] + c['len']                 # the entry as it was in the file: a widening shortens its raw
        new_data[f] = b''.join(pieces) + d[pos:]
    os.makedirs(args.out, exist_ok=True)
    cols = ['file', 'entry', 'id', 'kind', 'text', 'n', 'rule']
    with open(os.path.join(args.out, 'labels.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in sorted(rows['mark'] + rows['already'], key=lambda r: r['id']) + rows['cont']:
            fh.write('\t'.join(str(r.get(c, '')).replace('\t', ' ') for c in cols) + '\n')
    cols = ['file', 'entry', 'headword', 'id', 'span', 'printed', 'reference', 'certainty', 'held because', "the rule's reason"]
    with open(os.path.join(args.out, 'residue-c.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in sorted(rows['residue'], key=lambda r: r['id']):
            fh.write('\t'.join(str(x).replace('\t', ' ') for x in (r['file'], r['entry'], r['head'], r['id'], r['span'], r['printed'],
                                                                   r['ref'], r['cert'], r['reason'], r['was'])) + '\n')
    cols = ['entry', 'what moved', 'from', 'to', 'why']
    with open(os.path.join(args.out, 'markup.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in sorted(rows['moves'], key=lambda r: r['id']):
            x = [r['entry'], r['what moved'], r['from'].decode(), r['to'].decode(), r['why']]
            assert not any('\t' in v or '\n' in v for v in x)
            fh.write('\t'.join(x) + '\n')
    summary = {
        'pass': PASS, 'answers': sum(len(v) for v in want.values()), 'marked': len(rows['mark']),
        'markup_moved': len(rows['moves']), 'markup_moved_by_what': dict(collections.Counter(r['what moved'] for r in rows['moves'])),
        'widened_over_rule_labels': len(rows['widened']), 'rule_labels_gone': sum(len(r['gone'].split(' | ')) for r in rows['widened']),
        'with_n': sum(1 for r in rows['mark'] if r['n']), 'already': len(rows['already']), 'held': len(rows['residue']),
        'continuations': len(rows['cont']), 'continuations_with_n': sum(1 for r in rows['cont'] if r['n']),
        'held_by_reason': dict(collections.Counter(r['reason'] for r in rows['residue']).most_common()),
        'marked_by_kind': dict(collections.Counter(r['kind'] for r in rows['mark']).most_common()),
        'marked_by_rule': dict(collections.Counter(r['rule'] for r in rows['mark']).most_common()),
        'marked_by_the_rule_s_reason': dict(collections.Counter(r['was'] for r in rows['mark']).most_common()),
        'entries_marked': len({(r['file'], r['entry']) for r in rows['mark']}),
        'inputs': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (args.answers, args.items, args.key)},
        'files_before': {f: hashlib.sha256(data[f]).hexdigest() for f in FILES},
    }
    if args.write:
        for f in FILES:
            if new_data[f] != data[f]:
                with open(os.path.join(REPO, 'dictionary', f), 'wb') as fh:
                    fh.write(new_data[f])
        summary['files_after'] = {f: hashlib.sha256(new_data[f]).hexdigest() for f in FILES}
    with open(os.path.join(args.out, 'labels.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ('answers', 'marked', 'with_n', 'already', 'held', 'held_by_reason', 'marked_by_kind',
                                              'entries_marked', 'continuations', 'markup_moved', 'markup_moved_by_what',
                                              'widened_over_rule_labels', 'rule_labels_gone')}, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- the run

# ---------------------------------------------------------------- the second pass: names cited by the word

LEXICA = {'Hsch.', 'Hesych.', 'Suid.', 'Phot.', 'EM', 'Et.Magn.', 'Et.Gud.', 'Zonar.', 'Gloss.', 'Erot.', 'Harp.',
          'Moer.', 'Ammon.', 'Thom.Mag.', 'Apollon.', 'Cyr.', 'Lex.Rhet.'}          # cited by the word
BY_PAGE = {'Eust.', 'Poll.', 'Hdn.Gr.', 'Choerob.', 'Theognost.', 'AB', 'Phryn.'}   # cited by page or number
GREEKW = r'[Ͱ-Ͽἀ-῿][Ͱ-Ͽἀ-῿ʼ’-]*'
NAME_TAILS = [(r' ?s\.\s?vv?\.\s?' + GREEKW + r'(?:,\s?' + GREEKW + r')*', 'with its s.v. and the word'),
              (r' ?s\.\s?vv?\.(?=[\s,;:)\]]|\.|$)', 'with its s.v.'),
              (r' ?(?:l\.\s?c\.|ll\.\s?cc\.|ad loc\.)', 'with its l.c.'),
              (r' [α-ω] \d+(?: [A-Z][a-z]{0,2}\.)?(?![\w])', 'with its letter and number'),
              (r' ?p\.\s?\d+[a-z]?(?: ?[A-Z][a-z]{0,2}\.)?(?![\w])', 'with its page'),               # Moer. p. 167P.
              (r' [ivx]{1,5} \d+(?![\w.])', 'with its volume and page')]                           # Gloss. iii 283
USAGE = re.compile(r'(?:freq\.|frequent(?:ly)?|often|common(?:ly)?|esp\.|mostly|usu\.|always|chiefly)\s(?:in|ap\.)\s$')
BRACKET = re.compile(r'([\[(])(\s*=?\s*)([^\[\]()⟦]{0,60}?)(\s*)([\])])')


def hits_cover(s, pat):
    """The census's cover of an entry's string (unmarked.py): every hit and its comma-numbers, the ib.s."""
    cov, pos = [], 0
    while True:
        m = pat.search(s, pos)
        if not m:
            break
        end = m.end()
        if not m.group('B'):
            g = m.group('g1') if m.group('A1') else m.group('g2') if m.group('T1') else m.group('g3')
            if len(g) > 25:
                pos = m.start() + 1
                continue
        while True:
            c = CONT.match(s, end)
            if not c:
                break
            end = c.end()
        cov.append((m.start(), end))
        pos = end
    for m in IB.finditer(s):
        if not any(a <= m.start() < b for a, b in cov):
            cov.append((m.start(), m.end()))
    return cov


def char_span(mp, a, b):
    """The characters of a string whose bytes lie in [a, b)."""
    i = next(k for k, sp in enumerate(mp) if sp[0] >= a)
    j = max(k for k, sp in enumerate(mp) if sp[1] <= b) + 1
    return i, j


def names_entry(raw, f, oid, pat, night, tally):
    """The second pass over one entry with the first pass's marks: [(what, row)], what mark, join,
    left or residue; a mark's bytes, a join's old and new open-tag places, every row's start and end
    in the string over the dictionary's own bibls (the night's and the packages' string)."""
    bs = bibls(raw)
    s, mp = build(raw, bs)                              # every bibl a mark: what is still outside
    so, mpo = build(raw, own(raw, bs))                  # the dictionary's own only: the packages' offsets
    marks = [m.start() for m in re.finditer('⟦B⟧', s)]
    out = []

    def row(kind, a_byte, b_byte, rule, **kw):
        i, j = char_span(mpo, a_byte, b_byte)
        r = {'file': f, 'entry': oid, 'kind': kind, 'text': show(so[i:j]), 'rule': rule, 'start': i, 'end': j, **kw}
        return r

    # joins: a first-pass mark of a name the night ruled a citation, an author right before it the reader's
    # reference begins with (Apollon. ⟦Lex. s.v. γραπτῦς⟧: the reference Apollon. Lex. s.v. γραπτῦς)
    joined_at = set()
    for sp in night.get('citation', []):
        if sp['kind'] != 'NAME':
            continue
        a, b, moved = find_span(so, sp, pat)
        if a is None:
            continue
        byte = mpo[a][0]
        k = next((k for k, (x, y) in enumerate(bs) if ADDED.match(raw, x) and raw.find(b'>', x) + 1 == byte), None)
        if k is None:
            continue
        m = re.search(r'\x02([^\x02\x03]{1,40})\x03 ?$', so[:a])
        if not m or not sp['ref'].replace(' ', '').startswith(m.group(1).replace(' ', '')):
            continue
        ab = mpo[m.start()][0]
        if any(x <= ab < y for x, y in bs):
            continue
        why = check(raw, ab, bs[k][0])                  # the stretch the mark takes on: the author and the space
        if why:
            out.append(('residue', row('join', ab, bs[k][1], why, id=sp['id'])))
            continue
        out.append(('join', row('join', ab, bs[k][1], "the night's citation, with the author before it its reader names", id=sp['id'],
                                old=(bs[k][0], raw.find(b'>', bs[k][0]) + 1), new_at=ab)))
        joined_at.add(ab)
    # second addresses the night read so: the content of their bracket, or the number after a =
    for sp in night.get('second address', []):
        a, b, moved = find_span(so, sp, pat)
        if a is None:
            out.append(('residue', {'file': f, 'entry': oid, 'kind': 'second address', 'text': sp['text'], 'rule': 'span not found again in the files',
                                    'start': '', 'end': '', 'id': sp['id']}))
            continue
        ab, bb = mpo[a][0], mpo[b - 1][1]
        if any(x <= ab < y for x, y in bs):
            out.append(('left', row(sp['kind'], ab, bb, 'left: already inside a bibl', id=sp['id'])))
            continue
        ext = None
        for m in BRACKET.finditer(so, max(0, a - 30), min(len(so), b + 40)):
            if m.start(3) <= a and b <= m.end(3):
                body = so[m.start(3):m.end(3)]
                if sp['kind'] == 'DOT' and re.fullmatch(r'(?:[A-Za-z][A-Za-z.]{0,10}\.?\s)?' + re.escape(so[a:b]) + r'(?:\s[A-Z][\w.]*\.?\??)?', body):
                    ext = (m.start(3), m.end(3), 'second address, the night\'s: its bracket\'s content')
                break
        if ext is None and sp['kind'] == 'DOT' and re.search(r'=\s?$', so[max(0, a - 3):a]) and re.match(r'[\s.,;:)]|$', so[b:b + 1]):
            ext = (a, b, "second address, the night's: the number after =")
        if ext is None:
            out.append(('residue', row(sp['kind'], ab, bb, 'second address the rule cannot bound (not one number in its bracket)', id=sp['id'])))
            continue
        xa, xb = mpo[ext[0]][0], mpo[ext[1] - 1][1]
        why = check(raw, xa, xb)
        if why:
            out.append(('residue', row(sp['kind'], ab, bb, why, id=sp['id'])))
            continue
        out.append(('mark', row('second address', xa, xb, ext[2], id=sp['id'], bytes=(xa, xb))))
    # the names: the census's lexicon class, outside every bibl and every hit
    cov = hits_cover(s, pat)
    not_cit = {(sp['kind'], sp['off']) for sp in night.get('not a citation', [])}
    for m in re.finditer('[\x02\x04]', s):
        if any(x <= m.start() < y for x, y in cov):
            continue
        z = s.find('\x03' if m.group(0) == '\x02' else '\x05', m.start())
        nm = s[m.start() + 1:z]
        if nm not in LEXICA | BY_PAGE:
            continue
        tally['names of the lexicon class'] += 1
        a, b = m.start(), z + 1
        ab, bb = mp[a][0], mp[b - 1][1]
        nxt, pre = s[b:b + 40], s[max(0, a - 40):a]
        if ab in joined_at:
            out.append(('left', row('NAME', ab, bb, 'left: joined to the first pass\'s mark after it')))
            continue
        i0, _ = char_span(mpo, ab, bb)
        if ('NAME', i0) in not_cit:
            out.append(('left', row('NAME', ab, bb, "left: the night ruled it not a citation")))
            continue
        if re.match(r'\s?ap\.?\s', nxt):
            out.append(('left', row('NAME', ab, bb, 'left: an attribution, quoted through the citation after it (ap.)')))
            continue
        if re.match(r'\s?(?:in|ad)\s?⟦B⟧', nxt):
            out.append(('left', row('NAME', ab, bb, 'left: a part of the citation after it (in, ad)')))
            continue
        if re.match(r'[\])]?\s?⟦B⟧', nxt):
            k = marks.index(s.index('⟦B⟧', b))
            if ADDED.match(raw, bs[k][0]):
                out.append(('residue', row('NAME', ab, bb, "right before a first-pass mark the night's reference does not join it to")))
            else:
                out.append(('left', row('NAME', ab, bb, "left: a part of the dictionary's own citation after it (its work's name outside the bibl)")))
            continue
        if USAGE.search(pre):
            out.append(('left', row('NAME', ab, bb, 'left: named for its usage (freq. in), no place')))
            continue
        rule, end = 'a lexicon cited by the word', b
        for tail, label in NAME_TAILS:
            t = re.match(tail, s[end:end + 80])
            if t:
                end += t.end()
                rule += ', ' + label
                break
        if nm in BY_PAGE and end == b:
            out.append(('residue', row('NAME', ab, bb, 'a work cited by page or number, standing alone (%s)' % nm)))
            continue
        if nm in BY_PAGE:
            rule = rule.replace('a lexicon cited by the word', 'a work cited by page, with a place by name')
        be = mp[end - 1][1]
        why = check(raw, ab, be)
        if why and end > b:                               # the tail would cross: the name alone
            end, be, rule = b, bb, rule.split(', with')[0]
            why = check(raw, ab, be)
            if nm in BY_PAGE:
                out.append(('residue', row('NAME', ab, be, 'a work cited by page or number, standing alone (%s)' % nm)))
                continue
        if why:
            out.append(('left' if why.startswith('left') else 'residue', row('NAME', ab, be, why)))
            continue
        if re.match(r'\.\d', s[end:end + 2]):
            out.append(('residue', row('NAME', ab, be, 'a number runs on after it')))
            continue
        out.append(('mark', row('NAME', ab, be, rule, bytes=(ab, be))))
    return out


def names_pass(args):
    """--names: the second pass, on the files with the first pass's marks."""
    spans = spans_by_entry(args.spans, args.items)
    data = {f: open(os.path.join(REPO, 'dictionary', f), 'rb').read() for f in FILES}
    if not any(re.search(rb'resp="' + PASS.encode() + rb'"', d) for d in data.values()):
        sys.exit('the files hold no marks of %s: the first pass comes first' % PASS)
    vocab, tally = collections.Counter(), collections.Counter()
    for f in FILES:
        for _, raw, oid in entries(data[f]):
            for m in re.finditer(rb'<author[^>]*>(.*?)</author>', raw, re.S):
                vocab[plain(m.group(1))] += 1
    pat = detector(vocab)
    os.makedirs(args.out, exist_ok=True)
    rows = {'mark': [], 'join': [], 'residue': [], 'left': []}
    new_data = {}
    for f in FILES:
        d = data[f]
        pieces, at = [], 0
        for start, raw, oid in entries(d):
            if not oid:
                continue
            night = collections.defaultdict(list)
            for sp in spans.get((f, oid), []):
                night[sp['verdict']].append(sp)
            got = names_entry(raw, f, oid, pat, night, tally)
            taken, edits = [], []
            for what, r in sorted(got, key=lambda w: (w[1]['start'] if w[1]['start'] != '' else -1)):
                if what in ('mark', 'join'):
                    a = r['bytes'][0] if what == 'mark' else r['new_at']
                    b = r['bytes'][1] if what == 'mark' else r['old'][1]
                    if any(x < b and a < y for x, y in taken):
                        r['rule'] = 'overlaps another mark'
                        what = 'residue'
                    else:
                        taken.append((a, b))
                        if what == 'mark':                  # (place, end, order): at one place a close goes before an open
                            edits.append((b, b, 0, b'</bibl>'))
                            edits.append((a, a, 1, ('<bibl resp="%s">' % PASS).encode()))
                        else:
                            x, y = r['old']                 # the open tag moves to the author's start
                            edits.append((x, y, 2, b''))
                            edits.append((a, a, 1, raw[x:y]))
                rows[what].append(r)
            if edits:
                new = bytearray(raw)
                for x, y, o, t in sorted(edits, key=lambda e: (e[0], e[2]), reverse=True):
                    new[x:y] = t
                pieces.append(d[at:start])
                pieces.append(bytes(new))
                at = start + len(raw)
        pieces.append(d[at:])
        new_data[f] = b''.join(pieces)
    cols = ['file', 'entry', 'kind', 'text', 'rule', 'id', 'start', 'end']
    for what in rows:
        with open(os.path.join(args.out, what + 's.tsv' if what in ('mark', 'join') else what + '.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('\t'.join(cols) + '\n')
            for r in rows[what]:
                fh.write('\t'.join(str(r.get(c, '')).replace('\t', ' ') for c in cols) + '\n')
    summary = {'pass': PASS + ', the second (names)', 'marks': len(rows['mark']), 'joins': len(rows['join']),
               'marks_by_kind': dict(collections.Counter(r['kind'] for r in rows['mark']).most_common()),
               'marks_by_rule': dict(collections.Counter(r['rule'] for r in rows['mark']).most_common()),
               'names_marked_by_name': dict(collections.Counter(r['text'].split(' ')[0] for r in rows['mark'] if r['kind'] == 'NAME').most_common()),
               'residue': len(rows['residue']), 'residue_by_reason': dict(collections.Counter(r['rule'] for r in rows['residue']).most_common()),
               'left': len(rows['left']), 'left_by_rule': dict(collections.Counter(r['rule'] for r in rows['left']).most_common()),
               'entries_marked': len({(r['file'], r['entry']) for r in rows['mark'] + rows['join']}), 'tally': dict(tally),
               'inputs': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (args.spans, args.items)},
               'files_before': {f: hashlib.sha256(data[f]).hexdigest() for f in FILES}}
    if args.write:
        for f in FILES:
            if new_data[f] != data[f]:
                with open(os.path.join(REPO, 'dictionary', f), 'wb') as fh:
                    fh.write(new_data[f])
        summary['files_after'] = {f: hashlib.sha256(new_data[f]).hexdigest() for f in FILES}
    with open(os.path.join(args.out, 'marks.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ('marks', 'joins', 'marks_by_kind', 'residue', 'residue_by_reason', 'left', 'left_by_rule',
                                              'entries_marked', 'tally')}, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- the addresses, by the rule table (--table)

KUHN = re.compile(r'(\d+)(?:\s?\(([12])\))?\.(\d+)$')    # Gal. 11.127, 17(2).456: Kühn's volume, its part, and page
DOTS = re.compile(r'\d+[a-z]?(?:\.\d+[a-z]?)*$')          # 1.83, 4.32.11a, 158
PAGE = re.compile(r'p\.\s?(\d+(?:\.\d+)?)$')               # p.122, p.54.12
FOUND = ('exact', 'prefix')                                # Store.passage: the place itself, or the lines it opens


def load_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def label_parts(inner):
    """A label's name as printed (what stands up to its last <author> or <title>: Ps.-, the author, the
    title) and its number (the text after); a label with no name element is all number."""
    names = list(re.finditer(rb'<(author|title)\b[^>]*>.*?</\1>', inner, re.S))
    if not names:
        return '', plain(inner)
    return plain(inner[:names[-1].end()]), plain(inner[names[-1].end():])


def read_number(levels, text, prev):
    """The place a label's number names, as (the rule's fixed levels, the printed ones), or None: the
    printed form the rule does not read. levels: '=N' the printed numbers are the store's levels from the
    first, at least N of them ('=N-M': and at most M); 'p=N' the same after p.; 'kühn' Kühn's volume (its
    part in brackets: 17(2) is 17b) and page; 'F.=N' a fixed first level F before them; a + after them, a
    level the store divides into lettered parts (table_pass); a siglum after a space ('=1 D.') may end the
    number and is dropped.
    prev: the printed levels of the citation a bare number, ib. or Id. continues, whose leading levels
    complete a number shorter than the rule's least (Gal. 11.127, 130: 11.130; Stob. 4.32.11, 15:
    4.32.15); one as long or longer stands as printed, and one shorter than the citation before but not
    than the least (Com.Adesp. 22.41, 67: a fragment or a line) is not read."""
    form, _, siglum = levels.partition(' ')
    m = re.fullmatch(r'(?:(.+)\.)?(=|p=|kühn)(\d*)(?:-(\d+))?\+?', form)
    fixed, kind, least = (m.group(1).split('.') if m.group(1) else []), m.group(2), int(m.group(3) or 2)
    most = int(m.group(4)) if m.group(4) else 99
    t = re.sub(r'^ib\.\s*', '', text) if prev is not None else text
    if siglum and t.endswith(siglum):
        t = t[:-len(siglum)].rstrip()
    if kind == 'kühn':
        k = KUHN.match(t)
        if k:
            v, part, page = k.groups()
            if part and v not in ('17', '18'):
                return None
            parts = [v + ('ab'[int(part) - 1] if part else ''), page]
        elif prev is not None and re.fullmatch(r'\d+', t):
            parts = [t]
        else:
            return None
    else:
        if kind == 'p=':
            k = PAGE.match(t)
            if not k:
                return None
            t = k.group(1)
        if not DOTS.match(t):
            return None
        parts = t.split('.')
    if prev and len(parts) < least:
        parts = prev[:least - len(parts)] + parts
    elif prev and len(parts) < len(prev):
        return None
    return (fixed, parts) if least <= len(parts) <= most else None


def abo_n(wid, place):
    a, b = wid.split('.')
    return 'Perseus:abo:tlg,%s,%s:%s' % (a[3:], b[3:], ':'.join(place))


def table_pass(args):
    """The n of the labels the rule table names (tools/addresses.tsv), each verified in its store as the
    cutter will seek it; attributes only."""
    N = load_module(os.path.join(args.philology, 'Port', 'tools', 'citations', 'n1_package.py'), 'n1_package')
    P = load_module(os.path.join(REPO, 'tools', 'perseus_places.py'), 'perseus_places')
    store = N.Store(args.tlg)
    rules = {r['name']: r for r in tsv_rows(args.table)}
    keys = {}                                              # work -> its citations and their leading levels
    for r in rules.values():
        for wid in r['work'].split():
            if wid not in keys:
                first, last = store.works[wid][:2]
                ks = set()
                for L in range(first, last + 1):
                    parts = store.raw(L)[0].split('.')
                    ks.update('.'.join(parts[:j]) for j in range(1, len(parts) + 1))
                keys[wid] = ks
    data = {f: open(os.path.join(REPO, 'dictionary', f), 'rb').read() for f in FILES}
    rows, tally = [], collections.Counter()
    for f in FILES:
        for start, raw, oid in entries(data[f]):
            prev, prev_end = None, 0                       # (rule, printed levels or None) of the label just read
            for s, e in bibls(raw):
                if not ADDED.match(raw, s):                # one of the dictionary's own: no bare number after it continues a label
                    prev = None
                    continue
                head = raw[s:raw.find(b'>', s) + 1]
                name, number = label_parts(raw[s + len(head):e - 7])
                has_n = bool(attrs(head).get('n', '').strip())
                follow = (name in ('', 'Id.') and prev is not None and re.match(r'(?:ib\.\s*)?\d', number)
                          and not re.search(rb'<(?:author|title)\b', raw[prev_end:s]))
                rule = prev[0] if follow else rules.get(name)
                prev_end = e
                if rule is None:
                    prev = None
                    continue
                if follow and prev[1] is None:
                    got, why = None, 'continues a citation whose number the rule does not read'
                else:
                    got = read_number(rule['levels'], number, prev[1] if follow else None)
                    why = '' if got else 'the printed form the rule does not read'
                prev = (rule, got[1] if got else None)
                row = {'file': f, 'entry': oid, 'at': start + s, 'name': rule['name'], 'printed': plain(raw[s:e]),
                       'follow': 'yes' if follow else '', 'source': rule['source'], 'place': '', 'n': '',
                       'result': '', 'why': why, 'how': '', 'lines': ''}
                if got:
                    place = got[0] + got[1]
                    row['place'] = '.'.join(place)
                    held = [w for w in rule['work'].split() if row['place'] in keys[w]]
                    if not held and rule['levels'].split(' ')[0].endswith('+'):
                        # a level the store divides into lettered parts, its places numbered on (Stob. 4.22 in
                        # 4.22a to 4.22g, sections 1-27, 28-66, ...): the one part that holds the place
                        alt = {(w, '.'.join(place[:i] + [place[i] + x] + place[i + 1:])) for w in rule['work'].split()
                               for i in range(len(place) - 1) for x in 'abcdefghijklmnopqrstuvwxyz'
                               if '.'.join(place[:i] + [place[i] + x] + place[i + 1:]) in keys[w]}
                        if len(alt) == 1:
                            w, row['place'] = alt.pop()
                            place, held = row['place'].split('.'), [w]
                            row['why'] = 'in a lettered part of the level'
                        elif alt:
                            row['why'] = 'held by %d lettered parts' % len(alt)
                    if len(held) != 1:
                        row['why'] = row['why'] or ('no work of the rule holds the place' if not held else 'held by %d works: %s' % (len(held), ' '.join(held)))
                    else:
                        n = abo_n(held[0], place)
                        ref = P.abo(n)                     # as the cutter reads it: the abo work in CTS form, the locus as the store's levels
                        if not ref or ref[1] != held[0] or ref[2] != place:
                            row['why'] = 'the n does not read back as its work and place'
                        else:
                            row['n'], row['work'] = n, held[0]
                if has_n:
                    row['result'] = 'has an n'
                    row['n'] = attrs(head)['n']
                elif not got:
                    row['result'] = 'skipped'
                elif not row['n']:
                    row['result'] = 'unresolved'
                else:
                    row['result'] = 'resolved'
                rows.append(row)
    # every n verified in its store as the cutter seeks it, work by work (the store keeps the last work's citations)
    for row in sorted((r for r in rows if r['result'] == 'resolved'), key=lambda r: r['work']):
        lines, how = store.passage(row['work'], row['place'])
        row['how'] = how
        if lines and how in FOUND:
            row['lines'] = '%s %d' % (store.raw(lines[0])[0], len(lines))
        else:
            row.update(result='unresolved', n='', why='the store does not give its lines (%s)' % (how or 'none'))
    for r in rows:
        tally[(r['name'], r['result'])] += 1
    # the outputs
    os.makedirs(args.out, exist_ok=True)
    cols = ['file', 'entry', 'at', 'name', 'printed', 'follow', 'source', 'place', 'n', 'result', 'why', 'how', 'lines']
    with open(os.path.join(args.out, 'labels-n.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r.get(c, '')).replace('\t', ' ') for c in cols) + '\n')
    by = collections.defaultdict(collections.Counter)
    for r in rows:
        by[r['name']][r['result']] += 1
        by[r['name']]['follow-ons ' + r['result']] += r['follow'] == 'yes'
    summary = {'pass': 'table', 'labels': sum(1 for r in rows if r['result'] != 'has an n'),
               'resolved': sum(1 for r in rows if r['result'] == 'resolved'),
               'unresolved': sum(1 for r in rows if r['result'] == 'unresolved'),
               'skipped': sum(1 for r in rows if r['result'] == 'skipped'),
               'with an n already': sum(1 for r in rows if r['result'] == 'has an n'),
               'by name': {k: {kk: vv for kk, vv in v.items() if vv} for k, v in sorted(by.items(), key=lambda t: -sum(t[1].values()))},
               'inputs': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (args.table,)},
               'files_before': {f: hashlib.sha256(data[f]).hexdigest() for f in FILES}}
    if args.write:
        at = collections.defaultdict(list)
        for r in rows:
            if r['result'] == 'resolved':
                at[r['file']].append((r['at'], r['n']))
        old = ('<bibl resp="%s">' % PASS).encode()
        for f, xs in at.items():
            d = bytearray(data[f])
            for a, n in sorted(xs, reverse=True):
                if bytes(d[a:a + len(old)]) != old:
                    sys.exit('not a label with no n at %s:%d' % (f, a))
                d[a:a + len(old)] = opentag(n)
            with open(os.path.join(REPO, 'dictionary', f), 'wb') as fh:
                fh.write(bytes(d))
        summary['files_after'] = {f: hashlib.sha256(open(os.path.join(REPO, 'dictionary', f), 'rb').read()).hexdigest() for f in FILES}
    with open(os.path.join(args.out, 'addresses.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ('labels', 'resolved', 'unresolved', 'skipped', 'with an n already')}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--spans', help="the spans night's spans.tsv")
    ap.add_argument('--names', action='store_true', help="the second pass, on the files with the first pass's marks")
    ap.add_argument('--answers', help="the readers' answers on the residue (night C's marks-c.tsv)")
    ap.add_argument('--items', help="the package's items.jsonl: the spans package's, or with --answers night C's")
    ap.add_argument('--key', help="with --answers, the package's key, which says the residue's items (nightc-key.tsv)")
    ap.add_argument('--out', help='where marks.tsv, residue.tsv, left.tsv and marks.json go (with --answers labels.tsv, residue-c.tsv, labels.json)')
    ap.add_argument('--write', action='store_true', help='write the marks into the files')
    ap.add_argument('--check', help='a directory holding the files before: check the files here against them')
    ap.add_argument('--moves', help="with --check, the markup moved since the files before (corrections/markup.tsv): undone before comparing")
    ap.add_argument('--table', help='the rule table (tools/addresses.tsv): write the n of the labels it names')
    ap.add_argument('--philology', help='with --table, Philology-fable (its Store reads the stores)')
    ap.add_argument('--tlg', help='with --table, the TLG-E store')
    args = ap.parse_args()
    if args.check:
        return verify(args.check, args.moves)
    if args.table:
        if not (args.philology and args.tlg and args.out):
            ap.error('--table needs --philology, --tlg and --out')
        return table_pass(args)
    if args.answers:
        if not (args.items and args.key and args.out):
            ap.error('--answers needs --items, --key and --out')
        return answers_pass(args)
    if args.names:
        if not (args.spans and args.items and args.out):
            ap.error('--names needs --spans, --items and --out')
        return names_pass(args)
    if not (args.spans and args.items and args.out):
        ap.error('--spans, --items and --out, or --check')
    spans = spans_by_entry(args.spans, args.items)
    data = {f: open(os.path.join(REPO, 'dictionary', f), 'rb').read() for f in FILES}
    if any(ADDED.search(d) and re.search(rb'resp="' + PASS.encode() + rb'"', d) for d in data.values()):
        sys.exit('the files already hold marks of %s: run on the files before' % PASS)
    T, vocab, tally = Table(), collections.Counter(), collections.Counter()
    for f in FILES:
        for _, raw, oid in entries(data[f]):
            bs = bibls(raw)
            for a, b in own(raw, bs):
                T.learn(T.info(raw, a, b))
            for m in re.finditer(rb'<author[^>]*>(.*?)</author>', raw, re.S):
                vocab[plain(m.group(1))] += 1
    pat = detector(vocab)
    os.makedirs(args.out, exist_ok=True)
    rows = {'mark': [], 'residue': [], 'left': []}
    new_data, seen_span = {}, set()
    for f in FILES:
        d = data[f]
        pieces, at = [], 0
        for start, raw, oid in entries(d):
            if not oid:
                continue
            sps = spans.get((f, oid), [])
            sps = [sp for sp in sps if (f, oid, sp['id']) not in seen_span]
            s0 = census_build(raw, bibls(raw))
            s1, mp = build(raw, bibls(raw))
            if s0 != s1:
                tally['entries whose string differs from the census build'] += 1
                print('string differs from the census build:', f, oid, file=sys.stderr)
            ins = []
            for what, row in entry_marks(raw, oid, T, pat, sps, tally):
                if row.get('id'):
                    seen_span.add((f, oid, row['id']))
                row.update(file=f, entry=oid)
                rows[what].append(row)
                if what == 'mark':
                    ins.append(row)
            if ins:
                new = insert(raw, ins)
                for _ in range(3):                       # the comma-numbers after a new mark (C), which only then stand after a bibl
                    more = []
                    nbs = bibls(new)
                    for what, row in entry_marks(new, oid, T, pat, [], collections.Counter()):
                        if what == 'mark' and row['kind'] == 'C' and ADDED.match(new, nbs[before_mark(new, nbs, row['bytes'][0])][0]):
                            row.update(file=f, entry=oid, rule='after a new mark: ' + row['rule'])
                            more.append(row)
                    if not more:
                        break
                    rows['mark'].extend(more)
                    new = insert(new, more)
                pieces.append(d[at:start])
                pieces.append(new)
                at = start + len(raw)
        pieces.append(d[at:])
        new_data[f] = b''.join(pieces)
    left_spans = sum(len(v) for v in spans.values()) - len(seen_span)
    # the outputs
    cols = ['file', 'entry', 'kind', 'text', 'n', 'rule', 'id']
    with open(os.path.join(args.out, 'marks.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows['mark']:
            fh.write('\t'.join(str(r.get(c, '')).replace('\t', ' ') for c in cols) + '\n')
    for what, extra in (('residue', 'reason'), ('left', 'rule')):
        with open(os.path.join(args.out, what + '.tsv'), 'w', encoding='utf-8') as fh:
            c2 = ['file', 'entry', 'kind', 'text', 'n', extra, 'id', 'ref', 'start', 'end']   # start, end: in the entry's string
            fh.write('\t'.join(c2) + '\n')
            for r in rows[what]:
                fh.write('\t'.join(str(r.get(c, '') or '').replace('\t', ' ') for c in c2) + '\n')
    summary = {
        'pass': PASS, 'marks': len(rows['mark']), 'with_n': sum(1 for r in rows['mark'] if r['n']),
        'without_n': sum(1 for r in rows['mark'] if not r['n']),
        'marks_by_kind': dict(collections.Counter(r['kind'] for r in rows['mark']).most_common()),
        'marks_by_kind_with_n': dict(collections.Counter(r['kind'] for r in rows['mark'] if r['n']).most_common()),
        'marks_by_rule': dict(collections.Counter(r['rule'] for r in rows['mark']).most_common()),
        'residue': len(rows['residue']), 'residue_by_reason': dict(collections.Counter(r['reason'] for r in rows['residue']).most_common()),
        'left': len(rows['left']), 'left_by_rule': dict(collections.Counter(r['rule'] for r in rows['left']).most_common()),
        'entries_marked': len({(r['file'], r['entry']) for r in rows['mark']}),
        'spans_not_reached': left_spans, 'tally': dict(tally),
        'table': {'works': len(T.works), 'keys': len(T.K)},
        'inputs': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (args.spans, args.items)},
        'files_before': {f: hashlib.sha256(data[f]).hexdigest() for f in FILES},
    }
    if args.write:
        for f in FILES:
            if new_data[f] != data[f]:
                with open(os.path.join(REPO, 'dictionary', f), 'wb') as fh:
                    fh.write(new_data[f])
        summary['files_after'] = {f: hashlib.sha256(new_data[f]).hexdigest() for f in FILES}
    with open(os.path.join(args.out, 'marks.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ('marks', 'with_n', 'without_n', 'marks_by_kind', 'residue', 'residue_by_reason',
                                              'left', 'left_by_rule', 'entries_marked', 'spans_not_reached', 'tally')}, ensure_ascii=False, indent=1))


def opentag(n):
    return ('<bibl resp="%s"%s>' % (PASS, ' n="%s"' % html.escape(n, quote=True) if n else '')).encode()


def insert(raw, rows):
    """raw with each row's bibl tags put in at its bytes."""
    new = bytearray(raw)
    for row in sorted(rows, key=lambda r: r['bytes'][0], reverse=True):
        a, b = row['bytes']
        new[b:b] = b'</bibl>'
        new[a:a] = opentag(row['n'])
    return bytes(new)


def moved(rows, at):
    """Where byte at of raw stands once insert() has put in rows' tags, at outside every row."""
    return at + sum(len(opentag(r['n'])) + 7 for r in rows if r['bytes'][1] <= at)


def before_mark(raw, bs, at):
    """The index of the last bibl ending at or before byte at."""
    return max(k for k, (a, b) in enumerate(bs) if b <= at)


def strip_added(d):
    """The files with the added bibls' tags taken out: the open tag of a pass and its </bibl>."""
    out, i = [], 0
    for m in ADDED.finditer(d):
        close = d.find(b'</bibl>', m.end())
        out.append(d[i:m.start()])
        out.append(d[m.end():close])
        i = close + 7
    out.append(d[i:])
    return b''.join(out)


def verify(before, moves=None):
    tally = collections.Counter()
    undo = collections.defaultdict(list)                 # the markup moved (corrections/markup.tsv), entry by entry
    for r in tsv_rows(moves) if moves else []:
        undo[r['entry']].append((r['to'].encode(), r['from'].encode()))
    for f in FILES:
        old = open(os.path.join(before, f), 'rb').read()
        new = open(os.path.join(REPO, 'dictionary', f), 'rb').read()
        parts, pos, at = [], 0, collections.defaultdict(list)
        for start, raw, oid in entries(new):            # each move undone in its own entry (an orig_id may name two)
            parts += [new[pos:start], strip_added(raw)]
            at[oid].append(len(parts) - 1)
            pos = start + len(raw)
        parts.append(new[pos:])
        for oid in at.keys() & undo.keys():
            for to, frm in undo[oid]:
                k = [j for j in at[oid] if parts[j].count(to) == 1]
                if len(k) != 1:
                    tally['markup moves not found once'] += 1
                    continue
                parts[k[0]] = parts[k[0]].replace(to, frm)
                tally['markup moves undone'] += 1
        back = strip_added(b''.join(parts))
        if back != strip_added(old):
            tally['files not the files before once the added tags are out' + (' and the moves undone' if moves else '')] += 1
        olds = {(k, oid): raw for k, (_, raw, oid) in enumerate(entries(old))}
        news = {(k, oid): raw for k, (_, raw, oid) in enumerate(entries(new))}
        if olds.keys() != news.keys():
            tally['files whose entries differ'] += 1
            continue
        for key, raw in news.items():
            o = olds[key]
            tally['entries'] += 1
            if raw == o:
                continue
            tally['entries changed'] += 1
            if TAGB.sub(b'', raw) != TAGB.sub(b'', o):
                tally['entries whose plain text differs'] += 1
            try:
                ET.fromstring(raw.decode('utf-8'))
            except ET.ParseError:
                tally['entries not well formed'] += 1
            ob, nb = bibls(o), bibls(raw)
            if [o[a:b] for a, b in own(o, ob)] != [raw[a:b] for a, b in own(raw, nb)]:
                tally["entries whose own bibls differ"] += 1
            prior = [o[a:b] for a, b in ob if ADDED.match(o, a)]
            added = [raw[a:b] for a, b in nb if ADDED.match(raw, a)]
            unn = lambda x: re.sub(rb'^(<bibl\b[^>]*?)\s+n="[^"]*"', rb'\1', x)
            inner = lambda x: x[x.find(b'>') + 1:-7]
            j = 0
            for x in prior:                              # each still there, in order: the same but for its n,
                while j < len(added):                    # widened over what it held, or moved onto its source
                    y = added[j]
                    how = ('kept' if unn(y) == unn(x) else 'widened' if inner(x) in inner(y)
                           else 'onto its source' if inner(x).endswith(inner(y)) and re.search(rb'(?<![\w.])ap\.', inner(x)[:len(inner(x)) - len(inner(y))])
                           else None)
                    if how:
                        break
                    j += 1
                if j == len(added):
                    tally['entries whose bibls added before are not all kept'] += 1
                    break
                tally['bibls added before, ' + how] += 1
                tally['bibls added before whose n changed'] += how == 'kept' and added[j] != x
                j += how != 'widened'                    # a wider bibl may hold more than one before it
            tally['bibls added'] += len(added) - len(prior)
            tally['bibls added, nested'] += sum(1 for x in added if x.count(b'<bibl') > 1)
    print(json.dumps(dict(tally), indent=1))
    bad = [k for k in tally if 'differ' in k or 'not' in k or 'nested' in k]
    return 1 if any(tally[k] for k in bad) else 0


if __name__ == '__main__':
    sys.exit(main())
