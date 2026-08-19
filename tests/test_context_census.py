"""The census's MEMORY.md axis is the loader's — the guard on a constant that has just moved.

`scripts/context-census.py` used to count `min(st_size, 25 * 1024)` UTF-8 bytes. The loader that
actually reads the file trims it, keeps **200 lines**, then caps **25 000 UTF-16 code units** cut
back to the last newline (`vee` / `dde`, re-derived from the binary in
`docs/reports/vault-dream.md`). Two units and two numbers, which is Dv526; these tests pin the new
ones and the truncation semantics so a move back is red rather than quiet
([[a_moved_constant_fails_green]]).

`TARGET_KTOK` is pinned here too. It is SUSPENDED by the operator's ruling of 2026-08-19, not
moved, and a suspended number with nothing watching it is the one that drifts.
"""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "context_census", REPO_ROOT / "scripts" / "context-census.py"
)
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "MEMORY.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_constants_are_the_loaders_and_the_target_is_where_the_ruling_left_it():
    assert (census.MEMORY_LINES, census.MEMORY_UNITS) == (200, 25_000)
    assert census.TARGET_KTOK == 9.0
    assert not hasattr(census, "MEMORY_CAP"), "the flat 25 * 1024 byte cap is what Dv526 removed"


def test_a_file_under_both_caps_loses_only_what_the_trim_takes(tmp_path):
    """Today's MEMORY.md is this case, which is why the fix is expected to move the census ~0."""
    body = "\n".join(f"- line {n}" for n in range(50))
    assert census.loaded_memory(write(tmp_path, body + "\n")) == len(body.encode("utf-8"))


def test_a_file_over_the_line_cap_is_cut_at_two_hundred_lines(tmp_path):
    kept = "\n".join(f"- line {n}" for n in range(census.MEMORY_LINES))
    over = kept + "\n" + "\n".join(f"- line {n}" for n in range(census.MEMORY_LINES, 260))
    assert census.loaded_memory(write(tmp_path, over)) == len(kept.encode("utf-8"))


def test_a_file_over_the_unit_cap_is_cut_back_to_a_newline_and_counted_in_BYTES(tmp_path):
    """Cyrillic is one UTF-16 unit and two UTF-8 bytes per character, so a function that returned
    UNITS where the census sums BYTES would fail here — Dv526 pointing the other way."""
    line = "- " + "урок про то, как считается этот файл " * 5
    units, bytes_ = len(line.encode("utf-16-le")) // 2, len(line.encode("utf-8"))
    body = "\n".join([line] * 180)
    assert 180 < census.MEMORY_LINES, "the line cap must not be what fires here"
    assert 180 * (units + 1) - 1 > census.MEMORY_UNITS

    # the loader keeps whole lines: the last newline at or before the cap, and nothing after it
    kept = (census.MEMORY_UNITS + 1) // (units + 1)
    assert kept * (units + 1) - 1 <= census.MEMORY_UNITS < (kept + 1) * (units + 1) - 1
    loaded = census.loaded_memory(write(tmp_path, body))
    assert loaded == kept * bytes_ + (kept - 1)
    assert loaded > census.MEMORY_UNITS, "bytes, not units"


def test_a_first_line_longer_than_the_unit_cap_is_cut_mid_line(tmp_path):
    """The loader's `u > 0 ? u : dde` branch: no newline to fall back to."""
    loaded = census.loaded_memory(write(tmp_path, "x" * (census.MEMORY_UNITS + 500)))
    assert loaded == census.MEMORY_UNITS


def test_the_trim_is_the_JS_one_so_a_BOM_goes_and_a_NEL_stays(tmp_path):
    """`String.trim()` and `str.strip()` disagree at BOTH ends of their difference, so one fixture
    cannot see it: the BOM proves something is stripped, the NEL-and-US edges prove it is not a
    strip of everything Python calls whitespace ([[guard_selftest_negative_control]])."""
    body = "- line one\n- line two"
    assert census.loaded_memory(write(tmp_path, "\ufeff" + body + "\n")) == len(body.encode())

    edged = "\u0085" + body + "\u001f"  # whitespace to Python, ordinary characters to JS
    assert edged.strip() == body, "the fixture must be one str.strip() would have eaten"
    assert census.loaded_memory(write(tmp_path, edged)) == len(edged.encode())


def test_a_missing_memory_file_is_zero_and_not_a_crash(tmp_path):
    """A fresh clone has no MEMORY.md, and a census that raises there measures nothing at all."""
    assert census.loaded_memory(tmp_path / "nothing.md") == 0
