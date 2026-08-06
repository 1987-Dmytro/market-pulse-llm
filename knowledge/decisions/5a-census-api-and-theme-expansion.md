---
type: decision
id: dec-2026-08-06-5a-census-api-and-theme-expansion
date: 2026-08-06
status: accepted
tags: [decision]
---

# The census had to fetch, and three themes buy 6.8% of the gap

**Context:** Phase 5a (`docs/PROMPT-5a.md`) opened the production loop with three deliverables
— channel discovery with a coverage ledger, a storewide poll census, and the loop skeleton.
Two of them returned an answer the brief had not budgeted for. This record is the ratification
of the first, the number behind the second, and the operator's ruling of 2026-08-06 taken on
both. Everything below cost **$0**: Telegram's API is free and no model was called.

## (1) The census premise was false, and the census fetched

`docs/PROMPT-5a.md` scoped deliverable 2 as `$0, no API`, on a premise it states at lines 43–44:
**"The poll payload already sits in the stored raw messages (4.5g2 took its transcripts from
them; the collector just never surfaced it as text)."** It does not, and it did not.

Measured, not argued:

| claim | check | result |
|---|---|---|
| the payload is in the store | keys of every stored post record | **10 keys, 6 057 of 6 057**, none a poll |
| the collector saved it | `market_pulse.raw_store.post_record` | never reads `message.poll` |
| 4.5g2 read it off disk | `scripts/fetch_post_media.py:164` | `client.get_messages` — a **live fetch** |

So **799 of the 815** text-less ids had no transcript anywhere on disk; the 16 that did were in
`data/annotation/post_captions.jsonl`, off one channel's sitting pack (41 media-only parents).
The deviation taken: re-read the 815 ids from Telegram in batches of 100 and
write the transcripts to a **derived sidecar beside v1**, `data/raw/post_polls.jsonl`, in the
shape `caption_posts.poll_caption` writes and `parents.load_captions` already reads. The `$0`
constraint held; the `no API` line in the deliverable heading did not, and could not.

**The positive control is the reason this is ratifiable rather than merely plausible.** The 16
poll rows 4.5g2 transcribed live on 2026-08-03 were re-derived by the storewide run and came back
**16 of 16 byte-identical** — computed by the script and persisted as `cross_check_45g2` inside
`results/poll_census_5a.json`, not asserted in a report. If the read or the transcript format
had moved, every count in that file would be suspect; they are not.

What the store's 815 silent posts actually are: **37 polls (4.54%)**, 758 photos, 16 video,
2 giveaways, 1 voice, 1 document, **0 deleted**. Its rate and 4.5g2's 16-of-41 are different
populations and the record says so in its own body (`not_a_continuation_of_16_of_41`) — the two
numbers are not comparable and neither supersedes the other.

## (2) Three themes close 6.8% of the coverage gap

`results/discovery_5a.json`, 11 queries over the three themes authorised 2026-08-04, 66
candidates, each measured over a **fixed 28-day window** (the entry check's own sample is the
last 50 posts, however long that took — 18 to 73 days on the channels in the store).

| | channels | subscribers | gap to 10 000 000 |
|---|---|---|---|
| registry now | 4 | 178 372 | 9 821 628 |
| + all 66 candidates | 70 | 846 543 | **9 153 457** |
| + only the 29 live ones | 33 | 534 419 | **9 465 581** |

The three themes buy **6.8%** of the gap counting every candidate, **3.6%** counting only the
ones that posted in the window. 37 of 66 published nothing in four weeks and hold 312 k
subscribers between them — including the largest find of the scan, `@itsmamix` at 280 895.
Only **19** have both a discussion group and traffic. Size and activity are **uncorrelated**
(Pearson −0.01 over the 66): the top of the subscriber column is not the top of the flow column,
which is the second caveat — *subscribers != comment flow* — as a measurement rather than a
sentence.

## (3) The operator's ruling, 2026-08-06

Taken at the 5a acceptance on `docs/RESEARCH-5a1-themes.md`, whose landscape survey puts the
**entire** relevant UA-Telegram segment at ~4–5 M summed subscribers entering everything, with
audience overlap on top. The ≥10 M target is about twice the size of the segment it is drawn on.

- **Four more themes authorised**, and SPEC 3.11 (4) amended the same session: cooking/recipes,
  supermarket promos, **health/fitness — against the team lead's recommendation**, and
  food-quality/falsification watch (the operator's own: dairy is the most falsified category in
  UA retail, so the theme lands inside the mission). The reasoning on health/fitness is the
  point of the ledger: a theme priced by a scan beats a theme talked out of the brief, and a
  subtotal row of zeros is an answer where a missing row is an oversight. `theme_subtotals` in
  `scripts/discover_channels.py` therefore emits a row for every authorised theme, empty or not.
- **Seed handles** from the research note are checked directly, past the search: Telegram's
  `contacts.SearchRequest` ranks by its own relevance and caps each query, so a channel the
  operator already knows about can simply never surface.
- **The coverage target itself is deferred** to the combined ledger (`results/discovery_5a1.json`)
  — the decision the number is for is whether to keep 10 M, move it, or launch on the registry
  four and let the first reporting cycle price the question. Not taken here.

Also corrected in the same amendment: SPEC 3.11 (4) said the loop launches on **five** registry
channels. There are four — `@znizhki_ua` was removed 2026-07-27 ([[znizhki-ua-removed]]) and
`config/registry.yaml` had held four for a week when 3.11 was drafted. 5a flagged it and did not
edit the file; the team lead recorded the fault rather than smoothing it over.

**Consequence:** the census deviation is ratified as taken, and 5a's coverage numbers stand as
the "before" column of the combined ledger. The three-theme reading is not superseded by the
widened scan — the widened scan carries these 66 rows rather than re-measuring them on a
different day.

Related: [[45g2-captions-and-quiz-rulings]] (where the poll transcript format was born),
[[znizhki-ua-removed]], [[architecture-stack]].
