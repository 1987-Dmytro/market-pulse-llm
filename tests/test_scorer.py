"""Phase 1 ships scorer signatures, not numbers: every stub must still refuse to run.

Enumerating the module rather than listing four names means a fifth gate added
later is covered the moment it appears.
"""

import inspect

import pytest
from market_pulse import scorer

STUBS = [
    fn
    for name, fn in vars(scorer).items()
    if inspect.isfunction(fn) and fn.__module__ == scorer.__name__ and not name.startswith("_")
]


def test_every_public_scorer_function_raises_not_implemented():
    assert STUBS, "scorer exposes no public functions"
    for fn in STUBS:
        with pytest.raises(NotImplementedError):
            fn(*[[] for _ in inspect.signature(fn).parameters])
