"""Validation tests for the source registry loader."""

from hashlib import sha256
from pathlib import Path

import pytest
from market_pulse.brands import watchlist_aliases
from market_pulse.registry import (
    AUDIENCES,
    load_registry,
    load_registry_as_pinned,
    load_registry_text,
    registry_before_r2,
    registry_before_the_latin_aliases,
)

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "registry.yaml"

SIGNED_SCREEN_REGISTRY_SHA = "c82d0cff1ee7d1bbf7c40d46bbcb02662f44898e4bc6980a2d75ced9cce46a2e"
"""The registry bytes `results/yield_screen_5c1.json` read — the composition the operator signed.

That screen is never re-run (`yield_screen_5c1.refuse_to_overwrite`), so the sha it cites is
frozen at the file as it stood before the 2026-08-10 signature stamp. Same shape as
`results/sitting_45g2_manifest.json`, which also stopped matching the corpus it pins: the sealed
record describes what it read, the divergence is declared rather than re-pinned, and
:func:`registry_as_the_signed_screen_read_it` is where the chain to today's bytes is written down.

The chain has TWO links now. 2026-08-10 added the signature stamp, a comment block that moved no
row; 2026-08-12 added the three Latin aliases of SPEC 3.17 (13)(b), which DO move three rows and
are ratified. Each link is undone by its own function, and the enumeration of what (13)(b) touched
is literal in `market_pulse.registry` so a third link cannot land here unseen."""

PRE_13B_REGISTRY_SHA = "920c7f203b9f0e38fd8df9e893d9b15705a6b19b297bd9d14b14258ae38ac3be"
"""The bytes the sku pre-registrations v1–v4, the leaflet gold and the pre-filter census all pin —
today's file with r2 and then the (13)(b) aliases undone, and the stamp still in it. Eight records
carry this sha."""

R1_REGISTRY_SHA = "d4e3b2373c4378f3acc51079dc1d0560c28d58c46b71335b2bb352cae39be3ba"
"""The registry as it stood before revision r2 — the third link, added 2026-08-30.

Seven records pin these bytes: `census_5c2`, `census_c3a_posts`, `dashboard_data_w1`,
`gate_census_w1`, `gate_census_w1_reader`, `prereg_5c2_run` and `sku_pilot_prereg_b2`. They were
the LIVE sha until r2 added eight A1 sources and paused 39 rows, and they are not re-pinned: the
undo is written down in `market_pulse.registry.registry_before_r2` and nailed to this constant
below. Without that, `load_registry_as_pinned` would refuse for all seven and the four producers
that recompute a sealed bar through it would stop."""

STAMP_OPENS = "  # SIGNED 2026-08-10"
STAMP_CLOSES = "sitting-2026-08-10-composition-signed.md"


def registry_without_the_signature_stamp(text: str | None = None) -> bytes:
    """A registry minus the 2026-08-10 operator stamp — today's file unless `text` says otherwise.

    The stamp is a comment block: it changes no row, and it does move the file's sha256. Stripping
    it back out is what makes "nothing but the signature moved" a checkable claim instead of a
    sentence in a commit message.
    """
    source = REGISTRY.read_text(encoding="utf-8") if text is None else text
    lines = source.splitlines(keepends=True)
    opens = [i for i, line in enumerate(lines) if line.startswith(STAMP_OPENS)]
    closes = [i for i, line in enumerate(lines) if STAMP_CLOSES in line]
    assert len(opens) == len(closes) == 1, "the signature stamp is one block, written once"
    start, end = opens[0], closes[0]
    assert lines[start - 1] == "  #\n", "the stamp is set off by a bare comment line"
    return "".join(lines[: start - 1] + lines[end + 1 :]).encode("utf-8")


def registry_as_the_signed_screen_read_it() -> bytes:
    """Both links of the chain, oldest last: undo (13)(b), then take the signature stamp off."""
    before = registry_before_the_latin_aliases(REGISTRY).decode("utf-8")
    return registry_without_the_signature_stamp(before)


SOURCES = (
    "sources:\n"
    "  - id: a\n    name: A\n    source_type: official_retail\n"
    "    telegram_channels: ['@chan_one']\n"
)
TAXONOMY = "taxonomy:\n  tracked_groups:\n    dairy:\n      name: Молочні продукти\n"


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "registry.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_shipped_registry_loads():
    registry = load_registry(REGISTRY)
    assert registry.sources
    assert all(s.telegram_channels for s in registry.sources)
    assert len({s.id for s in registry.sources}) == len(registry.sources)
    assert registry.taxonomy.tracked_groups
    assert any(b.own for b in registry.watchlist)
    # Reactions must be readable somewhere, or T1 has no input at all (SPEC §9).
    assert any(s.comments_enabled for s in registry.sources)


def test_comments_enabled_defaults_to_false(tmp_path):
    # A source added before its entry check must not claim it carries comments.
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].comments_enabled is False


def test_watch_defaults_to_false(tmp_path):
    # The default has to be "collect normally": a launch channel that silently read as watch
    # would be dropped from the joins with nothing to see it.
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].watch is False


def test_watch_is_read_and_must_be_a_boolean(tmp_path):
    """`watch: "no"` is truthy in Python, and a launch channel read as watch loses its join."""
    body = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    watch: true\n")
    assert load_registry(write(tmp_path, body + TAXONOMY)).sources[0].watch is True

    bad = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    watch: 'no'\n")
    with pytest.raises(ValueError, match="non-boolean watch"):
        load_registry(write(tmp_path, bad + TAXONOMY))


def test_audience_defaults_to_none_and_is_a_closed_list(tmp_path):
    """The eight segments are the canon's; a ninth would silently make its own bucket in every
    aggregate 5c2 keys on this field and read as an audience nobody chose."""
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].audience is None

    good = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    audience: baby_food\n")
    assert load_registry(write(tmp_path, good + TAXONOMY)).sources[0].audience == "baby_food"

    bad = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    audience: mums\n")
    with pytest.raises(ValueError, match="unknown audience"):
        load_registry(write(tmp_path, bad + TAXONOMY))


def test_every_shipped_source_carries_an_audience():
    """The 08.08 ruling covers all 56, so a null here is a source no aggregate can attribute."""
    sources = load_registry(REGISTRY).sources
    assert [s.id for s in sources if s.audience is None] == []
    assert set(AUDIENCES) >= {s.audience for s in sources}


def test_government_is_a_source_type(tmp_path):
    """@dpssgovua, Держпродспоживслужба — a state inspectorate is neither retail, aggregator
    nor community, and the 5c1 registry write needed a fourth value (team-lead, 2026-08-07)."""
    body = SOURCES.replace("source_type: official_retail", "source_type: government")
    assert load_registry(write(tmp_path, body + TAXONOMY)).sources[0].source_type == "government"


def test_duplicate_source_id_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n"
        "  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['@chan_one']\n"
        "  - id: a\n    name: A again\n    source_type: aggregator\n"
        "    telegram_channels: ['@chan_two']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="duplicate source id"):
        load_registry(path)


def test_source_without_channels_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: []\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="no telegram_channels"):
        load_registry(path)


def test_an_invite_hash_and_a_bare_chat_id_are_accepted_handles(tmp_path):
    """Revision r2's two A1 entries that are not public usernames, and cannot be written otherwise.

    Маркетопт's private channel is an invite hash (`results/retail_chains.json` records its kind as
    `invite`) and @ATB_FANatik's discussion group «АТБ / ЗНИЖКИ» has `username: null` and only an id
    (`results/retail_census.json`). The group is a second channel on the FANatik row rather than a
    row of its own — it is the same source, read through two feeds.
    """
    body = (
        "sources:\n"
        "  - id: marketopt_private\n    name: Маркетопт\n    source_type: official_retail\n"
        "    telegram_channels: ['+Ejz6ubzm21IyMTQy']\n"
        "  - id: atb_fanatik\n    name: ФАНАТИК АТБ\n    source_type: aggregator\n"
        "    telegram_channels: ['@ATB_FANatik', '1925810730']\n" + TAXONOMY
    )
    registry = load_registry(write(tmp_path, body))
    assert [source.telegram_channels for source in registry.sources] == [
        ("+Ejz6ubzm21IyMTQy",),
        ("@ATB_FANatik", "1925810730"),
    ]


@pytest.mark.parametrize(
    "handle",
    [
        "chan_without_at",  # the one the username rule already refused
        "@four",  # 4 characters after the @ — a username is 5 and up
        "+Ejz6ubzm21IyMT",  # 15 — an invite hash is 16 and up
        "19258",  # 5 digits — a chat id is 6 and up
        "@ATB FANatik",  # a space is in none of the three
        "+Ejz6ubzm21IyMTQy@x",  # an invite with something appended
    ],
)
def test_the_widened_handle_still_refuses_what_is_none_of_the_three(tmp_path, handle):
    """The half a widened regex can lose. Each row sits one character outside its own branch, so a
    branch that had been written open-ended would fail here rather than in a silent empty
    collection ([[guard_selftest_negative_control]])."""
    body = SOURCES.replace(
        "    telegram_channels: ['@chan_one']\n",
        f"    telegram_channels: [{handle!r}]\n",
    )
    with pytest.raises(ValueError, match="malformed handle"):
        load_registry(write(tmp_path, body + TAXONOMY))


def test_collect_defaults_to_true_and_must_be_a_boolean(tmp_path):
    """`collect` is how r2 takes a source out of COLLECTION without taking it out of the registry.

    The default has to be "collect": a row written before the flag existed — every row in the file
    today — means collect, and a source that silently read as paused would stop being read with
    nothing saying so. Strict on the type for `watch`'s reason: `collect: "no"` is truthy.
    """
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].collect is True

    paused = SOURCES.replace(
        "    telegram_channels: ['@chan_one']\n",
        "    telegram_channels: ['@chan_one']\n    collect: false\n",
    )
    assert load_registry(write(tmp_path, paused + TAXONOMY)).sources[0].collect is False

    lying = SOURCES.replace(
        "    telegram_channels: ['@chan_one']\n",
        "    telegram_channels: ['@chan_one']\n    collect: 'no'\n",
    )
    with pytest.raises(ValueError, match="non-boolean collect"):
        load_registry(write(tmp_path, lying + TAXONOMY))


def test_malformed_channel_handle_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['chan_without_at']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="malformed handle"):
        load_registry(path)


def test_unknown_source_type_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: newspaper\n"
        "    telegram_channels: ['@chan_one']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="unknown source_type"):
        load_registry(path)


def test_empty_tracked_groups_rejected(tmp_path):
    path = write(tmp_path, SOURCES + "taxonomy:\n  tracked_groups: {}\n")
    with pytest.raises(ValueError, match="tracked_groups"):
        load_registry(path)


def test_duplicate_brand_id_rejected(tmp_path):
    path = write(
        tmp_path,
        SOURCES + TAXONOMY + "watchlist:\n"
        "  - brand_id: rud\n    display_names: ['Рудь']\n"
        "  - brand_id: rud\n    display_names: ['Rud']\n",
    )
    with pytest.raises(ValueError, match="duplicate brand_id"):
        load_registry(path)


def test_the_operators_watchlist_addition_is_in_both_files_and_says_the_same_thing():
    """The +3 of 2026-08-08. `docs/WATCHLIST.md` is the operator-facing list and the registry is
    what code reads; a brand that lives in one of them is a brand half the project cannot see.

    UA canon, RU as a matching alias — checked as an ORDER, because "Заріг, Зарог" and "Зарог,
    Заріг" are the same set and only one of them is the ruling.
    """
    doc = (REGISTRY.parent.parent / "docs" / "WATCHLIST.md").read_text(encoding="utf-8")
    brands = {b.brand_id: b for b in load_registry(REGISTRY).watchlist}
    added = {
        "zarih": ("Заріг", "Зарог"),
        "myrhorodska-korivka": ("Миргородська корівка", "Миргородская коровка"),
        "yahotynske-dlia-ditei": ("Яготинське для дітей", "Яготинское для детей"),
    }
    for brand_id, names in added.items():
        assert brands[brand_id].display_names == names, brand_id
        assert brands[brand_id].own is False, brand_id
        assert f"| {brand_id} | {names[0]}, {names[1]} |" in doc, brand_id


def test_the_signature_stamp_moved_the_file_and_not_one_row_of_it():
    """The 2026-08-10 operator signature (SPEC 3.17 step 0): composition 66 = launch 59 + watch 7,
    the day-2 PROVISIONAL diff signed as it stands.

    Two things have to be true at once, and only one of them is obvious. The stamp is provenance,
    so no source, no taxonomy group and no watchlist brand may move under it — checked by parsing
    the file with the block and without it and comparing all three entities. And the file's sha256
    DID move, which is what a record pinning those bytes sees; the reconstruction is the chain from
    the signed screen's citation to today's file.

    Since 2026-08-12 the chain has a second link, and it is not a comment block: SPEC 3.17 (13)(b)
    put three Latin display names into three watchlist rows. So the stamp strip alone no longer
    reaches the signed sha — that is asserted here rather than papered over, and the composed
    reconstruction does. The middle sha is checked too, because it is the one the sku registrations
    pin, and a chain is only a chain if every link is nailed to something.
    """
    stripped = registry_without_the_signature_stamp()
    assert sha256(stripped).hexdigest() != SIGNED_SCREEN_REGISTRY_SHA, "the aliases are the reason"
    assert sha256(registry_before_the_latin_aliases(REGISTRY)).hexdigest() == PRE_13B_REGISTRY_SHA
    assert sha256(registry_as_the_signed_screen_read_it()).hexdigest() == SIGNED_SCREEN_REGISTRY_SHA
    assert sha256(REGISTRY.read_bytes()).hexdigest() != SIGNED_SCREEN_REGISTRY_SHA

    text = REGISTRY.read_text(encoding="utf-8")
    assert text.count("SIGNED 2026-08-10") == 1
    for claim in ("66 sources", "launch 59 + watch 7", "changes no", "5c3 NAMED revision"):
        assert claim in text, claim
    # The numbers the stamp claims, read off the composition it stamps — which is the SIGNED one,
    # not today's. Revision r2 added eight A1 sources on 2026-08-30, and counting `live` here would
    # have made the stamp look wrong about a composition it never described. The stamp's own
    # numbers are never touched; the reconstruction is what is counted
    # ([[the_field_true_under_the_old_constant]]).
    signed = load_registry_text(registry_as_the_signed_screen_read_it().decode("utf-8"), REGISTRY)
    watch = [s for s in signed.sources if s.watch]
    assert (len(signed.sources), len(signed.sources) - len(watch), len(watch)) == (66, 59, 7)
    assert len(load_registry(REGISTRY).sources) > 66, "r2 is why this is counted on the signed link"


def test_the_latin_aliases_moved_three_display_name_lists_and_nothing_else():
    """SPEC 3.17 (13)(b) says «aliases only». Checked as an entity diff rather than believed: no
    source, no taxonomy group, no brand row and no `own` flag may move under an alias amendment,
    and the three lists that DO move are named with their before and after."""
    before = load_registry_text(
        registry_before_the_latin_aliases(REGISTRY).decode("utf-8"), REGISTRY
    )
    # Against r1 and not against today's file: the amendment's claim is about ONE revision, and
    # r2 moved ten source rows for reasons that have nothing to do with aliases. Diffing pre-(13)(b)
    # against live would fold two revisions into one and this test would be asserting r2.
    after = load_registry_text(registry_before_r2(REGISTRY).decode("utf-8"), REGISTRY)
    assert [vars(source) for source in before.sources] == [vars(s) for s in after.sources]
    assert before.taxonomy.tracked_groups == after.taxonomy.tracked_groups
    assert [b.brand_id for b in before.watchlist] == [b.brand_id for b in after.watchlist]
    assert [b.own for b in before.watchlist] == [b.own for b in after.watchlist]
    moved = {
        was.brand_id: (was.display_names, now.display_names)
        for was, now in zip(before.watchlist, after.watchlist, strict=True)
        if was.display_names != now.display_names
    }
    assert moved == {
        "rud": (("Рудь",), ("Рудь", "Rud")),
        "try-vedmedi": (
            ("Три Ведмеді", "Три Медведя"),
            ("Три Ведмеді", "Три Медведя", "Three Bears"),
        ),
        "limo": (("Лімо", "Лимо"), ("Лімо", "Лимо", "LIMO")),
    }


def test_the_reconstruction_refuses_a_display_names_list_it_no_longer_recognises(tmp_path):
    """The negative control the enumeration needs. A fourth alias added to one of these three rows
    without a line in `LATIN_ALIASES_13B` would silently reconstruct to bytes nobody registered —
    so the reconstruction fails instead, and the sealed pins fail with it."""
    edited = REGISTRY.read_text(encoding="utf-8").replace(
        'display_names: ["Лімо", "Лимо", "LIMO"]', 'display_names: ["Лімо", "Лимо", "LIMO", "Limo"]'
    )
    path = write(tmp_path, edited)
    with pytest.raises(ValueError, match=r"appears 0 times, expected once"):
        registry_before_the_latin_aliases(path)


def test_the_reconstruction_refuses_a_registry_the_amendment_never_touched(tmp_path):
    path = write(tmp_path, SOURCES + TAXONOMY)
    with pytest.raises(ValueError, match="this is not the amended registry"):
        registry_before_the_latin_aliases(path)


def test_r2_undoes_to_the_bytes_the_r1_records_pin():
    """The link that makes revision r2 legal at all, nailed to a sha rather than described.

    Seven sealed records pin `d4e3b237…`. r2 moved the live file off it, and re-pinning them would
    be a pin that follows the file. So the undo is checked here: strip the bracketed block r2
    appended and every line r2 marked, and what is left has to be exactly the bytes those seven
    read. If it is not, `load_registry_as_pinned` refuses for all seven and this test says so first.
    """
    assert sha256(registry_before_r2(REGISTRY)).hexdigest() == R1_REGISTRY_SHA
    assert sha256(REGISTRY.read_bytes()).hexdigest() != R1_REGISTRY_SHA, "r2 is in the live file"
    # and the whole chain still reaches the two older links THROUGH it
    assert sha256(registry_before_the_latin_aliases(REGISTRY)).hexdigest() == PRE_13B_REGISTRY_SHA
    assert sha256(registry_as_the_signed_screen_read_it()).hexdigest() == SIGNED_SCREEN_REGISTRY_SHA


def test_the_r2_undo_refuses_a_half_marked_or_unmarked_registry(tmp_path):
    """The negative control on the new link. A reconstruction that found nothing to undo would
    return today's bytes and satisfy a pin it never reached — so both halves must be present, and
    a file missing either is a refusal ([[guard_selftest_negative_control]])."""
    text = REGISTRY.read_text(encoding="utf-8")

    no_close = write(tmp_path, text.replace("  # --- r2 END", "  # r2 end, mis-spelled"))
    with pytest.raises(ValueError, match="found 1 open and 0 close markers"):
        registry_before_r2(no_close)

    unmarked = write(tmp_path, text.replace("  # (r2)", ""))
    with pytest.raises(ValueError, match="this is not the r2 registry"):
        registry_before_r2(unmarked)


def test_the_paused_rows_are_loaded_and_are_not_collected():
    """r2's whole mechanism, both directions (review 30.08): the rows that leave collection stay
    IN the registry and say they are not collected.

    Deleting them was the other way to write the ruling and it breaks the build at $0 —
    `scripts/build_aggregates.py::segment_for` raises `SystemExit` for any channel that carries
    evidence rows and has no registry entry. So the row is loaded (direction one) and `collect` is
    False (direction two), and every A1 row that survived the corrections is still collected.

    **57, not the 39 this test first held.** The scaffold review («Acceptance of the scaffold
    slice», 30.08) made three corrections to r2, and two of them move this count: the 17 Poltava
    rows are «deferred to phase B» — the phase spec §3 says «nothing collected» and r2 had left
    them collecting — and `@znishkom` is off-category (Steam discounts; the census title-matched
    the chain name). Each correction carries its OWN `paused_by`, so the three populations are
    counted separately here rather than summed into one number that could not say which ruling
    paused a row.
    """
    sources = load_registry(REGISTRY).sources
    paused = [s for s in sources if not s.collect]
    assert len(paused) == 57
    assert all(s.audience is not None for s in paused), "a paused row still attributes its history"
    text = REGISTRY.read_text(encoding="utf-8")
    assert text.count('paused_at: "2026-08-30"') == 57
    assert text.count('paused_by: "ruling (ц) 30.08"') == 39
    assert text.count('paused_by: "deferred to phase B (ruling (ц) 30.08)"') == 17
    assert [s.id for s in paused if s.audience == "regional"] != [], "phase B is the 17 regional"
    assert len([s for s in paused if s.audience == "regional"]) == 17
    assert text.count("off-category, census title-match false positive") == 1
    by_id = {s.id: s for s in sources}
    assert not by_id["znishkom"].collect, "review 30.08: @znishkom is off-category"
    assert by_id["marketopt_promo"].collect, "review 30.08: the public Маркетопт row STAYS"
    a1 = {"atb", "atb_fanatik", "atb_aktsiyi", "varus", "ekomarket_shop", "epicentrk_sale",
          "forainfo", "marketopt_private", "blyzenko", "silpo", "fozzy", "sim23", "rozetka",
          "msuaaaa", "kopiyochka1", "xochydeshevshe"}
    assert a1 <= set(by_id), sorted(a1 - set(by_id))
    assert [i for i in sorted(a1) if not by_id[i].collect] == []


def test_the_seventeen_A1_rows_of_the_phase_spec_are_expressible_and_present():
    """`docs/PHASE-promo-pulse-1.md` §3's A1 list, entry by entry, against the file.

    17 rows and 18 entries: @ATB_FANatik's discussion group is a SECOND CHANNEL on the FANatik row,
    and @kop1chat is a second channel on the Копійочка row that was already here. Two of the 18 are
    not usernames at all, which is why `_HANDLE` is a union — and this is the test that would have
    caught «the row cannot be written down» before the collector found it empty.
    """
    channels = {c for s in load_registry(REGISTRY).sources for c in s.telegram_channels}
    for entry in (
        "@atb_market_official", "@ATB_FANatik", "1925810730", "@atb_aktsiyi", "@VARUS_channel",
        "@ekomarket_shop", "@epicentrk_sale", "@forainfo", "+Ejz6ubzm21IyMTQy", "@blyzenkoua",
        "@silposilpo", "@fozzyshopua", "@sim23_simi", "@rrozetka", "@msuaaaa", "@kop1chat",
        "@znishkom", "@xochydeshevshe",
    ):
        assert entry in channels, entry


def test_a_pin_neither_branch_reaches_refuses():
    """`load_registry_as_pinned` is what every recomputation of a sealed bar goes through, so its
    failure mode has to be a refusal and not a quiet fall-back to today's alias table."""
    assert load_registry_as_pinned(PRE_13B_REGISTRY_SHA, REGISTRY).watchlist
    assert load_registry_as_pinned(R1_REGISTRY_SHA, REGISTRY).watchlist
    live_sha = sha256(REGISTRY.read_bytes()).hexdigest()
    assert load_registry_as_pinned(live_sha, REGISTRY).watchlist
    with pytest.raises(ValueError, match="the registry has moved in a way nothing here"):
        load_registry_as_pinned("f" * 64, REGISTRY)


def test_the_two_alias_tables_differ_only_where_the_amendment_says(tmp_path):
    """What the recomputation of a sealed bar actually depends on: «Three Bears» resolves today and
    did not when v4 was bought. «Rud» and «LIMO» casefold onto their own brand_ids, which is a
    second, quieter change — `gold_key` returns the brand_id when a name resolves, so those two
    keys move from `raw:rud`/`raw:limo` to `rud`/`limo` in any table built after the amendment."""
    was = watchlist_aliases(
        load_registry_text(
            registry_before_the_latin_aliases(REGISTRY).decode("utf-8"), REGISTRY
        ).watchlist
    )
    now = watchlist_aliases(load_registry(REGISTRY).watchlist)
    assert set(now) - set(was) == {"three bears", "rud", "limo"}
    assert set(was) - set(now) == set()
    assert {key: now[key] for key in set(now) - set(was)} == {
        "three bears": "try-vedmedi",
        "rud": "rud",
        "limo": "limo",
    }


def test_the_stamped_and_unstamped_registries_parse_to_the_same_three_entities(tmp_path):
    """The other half of the claim above: the comment block is invisible to the loader.

    Written against a temp copy rather than by re-reading the shipped file twice — two reads of one
    path cannot tell "the stamp changes nothing" from "the stamp is not there".
    """
    before = write(tmp_path, registry_without_the_signature_stamp().decode("utf-8"))
    a, b = load_registry(before), load_registry(REGISTRY)
    assert [vars(s) for s in a.sources] == [vars(s) for s in b.sources]
    assert a.taxonomy.tracked_groups == b.taxonomy.tracked_groups
    assert [vars(w) for w in a.watchlist] == [vars(w) for w in b.watchlist]


def test_the_baby_food_line_is_a_row_of_its_own_and_its_name_nests_in_its_parents():
    """«Яготинське для дітей» is tracked separately from «Яготинське» — the Мгарське pattern, and
    the operator's own words. The trap that comes with it: the child's display name CONTAINS the
    parent's, so a post naming the child matches both aliases. Pinned here so any matcher over
    this list has to answer for it rather than double-count in silence."""
    brands = {b.brand_id: b for b in load_registry(REGISTRY).watchlist}
    assert "yagotynske" in brands and "yahotynske-dlia-ditei" in brands
    parent = brands["yagotynske"].display_names
    child = brands["yahotynske-dlia-ditei"].display_names
    assert any(p in c for p in parent for c in child), "the nesting this test exists for is gone"
