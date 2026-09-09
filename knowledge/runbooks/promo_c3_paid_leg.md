# Runbook — the c3 paid leg (Маркетопт's private promo channel)

The mechanical half of c3, re-pointed from `promo_c2_paid_leg.md` (which stays as C2's record —
ruling 02.09 (b) cites it). Same producers, different flags: ruling 04.09 (l) item 2 gives the leg
`--out` / `--channels` / `--anchor` / `--prereg` / `--step` / `--cap` instead of sibling scripts.
The channel is written the way `config/registry.yaml` writes it — `+Ejz6ubzm21IyMTQy`, an invite and
not an `@handle` — because `promo_post.owner()` matches `telegram_channels` verbatim and every other
spelling resolves to no source at all (ruling 08.09 (dd) item 5).

## 0. The gates ($0) — chained with `&&`, each exits ≠ 0 before the step it guards

Nothing is typed at launch: the session is started as plain `claude` (its bypass confirmation
dialog accepted) and the mode comes from `permissions.defaultMode = "bypassPermissions"` in
`~/.claude/settings.json` (ruling 09.09 (ff) item 3 — from the PROJECT file that key is ignored).
What the session actually got is stamped by a `PreToolUse(Bash)` hook, so §0 reads the stamp and
never the intention:

```
grep -qx bypassPermissions .claude/session_mode && echo "MODE bypass" \
&& python3 -c 'import json,sys;s=json.load(open(".claude/settings.json"));h=[x for e in s["hooks"].values() for g in e for x in g["hooks"]];ok=s.get("env",{}).get("CLAUDE_CODE_EFFORT_LEVEL")=="xhigh" and s.get("ultracode") is False and s["permissions"].get("allow",[])==[] and len(s["permissions"]["deny"])==12 and all(x.get("timeout",600)<=60 for x in h) and len(s["hooks"]["SessionStart"][0]["hooks"])==1 and any("session_mode" in x.get("command","") for x in h);print("HARNESS FIELDS OK" if ok else "HARNESS FIELDS MISSING");sys.exit(0 if ok else 1)'
```

There is no create-permission gate any more: «Allow rules have no effect in bypassPermissions»
(permission-modes), so a rule that could only matter in a session gate 1 already refuses is inert,
and (ee) item 4's gate over an empty `allow` list would refuse every leg for a reason the harness
cannot fix — ruling 09.09 (gg) item 3 retires both, and the fields check now reads `allow == []`.

## 1. The line, in the PAID session, minutes before the create (ruling 06.09 (y))

The registration ANCHORS the line, so it never runs a session early. The cap is
`min($0.50, REMAINING − $0.30)` as the guard prints REMAINING — quoted from its own line, never
carried from a document ([[a_reading_that_outlived_its_state]]):

```
python3 scripts/runpod_guard.py                                   # read REMAINING now
PYTHONPATH=src python3.11 scripts/run_promo_c2.py --register \
  --prereg results/prereg_promo_c3.json --census results/promo_census_c3.json \
  --pagecount results/promo_pagecount_c3.json --projection results/promo_projection_c3.json \
  --manifest results/post_media_promo_c3.json --record results/run_promo_c3.json \
  --step promo-c3 --cap <the derived cap>
python3 scripts/runpod_guard.py --step promo-c3 --step-cap <the derived cap>
git add results/prereg_promo_c3.json results/spend_promo_c3.json && git commit -m "money(step): promo-c3 anchored"
```
`rung_0.fits` false → STOP, nothing is created. Room under $0.15 → STOP for the operator's word
(ruling (l) item 4).

## 2. Build — serverless, as C2's leg was (creation bills nothing)

```
runpodctl template create --name market-pulse-promo-c3 --serverless \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --docker-start-cmd "bash,-c,exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1" \
  --env '{"SERVING_CONFIG":"POSITIONS","BASE_WEIGHTS":"google/gemma-4-31b-it","MODEL_REVISION":"842da3794eaa0b77d5f08bae87a17459d91ff475"}'
# -> template id T

runpodctl serverless create --name market-pulse-promo-c3 --template-id T \
  --gpu-id ADA_24 --gpu-count 1 --workers-max 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 \
  --idle-timeout 60 --execution-timeout 900 --flash-boot
# -> endpoint id E
```
## 3. The paid run — one command; it health-checks itself (`assert_serving`)

```
PYTHONPATH=src python3.11 scripts/run_promo_c2.py --run --endpoint E \
  --prereg results/prereg_promo_c3.json --census results/promo_census_c3.json \
  --pagecount results/promo_pagecount_c3.json --projection results/promo_projection_c3.json \
  --manifest results/post_media_promo_c3.json --record results/run_promo_c3.json \
  --step promo-c3 --cap <the derived cap> 2>&1 | tee results/run_promo_c3.log
```
The cap is never raised mid-run — the gates decide. Watch the PROCESS, not the log
([[long_run_watch_the_process]]); the record lands on every exit and a second `--run` continues.

## 4. Teardown — proven by listing, never by an exit code

```
runpodctl serverless delete E && runpodctl template delete T
runpodctl serverless list              # -> []
runpodctl template list --type user    # -> T gone
runpodctl network-volume list          # -> qw4nwleanc mp-srv2 EU-RO-1 100  (positive control)
runpodctl pod list -a                  # -> []
```

**Then the volume, and ONLY then** — c3 is the phase's last paid run (ruling 05.09 (q), PHASE §6.1
«the volume goes after c3»; the operator's word given in ruling 09.09 (gg) item 6). The condition is
the run record, not the calendar: every page and every post ANSWERED in `results/run_promo_c3.json`.
A run that needs a second `--run` KEEPS the volume — 100 GB is ~$0.24/day, a re-download of the
weights is dearer. Syntax off the CLI's own help (`runpodctl network-volume delete --help`:
`delete <volume-id>`, aliases `rm`/`remove`):

```
runpodctl network-volume delete qw4nwleanc
runpodctl network-volume list          # -> qw4nwleanc gone  (the delete is proven by the listing)
```

## 5. Close the line (the billing walk lags 30–40 min; close AFTER it settles)

```
python3 scripts/runpod_guard.py --step promo-c3 --step-cap <cap> --note "c3: <pages> pages, <posts> posts"
python3 scripts/runpod_guard.py --step promo-c3 --step-cap <cap> --close --note "c3 closed"
```
Then `make tick --window all` — the tick's `--window` default is `w2` and
`tests/test_draw_positions_50.py` reads that default, so the line carries the flag rather than the
default moving (ruling 04.09 (l) item 3's own fallback) — then `make promo-screen`.
