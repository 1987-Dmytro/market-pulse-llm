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
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_gate_rulings_5c1 as apply  # noqa: E402

from moved_pins import composition_before_r2  # noqa: E402
from market_pulse.registry import registry_before_r2  # noqa: E402

from market_pulse.registry import AUDIENCES, load_registry  # noqa: E402

CANON = REPO_ROOT / "docs" / "CHANNELS-launch.md"


def canon_retail_5() -> list[str]:
    """The three national chains "Дозаявка №5" sends to the gate, read out of the master list.

    Parsed here rather than imported from tests/test_entry_gate_5c1.py, which has the same
    reader: a test module that imports another test module cannot be checked out on its own, and
    the commit that introduced this file could not run its own suite because of it. Five lines of
    duplication buy a file that stands up alone — the same trade `canon_audience` below makes.
    """
    import re

    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## МАСТЕР-ЛИСТ") :]
    listing = section[section.index("Дозаявка №5 на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing[: listing.index("\n**")])


RETAIL_5 = canon_retail_5()
"""The three national chains of "Дозаявка №5", parsed from the canon rather than retyped."""


def canon_harvest_6() -> list[str]:
    """The six public candidates of "Дозаявка №8", cut at the deferred privates track."""
    import re

    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Дозаявка №8") :]
    return re.findall(r"@[A-Za-z0-9_]+", section[: section.index("Приватные гиганты")])


HARVEST_6 = canon_harvest_6()


def canon_city_topup() -> list[str]:
    """ "Дозаявка №9"'s one handle, parsed here too rather than imported from the gate's test."""
    import re

    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Рулинги гейта дня 2") :]
    listing = section[section.index("хендл на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing.split("\n\n")[0])


CITY_TOPUP = canon_city_topup()


def canon_city_analogues() -> list[str]:
    """ "Дозаявка №10"'s four broadcast city feeds, parsed here too rather than imported."""
    import re

    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Дозаявка №10") :]
    listing = section[section.index("городских хендла на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing.split("\n\n")[0])


def canon_mothers_topup() -> list[str]:
    """ "Дозаявка №10"'s two handle top-ups, resolved from TGStat titles by the step-7 search."""
    import re

    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Дозаявка №10") :]
    listing = section[section.index("хендла матерей на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing.split("\n\n")[0])


CITY_ANALOGUES = canon_city_analogues()
MOTHERS_TOPUP = canon_mothers_topup()

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
    gated = row("@poltava_informue", "city", group=True, open_group=True)
    bucket, ruling = apply.final_bucket(gated)
    assert bucket == "posts"
    assert "POSTS-ONLY" in ruling and "5c2" in ruling
    entry = apply.source_entry(gated, bucket)
    assert entry["comments_enabled"] is False
    assert entry["watch"] is False
    assert entry["source_type"] == "community"


def test_a_city_feed_that_did_not_pass_is_not_routed_by_its_bucket():
    """ "FAIL or FLAG → report with evidence, do not resolve yourself" — the refusal is what
    enforces it, and a city row must not slip past on the strength of the ruling.

    Asked of a city feed the day-2 sitting did NOT clear: @gorishnie_plavni1 and @zinkivnews
    would pass this on their clearance, which is the difference the clearance is supposed to
    make."""
    for verdict in ("FAIL", "FLAG"):
        with pytest.raises(SystemExit, match="no ruling covers it"):
            apply.final_bucket(row("@poltava_informue", "city", verdict=verdict))


def test_a_city_row_the_ruling_does_not_name_refuses_to_enter():
    """The bucket is a label the gate wrote; the ruling is what authorises an entry. A 17th city
    handle appearing in the gate must not enter on the label alone."""
    with pytest.raises(SystemExit, match="CITY_FEEDS does not name it"):
        apply.final_bucket(row("@some_new_town", "city"))


# --- the day-2 sitting, 2026-08-08 ---------------------------------------------------------------


def test_the_three_supergroups_leave_and_the_gate_row_is_why():
    """Three of "Дозаявка №3"'s sixteen are chats, so their posts/week is member traffic. The
    ruling is checked against the measurement it cites rather than against its own wording."""
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text("utf-8"))
    rows = {r["handle"]: r for r in record["candidates"]}
    for handle in ("@poltava_misto", "@kremenchug_live", "@Karlivka_live"):
        bucket, ruling = apply.final_bucket(row(handle, "city", verdict="FLAG"))
        assert bucket is None and "supergroup" in ruling, handle
        assert rows[handle]["checks"]["megagroup"] is True, handle
        assert rows[handle]["checks"]["broadcast"] is False, handle


def test_the_dead_chain_leaves_on_the_same_conjunction_as_the_last_one():
    """@tadaua is the team lead's own suggestion in "Дозаявка №5" and the gate killed it: 71
    subscribers, last post 2025-01-02. The ruling names @akcii_skidki_plt, the precedent."""
    bucket, ruling = apply.final_bucket(row("@tadaua", "late", verdict="FAIL"))
    assert bucket is None
    assert "@akcii_skidki_plt" in ruling and "2025-01-02" in ruling


def test_a_cleared_flag_enters_by_the_rule_that_was_already_written():
    """The clearance does not invent a bucket — it lets the standing rule route the row. Both
    pairs land in posts-only: the city rule for the two feeds, LATE_RULE for the two additions."""
    for handle in ("@gorishnie_plavni1", "@zinkivnews"):
        bucket, ruling = apply.final_bucket(
            row(handle, "city", verdict="FLAG", group=True, open_group=False)
        )
        assert bucket == "posts", handle
        assert "POSTS-ONLY" in ruling and "FLAG CLEARED" in ruling, handle
    for handle in ("@tvorcha_matusyua", "@educationwithloven"):
        bucket, ruling = apply.final_bucket(
            row(handle, "late", verdict="FLAG", group=True, open_group=False)
        )
        assert bucket == "posts", handle
        assert "no discussion group" in ruling and "FLAG CLEARED" in ruling, handle


def test_a_clearance_covers_a_flag_and_never_a_fail():
    """A FAIL says the channel cannot be collected at all; overriding that is a bucket change, not
    a clearance. Without this the four entries would quietly cover a future FAIL on the same row."""
    for handle in apply.CLEARED:
        with pytest.raises(SystemExit):
            apply.final_bucket(row(handle, "city", verdict="FAIL"))


def test_the_clearance_leaves_the_measurement_alone():
    """The gate row still says FLAG. The clearance is a ruling ABOUT a finding, and a run that
    rewrote the finding would leave nothing to disagree with it."""
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text("utf-8"))
    rows = {r["handle"]: r for r in record["candidates"]}
    for handle in apply.CLEARED:
        assert rows[handle]["verdict"] == "FLAG", handle
        assert rows[handle]["flags"], handle


def test_the_quiet_harvest_candidate_enters_watch_and_buys_no_join():
    """0 posts in the window is what failed it; 49 posts to 2026-06-04 is why it is not dead.
    watch is that state exactly — collected, never joined."""
    gated = row("@lab_of_childhood", "late", verdict="FAIL", group=False)
    bucket, ruling = apply.final_bucket(gated)
    assert bucket == "watch"
    assert "2026-06-04" in ruling and "NEVER joined" in ruling
    entry = apply.source_entry(gated, bucket)
    assert entry["watch"] is True
    assert entry["comments_enabled"] is False
    assert entry["audience"] == "mothers_kids"


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
    # The canon amends rather than rewrites: wave 3 renamed a segment in its own section while
    # the table above still spells the old value. Applying the rename here — parsed from the
    # canon too, never typed — keeps "the table is the law" true of the whole file rather than
    # of its oldest section.
    for old, new in re.findall(r"`([a-z_]+)` переименован в `([a-z_]+)`", text):
        table = {handle: (new if segment == old else segment) for handle, segment in table.items()}
    return table


def test_the_audience_table_is_the_canons_own():
    """A hand-copied 56-row table is a table that stops matching the file it came from. The
    counts are checked against the canon's own «Сверка» line, which is its claim about itself."""
    canon = canon_audience()
    assert len(canon) == 56
    assert {handle: apply.AUDIENCE[handle] for handle in canon} == canon
    # Beyond the table: the regional row spelled out, and the three chains of "Дозаявка №5" —
    # which the table does NOT name, because it was written before them. Their segment comes from
    # the operator's brief and the master list, and the count line below is stale by three the
    # moment they pass; that is a mismatch for the canon's author, not for this script.
    assert set(apply.AUDIENCE) - set(canon) == set(apply.CITY_FEEDS) | set(RETAIL_5) | set(
        HARVEST_6
    ) | set(MOTHERS_TOPUP)
    assert {apply.AUDIENCE[handle] for handle in apply.CITY_FEEDS} == {"regional"}
    assert {apply.AUDIENCE[handle] for handle in RETAIL_5} == {"retail_official"}
    # The harvest six carry the segments PROMPT-5c1-day2 assigns; two of them are expectations
    # the canon leaves to the gate, which is why they are here and not in the segmentation table.
    assert {apply.AUDIENCE[handle] for handle in HARVEST_6} == {
        "baby_food",
        "mothers_kids",
        "health_fitness",
    }

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
        "food_quality": 1,
    }


def test_the_city_rows_of_the_audience_table_are_the_gates_own():
    """The 16 regional rows are written out one per line so a reader sees where each came from.
    Spelling them out means the same handles now live in two places, so this is what keeps them
    from drifting: same handles, same order, and `regional` for every one of them."""
    regional = [handle for handle, segment in apply.AUDIENCE.items() if segment == "regional"]
    assert regional == list(apply.CITY_FEEDS)
    assert len(regional) == 16 + len(CITY_TOPUP) + len(CITY_ANALOGUES)


def test_the_titles_beside_the_city_rows_are_the_scans_own():
    """Provenance is the reason those comments exist, so it is checked rather than trusted: each
    title is compared against `results/discovery_5c1_poltava.json`, the record the operator
    picked from. A title typed from memory is a comment that quietly stops being true."""
    import re

    ledger = json.loads(
        (REPO_ROOT / "results" / "discovery_5c1_poltava.json").read_text(encoding="utf-8")
    )
    titles = {row["handle"]: row["title"] for row in ledger["candidates"]}

    # "Дозаявка №9"'s row is the one the scan cannot answer for — it never returned the handle.
    # Its title is checked against the record that DID produce it: the gate's group finding on the
    # supergroup it replaces. A row with neither provenance is what this test is here to catch.
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text("utf-8"))
    replaced = next(r for r in record["candidates"] if r["handle"] == "@Karlivka_live")
    titles["@KarlivkaLive"] = replaced["checks"]["discussion_group"]["title"]
    assert "@KarlivkaLive" not in {row["handle"] for row in ledger["candidates"]}

    # "Дозаявка №10"'s four came from step 7's searches, a third record again. Each source is
    # named rather than merged into one pool: "where did this title come from" is the question,
    # and a row whose provenance is nowhere must not borrow another row's.
    for key in ("poltava_broadcast_analogue", "kremenchuk_broadcast_analogue"):
        for match in record["notes"][key]["name_matches"]:
            titles.setdefault(f"@{match['username']}", match["title"])
    # Three of the four were NOT in the 119-candidate town-name scan at all — @h_kremenchug is
    # 137,221 subscribers and the scan never returned it. Worth pinning rather than passing over:
    # it is the measured reason the operator's step-7 addition was not a duplicate of the scan.
    scanned = {row["handle"] for row in ledger["candidates"]}
    assert sorted(set(CITY_ANALOGUES) - scanned) == [
        "@h_kremenchug",
        "@kremen_news",
        "@poltava20",
    ]

    source = (REPO_ROOT / "scripts" / "apply_gate_rulings_5c1.py").read_text(encoding="utf-8")
    annotated = dict(re.findall(r'"(@[A-Za-z0-9_]+)": "regional",\s+# (.+)', source))
    assert set(annotated) == set(apply.CITY_FEEDS), "a city row lost its provenance comment"
    for handle, comment in annotated.items():
        assert comment == titles[handle], handle


def test_the_words_beside_the_retail_rows_are_the_canons_own():
    """Same instrument as the city rows, a different source: these three came from the master
    list, so each comment is grepped back to it. Only the segment comes from elsewhere — the
    segmentation table predates them and still counts retail_official as five."""
    import re

    source = (REPO_ROOT / "scripts" / "apply_gate_rulings_5c1.py").read_text(encoding="utf-8")
    annotated = dict(re.findall(r'"(@[A-Za-z0-9_]+)": "retail_official",[ \t]+# (.+)', source))
    assert set(annotated) == set(RETAIL_5), "a retail row lost its provenance comment"

    text = CANON.read_text(encoding="utf-8")
    master = " ".join(text[text.index("## МАСТЕР-ЛИСТ") :].split())
    for handle, comment in annotated.items():
        assert " ".join(comment.split()) in master, handle


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
    # The composition the canon's table was written for. Revision r2 (2026-08-30) added eight A1
    # sources and `docs/CHANNELS-launch.md` names none of them — «the table is the law, no
    # self-derived assignments» cuts both ways, so an r2 row is not silently graded against a table
    # that never claimed it. What r2's rows carry is asserted in `tests/test_registry.py`.
    sources = composition_before_r2().sources
    assert len(sources) == 66
    for src in sources:
        for handle in src.telegram_channels:
            assert src.audience == apply.AUDIENCE[handle], handle
    live = load_registry(REPO_ROOT / "config" / "registry.yaml").sources
    assert len(live) == 74, "r2 is why this is counted on the pre-r2 composition"
    assert all(src.audience in AUDIENCES for src in live), "and every r2 row still has one"


def test_a_field_the_block_does_not_have_yet_is_inserted_inside_it(tmp_path):
    """`audience` had to reach 56 entries that had no such line. `_blocks` sweeps the removal
    comments that follow a source into the preceding block, so appending at the block's end would
    put the new field after a `# … removed …` comment — outside the entry it belongs to. The
    shipped file has that shape right after `maudau`."""
    # The r1 bytes, not today's: the fixture is "this file before it had an `audience` field", and
    # revision r2's own three fields would otherwise sit in the block being tested and move the
    # insertion point this test exists to pin.
    original = registry_before_r2(REPO_ROOT / "config" / "registry.yaml").decode("utf-8")
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
    assert set(reversed_rows) == {"@discountua1", "@uasaler", "@prostetsofa", "@dikankaa"}
    for handle, history in reversed_rows.items():
        assert len(history) == 1, handle
    # Three of the four reversed a KEPT. @dikankaa reversed a PLACEMENT — it had already entered
    # as a city feed when the day-2 acceptance ruled it out on the census — and pinning the shape
    # is what keeps "a reversal is always a kept channel losing its keep" from being read into a
    # test that never said it.
    assert {
        handle: history[0]["ruling"].split(" ")[0] for handle, history in reversed_rows.items()
    } == {
        "@uasaler": "KEPT,",
        "@discountua1": "KEPT",
        "@prostetsofa": "KEPT",
        "@dikankaa": "CITY",
    }


def test_the_replacement_lands_by_the_rule_the_operator_wrote_in_advance():
    """Ruling 4, both branches — the gate's finding picks the bucket, not a later judgement."""
    with_group = row("@marketopt_promo", "late", group=True, open_group=True)
    assert apply.final_bucket(with_group)[0] == "comments"
    without = row("@marketopt_promo", "late", group=False)
    assert apply.final_bucket(without)[0] == "posts"
    assert apply.source_entry(without, "posts")["comments_enabled"] is False


def test_a_national_chain_routes_by_the_group_finding_like_any_late_addition():
    """ "Comments per the group finding" (operator, «Дозаявка №5») is the late-addition rule that
    was already written, so the three chains enter through it rather than through a new one.

    Asked of the chains the rule still routes. @tadaua came back FAIL at the day-2 gate and left
    on a ruling, so the rule no longer reaches it — asserted below rather than dropped, because a
    handle silently falling out of a loop is how a rule stops being tested.
    """
    assert set(RETAIL_5) <= set(apply.GATED_LATE)
    routed = [handle for handle in RETAIL_5 if handle not in apply.EXCLUDED]
    assert routed == ["@forainfo", "@ekomarket_shop"], routed
    for handle in routed:
        with_group = row(handle, "late", group=True, open_group=True)
        assert apply.final_bucket(with_group)[0] == "comments"
        assert apply.final_bucket(row(handle, "late", group=False))[0] == "posts"
        with pytest.raises(SystemExit, match="stop and report"):
            apply.final_bucket(row(handle, "late", verdict="FLAG"))
    assert apply.final_bucket(row("@tadaua", "late", verdict="FAIL"))[0] is None


def test_no_retail_official_source_enters_as_a_community_channel():
    """Audience and source_type answer different questions — «whose audience» and «who runs it» —
    but every source the canon segments as retail_official is a chain's own channel, and the
    shipped file has `official_retail` on all five. A sixth entering as `community` would be the
    default speaking where a fact was known; @marketopt_promo needed exactly that amendment after
    its write, and this is the same amendment made before one."""
    retail = [h for h, segment in apply.AUDIENCE.items() if segment == "retail_official"]
    assert len(retail) == 8, retail
    for handle in ("@forainfo", "@ekomarket_shop", "@tadaua"):
        assert apply.source_type_of(handle) == "official_retail", handle

    # The negative control, without which the loop above only reads back the dict it is checking:
    # the same handle with its ruling row removed must STOP the run, not fall back to the default.
    without = {k: v for k, v in apply.SOURCE_TYPE_RULING.items() if k != "@forainfo"}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(apply, "SOURCE_TYPE_RULING", without)
    try:
        with pytest.raises(SystemExit, match="would enter as `community`"):
            apply.source_type_of("@forainfo")
        # And the guard is about the segment, not about the handle: a source outside
        # retail_official still takes the ruling's own default.
        assert apply.source_type_of("@kopiyochka1") == "community"
    finally:
        monkeypatch.undo()

    shipped = {
        channel: source.source_type
        for source in load_registry(REPO_ROOT / "config" / "registry.yaml").sources
        for channel in source.telegram_channels
    }
    for handle in retail:
        if handle in shipped:
            # Including the three originals hand-written before this script existed, which never
            # pass through `source_entry` and so carry no ruling row.
            assert shipped[handle] == "official_retail", handle


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


def test_a_second_apply_run_does_not_write_a_second_section_header():
    """Three runs on 2026-08-08 left three identical banners in `config/registry.yaml`, each
    dated for a sitting that was not the one below it. The rows were right and the caption was
    not — and a caption that describes the wrong sitting is worse than none, because a reader
    six weeks from now takes it for provenance."""
    shipped = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    banner = apply.HEADER.splitlines()[0]
    assert shipped.count(banner) == 1, "the shipped file carries the banner more than once"

    entries = [apply.source_entry(row("@poltava_misto", "city", title="X", group=False), "posts")]
    assert apply.insert_sources(shipped, entries).count(banner) == 1

    # The negative control, without which this only proves the banner is never written: a file
    # that does not carry it yet gets exactly one.
    fresh = shipped.replace(apply.HEADER + "\n", "")
    assert banner not in fresh
    assert apply.insert_sources(fresh, entries).count(banner) == 1


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
    # A handle the AUDIENCE table names and the registry never will: @poltava_misto left as a
    # supergroup at the day-2 sitting. The earlier pick, @zinkivnews, entered the registry at the
    # same sitting and the round trip then failed on a duplicate id instead of on the quoting.
    entries = [apply.source_entry(row("@poltava_misto", "city", title=nasty, group=False), "posts")]
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
    # Against the pre-r2 composition: this gate wrote 62 entries and EXCLUDED others, and revision
    # r2 later brought one of the excluded back — @znishkom entered A1 on the operator's 30.08 list.
    # Checking «an excluded channel is in the registry» against today's file would read that ruling
    # as this gate's own record having drifted ([[the_field_true_under_the_old_constant]]).
    shipped = {
        handle: src
        for src in composition_before_r2().sources
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
    assert checked == 62


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

    # Wave 3 — the summary the registry has to match NOW. The wave-2 numbers above are kept
    # because the canon keeps them: an amended file is a history, not a latest-value store.
    wave3 = " ".join(text[text.index("**Сводка после волны 3") :][:300].split())
    assert "**Сводка после волны 3: реестр 41 = запуск 33 + watch 8.**" in wave3
    assert "боевых **0**" in wave3, "the launch mothers segment is empty and the canon says so"

    # The top-up amends that summary in its own section — two RU-titled watch channels the team
    # lead's table had missed. The wave-3 line above is kept because the canon keeps it.
    topup = " ".join(text[text.index("**Волна 3, добор") :][:400].split())
    assert "**реестр 39 = запуск 33 + watch 6**" in topup
    assert "исключено за фазу 29" in topup

    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    buckets = {"comments": 0, "posts": 0, "watch": 0, "excluded": 0}
    for _, bucket in resolved(record):
        buckets["excluded" if bucket is None else bucket] += 1
    # The day-2 sitting: 25 new candidates plus "Дозаявка №9"'s replacement. The wave-3 line above
    # is kept because the canon keeps it — an amended file is a history, not a latest-value store.
    day2 = " ".join(text[text.index("**Сводка после дня 2") :][:420].split())
    assert "**Сводка после дня 2: реестр 61 = запуск 54 + watch 7.**" in day2
    assert "комментных 16, постовых 34" in day2
    assert "Исключено за фазу **33**" in day2
    # And what step 7's own findings then added on top of it, in its own section for the same
    # reason every wave has one: the canon amends, it does not restate.
    ten = " ".join(text[text.index("**Сводка после дозаявки №10") :][:400].split())
    assert "Сводка после дозаявки №10: реестр 67 = запуск 60 + watch 7." in ten
    assert "Комментных 18" in ten and "постовых 38" in ten
    # And the acceptance that closed the day: one exclusion on the census, so the composition the
    # registry has to match now is 66. Same amend-never-restate rule as every wave above.
    accepted = " ".join(text[text.index("**Сводка после приёмки дня 2") :][:300].split())
    assert "**Сводка после приёмки дня 2: реестр 66 = запуск 59 + watch 7.**" in accepted
    assert "исключено за фазу **34**" in accepted
    assert "боевых mothers_kids 3" in ten
    assert "боевой **1** (@educationwithloven)" in day2, "the mothers segment stopped being empty"
    provisional = " ".join(text[text.index("**Весь дифф реестра дня 2") :][:400].split())
    assert "PROVISIONAL pending yield screen" in provisional

    assert buckets["comments"] == 18
    assert buckets["watch"] == 7
    assert buckets["posts"] == 37
    # Six by 07.08 midday, the five the theme screen caught that evening (@znishkom,
    # @whitecode_zny, @offspringrus off-topic; @discountua1, @ATB_FANatik text-free), @uasaler by
    # wave 2, wave 3's fifteen — 3 on the census, 1 on market-origin evidence, 11 on RU titles —
    # the day-2 four (three supergroups and one dead chain), and @dikankaa on the acceptance.
    assert buckets["excluded"] == 34
    # The four originals are out of the gate's scope, so they are added here rather than counted.
    # None of the fifteen was one of them: @tretyakovaele was gated in 5c1 like the rest.
    assert 4 + buckets["comments"] + buckets["posts"] == 59
    assert 4 + buckets["comments"] + buckets["posts"] + buckets["watch"] == 66


# --- the day-2 acceptance (operator, 2026-08-08 evening) ------------------------------------------


def test_dikankaa_leaves_on_the_census_and_its_evidence_leaves_with_it():
    """House style: a silently shorter registry cannot be told from one that never had the
    channel. So the exclusion carries the operator's own words AND the artifact that holds half
    of them — the census reading — into the comment the removal leaves behind."""
    bucket, ruling = apply.final_bucket(row("@dikankaa", "city"))
    assert bucket is None
    assert "ru 1.00 on 20 decidable posts" in ruling
    assert "UA-only policy" in ruling

    text = (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8")
    assert "\n  - id: dikankaa\n" not in text
    line = next(ln for ln in text.splitlines() if ln.startswith("  # dikankaa removed"))
    assert "2026-08-08" in line
    assert "language_census_5c1_day2.json" in line
    # The half the operator saw and no artifact here holds — said out loud rather than dropped.
    assert "the gate stores title, not bio" in line


def test_the_closed_group_ruling_covers_the_class_and_names_only_its_four():
    """Option 1 of the menu: the flag concerns a capability the assigned bucket does not use.

    A ruling about a CLASS has to be checkable against the rows in it, or the next channel of the
    same shape is cleared by resemblance. @KarlivkaLive carries the identical flag and is out of
    the tuple on purpose — it was ruled separately as «Дозаявка №9», and folding it in would make
    one ruling look like it had covered five.
    """
    record = json.loads((REPO_ROOT / "results" / "entry_gate_5c1.json").read_text(encoding="utf-8"))
    rows = {candidate["handle"]: candidate for candidate in record["candidates"]}
    for handle in apply.CLOSED_GROUP_FLAG["channels"]:
        assert handle in apply.CLEARED, handle
        assert rows[handle]["verdict"] == "FLAG", handle
        assert rows[handle]["flags"] == ["discussion group is not open — join needs admin approval"]
    assert "@KarlivkaLive" not in apply.CLOSED_GROUP_FLAG["channels"]
    assert rows["@KarlivkaLive"]["flags"] == rows["@zinkivnews"]["flags"]
    assert record["rulings"]["closed_group_flag"]["reading"].startswith("the flag concerns")


def test_the_three_rf_flags_are_kept_with_their_reading_on_the_row():
    """«RF 0 on the live 39» is quoted in STATUS; three flags arrived on 08.08 and all three are
    one war report. The ruling lives on the rows, so the zero cannot rot into a number whose
    explanation is only in prose somewhere."""
    screen = json.loads(
        (REPO_ROOT / "results" / "market_screen_5c1_day2.json").read_text(encoding="utf-8")
    )
    ruled = {row["handle"]: row["ruling"] for row in screen["sources"] if row.get("ruling")}
    assert set(ruled) == {"@myrhorodtown", "@poltava_informue", "@poltava20"}
    live = {
        handle
        for source in load_registry(REPO_ROOT / "config" / "registry.yaml").sources
        for handle in source.telegram_channels
    }
    for handle, ruling in ruled.items():
        assert ruling.startswith("KEPT — war-news-explained")
        assert handle in live, f"{handle} was ruled KEPT and is not in the registry"
