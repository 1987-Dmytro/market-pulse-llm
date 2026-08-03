---
type: decision
id: dec-2026-08-03-45g5-features-over-prompts
date: 2026-08-03
status: accepted
tags: [decision]
---

# The prompt track is closed by its own gate: adjudicated truth into the data, and two features measured before either is bought

**Context:** [[45g4-v22-affirmative-rewrite]] ends the third attempt to teach a model what the
operator had already decided. v2.2 said the eight rulings affirmatively, the pre-registered
100-row probe came back **KILL** (preserved 37/58 against a bar of 55, fixed 9/29 against 24),
and the rewrite was not what failed — v2.1 scored 20/58 and 4/29 on the identical rows. 15 of
the 20 remaining misses named `unclear`, and the corporate-voice class was shown to be out of
any prompt's reach: the rule reached the model twice and still failed on rows whose text
identifies no retailer. The operator chose **path A** — put the decisions into the data, teach
the collector the field that was missing, and measure the two candidate features before
registering anything. This ADR records what was done and what the numbers say.

## (a) The closure: the prompt-form track is shut by pre-registration, not by opinion

The v2.2 gate was committed before the first request and it refused. That is the whole
argument. A fourth wording could be written, and there is no version of it that reaches the
rows whose discriminator is absent from the input. Nothing about the eight rulings is in
question — they are the operator's, adjudicated row by row — only the route by which they
were supposed to arrive.

**Nothing was registered in this phase and no model was called.** `results/spend_45g5.json`
carries a provider anchor read before the work started; the phase-end delta is **$0.000000**
against a pre-registration of $0.00. `prompts.py` is untouched.

## (b) The decisions go into the data: 35 rows, and the 7 that stay open

`scripts/apply_sitting_verdicts.py` writes the sitting's answers onto the rows they name in
`data/annotation/uplabel_precheck_45g2.jsonl`. Scope was "rulings that name a value", and 35
of the 42 refusals qualify:

| where the value is written | rows | fields set |
|---|---|---|
| in the verdict note, in the shape the 4.5g3 parser reads | 29 | `unclear` 19 · `intents` 6 · `sarcasm` 3 · `sentiment` 1 |
| in the guideline's own prose, by pattern, and nowhere else | 6 | P5 → `intents ["service"]` (3) · P6 → `unclear true` (3) |
| **total** | **35** | `unclear` 22 · `intents` 9 · `sarcasm` 3 · `sentiment` 1 |

(`@VARUS_channel:1271` is named by both its note and P6, and the two agree; a family value that
contradicted a row's own note would stop the run rather than be merged.)

All 35 moved a value; none was already right. Only the named fields move — a ruling about
`unclear` says nothing about `intents`, and overwriting the rest would launder unjudged model
output as adjudicated truth. Rows carry `annotator: sitting-45g-verdicts` and a note naming
the ruling. The batch went 612 → 626 `unclear: true` and 809 → 800 rows with no intent.

**Seven refusals name the error and no value, and are left alone**: `@VARUS_channel:8478`
(P7 — a family this phase was not given), `@msuaaaa:11876`, `@VARUS_channel:18839`,
`@VARUS_channel:8932`, `@VARUS_channel:14759`, `@VARUS_channel:7555`, `@VARUS_channel:11615`.
Three of them — 8478, 14759, 11615 — do write the answer down in prose ("`[]` should be
`["service"]`", "`["price"]` should be `["availability"]`", "`[]` should be `["taste"]`"), and
the parser cannot read them because the note omits the field name. Listed, not guessed at.
One row that *was* touched, `@VARUS_channel:9271`, also gestures at an intents value in prose
("a promo-reward reaction (service family)") that was not applied for the same reason.

**A pin breaks here on purpose.** `results/sitting_45g2_manifest.json` pins the batch at
`df688e59…`; it is now `f436c419…`. The pin describes the corpus the 300 verdicts were passed
on, so it is right and stale at once, and it is **not** to be re-pinned.
`results/verdicts_45g5.json` carries both shas and is the only place the chain is written
down — the shape `results/relabel_45e.json` already uses for `results/calib_45e_manifest.json`.
`scripts/build_sitting_pack.py` will now refuse, and that refusal is correct.

## (c) The collector learned the field, and the corpus was re-fetched to fill it

`raw_store.comment_record` stores `message.reply_to_msg_id` raw. Nothing is derived at
collection: the value lives in the **discussion group's** id space while `parent_msg_id` is a
**channel** id, and the two are not comparable. This was measured on one real thread before the
long run rather than assumed — a top-level comment carries the group's mirror of the post and
no `reply_to_top_id`; a reply to another commenter carries the target comment plus
`reply_to_top_id` = the same mirror. Comparing `reply_to_msg_id` with `parent_msg_id` would
have called every comment a reply, and the table would have looked fine.

Both channels were re-fetched into `data/raw/comments_v2/`, joined onto v1 by (channel,
msg_id), v1 text kept as law. Drift is negligible: **2 deleted, 4 fresh-only, 0 edited** across
11,338 rows. `data/raw/comments/` is byte-identical.

## (d) The two families, measured

`results/features_45g5.json`. A comment is a **reply to a comment** when its reply target is
not the thread's smallest one (the group's mirror of the post, created before any comment on
it, so anything else is a comment — deleted since or not). A **channel-identity** row is one of
the two hyperactive pseudonyms: `58805a362c39…` (3,761 comments) and `2fa2b73f617b…` (876),
against **81** for the third-busiest — the cut is not a judgement call.

| | all comments | the 1,912 batch | the 42 refusals | judged correct | of those, `unclear: false` |
|---|---|---|---|---|---|
| replies to a comment | 3,147 / 11,338 | 882 | 23 co-occur, **10 explained** | 120 / 258 | **62** |
| channel identity | 4,637 / 11,338 | 236 | **7** | 45 / 258 | **10** |
| — `2fa2b73f617b…` @VARUS_channel | 876 (874 with text) | 219 | 6 | 40 | **6** |
| — `58805a362c39…` @msuaaaa | 3,761 (**73** with text) | 17 | 1 | 5 | **4** |
| both at once | 941 | 233 | 7 | 43 / 258 | 9 |

**"23 of 42" is a co-occurrence count and is reported as one.** A refusal can sit in the reply
family without the feature explaining it: a food-poll `taste` ruling is a note-level error that
happens to land on a row which structurally replies to someone. Of the 23, **10 have a verdict
note that names a commenter addressee** ("reply aimed at another commenter", "argument with
another commenter"); the other 13 are P5, P6, a queue joke, a sarcasm idiom, bare thanks. Ten is
what the feature would explain, and it agrees with the team lead's own "~10–12 of 42".

**The identity family is two senders behaving oppositely, and the average hides it.** The VARUS
support account is what the family was named for: 874 of its 876 comments carry text, it owns 219
batch rows and 6 refusals, and a blanket rule costs **6 of 40** (15%). The msuaaaa pseudonym is
the channel's own author — `Фото вже прибрали, дякую Вам`, `Кожного товару по 1 шт в один чек` —
but **3,688 of its 3,761 rows are media-only with no text at all**, so it contributes 81% of the
family's corpus column and 7% of its batch column, and a blanket rule costs **4 of its 5** (80%).
It is also a different case in law: `@msuaaaa` is an `aggregator` in the registry, not
`official_retail`, so P6 — *the retailer answering in its own voice* — does not describe it. **A
rule scoped to the VARUS pseudonym alone costs 6 of 40, not 10 of 45.**

Cross-checked: a second discriminator (the target is a comment this repo collected) finds
2,971 instead of 3,147. The 180-row symmetric difference is the class it is blind to — replies
to comments deleted since — plus two threads nobody answered at the top level, which have no
observed head and are named in the record rather than counted.

**The team lead's "219 / 46 / 7" does not reconcile as one scope, and was not made to.** 219
(batch) and 46 (judged) are `2fa2b73f617b…` **alone**, which accounts for **6** of the 42
refusals. The 7th comes from `58805a362c39…`. The pair together is 236 batch rows, 52 judged,
7 refusals, 45 judged-correct — and **10 of those 45 carry `unclear: false`**, which is the
10-of-45 exactly. Both readings are in the record.

## (e) The overlay-unsafety finding, and it is worse for the bigger family

The number that decides whether a feature is worth buying is not its size but what a rule over
it would cost on rows the sitting already called right.

- **Channel identity: 10 of 45 for the pair, 6 of 40 for the retailer alone.** A blanket "this
  pseudonym is the retailer → `unclear: true`" breaks 10 rows in 45 as the brief scopes it, and
  6 in 40 scoped to the account the rule is actually about. Small enough to argue about, and it
  buys 6 or 7 refusals.
- **Replies to a comment: 62 of 258, to buy 10.** A blanket "a reply to another commenter is not
  a consumer reaction" would flip **62 of the 258 judged-correct rows** — nearly a quarter of
  everything the sitting accepted — to explain the **10** refusals whose notes name the addressee.
  This is the "a direct accusation against the retailer outweighs a commenter addressee"
  exception (guideline rule 5, `@VARUS_channel:15587`) priced for the first time, and it is not
  an edge case: it is six times the size of the thing the rule would fix.

**The two families are nearly nested, not additive.** All 7 identity refusals are also reply
refusals, and 233 of the 236 identity batch rows are. Structurally they cover **23 of 42**
refusals; **explained**, they cover **17** (the 10 the reply notes name plus the 7 identity rows,
disjoint), leaving **25 unexplained**. **19 refusals are in neither family at all** — **14 of them
name `intents`** (the food-poll
`taste` family, the promo-mechanics `service` family, `packaging`, three "wrong
`availability`"), 3 name `unclear` and 2 name `sarcasm`. Neither feature touches any of them.

## (f) What the next probe is, and what this phase does not do

The numbers above feed a briefing, not a decision taken here. The registered probe will be of
the **v2 prompt plus context lines** — the sender and reply facts handed to the model as
evidence — and **not** the v2.2 rules, which the gate already refused. Nothing was registered,
no prompt was added, no model was called, and the wave-2 hundred is still unjudged.

The 62-against-10 ratio is the reason a context line is the shape to try rather than a rule: a
line that says *this comment replies to another commenter* leaves the exception available to
the model, where a rule removes it. Had only the sizes been measured — 882 batch rows against
236, 23 refusals against 7 — the reply feature would look like the obvious buy.

## Consequences

- `data/annotation/uplabel_precheck_45g2.jsonl` carries 35 hand-adjudicated rows under
  `annotator: sitting-45g-verdicts`. It is no longer pure model output, and any counter that
  reports "the precheck said X" has to say which rows it means.
- `results/sitting_45g2_manifest.json` no longer matches the file it pins.
  `scripts/build_sitting_pack.py` refuses. Do not re-pin it; read
  `results/verdicts_45g5.json` for the chain.
- `data/raw/comments_v2/` is the store anything reading reply structure should use. v1 remains
  the text of record and is byte-identical.
- Every comment collected from now on carries `reply_to_msg_id`. `message.poll` is still
  dropped — a named Phase-5 debt, deliberately not bundled here.
- **17 of the 42 refusals are explained by a feature and 25 are not** — the union of the 10 the
  reply notes name and the 7 identity rows, which turn out to be disjoint. Derived in the record
  rather than added up: 19-in-neither plus 13-co-occurring would double-count the identity
  refusals that sit inside the reply family.
- `data/raw/comments_v2/` is **gitignored**, like the rest of `data/raw/`. It exists only in the
  working tree and is rebuilt by `PYTHONPATH=src python3 scripts/fetch_comments_v2.py` — 1,538
  threads, ~54 minutes, $0. `results/drift_45g5.json` is the committed record of what it held.
