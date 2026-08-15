"""The metric dictionary — SPEC 3.20 (3). The bijection, both ways, and the no-figures rule."""

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import export_dashboard_data as exporter  # noqa: E402

DICTIONARY = yaml.safe_load(exporter.METRICS.read_text(encoding="utf-8"))
RECORD = json.loads(exporter.OUT.read_text(encoding="utf-8"))
ENTRIES = {one["id"]: one for one in DICTIONARY["metrics"]}


def test_every_metric_the_export_emits_has_a_dictionary_entry():
    """One direction. A figure can only reach a screen through the export, and SPEC 3.20 (3) says
    every displayed metric carries its definition from here — so a metric with no entry is a number
    that would be rendered with no way to explain it.

    `not_computable` is deliberately OUT of this bijection and the exclusion is asserted rather than
    assumed: those entries have no value, they are honest stubs with an unlock condition, and a test
    that silently scoped them out would stop noticing the day one of them grew a number.
    """
    assert set(RECORD["metrics"]) == set(ENTRIES)
    assert set(RECORD["dictionary"]["metrics"]) == set(ENTRIES)
    assert set(RECORD["not_computable"]) & set(ENTRIES) == set()
    for name, stub in RECORD["not_computable"].items():
        assert "value" not in stub, name


def test_every_dictionary_entry_names_the_export_field_it_describes():
    """The other direction, and it RESOLVES: the path is followed into the export, not compared as
    a string. An entry naming a field nobody emits is a definition of nothing."""
    for name, entry in ENTRIES.items():
        node = exporter.dig(RECORD, entry["export_field"])
        assert node, name
        assert entry["export_field"] == f"metrics.{name}"
        assert "sample" in node, f"{name}: the field it names does not carry its sample"


def test_every_entry_carries_both_languages_and_all_five_help_texts():
    """The command centre is bilingual (SPEC 3.20 (3)) and one home holds names, formulas and help.

    Checked field by field rather than by counting keys: a UA name with an empty EN twin would pass
    a count and leave half the tooltip blank.
    """
    for name, entry in ENTRIES.items():
        assert entry["formula"].strip(), name
        for field in ("name", "definition", "how_to_read"):
            for language in ("ua", "en"):
                assert entry[field][language].strip(), f"{name}.{field}.{language}"
        for language in ("ua", "en"):
            assert len(entry["pitfalls"][language]) >= 2, f"{name}.pitfalls.{language}"
            assert all(text.strip() for text in entry["pitfalls"][language]), name
        assert len(entry["pitfalls"]["ua"]) == len(entry["pitfalls"]["en"]), name


def test_the_dictionary_states_no_figure_of_its_own():
    """SPEC 3.20 (1): no hand-typed number reaches a presentation surface, and a tooltip is one.

    So the help texts carry no digits at all — where a pitfall depends on a number it names the
    field to read instead. Two exemptions, each narrow and each named: a SPEC clause reference is a
    citation and not a measurement, so those are stripped (and the strip is asserted to have FIRED,
    or the exemption would be untested); and `formula` is algebra, where a literal like the `1` of
    `1 − promo / old` is an operator. Everything a reader is SHOWN as help is checked.
    """
    citation = re.compile(r"(SPEC )?\d+\.\d+( \(\d+\))?(\(\w\))?")
    stripped = 0
    for name, entry in ENTRIES.items():
        for text in _texts(entry):
            clean, hits = citation.subn("", text)
            stripped += hits
            assert not re.search(r"\d", clean), f"{name}: a figure in help text — {text!r}"
    assert stripped > 0, "the control: some entry does cite a SPEC clause, so the strip can fire"


def test_the_dictionary_is_pinned_in_the_export_by_sha():
    """The export names the dictionary it was built beside, so a tooltip cannot silently redefine a
    number that was already rendered."""
    assert RECORD["dictionary"]["path"] == "config/metrics.yaml"
    assert RECORD["dictionary"]["sha256"] == exporter.summary.sha256_of(exporter.METRICS)
    assert RECORD["provenance"]["inputs"]["config/metrics.yaml"] == RECORD["dictionary"]["sha256"]


def _texts(entry: dict) -> list[str]:
    """The help a reader is shown. `formula` is deliberately not in it — see the test above."""
    out = []
    for field in ("name", "definition", "how_to_read"):
        out += [entry[field]["ua"], entry[field]["en"]]
    out += entry["pitfalls"]["ua"] + entry["pitfalls"]["en"]
    return out
