"""One text of ours for every citation, and its apparatus: the collation of every edition the cut
holds for the place (Bruce, 2 Nov 2026: "we say how OUR text we make however we make it, differs or
not from another in a certain way, with links to both"; the box shows one Greek text, the cited word
marked, under it one apparatus line where any witness differs, each siglum linked to its source, a
conspectus of the witnesses consulted when none differs).

The stages (Bruce, 2 Nov 2026): the cut writes every citation into the collection folders as it
does (docs/snippets/<collection>/<block>.json, the store for checking the word against each text
and translation); this tool joins those editions into a single text with its apparatus for the
page, docs/snippets/text/<block>.json, our version, the file the repository carries; the public
translations are copied beside it.

What a record holds: the citation's number and its chosen edition's metadata (status, kind, guess,
prefer, form, found, url, the collection as src), our constituted lines with their numbers, the
witnesses (name, collection, siglum, link, the lines it did not align to), and the apparatus (per
line: lemma, each variant with the witnesses that read it). The witnesses' full lines are not
stored, only the variant words: the apparatus is quotation-sized.

How the witnesses are compared (the algorithm the page ran at click time on 2 Nov 2026, moved here
so it runs once and can be counted): a line is cut into tokens at whitespace and after an apostrophe
(an elided word and the next are two tokens whatever the spacing); each token's key is its text in
Unicode NFD, apostrophes made one, iota subscript as adscript, punctuation removed, lower-cased, so
that the classes no edition means as a reading (the apostrophe's form, composition, oxia and tonos,
subscript and adscript, punctuation, capitals) never show as variants; a token that is punctuation
alone, a word the edition splits at the line's end (a trailing hyphen), and that word's tail at the
next line's start are left out of the comparison. A witness with the same line numbers is compared
line by line, with the line's edges; one that gives a sentence or a section (Perseus's prose, the
Loeb's) is aligned to the line inside its text, edges ignored; the alignment is a longest common
subsequence of keys, and a witness sharing fewer than half the line's words is "not aligned" there
and only named. This
text is the base's text, word for word: the base is the first edition that holds the place in the
order BASE (an open text first), a preview the
checks back before a guessed one (better()). No vote across witnesses: another edition's reading
never enters this text, it stands in the apparatus. The apparatus lists, at each word, the
witnesses that read otherwise, and the runs where a witness has more or fewer words (om., add.).

Usage: python3 -I tools/collate.py [--root docs/snippets] [--blocks 0592,0593]
"""
import argparse, collections, glob, importlib.util, io, json, os, re, unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = ['greek', 'loeb', 'perseus', 'first1k', 'digiliblt', 'papyri', 'inscriptions', 'latin']   # the page's order (Bruce, 1 Nov 2026): the witnesses after the base
BASE = ['perseus', 'first1k', 'papyri', 'inscriptions', 'latin', 'greek', 'loeb', 'digiliblt']   # the base on a tie: the open texts first, then the project's papyri, inscriptions, and Latin, then the editions given by link
BY_LINK = ('greek', 'loeb', 'digiliblt')   # the editions a record gives by its link; docs/snippets/text-all, on this machine only, keeps every record whole
OPEN = ('perseus', 'first1k')   # an open witness aligned on every line takes the base's place
NAMES = {'greek': 'TLG-E', 'loeb': 'Loeb', 'perseus': 'Perseus', 'first1k': 'First1KGreek', 'digiliblt': 'DigiLibLT',
         'papyri': 'DDbDP, PHI 7', 'inscriptions': 'PHI Inscriptions', 'latin': 'PHI Latin'}   # the makers named (Bruce, 2 Nov 2026)


def _cls(codes):
    return '[' + ''.join(re.escape(chr(c)) for c in codes) + ']'


# the character classes by code point, so that no quoting can bend them: the apostrophe's forms (right single
# quotation mark, koronis, modifier letter apostrophe, the ASCII apostrophe, psili as a letter, acute, grave)
APOS_CODES = (0x2019, 0x1FBF, 0x02BC, 0x27, 0x1FBD, 0xB4, 0x60)
APOS = re.compile(_cls(APOS_CODES))
APOS_SPLIT = ''.join(chr(c) for c in (0x2019, 0x1FBF, 0x02BC, 0x27, 0x1FBD))
PUNCT_CODES = tuple(ord(c) for c in '.,;:!?()[]<>{}*"') + (0xAB, 0xBB, 0x201C, 0x201D, 0x201E, 0x2039, 0x203A, 0x2020, 0x2021,
                                                            0x2014, 0x2013, 0x2026, 0xB7, 0x387, 0x2010, 0x2011, 0x2012, 0x2015)
PUNCT = re.compile(_cls(PUNCT_CODES))
PUNCT_END = re.compile(_cls(tuple(ord(c) for c in '.,;:!?)]') + (0xB7, 0xBB, 0x201C, 0x201D, 0x201E, 0x387)) + '+$')
YPOGEGRAMMENI, IOTA, HYPHEN, KERAIA = chr(0x345), chr(0x3B9), chr(0x2010), chr(0x374)
RUN_CAP = 6                                       # the most words of a witness's run the apparatus quotes; beyond it, their number
YEAR = re.compile(r'\b(1[5-9]\d\d|20\d\d)\b')
ED = re.compile(r'\bed\.\s*(.+)$')
SHELF_TAIL = re.compile(r'\s*\([^()]*\)\s*$')


def key_of(t):
    return PUNCT.sub('', APOS.sub("'", unicodedata.normalize('NFD', t)).replace(YPOGEGRAMMENI, IOTA)).lower()


def tokens_of(line):
    """The tokens of a line as printed: t, its place (i, e), the key compared (k), whether it is a word split at the line's end."""
    out = []
    for m in re.finditer(r'\S+', line):
        s, at, cut = m.group(0), m.start(), 0
        for i in range(len(s) - 1):
            if s[i] in APOS_SPLIT:
                out.append({'t': s[cut:i + 1], 'i': at + cut, 'e': at + i + 1}); cut = i + 1
        out.append({'t': s[cut:], 'i': at + cut, 'e': at + len(s)})
    for x in out:
        x['k'] = key_of(x['t']); x['split'] = x['t'].endswith('-') or x['t'].endswith(HYPHEN)
        letters = PUNCT.sub('', APOS.sub('', x['t'])).replace(KERAIA, '')
        x['speaker'] = 1 <= len(letters) <= 5 and letters.isupper()   # a speaker's label or a siglum in capitals (ΟΙ Β΄, ΔΗ., ΧΟ.) is not a reading
    return out


def lcs(a, b):
    """The pairs (i, j) of a longest common subsequence of two key lists (the page's tie-breaking kept)."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if a[i] == b[j] else max(L[i + 1][j], L[i][j + 1])
    out, i, j = [], 0, 0
    while i < n and j < m:
        if a[i] == b[j]:
            out.append((i, j)); i += 1; j += 1
        elif L[i + 1][j] >= L[i][j + 1]:
            i += 1
        else:
            j += 1
    return out


def comp_of(lines):
    """Per line its tokens and the indexes compared: not punctuation alone, not a word split at the line's end, nor its tail at the next line's start."""
    toks, comp = [], []
    for k, line in enumerate(lines):
        toks.append(None if line is None else tokens_of(line)); comp.append([])
        if toks[k] is None:
            continue
        prev = bool(k > 0 and toks[k - 1] and toks[k - 1][-1]['split'])
        first = True
        for i, x in enumerate(toks[k]):
            if not x['k'] or x['split'] or x['speaker']:
                continue
            if first and prev:
                first = False; continue
            first = False; comp[k].append(i)
    return toks, comp


def better(s, o):
    """site/build.py's better(): a preview marked prefer first, then one the checks back."""
    a, b = (bool(s.get('prefer')), not s.get('guess')), (bool(o.get('prefer')), not o.get('guess'))
    return a[0] if a[0] != b[0] else (a[1] and not b[1])


def sigla(ws):
    names = [NAMES.get(w['src'], w['src'] or '?') for w in ws]
    seen = collections.Counter(names)
    out = []
    for i, w in enumerate(ws):
        if seen[names[i]] < 2:
            out.append(names[i]); continue
        ys = YEAR.findall(w.get('source') or '')
        out.append(names[i] + ' ' + (ys[-1] if ys else chr(97 + i)))
    return out


def short_name(w):
    src = SHELF_TAIL.sub('', w.get('source') or '')
    m = ED.search(src)
    return (m.group(1) if m else src) + (' (%s)' % NAMES[w['src']] if w['src'] in NAMES else '')


def collate(s, others):
    """Our lines, the apparatus per line, and the witnesses' records, for a citation's chosen preview s and its other editions."""
    ws = [s] + others
    toks, comp = comp_of(s['lines'])
    read = []
    for w in ws:
        out = []
        for k in range(3):
            out.append(None)
            if toks[k] is None or not comp[k] or not w.get('lines') or not w.get('at'):
                continue
            wt, wc, line_mode = None, [], False
            if w['lines'][k] is not None and w['at'][k] == s['at'][k]:
                W = comp_of(w['lines']); wt, wc, line_mode = W[0][k], W[1][k], True
            elif w['lines'][1] and w['at'][0] is None:
                wt = tokens_of(w['lines'][1]); wc = [i for i, x in enumerate(wt) if x['k'] and not x['split'] and not x['speaker']]
            if wt is None:
                continue
            bk = [toks[k][i]['k'] for i in comp[k]]; wk = [wt[i]['k'] for i in wc]
            pairs = lcs(bk, wk)
            if len(pairs) < min(len(bk), max(2, (len(bk) + 1) // 2)):
                out[k] = False; continue
            at, runs = {}, []
            for bi, wj in pairs:
                at[bi] = wt[wc[wj]]
            pp = [(-1, -1)] + pairs + [(len(bk), len(wk))] if line_mode else pairs
            for p in range(len(pp) - 1):
                b1, b2, w1, w2 = pp[p][0] + 1, pp[p + 1][0], pp[p][1] + 1, pp[p + 1][1]
                if b2 == b1 and w2 == w1:
                    continue
                if b2 - b1 == w2 - w1:
                    for q in range(b2 - b1):
                        at[b1 + q] = wt[wc[w1 + q]]
                else:
                    runs.append({'from': b1, 'to': b2, 'text': ' '.join(PUNCT_END.sub('', wt[i]['t']) for i in wc[w1:w2])})
            out[k] = {'at': at, 'runs': runs}
        read.append(out)
    lines, app = [], []
    for k in range(3):
        if toks[k] is None:
            lines.append(None); app.append([]); continue
        ours = [toks[k][bi] for bi in comp[k]]          # this text is the base's text, word for word
        lines.append(s['lines'][k])
        by = {}
        for ci, bi in enumerate(comp[k]):
            o = ours[ci]
            for wi, r in enumerate(read):
                x = r[k] and r[k]['at'].get(ci)
                if not x or x['k'] == o['k']:
                    continue
                e = by.setdefault(ci, {'lem': PUNCT_END.sub('', o['t']), 'vars': {}, 'order': [], 'pos': ci})
                vt = PUNCT_END.sub('', x['t'])
                if vt not in e['vars']:
                    e['vars'][vt] = []; e['order'].append(vt)
                e['vars'][vt].append(wi)
        for wi, r in enumerate(read):
            if not r[k]:
                continue
            for run in r[k]['runs']:
                lem = ' '.join(PUNCT_END.sub('', toks[k][bi]['t']) for bi in comp[k][run['from']:run['to']])
                key = 'r%d-%d' % (run['from'], run['to'])
                e = by.get(key)
                if e is None:
                    before = PUNCT_END.sub('', toks[k][comp[k][run['from'] - 1]]['t']) if run['from'] > 0 else 'init.'
                    e = by[key] = {'lem': lem or ('post ' + before), 'vars': {}, 'order': [], 'pos': run['from'] + 0.5}
                words = run['text'].split()
                if len(words) > RUN_CAP:                  # a long run is not quoted: the apparatus stays quotation-sized (2 Nov 2026)
                    vt = '%d words differ' % len(words)
                else:
                    vt = (run['text'] if lem else 'add. ' + run['text']) if run['text'] else 'om.'
                if vt not in e['vars']:
                    e['vars'][vt] = []; e['order'].append(vt)
                e['vars'][vt].append(wi)
        app.append([[e['lem'], [[vt, e['vars'][vt]] for vt in e['order']]] for e in sorted(by.values(), key=lambda e: e['pos'])])
    sg = sigla(ws)
    wrec = []
    for wi, w in enumerate(ws):
        miss = [s['at'][k] for k in range(3) if read[wi][k] is False]
        wrec.append({'nm': short_name(w), 'sg': sg[wi], 'src': w['src'], 'url': w.get('url'), 'miss': miss})
    return lines, app, wrec


KEEP = ('n', 'status', 'kind', 'cite', 'urn', 'ref', 'source', 'at', 'form', 'found', 'url', 'guess', 'prefer', 'check')


def build_module():
    """site/build.py as a module: its guessed() and shelf constants, the one place the guess rule lives."""
    spec = importlib.util.spec_from_file_location('build', os.path.join(REPO, 'site', 'build.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def flag_guesses(got, B):
    """Mark each text record's guess as site/build.py marks it before writing the folders, so the base is chosen
    the same whether the collation runs before or after a build (the build adds the flags to the folders; a
    collation on fresh cut folders saw none and chose 2,800 bases otherwise, 2 Nov 2026)."""
    formed = {(i, x['n']) for src in got if src in B.TEXTS for i, v in got[src].items() for x in v if x.get('found')}
    for src in got:
        if src in B.TEXTS:
            for i, v in got[src].items():
                for x in v:
                    x.pop('guess', None)
                    g = B.guessed(x, src in B.SHELF and (i, x['n']) in formed)
                    if g:
                        x['guess'] = g


def by_link(r):
    """The record of a citation given by link: the citation and the witnesses with their links; no lines, no apparatus, no word found."""
    p = {k: v for k, v in r.items() if k != 'found'}
    p['lines'] = [None, None, None]; p['app'] = []
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.join(REPO, 'docs', 'snippets'))
    ap.add_argument('--blocks', default='', help='comma-separated block names to do (else every block)')
    ap.add_argument('--report', default='', help='write a TSV of every witness edition: how often it was a witness, not aligned, read otherwise (the check of the alignments)')
    a = ap.parse_args()
    by_ed = collections.defaultdict(lambda: [0, 0, 0, 0])   # (collection, edition name) -> [witness, not aligned, differs, base]
    out_dir = os.path.join(a.root, 'text'); os.makedirs(out_dir, exist_ok=True)
    all_dir = os.path.join(a.root, 'text-all'); os.makedirs(all_dir, exist_ok=True)
    names = sorted({os.path.basename(p) for src in SOURCES for p in glob.glob(os.path.join(a.root, src, '*.json'))})
    if a.blocks:
        want = set(a.blocks.split(',')); names = [n for n in names if n.replace('.json', '') in want]
    tally = collections.Counter(); pair = collections.Counter()
    B = build_module()
    for name in names:
        got = {}
        for src in SOURCES:
            p = os.path.join(a.root, src, name)
            if os.path.exists(p):
                with io.open(p, encoding='utf-8') as f:
                    got[src] = json.load(f)
        flag_guesses(got, B)
        ids = sorted({i for d in got.values() for i in d}, key=lambda x: (len(x), x))
        block = {}
        for i in ids:
            alls, pick = {}, {}
            for src in BASE:                              # the base: by better(), ties to the first in BASE
                for s in got.get(src, {}).get(i, ()):
                    s = dict(s); s['src'] = src
                    alls.setdefault(s['n'], []).append(s)
                    o = pick.get(s['n'])
                    if o is None or better(s, o):
                        pick[s['n']] = s
            for n in alls:                                # the witnesses after the base, in the page's order
                alls[n].sort(key=lambda s: SOURCES.index(s['src']))
            recs = []
            for n in sorted(pick):
                s = pick[n]; others = [x for x in alls[n] if x is not s]
                lines, app, wrec = collate(s, others)
                if s['src'] in BY_LINK:                       # an open witness aligned on every line takes the base's place
                    for wi, w in enumerate(wrec):
                        if wi and w['src'] in OPEN and not w['miss']:
                            o = others[wi - 1]; s, others = o, [s] + [x for x in others if x is not o]
                            lines, app, wrec = collate(s, others); tally['citations re-based on an open witness aligned on every line'] += 1
                            break
                if s['src'] in BY_LINK:
                    tally['citations given by link'] += 1
                r = {k: s[k] for k in KEEP if k in s}
                r.update({'src': s['src'], 'lines': lines, 'ws': wrec, 'app': app})
                recs.append(r)
                tally['citations'] += 1
                if len(wrec) > 1:
                    tally['citations with two witnesses or more'] += 1
                if any(app):
                    tally['citations with a variant'] += 1
                    differs = {wi for ln in app for e in ln for v in e[1] for wi in v[1]}
                    for wi in differs:
                        pair[(wrec[0]['src'], wrec[wi]['src'])] += 1
                differs = {wi for ln in app for e in ln for v in e[1] for wi in v[1]}
                for wi, w in enumerate(wrec):
                    row = by_ed[(w['src'], w['nm'])]
                    row[0] += 1
                    if w['miss']:
                        tally['witnesses not aligned on a line'] += 1; row[1] += 1
                    if wi in differs:
                        row[2] += 1
                    if wi == 0:
                        row[3] += 1
            block[i] = recs
        with io.open(os.path.join(all_dir, name), 'w', encoding='utf-8') as f:     # everything, this machine only
            json.dump(block, f, ensure_ascii=False, separators=(',', ':'))
        public = {i: [by_link(r) if r['src'] in BY_LINK else r for r in recs] for i, recs in block.items()}
        with io.open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f:     # the repository's tree
            json.dump(public, f, ensure_ascii=False, separators=(',', ':'))
    if a.report:
        with io.open(a.report, 'w', encoding='utf-8') as f:
            f.write('collection\tedition\twitness\tnot aligned\treads otherwise\tbase\n')
            for (src, nm), (n, miss, diff, base) in sorted(by_ed.items(), key=lambda x: (-x[1][1], -x[1][0])):
                f.write('%s\t%s\t%d\t%d\t%d\t%d\n' % (NAMES.get(src, src), nm, n, miss, diff, base))
    for k, v in sorted(tally.items()):
        print('%s\t%d' % (k, v))
    for (a_, b_), v in sorted(pair.items(), key=lambda x: -x[1]):
        print('variants: %s reads otherwise, %s chosen\t%d' % (NAMES.get(b_, b_), NAMES.get(a_, a_), v))


if __name__ == '__main__':
    main()
