"""The numbers, one AI to another: docs/numbers.txt, the compact text of every measure the site is judged
by, with the value before it and how each is made, for the next pass to beat; on this machine only, never pushed.

Reads docs/stats.json (the build's values) and site/build.py's METHOD (how each is made), docs/alignment.tsv
(the collation's per-edition report), tools/tlg_works.tsv and docs/snippets/text (the lines of each work
the records carry), corrections/corrections.tsv (the print's verdicts), and the
numbers.txt last committed (`git show HEAD:docs/numbers.txt`) for the values before. Writes docs/numbers.txt.
Run after a build; a tab separates the columns; a line that begins with # is a section.

Usage: python3 -I tools/numbers.py
"""
import collections, csv, glob, importlib.util, io, json, os, re, subprocess, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, 'docs')
OUT = os.path.join(DOCS, 'numbers.txt')                                                    # shown on the status page, on this machine only (.gitignore)
PRIVATE = os.environ.get('LSJAI_NUMBERS_COPY')                                              # a second copy of the text, where the agent keeps its notes (an environment variable; none by default)
TEXTS = ('greek', 'loeb', 'perseus', 'first1k', 'digiliblt', 'papyri', 'inscriptions', 'latin')
NAMES = {'greek': 'TLG-E', 'loeb': 'Loeb', 'perseus': 'Perseus', 'first1k': 'First1KGreek', 'digiliblt': 'DigiLibLT',
         'papyri': 'DDbDP, PHI 7', 'inscriptions': 'PHI Inscriptions', 'latin': 'PHI Latin'}


def method():
    spec = importlib.util.spec_from_file_location('build', os.path.join(REPO, 'site', 'build.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.METHOD


def before():
    """The values of the numbers.txt last committed: {measure: (value, date)}."""
    try:
        text = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:docs/numbers.txt'], capture_output=True, check=True).stdout.decode('utf-8')
    except subprocess.CalledProcessError:
        return {}, ''
    date = ''
    m = re.match(r'LSJAI numbers\t(.+?)\t', text)
    if m:
        date = m.group(1)
    out = {}
    section = ''
    for line in text.split('\n'):
        if line.startswith('#'):
            section = line
        elif section.startswith('# measure') and '\t' in line:
            f = line.split('\t')
            out[f[0]] = f[1]
    return out, date


def carried():
    """Per work the records quote as the base: lines carried, the work's lines, the share; the works over half, by lines."""
    sizes = {}
    with io.open(os.path.join(REPO, 'tools', 'tlg_works.tsv'), encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            sizes[r['work']] = (int(r['lines']), r['author'], r['title'])
    carried = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(DOCS, 'snippets', 'text', '*.json'))):
        with io.open(p, encoding='utf-8') as f:
            for recs in json.load(f).values():
                for r in recs:
                    if r.get('src') != 'greek':
                        continue
                    m = re.match(r'urn:cts:greekLit:([^:]+):', r.get('urn') or '')
                    if not m:
                        continue
                    for k in range(3):
                        if r['lines'][k] is not None:
                            carried[m.group(1)].add(r['at'][k])
    rows = []
    for w, s in carried.items():
        if w in sizes and sizes[w][0] > 0:
            rows.append((len(s), sizes[w][0], len(s) / sizes[w][0], w, sizes[w][1], sizes[w][2]))
    total = sum(len(s) for s in carried.values())
    return total, sum(v[0] for v in sizes.values()), rows


def main():
    with io.open(os.path.join(DOCS, 'stats.json'), encoding='utf-8') as f:
        S = json.load(f)
    P = {}   # the per-collection counts kept in site/stats-private.json
    pp = os.path.join(REPO, 'site', 'stats-private.json')
    if os.path.exists(pp):
        with io.open(pp, encoding='utf-8') as f:
            P = json.load(f)
    M = method()
    old, old_date = before()
    head = subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%h %cd', '--date=format:%d %b %Y %H:%M'], capture_output=True).stdout.decode().strip()
    now = datetime.datetime.now().strftime('%d %b %Y %H:%M')
    out = ['LSJAI numbers\t%s\tmaster %s\tbefore: %s' % (now, head, old_date or 'none'),
           'one line a measure: name, value now, value before, how it is made; the next pass beats the value now',
           '', '# measure\tnow\tbefore\thow']
    for k in sorted(S):
        v = S[k]
        if isinstance(v, (dict, list)):
            continue
        out.append('%s\t%s\t%s\t%s' % (k, v, old.get(k, ''), M.get(k, '')))
    out += ['', '# by collection\tcitations at the line\tat the word\tpreviews held\taligned to this text %\theadword found % of the testable']
    for t in TEXTS:
        if 'line_' + t in S:
            out.append('%s\t%s\t%s\t%s\t%s\t%s' % (NAMES[t], S['line_' + t], S['word_' + t], S.get('held_' + t, ''), S.get('align_' + t, ''), S.get('rate_' + t, '')))
    ap = os.path.join(DOCS, 'alignment.tsv')
    if os.path.exists(ap):
        with io.open(ap, encoding='utf-8') as f:
            rows = list(csv.DictReader(f, delimiter='\t'))
        big = [r for r in rows if int(r['witness']) >= 500]
        big.sort(key=lambda r: -int(r['not aligned']) / int(r['witness']))
        out += ['', '# alignment, the worst editions with 500 witness lines or more\tcollection\twitness\tnot aligned\tnot aligned %\treads otherwise\tthe base for']
        for r in big[:25]:
            out.append('%s\t%s\t%s\t%s\t%d\t%s\t%s' % (r['edition'], r['collection'], r['witness'], r['not aligned'], round(100 * int(r['not aligned']) / int(r['witness'])), r['reads otherwise'], r['base']))
    out += ['', '# per-collection counts (site/stats-private.json)\tnow\thow']
    for k in sorted(P):
        out.append('%s\t%s\t%s' % (k, P[k], M.get(k, '')))
    total, corpus, rows = carried()
    rows.sort(key=lambda x: -x[0])
    over = [x for x in rows if x[2] > .5]
    out += ['', '# lines carried by work, the TLG-E as the base\tlines carried\tof the corpus\tworks\tworks over half their lines\tof them 100 lines or more',
            'TLG-E\t%d\t%d (%.2f%%)\t%d\t%d\t%d' % (total, corpus, 100 * total / corpus, len(rows), len(over), sum(1 for x in over if x[1] >= 100)),
            '# the works over half, by lines carried\tcarried\tof\tshare %\tauthor\ttitle']
    for n, tot, share, w, au, ti in sorted(over, key=lambda x: -x[0])[:40]:
        out.append('%s\t%d\t%d\t%d\t%s\t%s' % (w, n, tot, round(100 * share), au, ti))
    cp = os.path.join(REPO, 'corrections', 'corrections.tsv')
    with io.open(cp, encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    c = collections.Counter(r.get('print', '') or 'unread' for r in rows)
    out += ['', '# the corrections against the printed page (the print column of corrections.tsv)\tcount',
            'rows\t%d' % len(rows)] + ['the print reads %s\t%d' % (k if k != 'unread' else 'nothing yet (unread, faulted)', v) for k, v in sorted(c.items())]
    wd = os.path.join(REPO, 'corrections', 'withdraw.tsv')
    if os.path.exists(wd):
        with io.open(wd, encoding='utf-8') as f:
            n = sum(1 for _ in f) - 1
        out.append('to withdraw, the page prints Logeion\'s text (corrections/withdraw.tsv)\t%d' % n)
    text = '\n'.join(out) + '\n'
    for path in (OUT, PRIVATE):
        if path:
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(text)
    print('%s and %s: %d lines, %d measures; on this machine only' % (OUT, PRIVATE, len(out), sum(1 for k in S if not isinstance(S[k], (dict, list)))))


if __name__ == '__main__':
    main()
