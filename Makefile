.PHONY: check

# The single verifier. Must be green after every commit (docs/SPEC.md §9).
check:
	ruff check .
	pytest -q
