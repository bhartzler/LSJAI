#!/usr/bin/env python3
"""Cut the citation previews: for every citation in the dictionary (every <bibl>), from every text
that holds its place, the cited line with the line before it and the line after it, three lines,
never more, and, from every open English translation numbered as a text is, its passage. A text is
the TLG-E or PHI-5 store, and every open Perseus or First1KGreek edition of a Greek work (below, The
open texts); each is kept apart, and the page chooses which to show (site/index.html's SOURCES).

    python3 -I tools/snippets.py --philology <Philology-fable> --masters <Philology-masters> \\
        --tlg <TLG-E store> --latin <PHI-5 Latin store> --papyri <DDbDP store> \\
        --inscriptions <Greek Inscriptions store> --morph <morph binary> \\
        --perseus <Philology-masters/Perseus> [--jobs 6]

Reads, here, greatscott01.xml to greatscott86.xml and readings/lsj-readings.txt; outside the
repository, the texts, which are not in this repository, and the project's tools:

  --tlg, --latin   the two stores of the Philology project the readers' lines were drawn from, made
                   from the TLG-E and PHI-5 shelves of Philology-masters (Philology-fable's
                   Docs/STORE.md); a place is a work and a citation in their numbering
  --papyri         the store of PHI 7's DDP files, the Duke Databank of Documentary Papyri
                   (DDbDP), its volumes works and its documents texts (texts.txt, texts.line), read
                   through tools/papyri_places.py, which says how a papyrus reference finds its
                   document and line there (the sidecar keys no papyrus: no-work)
  --inscriptions   the store of PHI's Greek Inscriptions, its books works and its documents texts,
                   read through tools/inscription_places.py, which says how LSJ's inscription
                   labels (a corpus and its printed numbers, no reference) find their document and
                   line there
  --philology      Philology-fable: its citation packager (Port/tools/citations/n1_package.py),
                   imported, not copied (the store reader, its betacode drawing, the Unicode the
                   readers read, the lexicon's forms of each entry's lemmas), and its lexicon's
                   citation sidecar (Lexicon/lsj/citations.txt), which resolves every bibl's
                   Perseus reference (n="Perseus:abo:tlg,0012,001:14:271") to a place
  --masters        Philology-masters: Catalogue/editions.txt (each work's edition and shelf, each
                   translation's translator) and the English translations of the Perseus shelf
                   whose rights are open (0)
  --perseus        the Perseus shelf of Philology-masters, its Greek texts from Perseus and
                   First1KGreek whose rights are open (0), read through tools/perseus_places.py
                   (--jobs processes side by side), which says how a place is found in them

and writes docs/snippets/<tree>/<block>.json, in the blocks of docs/entries (site/build.py's
ordered()), {entry id: [preview]} in citation order, a citation's the newest edition first, in seven
trees: perseus and first1k (the open texts), greek and latin (the TLG-E and PHI-5 stores), papyri (the
DDbDP), inscriptions (PHI's Greek Inscriptions) and english (the translations). A text's preview has
these keys (one absent where it would be null):

  n            the citation's number in the entry: its n-th <bibl> of the dictionary's own, the
               ones the sidecar holds; a bibl a pass of LSJAI marked (resp, tools/mark_citations.py)
               is numbered after them and has no preview yet (site/build.py's cite_order()); the bibls a pass of LSJAI marked (resp) follow
               the dictionary's own, N+1 onwards, resp by resp and each in its order, as site/build.py's
               cite_order() numbers them
  cite         the first 8 hex digits of the SHA-1 of the <bibl> element's bytes the preview is cut from;
               the build compares it with its own stamp and stops when a citation changed under its
               preview (Codex, 1 Nov 2026)
  status       read (a reading is in force for it: of a subject the latest row of
               readings/lsj-readings.txt by its `when`, as the Philology app reads them) or unread
  kind         a read citation's verdict: verified, repaired, scholion, relocated, unresolved,
               rejected; for the last two the lines are where the dictionary's reference points
  urn          the place cut: the reading's line where it names one, else the sidecar's; from an
               open text the work as that text's CTS URN names it and the place LSJ's reference
               names there (urn:cts:greekLit:tlg0059.tlg030:529c), no edition after the work; of a
               papyrus the store's volume and the place in its numbering, the cited line's own
               citation where the reference names a line the document holds
               (urn:cts:ddp:ddp0129.ddp005:535.r,2.48), else the document's first level and the line
               cited (urn:cts:ddp:ddp0031.ddp011:59012 rp.33, a line the DDbDP numbers otherwise) or
               the document alone (a reference with no line); of an inscription the same, in the
               store's book (urn:cts:ins:ins0010.ins019:956.col. I.58)
  ref          the place as a reader of LSJ writes it: the work as LSJ abbreviates it (the
               abbreviation its citations of that work print most often, with the work's number
               where LSJ prints one: D. 11 for the eleventh speech), the URN's citation; of an
               inscription the book as PHI names it (IG II² 956.col. I.58)
  source       the work and its edition, as the catalogue names them (not the shelf); from an open
               text with its shelf after it: Plato, Respublica, ed. John Burnet, Oxford 1905 (Perseus);
               of a papyrus the volume as the DDP file names it, its edition from the catalogue, then
               the Databank: PSI 5, ed. G. Vitelli; M. Norsa, Florence 1917 (DDbDP, PHI 7);
               of an inscription the book as PHI names it, its edition, then the collection:
               IG II², ed. Johannes Kirchner; Ericus Sironen, Berlin … (PHI Greek Inscriptions)
  at, lines    the three lines (before, cited, after), each its citation in the held text and its
               text in Unicode, null past a work's start or end; from an open text in prose, its
               sentences and the places they stand in (The open texts)
  form         what the page marks on the cited line: the form of the headword the lemma check
               found (its piece on the line, where hyphenated); only where it found none, the words
               of the line that chose it, space-separated: forms of the entry's lemmas, forms the
               entry names, its headword, words of the quotation the citation supports (the terms
               the readers' packages searched: n1_package.package)
  found        the lemma check, mechanical, no reader: the first word of the cited line that is a
               form of the entry: a form of its lemmas in the Philology lexicon's forms table, one
               of its heads (the headword and the entry's bold forms like it: ἀκοίτης lists
               ἄκοιτις), or a word morph (--morph) analyses to a lemma the lexicon ties to the
               entry or one spelling a head (case ignored; accents too for a word it analyses
               no other way: analyse()); every word tested whole, a word hyphenated across
               two printed lines joined (ἀγρά-|φοις is ἀγράφοις, its piece on the line marked in
               form); else a word whose morph lemma is a word of the entry's own text, outside its
               citations, of five letters or more and like its headword (akin()), accents exact, case
               folded (Bruce, 1 Nov 2026: Κοντοπορεία's Plb. 16.16.4 has Κοντοπορίαν, the entry names
               Κοντοπορία: named()); null where none stands there; absent where the lexicon gives the entry no
               lemma and morph analyses no word of the line (not testable)
  url          the text online: an open text's passage in the Scaife reader of the Perseus Digital
               Library (urn:cts:greekLit:tlg0059.tlg030.perseus-grc2:7.529, the edition's CTS
               passage of the cited line: perseus_places.cts); a work of TLG-E in the TLG's browser
               at its start (tlg_url(), which has the line's place for an address when one is known);
               a work of PHI-5 in the PHI Latin Texts at the work's start (latin_url()); a papyrus's
               document at papyri.info's DDbDP page (papyri_places' url()); an inscription's at PHI's
               site by its PHI number (inscription_places' url())
  prefer       true on the corpus line of Bekker's page and line, which the page shows first

and a translation's: n, source (its translator, edition and shelf as the catalogue names them), at
(its citation in the translation), lines ([before, cited, after], each line's own where the
translation numbers every line, else [null, the passage holding the cited line, null]), url (its
passage in the Scaife reader), and cut where the passage is over 200 words and lines hold part of it,
marked … where trimmed: "sentences" (the sentences that carry the cited line, found by its names,
numbers and rare words and the entry's gloss before the citation) or true (none found: its first 200
words).

A line is the held text's own: a verse in verse; in prose the edition's printed line, which TLG-E
and PHI-5 number within the section (Pl. Cra. 405.c is the lines 405.c.1 to 405.c.9). Where a place
names more lines than one (a section, a chapter, a book), the cited line is the first of them
holding the most words of the quotation, else the first holding a form of the lexicon's, else the
first holding a form of the entry by the morphology (every word of the section, and of the line
after its end, through morph as the lemma check tests it: the ὑφορᾶσθαι of D. 11.4 stands at 5.1 in
Butcher's lines, its sentence run over the section's end), else the first holding
a word like the headword (the packager's akin(), which chooses a line and is never marked), else
the first; a word hyphenated across lines is tested whole; the lines before and after are the
cited line's neighbours, so a prose preview is three printed lines.

The open texts (Bruce, 31 Oct 2026: "Perseus first, TLG-E for the rest"; for prose "the sentence and
its neighbours"; every text and translation kept, the page to choose). Every citation of a Greek
work is sought, by its abo reference, in every open edition of the work on the Perseus shelf, by
perseus_places's rules, the word check run on the TLG-E preview's found form edition by edition;
each edition that holds the place and passes gives a preview, the newest first. Verse (the place is
a line, or a passage most of whose text is lines) gives three lines, before, cited, after, the cited
one chosen in a passage of more lines as a TLG-E line is (choose(), then holding()). Prose (the
place is a section, a Stephanus page's letter, a chapter) gives sentences, and the preview is the cited
sentence alone, the line before and after null (Bruce, 1 Nov 2026: a citation is a thread to just enough
context to show the word in that sense; the link carries the rest). A sentence that runs over the
section's printed end is taken whole, as it stands in the running text (the sentence holding ὑπτίας
in Pl. R. 529c begins in 529b). The cited sentence is chosen as a TLG-E line is, and the lemma check (found,
form) runs on it as on a line. A sentence ends at a full stop, a question mark (; ;) or a raised
point (· ·) followed by a space or the text's end; one run over a passage's bound is the passage's.
A line's citation (at) is the place it begins in, the cited one's the first place of the passage it
reaches, in the edition's own numbering: 23.620, 529c, 5.82.2; of Philo by Mangey's page (perseus_places,
Philo by Mangey's page) the page as LSJ cites it, 1.252, its work the treatise whose file holds it, its
link Cohn's section the cited sentence stands in. A citation a reader or the sidecar
moved (a reading repaired or relocated, the sidecar's repaired: its line is the reader's, or the
line within ten of LSJ's that holds the form, not LSJ's reference) keeps the corpus line alone; the
corpus line of Bekker's page and line, which TLG-E holds line for line and the open text marks every
fifth, is marked prefer.

The papyri (Bruce, 31 Oct 2026: "we have all the DDbDP papyri collection… you should be using everything
we have"). A bibl whose Perseus reference names a papyrus (n="Perseus:abo:pap,PSI:5:535:48"), which the
sidecar keys nowhere (no-work) and no reading places, is sought in the DDbDP store by papyri_places'
rules: its series, volume and document, and in the document the lines whose citation ends in the line
cited, on the side and in the column it names. Where it names several (the line 11 of two columns, BGU
8.11), or two documents hold it (CPR's volumes number afresh), the cited line is chosen among them as a
passage's is (choose(), then holding()); the lines before and after are its neighbours in the
document, null past its first or last. A reference with no line is its document, the cited line chosen
the same way. A reference whose line the document does not hold under that number (Edgar's 59012.33 is
the DDbDP's 59012 rp.r,2.7) keeps its preview only where the line chosen holds something of the entry:
a form the lemma check finds, a word of the quotation, or a word whose first five letters are a head's
(near(): that line's Κορακησιωτικο[ῦ, κορακήσιον's bold Κορακησιωτικὸν); its urn names the line cited,
so the page marks the place as not the citation's. Its words are read without the editor's signs (a
word restored in part is one word: unmarked()), and its lines shown with them. A papyrus line is drawn as the DDbDP's Advice to Users says its text is written
(papyri_places' drawn()): its numerals kept, the notes in braces left out.

The inscriptions (Bruce, 1 Nov 2026: "Every <bibl> in the LSJ ends with a target in a text"). A label
with no reference whose <title> is one of LSJ's corpora of inscriptions (IG 2(2).956.58, SIG 827 i 9),
or that continues such a label (1006.12, ib. 683.60), is sought in PHI's Greek Inscriptions by
inscription_places' rules: the corpus's own book, else the text PHI's own references name by it; in the
document the lines whose citation ends in the line cited, on the face and in the column it names. It is
cut as a papyrus is: several lines or documents chosen among by the quotation and the forms, a line the
document does not hold kept only where the line chosen holds something of the entry, its words read
without the editor's signs.

A translation is used for a work when its own numbering places at least nine in ten of the work's
citations, each by any of its texts' places (a translation numbered otherwise, Bostock's Pliny by
chapters, places few); its numbering is read as the Greek's: a play's lines through the strophes,
scenes and acts a translation numbered by line divides them into (passages()), Aristotle's Bekker pages
and lines by its page and line marks (Translation.find). For a citation it gives the passage holding the
cited line, found by the first of the citation's texts that places it (the open texts', whose numbering
the Perseus translations share, before the corpus's): whole where it is 200 words or fewer, else trimmed
to the sentences that carry the cited line, else to its first 200 words (cut_english()); every
translation that places a citation is kept, the newest first (Bruce, 1 Nov 2026: "just missing
translations is sad"; "just enough context for the edge, never a wall"). Standard library only (the
imported packager is too); the same inputs give byte-identical files.
"""
import argparse, bisect, collections, concurrent.futures, datetime, hashlib, html, importlib.util, json, os, re, subprocess, sys, unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))     # for the processes perseus_places starts
import perseus_places as P
import papyri_places as PA
import inscription_places as IN

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READINGS = os.path.join(REPO, 'readings', 'lsj-readings.txt')
OUT = os.path.join(REPO, 'docs', 'snippets')
SUBJECT = re.compile(r'^entry:perseus\.1999\.04\.0057/([^/]+)/(\d+)$')
BIBL = re.compile(rb'<bibl\b(?![^>]*\sresp=")')      # the dictionary's own bibls, not those a pass of LSJAI marked
BIBL_EL = re.compile(rb'<bibl\b[^>]*>(.*?)</bibl>', re.S)
BIBL_N = re.compile(rb'<bibl\b[^>]*?\sn="([^"]*)"')
LABEL = re.compile(rb'<bibl\b[^>]*\sresp="([^"]*)"[^>]*>')   # a bibl a pass of LSJAI marked, its resp
BIBL_SPAN = re.compile(rb'<bibl\b.*?</bibl>', re.S)      # an entry's citations, left out of its own text
ORTH = re.compile(rb'<orth\b[^>]*>(.*?)</orth>', re.S)
GREEK = re.compile(r'[\u0370-\u03ff\u1f00-\u1fff]')
HYPHENS = ('-', '\u2010')
MORPHS = 12                   # morph processes run side by side
NOT_A_WORK = re.compile(r'^(?:id|ib|ibid|cf|v|fr|ap|in|ad|sq|sqq|al|s\.v)\b\.?', re.I)
CUT = ('verified', 'repaired', 'line', 'read')   # the sidecar's statuses whose place has a line
TREES = ('perseus', 'first1k', 'greek', 'latin', 'loeb', 'digiliblt', 'papyri', 'inscriptions', 'english', 'translations')   # docs/snippets/<tree>/
SHELF_TREE = {'Perseus': 'perseus', 'First1K': 'first1k', 'Loeb': 'loeb', 'DigiLibLT': 'digiliblt'}   # a shelf text's tree (perseus_places.SHELVES)
OPEN_SHELVES = ('Perseus', 'First1K')              # the shelves whose texts and translations go to the repository's trees (rights 0)
TR_RATE = 0.9
TR_WORDS = 200                # a translation's passage shown whole up to this, else cut to the citation (cut_english)
TR_LEAST = 30                 # a trimmed passage's least words, where its sentences allow (cut_english)
TR_SKIP = {'note', 'head', 'reg', 'bibl', 'figure', 'del', 'gap', 'orig', 'castList', 'speaker'}
DRAMA = {'strophe', 'antistrophe', 'epode', 'ephymnion', 'mesode', 'proode', 'choral', 'episode', 'dialogue',
         'scene', 'act'}     # a play's parts, no level of a translation numbered by line (passages)
BEKKER_PAGE = re.compile(r'^\d+[ab]$')                     # 1094a: a page and column of Bekker's Aristotle
BEKKER_PLACE = re.compile(r'^(\d+[ab])(?:\.(\d+))?$')      # 1172a.5: its page and line
EN_END = re.compile(r'[.!?]["\u201d\u2019)\]]*(?=\s+["\u201c\u2018(\[]?[A-Z])')   # an English sentence's end
ITALIC = re.compile(rb'<i\b[^>]*>(.*?)</i>', re.S)
EN_STOP = frozenset('''about after again against also away back been before being came come does done down each even
ever from give given good great have having here into just kind like long length made make many more most much must only
other over part people person persons place same some such take than that their them then there these they thing this
those thus time upon used very well were what when where which while whole will with within without would'''.split())
TRANSLIT = str.maketrans({'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'e', 'θ': 'th', 'ι': 'i',
                          'κ': 'c', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's',
                          'ς': 's', 'τ': 't', 'υ': 'y', 'φ': 'ph', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o'})


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readings():
    """The readings in force by (entry id, citation number), and the number of rows: of a subject,
    the latest row by its `when`, the order of the file breaking a tie (Philology-fable's
    Docs/STORE.md, "The readings", In force)."""
    rows = []
    with open(READINGS, encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#'):
                rows.append(line.rstrip('\n').split('\t'))
    force = {}
    for k, c in enumerate(rows):
        at = datetime.datetime.strptime(c[4], '%d %b %Y %H:%M:%S %z')
        if c[0] not in force or (at, k) >= force[c[0]][:2]:
            force[c[0]] = (at, k, c)
    out = {}
    for at, k, c in force.values():
        m = SUBJECT.match(c[0])
        if m:
            out[(m.group(1), int(m.group(2)))] = c
    return out, len(rows)


def editions(masters):
    """The rows of Catalogue/editions.txt, each a dict of its columns."""
    with open(os.path.join(masters, 'Catalogue', 'editions.txt'), encoding='utf-8', newline='') as f:
        lines = f.read().split('\n')
    head = lines[0].split('\t')
    return [dict(zip(head, line.split('\t'))) for line in lines[1:] if line]


def calm(name):
    """An author as the catalogue names it, the TLG's capitals in small letters and the genre after
    them left off (HOMERUS Epic. as Homerus, Flavius JOSEPHUS Hist. as Flavius Josephus)."""
    words = name.split()
    caps = [k for k, w in enumerate(words) if re.fullmatch(r"[A-Z][A-Z'().,-]*[A-Z]\.?", w)]
    if caps:
        words = words[:caps[-1] + 1]
    return ' '.join(w if re.fullmatch(r'[IVXLC]+', w) else
                    re.sub(r'\b([A-Z])([A-Z]+)\b', lambda m: m.group(1) + m.group(2).lower(), w) for w in words)


def work_name(author, title):
    a = calm(author)
    return title if not a or title.startswith(a) else '%s, %s' % (a, title)


def printed_prefix(N, bibl, place):
    """What a bibl prints before its place: the author and work (`Pl. Cra.`), with the number of
    the work where LSJ prints one that the held text's place lacks (`D. 11` of D. 11.4, the
    speech that TLG-E holds as its own work, place 4); or ''."""
    text = re.sub(r'\s+', ' ', N.text_of(bibl)).strip()
    m = re.match(r'^((?:\d+\s+(?=[A-Z]))?[^\d]*?)[\s,]*(?=\d|$)', text)
    p = m.group(1).strip() if m else ''
    if not re.search(r'[A-Za-z]', p) or NOT_A_WORK.match(p) or len(p) > 40:
        return ''
    rest = text[m.end():].replace(' ', '')
    lead = re.match(r'^(\d+)\.(.+)$', rest)
    if lead and lead.group(2) == place and not place.startswith(lead.group(1) + '.'):
        return '%s %s' % (p, lead.group(1))
    return p


# ---------------------------------------------------------------- the English translations

def tokens(n):
    """A citation as comparable pieces: `624a` and `624.a` are ('624', 'a')."""
    out = []
    for part in n.split('.'):
        out.extend(x for x in re.findall(r'\d+|[^\d]+', part.lower()) if x)
    return tuple(out)


def number(x):
    m = re.match(r'\d+', x)
    return int(m.group()) if m else None


def local(tag):
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ''


def passages(path):
    """A TEI translation's text in pieces, in order, (key, label, text, its divs' n's, its line), with the
    file's CTS scheme, its URN (perseus_places.steps; the translation div's n) and its Bekker marks. A piece
    runs from a textpart (its n; the cards of a Perseus translation are not citations) or a line marker (a
    line milestone, an <l n>; key ends ('#L', n)) or a section milestone (624a) to the next; notes, heads and
    the places' regularised names left out. In a translation numbered by line (its CTS scheme ends in a
    line) a div of a play's parts (DRAMA: a strophe, a choral part, a scene, an act) below the scheme's own
    divs is no level, its lines keeping the play's numbers: Coleridge's Alcestis holds 244 to 250 in a
    strophe n="1", which a citation of line 244 never found (the 90% gate refused 43 such translations,
    Sophocles' seven plays among them: the measure of 1 Nov 2026). The Bekker marks, read as perseus_places reads
    them in the Greek: [(page, line, piece)], for each Bekker page (a page milestone or a div whose n is a
    page and column, 1094a) line 0 and the piece its start falls in, and for each line milestone under it
    the piece it begins (Rackham's Aristotle marks lines 1 and 20 of each column)."""
    root = ET.parse(path).getroot()
    scheme = P.steps(root)
    lined, levels = bool(scheme) and scheme[-1] == 'l', scheme.count('div')
    cards = [e.get('n') for e in root.iter() if local(e.tag) == 'cRefPattern'] == ['card']   # a Loeb translation: its cards, named by the
    body = next((e for e in root.iter() if local(e.tag) == 'body'), None)
    urn = next((e.get('n') for e in root.iter() if local(e.tag) == 'div' and e.get('type') == 'translation'
                and (e.get('n') or '').startswith('urn:cts:')), '')
    out, st = [], {'divs': [], 'line': None, 'sec': None, 'buf': [], 'at': None, 'page': None, 'pb': None, 'pb_at': None}
    marks, pages = [], []                 # pages: the page printed where each piece begins (pb n), for a link to it

    def where():
        d = list(st['divs'])
        if st['line'] is not None:
            return tokens('.'.join(d)) + ('#L', st['line']), '.'.join(d + [st['line']]), tuple(d), st['line']
        if st['sec'] is not None:
            return tokens('.'.join(d[:-1] + [st['sec']])), '.'.join(d[:-1] + [st['sec']]), tuple(d), None
        return tokens('.'.join(d)), '.'.join(d), tuple(d), None

    def flush():
        t = ' '.join(''.join(st['buf']).split())
        if t and st['at'] is not None:
            out.append((st['at'][0], st['at'][1], t, st['at'][2], st['at'][3]))
            pages.append(st['pb_at'])
        st['buf'] = []
        st['at'], st['pb_at'] = where(), st['pb']

    def walk(e):
        tag = local(e.tag)
        if tag in TR_SKIP:
            return
        kind = (e.get('subtype') or e.get('type') or '').lower()
        n = (e.get('n') or '').strip()
        div = bool(tag.startswith('div') and e.get('n') and (kind != 'card' or cards)
                   and e.get('type') not in ('translation', 'edition', 'commentary')
                   and not (lined and kind in DRAMA and len(st['divs']) >= levels))
        if tag == 'pb' and n:
            st['pb'] = n
            if not ''.join(st['buf']).strip():
                st['pb_at'] = n               # a piece that has not begun yet begins on the new page
        if div:
            flush()
            st['divs'].append(e.get('n'))
            saved = (st['line'], st['sec'])
            st['line'] = st['sec'] = None
            st['at'], st['pb_at'] = where(), st['pb']
            if BEKKER_PAGE.match(n):
                st['page'] = n
                marks.append((n, 0, len(out)))
        elif e.get('n') and ((tag == 'milestone' and e.get('unit') == 'line') or tag == 'l'):
            flush()
            st['line'] = e.get('n')
            st['at'], st['pb_at'] = where(), st['pb']
            if tag == 'milestone' and st['page'] and n.isdigit():
                marks.append((st['page'], int(n), len(out)))
        elif tag == 'milestone' and e.get('unit') == 'section' and e.get('n'):
            flush()
            st['sec'] = e.get('n')
            st['at'], st['pb_at'] = where(), st['pb']
        elif tag == 'milestone' and e.get('unit') == 'page' and BEKKER_PAGE.match(n):
            st['page'] = n                        # no new piece: the one open holds the column's start
            marks.append((n, 0, len(out)))
        if e.text:
            st['buf'].append(e.text)
        for c in e:
            walk(c)
            if c.tail:
                st['buf'].append(c.tail)
        if div:
            flush()
            st['divs'].pop()
            st['line'], st['sec'] = saved
            st['at'], st['pb_at'] = where(), st['pb']

    if body is not None:
        walk(body)
        flush()
    return out, scheme, urn, marks, pages


class Translation:
    """A translation's pieces and how a cited line of the held text finds its piece: in verse the
    piece of the same book whose line is the last at or before the cited line (at most ten before);
    in prose the piece whose citation is the cited line's less its line; either with the
    translation's first level left off when that is unique (Plato's books, which TLG-E does not
    number). A piece holding a smaller piece is never one. A Bekker page and line its own numbering does
    not hold (Rackham's Politics by book and page, his Ethics by book, chapter and section) is found by
    its Bekker marks, as perseus_places finds it in the Greek: the stretch from the last line mark at or
    before the line on its page (else from where its page begins) to the next mark, whatever sections it
    crosses (Rackham's 1107b1 to 1107b20 runs over three of his sections), a piece of its own after the
    translation's pieces, named and linked as the piece it begins with."""

    def __init__(self, path):
        self.ps, self.scheme, self.urn, marks, self.pages = passages(path)
        self.loeb = LOEB_FILE.search(os.path.basename(path))         # a Loeb volume: its number and year
        self.topos = None                                             # a ToposText file: his work number
        if '.topostext-' in os.path.basename(path):
            root = ET.parse(path).getroot()
            self.topos = next((e.text for e in root.iter() if local(e.tag) == 'idno' and e.get('type') == 'ToposText-work'), None)
        keys = [x[0] for x in self.ps]
        self.verse = sum(1 for k in keys if '#L' in k) * 2 > len(keys)
        inner = set()
        for k in keys:
            for j in range(1, len(k)):
                inner.add(k[:j])
        self.lines = collections.defaultdict(list)
        self.exact = collections.defaultdict(list)
        for i, (k, label, t, chain, line) in enumerate(self.ps):
            if self.verse:
                if '#L' not in k or number(k[-1]) is None:
                    continue
                p = k[:k.index('#L')]
                self.lines[p].append((number(k[-1]), i))
                if p:
                    self.lines[('~',) + p[1:]].append((number(k[-1]), i))
            elif k and k not in inner:                # a piece with no citation of its own (a file's unlabelled tail, "The End") is no place
                self.exact[k].append(i)
                if len(k) > 1:
                    self.exact[('~',) + k[1:]].append(i)
        self.ranges = {}                                  # pieces named by the line each begins at (ToposText's Homer
        for k, idxs in self.exact.items():                # every fifth line, the Loeb's cards): base -> [(line, piece)]
            if k and k[-1].isdigit() and len(idxs) == 1:
                self.ranges.setdefault(k[:-1], []).append((int(k[-1]), idxs[0]))
        for base, got in list(self.ranges.items()):
            got.sort()
            if len(got) < 2 or all(b - a == 1 for (a, _), (b, _) in zip(got, got[1:])):
                del self.ranges[base]                     # consecutive numbers are sections, found exactly or not at all
        self.tops = {k[0] for k in keys if k and k[0] not in ('~', '#L', '#B')}   # the top-level n's the file holds
        self.bekker = collections.defaultdict(list)       # page -> [(line, its stretch's piece)]
        starts = sorted({i for page, line, i in marks if i < len(self.ps)})
        stretch = {}
        for a, b in zip(starts, starts[1:] + [len(self.ps)]):
            k, label, t, chain, line = self.ps[a]
            stretch[a] = len(self.ps)
            self.ps.append((('#B',) + k, label, ' '.join(x[2] for x in self.ps[a:b]), chain, line))
            self.pages.append(self.pages[a])
        for page, line, i in marks:
            if i in stretch:
                self.bekker[page].append((line, stretch[i]))

    def find(self, cit, printed=True):
        """The piece of a cited line's citation, as (index, whether it is that line's own), or None; in
        prose, of a printed line less its line, of a section (printed false: a Perseus sentence) itself;
        else of a Bekker page and line (1172a.5) by the Bekker marks."""
        got = self.held(cit, printed)
        if got or not self.bekker:
            return got
        m = BEKKER_PLACE.match(cit or '')
        if m and m.group(1) in self.bekker:
            line = int(m.group(2) or 0)
            best = max(((l, i) for l, i in self.bekker[m.group(1)] if l <= line), default=None)
            if best:
                return best[1], False
        return None

    def held(self, cit, printed):
        """find() by the translation's own numbering."""
        g = tokens(cit)
        if not g:
            return None
        if self.verse:
            line = number(g[-1])
            if line is None:
                return None
            for key in (g[:-1], ('~',) + g[:-1][1:] if g[:-1] else None):
                got = self.lines.get(key) if key is not None else None
                if not got:
                    continue
                if key[:1] == ('~',) and len({self.ps[i][0][0] for _, i in got}) > 1:
                    return None
                best = max(((l, i) for l, i in got if l <= line), default=None)
                if best and line - best[0] <= 10:
                    return best[1], best[0] == line
                return None
            return None
        # The translation's first level is dropped (the '~' keys) only where it is another kind of level than the
        # citation's: Plato's books over Stephanus pages, which TLG-E does not number. Where both number books,
        # a citation keeps its book: Hdt. 4.181 is not 7.181 in the volume of books 5 to 7 (2 Nov 2026).
        wild = not (g[0].isdigit() and self.tops and all(x.isdigit() for x in self.tops))
        base = g[:-1] if printed else g
        for key in (((base, ('~',) + base) if wild else (base,)) if base else ()):   # an empty base names nothing (2 Nov 2026: h.Cer. 272 fell on the file's "The End")
            got = self.exact.get(key)
            if got and len(got) == 1:
                return got[0], False
        line = number(g[-1]) if (len(g) > 1 or () in self.ranges) else None   # a work cited by line alone, in pieces of five lines (ToposText's hymns and plays): the piece at or before the line
        if line is not None and self.ranges:               # the piece that begins at or before the cited line, in the
            got = self.ranges.get(g[:-1])                  # cited book itself: a volume holding other books places nothing
            if got:
                j = bisect.bisect_right(got, (line, len(self.ps))) - 1
                if j >= 0:
                    return got[j][1], got[j][0] == line
        key = base[:-1]                                    # the containing piece: a citation with one level more than the
        if key:                                            # translation marks (Pl. R. 327a in cards by Stephanus page,
            for kk in ((key, ('~',) + key[1:] if len(key) > 1 else None) if wild else (key,)):   # Hdt. 1.73.4 in sections), where the piece is
                got = self.exact.get(kk) if kk else None   # one; two levels dropped put Th. 1.22.4 on a flat volume's first
                if got and len(got) == 1:                  # card (Bruce, 1 Nov 2026: focused first, then wider)
                    return got[0], False
        return None

    def holds(self, cit):
        """Whether the translation holds the cited top level (a volume of books 1 and 2 holds 1.73, not 9.109)."""
        g = tokens(cit)
        return bool(g) and (not self.tops or g[0] in self.tops)   # a file with no top level (a play by line) holds all it has

    def url(self, i):
        """The piece's place in the Scaife reader: its CTS passage where the file's scheme names it, else
        the translation's start; of a Loeb volume its spread on the Loeb's site (loeb_url); of ToposText
        his work's page at the passage."""
        k, label, t, chain, line = self.ps[i]
        if self.loeb:
            return loeb_url(self.loeb.group(1), self.loeb.group(2), self.pages[i])
        if self.topos:
            return 'https://topostext.org/work/%s#%s' % (self.topos, label) if self.topos.isdigit() else None
        return scaife(self.urn, P.cts(self.scheme, chain, line))

    def label(self, i):
        """The piece's citation in the translation: its first line to its last, in verse."""
        k, label, t = self.ps[i][:3]
        if self.verse and i + 1 < len(self.ps):
            nk = self.ps[i + 1][0]
            if '#L' in nk and '#L' in k and nk[:nk.index('#L')] == k[:k.index('#L')]:
                a, b = number(k[-1]), number(nk[-1])
                if a is not None and b is not None and b - 1 > a:
                    return '%s–%d' % (label, b - 1)
        return label


def translations(masters, eds, work_cits):
    """For each work every open English translation that places at least TR_RATE of its citations (each
    a list of the places a citation has, (citation, printed) as Translation.find takes them, any of them
    placing it), the newest first: {work: [(Translation, tr_source)]}; with the tallies."""
    by = collections.defaultdict(list)
    for e in eds:
        if (e['kind'] == 'translation' and e['language'] == 'eng' and e['file'].endswith('.xml')
                and e['file'].split('/')[0] in ('Perseus', 'Loeb', 'ToposText')):   # every TEI translation we hold (1 Nov 2026); PHI-5's are text files
            by[e['work']].append(e)
    out, tally = {}, collections.Counter()
    for wid in sorted(work_cits):
        for e in sorted(by.get(wid, ()), key=lambda e: -P.year(e)):
            try:
                tr = Translation(os.path.join(masters, e['file']))
            except ET.ParseError:
                tally['translations: unreadable files'] += 1
                continue
            held = [c for c in work_cits[wid] if any(tr.holds(x[0]) for x in c if x[0])]   # a volume is judged on the books it holds;
            if not held:                      # a translation numbered otherwise at the top (Plato's books against Stephanus
                held = work_cits[wid]         # pages) on the whole work, placing through the level it drops
                tally['translations: judged on the whole work, no top level in common'] += 1
            got = sum(1 for c in held if any(tr.find(*x) for x in c))
            if got < TR_RATE * len(held):
                tally['translations: numbered otherwise'] += 1
                continue
            name = ', '.join(x for x in ('tr. ' + e['translator'] if e['translator'] else '',
                                         ' '.join(x for x in (e['place'], e['year']) if x)) if x)
            tree = 'english' if e['rights'] == '0' and e['source'] in OPEN_SHELVES else 'translations'
            out.setdefault(wid, []).append((tr, '%s (%s)' % (name, e['source']) if name else e['source'], tree))
            tally['translations: used, %s' % tree] += 1
    tally['translations: works with one or more'] = len(out)
    return out, tally


def scaife(urn, passage):
    """An open text's place in the Perseus Digital Library's Scaife reader: the edition's URN and the
    passage, else the edition's start."""
    return 'https://scaife.perseus.org/reader/%s%s/' % (urn, ':' + passage if passage else '')


LOEB_FILE = re.compile(r'\.lcl(\d{3}[A-Z]?)-(\d{4})-')     # a Loeb shelf file: tlg0012.tlg001.lcl170-1924-grc1.xml
_loeb_slugs = None


def loeb_url(num, year, page):
    """A Loeb volume's page on the Loeb Classical Library's site, by its spread: the site addresses a
    spread by its right-hand, odd page (https://www.loebclassics.com/view/homer-iliad/1924/pb_LCL170.11.xml,
    tested 1 Nov 2026 in a browser: page 10 is not found, 11 is the spread of 10 and 11), under the
    work's slug of tools/loeb_slugs.tsv (the offline library's listing of 2015, 539 volumes by number, year
    and page range; a volume of several works by the range its page falls in). None without a page or a
    slug."""
    global _loeb_slugs
    if _loeb_slugs is None:
        _loeb_slugs = collections.defaultdict(list)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loeb_slugs.tsv'), encoding='utf-8') as f:
            next(f)
            for line in f:
                lcl, yr, slug, first, last, n = line.rstrip('\n').split('\t')
                if first:
                    _loeb_slugs[(lcl, yr)].append((int(first), int(last), slug))
    if not page or not str(page).isdigit():
        return None
    p = int(page)
    rows = _loeb_slugs.get((num, year), [])
    slug = next((s for a, b, s in rows if a <= p <= b), None) or next((s for a, b, s in rows if a <= p + 1 <= b), None)
    if slug is None:
        return None
    return 'https://www.loebclassics.com/view/%s/%s/pb_LCL%s.%d.xml' % (slug, year, num, p if p % 2 else p + 1)


def name_key(w):
    """A name as the Greek and the English spell it, reduced to compare (cut_english): letters, the Greek's
    transliterated, the spellings that differ made one (ph f, th t, ch c, k c, y i, ae and ai e, oe and oi e,
    ei i, ou u, h and double letters gone): Φορμίων and Phormio are formion and formio, Πάτρας and Patrae
    patras and patre."""
    s = ''.join(c for c in unicodedata.normalize('NFD', w.lower()) if unicodedata.category(c) != 'Mn')
    for a, b in (('γγ', 'ng'), ('γκ', 'nc'), ('γχ', 'nch'), ('γξ', 'nx'), ('ου', 'u'), ('αυ', 'au'), ('ευ', 'eu'),
                 ('ηυ', 'eu')):
        s = s.replace(a, b)
    s = s.translate(TRANSLIT)
    for a, b in (('ph', 'f'), ('th', 't'), ('ch', 'c'), ('rh', 'r'), ('h', ''), ('k', 'c'), ('y', 'i'), ('ae', 'e'),
                 ('ai', 'e'), ('oe', 'e'), ('oi', 'e'), ('ei', 'i'), ('ou', 'u')):
        s = s.replace(a, b)
    return re.sub(r'(.)\1+', r'\1', re.sub(r'[^a-z]', '', s))


NUMBERS = (('τριακοσ', 'hundred 300'), ('διακοσ', 'hundred 200'), ('τετρακοσ', 'hundred 400'), ('πεντακοσ', 'hundred 500'),
           ('εξακοσ', 'hundred 600'), ('επτακοσ', 'hundred 700'), ('οκτακοσ', 'hundred 800'), ('ενακοσ', 'hundred 900'),
           ('τριακοντ', 'thirty 30'), ('τεσσαρακοντ', 'forty 40'), ('τετταρακοντ', 'forty 40'), ('πεντηκοντ', 'fifty 50'),
           ('εξηκοντ', 'sixty 60'), ('εβδομηκοντ', 'seventy 70'), ('ογδοηκοντ', 'eighty 80'), ('ενενηκοντ', 'ninety 90'),
           ('ενδεκα', 'eleven 11'), ('δωδεκα', 'twelve 12'), ('εικοσι', 'twenty 20'), ('εκατον', 'hundred 100'),
           ('χιλι', 'thousand 1000'), ('μυρι', 'thousand myriad myriads 10000'), ('δυο', 'two 2'), ('τρεισ', 'three 3'),
           ('τρια', 'three 3'), ('τριων', 'three 3'), ('τρισι', 'three 3'), ('τεσσαρ', 'four 4'), ('τετταρ', 'four 4'),
           ('πεντε', 'five 5'), ('εξ', 'six 6'), ('επτα', 'seven 7'), ('οκτω', 'eight 8'), ('εννεα', 'nine 9'),
           ('δεκα', 'ten 10'))   # a Greek number's English, the longer stems first (cues_of)
GREEK_STOP = frozenset('''και καυτοσ καγω κακεινοσ αλλα αλλ επει επειδη επειτα ωσ ωσπερ ωστε οτι οτε οποτε ετι ηδη ταυτα
ταυτησ ταυτην τουτο τουτον τουτου τουτων τουτοισ ουτοσ αυτη ουτω ουτωσ τοιαυτα τοιουτοσ τοιουτον τοσαυτα τοσουτοσ
τοσουτον μετα κατα δια περι παρα προσ υπο υπερ επι απο εκ εξ εν εισ εσ συν αντι τοτε νυν ου ουκ ουχ μη ουδε μηδε ουτε μητε
ει εαν ην αν γαρ δε τε μεν ουν ο η το οι αι τα τον την του τησ των τοισ ταισ τουσ τασ τω τη εγω εμε εμοι εμου συ σε σοι σου
ημεισ ημιν ημασ ημων υμεισ υμιν υμασ υμων αυτοσ αυτου αυτω αυτον αυτοι αυτων αυτοισ αυτουσ εκεινοσ εκεινου εκεινω εκεινον
εκεινοι εκεινων εκεινα τισ τι τινα τινεσ τινων οσ ον οστισ πασ παντα παντεσ παντων πολλα πολλοι πολλων αλλοι αλλοσ αλλων
ετεροσ ετεροι ω ινα οπωσ πωσ που ποτε μαλλον μαλιστα ουδεν ουδεισ μηδεν ανθρωποσ ανθρωποι ανθρωπων ανθρωπουσ ανθρωποισ
πραγματα πραγματων εστι εστιν εισι εισιν ησαν ειναι εχει εχειν εφη φησι φησιν λεγει λεγειν ειπε ειπεν γενεσθαι
γιγνεσθαι γινεσθαι ποιειν ποιησαι δοκει εδοξε ουκετι παλιν αει ενθα ενταυθα εκει οθεν μεχρι εωσ πριν πλην ομωσ καιτοι
μεντοι τοινυν γουν δη γε'''.split())       # the commonest Greek words, never a name or a rare word (cues_of)


def plain_greek(w):
    """A word's letters, small, no accents or breathings, final sigma as sigma."""
    return ''.join(c for c in unicodedata.normalize('NFD', w.lower()) if unicodedata.category(c) != 'Mn').replace('ς', 'σ')


def cues_of(lines, xb, b):
    """What tells the sentence of a long English passage that carries the cited line (cut_english): the
    cited lines' names (a capitalised word but the commonest, GREEK_STOP, as name_key() spells it, its first
    four letters where it has five or more: Φορμίων form, Ζεῦ zeu), numbers (their English as words and
    figures: δώδεκα twelve, 12) and rare words (one of eight letters or more, the first six as name_key()
    spells it, which a translation may keep: ἀρχιτέκτονα arcite), and the cited word's English as the entry
    gives it, the gloss the page marks (site/index.html's glossWords): the entry's last italic before the
    citation (its bibl at b), its words of four letters or more but the commonest (EN_STOP), each less its
    ending, its first five letters (pole for κοντός)."""
    names, rare, numbers = set(), set(), set()
    for t in lines:
        for w in re.findall(r'[^\W\d_]+', t or ''):
            g = plain_greek(w)
            if g in GREEK_STOP:
                continue
            k = name_key(w)
            if w[:1].isupper():
                if len(k) >= 3:
                    names.add(k[:4] if len(k) >= 5 else k)
                continue
            num = next((en for stem, en in NUMBERS if g.startswith(stem) and len(g) <= len(stem) + 4), None)
            if num:
                numbers.update(num.split())
            elif len(g) >= 8 and len(k) >= 6:
                rare.add(k[:6])
    gloss, last = set(), None
    for last in ITALIC.finditer(xb, 0, b):
        pass
    if last is not None:
        t = html.unescape(re.sub(rb'<[^>]+>', b'', last.group(1)).decode('utf-8')).lower()
        gloss = {en_stem(w)[:5] for w in re.findall(r'[a-z]{4,}', t) if w not in EN_STOP}
    return names, numbers, rare, gloss


def en_stem(w):
    """An English word less its ending (palms palm, schemes scheme, running runn)."""
    w = w.lower()
    for end, then in (('ies', 'y'), ('ing', ''), ('ed', ''), ('es', ''), ('s', '')):
        if w.endswith(end) and len(w) - len(end) >= 4:
            return w[:len(w) - len(end)] + then
    return w


def cut_english(text, cues, limit=TR_WORDS):
    """A passage over limit words trimmed to the citation, never dropped (Bruce, 1 Nov 2026: "take what we
    can get and work it all up into the best citation blurb for the user"; "just enough context for the
    edge, never a wall"): the sentence holding most of what carries the cited line (cues_of(): a name
    counts 2, a number 1.5, the cited word's gloss 1, a rare word 0.5, each shared by the sentences holding
    it), with the sentences beside it that hold one too while the whole stays within the limit, and the
    sentences after it (else before) while it is under TR_LEAST words, a sentence longer than the limit its
    limit words from a little before the first such word: (text, 'sentences'). Where no sentence tells (none
    scores three quarters, or the best are apart: a name every sentence holds), the passage's first limit
    words: (text, True). The text is marked … where trimmed."""
    names, numbers, rare, gloss = cues
    sents, at = [], 0
    for m in EN_END.finditer(text):
        sents.append(text[at:m.end()].strip())
        at = m.end()
    sents = [x for x in sents + [text[at:].strip()] if x]

    def held(tok):
        got = set()
        for w in re.findall(r'[A-Za-z]+|\d[\d,]*', tok):
            if w[0].isdigit():
                if w.replace(',', '') in numbers:
                    got.add(('d', w.replace(',', '')))
                continue
            lw = w.lower()
            if lw in numbers:
                got.add(('d', lw))
            stem = en_stem(w)
            got.update(('g', x) for x in gloss if stem.startswith(x))
            k = name_key(w)
            if w[0].isupper():
                got.update(('n', x) for x in names if k.startswith(x))
            if len(k) >= 5:
                got.update(('r', x) for x in rare if k.startswith(x))
        return got

    toks = [x.split() for x in sents]
    hits = [[held(t) for t in ts] for ts in toks]
    seen = collections.Counter(a for h in hits for a in set().union(*h))
    weight = {'n': 2.0, 'd': 1.5, 'g': 1.0, 'r': 0.5}
    score = [sum(weight[a[0]] / seen[a] for a in set().union(*h)) for h in hits]
    top = max(score, default=0)
    tops = [j for j, x in enumerate(score) if x == top]
    if top < 0.75 or tops[-1] - tops[0] + 1 != len(tops):
        return ' '.join(text.split()[:limit]) + ' …', True
    best, lo, hi = tops[0], tops[0], tops[-1]
    total = sum(len(toks[j]) for j in tops)
    grew = True
    while grew:
        grew = False
        if lo > 0 and score[lo - 1] and total + len(toks[lo - 1]) <= limit:
            lo -= 1
            total += len(toks[lo])
            grew = True
        if hi + 1 < len(sents) and score[hi + 1] and total + len(toks[hi + 1]) <= limit:
            hi += 1
            total += len(toks[hi])
            grew = True
    while total < TR_LEAST and (hi + 1 < len(sents) or lo > 0):     # never a bare scrap: "He has two lieutenants."
        k = hi + 1 if hi + 1 < len(sents) else lo - 1
        if total + len(toks[k]) > limit:
            break
        lo, hi, total = min(lo, k), max(hi, k), total + len(toks[k])
    if total > limit:
        ts = toks[best]
        j = next(k for k, h in enumerate(hits[best]) if h)
        a = max(0, min(j - limit // 4, len(ts) - limit))
        body, pre, post = ' '.join(ts[a:a + limit]), a > 0 or best > 0, a + limit < len(ts) or best + 1 < len(sents)
    else:
        body, pre, post = ' '.join(sents[lo:hi + 1]), lo > 0, hi + 1 < len(sents)
    return ('… ' if pre else '') + body + (' …' if post else ''), 'sentences'


def tlg_url(wid, offset):
    """A work of the Greek corpus in the TLG's online browser, which opens for its subscribers: at the
    work's start; the line's place (offset, its line counted from the work's first in the TLG-E order)
    has no address there we have confirmed, and goes in here when one is."""
    return 'https://stephanus.tlg.uci.edu/Iris/indiv/browser.jsp#doc=tlg&aid=%s&wid=%s&st=0&l=20' % (
        wid[3:7], wid.split('.')[1][3:])


def latin_url(wid):
    """A work of the Latin corpus in the PHI Latin Texts online, at the work's start, as the TLG link opens
    at the work (second review 8: the site's book numbers are not the page's); a line has no address there."""
    return 'https://latin.packhum.org/loc/%d/%d/0' % (int(wid[3:7]), int(re.sub(r'\D', '', wid.split('.')[1]) or 0))


# ---------------------------------------------------------------- the cut

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--philology', required=True, help='Philology-fable')
    ap.add_argument('--masters', required=True, help='Philology-masters')
    ap.add_argument('--tlg', required=True, help='the TLG-E store')
    ap.add_argument('--latin', required=True, help='the PHI-5 Latin store')
    ap.add_argument('--papyri', required=True, help="the DDbDP store (PHI 7's DDP files)")
    ap.add_argument('--inscriptions', required=True, help="the Greek Inscriptions store (PHI's INS files)")
    ap.add_argument('--morph', required=True, help='the morph binary (GIT-REPOS/morph/bin/morph)')
    ap.add_argument('--perseus', required=True, help="Philology-masters' Perseus shelf (Philology-masters/Perseus)")
    ap.add_argument('--jobs', type=int, default=6, help='processes reading the Perseus shelf')
    ap.add_argument('--limit', type=int, default=0, help='a test cut: only the first N entries in the dictionary\'s order')
    ap.add_argument('--out', help='where the trees are written (default docs/snippets); a test cut must name another folder')
    args = ap.parse_args()
    out_dir = args.out or OUT
    if args.limit and not args.out:
        sys.exit('a test cut (--limit) must write elsewhere (--out)')

    N = load(os.path.join(args.philology, 'Port', 'tools', 'citations', 'n1_package.py'), 'n1_package')
    B = load(os.path.join(REPO, 'site', 'build.py'), 'build')
    stores = {'tlg': N.Store(args.tlg), 'latin': N.Store(args.latin), 'papyri': N.Store(args.papyri),
              'inscriptions': N.Store(args.inscriptions)}
    papyrus, stone = stores['papyri'], stores['inscriptions']
    lexicon = N.Dictionary(os.path.join(args.philology, 'Lexicon'), *N.DICTS[0])
    id_of = {row: key.split(':', 1)[1] for key, row in lexicon.row_of_id.items()}
    eds = editions(args.masters)
    pap = PA.Papyri(stores['papyri'], N, eds)
    ins = IN.Inscriptions(stone, N, eds)
    tally = collections.Counter()

    mine = B.dictionary(B.read_ours)
    xml = {i: x.encode('utf-8') for i, x in mine}
    position = {i: pos for pos, (nm, order, shown, i) in enumerate(B.ordered(mine))}
    if args.limit:                                   # a test cut: the first entries in order
        keep = {i for i, pos in sorted(position.items(), key=lambda t: t[1])[:args.limit]}
        xml = {i: x for i, x in xml.items() if i in keep}
    block = {i: pos // B.BLOCK for i, pos in position.items()}
    force, read = readings()
    tally['readings: rows'] = read
    tally['readings: citations with a reading in force'] = len(force)

    # Every bibl: its place (the reading's line, else the sidecar's), status, quotation and work.
    per_entry = collections.Counter(r[0] for r in lexicon.rows)
    todo, prefixes, seen = [], collections.defaultdict(collections.Counter), set()
    cits = []                   # every bibl of a tlg work, its place to be sought on the Perseus shelf
    papyri = []                 # every bibl of a papyrus with no place, to be sought in the DDbDP store
    stones = []                 # every label of an inscription, to be sought in the Greek Inscriptions store
    for e, n, b, length, key, status, how in lexicon.rows:
        oid = id_of.get(e)
        tally['citations in the dictionary'] += 1
        if oid not in xml:
            tally['no snippet: entry not in this copy'] += 1
            continue
        xb = xml[oid]
        at = [m.start() for m in BIBL.finditer(xb)]
        if len(at) != per_entry[e]:
            tally["no snippet: the entry's bibls are not the sidecar's"] += 1
            continue
        seen.add((oid, n))
        r = force.get((oid, n))
        kind = r[1] if r else None
        tag = BIBL_N.match(xb, at[n - 1])
        ref = P.abo(html.unescape(tag.group(1).decode('utf-8'))) if tag else None
        if ref:                     # the work the sidecar names, else the abo work; the sidecar's place
            sw, sp = N.split_key(key) if key.startswith('urn:') else key.partition(':')[::2]
            cits.append({'oid': oid, 'n': n, 'xb': xb, 'b': at[n - 1], 'reading': kind, 'status': status, 'wk': ref[0],
                         'cwork': sw if sw.startswith('tlg') else ref[1], 'parts': ref[2],
                         'side': P.locus_parts(sp.replace('.', ':')), 'fw': None})
        urn = r[2] if r and r[2] else (key if status in CUT else '')
        pn = html.unescape(tag.group(1).decode('utf-8')) if tag else ''
        if not urn and pn.startswith('Perseus:abo:pap,'):
            el = BIBL_EL.match(xb, at[n - 1])
            papyri.append([oid, n, xb, at[n - 1], kind, pn, re.sub(r'\s+', ' ', N.text_of(el.group(1))).strip() if el else ''])
            continue
        if not urn:
            tally['no snippet: no place (%s)' % (kind or status)] += 1
            continue
        wid, place = N.split_key(urn)
        store = N.store_of(stores, urn)
        if wid not in store.works:
            tally['no snippet: work not in TLG-E or PHI-5'] += 1
            continue
        el = BIBL_EL.match(xb, at[n - 1])
        p = printed_prefix(N, el.group(1), place) if el and kind != 'relocated' else ''
        if p:                       # a relocated citation prints another work than its line's
            prefixes[wid][p] += 1
        todo.append([oid, n, xb, at[n - 1], kind, urn, wid, place, store, None])
    # The bibls a pass of LSJAI marked (resp, tools/mark_citations.py), numbered after the entry's own, resp
    # by resp and each in its order, as site/build.py's cite_order() numbers them (Bruce, 1 Nov 2026: every
    # <bibl> ends with a target). The sidecar does not know them: one with an n is sought by that reference
    # alone, the abo work in CTS form and the locus as the store's levels; a papyrus goes to the DDbDP.
    for oid, xb in xml.items():
        own = sum(1 for _ in BIBL.finditer(xb))
        labels = sorted(((m.group(1), m.start()) for m in LABEL.finditer(xb)), key=lambda t: (t[0], t[1]))
        if labels and lexicon.row_of_id.get('lsj:' + oid) is None:
            tally['no snippet: labels of an entry the lexicon has no row for'] += len(labels)   # entry() needs its row
            continue
        named = ins.labels(xb, [(m.start(), m.group(0)) for m in BIBL_SPAN.finditer(xb)]) if labels else {}
        for n, (resp, b) in enumerate(labels, own + 1):
            tally['labels'] += 1
            seen.add((oid, n))
            tag = BIBL_N.match(xb, b)
            pn = html.unescape(tag.group(1).decode('utf-8')) if tag else ''
            if not pn and b in named:   # an inscription: its corpus and printed numbers (inscription_places)
                r = force.get((oid, n))
                stones.append([oid, n, xb, b, r[1] if r else None, named[b]])
                continue
            if not pn:
                tally['no snippet: a label with no n'] += 1
                continue
            r = force.get((oid, n))
            kind = r[1] if r else None
            if pn.startswith('Perseus:abo:pap,'):
                el = BIBL_EL.match(xb, b)
                papyri.append([oid, n, xb, b, kind, pn, re.sub(r'\s+', ' ', N.text_of(el.group(1))).strip() if el else ''])
                continue
            ref = P.abo(pn)
            urn = r[2] if r and r[2] else ('urn:cts:greekLit:%s:%s' % (ref[1], '.'.join(ref[2])) if ref and ref[1] and ref[2] else '')
            if not urn:
                tally['no snippet: a label whose n names no tlg work and place'] += 1
                continue
            wid, place = N.split_key(urn)
            store = N.store_of(stores, urn)
            if wid not in store.works:
                tally['no snippet: a label of a work not in TLG-E or PHI-5'] += 1
                continue
            tally['labels: sought in the stores'] += 1
            cits.append({'oid': oid, 'n': n, 'xb': xb, 'b': b, 'reading': kind, 'status': 'label', 'wk': ref[0],
                         'cwork': wid, 'parts': ref[2], 'side': P.locus_parts(place.replace('.', ':')), 'fw': None})
            todo.append([oid, n, xb, b, kind, urn, wid, place, store, None])   # a label does not vote on the work's printed abbreviation: the dictionary's own bibls define it
    tally['readings in force naming no bibl of this copy'] = len(set(force) - seen)

    # The lines each place names, work by work: a store keeps the citations of the last work asked.
    for item in sorted(todo, key=lambda t: (t[8] is stores['latin'], t[6])):
        item[9] = item[8].passage(item[6], item[7])[0]
    abbrev = {wid: sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0] for wid, c in prefixes.items()}

    drawn, out, quoted, ctx = {}, collections.defaultdict(list), {}, []

    def text(store, wid, L):
        """Line L of a store as (citation, Unicode), kept while the cache is small."""
        if len(drawn) > 400000:
            drawn.clear()
        k = (id(store), L)
        if k not in drawn:
            drawn[k] = pap.drawn(N, wid, L) if store is stores['papyri'] else store.drawn(wid, L)
        return drawn[k]

    def said(store, wid, L):
        """Line L's text as its words are read: a papyrus's with the editor's signs off, so that a word
        restored or written out in part is one word (Κορακησιωτικο[ῦ is Κορακησιωτικοῦ)."""
        t = text(store, wid, L)[1]
        return PA.unmarked(t) if store is papyrus or store is stone else t

    def joined(store, wid, first, last, L):
        """Line L's words as they are tested, each (word, its piece on the line): a word hyphenated
        across two printed lines is tested whole on both (ἀγρά-|φοις is ἀγράφοις)."""
        t = said(store, wid, L)
        ws = [(w, w) for w in N.words_of(t)]
        if ws and L > first:
            before = said(store, wid, L - 1).rstrip()
            if before.endswith(HYPHENS) and N.words_of(before):
                ws[0] = (N.words_of(before)[-1] + ws[0][0], ws[0][1])
        if ws and L < last and t.rstrip().endswith(HYPHENS):
            after = N.words_of(said(store, wid, L + 1))
            if after:
                ws[-1] = (ws[-1][0] + after[0], ws[-1][1])
        return ws

    cache, own_words = {}, {}

    def entry(oid, xb):
        """The entry's terms (forms of its lemmas, forms it names, its headword: package()), its
        headword's letters, the lexicon's forms of its lemmas, its heads (the headword and the bold
        forms of the entry like it: ἀκοίτης lists ἄκοιτις) and whether the lexicon gives it a lemma."""
        if cache.get('oid') != oid:
            row = lexicon.row_of_id.get('lsj:' + oid)
            h, l, k = lexicon.entries[row - 1]
            head, own = l.encode('utf-8'), lexicon.form_letters(row)
            terms, forms, heads = {}, {}, {head}
            for L, f in own + lexicon.named(row) + [(head, h)]:
                if len(L) >= 3:
                    terms.setdefault(L, set()).add(N.plain(f))
            for L, f in own + [(head, h)]:
                if len(L) >= 3:
                    forms.setdefault(L, set()).add(N.plain(f))
            for m in ORTH.finditer(xb):
                for w in N.words_of(N.text_of(m.group(1))):
                    L = N.letters_of(w)
                    if len(L) >= 3 and N.akin(L, head):
                        heads.add(L)
            cache.update(oid=oid, v=(terms, head, forms, heads, bool(own)))
            if oid not in own_words:
                ws = {unicodedata.normalize('NFC', w).casefold() for w in N.words_of(N.text_of(BIBL_SPAN.sub(b' ', xb)))
                      if GREEK.search(w)}
                like = {w for w in ws if len(N.letters_of(w)) >= 5 and N.akin(N.letters_of(w), head)}
                own_words[oid] = (like, ws, {N.letters_of(w) for w in like})
        return cache['v']

    def quotation(xb, b):
        q = N.quotation(xb, b)
        quote = {}
        if q[0] in ('quote', 'foreign') and q[2] > q[1]:
            for w in N.words_of(N.text_of(xb[q[1]:q[2]])):
                L = N.letters_of(w)
                if len(L) >= 3:
                    quote.setdefault(L, set()).add(N.plain(w))
        return quote

    def matched(ws, quote, terms, head):
        """The pieces of a line whose words are a quotation word or a form: ([pieces], quote count,
        form?, and whether a word looks like the headword (n1_package.akin))."""
        words, qs, fs, ak = [], set(), False, False
        for w, piece in ws:
            L = N.letters_of(w)
            ak = ak or N.akin(L, head)
            p = N.plain(w) if L[:1].isupper() else None
            inq = L in quote and (p is None or p in quote[L])
            inf = L in terms and (p is None or p in terms[L])
            if inq or inf:
                if piece not in words:
                    words.append(piece)
                if inq:
                    qs.add(L)
                fs = fs or inf
        return words, len(qs), fs, ak

    def choose(units, quote, terms, head):
        """Of a passage's units (lines; on the Perseus shelf lines or sentences), each its words as
        joined() gives them, the one cited: the first holding the most words of the quotation, else the
        first holding a form of the lexicon's, else the first holding a word like the headword, else the
        first; as (its index, the words of it that chose it, whether neither the quotation nor the
        lexicon's forms chose it, so that the morphology is to choose: holding())."""
        best = None
        for k, ws in enumerate(units):
            words_k, qn, fs, ak = matched(ws, quote, terms, head)
            if best is None or (qn, fs, ak) > best[0]:
                best = ((qn, fs, ak), k, words_k)
        return best[1], best[2], not best[0][0] and not best[0][1]

    def cut(s, store, wid, first, last, cited, words):
        three = [text(store, wid, L) if first <= L <= last else (None, None) for L in (cited - 1, cited, cited + 1)]
        s['at'], s['lines'] = [c for c, t in three], [t for c, t in three]
        s.pop('form', None)
        if words:
            s['form'] = ' '.join(words)

    # The papyri: each reference's document and lines in the DDbDP store (papyri_places); of two documents
    # that hold the line cited, the one whose line holds more of the quotation, a form, a word like the
    # headword (matched(), as choose() weighs a line). Each goes into the first pass as a passage of its
    # document's lines, its bounds the document's, its work in the ref as LSJ prints it (the volume's
    # commonest where the bibl prints none), the store's book where a pointer or an earlier edition led
    # to another edition's lines (W.Chr. 273 for POxy. 36).
    pinfo, pprefixes = {}, collections.defaultdict(collections.Counter)
    for oid, n, xb, b, kind, pn, printed in papyri:
        tally['papyri: citations'] += 1
        terms, head, forms, heads, own = entry(oid, xb)
        quote = quotation(xb, b)

        def score(t, ls):
            return max(matched(joined(papyrus, t['wid'], t['first'], t['last'], L), quote, terms, head)[1:] for L in ls)
        g = pap.resolve(pn, printed, score)
        if g['status'] not in ('line', 'lines', 'marks', 'document', 'all'):
            tally['papyri: no preview: %s' % g['status']] += 1
            continue
        tally['papyri: resolved: %s' % g['status']] += 1
        for h in g['how']:
            tally['papyri: resolved by: %s' % h] += 1
        if g.get('others'):
            tally['papyri: the line cited in two or more documents, chosen by the quotation and the forms'] += 1
        wid = g['wid']
        pinfo[(oid, n)] = g
        el = BIBL_EL.match(xb, b)
        p = printed_prefix(N, el.group(1), g['place']) if el else ''
        moved = 'pointer' in g['how'] or 'earlier' in g['how']      # the lines another edition's
        g['work'] = ' '.join(x for x in pap.book_of[wid] if x) if moved else p
        if p and not moved:
            pprefixes[wid][p] += 1
        todo.append([oid, n, xb, b, kind, 'urn:cts:ddp:%s:%s' % (wid, g['place']), wid, g['place'], papyrus, g['lines']])
    pabbrev = {wid: sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0] for wid, c in pprefixes.items()}

    # The inscriptions: each label's document and lines in the Greek Inscriptions store (inscription_places),
    # chosen as a papyrus's are; its work in the ref the book as PHI names it (IG II², not LSJ's IG 2(2)).
    for oid, n, xb, b, kind, (corpus, rest) in stones:
        by = 'inscriptions by corpus: %s: ' % corpus
        tally['inscriptions: citations'] += 1
        tally[by + 'labels'] += 1
        terms, head, forms, heads, own = entry(oid, xb)
        quote = quotation(xb, b)

        def score(t, ls):
            return max(matched(joined(stone, t['wid'], t['first'], t['last'], L), quote, terms, head)[1:] for L in ls)
        g = ins.resolve(corpus, rest, score)
        if g['status'] not in ('line', 'lines', 'marks', 'document', 'all'):
            tally['inscriptions: no preview: %s' % g['status']] += 1
            continue
        tally['inscriptions: resolved: %s' % g['status']] += 1
        tally[by + 'documents reached'] += 1
        if g['status'] != 'all':
            tally[by + 'line cited'] += 1
        if g['status'] in ins.FOUND:
            tally[by + 'line cited, found'] += 1
        for h in g['how']:
            tally['inscriptions: resolved by: %s' % h] += 1
        if g.get('others'):
            tally['inscriptions: the line cited in two or more documents, chosen by the quotation and the forms'] += 1
        g['work'] = g['text']['book']
        pinfo[(oid, n)] = g
        todo.append([oid, n, xb, b, kind, 'urn:cts:ins:%s:%s' % (g['wid'], g['place']), g['wid'], g['place'], stone, g['lines']])
    shelves = {id(papyrus): ('papyri', 'ddp', pap), id(stone): ('inscriptions', 'ins', ins)}   # the trees cut by document

    # First pass: each citation's line, chosen by the quotation's words and the lexicon's forms.
    for oid, n, xb, b, kind, urn, wid, place, store, lines in todo:
        if not lines:
            tally['no snippet: line not found (%s)' % (kind or 'unread')] += 1
            continue
        first, last, author, title, _ = store.works[wid]
        g = pinfo.get((oid, n)) if id(store) in shelves else None
        tree, ns, _ = shelves.get(id(store), ('', '', None))
        if g:
            first, last = g['text']['first'], g['text']['last']
        terms, head, forms, heads, own = entry(oid, xb)
        quote = quotation(xb, b)
        fallback = None
        if len(lines) == 1:
            cited = lines[0]
            words = matched(joined(store, wid, first, last, cited), quote, terms, head)[0]
        else:
            k, words, more = choose([joined(store, wid, first, last, L) for L in lines], quote, terms, head)
            cited = lines[k]
            tally[tree + ': cited line chosen among more lines' if g else 'cited line chosen in a passage of more lines'] += 1
            if more:
                # nothing of the quotation or the lexicon's forms: the morphology next, over the
                # passage and the line after it (a sentence runs over a section's printed end: the
                # ὑφορᾶσθαι of D. 11.4 stands at 5.1 in Butcher); a papyrus's lines alone
                fallback = (lines, lines[-1] + 1 if lines[-1] < last and not g else None)
        s = {'n': n, 'status': 'read' if kind else 'unread', 'cite': hashlib.sha1(BIBL_EL.match(xb, b).group(0)).hexdigest()[:8]}   # the bibl it is cut from (build.py's stamp())
        if kind:
            s['kind'] = kind
        if g:
            work = g['work'] or pabbrev.get(wid) or g['abbr']
            if g['status'] in ('line', 'lines'):
                place = store.raw(cited)[0]
                urn = 'urn:cts:%s:%s:%s' % (ns, wid, place)
        else:
            work = abbrev.get(wid) or work_name(author, title)
        s.update(urn=urn, ref='%s%s%s' % (work, '.' if work[-1:].isdigit() and store is not stone else ' ', place), source=wid)   # IG II² 956.58, as PHI writes it
        cut(s, store, wid, first, last, cited, words)
        out[oid].append(s)
        ctx.append([s, oid, xb, b, store, wid, first, last, cited, fallback])
        tally[tree + ': snippets' if g else 'snippets: %s' % (kind or 'unread')] += 1

    # The morphology: every word of every cited line, and of every line of a passage the first pass
    # chose by a word like the headword or by its first line, through morph to its lemmas.
    want = set()
    for s, oid, xb, b, store, wid, first, last, cited, fallback in ctx:
        for L in (fallback[0] + [fallback[1]] if fallback and fallback[1] else fallback[0] if fallback else [cited]):
            want.update(w for w, piece in joined(store, wid, first, last, L) if GREEK.search(w))
    lemmas, asked = collections.defaultdict(set), set()

    died = []

    def morph(flags):
        """morph over a chunk of words, its output; where morph dies by a signal (a bus error in its stemmer
        ended a cut on 1 Nov 2026), the chunk again in halves, and a word it dies on alone left unanalysed and
        counted; any other failure stops the cut."""
        def run(chunk):
            p = subprocess.run([args.morph, flags, '-q'], input=('\n'.join(chunk) + '\n').encode('utf-8'), capture_output=True)
            if p.returncode > 0:
                raise subprocess.CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)
            if p.returncode == 0:
                return p.stdout.decode('utf-8')
            if len(chunk) == 1:
                died.append(chunk[0])
                return ''
            h = len(chunk) // 2
            return run(chunk[:h]) + '\n' + run(chunk[h:])
        return run

    def analyse(want):
        """Every word not asked before through morph, MORPHS processes side by side, its lemmas into
        lemmas; the number asked. Case ignored (-S: a word a sentence begins, Ταπεινώθητε), and for a word
        with no analysis so, accents too (-Sn: an elided κατ, an unaccented χθωροδλαψου); a word with one
        is not asked again without its accents, which would give it another word's (γραφὴ as γράφω). An
        answer is kept only under a word asked: without its accents morph may name the word it read as
        another (an inscription's ἐ͂ι as εἰ, with εἰμί and εἶμι), whose own analyses it would otherwise join;
        the word is matched to its answer by NFC, since morph writes most answers in another normalization."""
        words = sorted(set(want) - asked)
        asked.update(words)
        for flags in ('-JUS', '-JUSn'):
            todo = [w for w in words if w not in lemmas] if flags == '-JUSn' else words
            sent = collections.defaultdict(list)       # the words asked, by their NFC form: morph answers in another
            for w in todo:                             # normalization for most (2,304 of 3,573 in a sample, 1 Nov 2026)
                sent[unicodedata.normalize('NFC', w)].append(w)
            with concurrent.futures.ThreadPoolExecutor(MORPHS) as pool:
                for got in pool.map(morph(flags), [todo[k::MORPHS] for k in range(MORPHS)]):
                    for line in got.split('\n'):
                        if line.startswith('{'):
                            d = json.loads(line)
                            for w in sent.get(unicodedata.normalize('NFC', d['form']), ()):   # under the word asked, as the text spells it
                                for a in d.get('analyses', ()):
                                    lemmas[w].add(unicodedata.normalize('NFC', re.sub(r'\d+$', '', a.get('lemma', ''))))
        return len(words)

    tally['lemma check: words sent to morph'] = analyse(want)
    tally['lemma check: words morph analysed'] = len(lemmas)
    ties = collections.defaultdict(set)
    for row, rs in lexicon.entry_lemmas.items():
        for r in rs:
            ties[unicodedata.normalize('NFC', lexicon.lemmas[r - 1][1])].add(id_of.get(row))

    def hit(w, oid, forms, heads):
        """Whether a word is a form of the entry: a form of its lemmas in the lexicon, one of its heads,
        or a word morph analyses to a lemma the lexicon ties to the entry or one spelling a head."""
        L = N.letters_of(w)
        if L in heads or (L in forms and (not L[:1].isupper() or N.plain(w) in forms[L])):
            return True
        return any(oid in ties.get(l, ()) or N.letters_of(l) in heads for l in lemmas.get(w, ()))

    def near(ws, quote, heads):
        """Whether a line chosen without the line cited holds a word of the quotation, or a word whose
        first five letters are a head's (the headword's, or a bold form's like it: the Κορακησιωτικοῦ of
        P.Cair.Zen. 59012, κορακήσιον's Κορακησιωτικὸν)."""
        for w, piece in ws:
            L = N.letters_of(w)
            if L in quote or any(len(L) >= 5 and len(h) >= 5 and L[:5] == h[:5] for h in heads):
                return True
        return False

    def named(w, oid, every=False):
        """Whether a word's morph lemma is a word of the entry's own text, outside its citations (Bruce, 1 Nov
        2026), accents exact, case folded: of those words, the ones of five letters or more like its headword
        (akin(): Κοντοπορία of Κοντοπορεία; a shorter one is a preposition or a particle, ἐπί of ἐπιφώνημα,
        πρός of προσβάλλω, which akin() alone let through); every one with every (counted, not applied: an
        entry's ὁ, καί or ἐν would pass)."""
        akin, every_word, _ = own_words.get(oid, (set(), set(), set()))
        within = every_word if every else akin
        return any(l.casefold() in within for l in lemmas.get(w, ()))

    def ending(w, oid):
        """Counted, not applied: a word morph does not analyse whose letters less its last are a word's the
        entry names like its headword (Κοντοπορίαν, Κοντοπορίας and the entry's Κοντοπορία)."""
        L = N.letters_of(w)
        return w not in lemmas and len(L) >= 6 and L[:-1] in own_words.get(oid, (set(), set(), set()))[2]

    def holding(units, oid, forms, heads):
        """The index of the first unit holding a form of the entry (hit()), or None."""
        return next((k for k, ws in enumerate(units) if any(hit(w, oid, forms, heads) for w, piece in ws)), None)

    def check(s, ws, oid, forms, heads, own, tree):
        """The lemma check of a cited unit's words: found and the form marked, found null, or neither."""
        found = next(((w, piece) for w, piece in ws if hit(w, oid, forms, heads)), None)
        if not found:
            found = next(((w, piece) for w, piece in ws if named(w, oid)), None)
            if found:
                tally['lemma check: found by a word the entry names like its headword (1 Nov 2026): %s' % tree] += 1
            if any(named(w, oid, True) for w, piece in ws):
                tally['lemma check: a word whose lemma is any word of the entry (not applied): %s' % tree] += 1
            if not found and any(ending(w, oid) for w, piece in ws):
                tally['lemma check: a word morph does not analyse, a named word and one letter (not applied): %s' % tree] += 1
        if found:
            s['found'] = found[0]
            s['form'] = found[1]          # the headword's own form alone is marked (hyphenated: its piece here)
            if found[1] != found[0]:
                tally['lemma check: found across a line break'] += 1
        elif own or any(w in lemmas for w, piece in ws):
            s['found'] = None

    # Second pass: a passage the first pass chose by a word like the headword or its first line takes
    # its first line holding a form of the headword by the morphology; then the lemma check, every word
    # of the cited line tested whole.
    shelf_of = {id(stores['tlg']): 'tlg', id(stores['latin']): 'latin', id(papyrus): 'papyri', id(stone): 'inscriptions'}
    dropped = set()
    for c in ctx:
        s, oid, xb, b, store, wid, first, last, cited, fallback = c
        g = pinfo.get((oid, s['n'])) if id(store) in shelves else None
        tree, ns, _ = shelves.get(id(store), ('', '', None))
        pre = tree + ': ' if g else ''
        terms, head, forms, heads, own = entry(oid, xb)
        if fallback:
            ls = fallback[0] + ([fallback[1]] if fallback[1] else [])
            k = holding((joined(store, wid, first, last, L) for L in ls), oid, forms, heads)
            if k is None:
                tally[pre + 'cited line in a passage: the morphology found nothing, kept'] += 1
            elif ls[k] != cited:
                L = ls[k]
                tally[pre + 'cited line moved in a passage by the morphology'] += 1
                if L == fallback[1]:
                    tally['cited line moved past the passage by one line'] += 1
                cited = c[8] = L
                cut(s, store, wid, first, last, cited,
                    matched(joined(store, wid, first, last, cited), quotation(xb, b), terms, head)[0])
                if g and g['status'] in ('line', 'lines'):      # the place a papyrus's line moved to is its own
                    work = g['work'] or pabbrev.get(wid) or g['abbr']
                    s['urn'] = 'urn:cts:%s:%s:%s' % (ns, wid, store.raw(cited)[0])
                    s['ref'] = '%s%s%s' % (work, '.' if work[-1:].isdigit() and store is not stone else ' ', store.raw(cited)[0])
        check(s, joined(store, wid, first, last, cited), oid, forms, heads, own,
              tree if g else 'latin' if store is stores['latin'] else 'greek')
        if g and g['status'] in ('document', 'marks') and not s.get('found') and not near(
                joined(store, wid, first, last, cited), quotation(xb, b), heads):
            dropped.add(id(s))      # the line cited not in the document, and nothing of the entry on the line chosen
            tally[tree + ': no preview: the line cited not in the document, nothing of the entry on a line of it'] += 1
            continue
        quoted[id(s)] = [(shelf_of[id(store)], L) for L in (cited - 1, cited, cited + 1) if first <= L <= last]
        if s.get('form'):
            tally[pre + 'snippets with a form'] += 1
        got = 'unresolved' if 'found' not in s else 'found' if s['found'] else 'not found'
        tally['lemma check: %s' % got, ('%s, %s' % (tree, g['status'])) if g else s.get('kind') or 'unread'] += 1
    for oid in [i for i, v in out.items() if any(id(s) in dropped for s in v)]:
        out[oid] = [s for s in out[oid] if id(s) not in dropped]
        if not out[oid]:
            del out[oid]

    # the source of each work: its shelf and edition, as the catalogue names them
    shelf = {}
    for e in eds:
        top, _, name = e['file'].partition('/')
        if top in ('TLG-E', 'PHI-5'):
            shelf.setdefault((e['work'], name), e)
    files = {}
    for path in (args.tlg, args.latin):
        for w in N.CV.works(path):
            files.setdefault(w[N.CV.ID], w[N.CV.SOURCE])
    sources = {}
    for items in out.values():
        for s in items:
            wid = s['source']
            if wid in sources:
                continue
            if wid in pap.book_of:
                sources[wid] = pap.source(wid)
                continue
            if wid in ins.book_of:
                sources[wid] = ins.source(wid)
                continue
            store = stores['tlg'] if wid.startswith('tlg') else stores['latin']
            author, title = store.works[wid][2:4]
            e = shelf.get((wid, files.get(wid)))
            if e:
                ed = 'ed. %s' % e['editors'] if e['editors'] else ''
                imprint = ' '.join(x for x in (e['place'], e['year']) if x)
                sources[wid] = ', '.join(x for x in (work_name(author, title), ed, imprint) if x)
            else:
                tally['works with no edition row'] += 1
                sources[wid] = work_name(author, title)

    # the corpus previews: their sources and their addresses online
    where, wid_of = {id(c[0]): c for c in ctx}, {}

    trees = {t: collections.defaultdict(list) for t in TREES}
    for oid, items in out.items():
        for s in items:
            wid = wid_of[id(s)] = s['source']
            s['source'] = sources[wid]
            c = where[id(s)]
            store, first, last, cited = c[4], c[6], c[7], c[8]
            if id(store) in shelves:
                tree, ns, src = shelves[id(store)]
                u = src.url(pinfo[(oid, s['n'])]['text'])
                if u:
                    s['url'] = u
                trees[tree][oid].append(s)
                if store is stone:
                    tally['inscriptions by corpus: %s: previews' % pinfo[(oid, s['n'])]['corpus']] += 1
                continue
            latin = store is stores['latin']
            s['url'] = latin_url(wid) if latin else tlg_url(wid, cited - first)
            trees['latin' if latin else 'greek'][oid].append(s)

    # The open Greek texts, Perseus and First1KGreek (perseus_places): the places LSJ's references name
    # in every edition that holds them and whose word check keeps them, each cut from it, a verse with
    # its neighbours, prose by its sentences, the cited one chosen as a TLG-E line is. A citation a reader
    # or the sidecar moved keeps the corpus line alone; of Bekker's page and line the corpus line is
    # marked to be preferred.
    tlge = {(oid, s['n']): s for oid, items in out.items() for s in items}
    for c in cits:
        f = tlge.get((c['oid'], c['n']), {}).get('found')
        f = P.words(f) if f else []
        c['fw'] = f[0] if f else None
    texts, names, t3 = P.places(cits, args.masters, args.perseus, args.jobs, every=True)
    tally.update(t3)
    here, prefer = [], set()
    for c in cits:
        if not c['places']:
            continue
        if c['reading'] in ('repaired', 'relocated') or c['status'] == 'repaired':
            tally['perseus: citations a reader or the sidecar moved, the corpus line alone'] += 1
            continue
        for pl in c['places']:
            if pl['how'] in ('bekker', 'sidecar bekker') or pl['kind'] == 'bekker-line':
                prefer.add((c['oid'], c['n']))
            here.append((c, pl))
    for k in prefer:
        if k in tlge:
            tlge[k]['prefer'] = True
            tally['perseus: citations of Bekker page and line, the corpus line preferred'] += 1
    wants = collections.defaultdict(set)
    for c, pl in here:
        wants[pl['path']].add(pl['key'])
    got = P.pieces(wants, args.jobs, {p: n.get('mangey') for p, n in names.items()})

    pctx, pprefixes = [], collections.defaultdict(collections.Counter)
    for c, pl in here:
        piece = got.get((pl['path'], pl['key']))
        if not piece:
            tally['perseus: places with no text (a line the editor deletes)'] += 1
            continue
        terms, head, forms, heads, own = entry(c['oid'], c['xb'])
        quote = quotation(c['xb'], c['b'])
        units = [[(w, w) for w in N.words_of(u[1])] for u in piece['units']]
        if len(units) == 1:
            k, words, more = 0, matched(units[0], quote, terms, head)[0], False
        else:
            k, words, more = choose(units, quote, terms, head)
        el = BIBL_EL.match(c['xb'], c['b'])
        p = printed_prefix(N, el.group(1), pl.get('label', pl['key'])) if el else ''
        if p:
            pprefixes[c['cwork']][p] += 1
        pctx.append([c, pl, piece, units, k, words, more])
    want = set()
    for c, pl, piece, units, k, words, more in pctx:
        for ws in (units if more else [units[k]]):
            want.update(w for w, x in ws if GREEK.search(w))
    tally['perseus: words sent to morph'] = analyse(want)
    pabbrev = {w: sorted(x.items(), key=lambda y: (-y[1], y[0]))[0][0] for w, x in pprefixes.items()}

    psources, pverse, pwork = {}, {}, {}
    for c, pl, piece, units, k, words, more in pctx:
        terms, head, forms, heads, own = entry(c['oid'], c['xb'])
        if more:
            h = holding(units, c['oid'], forms, heads)
            if h is not None and h != k:
                k, words = h, matched(units[h], quotation(c['xb'], c['b']), terms, head)[0]
                tally['perseus: cited unit moved in a passage by the morphology'] += 1
        u = piece['units']
        if piece['verse']:
            three = [u[k - 1] if k else piece['before'], u[k], u[k + 1] if k + 1 < len(u) else piece['after']]
            at, lines = [x[0] if x else None for x in three], [x[1] if x else None for x in three]
            tally['perseus: previews, verse'] += 1
        else:                        # prose: the cited sentence only, no neighbours (Bruce, 1 Nov 2026: a thread
            at, lines = [None, u[k][2], None], [None, u[k][1], None]   # to just enough context, not more)
            tally['perseus: previews, prose, the cited sentence only'] += 1
        path, row = pl['path'], pl['row']
        cts = '.'.join(os.path.basename(path).split('.')[:2])
        if path not in psources:             # the work as TLG-E names it, else as the file does
            held = stores['tlg'].works.get(pl.get('work') or c['cwork'])
            name = work_name(*held[2:4]) if held else work_name(names[path].get('author', ''), names[path].get('title', ''))
            ed = 'ed. %s' % row['editors'] if row['editors'] else ''
            imprint = ' '.join(x for x in (row['place'], row['year']) if x)
            lit = 'latinLit' if row['language'] == 'lat' else 'greekLit'
            psources[path] = ('%s (%s)' % (', '.join(x for x in (name, ed, imprint) if x), row['source']), name,
                              names[path].get('urn') or 'urn:cts:%s:%s' % (lit, os.path.basename(path)[:-4]), lit)
        source, name, edition, lit = psources[path]
        s = {'n': c['n'], 'status': 'read' if c['reading'] else 'unread', 'cite': hashlib.sha1(BIBL_EL.match(c['xb'], c['b']).group(0)).hexdigest()[:8]}
        if c['reading']:
            s['kind'] = c['reading']
        work = abbrev.get(c['cwork']) or pabbrev.get(c['cwork']) or name
        place = pl.get('label', pl['key'])      # Philo by Mangey's page: 1.252, not the file's key M.252
        s.update(urn='urn:cts:%s:%s:%s' % (lit, cts, place),
                 ref='%s%s%s' % (work, '.' if work[-1:].isdigit() else ' ', place), source=source)
        s['at'], s['lines'] = at, lines
        if words:
            s['form'] = ' '.join(words)
        tree = SHELF_TREE[row['source']]
        check(s, units[k], c['oid'], forms, heads, own, tree)
        if row['source'] in OPEN_SHELVES:
            s['url'] = scaife(edition, u[k][-1])
        elif row['source'] == 'Loeb':                  # the volume's spread on the Loeb's site; DigiLibLT has no reader online
            m = LOEB_FILE.search(os.path.basename(path))
            url = loeb_url(m.group(1), m.group(2), (piece.get('pages') or [None] * len(u))[k]) if m else None
            if url:
                s['url'] = url
        trees[tree][c['oid']].append(s)
        pverse[id(s)], pwork[id(s)] = bool(piece['verse']), c['cwork']
        ls = [x for x in lines if x]
        tally['perseus: characters of the lines, %s' % ('verse' if piece['verse'] else 'prose')] += sum(map(len, ls)) + len(ls) - 1
        tally['perseus: lemma check: %s' % ('unresolved' if 'found' not in s else 'found' if s['found'] else 'not found')] += 1

    # The translations: every open English translation of the work that places the citation by one of
    # its texts' places, the open texts' first (the Perseus translations share their numbering), the
    # newest first; each its passage, or its three lines where it numbers every line, and its address.
    cands, workof = collections.defaultdict(list), {}
    for t in ('perseus', 'first1k', 'loeb', 'digiliblt', 'greek', 'latin'):
        for oid, items in trees[t].items():
            for s in items:
                k = (oid, s['n'])
                cands[k].append((s, pverse.get(id(s), True)))
                if t in ('greek', 'latin'):
                    workof[k] = wid_of[id(s)]
                else:
                    workof.setdefault(k, pwork[id(s)])
    work_cits = collections.defaultdict(list)
    for k, cs in cands.items():
        work_cits[workof[k]].append([(s['at'][1], printed) for s, printed in cs])
    trs, t2 = translations(args.masters, eds, work_cits)
    tally.update(t2)

    bibls = {}

    def cues(k):
        """What tells the sentence of a long passage of citation k that carries it (cues_of): its texts'
        cited lines and the entry's gloss before it."""
        oid, n = k
        if oid not in bibls:
            bibls.clear()
            bibls[oid] = [m.start() for m in BIBL.finditer(xml[oid])] + [b for r, b in sorted(
                ((m.group(1), m.start()) for m in LABEL.finditer(xml[oid])), key=lambda t: (t[0], t[1]))]   # the labels after the own, as numbered
        return cues_of([s['lines'][1] for s, printed in cands[k]], xml[oid], bibls[oid][n - 1])

    def english(s, tr, name, printed, k):
        """The translation's passage of a preview's cited line, or its three lines; None where it does not
        place it. A passage over TR_WORDS words is trimmed to the citation (cut_english), the record's cut
        saying how (sentences, or true where by length): never dropped."""
        got = [tr.find(c, printed) if c else None for c in s['at']]
        if not got[1]:
            return None
        cut = None
        if all(g and g[1] for g in got) and len({g[0] for g in got}) == 3:
            lines = [tr.ps[g[0]][2] for g in got]
        else:
            passage = tr.ps[got[1][0]][2]
            if len(passage.split()) > TR_WORDS:
                passage, cut = cut_english(passage, cues(k))
            lines = [None, passage, None]
        e = {'n': s['n'], 'source': name, 'at': tr.label(got[1][0]), 'lines': lines, 'url': tr.url(got[1][0])}
        if cut:
            e['cut'] = cut
        return e

    for k in sorted(cands, key=lambda k: (position[k[0]], k[1])):
        for tr, name, tree in trs.get(workof[k], ()):
            for s, printed in cands[k]:
                e = english(s, tr, name, printed, k)
                if e is None:
                    continue
                trees[tree][k[0]].append(e)
                tally['translations: passages stored'] += 1
                tally['translations: passages %s' % ('whole' if 'cut' not in e else 'over %d words, trimmed to the sentences'
                      % TR_WORDS if e['cut'] == 'sentences' else 'over %d words, trimmed by length' % TR_WORDS)] += 1
                break

    # the trees, docs/snippets/<tree>/<block>.json, each block in index order of its entries, an entry's
    # previews by citation, a citation's the newest edition first
    os.makedirs(out_dir, exist_ok=True)
    made, total = set(), collections.Counter()
    for t in TREES:
        blocks = collections.defaultdict(dict)
        for oid in sorted(trees[t], key=lambda i: position[i]):
            blocks[block[oid]][oid] = sorted(trees[t][oid], key=lambda s: s['n'])
        os.makedirs(os.path.join(out_dir, t), exist_ok=True)
        for b in sorted(set(block.values())):
            path = os.path.join(out_dir, t, '%04d.json' % b)
            data = B.dump(blocks.get(b, {}))
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(data)
            made.add(path)
            total[t] += len(data.encode('utf-8'))
        tally['previews: %s' % t] = sum(len(v) for v in trees[t].values())
        tally['citations: %s' % t] = len({(oid, s['n']) for oid, v in trees[t].items() for s in v})
        tally['bytes: %s' % t] = total[t]
    for d, sub, fs in os.walk(out_dir, topdown=False):
        for name in fs:
            if os.path.join(d, name) not in made:
                os.remove(os.path.join(d, name))
        if d != out_dir and not os.listdir(d):
            os.rmdir(d)
    texts_of = collections.Counter((oid, s['n']) for t in TREES if t != 'english' for oid, v in trees[t].items() for s in v)
    tally['citations with a text'] = len(texts_of)
    tally['citations with two or more texts'] = sum(1 for v in texts_of.values() if v > 1)
    lines = {x for v in out.values() for s in v for x in quoted.get(id(s), ())}
    tally['lines quoted, distinct: TLG-E'] = sum(1 for s, L in lines if s == 'tlg')
    tally['lines quoted, distinct: PHI-5'] = sum(1 for s, L in lines if s == 'latin')
    tally['lines quoted, distinct: DDbDP'] = sum(1 for s, L in lines if s == 'papyri')
    tally['lines quoted, distinct: PHI Greek Inscriptions'] = sum(1 for s, L in lines if s == 'inscriptions')
    tally['lines held: TLG-E'] = len(stores['tlg'].at) - 1
    tally['lines held: PHI-5'] = len(stores['latin'].at) - 1
    tally['lines held: DDbDP'] = len(papyrus.at) - 1
    tally['lines held: PHI Greek Inscriptions'] = len(stone.at) - 1
    tally['bytes written'] = sum(total.values())
    tally['lemma check: words morph died on, left unanalysed'] = len(set(died))
    for k in sorted(tally, key=lambda k: k if isinstance(k, str) else ' / '.join(k)):
        print('%s\t%d' % (k if isinstance(k, str) else ' / '.join(k), tally[k]))

if __name__ == '__main__':
    main()
