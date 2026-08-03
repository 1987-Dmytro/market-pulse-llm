---
type: decision
id: dec-2026-08-03-45g6-context-lines-probe
date: 2026-08-03
status: accepted
tags: [decision]
---

# Facts, not rules — and the fact turned out to be the rule: v2ctx is KILLed at 41/58

**Context:** [[45g5-features-over-prompts]] closed the prompt-form track by pre-registration and
measured the two candidate features. 17 of the 42 refusals are explained by a fact that is not in
the row's text — who wrote the comment (7) and what it replies to (10). A blanket rule over the
larger family would flip **62 of the 258** rows the sitting accepted in order to fix **10**, so
the operator refused the rule and chose to hand the model the **evidence** instead: the same two
facts, rendered beside the post, with the law left where it was. This ADR records the six
dictated verdicts that completed the adjudicated set, the registration of that rendering, and
what the pre-registered probe returned.

## (a) Six values dictated, and two rows left open

4.5g5 applied every ruling a parser could read a value out of — 35 rows — and listed seven it
could not. The team lead read six of them out of the notes by hand
(`docs/PROMPT-4.5g6.md` §Task 1) and they were **transcribed, not derived**:

| row | intents | the note it comes from |
|---|---|---|
| `@VARUS_channel:8478` | `["service"]` | operator-P7 retroactive — bare praise of conduct |
| `@VARUS_channel:14759` | `["availability"]` | «нічого не дістанеться з акційного» is missing goods, not price |
| `@VARUS_channel:11615` | `["taste"]` | dish answer under a food poll (4th of the family) |
| `@VARUS_channel:18839` | `["service"]` | queue at the till is service by the guideline letter |
| `@VARUS_channel:8932` | `["quality","taste"]` | «не смачними» is explicit taste beside quality; label both |
| `@VARUS_channel:9271` | `["service"]` | promo-reward reaction, service family |

The guard that makes this a transcription is small and it is the point: **every intent written
has to be a word the row's own verdict note already uses**, so a typo fails at the run rather
than becoming adjudicated truth — a wrong label here is legal, passes `check_labels` and is
indistinguishable afterwards. `@VARUS_channel:9271` was adjudicated twice (`unclear` in 4.5g5,
`intents` here) and its note now carries both clauses rather than the newer one alone.

**40 of the 42 refusals now state a value.** Two do not, deliberately: `@VARUS_channel:7555`,
whose note names the error and not the answer («что попало?» asks box contents, not presence),
and `@msuaaaa:11876`, which the operator ruled **pending law** on 03.08 — mocking a novelty
claim, true value `[]` or `service`, to be settled in the guideline round. Neither was guessed
at, and the run asserts that set rather than reporting it.

The batch chain is written down: 4.5g5 left `f436c419…`, this phase found exactly that and left
`ea7fa2ab…` (`results/verdicts_45g6.json`). `results/sitting_45g2_manifest.json` remains stale by
design and is still not to be re-pinned.

## (b) The registration: a revision with no new text

`precheck_v2ctx_with_post` **is** `precheck_v2_with_post` — the same object, the same
`prompt_sha256` `113000df…`. Nothing in the prompt moved. What moved is `build_messages`, which
now renders up to two optional lines between `</post>` and `<comment>`:

- `[reply] Addressed to another commenter in the thread.` — when the row's `reply_to_msg_id` is
  not its thread's smallest reply target;
- `[sender] The channel's own identity of @VARUS_channel is speaking — the retailer itself.` /
  `… of @msuaaaa is speaking — an aggregator that reposts retail offers.` — for the two
  hyperactive pseudonyms.

Three guards, because a hash cannot see any of this. The templates are transcribed from the
briefing and checked whitespace-insensitively against a second copy. They pass the v2.2 negation
scan and name no output field — a line that named one would be law arriving as evidence. And
**a row with no feature renders the v2 request byte for byte**: asserted as a unit test, again
by the plan on a real featureless row of the sample (`@VARUS_channel:11605`), and again on the
wire through the real `Asker` with the transport faked. The collision itself is declared in
`prompts.RENDER_ONLY`, so the distinctness guard reads the intent instead of hiding it, and
`docs/annotation/comments.md` §`v2ctx changelog` records it as RENDER-ONLY.

## (c) The gate, with its denominator computed before the run

`results/v2ctx_probe_plan.json`, committed at `8b52971` before a request was made. Same 100 ids
as the v2.2 probe — the fifth paired column. Two denominators:

- **preserved = 58**, the accepted rows, PASS at 55, KILL below 52 (4.5g4's bar, unchanged);
- **feature_named = 17**, PASS at `ceil(0.70·17) = 12`, KILL below `ceil(0.50·17) = 9`.

The 17 is the number the phase turns on and it is a choice worth naming. It is
`refusals_explained_by_a_feature` — the refusals whose *own record* names the feature —
intersected with the 40 rows that state a value. The larger reading, "every refusal that belongs
to a family", is **23**, and gating it would price co-occurrence as explanation: a food-poll
`taste` ruling on a row that happens to reply to somebody is not a thing a `[reply]` line can
fix. Those 23 are reported and never gated. Note that membership is what drives **rendering**
(52 of the 100 rows carry the reply feature, 20 the sender feature, 19 both, 47 neither) while
explanation drives the **gate**; the two sets are deliberately different.

One correction to the briefing, which stated v2.2 = 2 on the feature-named rulings: under the
plan's own definitions it is **3**. The extra row is `@VARUS_channel:6239`, whose value comes
from the P5 family rather than from its own note, so it was `reported_only` in the 4.5g4 plan and
falls inside `fixed` here. The gate is unaffected — n = 17 either way — but the bar to beat was 3.

The sealed pack can no longer be rebuilt: 41 adjudicated values now sit in the batch it was built
from. So the reference labels come from the committed 4.5g4 plan and the chain is checked in its
place — the batch is the one 4.5g6 left, and the **60** sampled rows no verdict has ever touched
still equal that reference field for field.

## (d) The result: KILL, and not on the counter anyone was watching

| column | preserved /58 | feature-fixed /17 | other named /23 |
|---|---|---|---|
| v2 (the labels the sitting judged) | 58 | 0 | 0 |
| v2.1 | 20 | 0 | 4 |
| v2.2 | 37 | 3 | 11 |
| **v2ctx** | **41** | **9** | 11 |

**Verdict: KILL** — `41 < 52`. The feature counter did not kill it: 9 of 17 is above the KILL
line and below the PASS line, which on its own would have been the operator's call.

So the evidence hypothesis is not wrong in kind. Handing the model the two facts tripled the
landings the best prompt revision managed (3 → 9) and improved preservation over both earlier
revisions (20 → 37 → 41). It failed on price, and the price is measurable:

- 17 accepted rows were lost, and **16 of them carry a feature**. Of the 30 accepted rows that
  carry one, **53%** were lost; of the 28 that carry none, one was (3.6%).
- **14 of the 17** flipped `unclear` from `false` to `true`.
- Per field, `unclear` moved on 35 of the 100 rows, against 13 under v2.2.

## (e) What this measured, and it is not what it set out to measure

**A fact rendered for a whole family behaves like a rule over that family.** The distinction
between "evidence" and "law" is a distinction in wording, not in effect, when the law downstream
keys on exactly that fact. `UNCLEAR_RULE` — untouched since v2, and deliberately so — already
says to mark `unclear` for *a reply aimed at another commenter*. Telling the model the row **is**
one is not handing it something to weigh; it is firing that clause. The 4.5g5 measurement priced
a blanket reply rule at 62 of 258 judged-correct rows (24%); this probe, on a sample, lost 16 of
58 accepted rows (28%) — and 16 of the 30 that actually carry a feature. The prediction held. The
context line was the rule, bought at the rule's price.

The second thing measured is that the **discriminator is too coarse for the evidence it carries**.
It fires on 52 of the 100 rows, and only 10 of the 42 refusals are about it. A feature that
describes half the corpus and explains a quarter of the errors cannot be handed to a model as an
undifferentiated fact — whatever the model does with it, it does to half the corpus.

## Consequences

- The v2ctx rendering is **registered and KILLed**, one attempt, no re-prompting and no threshold
  edit. It stays in `prompts.PROMPTS` as a refused instrument, exactly as v2.1 and v2.2 do; its
  record and its plan are the evidence that the bar was set first.
- Three tracks are now closed by their own pre-registered gates: the rulings as negations (v2.1),
  the rulings as affirmations (v2.2), and the features as rendered facts (v2ctx). What has not
  been tried is a **narrower discriminator** — the law's own carve-out is that a reply which
  accuses the retailer directly is judged normally, and nothing in the current feature knows that
  — or the features reaching a *classifier* rather than a prompt. Both are the next briefing's
  decision, and neither is scoped here.
- The batch now holds 40 adjudicated refusals. `@VARUS_channel:7555` and `@msuaaaa:11876` are the
  two open rows, the second pending law.
- No surgical batch run was made and none is authorised by this probe: it is in-sample by
  construction, and only a fresh blind hundred drawn outside the judged 300 can accept a
  re-labelled batch.
- `scripts/backfill.py` now refuses to append to the v1 comment store without `--allow-v1-write`
  (4.5g5 deviation 11, closed).
- Spend: **$0.0301** for 100 requests, against an estimate of $0.0345. Shared cap $1.50, total
  across 4.5g3–4.5g6 **$0.8095**.
