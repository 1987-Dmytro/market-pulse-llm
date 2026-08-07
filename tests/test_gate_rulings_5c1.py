"""Offline tests for applying the 5c1 gate rulings and writing the registry.

The registry write is the moment a measurement becomes production configuration, so what is
guarded here is the pair of things a wrong write would cost: the composition the operator ruled
(who enters, in which bucket, with which join), and the promise that the edit is additive.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_gate_rulings_5c1 as apply  # noqa: E402

from market_pulse.registry import load_registry  # noqa: E402

CANON = REPO_ROOT / "docs" / "CHANNELS-launch.md"


def row(handle, bucket, *, verdict="PASS", group=True, open_group=True, title="T"):
    return {
        "handle": handle,
        "bucket": bucket,
        "verdict": verdict,
        "checks": {
            "title": title,
            "discussion_group": (
                {"present": True, "open": open_group, "closed_because": []} if group else None
            ),
        },
        "ruling": None,
    }


# --- the composition the operator ruled ---------------------------------------------------------


def test_the_five_excluded_channels_do_not_enter():
    """Four flagged channels plus the withdrawn late addition. Their gate rows stay; the
    `ruling` field is what says they are out."""
    for handle in ("@kolyastravinsky", "@whowears", "@Mambabyua", "@kulinariya_chat_a"):
        bucket, ruling = apply.final_bucket(row(handle, "comments"))
        assert bucket is None and ruling.startswith("EXCLUDED")
    bucket, ruling = apply.final_bucket(row("@marketopt_official", "late", verdict="FAIL"))
    assert bucket is None and "WITHDRAWN" in ruling


def test_maudau_moves_to_posts_and_loses_its_comments_flag():
    """Ruling 2: its group bans everyone from sending, so the flag the gate measured is
    overridden — a join there would buy nothing and comments_enabled would promise rows."""
    bucket, ruling = apply.final_bucket(row("@maudau", "comments"))
    assert bucket == "posts"
    assert apply.source_entry(row("@maudau", "comments"), bucket)["comments_enabled"] is False
    assert "NO join" in ruling


def test_discountua1_keeps_its_bucket_and_its_join():
    """Ruling 3: 0 of 7 sampled posts is a thin denominator, not a verdict. The window measures
    it; demotion is a cycle-1 question."""
    bucket, ruling = apply.final_bucket(row("@discountua1", "comments"))
    assert bucket == "comments"
    assert apply.source_entry(row("@discountua1", "comments"), bucket)["comments_enabled"] is True
    assert "cycle-1" in ruling


def test_the_replacement_lands_by_the_rule_the_operator_wrote_in_advance():
    """Ruling 4, both branches — the gate's finding picks the bucket, not a later judgement."""
    with_group = row("@marketopt_promo", "late", group=True, open_group=True)
    assert apply.final_bucket(with_group)[0] == "comments"
    without = row("@marketopt_promo", "late", group=False)
    assert apply.final_bucket(without)[0] == "posts"
    assert apply.source_entry(without, "posts")["comments_enabled"] is False


def test_a_replacement_that_did_not_pass_stops_the_run():
    """ "FAIL or FLAG → STOP and report before any further action on it" — enforced, not
    remembered."""
    for verdict in ("FAIL", "FLAG"):
        with pytest.raises(SystemExit, match="stop and report"):
            apply.final_bucket(row("@marketopt_promo", "late", verdict=verdict))


def test_an_unruled_non_pass_row_refuses_to_be_guessed():
    """Silence is not a ruling: a FLAG nobody decided must not enter on the strength of its
    bucket alone."""
    with pytest.raises(SystemExit, match="no ruling covers it"):
        apply.final_bucket(row("@somebody", "comments", verdict="FLAG"))


def test_watch_entries_carry_the_marker_and_keep_the_group_they_may_not_join():
    entry = apply.source_entry(row("@itsmamix", "watch"), "watch")
    assert entry["watch"] is True
    assert entry["comments_enabled"] is True, "the group exists; the join is what it lacks"


def test_the_source_type_ruling_is_applied_and_defaults_to_community():
    assert apply.source_entry(row("@dpssgovua", "posts"), "posts")["source_type"] == "government"
    assert (
        apply.source_entry(row("@uasaler", "comments"), "comments")["source_type"] == "aggregator"
    )
    assert (
        apply.source_entry(row("@epicentrk_sale", "posts"), "posts")["source_type"]
        == "official_retail"
    )
    assert (
        apply.source_entry(row("@retsepty", "comments"), "comments")["source_type"] == "community"
    )


def test_names_come_from_the_gate_record_not_from_the_canon_table():
    """The canon's table truncates its title cells; the record holds what Telegram returned."""
    entry = apply.source_entry(
        row("@x", "posts", title="Третьякова Елена Блогер 👧 Материнство"), "posts"
    )
    assert entry["name"] == "Третьякова Елена Блогер 👧 Материнство"
    assert entry["id"] == "x"


# --- the write is additive ----------------------------------------------------------------------


def test_the_write_appends_sources_and_leaves_taxonomy_byte_identical(tmp_path, monkeypatch):
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    path = tmp_path / "registry.yaml"
    path.write_text(original, encoding="utf-8")
    monkeypatch.setattr(apply, "REGISTRY", path)

    entries = [apply.source_entry(row("@newchan", "comments", title="New 🥛"), "comments")]
    path.write_text(apply.insert_sources(original, entries), encoding="utf-8")

    written = path.read_text(encoding="utf-8")
    assert written.split("\ntaxonomy:\n", 1)[1] == original.split("\ntaxonomy:\n", 1)[1]
    after = load_registry(path)
    assert [s.id for s in after.sources[:4]] == [s.id for s in load_registry_text(original)][:4]
    assert after.sources[-1].id == "newchan"
    assert after.sources[-1].name == "New 🥛"
    assert after.sources[-1].comments_enabled is True


def load_registry_text(text: str):
    """`load_registry` needs a path; the four ids are what this comparison is about."""
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as handle:
        handle.write(text)
    return load_registry(handle.name).sources


def test_an_emoji_title_survives_the_yaml_round_trip(tmp_path):
    """Titles carry emoji, colons and quotes; a hand-rolled YAML writer is where those break."""
    nasty = 'Знижки: "супер" 💛 | все'
    entries = [apply.source_entry(row("@tricky", "posts", title=nasty, group=False), "posts")]
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    path = tmp_path / "registry.yaml"
    path.write_text(apply.insert_sources(original, entries), encoding="utf-8")
    assert load_registry(path).sources[-1].name == nasty


# --- the counts are the canon's, not the script's -----------------------------------------------


def test_the_composition_matches_the_canons_own_summary():
    """`docs/CHANNELS-launch.md` states the post-ruling summary in prose. If the script and the
    canon disagree about how many channels launch, the script is wrong by definition."""
    text = CANON.read_text(encoding="utf-8")
    # The canon hard-wraps its prose; the claim is about the numbers, not the line breaks.
    summary = " ".join(text[text.index("**Сводка после рулингов") :][:400].split())
    assert "запуск 47" in summary
    assert "реестр 4 + 26 комментных + 17 постовых" in summary
    assert "watch 14" in summary
    assert "+ 1 на гейте** (@marketopt_promo)" in summary

    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    buckets = {"comments": 0, "posts": 0, "watch": 0, "excluded": 0}
    for candidate in record["candidates"]:
        bucket, _ = apply.final_bucket(candidate)
        buckets["excluded" if bucket is None else bucket] += 1
    assert buckets["comments"] == 26
    assert buckets["watch"] == 14
    # 17 in the canon's summary plus @marketopt_promo, which the summary counts separately as
    # "+1 на гейте" because its bucket was still pending when the operator wrote it.
    assert buckets["posts"] == 18
    assert buckets["excluded"] == 5
