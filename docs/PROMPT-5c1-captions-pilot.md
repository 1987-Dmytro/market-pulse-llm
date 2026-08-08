# PROMPT-5c1-captions-pilot — the image census and the ATB caption pilot

**Contract:** operator direction 08.08 (yield-screen acceptance): the
empty-channel recheck and the launch signing wait for IMAGE evidence.
This contract buys that evidence at pilot scale: **one paid step,
cap $0.10**, everything else $0. The launch signing and any registry
action stay FROZEN until screen v2 — not in this contract's scope.

## Steps, in order

0. **Rulings on record ($0, offline):** the operator ruled the two
   bar_A_sole_carriers (@polyakova_fitness on «варто», @myrhorodtown
   on «Президент») COUNT AS BELOW bar A — noise passes, matcher
   guards for «Варто»/«Президент» deferred to the 5c3 lexicon
   session. Record beside the screen rulings, house pattern.

1. **Image census ($0):** over every registry channel's collected
   window, count posts by their `parents.context` state (post_text /
   image_caption / poll_text / no_text_and_no_caption) →
   `results/image_census_5c1.json`: per-channel counts + totals, and
   a PRICE PROJECTION for captioning every no-text image post, at the
   per-caption cost measured in 4.5g2 (cite the artifact the rate
   comes from). This number is what the operator's full-run decision
   reads.

2. **Fetch ATB's windowed image posts ($0, network):** the 19
   no-text posts of @atb_market_official's screen window — media via
   the fetch_post_media pattern, graceful FloodWait, raw v1 stays
   byte-untouched (sidecar placement as in 4.5g2).

3. **Caption the 19 (PAID, cap $0.10):** registered `caption_post`
   prompt, same model as 4.5g2. Own spend anchor (this pilot's three
   constants — never import another phase's), STOP over cap, one
   attempt, no retry loops.

4. **Matcher over captions ($0):** the yield screen's matcher + same
   lexicon over text+captions for ATB's window. Report: does ATB now
   clear bar A=4 (relevant_posts before → after); per-term hits;
   THREE sample captions quoted VERBATIM (evidence lines, включая
   один промах). Bars stay untouched — prereg `1aa89818…` stands.

## Verify & report
`make check` green; spend read from this pilot's anchor, not summed
receipts; report = artifact paths + the before/after ATB number + the
census price projection + Deviations. Then STOP: the full-run
captioning (~all 66) and screen v2 are the OPERATOR'S decision on the
census price × pilot quality — do not start them.

## DO NOT
Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md):
read and commit, never edit. No full-run captioning; no registry or
watchlist edits; no bars edits; no Stars spend; never `git add -A`;
no re-run of refused screens without `--out`. Batch 1 stands.
