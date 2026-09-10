# Runbook — the c3 paid leg (Маркетопт's private promo channel)

The mechanical half of c3, re-pointed from `promo_c2_paid_leg.md` (which stays as C2's record —
ruling 02.09 (b) cites it). Same producers, different flags: ruling 04.09 (l) item 2 gives the leg
`--out` / `--channels` / `--anchor` / `--prereg` / `--step` / `--cap` instead of sibling scripts.
The channel is written the way `config/registry.yaml` writes it — `+Ejz6ubzm21IyMTQy`, an invite and
not an `@handle` — because `promo_post.owner()` matches `telegram_channels` verbatim and every other
spelling resolves to no source at all (ruling 08.09 (dd) item 5).

## 0. The gates ($0) — ONE chain, `&&` all the way into §1; each link exits ≠ 0 before the step it guards

Nothing is typed at launch: the session is started as plain `claude` (its bypass confirmation
dialog accepted) and the mode comes from `permissions.defaultMode = "bypassPermissions"` in
`~/.claude/settings.json` (ruling 09.09 (ff) item 3 — from the PROJECT file that key is ignored).
What the session actually got is stamped by a `PreToolUse(Bash)` hook, so §0 reads the stamp and
never the intention.

The key is NOT in `.env` — `~/.runpod/config.toml` holds it, and `--run` refuses without it AFTER
the endpoint exists (`run_promo_c2.py` :: `api_key`). Read it here to prove the file answers and
the length is right; the value is never printed (C2's §0 line 19). This export does NOT reach §3 —
nothing below needs it (`--register` and the guard do not), and §3 exports it again in the same
call as its own launch (ruling 09.09 (ii) item 3(i)):

```
export RUNPOD_API_KEY=$(python3.11 -c "import tomllib;print(tomllib.load(open('$HOME/.runpod/config.toml','rb'))['apikey'])")
python3.11 -c "import os;k=os.environ['RUNPOD_API_KEY'];print(f'RUNPOD_API_KEY set, {len(k)} chars')"
```

Then the two gates and the cap, as ONE command — the cap is not hand arithmetic, it is the last
link of the chain that guards it (ruling 09.09 (hh) item 4(i)):

```
grep -qx bypassPermissions .claude/session_mode && echo "MODE bypass" \
&& python3.11 -c 'import json,sys;s=json.load(open(".claude/settings.json"));h=[x for e in s["hooks"].values() for g in e for x in g["hooks"]];ok=s.get("env",{}).get("CLAUDE_CODE_EFFORT_LEVEL")=="xhigh" and s.get("ultracode") is False and s["permissions"].get("allow",[])==[] and len(s["permissions"]["deny"])==12 and all(x.get("timeout",600)<=60 for x in h) and len(s["hooks"]["SessionStart"][0]["hooks"])==1 and any("session_mode" in x.get("command","") for x in h);print("HARNESS FIELDS OK" if ok else "HARNESS FIELDS MISSING");sys.exit(0 if ok else 1)' \
&& GUARD=$(python3.11 scripts/runpod_guard.py) && echo "$GUARD" | tail -2 \
&& CAP=$(echo "$GUARD" | python3.11 -c '
import re, sys
rem = float(re.search(r"^REMAINING\s+\$([0-9.]+)$", sys.stdin.read(), re.M).group(1))
room = rem - 0.30
if room < 0.15:
    sys.exit(f"FLOOR: REMAINING ${rem:.4f} − $0.30 = ${room:.4f} < $0.15 — STOP for the operator (ruling (l) item 4)")
print(f"{min(0.80, int(room * 100) / 100):.2f}")
') && echo "CAP $CAP" \
&& <§1, in this same call>
```

`$CAP` = min($0.80, REMAINING − $0.30) rounded DOWN to the cent, off the guard's OWN `REMAINING`
line in this session — never carried from a document ([[a_reading_that_outlived_its_state]]).
$0.80 is the operator's word of 09.09 15:20 (ruling (hh) item 3). The three directions were run
before this line was written: live `REMAINING $1.4664` → `CAP 0.80`; a canned `$0.9000` →
`CAP 0.60` (the room, not the ceiling); a canned `$0.4000` → the floor message and exit 1, the
chain dead before §1.

There is no create-permission gate any more: «Allow rules have no effect in bypassPermissions»
(permission-modes), so a rule that could only matter in a session gate 1 already refuses is inert,
and (ee) item 4's gate over an empty `allow` list would refuse every leg for a reason the harness
cannot fix — ruling 09.09 (gg) item 3 retires both, and the fields check now reads `allow == []`.

## 1. The line, in the PAID session, minutes before the create (ruling 06.09 (y))

The registration ANCHORS the line, so it never runs a session early. It is the tail of §0's chain,
in the SAME call: shell state does not survive between calls, so a `$CAP` computed in one call and
used in another is a number typed by hand again.

```
&& PYTHONPATH=src python3.11 scripts/run_promo_c2.py --register \
  --prereg results/prereg_promo_c3.json --census results/promo_census_c3.json \
  --pagecount results/promo_pagecount_c3.json --projection results/promo_projection_c3.json \
  --manifest results/post_media_promo_c3.json --record results/run_promo_c3.json \
  --step promo-c3 --cap $CAP \
&& python3.11 scripts/runpod_guard.py --step promo-c3 --step-cap $CAP \
&& git add results/prereg_promo_c3.json results/spend_promo_c3.json \
&& git commit -m "money(step): promo-c3 anchored"
```
`rung_0.fits` false → STOP, nothing is created. The floor gate in §0 has already answered ruling
(l) item 4's «room under $0.15 → STOP»; from here the cap is READ from the committed registration
(§3), never retyped.

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
## 3. The paid run — DETACHED, one command; it health-checks itself (`assert_serving`)

ONE call, `&&` all the way (ruling 09.09 (ii) item 3(i)). The API key is EXPORTED here and not
inherited from §0: shell state does not survive between calls, and `run_promo_c2.py` reads the key
from the environment only (`:: api_key`, no `config.toml` fallback), so the §0 export would be gone
by now and `--run` would exit 1 AFTER the endpoint exists — the boot billed, nothing collected. The
cap comes back off the registration §1 committed — the same number by construction, and the one the
guard's step anchor was written with.

**SUBSTITUTE BEFORE PASTING** (ruling 09.09 (jj) item 3, nit 1): `--endpoint E` is a PLACEHOLDER —
`E` is the endpoint id §2 printed. Pasted unsubstituted the run fails `assert_serving` with no
worker and $0, which is fail-safe and still a leg to re-launch. The `-T` of the §2 build block is
the same kind of placeholder.

**`[ -n "$RUNPOD_API_KEY" ]` is the second link** (nit 2): `export X=$(…)` takes the ASSIGNMENT's
exit status, not the substitution's, so an unreadable `config.toml` between §0 and §3 would export
an empty key and the `&&` chain would walk on to the create. The check is §0's length line in the
form a chain can use, and it stops before anything is created. Rehearsed at $0 by the team lead:
an empty key stops the chain, a good key passes.

```
export RUNPOD_API_KEY=$(python3.11 -c "import tomllib;print(tomllib.load(open('$HOME/.runpod/config.toml','rb'))['apikey'])") \
&& [ -n "$RUNPOD_API_KEY" ] \
&& CAP=$(python3.11 -c "import json;print(f\"{json.load(open('results/prereg_promo_c3.json'))['step']['cap_usd']:.2f}\")") && echo "CAP $CAP" \
&& { nohup env PYTHONPATH=src python3.11 scripts/run_promo_c2.py --run --endpoint E \
  --prereg results/prereg_promo_c3.json --census results/promo_census_c3.json \
  --pagecount results/promo_pagecount_c3.json --projection results/promo_projection_c3.json \
  --manifest results/post_media_promo_c3.json --record results/run_promo_c3.json \
  --step promo-c3 --cap $CAP > results/run_promo_c3.log 2>&1 & echo $! > results/run_promo_c3.pid; } \
&& cat results/run_promo_c3.pid
```
The launch is BRACED. `a && b && nohup c &` backgrounds the whole `&&` list as one subshell and
`$!` is that subshell's pid — `kill -0` then says GONE while the run is alive. Inside `{ … & … ; }`
the `&` binds the `nohup` alone and `$!` is its pid. Measured on this shape: ONE pid all the way
down, because every link exec's in place — `env`, then `python3.11` (a bash script: the pyenv shim,
which is why the guard lines spell the version and not `python3`), then the interpreter itself.

**Not `| tee`.** That is the foreground form the harness killed TWICE inside C2's own leg
(`results/run_promo_c2.log:113` «resumed after the watcher's TaskStop killed run 2a's process»,
`:171`), and a kill bypasses `except BaseException`: the record does not land and the in-flight
pack is re-bought. C2 finished under `nohup` (the 02.09 log). `setsid` is NOT on macOS — the same
log line 172 records `command not found`; hot.md's «ТОЛЬКО setsid» is the REMOTE runner's rule.

Watch by SHORT polls, each ≤ 55 s, and read the RECORD, never the log:

```
kill -0 $(cat results/run_promo_c3.pid) && echo ALIVE || echo GONE
ps -p $(cat results/run_promo_c3.pid) -o args=   # -> …python3.11 scripts/run_promo_c2.py --run…
tail -3 results/run_promo_c3.log
python3.11 -c "import json;r=json.load(open('results/run_promo_c3.json'))['runs'][-1];print(r['at'], r['timing'])"
```
`kill -0` alone cannot tell the run from a shell that inherited the number; `-o args=` names it,
and `-o comm=` does not — the image is `env` for the first instants and the pyenv shim after that.
The cap is never raised mid-run — the gates decide. The record lands on every exit and a second
`--run` continues (markers on disk); a run that needed one is NOT complete for §5's volume line.

## 4. Teardown — proven by listing, never by an exit code

```
runpodctl serverless delete E && runpodctl template delete T
runpodctl serverless list              # -> []
runpodctl template list --type user    # -> T gone
runpodctl network-volume list          # -> qw4nwleanc mp-srv2 EU-RO-1 100  (positive control)
runpodctl pod list -a                  # -> []
```
The volume STAYS until the line is closed — §5. The close's walk asks
`runpodctl billing network-volume` (`runpod_guard.py:62` `ALWAYS_ON_KINDS`) and an unreadable kind
refuses the close (`:608`), so deleting it here would cost the line its settlement.

Then the post-run reading, RIGHT HERE — PROCESS «Closing a line» puts it after the resource is
released and before any next run, and this is not only an ordering rule: the reading it writes
(`step_spent_usd`) is the right-hand side of the close's tolerance gate, and it is a `max(balance
delta, EVERY billed kind)` — the volume's rent included — while the close's settled figure is
`own_resources`, the volume left OUT (`runpod_guard.py:274`). The gap between them is the volume's
drip since §1's anchor, ≈ $0.01 an hour against a leg priced at $0.19, so every minute between the
teardown and this line spends the 5% band (ruling 09.09 (ii) item 2).

```
CAP=$(python3.11 -c "import json;print(f\"{json.load(open('results/prereg_promo_c3.json'))['step']['cap_usd']:.2f}\")") && echo "CAP $CAP"
python3.11 scripts/runpod_guard.py --step promo-c3 --step-cap $CAP --note "c3: <pages> pages, <posts> posts"
```

## 5. Close the line, THEN the volume (the billing walk lags 30–40 min; close AFTER it settles)

30–40 minutes after §4, in this session or the next. NO `--expect-ms`: C2's own close entry is the
template (`results/spend_promo_pulse_1.json`, the third session — `expected_ms: null`,
`walk_ms 9 821 341`). A serverless walk bills worker UPTIME — the creation boot, the 60 s idle tail,
the killed runs — never the run record's wall, and on C2's own numbers `Σ wall_seconds × 1000` is
5 840 215 ms against that walk: `complete()` (`runpod_guard.py:568`) would be False and the close
would refuse BY CONSTRUCTION (ruling 09.09 (ii) item 2). `--until` is the clock, not a hand-typed
stamp — it is after the run by construction and it bounds the walk (`docs/PROMPT-guard-until.md`):

```
CAP=$(python3.11 -c "import json;print(f\"{json.load(open('results/prereg_promo_c3.json'))['step']['cap_usd']:.2f}\")") && echo "CAP $CAP"
python3.11 scripts/runpod_guard.py --step promo-c3 --step-cap $CAP --close \
  --until "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --tolerance 0.05 --note "c3 closed"
```
The cap is read back from the registration again, as in §3 — §5 runs 30–40 min after the run and a
retried close runs in ANOTHER session, where a `$CAP` from §0 is long gone and `--step` without
`--step-cap` is a `parser.error`. `--close` on a step REFUSES without `--tolerance`
(`runpod_guard.py:697`) and `--close` without `--note` likewise. With no `--expect-ms` the
completeness gate stands down (`complete()` returns True on `None`) and TWO refusals remain, both
real: a walk that does not answer «read» settles nothing (`closing_record` returns None), and a
settled figure further than `--tolerance` from §4's recorded reading is refused with both numbers
named. Either refusal is RETRIED at the next session's start, read-only walk first — never settled
by widening the tolerance, and the volume waits with it.

**Then the volume, and ONLY then** — c3 is the phase's last paid run (ruling 05.09 (q), PHASE §6.1
«the volume goes after c3»; the operator's word in ruling 09.09 (gg) item 6), and it goes after the
close, not before it (ruling 09.09 (hh) item 4(iv)); if the close is retried tomorrow the volume
waits with it, ~$0.24/day. The condition is the run record, not the calendar: every page and every
post ANSWERED in `results/run_promo_c3.json`. A run that needed a second `--run` KEEPS the volume —
a re-download of the weights is dearer. Syntax off the CLI's own help
(`runpodctl network-volume delete --help`: `delete <volume-id>`, aliases `rm`/`remove`):

```
runpodctl network-volume delete qw4nwleanc
runpodctl network-volume list          # -> qw4nwleanc gone  (the delete is proven by the listing)
```

Then `make tick --window all` — the tick's `--window` default is `w2` and
`tests/test_draw_positions_50.py` reads that default, so the line carries the flag rather than the
default moving (ruling 04.09 (l) item 3's own fallback) — then `make promo-screen`.
