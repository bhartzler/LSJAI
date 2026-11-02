#!/usr/bin/env python3
"""The readers' LSJ corrections applied to Logeion's one-file LSJ (logeion.lsj.xml), as run on 26 to 29 Oct 2026 and
mended on 31 Oct 2026. Verdict B (in the preparation files PHI) = copy B's reading (the item's phi_text), both-wrong = the
`correct` column. The tables are the readers' selected TSVs (#lsj-phi-fixes 2 of 26 to 29 Oct, #lsj-b-fixes 2 of 31 Oct:
'#' lines skipped, the item first, verdict and correct sixth and seventh). An item (from a preparation's items.jsonl)
indexes the preparation's plain text of the entry (a batch's contexts/<unit>.jsonl, current.plain, the article found by
its entry_number, never by its place in the file); the span is found in the entry's XML line by aligning that plain text
with the line's own text. The contexts pin the copy the readers read: an item whose line is no longer the context's is
held, never guessed. Spans overlapping in one line, a span not found, a span crossing a tag: held, listed.
Four rules of placement (31 Oct 2026): an inserted span whose first character continues the token before it (letters
and digits, a dot beside a digit) goes inside the element that token ends, not after its closing tag; an inserted span
stands on the side of a space where copy B has it and takes copy B's space where Logeion's text has none; inserted punctuation sits against its word
(a closing mark, comma or period before the space, an opening mark after it); a change to the visible text of a <bibl> remakes
the trailing segments of its n="Perseus:abo:..." from the new text the way they read from the old, and where they did
not read that way, or the change is more than numbers for numbers, the change is held.
A head's text follows its orth_orig (29 Oct 2026, after the reviewer's note on W-139.35.d1): where a change lies in a
head's orth_orig and the text read as the printed form before (its hyphens and quantity marks taken off), the text
is made from the corrected form the same way; --since <xml> extends the pass to lines changed since that copy.
usage: apply.py --items <items.jsonl> [--items <a later preparation's items.jsonl>, its items taking over] \\
       --xml <in> --out <out> --report <tsv> [--apply] [--since <xml>] --batch <name> <contexts dir> <selected.tsv>... [--batch ...]
       apply.py --repair <repository> <base commit> --report <tsv> [--apply] --items <items.jsonl>... --contexts <dir>...:
       the four rules applied to what is already in the repository's greatscott*.xml, entry by entry against the base
       commit; nothing else changes."""
import sys, os, json, re, hashlib, collections, html, difflib
import xml.parsers.expat
def well_formed(line):
    try: xml.parsers.expat.ParserCreate().Parse('<r>' + line + '</r>', True); return True
    except Exception: return False
def continues(a, b):   # the characters either side of a boundary are one token: letters and digits, or a dot beside a digit
    return (a.isalnum() and b.isalnum()) or (a == '.' and b.isdigit()) or (a.isdigit() and b == '.')
CLOSE = re.compile(r'</\w+>$')
def inside(raw, s, new):   # rule 1: an insertion at s after closing tags goes before them when it continues the token they close
    k = s
    while (m := CLOSE.search(raw, 0, k)): k = m.start()
    return k if k < s and k > 0 and new and continues(raw[k - 1], new[0]) else s
CLOSERS, OPENERS = set(').,;:]·'), set('([')
OPEN = re.compile(r'<\w[^>]*>$'); SHUT = re.compile(r'</\w+>')
def attach(text, j1, j2, new):   # rule 4: where an insertion at j1..j2 goes: a span opening with a closing mark goes back
    k, crossed = j1, False       # over the space before it, a span ending in an opening mark forward over the space after it
    if new[:1] in CLOSERS:
        while True:
            if k > 0 and text[k - 1].isspace(): k -= 1; crossed = True
            elif (m := OPEN.search(text, 0, k)): k = m.start()
            else: break
    elif new[-1:] in OPENERS:
        k = j2
        while True:
            if k < len(text) and text[k].isspace(): k += 1; crossed = True
            elif (m := SHUT.match(text, k)): k = m.end()
            else: break
    return k if crossed else None
def near(raw, s, step):   # where the nearest character of text before (step -1) or after (+1) position s is, tags skipped
    i = s - 1 if step < 0 else s
    while 0 <= i < len(raw):
        if raw[i] == '>' and step < 0: i = raw.rfind('<', 0, i) - 1; continue
        if raw[i] == '<' and step > 0: i = raw.find('>', i) + 1; continue
        return i
    return None
def beside(t, p):   # the text's two characters before and two after position p, tags skipped ('\0' past an end)
    l = near(t, p, -1); r = near(t, p, 1)
    l2 = near(t, l, -1) if l is not None else None; r2 = near(t, r + 1, 1) if r is not None else None
    ch = lambda i: '\0' if i is None else t[i]
    return ch(l2) + ch(l), ch(r) + ch(r2)
def word(pair, step):   # the nearest character that is not a space, on that side
    x = pair[1] if step < 0 else pair[0]
    return (pair[0] if step < 0 else pair[1]) if x.isspace() else x
def agree(have, want):   # copy B's spaces beside an insertion are there, and the nearest words either side are copy B's;
    for h, w, step in ((have[0], want[0], -1), (have[1], want[1], 1)):   # a space Logeion has and copy B lacks is kept
        if '\0' in w: continue
        if (w[1] if step < 0 else w[0]).isspace() and not (h[1] if step < 0 else h[0]).isspace(): return False
        if word(h, step) != word(w, step): return False
    return True
def place(t, p, seg, want):   # rule 2: insertion seg at p in text t (without it): where copy B has a space beside the span and
    if want is None: return p, seg                              # the text has none, the span crosses the text's space or
    (hp, hn), (wp, wn) = beside(t, p), want                     # takes copy B's, whichever leaves copy B's words either
    if wp[1].isalpha() and wn[0].isalpha() and (hp[1].isspace() or hn[0].isspace()): return None   # side; None (held) when
    if not ((wp[1].isspace() and not hp[1].isspace()) or (wn[0].isspace() and not hn[0].isspace())): return p, seg   # none
    l, r = near(t, p, -1), near(t, p, 1); tries = []   # does, or when copy B has the span inside a word and the text a space
    if l is not None and t[l] == ' ': tries.append((l, seg))
    if r is not None and t[r] == ' ': tries.append((r + 1, seg))
    pre = ' ' if wp[1] == ' ' and l is not None and not t[l].isspace() else ''
    post = ' ' if wn[0] == ' ' and r is not None and not t[r].isspace() else ''
    if pre or post: tries.append((p, pre + seg + post))
    for q, s2 in tries:
        u = t[:q] + s2 + t[q:]; a = q + len(s2) - len(s2.lstrip(' ')); b = q + len(s2.rstrip(' '))
        if agree(beside(u[:a] + u[b:], a), want): return q, s2
    return None
def articles(path):   # a contexts file's articles by their entry_number (a re-cut's files are not in entry order)
    with open(path, encoding='utf-8') as h: return {int(c['entry_number']): c for c in map(json.loads, h)}
def b_side(c, it, new):   # copy B's two characters either side of the item's span; None when the inserted text is not copy
    bp, (pa, pb) = c['phi']['plain'], it['phi_range']   # B's (both-wrong) or the range is not the text
    if html.unescape(new) != it['phi_text'] or bp[pa:pb] != it['phi_text']: return None
    return bp[max(0, pa - 2):pa].rjust(2, '\0'), bp[pb:pb + 2].ljust(2, '\0')
BIBL = re.compile(r'(<bibl\b[^>]*?\bn=")([^"]*)("[^>]*>)(.*?)</bibl>', re.S)
NUM = re.compile(r'\d+[a-z]?')
def shape(t): return NUM.sub(lambda m: '#a' if m.group(0)[-1].isalpha() else '#', t)
def readings(t):   # the two ways Perseus's abo segments read off the visible text: its numbers, or with a letter its own segment
    nums = NUM.findall(t)
    return nums, [p for x in nums for p in ([x[:-1], x[-1]] if x[-1].isalpha() else [x])]
def renumber(n, old, new):   # rule 3: the n for the bibl's new visible text; None when it cannot be derived
    old, new = re.sub(r'<[^>]+>', '', old), re.sub(r'<[^>]+>', '', new)
    if not n.startswith('Perseus:abo:'): return n
    parts = n.split(':'); head, tail = parts[:3], parts[3:]; k = len(tail)
    if not k or readings(old)[0] == readings(new)[0] or any(r[-k:] == tail for r in readings(new)): return n
    for i, r in enumerate(readings(old)):
        if r[-k:] == tail and len(r) >= k:
            if shape(old) != shape(new): return None
            return ':'.join(head + readings(new)[i][-k:])
    return None
def retag(old, new):   # the new line's bibl n's remade; and the bibls (as ranges of the old line) whose n cannot be
    A, B = list(BIBL.finditer(old)), list(BIBL.finditer(new))
    if len(A) != len(B): return new, [(0, len(old))]
    out, bad, last = [], [], 0
    for a, b in zip(A, B):
        if a.group(4) == b.group(4) or a.group(2) != b.group(2): continue
        n = renumber(b.group(2), a.group(4), b.group(4))
        if n is None: bad.append((a.start(), a.end()))
        elif n != b.group(2): out += [new[last:b.start(2)], n]; last = b.end(2)
    return ''.join(out) + new[last:], bad
args = sys.argv[1:]
def opt(name):
    i = args.index(name); return args[i + 1]
def repair(repo, base, rep, apply, items_paths, ctxdirs):
    """What the four rules would have prevented, found in the repository's files entry by entry against the base commit
    and mended in place: an insertion that continues a token after a closing tag (rule 1), an insertion on the other side of a
    space from copy B, or without copy B's space beside it (rule 2; copy B's text from the preparations' items and contexts), a bibl's n left from its old
    number (rule 3), punctuation inserted on the wrong side of a space or a deletion that left a space before a closing
    mark (rule 4). Nothing else changes."""
    import subprocess, glob
    items = {}
    for path in items_paths:
        for l in open(path, encoding='utf-8'): d = json.loads(l); items[d['item']] = d
    def context_of(it):   # the preparation's context of an item: the contexts dir whose entry is the item's subject
        for d in ctxdirs:
            f = os.path.join(d, 'contexts', it['unit'] + '.jsonl')
            if not os.path.exists(f): continue
            c = articles(f).get(int(it['context_entry'])); a, b = it['current_range']
            if c and c['subject'] == it['subject'] and c['current']['plain'][a:b] == it['current_text'] and c['phi']['plain'][slice(*it['phi_range'])] == it['phi_text']: return c
    sides = {}   # (entry, the inserted text) -> copy B's space before, after
    for r in [l.rstrip('\n').split('\t') for l in open(os.path.join(repo, 'corrections', 'corrections.tsv'), encoding='utf-8')][1:]:
        if r[5] == '' and r[2] in items and (c := context_of(items[r[2]])): sides[(r[0], html.escape(r[6], quote=False))] = b_side(c, items[r[2]], r[6])
    ENTRY = re.compile(r'<div2 [^>]*orig_id="(n\d+[a-z]*)"[^>]*>.*?</div2>', re.S)
    report, status = [], collections.Counter()
    def note(i, rule, what, before, after): status[rule] += 1; report.append([i, rule, what, before, after])
    for path in sorted(glob.glob(os.path.join(repo, 'dictionary', 'greatscott*.xml'))):
        name = os.path.basename(path)
        B = {m.group(1): m.group(0) for m in ENTRY.finditer(subprocess.run(['git', '-C', repo, 'show', f'{base}:{name}'], capture_output=True, text=True, check=True).stdout)}
        text = open(path, encoding='utf-8', newline='').read(); out, last = [], 0
        for m in ENTRY.finditer(text):
            i, ours = m.group(1), m.group(0); old = B.get(i)
            if old is None or old == ours: continue
            fixed = ours
            for tag, i1, i2, j1, j2 in reversed(difflib.SequenceMatcher(None, old, ours, autojunk=False).get_opcodes()):
                if tag == 'delete' and j1 > 0 and ours[j1 - 1] == ' ' and ours[j1:j1 + 1] in CLOSERS:
                    fixed = fixed[:j1 - 1] + fixed[j1:]; note(i, 'rule 4', 'the space before the mark taken with the deletion', ours[j1 - 25:j1 + 5], fixed[j1 - 25:j1 + 4]); continue
                if tag != 'insert': continue
                seg = ours[j1:j2]; w = attach(ours, j1, j2, seg)
                if w is not None and w < j1:
                    fixed = fixed[:w] + seg + fixed[w:j1] + fixed[j2:]; note(i, 'rule 4', 'the mark before the space', ours[w - 20:j2 + 5], fixed[w - 20:j2 + 5]); continue
                if w is not None:
                    fixed = fixed[:j1] + fixed[j2:w] + seg + fixed[w:]; note(i, 'rule 4', 'the mark after the space', ours[j1 - 20:w + 5], fixed[j1 - 20:w + 5]); continue
                k = inside(ours, j1, seg)
                if k < j1:
                    fixed = fixed[:k] + seg + fixed[k:j1] + fixed[j2:]; note(i, 'rule 1', 'moved inside the element', ours[k - 20:j2 + 5], fixed[k - 20:j2 + 5]); continue
                if (i, seg) in sides:
                    t = ours[:j1] + ours[j2:]; got = place(t, j1, seg, sides[(i, seg)])
                    if got is None: note(i, 'rule 2 not placed', "no placement agrees with copy B on both sides", ours[j1 - 25:j2 + 10], ''); continue
                    q, s2 = got
                    if (q, s2) != (j1, seg):
                        fixed = fixed[:j1] + fixed[j2:]; fixed = fixed[:q] + s2 + fixed[q:]
                        note(i, 'rule 2', "on copy B's side of the space, with its space", ours[min(q, j1) - 20:max(q, j2) + 5], fixed[min(q, j1) - 20:max(q, j1) + len(s2) + 5])
            retagged, bad = retag(old, fixed)
            for a in BIBL.finditer(old):
                if (a.start(), a.end()) in bad: note(i, 'rule 3 held', 'the n cannot be derived from the new text', a.group(0), BIBL.findall(fixed)[[x.start() for x in BIBL.finditer(old)].index(a.start())][3])
            for a, b in zip(BIBL.finditer(fixed), BIBL.finditer(retagged)):
                if a.group(2) != b.group(2): note(i, 'rule 3', 'n remade from the new text', a.group(2), b.group(2))
            fixed = retagged
            if fixed == ours: continue
            assert well_formed(fixed), i
            out += [text[last:m.start()], fixed]; last = m.end()
        new_text = ''.join(out) + text[last:]
        assert new_text.count('<div2') == text.count('<div2')
        if apply and new_text != text:
            with open(path, 'w', encoding='utf-8', newline='') as f: f.write(new_text)
    with open(rep, 'w', encoding='utf-8') as f:
        f.write('entry\trule\twhat\tbefore\tafter\n' + ''.join('\t'.join(x) + '\n' for x in report))
    print(dict(status), 'insertions with copy B known', len(sides))
if '--repair' in args:
    i = args.index('--repair')
    repair(args[i + 1], args[i + 2], opt('--report'), '--apply' in args, [args[j + 1] for j, x in enumerate(args) if x == '--items'], [args[j + 1] for j, x in enumerate(args) if x == '--contexts'])
    sys.exit(0)
items_paths = [args[i + 1] for i, a in enumerate(args) if a == '--items']; src, out, rep = opt('--xml'), opt('--out'), opt('--report'); apply = '--apply' in args
batches = []
i = 0
while i < len(args):
    if args[i] == '--batch':
        name, ctxdir = args[i + 1], args[i + 2]; files = []; i += 3
        while i < len(args) and not args[i].startswith('--'): files.append(args[i]); i += 1
        batches.append((name, ctxdir, files))
    else: i += 1
items = {}
for items_path in items_paths:   # a later file's item takes over an earlier one's (the to10 preparation of 29 Oct re-cut W-130 on)
    for l in open(items_path, encoding='utf-8'):
        d = json.loads(l); items[d['item']] = d
contexts = {}
def context(ctxdir, it):
    k = (ctxdir, it['unit'])
    if k not in contexts:
        contexts[k] = articles(os.path.join(ctxdir, 'contexts', it['unit'] + '.jsonl'))
    c = contexts[k][int(it['context_entry'])]
    assert c['subject'] == it['subject'], (it['item'], c['subject'], it['subject'])
    return c
text = open(src, encoding='utf-8', newline='').read()
lines = text.split('\n')
HEAD = re.compile(r'<head([^>]*)>(.*?)</head>', re.S); ORTH = re.compile(r'orth_orig="([^"]*)"'); ENT = re.compile(r'&(#x[0-9A-Fa-f]+|#[0-9]+|[A-Za-z]+);')
def stripped(raw):
    S, M = [], []; i = 0; head_done = False
    while i < len(raw):
        ch = raw[i]
        if ch == '<':
            j = raw.find('>', i)
            if j < 0: S.append(ch); M.append(i); i += 1; continue
            tag = raw[i:j + 1]
            if not head_done and tag.startswith('<head'):
                m = ORTH.search(tag); end = raw.find('</head>', j)
                if m and end >= 0:
                    base = i + m.start(1)
                    for k, c in enumerate(m.group(1)): S.append(c); M.append(base + k)
                    head_done = True; i = end + len('</head>'); continue
                head_done = True
            i = j + 1; continue
        if ch == '&':
            m = ENT.match(raw, i)
            if m:
                for c in html.unescape(m.group(0)): S.append(c); M.append(i)
                i = m.end(); continue
        S.append(ch); M.append(i); i += 1
    return ''.join(S), M
def locate(raw, plain, a, b):
    S, M = stripped(raw)
    sm = difflib.SequenceMatcher(None, plain, S, autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        if i <= a and b <= i + n and (b > a or (a < i + n or (a == i + n and n))):
            if b > a: return M[j + (a - i)], M[j + (b - i) - 1] + 1
            s = M[j + (a - i)] if a < i + n else M[j + n - 1] + 1
            return s, s
    return None
changes = collections.defaultdict(list); report = []; status = collections.Counter(); seen = set()
for name, ctxdir, files in batches:
    rows = []
    for f in files: rows += [l.rstrip('\n').split('\t') for l in open(f, encoding='utf-8') if not l.startswith('#')]
    for r in rows:
        item, verdict, correct = r[0], r[5], r[6]
        if verdict in ('B', 'PHI'): new = items[item]['phi_text']   # copy B's reading: B in the tables of 31 Oct on, PHI before
        elif verdict == 'both-wrong': new = correct
        else: continue
        new = html.escape(new, quote=False)   # PHI's text is text: its < > & become entities in the XML (W-035.14, W-076.7, W-079.15)
        if item in seen: report.append([name, item, 'same', 'listed twice', '', '']); continue
        seen.add(item)
        it = items[item]; c = context(ctxdir, it)
        ln = it['current_physical_line']; raw = lines[ln - 1]; plain = c['current']['plain']; a, b = it['current_range']; cur = it['current_text']
        def hold(why): report.append([name, item, 'held', why, cur, new]); status['held'] += 1
        if raw != c['current']['raw_xml']: hold('the line is no longer the context\'s (changed since the preparation)'); continue
        if plain[a:b] != cur: hold(f'the range is not the text ({plain[a:b]!r})'); continue
        if a == b and (k := attach(plain, a, a, html.unescape(new))) is not None: a = b = k   # rule 4
        elif not new and a > 0 and plain[a - 1].isspace() and plain[b:b + 1] in CLOSERS: a -= 1; cur = plain[a:b]   # rule 4 for a deletion
        span = locate(raw, plain, a, b)
        if span is None: hold('not aligned to the line'); continue
        s, e = span
        if raw[s:e] != cur: hold(f'the line reads {raw[s:e]!r} there'); continue
        if a == b:   # an insertion: rule 2, then rule 1
            got = place(raw, s, new, b_side(c, it, new))
            if got is None: hold("no placement agrees with copy B's spacing on both sides"); continue
            s, new = got; s = e = inside(raw, s, new)
        changes[ln].append((s, e, cur, new, item, name))
for ln, ch in changes.items():
    ch.sort(); keep = []
    for x in ch:
        if keep and x[0] < keep[-1][1]:
            if (x[0], x[1], x[3]) == (keep[-1][0], keep[-1][1], keep[-1][3]): report.append([x[5], x[4], 'same', 'the same change twice', x[2], x[3]]); status['same'] += 1; continue
            report.append([x[5], x[4], 'held', f'overlaps {keep[-1][4]}', x[2], x[3]]); status['held'] += 1; continue
        keep.append(x)
    changes[ln] = keep
def changed(raw, ch):
    for s, e, cur, new, item, name in reversed(ch):
        assert raw[s:e] == cur
        raw = raw[:s] + new + raw[e:]
    return raw
for ln, ch in changes.items():
    # a change inside a <bibl> takes its n along (rule 3); where the n cannot be derived, the changes in that bibl are held
    raw, bad = retag(lines[ln - 1], changed(lines[ln - 1], ch))
    if bad:
        held = [x for x in ch if any(bs <= x[0] and x[1] <= be for bs, be in bad)]
        for s, e, cur, new, item, name in held: report.append([name, item, 'held', 'a citation\'s number: its n attribute cannot be derived from the new text', cur, new]); status['held'] += 1
        ch = changes[ln] = [x for x in ch if x not in held]
        raw, bad = retag(lines[ln - 1], changed(lines[ln - 1], ch))
        assert not bad
    # a changed line must stay well-formed XML: else the whole line is left as it was and its items held
    if well_formed(raw):
        for s, e, cur, new, item, name in ch: report.append([name, item, 'applied', f'line {ln}', cur, new]); status['applied'] += 1
        lines[ln - 1] = raw
    else:
        for s, e, cur, new, item, name in ch: report.append([name, item, 'held', f'line {ln} would not be well-formed XML with the change', cur, new]); status['held'] += 1
# the head's text follows its orth_orig: Logeion's text of a head is the printed form (orth_orig) without its hyphens and
# quantity marks; a change inside orth_orig that left the text as it was leaves the head saying two things
import unicodedata
QUANT = {'ᾰ': 'α', 'ᾱ': 'α', 'ῐ': 'ι', 'ῑ': 'ι', 'ῠ': 'υ', 'ῡ': 'υ', 'Ᾰ': 'Α', 'Ᾱ': 'Α', 'Ῐ': 'Ι', 'Ῑ': 'Ι', 'Ῠ': 'Υ', 'Ῡ': 'Υ'}
def rule(o):   # the printed form's supplement brackets, closing ano teleia (a glossed word), hyphens and quantity marks taken off
    o = o.replace('&lt;', '').replace('&gt;', '').rstrip('\u0387\u00b7 ')
    o = ''.join(QUANT.get(c, c) for c in o.replace('-', ''))
    o = ''.join(c for c in unicodedata.normalize('NFD', o) if c not in '\u0304\u0306')
    return unicodedata.normalize('NFC', o)
def grave_only(a, b):   # the two differ only in a grave for an acute: the printed form's grave before a following word is not the headword's
    a, b = unicodedata.normalize('NFD', a), unicodedata.normalize('NFD', b)
    return a != b and a.replace('\u0300', '\u0301') == b.replace('\u0300', '\u0301')
HEADSTRICT = re.compile(r'<head[^>]*\borth_orig="([^"]*)"[^>]*>([^<]*)</head>')
before_lines = text.split('\n')
if '--since' in args:
    since_lines = open(opt('--since'), encoding='utf-8', newline='').read().split('\n')
    assert len(since_lines) == len(before_lines), 'the --since copy has another number of lines'
    before_lines = since_lines
who_of = {ln: ','.join(sorted({x[5] for x in ch})) for ln, ch in changes.items() if ch}
for ln, (b, a) in enumerate(zip(before_lines, lines), 1):
    if b == a: continue
    who = who_of.get(ln, 'since'); mb, ma = HEADSTRICT.search(b), HEADSTRICT.search(a)
    hb, ha = HEAD.search(b), HEAD.search(a)
    if not (hb and ha): continue
    ob = ORTH.search(hb.group(1)); oa = ORTH.search(ha.group(1))
    if not (ob and oa) or ob.group(1) == oa.group(1): continue
    if not (mb and ma): report.append([who, f'line {ln}', 'head kept', f'tags inside the head; orth_orig {ob.group(1)} -> {oa.group(1)}', '', '']); status['head kept'] += 1; continue
    tb, ta = mb.group(2), ma.group(2)
    if tb != ta: continue
    if tb != rule(mb.group(1)): report.append([who, f'line {ln}', 'head kept', f'the text {tb} did not read as orth_orig {mb.group(1)} before; now {ma.group(1)}', '', '']); status['head kept'] += 1; continue
    want = rule(ma.group(1))
    if want == ta: continue
    if len(ta) == 1: report.append([who, f'line {ln}', 'head kept', f'a letter entry: its text is the letter; orth_orig {mb.group(1)} -> {ma.group(1)}', ta, want]); status['head kept'] += 1; continue
    if grave_only(ta, want): report.append([who, f'line {ln}', 'head kept', f'the printed form took a grave; the headword keeps its acute; orth_orig {mb.group(1)} -> {ma.group(1)}', ta, want]); status['head kept'] += 1; continue
    new_raw = a[:ma.start(2)] + want + a[ma.end(2):]
    if not well_formed(new_raw): report.append([who, f'line {ln}', 'head kept', 'not well-formed with the text changed', tb, want]); status['head kept'] += 1; continue
    lines[ln - 1] = new_raw; report.append([who, f'line {ln}', 'head followed', f'orth_orig {mb.group(1)} -> {ma.group(1)}', tb, want]); status['head followed'] += 1
new_text = '\n'.join(lines)
with open(rep, 'w', encoding='utf-8') as f:
    f.write('batch\titem\tstatus\twhy\told\tnew\n' + ''.join('\t'.join(x) + '\n' for x in report))
print(dict(status), 'lines changed', len([1 for ch in changes.values() if ch]))
if apply:
    with open(out, 'w', encoding='utf-8', newline='') as f: f.write(new_text)
    print('written', out, hashlib.sha256(new_text.encode('utf-8')).hexdigest())
