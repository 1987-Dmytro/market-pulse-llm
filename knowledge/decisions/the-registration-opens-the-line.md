---
type: decision
date: 2026-09-06
status: accepted; executed and measured the same day
authority: team lead — ruling 06.09 (y) → PHASE-promo-pulse-1 v14 §6.1, PROCESS «Money» v2.1
tags: [decision, money, guard]
---

# The registration OPENS its line, so §0a lives in the PAID session

## What was decided

`--register --step <line> --cap <n>` reads the guard **with** `--step`, and that reading **creates
and anchors** the line's ledger (`results/spend_<line>.json`). So the registration **is** the
opening of the line, not a preparation for it: it runs in the PAID session, **minutes before the
create**, and never a session earlier. Ruling 05.09 (x) item 2 — "the $0 prep ends at the committed
registration" — is **withdrawn**.

Rejected with it: **(i)** anchoring a session earlier and living with the drift (a rule on the
operator's clock — it would say "buy the pod within N hours or re-anchor"), and **(iii)** deleting
and re-writing the ledger at create time (a ledger anchor is never regenerated).

## Why

The close settles on `own_resources` — the always-on kinds are **outside** it — while the tolerance
gate's right-hand side is a `--note`, a **balance delta**, with those kinds **inside**. So the
network volume's ≈ $0.0079/h drip lands in the reference and never in the settlement, and the drift
is nothing but the **anchor's AGE**:

    drift = drip·H / (pods + drip·H),  H = hours from the anchor to the post-run --note

`promo-iter4`'s entire 2.73 % was that term over 2.45 h. At ~$0.85 of pod it reaches the registered
5 % band at **≈ 6 h**, and sooner on a cheaper run — so an anchor one session old can shut a gate
that nothing later can re-open. Keeping the anchor and the pod in one session makes `H` minutes.

## How it is applied, and what it cost to get right

§0a of `scripts/runbook_promo_dev_1.md` is the paid session's **first minutes**; in front of it only
the start ritual, no development. It is **TWO commits, and that is not a style**: `build_pack()`
opens the record through `committed_registration()`, which runs `git ls-files --error-unmatch` and
`git diff HEAD --quiet` and raises `SystemExit` on either — so a `--pack` placed **between**
`--register` and its commit refuses on the file `--register` has just rewritten. Found at $0 on
2026-09-06 (s30) but with the anchor already live; the order is registration → commit → pack →
commit, and git history is the only witness that both preceded the money.

Then `make check` at THAT HEAD, before the create — (y) item 3 reversed the older "not in a paid
session", because those tests read the committed record and it is also the HEAD the bundle is cut
from. It runs as `ruff` plus three slices whose coverage and floor are **commands**, never eyes.

## What the first execution measured

Iteration 5, 2026-09-06 (s31): anchor 11:06:19Z → post-run `--note` 12:39Z, **H = 1.55 h**, pod
$0.9396 → drift `0.0079·1.55/(0.9396 + 0.0079·1.55)` = **1.29 %**, well inside the 5 % band that
iteration 4 had blown with the same instrument. The §0a order held under live money on its first
paid use. The line's `--close` still refused — on the **clock**, not the anchor: the walk covered
1 072 748 ms of 4 698 000 because billing posts 30–40 min late.

Related: [[a-lines-close-settles-against-its-post-run-reading]],
[[the-holdout-gate-is-rung-0-fits-plus-the-hard-stop]],
[[terminate-after-is-the-cap-less-what-the-step-spent]].
