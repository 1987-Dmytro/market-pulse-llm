"""`config/ui_strings.yaml` as a file: both languages everywhere, no figures, and one home per fact.

The page-level half — every key rendered, no key orphaned — lives in `tests/test_build_dashboard.py`
because it needs the document. What is checked HERE needs only the two config files, so it stays
green on a checkout where the export has not been built.
"""

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

STRINGS = yaml.safe_load((REPO_ROOT / "config" / "ui_strings.yaml").read_text(encoding="utf-8"))
METRICS = yaml.safe_load((REPO_ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))
TABLE = STRINGS["strings"]

CITATION = re.compile(
    # a law, named as one: the word, then the number, then its clause if it has one
    r"(?:SPEC|amendment|амендментом|амендмент)\s*\d+\.\d+(?:\s*\(\d+\))?"
    r"|\d+\.\d+\s*\(\d+\)"  # the same clause where the sentence already said which law
    r"|G\d[a-e]–G\d[a-e]"  # the pre-registered gate range
    r"|sha256"  # the algorithm's name, which carries its own digits
    r"|window-2|вікна-2"  # the ordinal of a window that does not exist yet
    r"|6a"  # the phase whose backlog a gap stub names
)
"""What a digit is ALLOWED to be part of: an identity, never a measurement.

The pattern is general so a new citation of the same kind needs no new line here, and it is TIGHT
on purpose — a law is matched only when the sentence names it as one, so a bare decimal like a
median or a share matches nothing and fails the test, which is the whole point. The keys that may
cite are enumerated below one by one, so a new exemption cannot arrive unseen."""

MAY_CITE = {
    "common.delta.next_window": "the window a trend needs, and it is an ordinal, not a count",
    "stub.gap.note": "names phase 6a as the owner of the backlog",
    "t0.insights.note": "cites SPEC 3.20 (4), the rule that makes the insights code-generated",
    "t1.text_less.badge": "cites SPEC 3.19, the rule that puts these rows outside the sample",
    "t2.price_origin": "cites SPEC 3.17 and 3.20 (5), the boundary it is stating",
    "t5.named_by_law": "cites amendment 3.20 (6), which is what the badge means",
    "t8.provenance.note": "names sha256",
    "t8.gates.model": "names the gates G1a–G1e that the export does not carry",
    "t8.embedded.note": "names sha256",
}


def test_every_key_carries_both_languages_and_nothing_else():
    for key, entry in TABLE.items():
        assert set(entry) == {"ua", "en"}, key
        for language, text in entry.items():
            assert isinstance(text, str) and text.strip(), f"{key}[{language}]"
            assert not text.startswith(" ") and not text.endswith(" "), key


def test_no_string_states_a_figure_of_its_own():
    """SPEC 3.20 (1): a label is a presentation surface, so a hand-typed number is a hand-typed
    number wherever it sits.

    The 6a precedent is Dv339 — «У вікні-1 листівки зібрані лише по АТБ» was true when it was typed
    and false the moment a second chain was collected. What survives the check is a citation: the
    number of a law or the ordinal of a window is an identity that cannot go stale, and each key
    allowed to carry one is named above with its reason.
    """
    for key, entry in TABLE.items():
        for language, text in entry.items():
            stripped = CITATION.sub("", text)
            if re.search(r"\d", stripped):
                assert key in MAY_CITE, f"{key}[{language}]: {stripped}"
                assert not re.search(r"\d", CITATION.sub("", stripped)), f"{key}[{language}]"
    for key in MAY_CITE:
        assert key in TABLE, f"{key} is exempted and no longer exists"
        assert any(re.search(r"\d", TABLE[key][language]) for language in ("ua", "en")), (
            f"{key} no longer cites anything — drop its exemption"
        )


def test_a_template_asks_for_the_same_values_in_both_languages():
    """A placeholder present in one language and missing in the other fails at build time on one
    side only, which is exactly the kind of break a bilingual page hides until someone toggles."""
    for key, entry in TABLE.items():
        holes = {language: set(re.findall(r"\{(\w+)\}", text)) for language, text in entry.items()}
        assert holes["ua"] == holes["en"], f"{key}: {holes}"


def test_the_metric_dictionary_and_the_chrome_do_not_hold_the_same_fact():
    """One home per fact — D4. Metric names, definitions and formulas live in `config/metrics.yaml`
    and the tooltip and the glossary both render from THAT file; the chrome file may not restate
    them, or the two would drift and a reader would meet a metric explained two ways."""
    values = {text.strip().lower() for entry in TABLE.values() for text in entry.values()}
    keys = set(TABLE)

    for metric in METRICS["metrics"]:
        assert metric["id"] not in keys
        assert f"metric.{metric['id']}" not in keys
        for language in ("ua", "en"):
            assert metric["name"][language].strip().lower() not in values, metric["id"]
            assert metric["definition"][language].strip().lower() not in values
            assert metric["how_to_read"][language].strip().lower() not in values
        assert metric["formula"].strip().lower() not in values


def test_the_file_names_its_authority():
    assert STRINGS["version"] == 1
    assert "PROMPT-phase6b" in STRINGS["authority"]
