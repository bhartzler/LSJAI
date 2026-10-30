# LSJAI

LSJAI is Helma Dik's **LSJLogeion**, the Perseus LSJ as edited for Logeion at Chicago, with corrections to the dictionary's text read by AI readers, checked by a second AI reader and applied by an AI agent, each one recorded with its evidence. No person read the entries; Bruce Hartzler directed the work and chose what to publish. In this repository "we" and "ours" mean Bruce Hartzler and the AI agents he directs; "Logeion's" means the text of LSJLogeion as Helma Dik keeps it. It is a fork, not a new edition: LSJLogeion's files, its entry ids and keys, its layout; our changes on top, in the open, so that Logeion can take what it wants of them and anyone can check each one.

The readers compared Logeion's text of each entry with a second digital copy of the dictionary (copy B: a plain-text LSJ a colleague gave Bruce Hartzler in 2020, found online, source not remembered; it is not ours to publish, so it is not named or quoted here), and said which of the two has the print, going in doubtful cases to images of the printed page and the 1968 Supplement; a second reader checked about a fifth of the answers blind and reviewed the disagreements against the sources; what the checks upheld was applied by a tool. Copy B is not an independent typing: it descends from the same Perseus digitization as Logeion, corrected in many places by hands unknown (`METHOD.md`, "The witnesses"). The comparison therefore finds only the places where the two copies disagree; an error they share is not found by it. `METHOD.md` says how, with the counts.

## What is here

- `greatscott01.xml` to `greatscott86.xml`: LSJLogeion at its commit 5f4f476 (29 Oct 2026), with 1,132 entries changed: 1,228 corrections from the readings of 25 to 29 Oct 2026 on 1,140 entries, 29 typo fixes carried from copy B's own history on 28 entries, and 37 heads whose visible text follows their corrected printed form, carried entry by entry onto Logeion's current files (of the 1,163 entries we corrected, 10 Logeion had already corrected the same way, and 21 are left as Logeion's where a later Logeion edit and ours touch the same place).
- `corrections/corrections.tsv`: every correction, one a row: the entry and its headword, the old and new text, the verdict and its certainty, the reader's reason, the evidence quoted with its source, and how the row was carried onto Helma's current file. `held.tsv`: 81 corrections the readers established that the applier held (a span across a tag or a sense boundary, a line that had changed since the reading), waiting for a hand. `heads.tsv`: the heads followed and kept. `merge-report.tsv`: how each entry was carried, with the 21 where a later Logeion edit and ours touch the same place (Logeion's stands).
- `readings/lsj-readings.txt`: 41,612 readings of the citations in LSJ's entries against the texts cited, in the project's digital corpora of Greek and Latin (verified, repaired, scholion, relocated, unresolved), keyed by entry id and citation number, re-keyed to this copy's text where Logeion's edits moved a citation. `glosses/lsj-glosses.tsv`: a short meaning for 2,481 entries.
- `METHOD.md`: the witnesses, the readers, the checks, the application, the counts.

## Limits

- Copy B's provenance is unknown. It shares Perseus's keyboarding errors, so an error the two copies share is not found by comparing them; the corrections are a floor.
- No person proofread the entries or the corrections one by one. Each correction's evidence is in the table; the readers' certainty is a column.
- 81 corrections the readers established are held, not applied; in 21 entries a later Logeion edit is kept over ours.
- The citation readings name lines in the numbering of one edition of each text, the one the project holds, which may differ from the edition a reader has.

## Credit and license

This work is licensed under Creative Commons Attribution-ShareAlike 4.0 International, as LSJLogeion is (`LICENSE.md` holds the licence's full text; `CITATION.cff` says how to cite). Credit Perseus (Tufts University) for the LSJ data, Helma Dik and Logeion (University of Chicago) for the edited text, and for the corrections, readings and glosses the Philology project of Bruce Hartzler, where AI readers and agents did the work under his direction; `METHOD.md` names them.

Corrections to the dictionary's text are best reported to LSJLogeion, where the editing happens; corrections to the tables here, to this repository.

---

## LSJLogeion's own README (Helma Dik)

# LSJLogeion
This is the heavily edited local Chicago version of the Perseus LSJ; all Greek converted to Unicode; 
many entries split or merged. 
If using these files, please credit Perseus Tufts *and* Helma Dik/Logeion, and please report issues. 

Perhaps a few words about edits to these LSJ files are in order. The changes made are typically to 
reflect the actual text of the dictionary, missed by original data entry. In a few rare cases, changes 
made in the various Supplements are incorporated. Changes are not made to split entries up where the original
had a single entry, except in the case of οἶδα, which I decided to (also) make available as a separate entry.

Despite the many incremental changes over the years, close reading of just about any entry will reveal that more
can be done. Corrections very much welcome! 

<b>Important update to mark-up, Aug. 2025: Accessibility standards demand up-to-date language notations, so lang="greek", described below, has been replaced with lang="grc" ('ancient', up to 1453). </b>

Change to mark-up, Nov. 2024: italics in the print version could include anything from titles to glosses to foreign languages cited for cognates/loans. Markup had long differentiated successfully recognized titles as such (``<title>``), and now, in addition to most Greek, marked since the Perseus days as ``<foreign lang="greek">``, the other languages are also marked. Volunteers to correct Sanskrit (``lang="sa"``) and other obscure languages from Mandian to Old Prussian, etc., are welcome:-) We have cheated slightly. Latin is now marked as ``lang="lat"`` in LSJ, and still marked as ``lang="la"`` in Lewis&Short. Helma apologizes:-). Also, a million thanks to Josh Dillon, who proof-read all italics that did not pass a spell check (spell-check? he would know) *before* this change was made. As always, let us know when you find we missed a spot! 
