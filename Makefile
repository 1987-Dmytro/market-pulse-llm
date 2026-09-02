.PHONY: check check-stamped fmt preflight baselines tick promo-screen

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
tick:
	PYTHONPATH=src python3.11 scripts/tick.py

# The C5 promo screen. Reads `results/promo_screen_data.json` and NOTHING else, and exits non-zero
# with a named error when a source is missing — which is what makes it runnable on a clean clone.
promo-screen:
	PYTHONPATH=src python3.11 scripts/build_promo_screen.py
