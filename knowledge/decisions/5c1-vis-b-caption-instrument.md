---
type: decision
id: dec-2026-08-09-5c1-vis-b-caption-instrument
date: 2026-08-09
status: accepted
tags: [decision]
---

# The project's own Gemma 4 is the caption instrument: 19 of 19, bar A taken, and the bridge says a caption is a sample

**Context:** SPEC amendment 3.13 retired the paid caption API and ruled that captions run on the
project's own Gemma-4; amendment 3.15 moved the vis program onto the serverless runtime
[[srv2-program-close]] earned. vis-b was the gate on that ruling: re-buy, on our own weights, the
answer the API pilot gave — that @atb_market_official's 19 silent posts carry the tracked category
— and report whether the two instruments agree. This record closes vis-b. Every number is read out
of the artifact named beside it.

## (1) The instrument is VALID

`results/captions_gm4_atb19.json`: **19 of 19** media-only posts captioned, 8 jobs, one attempt per
slice, `population.unusable: []`, `no_surrogate_at_all: []`. Every row carries
`caption_source: "gm4-nf4-base"`, the NF4 base at the pinned revision
`842da3794eaa0b77d5f08bae87a17459d91ff475` with the adapter OFF, greedy, forward batch 1, under
the registered prompt `caption_post_gm4` (`41d33d0299fe…`) — 3.13 (3) as written.

`results/caption_rematch_gm4_5c1.json`, against the **untouched** pre-registration
`results/yield_bars_5c1.preregistration.json`, sha
`1aa898180b01762d909e29997db659d2dc70931816855f4c0325b1ea1c892f2b`:

| reading | relevant posts in the 28-day window | bar A (≥4) |
|---|---|---|
| before — the posts' own text, exactly what the yield screen read | **0** | FAIL |
| after — text plus the caption written for the silent ones | **14** | **PASS** |
| after, category terms only (brands ignored) | 12 | PASS |

The *before* is re-derived by the rematch itself and refuses if it cannot reproduce the zero the
signed screen reported — an *after* measured against an irreproducible *before* would be a number
about a different instrument.

**The pre-registered instrument-failure rule of 3.13 (4) did NOT fire.** It says: if ATB with GM4
captions fails bar A where qwen's PASS stands, the instrument failed and the fork returns to the
operator. qwen scored **13** (`results/caption_rematch_5c1.json`), GM4 scored **14**, both against
a bar of 4. The rule was live, it was checked, and it did not trigger.

## (2) The bridge: 8 of 18, on inputs proven identical — and that is a fact about the task

`results/bridge_gm4_qwen_5c1.json`: the two instruments were asked the same task about the same
posts, and their extracted term sets agree on **8 of 18** posts — four of those eight because both
are empty. One post's terms exist only in the GM4 arm (4350); none only in qwen's, because the
qwen run had failed one post outright.

The tempting reading is "the models differ". Before it was written down, the other reading was
tested for **$0**: each written row carries the sha256 of every image sent, and **all 18 posts sent
byte-identical image lists** — same manifest `a93fc8a1…`, unmoved since the fetch commit, same
`[:6]` slice in both drivers, the two arms' image totals differing by exactly the six pictures of
the post qwen dropped. The inputs are not the explanation.

What is left is the finding: an ATB album is **six pages of a promotional leaflet** holding dozens
of products, and a ~230-character caption is a **sample** of it, not a description. Two samplers of
the same dense object agree only where the content is thin — which is why half the agreements are
both-empty. Every term match downstream inherits that sampling.

**This is a 5c2 design input, not a captioner defect.** No choice of "better" captioner repairs it;
what would change it is asking the model a different question (per-page extraction, a targeted
category question) or accepting that leaflet channels are measured by sampling. An agreement rate
between two caption instruments is a **description and gates nothing** — it exists so that a reader
of a future screen number knows which instrument produced it.

## (3) The ceiling, and the one truncation

`CAPTION_MAX_NEW_TOKENS = 400`. One reply of the nineteen hit it —
`truncated_replies: ["@atb_market_official:4391"]`. Per the abort ladder that is **a finding, not a
retry**: the budget was not raised mid-run, because two ceilings inside one comparison cannot be
told apart afterwards. Whether 400 is right for non-leaflet channels is an open question, and 3.13
answers *how* it may be revisited: only as a **named revision**, never silently.

## (4) What the two attempts cost, and the number that was wrong

`results/spend_5c1_vis.json`, anchor `runpod_balance_at_5c1vis_vis-b_start` = $13.9988911968,
never regenerated across both attempts:

| leg | what it bought | reading |
|---|---|---|
| attempt 1 | STOP at the boot rung, 0 captions: two staging pods, endpoint `5zd8xmlj3kg7wl`, two refused handshakes | **$0.1581** balance floor |
| smoke (attempt 2) | 1 post captioned, dump read back byte-for-byte | **$0.0052** rate-derived; $0.1944 cumulative balance floor |
| re-pilot | 19 posts, 8 jobs | **$0.1693** rate-derived; $0.3869 cumulative balance floor |
| session | | **$0.4993** of the $1.00 cap, remaining $0.5007 |

The two columns are different instruments and are not made to agree. All the endpoint time either
attempt ever bought is **813.075 s = $0.2494**; the balance floor at close is **$0.4993**, and the
gap is the three staging and fetch pods at $0.24/h plus the volume's run-rate.

The re-pilot leg was first published as **$0.2211** and that figure is **wrong**. It was a balance
delta, and a $0.24/h fetch pod was running inside the same window, so the pod's cost was charged to
the captions. The defensible number is the leg's own record: **552.14 s** of measured wall clock ×
the settled **$0.00030669/s** (`results/srv2d_cost.json :: rate`) = **$0.1693**, which puts §C.1's
$0.1716 projection within **1.4%** instead of 29% over. A balance delta prices the **account**, not
the **step**; it stays the instrument for the cap and never for a unit cost.

`results/captions_gm4_atb19.json :: timing` also settles a related question from the record rather
than from memory: `worker_ids: ["spotut2es3fgl2"]` across handshake, smoke and re-pilot, with
`idle_share 0.1088` — **one worker, one cold start** for the whole attempt. The pre-registered
cold-start constant **$0.0733** (239.022 s, srv-2d) stays in the formula; attempt 2's own clean
measurement is **244.074 s**, within 2%, and is reported beside it, never swapped in. An earlier
claim that $0.0733 was "twice too high" is retracted — it summed `delayTime` and a weight-load
progress bar, and `executionTime` covers more than that bar.

## (5) The two defects attempt 1 bought, and what they cost

**The guard refused its own base.** `assert_no_adapter` read `active_adapters` as a flag.
`transformers.integrations.peft.PeftAdapterMixin` gives **every** `PreTrainedModel` a bound method
of that name, and a bound method is truthy — so the guard that exists to serve the bare NF4 base
refused a `Gemma4ForConditionalGeneration` carrying no `peft_config` at all. Fixed in `d408034` by
calling it and reading only `ValueError`/`ImportError` as "no adapter"; anything else propagates.
The vis-a tests could not have caught it: they were stubs built from the same assumption as the
guard, and a stub cannot contradict the premise it was written from. The negative control added
with the fix was proven to fail against the old guard body before it was accepted.

**A running worker holds its old code.** The fix was staged onto the volume and hash-verified, and
the next handshake failed identically: one `Starting Serverless Worker`, one worker id, two full
weight loads, `/health` still reading `workers.running: 1`. A `git merge` on the volume changes
files a live process already imported and reaches nothing; `serverless update` does not restart a
worker and `--idle-timeout 60` did not stop a failed one. **The only restart lever is deleting the
endpoint** — which the original contract banned by letter, so the session stopped correctly and the
operator's RESUME addendum amended exactly that line.

Both are now standing procedure rather than prose: `scripts/preflight_serving_guards.py` exercises
the guards against the **real** transformers/peft stack for $0 before any paid session (a stub is
not a valid subject), and `scripts/runbook_vis_b.md` stages the volume **before** the endpoint
exists, with "a worker does NOT restart" as its own rung of the abort ladder.

## (6) What this decides, and what it does not

**Decided:** the caption instrument of 3.13 is built, measured and valid; vis-c may buy the
remaining silent posts on it. The measured production rate for 5c2 is the re-pilot's, not the
smoke's: `wall_per_row 29.06 s`, `seconds_per_row 25.898`, `idle_share 0.1088` — **$0.00891/post**
at the settled rate, against the one-post smoke's $0.00517/post, whose `idle_share 0.3765` and
`calls: 2` do not describe production. A smoke's rate is safe as a bound and wrong as a ratio.

**Not decided here:** the launch composition — the operator's freeze stands until screen v2; the
400-token ceiling for non-leaflet channels; and whether leaflet-style albums should be asked a
different question at all, which is the bridge's finding handed to 5c2.

Related: [[srv2-program-close]] · [[5c1-relevance-floor-and-discovery]] ·
[[5c1-day2-composition-and-search]] · [[2026-08-09]]
