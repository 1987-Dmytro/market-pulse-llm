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

from market_pulse.registry import AUDIENCES, load_registry  # noqa: E402

CANON = REPO_ROOT / "docs" / "CHANNELS-launch.md"

AWAITING_A_RULING = set()
"""Gated, not PASS, and no ruling covers it yet — the operator's rule is to stop and report.

Named rather than skipped by accident: `final_bucket` refuses to guess, so every candidate in
this set raises, and a NEW unruled non-PASS row makes the tests below fail loudly instead of
quietly entering the registry on the strength of its bucket. Empty right now: every gated
candidate has a resolution, @akcii_skidki_plt having been excluded on 2026-08-07."""


def resolved(record: dict):
    """Every candidate that has a resolution, with the pending ones checked to still be pending."""
    pending, rows = set(), []
    for candidate in record["candidates"]:
        try:
            rows.append((candidate, apply.final_bucket(candidate)[0]))
        except SystemExit:
            pending.add(candidate["handle"])
    assert pending == AWAITING_A_RULING, f"unruled rows changed: {pending}"
    return rows


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


def test_discountua1_was_kept_to_be_measured_and_the_measurement_excluded_it():
    """Ruling 3 of 06.08 kept it so the 28-day window could measure its real flow. The window
    measured: 19 posts repeating one line with the products inside the images. The later ruling
    wins, and the earlier one is not silently still in the code."""
    bucket, ruling = apply.final_bucket(row("@discountua1", "comments"))
    assert bucket is None
    assert "text-free" in ruling
    assert "@discountua1" not in apply.KEPT


def test_uasaler_leaves_the_composition_entirely():
    """Wave 2: the 07.08 word named the CHAT and demoted the channel; the 08.08 ruling names the
    CHANNEL. It is out of the registry, not sitting in posts-only."""
    bucket, ruling = apply.final_bucket(row("@uasaler", "comments"))
    assert bucket is None
    assert "EXCLUDED ENTIRELY" in ruling
    assert "@uasaler" not in apply.MOVED


def test_a_city_feed_enters_posts_only_and_buys_no_join():
    """ "Дозаявка №3": PASS → registry bucket posts, comments_enabled false, watch false. The
    group it may have does not move any of the three — that is the whole ruling."""
    gated = row("@poltava_misto", "city", group=True, open_group=True)
    bucket, ruling = apply.final_bucket(gated)
    assert bucket == "posts"
    assert "POSTS-ONLY" in ruling and "5c2" in ruling
    entry = apply.source_entry(gated, bucket)
    assert entry["comments_enabled"] is False
    assert entry["watch"] is False
    assert entry["source_type"] == "community"


def test_a_city_feed_that_did_not_pass_is_not_routed_by_its_bucket():
    """ "FAIL or FLAG → report with evidence, do not resolve yourself" — the refusal is what
    enforces it, and a city row must not slip past on the strength of the ruling."""
    for verdict in ("FAIL", "FLAG"):
        with pytest.raises(SystemExit, match="no ruling covers it"):
            apply.final_bucket(row("@poltava_misto", "city", verdict=verdict))


def test_a_city_row_the_ruling_does_not_name_refuses_to_enter():
    """The bucket is a label the gate wrote; the ruling is what authorises an entry. A 17th city
    handle appearing in the gate must not enter on the label alone."""
    with pytest.raises(SystemExit, match="CITY_FEEDS does not name it"):
        apply.final_bucket(row("@some_new_town", "city"))


# --- audience is the canon's table, not a reading of the channels --------------------------------


def canon_audience() -> dict[str, str]:
    """The "Сегментация источников" table as handle → segment, parsed rather than retyped.

    The section writes each segment as a bullet whose handles run across wrapped lines, with the
    watch channels after a `+ watch:` inside the same bullet — they belong to the segment, and
    the canon's own per-segment count includes them. `regional` names no handles: its row says
    "по прохождении гейта: 16 хендлов дозаявки №3", so its members are that list.
    """
    import re

    text = CANON.read_text(encoding="utf-8")
    block = text[text.index("## Сегментация источников") :]
    block = block[: block.index("Сверка:")]

    table = {}
    for chunk in re.split(r"\n- \*\*", block)[1:]:
        segment = chunk.split("(", 1)[0].strip()
        for handle in re.findall(r"@[A-Za-z0-9_]+", chunk):
            table[handle] = segment
    return table


def test_the_audience_table_is_the_canons_own():
    """A hand-copied 56-row table is a table that stops matching the file it came from. The
    counts are checked against the canon's own «Сверка» line, which is its claim about itself."""
    canon = canon_audience()
    assert len(canon) == 56
    assert {handle: apply.AUDIENCE[handle] for handle in canon} == canon
    # Everything the script holds beyond the table is the regional row, spelled out.
    assert set(apply.AUDIENCE) - set(canon) == set(apply.CITY_FEEDS)
    assert {apply.AUDIENCE[handle] for handle in apply.CITY_FEEDS} == {"regional"}

    text = CANON.read_text(encoding="utf-8")
    assert "5+4+13+9+7+17+1 = 56" in " ".join(text[text.index("Сверка:") :][:120].split())
    sizes = {}
    for segment in canon.values():
        sizes[segment] = sizes.get(segment, 0) + 1
    assert sizes == {
        "retail_official": 5,
        "supermarket_deals": 4,
        "cooking_recipes": 13,
        "mothers_kids": 9,
        "baby_food": 7,
        "health_fitness": 17,
        "food_quality_gov": 1,
    }


def test_every_audience_value_is_one_of_the_eight():
    assert set(apply.AUDIENCE.values()) == set(AUDIENCES)


def test_a_channel_the_table_does_not_name_gets_no_audience_guessed_for_it():
    """ "The table is the law, no self-derived assignments" — so an unlisted channel stops the
    run rather than being sorted by what its name looks like."""
    with pytest.raises(SystemExit, match="no row in the audience table"):
        apply.audience_of("@some_new_channel")


def test_the_shipped_registry_carries_the_canons_audience_for_every_source():
    """Read by HANDLE: the four originals predate `source_entry` and their ids do not follow
    from their handles (@VARUS_channel is `varus`), so an id-keyed check would miss them."""
    sources = load_registry(REPO_ROOT / "config" / "registry.yaml").sources
    assert len(sources) == 56
    for src in sources:
        for handle in src.telegram_channels:
            assert src.audience == apply.AUDIENCE[handle], handle


def test_a_field_the_block_does_not_have_yet_is_inserted_inside_it(tmp_path):
    """`audience` had to reach 56 entries that had no such line. `_blocks` sweeps the removal
    comments that follow a source into the preceding block, so appending at the block's end would
    put the new field after a `# … removed …` comment — outside the entry it belongs to. The
    shipped file has that shape right after `maudau`."""
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    stripped = "\n".join(
        line for line in original.splitlines() if not line.startswith("    audience:")
    )
    assert "# uasaler removed" in stripped, "the case this test exists for is not in the file"

    written = apply.update_sources(stripped + "\n", {"maudau": {"audience": "supermarket_deals"}})
    block = written[written.index("  - id: maudau") : written.index("# uasaler removed")]
    assert "    audience: supermarket_deals\n" in block
    path = tmp_path / "registry.yaml"
    path.write_text(written, encoding="utf-8")
    by_id = {s.id: s for s in load_registry(path).sources}
    assert by_id["maudau"].audience == "supermarket_deals"
    assert by_id["retsepty"].audience is None, "the neighbour was not touched"


# --- a reversal says what it reversed ------------------------------------------------------------


def test_a_reversed_ruling_carries_what_it_replaced():
    """The record-integrity fix: overwriting `ruling` in place left the record reading as if the
    reversal had never happened, and only `git show` could say otherwise."""
    reversed_row = {**row("@somebody", "comments"), "ruling": "KEPT — measured next window"}
    apply.record_reversal(reversed_row, "EXCLUDED — off theme", "2026-08-08T10:00:00+00:00")
    assert reversed_row["replaced"] == [
        {"at": "2026-08-08T10:00:00+00:00", "ruling": "KEPT — measured next window"}
    ]


def test_an_unchanged_ruling_replaces_nothing():
    """Re-deriving the record is how it is verified, so a run that changes no ruling must add
    no history — otherwise `replaced` grows by one every verification."""
    same = {**row("@somebody", "posts"), "ruling": "KEPT — unchanged"}
    for _ in range(3):
        apply.record_reversal(same, "KEPT — unchanged", "2026-08-08T10:00:00+00:00")
    assert "replaced" not in same


def test_the_seed_puts_back_a_ruling_overwritten_before_replaced_existed_and_lands_once():
    """@discountua1's KEPT text was overwritten at 13b04e6. It is recovered from the record's own
    history — and the seed is a second write path, so it needs its own idempotence."""
    seeded = {**row("@discountua1", "comments"), "ruling": "EXCLUDED — text-free"}
    for _ in range(3):
        apply.record_reversal(seeded, "EXCLUDED — text-free", "2026-08-08T10:00:00+00:00")
    assert seeded["replaced"] == [apply.PRIOR_RULINGS["@discountua1"]]
    assert seeded["replaced"][0]["ruling"].startswith("KEPT — kept in the comments bucket")


def test_every_reversal_in_the_shipped_record_says_what_it_replaced():
    """The claim the operator asked for, checked against the artifact rather than the code: a row
    whose ruling reverses an earlier one carries that earlier one."""
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    reversed_rows = {
        candidate["handle"]: candidate["replaced"]
        for candidate in record["candidates"]
        if candidate.get("replaced")
    }
    assert set(reversed_rows) == {"@discountua1", "@uasaler"}
    for handle, history in reversed_rows.items():
        assert len(history) == 1, handle
        assert history[0]["ruling"].startswith("KEPT"), handle


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
        apply.source_entry(row("@epicentrk_sale", "posts"), "posts")["source_type"]
        == "official_retail"
    )
    assert (
        apply.source_entry(row("@retsepty", "comments"), "comments")["source_type"] == "community"
    )
    # @uasaler is excluded, so nothing builds an entry for it any more — its ruling stays in the
    # table as history, which is a claim about the dict rather than about the write.
    assert apply.SOURCE_TYPE_RULING["@uasaler"] == "aggregator"


def test_names_come_from_the_gate_record_not_from_the_canon_table():
    """The canon's table truncates its title cells; the record holds what Telegram returned."""
    entry = apply.source_entry(
        row("@poltava_misto", "city", title="Полтава Місто 👧 Новини"), "posts"
    )
    assert entry["name"] == "Полтава Місто 👧 Новини"
    assert entry["id"] == "poltava_misto"


# --- the write is additive ----------------------------------------------------------------------


def test_the_write_appends_sources_and_leaves_taxonomy_byte_identical(tmp_path, monkeypatch):
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    path = tmp_path / "registry.yaml"
    path.write_text(original, encoding="utf-8")
    monkeypatch.setattr(apply, "REGISTRY", path)

    # A city feed: named by the canon's regional row and not in the registry yet, so this is also
    # a rehearsal of the block "Дозаявка №3" will append once the gate has run.
    entries = [apply.source_entry(row("@kremenchug_live", "city", title="New 🥛"), "posts")]
    path.write_text(apply.insert_sources(original, entries), encoding="utf-8")

    written = path.read_text(encoding="utf-8")
    assert written.split("\ntaxonomy:\n", 1)[1] == original.split("\ntaxonomy:\n", 1)[1]
    after = load_registry(path)
    assert [s.id for s in after.sources[:4]] == [s.id for s in load_registry_text(original)][:4]
    assert after.sources[-1].id == "kremenchug_live"
    assert after.sources[-1].name == "New 🥛"
    assert after.sources[-1].comments_enabled is False, "a city feed is posts-only"
    assert after.sources[-1].audience == "regional"


def load_registry_text(text: str):
    """`load_registry` needs a path; the four ids are what this comparison is about."""
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as handle:
        handle.write(text)
    return load_registry(handle.name).sources


def test_a_removal_leaves_a_line_saying_why_and_cannot_reach_past_the_sources():
    """The draft of this function delimited a block by "the next `  - id:` line", which makes the
    LAST source's block run to the end of the file — taxonomy and watchlist included. It is
    bounded by the `taxonomy:` marker instead, and that is what this checks."""
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    last = load_registry(REPO_ROOT / "config" / "registry.yaml").sources[-1].id

    trimmed = apply.remove_sources(original, {last: "ruled out"})
    assert trimmed.split("\ntaxonomy:\n", 1)[1] == original.split("\ntaxonomy:\n", 1)[1]
    assert f"  # {last} removed 2026-08-07: ruled out\n" in trimmed
    after = load_registry_text(trimmed)
    assert last not in {s.id for s in after}
    assert len(after) == len(load_registry(REPO_ROOT / "config" / "registry.yaml").sources) - 1


def test_removing_a_source_that_is_not_there_stops_the_run():
    """A typo'd id must not pass for a removal that happened."""
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    with pytest.raises(SystemExit, match="which is not in it"):
        apply.remove_sources(original, {"nosuchsource": "ruled out"})
    assert apply.remove_sources(original, {}) == original


def test_a_run_with_nothing_new_leaves_the_file_byte_identical():
    """The re-run bug this exists for: with every channel already written the script had nothing
    to add and appended the section's comment header anyway, dirtying the registry by nine lines
    on a run whose whole job was to change nothing."""
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    assert apply.insert_sources(original, []) == original


def test_an_emoji_title_survives_the_yaml_round_trip(tmp_path):
    """Titles carry emoji, colons and quotes; a hand-rolled YAML writer is where those break."""
    nasty = 'Знижки: "супер" 💛 | все'
    entries = [apply.source_entry(row("@zinkivnews", "city", title=nasty, group=False), "posts")]
    original = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    path = tmp_path / "registry.yaml"
    path.write_text(apply.insert_sources(original, entries), encoding="utf-8")
    assert load_registry(path).sources[-1].name == nasty


# --- the counts are the canon's, not the script's -----------------------------------------------


def test_the_shipped_registry_is_re_derivable_from_the_gate_record():
    """The registry was written by this script, then amended by hand once (@marketopt_promo's
    source_type). A hand edit is exactly how a generated file and its generator start disagreeing
    in silence, so every entered channel is re-derived here and compared field by field.
    """
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    shipped = {
        handle: src
        for src in load_registry(REPO_ROOT / "config" / "registry.yaml").sources
        for handle in src.telegram_channels
    }
    checked = 0
    for candidate, bucket in resolved(record):
        if bucket is None:
            assert candidate["handle"] not in shipped, "an excluded channel is in the registry"
            continue
        expected = apply.source_entry(candidate, bucket)
        got = shipped[candidate["handle"]]
        assert (got.id, got.name, got.source_type, got.comments_enabled, got.watch) == (
            expected["id"],
            expected["name"],
            expected["source_type"],
            expected["comments_enabled"],
            expected["watch"],
        ), candidate["handle"]
        checked += 1
    assert checked == 52


def test_the_composition_matches_the_canons_own_summary():
    """`docs/CHANNELS-launch.md` states the post-ruling summary in prose. If the script and the
    canon disagree about how many channels launch, the script is wrong by definition."""
    text = CANON.read_text(encoding="utf-8")
    # The canon hard-wraps its prose; the claim is about the numbers, not the line breaks.

    # Wave 1, kept because the canon keeps it: the composition as it stood on 07.08 midday.
    wave1 = " ".join(text[text.index("**Сводка после рулингов") :][:400].split())
    assert "запуск 47" in wave1
    assert "реестр 4 + 26 комментных + 17 постовых" in wave1
    assert "+ 1 на гейте** (@marketopt_promo)" in wave1

    # Wave 2 — the summary the registry now has to match.
    wave2 = " ".join(text[text.index("**Сводка: запуск 42**") :][:300].split())
    assert "**Сводка: запуск 42** (реестр 4 + 21 комментный + 17 постовых)" in wave2
    assert "watch 14" in wave2
    assert "**реестр 56**" in wave2

    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    buckets = {"comments": 0, "posts": 0, "watch": 0, "excluded": 0}
    for _, bucket in resolved(record):
        buckets["excluded" if bucket is None else bucket] += 1
    assert buckets["comments"] == 21
    assert buckets["watch"] == 14
    assert buckets["posts"] == 17
    # Six by 07.08 midday, the five the theme screen caught that evening (@znishkom,
    # @whitecode_zny, @offspringrus off-topic; @discountua1, @ATB_FANatik text-free), and
    # @uasaler, demoted on 07.08 and excluded outright by the wave-2 ruling.
    assert buckets["excluded"] == 12
    assert 4 + buckets["comments"] + buckets["posts"] == 42
