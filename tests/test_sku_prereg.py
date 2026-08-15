"""The pre-registration: are the bars the law's own words, and does every ratio have a denominator?

sku-b is ONE paid attempt and a failed bar closes B by measurement, so the things that can go wrong
here are expensive and quiet: a bar paraphrased away from SPEC, a denominator that can come back
empty, an executor's reading passing as the contract's.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import write_sku_prereg as prereg  # noqa: E402

from market_pulse import positions, prompts  # noqa: E402
from market_pulse.registry import registry_before_the_latin_aliases  # noqa: E402


@pytest.fixture(scope="module")
def record():
    return json.loads(prereg.RECORD.read_text(encoding="utf-8"))


def test_every_bar_is_quoted_out_of_the_spec_as_written(record):
    """A bar retyped is a bar that can drift from the law it claims to be. Checked whitespace-
    insensitively against docs/SPEC.md, which is where the amendment lives wrapped."""
    law = prereg.verbatim(prereg.SPEC)
    for name, bar in record["bars"].items():
        assert bar["verbatim"] in law, name
        assert bar["verbatim"] == prereg.BARS[name]
    assert record["attempts"]["verbatim"] in law
    assert record["attempts"]["on_success"] in law
    # (11)'s five readings are TRANSCRIBED, not redesigned: the resumed session is held to them and
    # a paraphrase here would be a clause the law does not contain
    assert record["resume"]["supersedes_clause"]["verbatim"] in law
    assert record["resume"]["bars_unchanged"] in law
    for key, reading in record["resume"]["readings"].items():
        assert reading in law, key
        assert reading == prereg.RESUME_READINGS[key]
    assert set(record["resume"]["readings"]) == {"a", "b", "c", "d", "e"}
    # and (12)(a)–(d), which is the law THIS record is registered under. Same rule, same check: the
    # markdown emphasis is carried through because a quote that tidies the law can drift from it
    assert record["supersedes"]["verbatim"] in law
    for key, reading in record["supersedes"]["readings"].items():
        assert reading in law, key
        assert reading == prereg.V4_READINGS[key]
    assert set(record["supersedes"]["readings"]) == {"a", "b", "c", "d"}


def test_a_paraphrased_bar_stops_the_write(monkeypatch, tmp_path):
    """The negative control: the check is only worth having if it fires on a reworded bar."""
    monkeypatch.setitem(prereg.BARS, "text_tier_accuracy", "text tier accuracy at least 0.85")
    with pytest.raises(SystemExit, match="not in docs/SPEC.md as written"):
        prereg.main(["--out", str(tmp_path / "p.json")])


def test_a_paraphrased_resume_reading_stops_the_write(monkeypatch, tmp_path):
    """The same control on (11)'s readings, which the bars' check did not cover until v3 carried
    them. The resumed session is held to (11)(c) — a warm-up that is representative — and a
    reworded copy of it here is a clause with nobody's signature on it."""
    monkeypatch.setitem(
        prereg.RESUME_READINGS, "c", "the warm-up uses a real page and a real row this time"
    )
    with pytest.raises(SystemExit, match="not in docs/SPEC.md as written"):
        prereg.main(["--out", str(tmp_path / "p.json")])


def test_a_paraphrased_v4_reading_stops_the_write(monkeypatch, tmp_path):
    """(12)'s readings under the same control, and (12)(b) is the one worth naming: it is the clause
    that says a refused session charges the PHASE, and a paraphrase of it here would be the licence
    this record claims to carry with nobody's signature on it."""
    monkeypatch.setitem(
        prereg.V4_READINGS, "b", "a refused session's spend does not come out of the next cap"
    )
    with pytest.raises(SystemExit, match="not in docs/SPEC.md as written"):
        prereg.main(["--out", str(tmp_path / "p.json")])


def test_the_three_thresholds_and_their_direction(record):
    assert {name: bar["threshold"] for name, bar in record["bars"].items()} == {
        "leaflet_brand_recall": 0.75,
        "price_pair_accuracy": 0.80,
        "text_tier_accuracy": 0.85,
    }
    for bar in record["bars"].values():
        assert bar["direction"] == ">="
        # a threshold on a ratio has to be reachable at all: none of these exceeds 1.0
        assert 0 < bar["threshold"] <= 1.0


def test_one_attempt_and_a_failure_closes_b(record):
    """v4 buys ONE additional session at the cap (12)(a) names, and every earlier clause is quoted
    beside it rather than deleted: (6)'s is what the first 17 answers were bought under and (11)'s
    is the clause the attempt still runs on, so a reader can see which law each half came from."""
    assert record["attempts"]["count"] == 1
    assert record["attempts"]["cap_usd"] == 0.65
    assert "BY MEASUREMENT" in record["attempts"]["on_failure"]
    assert "No retry" in record["attempts"]["on_failure"]
    assert record["attempts"]["verbatim"] == prereg.RESUME_CLAUSE
    assert record["resume"]["supersedes_clause"]["verbatim"] == prereg.ONE_ATTEMPT


def test_every_bar_names_a_denominator_and_what_it_excludes(record):
    """The failure this exists to prevent: an absolute ratio whose denominator can be empty fails by
    arithmetic and reads as a measurement."""
    for name, bar in record["bars"].items():
        assert bar["denominator"], name
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert len(leaflet["excluded"]["posts"]) == 4
    assert "undefined" in leaflet["excluded"]["why"]
    assert "PRECISION probe" in leaflet["excluded"]["instead"]
    assert "15 of 19" in leaflet["reachable"]
    price = record["bars"]["price_pair_accuracy"]
    assert "NOT_REACHABLE" in price["reachability"]["rule"]
    assert "NOT_SCORED" in price["reachability"]["rule"]
    text = record["bars"]["text_tier_accuracy"]
    assert "NOT_SCORED" in text["reachability"]["rule"]
    assert "NOT_SCORED" in text["unreadable_rows"]


def test_the_unreadable_reply_is_not_scored_as_an_empty_answer(record):
    """An unreadable reply and «nothing on this row» are different outcomes, and the empty class is
    where parse failures pile up if nobody separates them."""
    text = record["bars"]["text_tier_accuracy"]
    assert "NOT scored as `none`" in text["unreadable_rows"]
    assert "excluded from the denominator" in text["unreadable_rows"]
    assert "10%" in text["unreadable_rows"]


def test_the_per_page_reading_is_declared_the_executors_and_needs_a_word(record):
    """The most expensive thing in the file. The bar says «per page», the gold is per POST, and the
    session that would discover that is the one paid attempt."""
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert "per page" in leaflet["verbatim"]
    assert "THE EXECUTOR'S READING" in leaflet["why_not_per_page"]
    assert "MACRO MEAN" in leaflet["denominator"]
    ids = {item["id"] for item in record["ratification_required"]}
    assert ids == {"R1", "R2", "R3", "R4", "R5"}
    r1 = next(item for item in record["ratification_required"] if item["id"] == "R1")
    assert "must NOT run until this line is ratified" in r1["if_refused"]
    for item in record["ratification_required"]:
        assert item["bar"] in record["bars"]
        assert item["question"] and item["if_refused"]


def test_the_page_set_is_the_pages_the_reviewer_saw(record):
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert "108 pages" in leaflet["extraction_unit"]
    assert "not the 159 available" in leaflet["extraction_unit"]
    reference = json.loads((REPO_ROOT / leaflet["gold"]["path"]).read_text(encoding="utf-8"))
    assert reference["population"]["pages_sent"] == 108
    assert reference["population"]["pages_available"] == 159
    assert leaflet["gold"]["pairs"] == reference["gold"]["pairs"] == 55


def test_the_price_bar_names_the_dump_the_team_lead_reads(record):
    """SPEC's own wording puts a human between the run and the number, and the procedure has to say
    what that human opens. The executor never scores its own sample (SPEC §10)."""
    price = record["bars"]["price_pair_accuracy"]
    assert "team-lead read of the per-position dump against the images" in price["verbatim"]
    for field in ("page", "sha256", "price_promo", "price_old", "discount_pct_printed", "depth"):
        assert field in price["procedure"], field
    assert "never scores its own sample" in price["procedure"]
    assert "a right promo beside a wrong old price is a wrong pair" in price["numerator"]


def test_the_ladder_is_pinned_as_an_input_and_not_only_as_a_hash(record):
    """Bar 3's gold is computed from the operator's ticks by this ladder, so a ladder that moved
    between the pack build and the pilot would move the gold. Pinned as its whole table, so a future
    reader does not have to run this code to see what was registered."""
    assert record["ladder"]["sha256"] == positions.ladder_sha256()
    assert record["ladder"]["table"] == positions.ladder_table()
    assert len(record["ladder"]["table"]) == 32
    pack = json.loads((REPO_ROOT / "results" / "sku_text_pack_manifest.json").read_text("utf-8"))
    assert pack["ladder"]["sha256"] == record["ladder"]["sha256"]
    assert record["bars"]["text_tier_accuracy"]["gold"]["ladder_sha256"] == pack["ladder"]["sha256"]


def test_both_instruments_are_pinned_by_sha(record):
    assert record["instruments"]["positions_post_gm4"] == prompts.prompt_sha256(
        "positions_post_gm4"
    )
    assert record["instruments"]["positions_text_gm4"] == prompts.prompt_sha256(
        "positions_text_gm4"
    )
    assert set(prompts.POSITIONS) == {"positions_post_gm4", "positions_text_gm4"}


def test_every_pinned_input_still_hashes_to_what_it_says(record):
    """`docs/SPEC.md` now carries amendment 3.17 (7), which the pin predates: the block ratifies
    readings this record already states and moves no bar, so the pin holds the file WITHOUT it —
    the registered law — instead of following the file. Checked both directions, because either
    one alone passes for the wrong reason: a live hash equal to the pin would mean the amendment
    never landed, and a stripped hash equal to the pin proves the law is the bytes that were
    registered. The strip is the producer's own function; a copy of it here could drift from the
    one that writes the record. Every other pinned input is still hashed as it sits on disk.
    """
    live = hashlib.sha256(prereg.SPEC.read_bytes()).hexdigest()
    pin = record["pinned_inputs"]["docs/SPEC.md"]
    spec_text = prereg.SPEC.read_text(encoding="utf-8")
    assert prereg.RATIFICATION_BEGIN in spec_text and prereg.RATIFICATION_END in spec_text
    assert live != pin, "the live SPEC hashes to the pin — 3.17 (7) is not in the file"
    assert hashlib.sha256(prereg.registered_law(prereg.SPEC)).hexdigest() == pin

    # 3.17 (8) landed beside (7) in uni-b and (9) beside both in sku-b-prep, so the strip has to
    # take EVERY marked block off or this pin stops re-deriving. Named here rather than implied:
    # this is the line that says what the strip is expected to know about, and extending it is the
    # only legal way to green a ratification block — re-pinning the record is not (the prereg chain
    # is the pilot's witness, and a v3 happens only on team-lead instruction).
    blocks = [
        # the amendment index, repaired 2026-08-13: the header paragraph stopped being updated after
        # 3.14 and the body kept growing, so the list of amendments became a finding aid written
        # separately. It moves no bar and it did not exist when this pin was taken, so it wears
        # markers like the rest. Document order puts it first — it sits near the top of the file.
        "amendment-index",
        "sku-b-ratification",
        "sku-b-ratification-2",
        "sku-b-ratification-3",
        "sku-b-ratification-4",
        "sku-b-ratification-5",
        # (12) — the v4 session and the cost of a refusal, ratified at the sku-b-v3-run acceptance.
        # It landed with this line missing, which is how the enumeration stays the thing that has to
        # be looked at: the amendment cannot arrive unnoticed.
        "sku-b-ratification-6",
        # (13) — the B′ revision, ratified off the miss decomposition. It arrived the same way, one
        # name short, and it is the first block that moves an INSTRUMENT: the parser family, the
        # 800 → 1200 ceiling and three alias rows. The strip still takes it off, because this pin is
        # v4's and v4 was registered before any of that existed.
        "sku-b-ratification-7",
        # (14) — B′ finalised: the four pending pairs read, B1/B4/B5 ruled, and the cap moved from
        # (13)(d)'s $0.40 to $0.65. Same one-name-short arrival as its two predecessors. Stripped
        # here for the same reason (13) is — v4 predates it — and KEPT by
        # `write_sku_prereg_b2.KEEP_BLOCKS`, whose registration is made UNDER it.
        "sku-b-ratification-8",
        # 3.18 — the 5c2 briefing (2026-08-13): question 7's depth instrument, the NARROWED
        # integration on a red gate, the phase cap 25 → 30 and the 5c2-validate operator sitting.
        # The first block of a second family, and the arrival was the same one-name-short one its
        # predecessors had. Stripped here because this pin predates every word of it.
        "amendment-3.18",
        # 3.19 — the 5c2-validate sitting (2026-08-14): text-less comments leave the inference
        # queue from the next paid cycle, reporting denominators follow, and the 5 075 rows already
        # bought are explicitly never re-scored. It arrived one name short like every block before
        # it. Stripped here for the same reason as the rest — this pin is v1–v4's, and every one of
        # them predates it by weeks — and stripped by the SEALED 5c2 registration too, whose
        # ten-name keep (`write_prereg_5c2.KEEP_BLOCKS`) deliberately did NOT grow to meet it.
        "amendment-3.19",
        # 3.20 — the Phase-6 command-centre plan (2026-08-15): every displayed figure comes from
        # committed artifacts through the aggregate layer, SQLite is that layer's home, the centre
        # is bilingual off `config/metrics.yaml`, overview insights are code-generated, and the
        # promo surface gains Маркетопт. One name short on arrival like every block before it.
        # Stripped here for the same reason: these pins are v1–v4's and predate all of it. Its
        # index entry lives INSIDE the block — `amendment-index` is one of the ten blocks the
        # SEALED 5c2 pin KEEPS, so an edit there would break `results/prereg_5c2_run.json`.
        "amendment-3.20",
        # 3.21 — the red-gate sitting (2026-08-15): the watchlist's text-matching rules become law
        # in a file of their own (`config/watchlist_rules.yaml`, revision r1) so that a rule change
        # never edits the two SEALED configs, the comment-signals architecture is ratified, brand ×
        # tonality surfaces are labelled as MENTIONS and not as stance, and the promo surface owes
        # a positions table. One name short on arrival like every block before it. Stripped here
        # for the same reason as all of them: these pins are v1–v4's and predate every word of it.
        "amendment-3.21",
        # 3.22 — the fix-b finding, closed by operator ruling (2026-08-15): a row-level promo
        # surface prints the PRINTED badge's depth and never the arithmetic one, because the
        # arithmetic reading beside the row's own promo price returns the extracted old price.
        # The narrowest block of the family — it recomputes nothing, it rules on which of two
        # readings already in the evidence may be shown. One name short on arrival like every
        # block before it. Stripped here for the same reason: these pins are v1–v4's.
        "amendment-3.22",
    ]
    assert prereg.RATIFICATION_NAME.findall(spec_text) == blocks
    law = prereg.registered_law(prereg.SPEC).decode("utf-8")
    for name in blocks:
        if name == "sku-b-ratification":
            # skipped by NAME and not by position. It is a prefix of `sku-b-ratification-2` … `-8`,
            # so a strip that left one of those standing would fail on this line first and name the
            # wrong block. Document order now puts `amendment-index` at blocks[0], and a `[1:]`
            # slice would quietly stop checking whichever name sorts there.
            continue
        assert name not in law

    # `config/registry.yaml` is the second input that has moved under a ratified amendment, and it
    # gets its own narrow branch rather than a loosened loop: SPEC 3.17 (13)(b) put three Latin
    # display names into three watchlist rows on 2026-08-12, which is a CONTENT change and not a
    # comment block. Same rule as above and checked the same both ways — the live file must no
    # longer hash to the pin (or the amendment never landed) and the pre-(13)(b) reconstruction
    # must. The producer's own function does the undoing; a copy here could drift from it.
    registry = REPO_ROOT / "config" / "registry.yaml"
    registry_pin = record["pinned_inputs"]["config/registry.yaml"]
    assert hashlib.sha256(registry.read_bytes()).hexdigest() != registry_pin
    assert hashlib.sha256(prereg.registered_bytes(registry)).hexdigest() == registry_pin
    assert prereg.registered_bytes(registry) == registry_before_the_latin_aliases(registry)

    for path, sha in record["pinned_inputs"].items():
        if path in ("docs/SPEC.md", "config/registry.yaml"):
            continue  # both directions, above
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert set(record["pinned_inputs"]) == {
        "docs/SPEC.md",
        "results/sku_reference_leaflet.json",
        "results/sku_text_pack_manifest.json",
        "results/sku_prefilter_census.json",
        "config/registry.yaml",
        # new in v2: the pre-filter's category vocabulary stopped being a draft nobody pinned
        # (SPEC 3.17 (8)). Bar 3's rows were selected by that filter, so it is an input like the
        # registry is — and an unpinned input is one that can move under the bar unnoticed.
        "config/lexicon.yaml",
    }


B2 = "results/sku_pilot_prereg_b2.json"


def test_a_line_outside_every_marked_block_breaks_both_sealed_pins(tmp_path):
    """The negative control for the strip, and the reason the strip is not a licence to edit SPEC.

    Extending `RATIFICATION_NAME` greens a pin by taking MARKED text off. What it must never do is
    make the pin blind: a line that arrives outside every marked block still moves the registered
    law, and both sealed records have to notice. Driven on a COPY in `tmp_path` — a test that wrote
    to `docs/SPEC.md` would be the drift these pins exist to catch, and that file is the team
    lead's.

    Both records, because they strip different sets: v4 keeps nothing (it predates every block) and
    B′ keeps `sku-b-ratification-7` and `-8` (it is registered UNDER them). The live file is checked
    first as the positive control — an inequality nobody has seen equal is not evidence.
    """
    import write_sku_prereg_b2 as b2

    v4_pin = json.loads(prereg.RECORD.read_text(encoding="utf-8"))["pinned_inputs"]["docs/SPEC.md"]
    b2_pin = json.loads((REPO_ROOT / B2).read_text(encoding="utf-8"))["pinned_inputs"][
        "docs/SPEC.md"
    ]
    assert hashlib.sha256(prereg.registered_law(prereg.SPEC)).hexdigest() == v4_pin
    assert (
        hashlib.sha256(prereg.registered_law(prereg.SPEC, keep=b2.KEEP_BLOCKS)).hexdigest()
        == b2_pin
    )

    copy = tmp_path / "SPEC.md"
    copy.write_text(
        prereg.SPEC.read_text(encoding="utf-8") + "\nan amendment nobody marked.\n",
        encoding="utf-8",
    )
    assert hashlib.sha256(prereg.registered_law(copy)).hexdigest() != v4_pin
    assert hashlib.sha256(prereg.registered_law(copy, keep=b2.KEEP_BLOCKS)).hexdigest() != b2_pin


def test_the_prereg_says_what_it_does_not_touch(record):
    """The 5c3 rulings are the loudest omission: «Варто» and «Селянське» are a named revision and
    applying them here would change what the leaflet gold means mid-contract."""
    out = record["not_in_scope"]
    assert "«Варто» text-matching OFF" in out["the 5c3 rulings"]
    assert "NOT applied" in out["the 5c3 rulings"]
    assert "symmetric" in out["the 141 names"]
    assert "baselines.json" in out["the frozen family"]
    assert "consumer quotes never enter" in out["aggregates"]


V1 = "results/sku_pilot_prereg.json"
V2 = "results/sku_pilot_prereg_v2.json"
V3 = "results/sku_pilot_prereg_v3.json"
V4 = "results/sku_pilot_prereg_v4.json"
PREREGS = (V1, V2, V3, V4)
BEFORE_ANY_ARTIFACT = (V1, V2)
"""The two that were registered before sku-b had bought anything. Neither v3 nor v4 can make that
claim and neither pretends to — each is registered before its own session, over a population part of
which is already paid for, and each has its own ordering rule in the tests below."""

SEALED = {
    V1: "b1bfa40d1f5073ec7b3d199bd57d96dd1bb72f37d99d26135f98386a8473a142",
    V2: "d4ced2a8ba00b48bca2d30af9c7ce8977eb387631b1735b4e05ea15ba306e9ad",
    V3: "a80e8e55488439372244715f24f7bbfb56cf46a3a2586d38fa75a14c4c643656",
}
"""Every superseded registration, by the bytes rather than by a description. Each leaves the
producer's hands when RECORD moves past it, and from that moment nothing rebuilds it, so a literal
sha is the only thing standing between "v2 is untouched" and nobody checking. v2 matters most: it is
the record the 17 paid answers were bought under, and the bars are scored against ITS verbatim texts.
v3 was registered and never spent — its session was refused at the (10)(a) gate — which is exactly
why it is sealed rather than deleted: it is the registration that refusal happened under."""


def leaves(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from leaves(value, f"{path}[{index}]")
    else:
        yield path, node


@pytest.mark.parametrize("prereg_path", BEFORE_ANY_ARTIFACT)
def test_the_prereg_was_committed_before_any_pilot_artifact(prereg_path):
    """A pre-registration written after the thing it judges is a rationalisation, and git history is
    the only witness to the ordering — so the claim is checked against history rather than against
    today's directory listing, which stops being evidence the moment sku-b writes its records.

    Both records, because v2 re-registers BESIDE v1 and inherits the same duty: the ordering that
    matters is "before the one paid attempt", and each has to be able to prove it on its own.

    The same discipline `run_v22_probe.py` uses: shell out to git, and treat "not tracked" as a
    failure rather than a skip. An uncommitted pre-registration is not one.
    """
    body = json.loads((REPO_ROOT / prereg_path).read_text(encoding="utf-8"))
    assert "before any sku-b artifact exists" in body["class"]
    added = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", prereg_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert len(added) == 1, "the pre-registration is added exactly once, or its ordering is unclear"
    tree = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", added[0], "results/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert prereg_path in tree
    # at the commit that added it, no pilot RESULT existed — only pre-registrations. That is
    # permanent: a record written after the artifact it judges cannot be repaired later.
    others = [
        name for name in tree if name.startswith("results/sku_pilot_") and name not in PREREGS
    ]
    assert others == [], others


def registered_over(prereg_path: str, pinned: dict[str, str]) -> None:
    """At the commit that ADDED this registration, the sku-b run artifacts in the tree were exactly
    `pinned` and each hashed to what the record pins.

    The `BEFORE_ANY_ARTIFACT` rule cannot be reused from v3 onwards: `results/sku_pilot_serving.json`
    landed after v2 and the interrupted run's own artifacts landed before v3, so "no pilot artifact
    exists" would fail a record for being exactly what SPEC 3.17 (11) asked for. What a resumed
    registration must prove is narrower and stronger, and it rules out both directions of the
    failure: a resume registered after its own session had already bought something, and a resume
    registered against a record that has since moved.
    """
    added = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", prereg_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert len(added) == 1, "the re-registration is added exactly once, or its ordering is unclear"
    tree = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", added[0], "results/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert prereg_path in tree
    assert sorted(name for name in tree if name.startswith("results/sku_b_")) == sorted(pinned)
    for path, sha in pinned.items():
        blob = subprocess.run(
            ["git", "show", f"{added[0]}:{path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        ).stdout
        assert hashlib.sha256(blob).hexdigest() == sha, path


def test_v3_was_committed_before_the_resumed_session_and_over_what_it_pins():
    """Read off disk, not through the `record` fixture: that fixture is v4 now, and v3 is a link in
    the chain whose producer is gone. Two artifacts existed when it landed — the first session's
    record and its dump."""
    already = json.loads((REPO_ROOT / V3).read_text(encoding="utf-8"))["resume"]["bought_already"]
    registered_over(
        V3,
        {
            already["run_record"]["path"]: already["run_record"]["sha256"],
            already["dump"]["path"]: already["dump"]["sha256"],
        },
    )


def test_v4_was_committed_before_the_v4_session_and_over_all_three_artifacts(record):
    """v4's version of the same duty, and the set is THREE files rather than two.

    The refused v3 session left a record — `results/sku_b_positions_v3.json` — and it is a sku-b run
    artifact like the other two, so a copy of v3's check would fail here for the honest reason that
    the tree has grown. Pinned instead: v4's population claim rests on that record saying the
    session bought nothing, and this is where "it had not moved when we registered against it" is
    proved. There is no `sku_b_positions_v3.jsonl` — a session refused before the first gold call
    writes no dump, which is why the expected set is three and not four.
    """
    already = record["resume"]["bought_already"]
    refused = record["supersedes"]["refused_record"]
    registered_over(
        V4,
        {
            already["run_record"]["path"]: already["run_record"]["sha256"],
            already["dump"]["path"]: already["dump"]["sha256"],
            refused["path"]: refused["sha256"],
        },
    )


def test_every_superseded_registration_is_sealed_and_this_record_names_its_parent(record):
    """v1 and v2 are what was registered, and neither is edited by the re-registration that follows
    it — the c82d0cff pattern: the bytes are the evidence, so they are hashed here rather than
    described.

    The live pin-test above now runs against v3; this is the other half, and without it the phrase
    "v2 is untouched" would rest on nobody checking. It is also the moment v2 stops being
    rebuildable: the producer points at v3 now, so this literal sha is v2's only witness.
    """
    for path, sha in SEALED.items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert prereg.RECORD.name == "sku_pilot_prereg_v4.json"
    assert record["supersedes"]["record"] == V3
    assert record["supersedes"]["sha256"] == SEALED[V3]
    assert "nothing in `resume` moves" in record["supersedes"]["reason"]
    # the whole chain, each link naming the one before it by the bytes that were registered
    for child, parent in ((V3, V2), (V2, V1)):
        body = json.loads((REPO_ROOT / child).read_text(encoding="utf-8"))
        assert body["supersedes"]["record"] == parent
        assert body["supersedes"]["sha256"] == SEALED[parent]


def test_v2_carries_v1s_bars_and_readings_byte_for_byte():
    """The whole point of a re-registration: the pins move and the CONTRACT does not.

    Compared leaf by leaf rather than field by field, because "verbatim" is a property of every
    string in those sections and a spot-check of three of them would pass while a fourth drifted.
    The two ladder/manifest shas are the declared exceptions and are asserted to BE the differences,
    not merely allowed to differ.

    Both records are read off disk rather than through the live `record` fixture: that fixture is
    v3 now, and this test is about a link in the chain that no longer has a producer.
    """
    v1 = json.loads((REPO_ROOT / V1).read_text(encoding="utf-8"))
    v2 = json.loads((REPO_ROOT / V2).read_text(encoding="utf-8"))

    differ = []
    for section in ("bars", "attempts", "ratification_required", "not_in_scope", "instruments"):
        old = dict(leaves(v1[section], section))
        new = dict(leaves(v2[section], section))
        assert set(old) == set(new), section
        differ += [path for path in old if old[path] != new[path]]
    assert sorted(differ) == [
        "bars.text_tier_accuracy.gold.ladder_sha256",
        "bars.text_tier_accuracy.gold.manifest_sha256",
    ]


FROZEN_SECTIONS = (
    "bars",
    "ratification_required",
    "not_in_scope",
    "instruments",
    "ladder",
    "pinned_inputs",
)
"""What a re-registration may never move. `pinned_inputs` is compared as a mapping rather than as a
key set, because the key-set assertion elsewhere would pass a pin whose VALUE had moved — which is
the only way a pinned input can betray a bar."""


def test_v3_carries_v2s_measurement_byte_for_byte_and_moves_only_the_attempt():
    """SPEC 3.17 (11)(b): the instrument is FROZEN as registered. So the resume may move the ATTEMPT
    and nothing that decides a number. Both records off disk — v3's producer is gone.
    """
    v2 = json.loads((REPO_ROOT / V2).read_text(encoding="utf-8"))
    v3 = json.loads((REPO_ROOT / V3).read_text(encoding="utf-8"))
    for section in FROZEN_SECTIONS:
        assert v3[section] == v2[section], section

    old = dict(leaves(v2["attempts"], "attempts"))
    new = dict(leaves(v3["attempts"], "attempts"))
    assert set(old) == set(new), "the attempt clause gains no field and loses none"
    assert sorted(path for path in old if old[path] != new[path]) == [
        "attempts.cap_usd",
        "attempts.verbatim",
    ]
    assert set(v3) - set(v2) == {"resume"}
    assert set(v2) - set(v3) == set()
    assert len(v3["supersedes"]["moved"]) == 4


def test_v4_carries_v3s_whole_measurement_and_moves_only_the_cap_and_the_two_names(record):
    """SPEC 3.17 (12): v3's session was refused BEFORE the first gold call, so it measured nothing a
    bar can read and there is nothing for a re-registration to reflect.

    That makes this comparison stricter than the last one: `resume` is in the frozen list too. The
    population, the (11)(c) warm-up pins and `bought_already`'s 17 of 138 are the same bytes v3
    carried, because the same 17 answers are still the only ones bought. What is allowed to move is
    the cap and the two names that decide which anchor it is enforced against — (12)(a) and (12)(b),
    the Dv167 finding — and `attempts.authority` beside them, which says where the $0.65 comes from
    given that the clause it sits under is still (11)'s. If this list ever comes out longer than the
    three entries `supersedes.moved` enumerates, the re-registration is doing something (12) did not
    authorise.
    """
    v3 = json.loads((REPO_ROOT / V3).read_text(encoding="utf-8"))
    for section in (*FROZEN_SECTIONS, "resume"):
        assert record[section] == v3[section], section

    old = dict(leaves(v3["attempts"], "attempts"))
    new = dict(leaves(record["attempts"], "attempts"))
    assert sorted(set(new) - set(old)) == [
        "attempts.authority",
        "attempts.ledger",
        "attempts.phase",
    ]
    assert set(old) - set(new) == set(), "the attempt clause loses no field"
    assert [path for path in old if old[path] != new[path]] == ["attempts.cap_usd"]
    assert (v3["attempts"]["cap_usd"], record["attempts"]["cap_usd"]) == (0.45, 0.65)
    assert set(record) == set(v3), "no section is added or dropped"
    assert len(record["supersedes"]["moved"]) == 3
    assert record["supersedes"]["moved_metadata"], "what necessarily moved is named, not omitted"

    # (11)(d)'s $0.45 is SUPERSEDED and not overwritten: it stays in the resume block as the reading
    # v3 ran under, and the record says so in one place a reader will reach from either direction
    assert "$0.45" in record["resume"]["readings"]["d"]
    assert "supersedes (11)(d)'s $0.45 without overwriting it" in record["attempts"]["authority"]


def test_the_refused_session_is_pinned_and_read_not_merely_quoted(record):
    """v4's population is 121 because the v3 session bought nothing. That is a claim about the
    CONTENTS of a file, and a sha does not check contents — so both halves are asserted here.
    """
    refused = record["supersedes"]["refused_record"]
    body = json.loads((REPO_ROOT / refused["path"]).read_bytes())
    assert (
        hashlib.sha256((REPO_ROOT / refused["path"]).read_bytes()).hexdigest() == refused["sha256"]
    )
    assert body["stopped_before_gold"] is True
    assert body["population"]["asked"] == 0 == refused["asked"]
    assert body["dump"]["path"] is None, "a session refused before gold writes no dump"
    # and the population it leaves is the one v4 registers, unchanged from v3
    assert record["resume"]["population"]["to_buy"] == len(body["population"]["unbought"]) == 121


def test_a_v3_record_that_had_bought_something_stops_the_write(monkeypatch, tmp_path):
    """The control for the check above: it is only worth having if it fires. A refusal record whose
    session reached the gold means elements carry answers this registration does not know about, and
    the v4 run would buy them twice."""
    bought = json.loads(prereg.REFUSED.read_text(encoding="utf-8"))
    bought["stopped_before_gold"] = False
    bought["population"]["asked"] = 3
    fake = tmp_path / "sku_b_positions_v3.json"
    fake.write_text(json.dumps(bought, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(prereg, "REFUSED", fake)
    with pytest.raises(SystemExit, match="would buy them twice"):
        prereg.main(["--out", str(tmp_path / "p.json")])


def test_the_resume_warm_up_is_real_full_size_and_outside_every_gold_set(record):
    """SPEC 3.17 (11)(c), and the reason it exists: the first session priced 138 gold calls off a
    generated 64x64 image that answered in 1.436 s, and the pages cost 5.0772 s each.

    The probe is now fixed on the axis that moves the number — a real leaflet page, a real collected
    row — and must stay unrepresentative on the axis that must not move. That second half is what is
    checked hardest here: a seed-42 pick that quietly landed inside the 108 sent pages or inside the
    30-row pack would spend a warm-up on a scored input and contaminate the denominator the resume
    exists to complete. Stability is checked too, because a pick that is not reproducible is not a
    registration.
    """
    warmup = record["resume"]["warmup"]
    reference = json.loads(
        (REPO_ROOT / "results" / "sku_reference_leaflet.json").read_text("utf-8")
    )
    manifest = json.loads(
        (REPO_ROOT / "results" / "sku_text_pack_manifest.json").read_text(encoding="utf-8")
    )

    sent = {page["file"] for post in reference["posts"] for page in post["pages_sent"]}
    unsent = {file for post in reference["posts"] for file in post["pages_not_sent"]}
    assert len(sent) == 108 and len(unsent) == 51
    assert warmup["page"]["file"] in unsent
    assert warmup["page"]["file"] not in sent, "the warm-up page is inside R2's registered gold set"
    page = REPO_ROOT / warmup["page"]["file"]
    assert hashlib.sha256(page.read_bytes()).hexdigest() == warmup["page"]["sha256"]
    assert warmup["page"]["bytes"] > 100_000, "a real leaflet page, not a thumbnail"

    assert warmup["text"]["id"] not in set(manifest["ids"])
    frame = {
        row["id"] for row in json.loads((REPO_ROOT / prereg.CENSUS).read_text("utf-8"))["rows"]
    }
    assert warmup["text"]["id"] in frame, "the warm-up row is one the pre-filter actually passed"

    again = prereg.resume_warmup(reference, manifest)
    assert again["page"]["file"] == warmup["page"]["file"]
    assert again["text"]["id"] == warmup["text"]["id"]
    assert again["text"]["text_sha256"] == warmup["text"]["text_sha256"]
    assert warmup["seed"] == 42


def test_the_bought_already_block_partitions_the_registered_population(record):
    """SPEC 3.17 (11)(a): each element is bought EXACTLY ONCE across the program. The resumed
    session's population is this block's `unbought` and nothing else, so the two lists have to
    partition the registered 138 — not merely add up to it."""
    already = record["resume"]["bought_already"]
    run = json.loads((REPO_ROOT / already["run_record"]["path"]).read_text(encoding="utf-8"))
    asked, unbought = set(already["asked"]), set(already["unbought"])
    assert len(asked) == already["n_asked"] == 17
    assert len(unbought) == already["n_unbought"] == 121
    assert not asked & unbought
    assert len(asked | unbought) == 138
    assert asked == {row["source"] for row in run["outcomes"]}
    assert unbought == set(run["population"]["unbought"])
    assert record["resume"]["population"] == {
        "registered": 138,
        "already_bought": 17,
        "to_buy": 121,
        "why": record["resume"]["population"]["why"],
    }
    for path, sha in (
        (already["run_record"]["path"], already["run_record"]["sha256"]),
        (already["dump"]["path"], already["dump"]["sha256"]),
        (already["serving_pin"]["path"], already["serving_pin"]["sha256"]),
        (already["bought_under"]["path"], already["bought_under"]["sha256"]),
    ):
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    # the parse refusal is an ANSWER that was paid for; (11)(a) makes it enter the bars as it stands
    assert already["unreadable"] == run["extraction"]["unreadable"]


def test_a_run_record_that_moved_stops_the_re_registration(tmp_path, monkeypatch):
    """The negative control for the block above, driven both ways.

    A resume registered against a record that has since moved would pin evidence nobody can
    re-derive, and a record whose asked and unbought sets overlap cannot say which elements are
    still to buy. Both are refusals in the producer rather than findings in the report.
    """
    run = json.loads(prereg.RUN_RECORD.read_text(encoding="utf-8"))

    def rewritten(section: str, value: dict):
        body = json.loads(json.dumps(run)) | {section: value}
        path = tmp_path / "moved.json"
        path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        monkeypatch.setattr(prereg, "RUN_RECORD", path)

    rewritten("dump", dict(run["dump"], sha256="0" * 64))
    with pytest.raises(SystemExit, match="as it now hashes"):
        prereg.bought_already()

    rewritten("population", dict(run["population"], unbought=[run["outcomes"][0]["source"]]))
    with pytest.raises(SystemExit, match="EXACTLY ONCE"):
        prereg.bought_already()

    # the control: the record as it stands passes the same path
    monkeypatch.undo()
    assert prereg.bought_already()["n_unbought"] == 121


def test_the_ladder_rename_is_a_bijection_and_moved_no_rung(record):
    """SPEC 3.17 (8) renamed the schema's fifth presence field; bar 3 reads the LADDER, so the
    question the operator signs off is not "did the hash change" — it did, by design — but "did any
    row change its rung". Substring-safe: none of brand/line/category/size contains `fat`."""
    v1 = json.loads((REPO_ROOT / "results" / "sku_pilot_prereg.json").read_text(encoding="utf-8"))
    renamed = {key.replace("fat", "attribute"): rung for key, rung in v1["ladder"]["table"].items()}
    assert renamed == record["ladder"]["table"] == positions.ladder_table()
    assert record["ladder"]["sha256"] != v1["ladder"]["sha256"]
    assert len(record["ladder"]["table"]) == 32
    # the 32 keys also re-sort — `attribute` sorts before `brand` — and the hash does not notice,
    # because ladder_sha256 dumps with sort_keys=True. Said here so a reader diffing the two tables
    # does not read the reordering as a change.
    assert list(record["ladder"]["table"]) == sorted(record["ladder"]["table"])


def test_nothing_here_carries_a_bar_result(record):
    """The other half, and it holds after sku-b runs too: a pre-registration states thresholds and
    procedures, and a `measured` field in it would make the file its own scorer."""
    for name, bar in record["bars"].items():
        assert not {"measured", "value", "verdict", "result"} & set(bar), name
    assert "verdict" not in record
    for path in (REPO_ROOT / "results").glob("sku_*.json"):
        if path.name.startswith("sku_pilot_") and f"results/{path.name}" not in PREREGS:
            continue  # sku-b's own records may carry verdicts; a pre-registration never may
        body = json.loads(path.read_text(encoding="utf-8"))
        assert "verdict" not in body, path.name


def test_the_record_rebuilds_identically_apart_from_its_timestamp(tmp_path):
    out = tmp_path / "prereg.json"
    assert prereg.main(["--out", str(out)]) == 0
    a, b = (json.loads(path.read_text(encoding="utf-8")) for path in (out, prereg.RECORD))
    for body in (a, b):
        body.pop("generated_at"), body.pop("git")
    assert a == b
