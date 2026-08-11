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


def test_a_paraphrased_bar_stops_the_write(monkeypatch, tmp_path):
    """The negative control: the check is only worth having if it fires on a reworded bar."""
    monkeypatch.setitem(prereg.BARS, "text_tier_accuracy", "text tier accuracy at least 0.85")
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
    assert record["attempts"]["count"] == 1
    assert record["attempts"]["cap_usd"] == 0.35
    assert "BY MEASUREMENT" in record["attempts"]["on_failure"]
    assert "No retry" in record["attempts"]["on_failure"]


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
    assert prereg.RATIFICATION_NAME.findall(spec_text) == [
        "sku-b-ratification",
        "sku-b-ratification-2",
        "sku-b-ratification-3",
    ]
    law = prereg.registered_law(prereg.SPEC).decode("utf-8")
    assert "sku-b-ratification-2" not in law
    assert "sku-b-ratification-3" not in law

    for path, sha in record["pinned_inputs"].items():
        if path == "docs/SPEC.md":
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


def test_the_prereg_says_what_it_does_not_touch(record):
    """The 5c3 rulings are the loudest omission: «Варто» and «Селянське» are a named revision and
    applying them here would change what the leaflet gold means mid-contract."""
    out = record["not_in_scope"]
    assert "«Варто» text-matching OFF" in out["the 5c3 rulings"]
    assert "NOT applied" in out["the 5c3 rulings"]
    assert "symmetric" in out["the 141 names"]
    assert "baselines.json" in out["the frozen family"]
    assert "consumer quotes never enter" in out["aggregates"]


PREREGS = ("results/sku_pilot_prereg.json", "results/sku_pilot_prereg_v2.json")


@pytest.mark.parametrize("prereg_path", PREREGS)
def test_the_prereg_was_committed_before_any_pilot_artifact(record, prereg_path):
    """A pre-registration written after the thing it judges is a rationalisation, and git history is
    the only witness to the ordering — so the claim is checked against history rather than against
    today's directory listing, which stops being evidence the moment sku-b writes its records.

    Both records, because v2 re-registers BESIDE v1 and inherits the same duty: the ordering that
    matters is "before the one paid attempt", and each has to be able to prove it on its own.

    The same discipline `run_v22_probe.py` uses: shell out to git, and treat "not tracked" as a
    failure rather than a skip. An uncommitted pre-registration is not one.
    """
    assert "before any sku-b artifact exists" in record["class"]
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


def test_v1_is_sealed_and_this_record_names_it(record):
    """v1 is what was registered on 2026-08-10 and it is not edited by the re-registration — the
    c82d0cff pattern: the bytes are the evidence, so they are hashed here rather than described.

    The live pin-test above now runs against v2; this is the other half, and without it the phrase
    "v1 is untouched" would rest on nobody checking.
    """
    sealed = REPO_ROOT / "results" / "sku_pilot_prereg.json"
    assert hashlib.sha256(sealed.read_bytes()).hexdigest() == (
        "b1bfa40d1f5073ec7b3d199bd57d96dd1bb72f37d99d26135f98386a8473a142"
    )
    assert prereg.RECORD.name == "sku_pilot_prereg_v2.json"
    assert record["supersedes"]["record"] == "results/sku_pilot_prereg.json"
    assert record["supersedes"]["sha256"] == hashlib.sha256(sealed.read_bytes()).hexdigest()
    assert "no bar moved" in record["supersedes"]["reason"]


def test_v2_carries_v1s_bars_and_readings_byte_for_byte(record):
    """The whole point of a re-registration: the pins move and the CONTRACT does not.

    Compared leaf by leaf rather than field by field, because "verbatim" is a property of every
    string in those sections and a spot-check of three of them would pass while a fourth drifted.
    The two ladder/manifest shas are the declared exceptions and are asserted to BE the differences,
    not merely allowed to differ.
    """
    v1 = json.loads((REPO_ROOT / "results" / "sku_pilot_prereg.json").read_text(encoding="utf-8"))

    def leaves(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                yield from leaves(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from leaves(value, f"{path}[{index}]")
        else:
            yield path, node

    differ = []
    for section in ("bars", "attempts", "ratification_required", "not_in_scope", "instruments"):
        old = dict(leaves(v1[section], section))
        new = dict(leaves(record[section], section))
        assert set(old) == set(new), section
        differ += [path for path in old if old[path] != new[path]]
    assert sorted(differ) == [
        "bars.text_tier_accuracy.gold.ladder_sha256",
        "bars.text_tier_accuracy.gold.manifest_sha256",
    ]


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
