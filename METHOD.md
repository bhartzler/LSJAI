# How the corrections were made

In this note "we" and "ours" mean Bruce Hartzler and the AI agents he directs; "Logeion's" means the text of LSJLogeion as Helma Dik keeps it. LSJAI's corrections to the text of LSJ come from reading the Logeion text of each entry against a second digital copy and, in doubtful cases, the printed dictionary, by AI readers whose answers were checked by a second AI reader, and from an AI agent applying what the checks upheld with a tool that holds whatever it cannot place exactly. No person read the entries or the corrections one by one; Bruce Hartzler directed the work and chose what to publish.

## The witnesses

- **Logeion** (Helma Dik, `LSJLogeion`): the Perseus LSJ as edited at Chicago, one entry a line, Perseus's ids (`orig_id`) and betacode keys kept. The copy read was LSJLogeion's commit 486e34a7 of 21 Nov 2025; the corrections were then carried onto her commit 5f4f476 of 29 Oct 2026.
- **Copy B** (so called here; the readers' briefs and the verdict column used another label): a second digital copy of the dictionary, plain text, 119,553 entries, that a colleague gave Bruce Hartzler in 2020; he had found it online, did not remember where, and had fixed 153 typos in 120 of its entries; the file carries no colophon. It is not ours to publish, so it is not named or quoted here. It is not an independent typing of the print: of 139 misspelt English words that Perseus's digitization had and Logeion corrected in 2024, it shares 50 (grones for groves, exlravagant, mositen, pulied) and has the right word in 81, so it descends from the same digitization, corrected further by hands unknown. It also follows the print more closely in places: it keeps hyphens as printed, keeps an accent together with a quantity mark, and makes each Hesychius gloss its own entry.
- **The printed dictionary and the 1968 Supplement**, page images, read in the source review where the disagreement turned on them.

Where the two copies disagree, at least one has mistyped the print, and the reading decides which. Where they agree, the comparison sees nothing: an error the two copies share, inherited from the digitization, is not found by this method. The 1,228 corrections are therefore a floor, not the dictionary proofread.

## The comparison

The two texts of each entry were aligned and every differing span became an item: the Logeion reading, copy B's reading, and the entry around them. 13,645 items in 280 units were prepared on 23 to 25 Oct 2026; 6,856 of them were read over four rounds (the last 489 from a preparation refreshed on 29 Oct), 6,789 were not. Sixteen kinds of systematic difference between the two copies (quantity marks, hyphenation and the like) were ruled on as classes, not read item by item.

## The readers

The reading was run as a nightshift by Lychnos, an AI operator role, on 25 to 29 Oct 2026:

- a primary reader on every item: OpenAI's Sol 6.1 at its highest reasoning effort, through Codex;
- a blind check on a fixed share of the items (about a fifth) by a second reader, Anthropic's Astra (ultra), its answers reconciled with the primary's;
- a source review of the disagreements by the second reader, against the printed dictionary and the Supplement where page images were to hand;
- a root acceptance of every delivery: the payloads' hashes, the validators, the external pins replayed.

Each item's verdict is one of `B` (copy B has the print), `Current` (Logeion has the print), `same` (the difference is no difference), `both-wrong` (with the text the print has), or `unknown` (held, with the reason). Every verdict carries a certainty, a reason, and where it can, the evidence quoted with its source.

| Round | Comparisons read | Corrections proposed | Applied | Held |
| --- | --- | --- | --- | --- |
| 25 Oct night (pilot, waves 1 and 2) | 1,355 | 269 | 261 | 8 |
| 26 to 28 Oct batch (W-026 to W-065) | 2,014 | 423 | 401 | 22 |
| 28 to 29 Oct continuation (W-066 to W-129) | 2,998 | 539 | 496 | 43 |
| 29 Oct shift (W-130 to W-139) | 489 | 77 | 70 (69 of the 77, and one reading the reviewer had held, applied on the agent's judgement) | 8 |
| | 6,856 | 1,308 | 1,228 | 81 |

The retained readings (`same`, `Current`) are the larger part of every round and are not in this repository: they are the readers saying Logeion already has the print.

## The application

A correction is applied by Aristarchus, the project's AI philology agent, with a tool (`apply_lsj2.py`, in the project's working notes) that finds the item's span in the entry's XML line by aligning the preparation's plain text with the line's own text, tags dropped and entities read, and replaces exactly that span. It holds, and lists, a correction whose line is no longer the one the preparation read, whose span crosses a tag or a sense boundary, which overlaps another span on the line, or which would leave the line other than well-formed XML. Copy B's literal `<` and `>` go in as entities. Keys, `id`s and `orig_id`s are never changed: an accent corrected in a head is not yet in Logeion's betacode key for it, and the key is what Logeion and Perseus look an entry up by.

A head's visible text in Logeion is its `orth_orig` without hyphens, quantity marks, supplement brackets and a closing ano teleia (114,156 of 116,930 heads follow this). Where a correction changed `orth_orig` and the text had read as the printed form before, the text was made from the corrected form the same way (37 heads); where it had not, it was left and listed (48).

The 81 held corrections are in `corrections/held.tsv` with their reasons; the readers' verdicts on them stand, the application waits for a hand.

## Carrying the corrections onto LSJLogeion's HEAD

Our corrections were made on the 21 Nov 2025 copy. Helma Dik changed 15,841 entries between that copy and 29 Oct 2026 and added 237, mostly citation markup, spacing and entry splits. Each entry we changed was carried onto her current line by a three-way comparison (`merge.py`): where Logeion's line was unchanged, our corrected line replaced it ("replaced Logeion's" in the tables); where Logeion had changed the entry elsewhere, our corrected spans were carried onto its line ("carried onto Logeion's"); where a Logeion change and ours touch the same place (21 entries), Logeion's line stands and ours is listed in `corrections/merge-report.tsv` ("Logeion's kept"); 10 entries Logeion had already corrected the same way. So 1,132 of the 1,163 entries we corrected are changed here. Every file was parsed whole afterwards.

## The readings of the citations and the glosses

`readings/lsj-readings.txt` is a different kind of work: every citation in LSJ's entries read against the texts cited, in the project's digital corpora of Greek and Latin, by AI readers (Anthropic's and OpenAI's models) between 8 and 29 Oct 2026, 200 of the rows by hand; the rows were re-keyed to this copy's text where Logeion's edits moved a citation (101 moved, 28 taken out whose citation is gone or now points elsewhere). A row names the entry (`orig_id`) and the citation's number within the entry, the verdict (`verified`: the cited line holds the word; `repaired`: the word is at the line given instead; `scholion`: the entry cites a scholion or a variant at that line; `relocated`: the citation belongs to another work; `unresolved`), the line as a CTS URN in the canonical numbering of the corpora, who read it, when, how sure, why, and the SHA-256 of the LSJ copy it was read on. `glosses/lsj-glosses.tsv` gives 2,481 entries a short meaning chosen from the entry's own definitions, read and checked the same way.
