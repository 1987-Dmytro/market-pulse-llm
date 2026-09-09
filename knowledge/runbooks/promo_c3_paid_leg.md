# Runbook — the c3 paid leg (Маркетопт's private promo channel)

The mechanical half of c3, re-pointed from `promo_c2_paid_leg.md` (which stays as C2's record —
ruling 02.09 (b) cites it). Same producers, different flags: ruling 04.09 (l) item 2 gives the leg
`--out` / `--channels` / `--anchor` / `--prereg` / `--step` / `--cap` instead of sibling scripts.
The channel is written the way `config/registry.yaml` writes it — `+Ejz6ubzm21IyMTQy`, an invite and
not an `@handle` — because `promo_post.owner()` matches `telegram_channels` verbatim and every other
spelling resolves to no source at all (ruling 08.09 (dd) item 5).

## 0. The gates ($0) — chained with `&&`, each exits ≠ 0 before the step it guards

The launch line is no longer typed: `permissions.defaultMode = "bypassPermissions"` lives in
`~/.claude/settings.json` (ruling 09.09 (ff) item 3 — from the PROJECT file that key is ignored).
What the session actually got is stamped by a `PreToolUse(Bash)` hook, so §0 reads the stamp and
never the intention:

```
grep -qx bypassPermissions .claude/session_mode && echo "MODE bypass" \
&& python3 -c 'import json,sys;s=json.load(open(".claude/settings.json"));h=[x for e in s["hooks"].values() for g in e for x in g["hooks"]];ok=s.get("env",{}).get("CLAUDE_CODE_EFFORT_LEVEL")=="xhigh" and s.get("ultracode") is False and {"Bash(runpodctl pod create:*)","Bash(runpodctl pod delete:*)"}<=set(s["permissions"].get("allow",[])) and all(x.get("timeout",600)<=60 for x in h) and len(s["hooks"]["SessionStart"][0]["hooks"])==1 and len(s["permissions"]["deny"])==12;print("HARNESS FIELDS OK" if ok else "HARNESS FIELDS MISSING");sys.exit(0 if ok else 1)' \
&& python3 -c 'import json,sys,pathlib;a=[x[5:-3] for x in json.load(open(".claude/settings.json"))["permissions"]["allow"] if x.startswith("Bash(") and x.endswith(":*)")];c=[l.strip() for l in pathlib.Path(sys.argv[1]).read_text().splitlines() if l.strip().startswith("runpodctl") and " create" in l];bad=[one for one in c if not any(one.startswith(p) for p in a)];print("allow prefixes:",a);[print(("  COVERED   " if one not in bad else "  UNCOVERED "),one[:56]) for one in c];print("CREATE PERMISSION OK" if not bad else "CREATE PERMISSION MISSING");sys.exit(1 if bad else 0)' knowledge/runbooks/promo_c3_paid_leg.md
```

The third gate is the one ruling 08.09 (ee) item 4 asks for: it reads this runbook's OWN create
lines and the allow prefixes out of `.claude/settings.json`, so neither side is typed here. It is
NOT satisfied today — see the note under §2 — and that refusal is the gate working, at $0, before
any anchor exists. Both directions, run 09.09: this file → `CREATE PERMISSION MISSING`, exit 1; the
same command over a file whose create line is `runpodctl pod create …` → `CREATE PERMISSION OK`,
exit 0.

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
**The gap §0's third gate refuses on:** the harness's two allow rules are
`Bash(runpodctl pod create:*)` and `Bash(runpodctl pod delete:*)`. This leg creates a TEMPLATE and a
SERVERLESS ENDPOINT — neither is `runpodctl pod create`, so no narrow rule covers the commands this
runbook actually runs, and in any session where the classifier is live they meet it exactly as
`pod create` did in s33. Named for the team lead; the harness file is not the executor's to edit.

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

## 5. Close the line (the billing walk lags 30–40 min; close AFTER it settles)

```
python3 scripts/runpod_guard.py --step promo-c3 --step-cap <cap> --note "c3: <pages> pages, <posts> posts"
python3 scripts/runpod_guard.py --step promo-c3 --step-cap <cap> --close --note "c3 closed"
```
Then `make tick --window all` — the tick's `--window` default is `w2` and
`tests/test_draw_positions_50.py` reads that default, so the line carries the flag rather than the
default moving (ruling 04.09 (l) item 3's own fallback) — then `make promo-screen`.
