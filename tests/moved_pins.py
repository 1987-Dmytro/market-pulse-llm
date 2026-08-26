"""One shared assertion: a sealed record rebuilds identically EXCEPT where it pins a moved file.

`docs/PROMPT-pass1-fewshot.md` D0.2 registered a second pass-1 text in `src/market_pulse/prompts.py`
and ruled that old records' pins of that module are «moved since» and are NOT re-pinned. Five sealed
records pin it — the two label packs, the two pass-1 registrations and the reader top-up's — and
each of them had a test asserting a byte-identical rebuild. Those tests were right and they still
have to say something true, so the claim is narrowed rather than deleted: the rebuild differs from
what shipped at EXACTLY the paths that pin the moved module, and at those paths it carries the
module's live sha.

Both directions, and derived rather than typed: the expected set is computed from which paths hold
the live sha, so a record that moved somewhere else fails, and a list that has gone stale fails too
([[an_enumerated_diff_is_asserted_in_both_directions]]).

The one thing that may NOT move is the registered pass-1 TEXT. `pass1_comment_gm4_v1`'s own sha is
unchanged — that is what keeps probe-b's evidence and this line's dev legs comparable — and every
caller below asserts it beside the diff.
"""

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import write_pass1_prereg_b as prereg_b  # noqa: E402

PROMPTS = REPO_ROOT / "src" / "market_pulse" / "prompts.py"


def live_sha(path: Path = PROMPTS) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paths_holding(record, value, prefix: tuple[str, ...] = ()) -> set[str]:
    """Every dotted path at which `record` carries exactly `value`."""
    if isinstance(record, dict):
        return {
            one
            for key, item in record.items()
            for one in paths_holding(item, value, (*prefix, str(key)))
        }
    if isinstance(record, list):
        return {
            one
            for index, item in enumerate(record)
            for one in paths_holding(item, value, (*prefix, str(index)))
        }
    return {".".join(prefix)} if record == value else set()


def servable(pack: dict) -> dict:
    """A sealed pack copy whose ONE legitimately-moved pin is brought up to date.

    The pod's handshake refuses a pack whose `instruments.parser.sha256` is not this checkout's
    `prompts.py` — correctly, and that is now every pack sealed before D0.2 registered the second
    pass-1 text. The runner tests are about the render, the resume and the persistence; re-pinning
    the module sha in a THROWAWAY copy is not editing the sealed record, and the file on disk is
    never written. What must not be touched is the per-task prompt sha, and it is not: v1's text has
    not moved and the copy carries it unchanged.
    """
    copy = json.loads(json.dumps(pack))
    copy["instruments"]["parser"]["sha256"] = live_sha()
    return copy


_SERVABLE: dict[Path, Path] = {}


def servable_file(path: Path) -> Path:
    """:func:`servable`'s copy as a FILE, for the runners that are handed a `--pack` path.

    Several transport tests give `main()` a path rather than a dict, and one drives the runner in a
    subprocess. The sealed file on disk is never written: the copy lives in a temp directory for the
    length of the session, and is built once per path.
    """
    if path not in _SERVABLE:
        where = Path(tempfile.mkdtemp(prefix="servable-")) / path.name
        pack = servable(json.loads(path.read_text(encoding="utf-8")))
        where.write_text(json.dumps(pack, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        _SERVABLE[path] = where
    return _SERVABLE[path]


def assert_only_the_prompts_pin_moved(
    shipped: dict, rebuilt: dict, *also: Path, carried: dict[Path, tuple[str, ...]] | None = None
) -> set[str]:
    """The whole claim, in one call. Returns the paths that moved, so a caller can name them.

    `also` names further files this contract edited whose pins may therefore move — a producer that
    hashes ITSELF into the record it writes is the usual one. Each is resolved to its LIVE sha and
    the paths carrying it are found in the rebuild, so the allowance is derived from the file rather
    than from a name somebody typed ([[provenance_cannot_name_itself]]).

    `carried` is for the other half of a moved file: a record that pins a CONFIG also quotes values
    out of it, and those move with the pin and only with it. Amendment 3.25 (1) revised
    `config/qlora.yaml` (`max_seq_len` 1 408 -> 2 816) and line B's registration is never re-pinned,
    so its `config_sha256` now describes revision 1 — and `training.max_seq_len` moves in the
    rebuild for exactly that reason and no other. The allowance is CONDITIONAL on the pin having
    actually moved, so when the config is restored these names stop being excused
    ([[one_constant_answering_two_questions]]).
    """
    expected: set[str] = set()
    for path, names in (carried or {}).items():
        here = paths_holding(rebuilt, live_sha(path))
        assert here, f"no path in the rebuild carries {path.name}'s live sha — check is vacuous"
        if any(path_name not in paths_holding(shipped, live_sha(path)) for path_name in here):
            expected |= set(names)
    for path in (PROMPTS, *also):
        found = paths_holding(rebuilt, live_sha(path))
        assert found, (
            f"no path in the rebuild carries {path.name}'s live sha — the check is vacuous"
        )
        expected |= found
    moved = set(prereg_b.moved_paths(shipped, rebuilt, opaque=()))
    assert moved == expected, {"moved": sorted(moved), "expected": sorted(expected)}
    return moved
