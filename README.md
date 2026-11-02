# LSJAI

Look up any entry, with its corrections and their evidence, at [bhartzler.github.io/LSJAI](https://bhartzler.github.io/LSJAI/).

LSJAI is a fork of Helma Dik's **LSJLogeion**, the Perseus LSJ as edited for Logeion at Chicago, with corrections to the dictionary's text made by AI readers, each with its evidence. The site shows the corrections, the text cited under each citation with every edition as a witness and an apparatus of their differences, and the printed page at each entry. An AI agent keeps it under the direction of one person. The method is on the site's [checklist page](https://bhartzler.github.io/LSJAI/agent.html) and, with the counts, in `METHOD.md`.

## What is here

- `dictionary/greatscott01.xml` to `greatscott86.xml`: the dictionary, LSJLogeion's files with the corrections applied and every citation marked.
- `corrections/`: `corrections.tsv`, every correction with the old text, the new text, the reader's reason, the evidence, and what the printed page reads at that place; `withdraw.tsv`, the corrections the printed page contradicts; `held.tsv`, the corrections waiting for a hand; `apparatus.tsv`, each correction as an apparatus entry; `verdicts.tsv`, the verdicts sent from the site's proofread mode; the rest are described in `corrections/README.md`.
- `readings/lsj-readings.txt`: every citation read against the text cited, with its verdict, its reader, and its certainty.
- `docs/snippets/text/`: the text cited, one record per citation: the base edition's lines, every other edition as a witness with its link, and the apparatus. `docs/snippets/english/`: the open English translations of the passages.
- `site/places.json`: where each entry stands on its page of the scan of the ninth edition.
- `glosses/lsj-glosses.tsv`: a short meaning for some entries.
- `site/` and `tools/`: the page, the build, and the tools that make the files above.
- `METHOD.md`: how each file was made, with the counts.

## Limits

- An error that the two digital copies share is not found by comparing them; the printed page is read where they differ.
- The texts cited are not here; each edition is named and linked where it is used.
- The readings name lines in the numbering of the editions the project holds, which may differ from a reader's edition.

## Credit and licence

This work is licensed under Creative Commons Attribution-ShareAlike 4.0 International, as LSJLogeion is (`LICENSE.md`; `CITATION.cff` says how to cite). Credit Perseus (Tufts University) for the LSJ data, Helma Dik and Logeion (University of Chicago) for the edited text, the Perseus Digital Library and the Open Greek and Latin project for the open editions and translations, DigiLibLT, ToposText, the Thesaurus Linguae Graecae, the Packard Humanities Institute, and the Loeb Classical Library for the editions cited as witnesses, and the Philology project of Bruce Hartzler for the corrections, readings, and glosses.

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
