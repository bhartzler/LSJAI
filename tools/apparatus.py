"""The corrections as an apparatus (Bruce, 2 Nov 2026: an LSJ with an apparatus criticus): one line a change, the word before and the word after as an apparatus
entry with its sigla, the kind of change, the certainty, the printed page and the scan, and
one sentence of why.

Reads docs/entries/*.json (built by site/build.py: each corrected entry carries its rows, the
word-level marks from the diff against LSJLogeion 5f4f476, and its place on the scan) and writes
corrections/apparatus.tsv: entry, headword, apparatus, kind, certainty, page, scan, before,
after, why.

The sigla: L is Logeion's text (LSJLogeion 5f4f476); B is copy B (the Internet Archive text of
2017, METHOD.md); pr. is the printed ninth edition, where the reader's evidence quotes its page
or scan; S is the 1968 Supplement; T is the text cited (the reader's record of the passage,
for a citation's number). The apparatus entry reads: the reading adopted, the sigla that give
it, a bracket, the reading replaced, its siglum: `POxy. B] FOxy. L`.

The kinds say which witness gives the adopted reading, no more: "copy B reads so, said to
have the print" (the reader judged B had the print without quoting the page: the kind to check against the page, since copy B supplements the print in places, as n66 ἀβαφής shows); "the printed page reads so" (the reader quoted the page or the scan); "the text cited
reads so" (a citation's number, from the passage); "the Supplement reads so"; "Logeion's
markup" (attributes and the like). A change to one of LSJ's conventions is not a kind this
tool can tell; a reader's pass against the scan will mark those.
"""
import glob, json, os, re, io
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAIL = re.compile(r'\S+$'); HEAD = re.compile(r'^\S+')
SCAN = 'https://archive.org/details/greekenglishlexi12lidd/page/n%d'


def word_pair(m):
    tail = TAIL.search(m.get('b', '')); head = HEAD.search(m.get('a', ''))
    tail = tail.group(0) if tail else ''; head = head.group(0) if head else ''
    return tail + m.get('o', '') + head, tail + m.get('t', '') + head


def sigla_of(src, quote, prt=''):
    """The sigla that give the adopted reading, from the row's evidence source and quote; since 2 Nov 2026 the
    print's own reading (corrections/corrections.tsv, column print: new, old, other, not visible, read by an AI reader
    from the scan's crop of the entry) outranks everything: pr. where the page prints our text, and where it
    prints Logeion's the row is one to withdraw."""
    q = quote or ''
    if prt == 'new':
        return 'pr.', 'the printed page reads so'
    if prt == 'old' and src in ('copy B', 'B', 'current', 'Logeion'):
        return 'B', "the printed page reads Logeion's text: withdraw"
    if prt == 'other':
        return (('T' if src.startswith("the readers' record") else 'B'), 'the printed page reads otherwise: a hand')
    if re.search(r'1968 Supplement', q):
        return 'S', 'the Supplement reads so'
    if src in ('copy B', 'B'):
        if re.search(r'printed page|the scan|page image', q, re.I):
            return 'B pr.', 'the printed page reads so'
        return 'B', 'copy B reads so, said to have the print'
    if src.startswith("the readers' record"):
        return 'T', 'the text cited reads so'
    if src in ('current', 'Logeion'):
        return 'L', "Logeion's markup"
    return src, ''


import csv
csv.field_size_limit(10**9)
prt = {}   # (entry, old, new) -> what the printed page reads (corrections.tsv, column print, since 2 Nov 2026)
with io.open(os.path.join(REPO, 'corrections', 'corrections.tsv'), encoding='utf-8') as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        prt[(r['entry'], r['old'], r['new'])] = r.get('print', '')
rows = []
for f in sorted(glob.glob(os.path.join(REPO, 'docs', 'entries', '*.json'))):
    for i, e in json.load(io.open(f, encoding='utf-8')).items():
        if not e.get('corr'):
            continue
        marks, used = e.get('marks') or [], set()
        page = e.get('page', '')
        scan = SCAN % (e['box'][0] - 1) if e.get('box') else ''
        for c in e['corr']:
            m = None
            for k, x in enumerate(marks):
                if k in used:
                    continue
                if c['new'] and x['t'] and (x['t'] == c['new'] or x['t'] in c['new'] or c['new'] in x['t']):
                    m = x; used.add(k); break
            if m is None:
                for k, x in enumerate(marks):
                    if k not in used and not c['new'] and not x['t']:
                        m = x; used.add(k); break
            if m is not None:
                before, after = word_pair(m)
            else:
                before, after = c['old'] or '(nothing)', c['new'] or '(nothing)'
            sg, kind = sigla_of(c.get('src', ''), c.get('quote', ''), prt.get((i, c.get('old', ''), c.get('new', '')), ''))
            app = '%s %s] %s L' % (after, sg, before)
            why = re.split(r'(?<=[.;])\s', c['why'].strip())[0] if c.get('why') else ''
            rows.append((i, e['head'], app, kind, c.get('sure', ''), page, scan, before, after, why))


def key(r):
    n = re.sub(r'\D', '', r[0]); return (int(n) if n else 0, r[0])


rows.sort(key=key)
out = os.path.join(REPO, 'corrections', 'apparatus.tsv')
with io.open(out, 'w', encoding='utf-8', newline='') as fh:
    fh.write('entry\theadword\tapparatus\tkind\tcertainty\tpage\tscan\tbefore\tafter\twhy\n')
    for r in rows:
        fh.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in r) + '\n')
import collections
print(len(rows), 'rows ->', out, '| kinds', dict(collections.Counter(r[3] for r in rows)))
