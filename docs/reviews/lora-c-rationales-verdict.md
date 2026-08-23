# lora-c — review gate 1 VERDICT: the rationales (team lead, 2026-08-23)

**This file is the TEAM LEAD's. The executor rewrites ONLY the rows named here and the rows
matching a named pattern, reports the count per pattern in the application report, and flips
`rationale_reviewed` to `true` for all 515 only after the rewrites land.**

Sample read in full: 40 «our» + 9 tier A + 31 tier B (`docs/reviews/lora-c-rationales-sample.md`).
Lens 2's findings were re-checked against the shipped `results/rationales_pass1_v1.jsonl` with my
own greps before ruling; two of its patterns did not reproduce and are closed as no-action below.

## Verdict: ACCEPT with 4 named-row rewrites, 1 label correction, 2 enumerable patterns

Everything not named below stands as shipped. Explicitly ACCEPTED as-is:

- The shared `не_наш_рынок` frame («коментар ПРО X, поза нашою категорією») — the information is
  in the CUE (267 distinct cues over 272 rows, my own count), and a shared frame for a shared
  reading is the honest shape.
- **Post-derived subjects WITH the «з допису» marker** — `@retsepty:7342#49696` vs `7349#49742`
  (byte-identical praise resolving to different post dishes) is the pattern working as designed:
  the post is part of the model's input, and identical text SHOULD resolve by context. This is
  the discrimination the line teaches; it is not a defect.
- Bare thread-inheritance shapes that name the FUNCTION («уточнення до репліки», «згода з
  попередньою реплікою», «службове перенаправлення», «випад у бік співрозмовниці») — rows 29/31
  of the «our» table and tier B #8/#30 are the model examples of this done right.

## Named rows (4 rewrites + 1 label correction)

| row | defect | rewrite to |
|---|---|---|
| `@VARUS_channel:10356#20696` (tier A 1) | «власний формат мережі» — in this corpus «власний» means the COMMENTER's own everywhere else; here it means the chain's. The supervised span must not overload the frame word | «коментар ПРО формат мережі — VARUS CAFE (cue: «варус кафе»)» |
| `@klopotenkofood:6032#21190` («our» 18) | «ПРО власну звичку» claimed on a contentless join («Я🤝❤️‍🔥») — the text carries no habit; the rationale asserts more than the comment holds, then contradicts itself with «беззмістовне приєднання» | «коментар ПРО сирну запіканку — приєднання до відповіді у треді без власного змісту (cue: «Я🤝»)» |
| `@matusi_ukr:22158#578032` («our» 34) | The rationale argues the OTHER label: «лише ЗГАДУЄ морозиво… насправді про лікування горла» under `категория_личное`. **The LABEL STANDS** — «Морозиво. Мені чудово допомагає…» opens by answering the thread's question with the commenter's own use of the product; that is personal category use, not a bare mention. The rationale must argue the label it carries | «коментар ПРО власний досвід із морозивом як помічним при болю в горлі (cue: «Мені чудово допомагає»)» |
| `@VARUS_channel:10367#20766` (the singleton `молочный_бренд`) | **Not a rewrite — a record correction: this row was ABSENT from the sample**, which promised every «our» row (41 in the pool, 40 in the table). Reviewed here from the store: cue «цей сир» occurs, «з допису» marker present, agrees with the label. PASSES. The application report adds it to the sample file with this verdict quoted, so the sample's own promise holds | — (no text change) |
| `@retsepty:7342#49685` | **Label correction, not a rationale defect.** Byte-identical spam text with `#49686` in the SAME thread, labelled `null` vs `не_наш_рынок`. The corpus precedents (`#49707`, `#49711`, tier B 25–27: job/earnings spam) all read `не_наш_рынок` | label `null` → `не_наш_рынок` via a **labels r3 delta** (one row, provenance-tagged, regenerated distributions); rationale follows: «коментар ПРО стороннє оголошення про заробіток, поза нашою категорією (cue: «Зарабатывай вместе с нами»)» |

## Enumerable patterns (executor enumerates, rewrites, reports the list + count)

**P-NULL — a `null` rationale may not attach a definite SUBJECT after «ні про кого».** The
continuation names the comment's FUNCTION (жарт, вигук, згода, побажання, перенаправлення,
випад), never a topic/product as the comment's predicate. Exemplar of the defect:
`@tarilka_malyuka:695#8` «коментар ні про кого — сумнів у першому продукті прикорму» — «сумнів у
<продукті>» smuggles a subject into a no-subject span; rewrite shape: «коментар ні про кого —
емоційний вигук у відповідь на пораду (cue: «Кабачок? Серйозно»)». Lens 2 counted 24 rows of
this shape; enumerate by the rule above (function vs subject after the dash), list every row id
in the application report. Borderline calls default to KEEP (no rewrite) and are listed as kept.

**P-MARKER — a rationale whose subject token does not occur in the comment text must carry the
«з допису»/«під допис» marker.** The marker is what makes post-derived subjects honest. Enumerate:
subject named in the rationale body, absent from the comment (whitespace-collapsed, casefolded),
no «допис» in the rationale → add the marker, changing nothing else. Expected small; report the
list (lens 2's 17 candidates largely carry the marker already — the two proof rows do).

## Lens-2 patterns closed as NO ACTION (did not reproduce on the shipped file)

- «7 UA/RU hybrid rationales („лише УПОМИНАЕТ")» — my grep over all 515 rationale bodies
  (cue excluded — cues legitimately quote Russian comment text) finds **zero** rows with RU-only
  letters. Either fixed by the Dv737 seeded pass or measured on a pre-correction state. The
  application report re-runs the grep and prints the zero (or the rows, if I am wrong).
- «17 rationales name a subject read off the POST» — subsumed by P-MARKER above; WITH the marker
  the shape is correct by design.

## What this verdict does NOT do

No relabeling beyond the one r3 delta row. No rewrite of any row not named and not matching
P-NULL/P-MARKER. The 15-row synthetic finding and the `mention_vs_about` twin of `578032` are
gate 2's business (`docs/reviews/lora-c-synthetic-verdict.md`).
