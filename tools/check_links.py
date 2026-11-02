#!/usr/bin/env python3
"""Does each Scaife link of the open-text previews name a passage the edition holds? A program, no
reader: every url of docs/snippets/perseus and docs/snippets/first1k tested against the TEI of the
edition it was cut from, by the edition's own citation scheme, not by the cut that made it.

    python3 -I tools/check_links.py --masters <Philology-masters> [--repo .] --out links.tsv \\
        [--json counts.json] [--jobs 8]
    python3 -I tools/check_links.py --repo . --live 30 --out live.tsv [--seed 31] [--wait 10]

The edition. A url is https://scaife.perseus.org/reader/<edition URN>[:<passage>]/. Its edition is
the file of the Perseus shelf (Catalogue/editions.txt, kind text, language grc, source Perseus or
First1K, rights 0, file Perseus/...) whose TEI edition div names that URN, else whose file name is
the URN's last part. Nothing else on the shelf is read.

The scheme. A file's CTS scheme is its refsDecl's cRefPatterns: each replacementPattern's xpath
(#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:l[@n='$2'])) is evaluated here over
the TEI (child and descendant steps, element names, @n='$k' and @attr='literal' predicates) and
gives the passages of its level, each the $ values joined by full stops. The deepest pattern is the
scheme's level.

What is tested, per url:
  exact         the passage is one of the deepest pattern's (Il. 23.620; Pl. R. 7.529)
  shallower     the passage is one of a shallower pattern's (a section of a text cited by line, a
                book): Scaife opens the whole of it
  not in scheme the passage is no passage of any pattern: Scaife sends the reader elsewhere (303)
  work only     no passage in the url (the scheme names elements other than div and l): the work's start
  no edition    no file of the shelf names the URN
and, for a passage in the scheme, whether the cited place (the preview's `at`, the cited line's place
in the edition's numbering) meets it: the passage's own n is the place's last part or its first (a
fragment holding a line the file counts but does not mark: E. Fr. 282.26), or an element
named by the place, whole or its last part (a div, a line, a milestone: Ath. 5.207c's milestone
207c), has a stretch that meets the passage's (a div's or a line's own; a milestone's to the next
milestone of its unit): `holds the place`, else `place not inside`.

--live samples urls at random (--seed) and asks Scaife for each passage's JSON
(https://scaife.perseus.org/library/passage/<urn>/json/), --wait seconds apart: a passage it holds
comes back at its own address (lands), one it does not is redirected (303); for a landing passage,
whether the preview's found form stands in the passage's text Scaife returns (accents and case off).

Writes, one a line: tree, entry, n, url, the preview's urn and at, the result and the place test;
--json the counts by result and by work. Standard library only; reads, changes nothing.
"""
import argparse, collections, concurrent.futures, csv, glob, json, os, random, re, sys, time, unicodedata, urllib.error, urllib.request
import xml.etree.ElementTree as ET

URL = re.compile(r'^https://scaife\.perseus\.org/reader/(urn:cts:[^:/]+:[^:/]+)(?::([^/]*))?/$')
STEP = re.compile(r'(//?)([\w.:-]+)((?:\[[^\]]*\])*)')
PRED = re.compile(r"@([\w:]+)\s*=\s*\\?['\"]([^'\"\\]*)\\?['\"]")
TREES = ('perseus', 'first1k')


def local(tag):
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ''


def steps(pattern):
    """An xpath of a replacementPattern as [(axis, name, [(attr, value)])]."""
    path = re.sub(r'^#xpath\((.*)\)$', r'\1', pattern.strip()).replace("\\'", "'")
    out = []
    for axis, name, preds in STEP.findall(path):
        ps = []
        for p in re.findall(r'\[([^\]]*)\]', preds):
            ps += PRED.findall(p)
        out.append((axis, name.split(':')[-1], ps))
    return out


def evaluate(root, st):
    """{passage: element} of one pattern over the tree."""
    found = {}

    def match(el, name, preds, bind):
        if local(el.tag) != name:
            return None
        b = dict(bind)
        for attr, val in preds:
            got = el.get(attr)
            if got is None:
                return None
            if val.startswith('$'):
                b[int(val[1:])] = got
            elif got != val:
                return None
        return b

    def walk(el, k, bind):
        if k == len(st):
            found.setdefault('.'.join(bind[i] for i in sorted(bind)), el)
            return
        axis, name, preds = st[k]
        cands = el.iter() if axis == '//' else list(el)
        for c in cands:
            if c is el:
                continue
            b = match(c, name, preds, bind)
            if b is not None:
                walk(c, k + 1, b)

    if not st:
        return found
    b = match(root, st[0][1], st[0][2], {})
    if b is not None:
        walk(root, 1, b)
    return found


def scheme(root):
    """[(depth, {passage: element})] of a file's cRefPatterns, deepest first."""
    pats = []
    for e in root.iter():
        if local(e.tag) == 'cRefPattern' and e.get('replacementPattern'):
            st = steps(e.get('replacementPattern'))
            depth = sum(1 for a, n, ps in st for x, v in ps if v.startswith('$'))
            pats.append((depth, st))
    out = [(d, evaluate(root, st)) for d, st in pats]
    return sorted(out, key=lambda x: -x[0])


class Order:
    """Every element of a file in document order: its index, and the index past its last descendant."""
    def __init__(self, root):
        self.idx, self.end, self.by_n, self.seq = {}, {}, {}, []
        self._walk(root)

    def _walk(self, root):
        stack = [(root, False)]
        while stack:
            el, done = stack.pop()
            if done:
                self.end[id(el)] = len(self.seq)
                continue
            self.idx[id(el)] = len(self.seq)
            self.seq.append(el)
            n = el.get('n')
            if n:
                self.by_n.setdefault(n, []).append(el)
            stack.append((el, True))
            for c in reversed(list(el)):
                stack.append((c, False))

    def stretch(self, el):
        """A place marker's stretch: a div's or a line's own elements; a milestone's, to the next
        milestone of its unit."""
        i = self.idx[id(el)]
        if local(el.tag) != 'milestone':
            return i, self.end[id(el)]
        unit = el.get('unit')
        for j in range(i + 1, len(self.seq)):
            e = self.seq[j]
            if local(e.tag) == 'milestone' and e.get('unit') == unit:
                return i, j
        return i, len(self.seq)


def holds(order, el, at):
    """Whether the cited place's stretch meets the passage: the passage's own n is the place's last
    part, or an element named by the place (whole, or its last part) stands in it or runs into it."""
    if not at:
        return None
    parts = [p for p in re.split(r'[.:]', at) if p]
    last = parts[-1]
    if el.get('n') in (last, at, parts[0]):          # the passage is the place, or the fragment or book holding
        return True                                  # a line the file counts but does not mark (E. Fr. 282.26)
    a, b = order.idx[id(el)], order.end[id(el)]
    for n in (at, last):
        for m in order.by_n.get(n, ()):
            s, e = order.stretch(m)
            if s < b and e > a:
                return True
    return False


def check_file(arg):
    path, wants = arg
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as e:
        return path, {w: ('unreadable', None) for w in wants}
    levels = scheme(root)
    order = Order(root)
    out = {}
    for passage, at in wants:
        if passage is None:
            out[(passage, at)] = ('work only', None)
            continue
        res = None
        for k, (depth, refs) in enumerate(levels):
            if passage in refs:
                res = ('exact' if k == 0 else 'shallower', holds(order, refs[passage], at))
                break
        out[(passage, at)] = res or ('not in scheme', None)
    return path, out


def previews(repo):
    for t in TREES:
        for p in sorted(glob.glob(os.path.join(repo, 'docs', 'snippets', t, '*.json'))):
            with open(p, encoding='utf-8') as f:
                for oid, v in json.load(f).items():
                    for x in v:
                        if x.get('url'):
                            yield t, oid, x


def shelf(masters):
    """{edition URN: path} of the open Greek texts of the Perseus shelf."""
    out = {}
    with open(os.path.join(masters, 'Catalogue', 'editions.txt'), encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    for r in rows:
        if r['kind'] == 'text' and r['language'] == 'grc' and r['source'] in ('Perseus', 'First1K') \
                and r['rights'] == '0' and r['file'].startswith('Perseus/'):
            path = os.path.join(masters, r['file'])
            stem = os.path.basename(path)[:-4]
            out.setdefault('urn:cts:greekLit:' + stem, path)
            try:
                with open(path, encoding='utf-8', errors='replace') as f:
                    head = f.read(400000)
                m = re.search(r'<div[^>]*type="edition"[^>]*n="(urn:cts:[^"]+)"|<div[^>]*n="(urn:cts:[^"]+)"[^>]*type="edition"', head)
                if m:
                    out[m.group(1) or m.group(2)] = path
            except OSError:
                pass
    return out


def plain(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('ς', 'σ')


def live(a):
    links = [(t, oid, x) for t, oid, x in previews(a.repo)]
    rnd = random.Random(a.seed)
    sample = rnd.sample(links, a.live)
    counts = collections.Counter()
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('tree\tentry\tn\turl\tstatus\tlands\tform in passage\tform\n')
        for k, (t, oid, x) in enumerate(sample):
            m = URL.match(x['url'])
            urn = m.group(1) + (':' + m.group(2) if m.group(2) else '')
            req = urllib.request.Request('https://scaife.perseus.org/library/passage/%s/json/' % urn,
                                         headers={'User-Agent': 'LSJAI link check (one request every %d s)' % a.wait})

            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *args, **kw):
                    return None
            opener = urllib.request.build_opener(NoRedirect)
            status, lands, has = '', 'no', ''
            try:
                with opener.open(req, timeout=60) as r:
                    status = str(r.status)
                    body = json.load(r)
                lands = 'yes' if body.get('url', '').rstrip('/') == '/reader/' + urn else 'no'
                text = json.dumps(body, ensure_ascii=False)
                form = x.get('found') or ''
                has = ('yes' if plain(form) in plain(text) else 'no') if form else 'no form'
            except urllib.error.HTTPError as e:
                status = str(e.code)
            except Exception as e:
                status = 'error ' + str(e)[:60]
            if not m.group(2):
                lands = 'work only'
            counts[lands] += 1
            counts['form ' + has] += 1 if has else 0
            f.write('\t'.join([t, oid, str(x['n']), x['url'], status, lands, has, x.get('found') or '']) + '\n')
            f.flush()
            print(k + 1, status, lands, has, x['url'], flush=True)
            if k + 1 < len(sample):
                time.sleep(a.wait)
    print(dict(counts))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--masters')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json')
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--live', type=int, default=0)
    ap.add_argument('--seed', type=int, default=31)
    ap.add_argument('--wait', type=float, default=10)
    a = ap.parse_args()
    if a.live:
        return live(a)

    eds = shelf(a.masters)
    links, wants = [], collections.defaultdict(set)
    for t, oid, x in previews(a.repo):
        m = URL.match(x['url'])
        if not m:
            links.append((t, oid, x, None, None, 'url unread'))
            continue
        path = eds.get(m.group(1))
        at = (x.get('at') or [None, None])[1]
        links.append((t, oid, x, path, (m.group(2), at), None))
        if path:
            wants[path].add((m.group(2), at))
    results = {}
    with concurrent.futures.ProcessPoolExecutor(a.jobs) as ex:
        for path, out in ex.map(check_file, sorted(wants.items(), key=lambda kv: -os.path.getsize(kv[0]))):
            for w, r in out.items():
                results[(path, w)] = r
    counts, place, by_work = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('tree\tentry\tn\turl\turn\tat\tresult\tplace\n')
        for t, oid, x, path, w, bad in links:
            if bad:
                res, inside = bad, None
            elif not path:
                res, inside = 'no edition', None
            else:
                res, inside = results[(path, w)]
            work = x['urn'].split(':')[3] if x.get('urn', '').count(':') >= 3 else ''
            counts[(t, res)] += 1
            by_work[work][res] += 1
            pl = '' if inside is None else 'holds the place' if inside else 'place not inside'
            if pl:
                place[(t, pl)] += 1
                by_work[work][pl] += 1
            if res not in ('exact',) or pl == 'place not inside':
                f.write('\t'.join([t, oid, str(x['n']), x['url'], x.get('urn', ''), ' / '.join(str(y) for y in x.get('at') or []), res, pl]) + '\n')
    summary = {'links': len(links), 'editions read': len(wants),
               'by result': {'%s: %s' % k: v for k, v in sorted(counts.items())},
               'place': {'%s: %s' % k: v for k, v in sorted(place.items())},
               'by work': {w: dict(c) for w, c in sorted(by_work.items(), key=lambda kv: -sum(v for k, v in kv[1].items()
                                                                                              if k not in ('exact', 'holds the place')))}}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ('links', 'editions read', 'by result', 'place')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    sys.exit(main())
