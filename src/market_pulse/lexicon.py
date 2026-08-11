"""The category vocabulary as LAW: `config/lexicon.yaml` (SPEC 3.17 (8)).

uni-a's finding in one line — the schema follows the registry and the vocabulary did not
(`docs/reports/uni-a.md`, LEAK L1). The pre-filter's category half read
`data/category_lexicon_draft.json`, a file marked `status: draft-not-law` that no edit of
`config/registry.yaml` could reach, so a new tracked category kept passing dairy rows. This module
is the loader for the file that replaced it, and the two guards that keep it honest:

* **the stems are the registry's own words.** Every tracked stem must be a PREFIX of a token in
  its group's display names — `scripts/measure_categories.py::build_lexicon`'s rule, moved here
  so there is ONE implementation of it and the law is held to the same bar its draft was.
* **the units are ordered, not a set.** `units` is longest-first because a regex alternation takes
  the first branch that matches and «г» before «грн» would read "90 грн" as a size.

Returns a plain mapping rather than a dataclass, deliberately: it is the shape
`yield_screen.compile_categories` already reads, so the law drops into every existing caller
without touching one of them, and `Taxonomy` next door keeps its raw mapping for the same reason.
"""

from pathlib import Path

import yaml

from market_pulse.registry import Taxonomy

LAW = Path(__file__).resolve().parents[2] / "config" / "lexicon.yaml"
"""The law file. A path constant rather than a default argument, so a caller that wants another
file passes it and a caller that wants the law does not restate where it lives."""

REQUIRED = ("status", "tracked", "endings", "units")


def load_lexicon(path: str | Path = LAW, *, taxonomy: Taxonomy | None = None) -> dict:
    """Load and validate the vocabulary law, or raise ``ValueError`` naming the defect.

    Strict for the reason `registry.py` is strict: a stem that silently drops out of the file
    matches nothing, and "the category is not in the corpus" is what that looks like downstream.

    ``taxonomy`` is optional and is the loud half: pass one and every tracked stem is checked
    against that registry's display names. The pre-filter's callers all hold a registry already,
    and a caller that does not (the schema reading `units`) has nothing to check against.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    for key in REQUIRED:
        if key not in data:
            raise ValueError(f"{path}: the lexicon needs a '{key}' section")
    tracked = data["tracked"]
    if not isinstance(tracked, dict) or not tracked:
        raise ValueError(f"{path}: 'tracked' must be a non-empty mapping of group -> stems")
    for group, stems in tracked.items():
        if not isinstance(stems, list) or not stems:
            raise ValueError(f"{path}: tracked group {group!r} has no stems")
        for stem in stems:
            if not isinstance(stem, str) or not stem.strip():
                raise ValueError(f"{path}: tracked group {group!r} carries an empty stem")
    for key in ("endings", "units"):
        values = data[key]
        if not isinstance(values, list) or not values:
            raise ValueError(f"{path}: '{key}' must be a non-empty list")
        for value in values:
            # `endings` legitimately carries "" — the bare stem — and `None` is what a bare `-`
            # in YAML becomes, which would reach `re.escape` and raise somewhere far from here.
            if not isinstance(value, str):
                raise ValueError(f"{path}: '{key}' carries {value!r}, which is not a string")
    if any(not unit.strip() for unit in data["units"]):
        raise ValueError(f"{path}: a unit is empty — «число + nothing» matches every number")
    if taxonomy is not None:
        check_against_registry(data, taxonomy, path=path)
    return data


def unmatched_stems(
    tracked: dict, taxonomy: Taxonomy, *, exempt: frozenset[str] | set[str] | tuple = ()
) -> dict[str, list[str]]:
    """The rule, in one place: which tracked stems are not a prefix of any display name.

    Group by group, and a group the registry does not track at all is its own defect — reported
    with an empty stem list under its key so the caller can name it.

    ``exempt`` is the Russian-form escape hatch: the registry's display names are Ukrainian, so
    «кефир», «творог» and «морожен» have nothing to be a prefix of. Named one by one rather than
    by loosening the check, which is the only thing keeping a typo visible.
    """
    import re

    groups = taxonomy.tracked_groups
    names = {
        key: " ".join([group["name"], *(group.get("subcategories") or {}).values()]).casefold()
        for key, group in groups.items()
    }
    out = {}
    for key, stems in tracked.items():
        if key not in names:
            out[key] = []
            continue
        tokens = re.findall(r"[\w']+", names[key])
        missing = [
            stem
            for stem in stems
            if stem not in exempt and not any(token.startswith(stem) for token in tokens)
        ]
        if missing:
            out[key] = missing
    return out


def check_against_registry(lexicon: dict, taxonomy: Taxonomy, *, path: str | Path = LAW) -> None:
    """Raise unless every tracked stem names something in the registry. The loud guard."""
    exempt = frozenset(lexicon.get("ru_variants") or ())
    bad = unmatched_stems(lexicon["tracked"], taxonomy, exempt=exempt)
    if bad:
        detail = "; ".join(
            f"{key}: {stems or 'is not a tracked group of the registry'}"
            for key, stems in sorted(bad.items())
        )
        raise ValueError(
            f"{path}: {detail} — are not prefixes of any display name in the registry."
            " A tracked stem that names nothing measures nothing"
        )
