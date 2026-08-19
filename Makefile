.PHONY: check fmt preflight baselines

# The single verifier. Must be green after every commit (docs/SPEC.md §9).
check:
	ruff check .
	pytest -q

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
