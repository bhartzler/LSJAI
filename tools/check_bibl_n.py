#!/usr/bin/env python3
"""Does each <bibl>'s printed text agree with its n? A program, no reader: every bibl of greatscott01.xml
to greatscott86.xml, its printed author, work and numbers against the Perseus reference in its n
(n="Perseus:abo:tlg,0012,001:17:443"), allowing LSJ's continuations.

    python3 -I tools/check_bibl_n.py [--repo .] --out mismatches.tsv [--json counts.json]

The printed text. A bibl prints a name (its <author> and <title> elements: the key `Arist.|Metaph.`)
and a place (the rest of its text: 1022b32). A name written outside any bibl since the bibl before
(an <author>, and the <title> just after it) is the name of a bibl printing none, unless it begins
ib. A bibl printing no name continues the citation before it in the entry (Il. 11.441, 17.443: the
Iliad), as does one beginning ib.; Id. takes the author written last since the bibl before, else the
citation before's (Id. Gym. 46 after Philostr. VA 5.5 is Philostr.|Gym.). A bibl whose place begins
with a word in capitals (Arg. 1, Sch.HQ 12.89, Arion l.18: a part of the work, a work about it, a
name left as text) is not judged on its work (`unjudged`).

The work. The files say which work each name means: of every bibl naming one, the key's works by
their n. A key whose bibls are 80 in 100 or more one work (5 or more bibls) has that work as its own;
so does a key with its first printed number (D. 18 is tlg,0014,018), 3 or more bibls. A bibl naming
a work disagrees when its n's work is neither the key's own nor the key-and-number's, and is a work
the key (the key and number, where that gave the own work: Isoc. 15 is tlg,0010,019, not 015) names
fewer than 3 times and in under 1 in 10 of its bibls: `author` where the n's author is
not the own work's, else `work`. A key with no own work is not judged (`unjudged`, counted). A
continuing bibl disagrees when its n's work is neither the work of the citation before nor the own
work of the name it continues with its first printed number (D. 32.10, 54.31: speech 54), nor by an
author named since the bibl before or just after it in parentheses (AP 7.196 (Mel.), cf. 12.125
(Mel.): Perseus's n names Meleager's epigrams, tlg,1492,001)
(`continuation`); an Id. when its n's author is neither the author of the citation before nor one the
author it stands for (the last name written since the bibl before, else the citation before's) names
3 times or more (LSJ's Philostr. is three TLG authors) (`Id.`).

The numbers. The printed place and the n's place are cut into their numbers and single letters
(405c and 405:c are 405 c; 1022b32 and 1022b:32 are 1022 b 32); words (ib., fr., sq., L.-P.) are left
out. They agree when the numbers are the same and the small letters a to h standing on a number (a
Stephanus, Bekker or Casaubon letter; not an editor's initial, p.85 D.) the same. An n that adds a
level inside the printed place, as the work's n's do 3 times or more (Hp. Epid. 4.24 is 4:1:24, the
section between book and chapter), agrees (`inserted level`, counted). A printed place
with a second numbering, in square brackets or in round ones after a number (Luc. DMort. 26[15].3,
Pi. I. 7(6).43), or a second address in square brackets just after the bibl (B. 17.5 [Dith. 4.5],
Call. Aet. 3.1.69 [Fr. 75.69]), agrees when the n follows either (`second numbering`, counted). A
range is its first place (19.407-9 is 19.407). A name inside a parenthesis closed before the bibl
(Nic. Fr. 74.51 (codd. Ath.); Id. Al. 89) is not the name the bibl continues. Otherwise, best first:
  continuation   the printed numbers are the last of the n's (Il. 11.441, 443 is 11:443): agrees when
                 the n's leading numbers are those of the citation before, or the key's n's add the
                 same leading numbers, or repeat its first, in 3 of 10 of its bibls or more
                 (CPHerm. is volume 5; Hp. Epid. 3.6 is 3:3:6), else `leading numbers`
  work number    the n's numbers are the printed without its first (D. 18.204 is tlg,0014,018:204,
                 Plu. 2.686b is 686:b): agrees when the first is the work's number or the key prints
                 it so in 3 of 10 of its bibls or more (5 or more), else `extra number`
  n coarser      the n's numbers are the first of the printed (AP 9.384.8 is 9:384)
  n finer        the printed numbers are the first of the n's and no continuation (Petron. 56 is 56:8)
  letter         the same numbers, another Stephanus, Bekker or Casaubon letter (327a for 327:b)
  another numbering  the last number alike and the rest another, as 3 or more bibls of the work have it
                 (Call. Aet. 3.1.43 is 75:43, Pfeiffer's fragment; B. 15.30 is 2:30)
  value          as many numbers, one or more other (Ath. 5.210 for 5:21c)
  levels         anything else
and a bibl with no number printed (`no number`), an n naming no place or no abo reference (`no
place`) or no n at all (`no n`, counted, not compared).

Writes the disagreements (not the counted kinds), one a line: entry (orig_id), index (the bibl's
number in the entry, the page's n-th <cite>), printed (its text), n, kind, and what differs in words.
--json writes the counts by kind, by group (place: the n names another place than the print;
another numbering; precision: the same place, coarser or finer) and by work (the n's work key, with
the name its bibls print most often). Standard library only; reads the files, changes nothing.
"""
import argparse, collections, glob, html, json, os, re

DIV2 = re.compile(rb'<div2\b[^>]*>.*?</div2>', re.S)
BIBL = re.compile(rb'<bibl\b([^>]*)>(.*?)</bibl>', re.S)
ABO = re.compile(r'^Perseus:abo:(?:((tlg|phi|stoa),([^,:]+),([^,:]+))|(pap,[^:]+))(?::(.*))?$')
TOK = re.compile(r'\d+|[^\W\d_\u0374\u02b9]+')
KERAIA = ('\u0374', '\u02b9')
ROMAN = re.compile(r'^[IVX]+$')
NAME_EL = re.compile(r'<(author|title)\b[^>]*>(.*?)</\1>', re.S)
TAG = re.compile(r'<[^>]+>')
STRIP = re.compile(r'<(author|title|abbr|foreign)\b[^>]*>.*?</\1>', re.S)
IB = re.compile(r'^\s*ib(?:id)?\b\.?\s*')
RANGE = re.compile(r'(\d[a-h]?)\s*[-\u2013]\s*\d+[a-h]?\b')     # 19.407-9 is 19.407
QUALIFIED = re.compile(r'^\s*(?:\[\s*)?[A-Z][^\W\d_]+')    # Arg. 1, Sch.HQ 12.89, Arion l.18: a name or part printed as text
POSITIONAL = set('abcdefgh')
COUNTED = ('no n', 'unjudged', 'second numbering', 'inserted level')     # counted, not disagreements
GROUPS = {'place': ('author', 'work', 'continuation', 'Id.', 'leading numbers', 'extra number', 'value', 'levels', 'letter', 'no place'),
          'another numbering': ('another numbering',), 'precision': ('n coarser', 'n finer', 'no number')}
LEAST_KEY, LEAST_FIRST, OWN, RARE, SHARE = 5, 3, 0.8, 3, 0.1
CONV, CONV_LEAST = 0.3, 3
RENUM = 3                # a renumbering seen this often in a work is consistent


def text(s):
    return ' '.join(html.unescape(TAG.sub('', s)).split())


GREEK_NUM = dict(zip('αβγδεϛζηθικλμνξοπϟρστυφχψωϡ', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90,
                                                         100, 200, 300, 400, 500, 600, 700, 800, 900]))
GREEK_NUM.update({'ϝ': 6, 'ϙ': 90})


def greek_number(t, s, end):
    """A Greek numeral with its keraia (ιθʹ is 19), or a lone Greek letter in an n (7:9:γ is 3), as digits."""
    marked = s[end:end + 1] in KERAIA
    if (marked or len(t) == 1) and t and all(c in GREEK_NUM for c in t):
        return str(sum(GREEK_NUM[c] for c in t))
    return None


def roman(t):
    v = {'I': 1, 'V': 5, 'X': 10}
    return sum(-v[c] if k + 1 < len(t) and v[c] < v[t[k + 1]] else v[c] for k, c in enumerate(t))


def cut(s):
    """A place's numbers and single letters in order, each with whether it is a small letter a to h
    standing on the number before it: 405c and 405:c are [('405', False), ('c', True)]; a Greek
    numeral a number (6.76.βʹ is 6 76 2)."""
    out = []
    for m in TOK.finditer(s or ''):
        raw = m.group(0)
        t = raw.lower()
        g = greek_number(t, s, m.end())
        if g:
            out.append((g, False))
            continue
        if ROMAN.match(raw) and re.match(r'\.?\s*\d', s[m.end():m.end() + 3]):      # II.4, XV 8: a Roman numeral before a number
            out.append((str(roman(raw)), False))
            continue
        if t.isdigit() or len(t) == 1:
            on = (not t.isdigit() and raw in POSITIONAL and m.start() > 0 and s[m.start() - 1] in '0123456789:')
            out.append((t, on))
    return out


def digits(c):
    return [t for t, _ in c if t.isdigit()]


def letters(c):
    return [t for t, on in c if on]


def place(n):
    """(work key, author key, place) of an abo n, or None."""
    m = ABO.match(n)
    if not m:
        return None
    if m.group(1):
        return m.group(1), '%s,%s' % (m.group(2), m.group(3)), m.group(6)
    return m.group(5), m.group(5), m.group(6)


def bibls(repo):
    """Every bibl in file order, as a dict."""
    for f in sorted(glob.glob(os.path.join(repo, 'dictionary', 'greatscott[0-9][0-9].xml'))):
        data = open(f, 'rb').read()
        for m in DIV2.finditer(data):
            raw = m.group(0)
            oid = re.search(rb'orig_id="([^"]*)"', raw[:raw.find(b'>')])
            oid = oid.group(1).decode() if oid else ''
            last = 0
            for k, b in enumerate(BIBL.finditer(raw), 1):
                after = text(raw[b.end():b.end() + 400].decode('utf-8', 'replace').split('<bibl')[0])
                square = re.match(r'^\s*\[([^\]]{1,60})\]', after)
                poet = re.match(r'^\s*\(\s*<author>(.*?)</author>\s*\)', raw[b.end():b.end() + 200].decode('utf-8', 'replace'))
                attrs, inner = b.group(1).decode(), b.group(2).decode()
                between = re.sub(r'<bibl\b.*?</bibl>', '', raw[last:b.start()].decode(), flags=re.S)
                last = b.end()
                nm = re.search(r'\bn="([^"]*)"', attrs)
                els = NAME_EL.findall(inner)
                named = [text(x) for t, x in NAME_EL.findall(between) if t == 'author']   # every author named since the bibl before
                groups = []                      # the names written outside any bibl since the bibl before, an author
                end = None                       # and the title just after it one name (Phld. Mus.)
                for e in NAME_EL.finditer(between):
                    if between[:e.start()].count('(') - between[:e.start()].count(')') > between.count('(') - between.count(')'):
                        continue                 # inside a parenthesis closed before the bibl: (codd. Ath.)
                    if end is not None and not between[end:e.start()].strip() and groups and e.group(1) == 'title' and 'title' not in groups[-1]:
                        groups[-1]['title'] = text(e.group(2))
                    else:
                        groups.append({e.group(1): text(e.group(2))})
                    end = e.end()
                outside = groups[-1] if groups else {}
                yield dict(entry=oid, index=k, file=os.path.basename(f),
                           author=' '.join(text(x) for t, x in els if t == 'author'),
                           title=' '.join(text(x) for t, x in els if t == 'title'),
                           out_author=outside.get('author', ''), out_title=outside.get('title', ''), between_authors=named, poet=text(poet.group(1)) if poet else '',
                           rest=text(STRIP.sub(' ', inner)), printed=text(inner), after=square.group(1) if square else '',
                           n=html.unescape(nm.group(1)) if nm else '')


def relation(P, N):
    """How the printed place's numbers stand to the n's, with the leading numbers a continuation adds."""
    Pd, Nd = digits(P), digits(N)
    if Pd == Nd:
        return 'same', None
    if len(Nd) == len(Pd) + 1 and Nd[:len(Pd)] != Pd and any(Nd[:i] + Nd[i + 1:] == Pd for i in range(1, len(Nd))) \
            and not (Pd and Nd[1:] == Pd and Nd[0] != Pd[0]):
        return 'insert', None
    if len(Pd) < len(Nd) and Nd[-len(Pd):] == Pd:
        return 'suffix', Nd[:len(Nd) - len(Pd)]
    if len(Pd) == len(Nd) + 1 and Pd[1:] == Nd:
        return 'drop', None
    if len(Pd) > len(Nd) and Pd[:len(Nd)] == Nd:
        return 'coarser', None
    if len(Pd) < len(Nd) and Nd[:len(Pd)] == Pd:
        return 'finer', None
    return 'other', None


def seconds(rest):
    """The printed place read each way where it gives two numberings: [] or [first, second]."""
    sq = re.findall(r'\[([^\]]*)\]', rest)
    rd = re.findall(r'(?<=\d)\s*\(([^)]*)\)', rest)
    out = []
    if sq:
        out += [re.sub(r'\[[^\]]*\]', ' ', rest), ' '.join(sq)]
    if rd:
        out += [re.sub(r'(?<=\d)\s*\([^)]*\)', '', rest), re.sub(r'\d+\s*\(([^)]*)\)', r'\1', rest)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--out', required=True)
    ap.add_argument('--json')
    a = ap.parse_args()

    rows = list(bibls(a.repo))
    prev = None
    for b in rows:                                   # each bibl's name, its own or the one it continues
        if prev is not None and prev['entry'] != b['entry']:
            prev = None
        b['place'] = place(b['n']) if b['n'] else None
        b['ib'] = bool(IB.match(b['rest']))
        b['p'] = cut(RANGE.sub(r'\1', IB.sub('', b['rest'])))
        pk = prev['eff'] if prev else ''
        before = b['out_author'] or pk.split('|')[0]     # the author a title alone or an Id. stands for
        b['ctx'] = False
        if b['author'] or b['title']:
            b['named'] = True
            if b['author'] == 'Id.':
                b['eff'] = '%s|%s' % (before, b['title']) if before else ''
                b['idem'] = True
            else:
                b['eff'] = '%s|%s' % (b['author'], b['title'])
                if not b['author']:
                    b['alt'] = '%s|%s' % (before, b['title']) if before else ''
        elif (b['out_author'] or b['out_title']) and not b['ib']:
            b['named'] = b['ctx'] = True
            b['eff'] = '%s|%s' % (b['out_author'], b['out_title'])
            if not b['out_author']:
                b['alt'] = '%s|%s' % (pk.split('|')[0], b['out_title']) if pk.split('|')[0] else ''
        else:
            b['named'] = False
            b['eff'] = pk
        b['prev'] = prev
        b['qualified'] = bool(QUALIFIED.match(IB.sub('', b['rest'])))
        prev = b

    kw, kfw = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    conv, ka = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    wconv = collections.defaultdict(collections.Counter)     # the same, by the n's work: Plutarch's 2., Hp. Epid.
    for b in rows:                                   # what the files say each name means
        if not (b['named'] and not b['ctx'] and not b['ib'] and b['eff'] and b['place']):
            continue
        work, auth, loc = b['place']
        kw[b['eff']][work] += 1
        if b['author'] and b['author'] != 'Id.':
            ka[b['author']][auth] += 1
        d = digits(b['p'])
        if d:
            kfw[(b['eff'], d[0])][work] += 1
        rel, lead = relation(b['p'], cut(loc))
        for c in (conv[b['eff']], wconv[work]):
            c['all'] += 1
            c[rel] += 1
            if rel == 'suffix':
                c['suffix:' + '.'.join(lead)] += 1
                if lead == digits(b['p'])[:len(lead)]:
                    c['suffix:repeat'] += 1
    for b in rows:                                   # the poet printed after a place of the Anthology: 12.125 (Mel.)
        if b['poet'] and b['place']:
            ka[b['poet']][b['place'][1]] += 1

    def own(counter, least):
        tot = sum(counter.values())
        if tot >= least:
            w, c = counter.most_common(1)[0]
            if c >= OWN * tot:
                return w
        return None

    def usual(key, what, work=None):
        return any(c[what] >= CONV_LEAST and c[what] >= CONV * c['all'] for c in (conv[key], wconv[work] if work else {'all': 0, what: 0}))

    def author_of(work):
        return ','.join(work.split(',')[:2]) if work else ''

    renum = collections.Counter()               # (work, printed numbers but the last, the n's but the last), the last alike
    for b in rows:
        if b['place'] and b['place'][2]:
            Pd, Nd = digits(b['p']), digits(cut(b['place'][2]))
            if Pd and Nd and Pd[-1] == Nd[-1] and Pd != Nd:
                renum[(b['place'][0], tuple(Pd[:-1]), tuple(Nd[:-1]))] += 1

    out, kinds = [], collections.Counter()
    works, labels = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for b in rows:
        found = []
        prev = b['prev']
        pw = prev['place'] if prev and prev['place'] else None
        if b['place']:
            labels[b['place'][0]][b['eff'] if b['named'] else '(continuing) ' + b['eff']] += 1
        if not b['n']:
            found.append(('no n', 'the bibl has no n'))
        elif not b['place']:
            found.append(('no place', 'the n is no Perseus abo reference: ' + b['n']))
        else:
            work, auth, loc = b['place']
            P, N = b['p'], cut(loc)
            Pd, Nd = digits(P), digits(N)
            # the work
            if b.get('idem'):
                pa = b['eff'].split('|')[0]
                if pw and author_of(pw[0]) != auth and ka[pa][auth] < RARE:
                    found.append(('Id.', 'Id. after %s (%s), the n names author %s, which %s names %d times' % (
                        prev['printed'], pw[0], auth, pa or 'that citation', ka[pa][auth])))
            elif b['qualified']:
                kinds['unjudged'] += 1
            elif not b['named']:
                if pw and pw[0] != work and not any(ka[x][auth] >= RARE for x in b['between_authors'] + [b['poet']]):
                    o = own(kfw[(b['eff'], Pd[0])], LEAST_FIRST) if Pd else None
                    if o != work:
                        found.append(('continuation', '%s; the citation before, %s, is %s, the n names %s' % (
                            'ib.' if b['ib'] else 'no name printed', prev['printed'], pw[0], work)))
            elif b['eff']:
                key = b['eff']
                if b.get('alt') and sum(kw[b['alt']].values()) >= LEAST_KEY:
                    key = b['alt']
                c = kw[key]
                o1 = own(c, LEAST_KEY)
                o2 = own(kfw[(key, Pd[0])], LEAST_FIRST) if Pd else None
                if work not in (o1, o2) and not (b['ctx'] and pw and pw[0] == work):
                    if o1 or o2:
                        src = kfw[(key, Pd[0])] if o2 else c
                        if src[work] < RARE and src[work] < SHARE * sum(src.values()):
                            o = o2 or o1
                            found.append(('author' if author_of(o) != auth else 'work', '%s is %s in %d of %d bibls, the n names %s (%d)' % (
                                key + (' ' + Pd[0] if o2 else ''), o, src[o], sum(src.values()), work, src[work])))
                    else:
                        kinds['unjudged'] += 1
            # the numbers
            twice = seconds(b['rest'])
            rel, lead = relation(P, N)
            if not Nd and not N:
                found.append(('no place', 'the n names no place: ' + b['n']))
            elif not Pd:
                found.append(('no number', "nothing printed for the n's %s" % loc))
            elif rel == 'same':
                if letters(P) != letters(N) and letters(N) and letters(P):
                    found.append(('letter', 'printed %s, the n %s' % (b['rest'], loc)))
            elif b['after'] and relation(cut(b['after']), N)[0] in ('same', 'suffix', 'drop', 'insert') and digits(cut(b['after'])):
                kinds['second numbering'] += 1
            elif twice and any(relation(cut(IB.sub('', x)), N)[0] in ('same', 'suffix', 'drop') for x in twice):
                kinds['second numbering'] += 1
            elif rel == 'suffix':
                pn = digits(cut(pw[2])) if pw and pw[0] == work else None
                if not (pn is not None and pn[:len(lead)] == lead) and not usual(b['eff'], 'suffix:' + '.'.join(lead), work) \
                        and not (lead == Pd[:len(lead)] and usual(b['eff'], 'suffix:repeat', work)):
                    found.append(('leading numbers', 'printed %s; the n %s adds %s; the citation before %s' % (
                        b['rest'], loc, '.'.join(lead), ('%s (%s)' % (prev['printed'], pw[2])) if pw else 'none')))
            elif rel == 'insert':
                if usual(b['eff'], 'insert', work) or wconv[work]['insert'] >= RENUM:
                    kinds['inserted level'] += 1
                else:
                    found.append(('levels', 'printed %s; the n %s adds a level inside it' % (b['rest'], loc)))
            elif rel == 'drop':
                wn = work.split(',')[-1].lstrip('0') if work.count(',') == 2 else ''
                if not (Pd[0] == wn or usual(b['eff'], 'drop', work)):
                    found.append(('extra number', 'printed %s; the n %s lacks its first number' % (b['rest'], loc)))
            elif rel == 'coarser':
                found.append(('n coarser', 'printed %s; the n %s stops at %s' % (b['rest'], loc, '.'.join(Nd))))
            elif rel == 'finer':
                if not usual(b['eff'], 'finer', work):
                    found.append(('n finer', 'printed %s; the n %s goes on to %s' % (b['rest'], loc, '.'.join(Nd))))
            elif Pd[-1] == Nd[-1] and renum[(work, tuple(Pd[:-1]), tuple(Nd[:-1]))] >= RENUM:
                found.append(('another numbering', 'printed %s, the n %s: %s is %s in %d bibls of this work' % (
                    b['rest'], loc, '.'.join(Pd[:-1]) or '(none)', '.'.join(Nd[:-1]) or '(none)', renum[(work, tuple(Pd[:-1]), tuple(Nd[:-1]))])))
            elif len(Pd) == len(Nd):
                diff = [str(i + 1) for i in range(len(Pd)) if Pd[i] != Nd[i]]
                found.append(('value', 'printed %s, the n %s: level %s differs' % (b['rest'], loc, ','.join(diff))))
            else:
                found.append(('levels', 'printed %s (%d numbers), the n %s (%d)' % (b['rest'], len(Pd), loc, len(Nd))))
        for kind, why in found:
            kinds[kind] += 1
            if kind in COUNTED:
                continue
            works[b['place'][0] if b['place'] else '(none)'][kind] += 1
            out.append((b['entry'], b['index'], b['printed'], b['n'], kind, why))

    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('entry\tindex\tprinted\tn\tkind\twhat differs\n')
        for r in out:
            f.write('\t'.join(str(x).replace('\t', ' ') for x in r) + '\n')
    dis = {k: v for k, v in kinds.items() if k not in COUNTED}
    by_work = sorted(((w, sum(n for k, n in v.items() if k not in COUNTED), dict(v)) for w, v in works.items()), key=lambda x: (-x[1], x[0]))
    summary = {'bibls': len(rows), 'rows written': len(out), 'disagreements': sum(dis.values()),
               'by group': {g: sum(kinds[k] for k in ks) for g, ks in GROUPS.items()},
               'by kind': dict(kinds.most_common()),
               'by work': [{'work': w, 'name': labels[w].most_common(1)[0][0] if labels[w] else '', 'disagreements': t, 'kinds': v}
                           for w, t, v in by_work if t]}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    print('%d bibls; %d disagreements; by kind: %s' % (len(rows), sum(dis.values()), ', '.join('%s %d' % kv for kv in kinds.most_common())))


if __name__ == '__main__':
    main()
