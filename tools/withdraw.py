"""Withdraw corrections the printed page contradicts: the entry's text goes back to Logeion's at those places.

On 2 Nov 2026 an AI reader read the scan's crop of every corrected entry (a second
reader agreed on 95 percent of 150) and corrections/corrections.tsv took three columns: print (new, old, other,
not visible), print quote, print leaf. Where the page prints Logeion's text (print old) and the correction's
evidence was copy B's word (evidence source copy B, B, current, Logeion), the correction restored nothing: copy
B had supplemented the print. Those rows, at certainty 4 or 5, are withdrawn (the agent's ruling,
2 Nov 2026); the rows at 2 or 3 wait for a second reader.

How: for each such row, the entry's XML now is compared with Logeion's at the base commit (5f4f476, the copy the
corrections were carried onto), character by character; the difference whose Logeion side is the row's old text
and whose side here is the row's new text is the correction, and it is undone by taking Logeion's text there.
A row whose difference cannot be found alone (merged with an inserted tag, or the text has moved) is held and
listed. The row's `in LSJAI` becomes "withdrawn: the page prints Logeion's text" so the build stops counting it
as applied; nothing else in the table changes.

Usage: python3 -I tools/withdraw.py [--apply] [--min 4]   (a dry run without --apply)
"""
import argparse, csv, difflib, glob, io, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '5f4f4764b'
TABLE = os.path.join(REPO, 'corrections', 'corrections.tsv')
DIV = re.compile(rb'<div2 [^>]*orig_id="([^"]+)"[^>]*>.*?</div2>', re.S)
WITHDRAWN = "withdrawn: the page prints Logeion's text"
COPY_B = ('copy B', 'B', 'current', 'Logeion')


def entries(data):
    """{orig_id: (start, end)} of each entry's bytes in a file."""
    return {m.group(1).decode(): (m.start(), m.end()) for m in DIV.finditer(data)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--min', type=int, default=4, help='the least certainty withdrawn (default 4)')
    a = ap.parse_args()
    with io.open(TABLE, encoding='utf-8', newline='') as f:
        rd = csv.reader(f, delimiter='\t'); head = next(rd); rows = [dict(zip(head, r)) for r in rd]
    sure = {}   # the print reader's certainty, by (entry, item), from corrections/withdraw.tsv (the reader's answers)
    wp = os.path.join(REPO, 'corrections', 'withdraw.tsv')
    if os.path.exists(wp):
        with io.open(wp, encoding='utf-8') as f:
            for w in csv.DictReader(f, delimiter='\t'):
                sure[(w['entry'], w['item'])] = int(w['certainty'] or 0)
    want = [r for r in rows if r.get('print') == 'old' and r['evidence source'] in COPY_B and sure.get((r['entry'], r['item']), 0) >= a.min and r['in LSJAI'] != WITHDRAWN]
    print('rows to withdraw:', len(want))
    by_file = {}
    for path in sorted(glob.glob(os.path.join(REPO, 'dictionary', 'greatscott[0-9][0-9].xml'))):
        for oid in entries(open(path, 'rb').read()):
            by_file[oid] = path
    done, held = [], []
    changed = {}
    for r in want:
        oid = r['entry']; path = by_file.get(oid)
        if not path:
            held.append((r, 'entry not in the files')); continue
        name = os.path.basename(path)
        if name not in changed:
            changed[name] = {'now': open(path, 'rb').read().decode('utf-8'),
                             'base': subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (BASE, name)], capture_output=True, check=True).stdout.decode('utf-8')}
        now, base = changed[name]['now'], changed[name]['base']
        mn = re.search(r'<div2 [^>]*orig_id="%s"[^>]*>.*?</div2>' % re.escape(oid), now, re.S)
        mb = re.search(r'<div2 [^>]*orig_id="%s"[^>]*>.*?</div2>' % re.escape(oid), base, re.S)
        if not mn or not mb:
            held.append((r, 'entry not in both copies')); continue
        cur, old_entry = mn.group(0), mb.group(0)
        sm = difflib.SequenceMatcher(None, old_entry, cur, autojunk=False)
        hit = None
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ('replace', 'insert', 'delete') and old_entry[i1:i2] == r['old'] and cur[j1:j2] == r['new']:
                hit = (i1, i2, j1, j2); break
        if hit is None and r['new'] and 1 <= cur.count(r['new']) <= 3 and r['old'] in old_entry:
            new_entry = cur.replace(r['new'], r['old'])                 # the new text stands once or twice (a head's attribute and its text): every one goes back to the old
            if difflib.SequenceMatcher(None, old_entry, new_entry, autojunk=False).ratio() <= sm.ratio():
                held.append((r, 'the entry would move away from Logeion\'s')); continue
        elif hit is None:
            held.append((r, 'the difference is not found alone')); continue
        else:
            i1, i2, j1, j2 = hit
            new_entry = cur[:j1] + old_entry[i1:i2] + cur[j2:]
        changed[name]['now'] = now[:mn.start()] + new_entry + now[mn.end():]
        r['in LSJAI'] = WITHDRAWN
        done.append(r)
    print('withdrawn:', len(done), '| held:', len(held))
    for r, why in held[:12]:
        print('  held', r['entry'], r['headword'], repr(r['old'][:20]), '->', repr(r['new'][:20]), ':', why)
    if a.apply:
        for name, d in changed.items():
            with open(os.path.join(REPO, name), 'wb') as f:
                f.write(d['now'].encode('utf-8'))
        with io.open(TABLE, 'w', encoding='utf-8', newline='') as f:
            f.write('\t'.join(head) + '\n')
            for r in rows:
                f.write('\t'.join(r.get(h, '').replace('\t', ' ').replace('\n', ' ') for h in head) + '\n')
        print('applied to', len(changed), 'files; the table marks', len(done), 'rows withdrawn')
    else:
        print('dry run; nothing written')


if __name__ == '__main__':
    main()
