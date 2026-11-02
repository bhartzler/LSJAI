#!/usr/bin/env python3
"""The citations with no text and the place guesses, by work and by reason, and which of them one
numbering rule would place. A measure, no reader.

    python3 -I tools/worklist.py --philology <Philology-fable> --tlg <TLG-E store> \\
        --masters <Philology-masters> [--repo .] --out worklist.tsv --citations worklist-citations.tsv \\
        [--json counts.json]

The citations. Every <bibl> of greatscott01.xml to greatscott86.xml (the page's n-th <cite>). One has
a text when a preview of it stands in docs/snippets/perseus, first1k, greek or latin; one is a place
guess when the preview the page shows (site/build.py's chosen() and guessed()) is guessed `place`.

The reasons, for a citation with no text, from the lexicon's citation sidecar
(Lexicon/lsj/citations.txt: the bibl's place in TLG-E's numbering and its status):
  no reference       the bibl has no n, or an n naming no place (status none)
  work not held      no store holds the work (no-work); a papyrus apart (`work not held: papyrus`)
  numbering differs  the work is held (no-line) and the place has another shape than the held text's:
                     its first number is none the text has at its first level, or it has more levels
                     than the text, or a letter where the text has a number or the reverse, or it is
                     one of the numberings below (Bekker, Stephanus, Kühn, Mangey, Littré, Casaubon)
                     that the store's text does not hold
  no line            the work is held and the place has the text's shape and first number, and is
                     not in it (a line past its end, a lacuna, a gap)
  held, not cut      the sidecar has a line (verified, line) and the cut made no preview of it
and a place guess's reason is `place guess` (the line shown is another place than the cited one).

The numbering rules, by the work's author and the place's shape (the bibl's printed place and its n):
  Bekker     Aristotle (tlg0086) and the Rhetorica ad Alexandrum (tlg0547): page, column, line (1022b32)
  Stephanus  Plato (tlg0059): page and letter (327a); Plutarch's Moralia (tlg0007): 2.686b
  Kühn       Galen (tlg0057): volume and page (6.554)
  Mangey     Philo (tlg0018): volume and page (1.58, 2.345)
  Littré     Hippocrates (tlg0627): volume and page (6.554); his chapters apart (`Hp. chapter`)
  Casaubon   Athenaeus (tlg0008): book, page and letter (5.207c)
  IG numbers an inscription's corpus printed (IG, SIG, OGI, CIG, GDI, IGRom., SEG, TAM, Michel)
and each is tested where what we hold can test it, no concordance made or guessed:
  Bekker, Stephanus, Kühn   the place (1022b.32, 327.a, 686.c, 6.554) among the store's lines of every
                            work of the author: `one work`, `several works`, `none`
  Mangey                    the page among the Mangey pages First1K's Philo files mark (milestones
                            altpage1 and altpage2, n="p. 58 M."), in the volume the citation names,
                            each file's volume where its pages begin again (the files in the order of
                            their work numbers): `one work`, `several works`, `none`
  the others                `not tested` (no edition we hold marks them)

Writes worklist.tsv, one row per work and reason, largest first: the work (the store's id, else the
n's abo work, else the name printed), the name LSJ prints most often for it, the reason, the rule, the
citations, of which place guesses, how the rule's test came out, the held text (the store's levels as
a template, its first and last place) and up to five samples (entry:index printed); the citations
one a line to --citations; --json the counts. Standard library only; reads, changes nothing.
"""
import argparse, bisect, collections, glob, html, importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
DIV2 = re.compile(rb'<div2\b[^>]*>.*?</div2>', re.S)
BIBL = re.compile(rb'<bibl\b([^>]*)>(.*?)</bibl>', re.S)
RESP = re.compile(rb'\sresp="([^"]*)"')
NAME_EL = re.compile(r'<(author|title)\b[^>]*>(.*?)</\1>', re.S)
ABO = re.compile(r'^Perseus:abo:(?:((tlg|phi|stoa),([^,:]+),([^,:]+))|(pap,[^:]+))(?::(.*))?$')
TAG = re.compile(r'<[^>]+>')
TREES = ('perseus', 'first1k', 'greek', 'latin')
INSCRIPTIONS = re.compile(r'^(?:IG|SIG|OGI|CIG|GDI|IGRom\.|SEG|TAM|Michel|IPE|Schwyzer|Inscr\.)\b')
BEKKER = re.compile(r'^(\d{2,4})([ab])\.?(\d+)?$')
RULE_AUTHORS = {'tlg0086', 'tlg0547', 'tlg0059', 'tlg0007', 'tlg0057'}


def text(s):
    return ' '.join(html.unescape(TAG.sub('', s)).split())


def template(p):
    return re.sub(r'[a-z]+', 'a', re.sub(r'\d+', '9', p.lower()))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def bibls(repo):
    out = {}
    for f in sorted(glob.glob(os.path.join(repo, 'dictionary', 'greatscott[0-9][0-9].xml'))):
        data = open(f, 'rb').read()
        for m in DIV2.finditer(data):
            raw = m.group(0)
            o = re.search(rb'orig_id="([^"]*)"', raw[:raw.find(b'>')])
            o = o.group(1).decode() if o else ''
            vol = None                                   # the last volume printed (Ph. 1.501, 577)
            tags = list(BIBL.finditer(raw))
            # Numbered as the sidecar, the previews and the page number them (site/build.py cite_order()):
            # the dictionary's own bibls 1 to N in document order, then the bibls a pass of LSJAI marked
            # (resp) N+1 onward, pass by pass in the order of resp, each in document order; read in
            # document order still, for the volume that carries on.
            own = [t for t in tags if not RESP.search(t.group(1))]
            marked = sorted((t for t in tags if RESP.search(t.group(1))), key=lambda t: (RESP.search(t.group(1)).group(1), t.start()))
            number = {t.start(): k for k, t in enumerate(own + marked, 1)}
            for b in tags:
                k = number[b.start()]
                inner = b.group(2).decode()
                nm = re.search(r'\bn="([^"]*)"', b.group(1).decode())
                els = NAME_EL.findall(inner)
                key = '%s|%s' % (' '.join(text(x) for t, x in els if t == 'author'), ' '.join(text(x) for t, x in els if t == 'title'))
                rest = text(re.sub(r'<(author|title|abbr|foreign)\b[^>]*>.*?</\1>', ' ', inner, flags=re.S))
                nums = re.findall(r'\d+', re.sub(r'^\s*ib\.?\s*', '', rest))
                if key != '|' and key.split('|')[0] not in ('Id.',) and key.split('|')[1]:
                    vol = None                           # a work named: no volume carries on
                if len(nums) >= 2:
                    vol = nums[0]
                elif len(nums) == 1 and vol and (key == '|' or key.split('|')[0] in ('Id.',) or not key.split('|')[1]):
                    nums = [vol] + nums
                out[(o, k)] = dict(n=html.unescape(nm.group(1)) if nm else '', printed=text(inner), key=key, rest=rest, nums=nums)
    return out


def sidecar(philology):
    lex = os.path.join(philology, 'Lexicon', 'lsj')
    with open(os.path.join(lex, 'entries.txt'), encoding='utf-8') as f:
        ids = [line.rstrip('\n').split('\t')[5] for line in f]
    out = {}
    with open(os.path.join(lex, 'citations.txt'), encoding='utf-8') as f:
        for line in f:
            c = line.rstrip('\n').split('\t')
            out[(ids[int(c[0]) - 1], int(c[1]))] = (c[4], c[5])
    return out


def store(tlg):
    """{work: stats} of the TLG-E store: lines, templates, first, last, first-level values, samples, and
    for the rule authors every place's first two parts (small letters)."""
    works = []
    with open(os.path.join(tlg, 'works.txt'), encoding='utf-8') as f:
        for line in f:
            c = line.rstrip('\n').split('\t')
            works.append((int(c[1]), c[0], c[4], c[5]))
    works.sort()
    starts = [w[0] for w in works]
    stats = {w[1]: dict(author=w[2], title=w[3], lines=0, tpl=collections.Counter(), first=None, last=None,
                        top=set(), samples=[], pairs=set() if w[1].split('.')[0] in RULE_AUTHORS else None) for w in works}
    k, nxt = 0, (starts[1] if len(starts) > 1 else 1 << 60)
    cur = stats[works[0][1]]
    with open(os.path.join(tlg, 'lines.txt'), 'rb') as f:
        for i, line in enumerate(f, 1):
            while i >= nxt:
                k += 1
                cur = stats[works[k][1]]
                nxt = starts[k + 1] if k + 1 < len(starts) else 1 << 60
            p = line.split(b'\t', 1)[0].decode('utf-8', 'replace')
            parts = p.split('.')
            if any(x.startswith('t') and (x == 't' or x[1:].isdigit()) for x in parts):
                continue                                   # a title line
            cur['lines'] += 1
            cur['tpl'][template(p)] += 1
            if cur['first'] is None:
                cur['first'] = p
            cur['last'] = p
            cur['top'].add(parts[0].lower())
            if cur['lines'] in (1, 50, 500, 5000, 20000):
                cur['samples'].append(p)
            if cur['pairs'] is not None:
                low = [x.lower() for x in parts]
                cur['pairs'].add('.'.join(low[:2]))
                cur['pairs'].add(low[0])
    for s in stats.values():
        s['template'] = s['tpl'].most_common(1)[0][0] if s['tpl'] else ''
        s['depth'] = s['template'].count('.') + 1 if s['template'] else 0
        del s['tpl']
    return stats


def mangey(masters):
    """{volume: {page: [work]}} of the Mangey pages the open Philo files mark."""
    files = sorted(glob.glob(os.path.join(masters, 'Perseus', 'tlg0018.tlg*.1st1K-grc*.xml')))
    seq = []
    for path in files:
        with open(path, encoding='utf-8', errors='replace') as f:
            pages = [int(x) for x in re.findall(r'<milestone[^>]*unit="altpage[12]"[^>]*n="p\.\s*(\d+)\s*M\.?"', f.read())]
        if pages:
            seq.append(('.'.join(os.path.basename(path).split('.')[:2]), min(pages), max(pages), set(pages)))
    vol, out, last = 1, {1: collections.defaultdict(list), 2: collections.defaultdict(list)}, 0
    for work, lo, hi, pages in seq:
        if lo + 200 < last and vol == 1:
            vol = 2                                      # the pages begin again: Mangey's second volume
        last = max(last, hi)
        for p in pages:
            out[vol][p].append(work)
    return out, len(seq)


def rule_of(author, place, printed, key, pnums, alone):
    """(rule, the place as the rule's test looks it up or None). alone: the bibl names its author
    only, or continues one that did (Gal. 6.554, Ph. 1.58, 577): a volume and page, not a work."""
    loc = place.lower()
    name = key.split('|')
    if not author and INSCRIPTIONS.match((name[0] or name[1]).strip() or printed):
        return 'IG numbers', None
    nums = re.findall(r'\d+', loc)
    if author in ('tlg0086', 'tlg0547'):
        m = re.match(r'^(\d{2,4})([ab])[.:]?(\d+)?', loc.replace(' ', ''))
        if m:
            return 'Bekker', '%s%s.%s' % (m.group(1), m.group(2), m.group(3)) if m.group(3) else m.group(1) + m.group(2)
    if author == 'tlg0059':
        m = re.match(r'^(\d+)[.:]?([a-e])\b', loc)
        if m:
            return 'Stephanus', '%s.%s' % (m.group(1), m.group(2))
    if author == 'tlg0007':
        m = re.match(r'^(?:2\.)?(\d{2,4})[.:]?([a-f])\b', loc)
        if m:
            return 'Stephanus', '%s.%s' % (m.group(1), m.group(2))
    if author == 'tlg0057' and alone and len(pnums) >= 2 and int(pnums[0]) <= 20:
        return 'Kühn', '%s.%s' % (pnums[0], pnums[1])
    if author == 'tlg0018' and alone and len(pnums) >= 2 and pnums[0] in ('1', '2'):
        return 'Mangey', '%s.%s' % (pnums[0], pnums[1])
    if author == 'tlg0627':
        return ('Littré', None) if alone and len(pnums) >= 2 and int(pnums[0]) <= 10 else ('Hp. chapter', None)
    if author == 'tlg0008' and re.search(r'\d+[a-f]\b', loc):
        return 'Casaubon', None
    return '', None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--philology', required=True)
    ap.add_argument('--tlg', required=True)
    ap.add_argument('--masters', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--citations', required=True)
    ap.add_argument('--json')
    a = ap.parse_args()

    B = load(os.path.join(a.repo, 'site', 'build.py'), 'build')
    bib = bibls(a.repo)
    ids = {o for o, k in bib}
    trees = {t: {} for t in B.TREES}
    for t in B.TREES:
        for path in sorted(glob.glob(os.path.join(a.repo, 'docs', 'snippets', t, '*.json'))):
            with open(path, encoding='utf-8') as f:
                for i, v in json.load(f).items():
                    if i in ids:
                        trees[t][i] = sorted(v, key=lambda x: x['n'])
    have = {(i, x['n']) for t in TREES for i, v in trees[t].items() for x in v}
    for t in TREES:
        for v in trees[t].values():
            for x in v:
                x.pop('guess', None)
                g = B.guessed(x)
                if g:
                    x['guess'] = g
    shown = B.chosen(trees)
    guess = {(i, n) for i, v in shown.items() for n, (t, x) in v.items() if x.get('guess') == 'place'}
    side = sidecar(a.philology)
    st = store(a.tlg)
    mg, mg_files = mangey(a.masters)
    by_author = collections.defaultdict(list)
    for w in st:
        by_author[w.split('.')[0]].append(w)

    labels = collections.defaultdict(collections.Counter)      # a work's name as its bibls print it
    for (o, k), b in bib.items():
        s = side.get((o, k))
        w = s[0].split(':')[0] if s and s[0] else ''
        if w and b['key'] != '|':
            labels[w][b['key']] += 1

    def test(rule, author, look):
        if rule in ('Bekker', 'Stephanus', 'Kühn'):
            hits = [w for w in by_author[author] + (by_author['tlg0547'] if author == 'tlg0086' else []) if look in st[w]['pairs']]
            return 'one work' if len(hits) == 1 else 'several works' if hits else 'none', hits
        if rule == 'Mangey':
            v, p = look.split('.')
            hits = mg.get(int(v), {}).get(int(p), [])
            return 'one work' if len(hits) == 1 else 'several works' if hits else 'none', hits
        return 'not tested', []

    rows, kinds, shape = [], collections.Counter(), collections.Counter()
    for (o, k), b in bib.items():
        if (o, k) in have and (o, k) not in guess:
            continue
        s = side.get((o, k))
        key_, status = (s if s else ('', 'no row'))
        m = ABO.match(b['n']) if b['n'] else None
        nwork = (m.group(1) or m.group(5)) if m else ''
        nloc = (m.group(6) or '') if m else ''
        swork, splace = key_.split(':', 1) if ':' in key_ else (key_, '')
        work = swork or (nwork.replace(',', '.', 1).replace(',', '.') if nwork.startswith(('tlg', 'phi', 'stoa')) else nwork) or ('name: ' + (b['key'] if b['key'] != '|' else b['printed'][:30]))
        work = re.sub(r'^(tlg|phi|stoa)\.(\w+)\.(\w+)$', r'\1\2.\1\3', work)
        author = work.split('.')[0] if re.match(r'^(tlg|phi|stoa)\d', work) else ''
        alone = not b['key'].split('|')[1] if b['key'] != '|' else True
        rule, look = rule_of(author, (nloc.replace(':', '.') if nloc else '') or splace or b['rest'], b['printed'], b['key'], b['nums'], alone)
        if rule in ('Bekker', 'Stephanus', 'Kühn') and splace and not look:
            pass
        if (o, k) in guess:
            reason = 'place guess'
        elif not b['n'] or status == 'none':
            reason = 'no reference'
        elif status == 'no-work':
            reason = 'work not held: papyrus' if nwork.startswith('pap') else 'work not held'
        elif status == 'no-line':
            h = st.get(swork)
            parts = splace.lower().split('.')
            if not h or not h['lines']:
                reason = 'work not held'
            else:
                why = ('a numbering rule' if rule in ('Bekker', 'Stephanus', 'Kühn', 'Mangey', 'Littré', 'Casaubon') else
                       'first number not in the text' if parts[0] not in h['top'] else
                       'more levels than the text' if len(parts) > h['depth'] else
                       'another shape' if template(splace).split('.') != h['template'].split('.')[:len(parts)] else '')
                reason = 'numbering differs' if why else 'no line'
                shape[why or 'no line'] += 1
        else:
            reason = 'held, not cut'
        res, hits = test(rule, author, look) if look else ('not tested', [])
        kinds[reason] += 1
        rows.append(dict(entry=o, index=k, printed=b['printed'], n=b['n'], side=key_, status=status, reason=reason,
                         rule=rule, test=res, hits=' '.join(hits[:3]), work=work,
                         name=labels[swork].most_common(1)[0][0] if swork and labels[swork] else b['key']))

    with open(a.citations, 'w', encoding='utf-8') as f:
        cols = ['entry', 'index', 'printed', 'n', 'side', 'status', 'work', 'name', 'reason', 'rule', 'test', 'hits']
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]).replace('\t', ' ') for c in cols) + '\n')
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r['work'], r['reason'])].append(r)
    table = []
    for (work, reason), rs in groups.items():
        h = st.get(work)
        rules = collections.Counter(r['rule'] for r in rs)
        tests = collections.Counter(r['test'] for r in rs if r['test'] != 'not tested')
        names = collections.Counter(r['name'] for r in rs)
        table.append(dict(work=work, name=names.most_common(1)[0][0], reason=reason,
                          rule=', '.join('%s %d' % kv for kv in rules.most_common() if kv[0]),
                          citations=len(rs), guesses=sum(1 for r in rs if r['reason'] == 'place guess'),
                          test=', '.join('%s %d' % kv for kv in tests.most_common()),
                          held=('%s %s, %s to %s, %d lines' % (work, h['template'], h['first'], h['last'], h['lines'])) if h and h['lines'] else '',
                          samples=' | '.join('%s:%d %s' % (r['entry'], r['index'], r['printed']) for r in rs[:5])))
    table.sort(key=lambda r: (-r['citations'], r['work'], r['reason']))
    with open(a.out, 'w', encoding='utf-8') as f:
        cols = ['work', 'name', 'reason', 'rule', 'citations', 'guesses', 'test', 'held', 'samples']
        f.write('\t'.join(cols) + '\n')
        for r in table:
            f.write('\t'.join(str(r[c]).replace('\t', ' ') for c in cols) + '\n')
    by_rule = collections.defaultdict(collections.Counter)
    for r in rows:
        by_rule[r['rule'] or '(none)'][r['test']] += 1
    summary = {'citations': len(bib), 'with a text': len(have), 'no text': sum(1 for r in rows if r['reason'] != 'place guess'),
               'place guesses': len(guess), 'by reason': dict(kinds.most_common()),
               'by rule': {k: dict(v, total=sum(v.values())) for k, v in sorted(by_rule.items(), key=lambda kv: -sum(kv[1].values()))},
               'by rule and reason': {'%s | %s' % k: v for k, v in collections.Counter((r['rule'] or '(none)', r['reason']) for r in rows).most_common()},
               'no-line split': dict(shape.most_common()), 'mangey files': mg_files, 'rows': len(table)}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'by rule and reason'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
