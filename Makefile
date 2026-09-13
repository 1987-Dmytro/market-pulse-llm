.PHONY: check check-stamped fmt preflight baselines tick promo-screen serve loop front

# The single verifier. Must be green after every commit (docs/SPEC.md §9).
check:
	ruff check .
	pytest -q

# The same verifier, with a proof that the tree did not move under it. Twice — Dv785, Dv792 —
# a ten-minute reading had to be killed rather than quoted because something that ARRIVED mid-run
# got written down. HEAD and porcelain are stamped on both sides; a move exits non-zero and the
# reading may not be quoted. Whitelist: the two Stop-hook outputs no test reads —
# knowledge/daily_logs/ and knowledge/index.md (ruling (о), 24.08). hot.md is OUT: it is a suite input.
check-stamped:
	python3.11 scripts/check_stamped.py

fmt:
	ruff format .

# Consumers, prose, pins and digests for the names a contract is about to touch.
# ARGS goes through verbatim, options included; a query that starts with a dash goes
# after a `--` of its own, which is why this recipe does not add one:
#   make preflight ARGS='closing_record billing_by_kind'
#   make preflight ARGS='--limit 4 -- --until'
preflight:
	python3.11 scripts/preflight.py $(ARGS)

# The Baselines block a contract pastes: porcelain, census, the suite count pytest itself
# stamped, the boot files and the pin registry. Instrument output with a timestamp on it —
# never a recollection (Dv553).
baselines:
	python3.11 scripts/baselines.py

# The $0 loop (phase promo-pulse-1, S4). Promotes what the paid legs already wrote into the six
# promo tables and exports the screen's fuel. Idempotent by construction — uuid5 ids and
# INSERT OR IGNORE — so `make tick && make tick` writes zero new rows on an unchanged store.
# The weekly rows leave with the tick because the aggregate build REPLACES the store (measured:
# a planted window does not survive a second `build_aggregates.py` into the same `--out`), so the
# week on disk is only ever the last one collected unless it is written out beside it.
tick:
	PYTHONPATH=src python3.11 scripts/tick.py
	PYTHONPATH=src python3.11 scripts/weekly_positions.py

# The C5 promo screen. Reads `results/promo_screen_data.json` for the market and the graders'
# records of `build_promo_screen.S2_SOURCES` for the S2 block — committed result files, nothing
# else — and exits non-zero with a named error when any of them is missing, which is what makes it
# runnable on a clean clone. The README's S2 block is written from the SAME reader in the same
# breath (ruling 08.09 (dd) item 5 (iii)): the writer had no caller, so the block could go stale
# against the screen beside it without anything saying so.
promo-screen:
	PYTHONPATH=src python3.11 scripts/build_promo_screen.py
	PYTHONPATH=src python3.11 scripts/build_readme_results.py

# The product, locally: http://localhost:8000/ — the app at `/` (a stub until `make front` builds
# `dashboard/app/`) and the four API routes it reads. Localhost only, no auth: the public build is
# static and has no API. Needs the `serve` extra — `pip install -e '.[serve]'`.
serve:
	PYTHONPATH=src python3.11 scripts/serve.py

# The $0 loop, running: wake on `data/schedule.json`, run the tick, write one line into
# `results/loop.log`. It buys nothing — `data/loop.json :: endpoint` is READ and reported, and the
# paid reading of the queue stays the operator's word. `ops/com.marketpulse.loop.plist` is the
# launchd template that starts this at login (install steps in the README; not installed here).
loop:
	PYTHONPATH=src python3.11 scripts/loop_daemon.py

# The app, built: `dashboard/app/` — the static showcase and what `make serve` mounts at `/`.
# Three steps, in this order and for this reason:
#   1. the $0 producer writes `results/front_data.json` from the committed result files (a missing
#      required source is a named, non-zero exit, which is what makes the build refuse rather than
#      ship a screen with a hole in it);
#   2. `npm ci` from the committed lockfile, `tsc --noEmit`, `vite build` — the build EMPTIES
#      `dashboard/app/`, which is why nothing is copied in before it;
#   3. the same producer stages the two files the adapters fetch into `dashboard/app/data/` beside
#      `manifest.json` (file, sha256, bytes).
# `dashboard/app/` and `frontend/node_modules/` are gitignored build outputs: a clone runs this.
front:
	PYTHONPATH=src python3.11 scripts/export_front_data.py
	cd frontend && npm ci && npm run check && npm run build
	PYTHONPATH=src python3.11 scripts/export_front_data.py --stage dashboard/app/data
