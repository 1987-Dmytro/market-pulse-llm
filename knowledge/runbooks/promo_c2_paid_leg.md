# Runbook — the C2 paid leg (S4 of `promo-pulse-1`)

The mechanical half of S4, written so the session that gets the cap ruling does not reconstruct it.
Pattern: `scripts/runbook_vis_b.md:42-50` (the same volume, DC, GPU, flags) and the POSITIONS
template/endpoint 5c2 read back from RunPod (`docs/reports/5c2-run.md:138-155`). Nothing here is
a transcript of the 30.08 smoke's create — that was never recorded; this is the readback shape.

## 0. Before anything exists ($0)

```
python3.11 scripts/run_promo_c2.py --register                  # rung 0, the whole step priced
PYTHONPATH=src python3.11 scripts/run_promo_c2.py --dry-run    # selections + hashes + the table
python3.11 scripts/runpod_guard.py                             # exit 0, CYCLE 3 line
```
`rung_0.fits` false → STOP, nothing is created. The step cap is `run_promo_c2.STEP_CAP_USD`
(the ruling's number); a changed cap is one constant plus a new `--register`.

The key is NOT in `.env`: `~/.runpod/config.toml` holds it. Export it for the run only:
`export RUNPOD_API_KEY=$(python3.11 -c "import tomllib;print(tomllib.load(open('$HOME/.runpod/config.toml','rb'))['apikey'])")`
(check the key name with `grep -i key ~/.runpod/config.toml | sed 's/=.*/=<set>/'` first).

## 1. Rung 0 in the guard's words — anchors the step ledger (a write, commit it)

```
python3.11 scripts/runpod_guard.py --step promo-pulse-1 --step-cap 3.20
git add results/spend_promo_pulse_1.json && git commit -m "money(step): promo-pulse-1 anchored"
```

## 2. Build (the template, then the endpoint; creation bills nothing)

```
runpodctl template create --name market-pulse-promo-c2 --serverless \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --docker-start-cmd "bash,-c,exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1" \
  --env '{"SERVING_CONFIG":"POSITIONS","BASE_WEIGHTS":"google/gemma-4-31b-it","MODEL_REVISION":"842da3794eaa0b77d5f08bae87a17459d91ff475"}'
# -> template id T

runpodctl serverless create --name market-pulse-promo-c2 --template-id T \
  --gpu-id ADA_24 --gpu-count 1 --workers-max 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 \
  --idle-timeout 60 --execution-timeout 900 --flash-boot
# -> endpoint id E; read `gpuIds` back from the answer; workers-min 0 is the default (console)
```
Exactly three env vars (POSITIONS + `ADAPTER_DIR` is REFUSED by the worker). `--execution-timeout`
is seconds in, milliseconds stored, and cannot be updated — delete and recreate. A refused create
is the stock test and costs $0 ([[a_stock_window_needs_the_create_not_a_poll]]).

## 3. The paid run — one command; it does the health check (`assert_serving`) itself

```
PYTHONPATH=src python3.11 scripts/run_promo_c2.py --run --endpoint E 2>&1 | tee results/run_promo_c2.log
```
Watch the PROCESS, not the log ([[long_run_watch_the_process]]); the record lands in
`results/run_promo_c2.json` on every exit. A second `--run` continues (markers on disk).

## 4. Teardown — proven by listing, never by an exit code

```
runpodctl serverless delete E && runpodctl template delete T
runpodctl serverless list              # -> []
runpodctl template list --type user    # -> T gone
runpodctl network-volume list          # -> qw4nwleanc mp-srv2 EU-RO-1 100  (positive control)
runpodctl pod list -a                  # -> []
```

## 5. Close the step (the billing walk lags 30–40 min; close AFTER it settles)

```
python3.11 scripts/runpod_guard.py --step promo-pulse-1 --step-cap 3.20 --note "S4 C2: <pages> pages, <posts> posts"
python3.11 scripts/runpod_guard.py --step promo-pulse-1 --step-cap 3.20 --close --note "S4 C2 closed"
```
Then `make tick`, the re-draw of the 50 (`scripts/draw_positions_50.py`), `make promo-screen`.
