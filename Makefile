.PHONY: check fmt preflight

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
