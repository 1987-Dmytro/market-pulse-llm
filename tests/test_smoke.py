"""Smoke test: keeps `make check` green on an otherwise empty project.

Without at least one test, `pytest -q` exits 5 ("no tests collected") and the
verifier introduced by this very commit would be red.
"""

import market_pulse


def test_package_imports():
    assert market_pulse.__version__
