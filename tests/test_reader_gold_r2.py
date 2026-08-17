"""`results/reader_gold_w1_r2.json` — one ruling, one word, twelve cells, and nothing else.

The revision is worth what its re-derivation is worth, and there are two things to re-derive: that
the file rebuilds byte for byte, and that the ONLY thing it changes about v1 is the twelve
`subject_type` cells the sitting's ruling 4 reaches. The second is checked against v1 rebuilt TODAY
rather than against the committed v1 — the committed one carries sealed shas that MOVED under a
later contract, and diffing against it would report those as changes this revision made.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_census_w1 as census  # noqa: E402
import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_gold as gold  # noqa: E402
import write_reader_gold_r2 as r2  # noqa: E402
from test_prompts import assert_pinned, put_the_sealed_shas_back  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
V1_PATH = REPO_ROOT / "results" / "reader_gold_w1.json"
V1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
RULING = " ".join(r2.RULING.read_text(encoding="utf-8").split())


def cells_reading(record, word: str, path: str = "") -> list[str]:
    """Every `subject_type` cell in a document that holds `word` — the walk, stated once."""
    if isinstance(record, dict):
        return [
            f"{path}.{key}"
            for key, value in record.items()
            if key == "subject_type" and value == word
        ] + [
            one
            for key, value in record.items()
            if key != "subject_type"
            for one in cells_reading(value, word, f"{path}.{key}")
        ]
    if isinstance(record, list):
        return [
            one
            for index, value in enumerate(record)
            for one in cells_reading(value, word, f"{path}[{index}]")
        ]
    return []


def test_the_committed_r2_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it."""
    out = tmp_path / "again.json"
    assert r2.main(["--out", str(out)]) == 0
    # `producer.borrowed` is hashed LIVE and `src/market_pulse/prompts.py` moved when the v5 reader
    # text was registered. This gold is one of the artefacts a spent registration froze, so it is
    # NOT re-pinned: the one byte range allowed to differ is put back to the sealing commit's, and
    # the swap must fire — once, since this record names the module in `producer.borrowed` alone
    assert put_the_sealed_shas_back(out.read_bytes(), times=1) == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_r2_is_v1_rebuilt_today_with_twelve_cells_relabelled_and_nothing_else():
    """The claim the contract makes in so many words — «Nothing else changes: same rows, same
    msg-ids, same reachability block» — checked as a DIFF and not as a description.

    v1 is rebuilt here rather than read from disk: the committed v1 pins `prompts.py` and the plan
    at shas a later contract moved, so a diff against the file would attribute those to this
    revision. Rebuilt, the two documents differ in exactly the cells the ruling reaches, plus the
    two blocks this producer adds and replaces on purpose.
    """
    fresh = gold.build(
        population.population(),
        gold.evidence_index(),
        census.raw_posts(),
        population.window(),
        population.gate(),
    )
    # counted by a walk written HERE, before the producer's own is allowed to run: a count taken
    # from `relabel` would be the producer agreeing with itself
    assert len(cells_reading(fresh, r2.COLLAPSED)) == r2.CELLS == 12
    assert cells_reading(fresh, r2.RATIFIED) == cells_reading(V1, r2.RATIFIED), "v1 is not rebuilt"

    changed = r2.relabel(fresh)
    assert sorted(changed) == RECORD["revision"]["cells"]
    # the two blocks this producer owns are grafted on; every other byte has to already match
    rebuilt = fresh | {key: RECORD[key] for key in ("revision", "producer")}
    assert json.dumps(rebuilt, ensure_ascii=False, indent=2, sort_keys=True) + "\n" == (
        RECORD_PATH.read_text(encoding="utf-8")
    )
    assert set(RECORD) - set(V1) == {"revision"}


def test_the_word_is_gone_from_the_cells_and_still_there_in_v1():
    """Both directions, because either alone passes for the wrong reason: no cell reading the
    collapsed word in r2 says the relabel ran, and twelve of them still reading it in v1 says the
    revision is a NEW file and not an edit to the one two sealed registrations pin."""
    assert cells_reading(RECORD, r2.COLLAPSED) == []
    assert len(cells_reading(V1, r2.COLLAPSED)) == 12
    assert len(cells_reading(RECORD, r2.RATIFIED)) == len(cells_reading(V1, r2.RATIFIED)) + 12
    # and the prose that DISCUSSES the word is untouched — the walk is typed, not textual
    assert r2.COLLAPSED in json.dumps(RECORD, ensure_ascii=False)
    assert V1["derivation"]["per_comment_rule"] == RECORD["derivation"]["per_comment_rule"]


def test_the_ruling_is_quoted_verbatim_from_the_record_that_carries_it():
    """A ruling quoted from memory is a ruling nobody checked ([[verbatim_quotes_must_be_grepped]]).
    Each quoted phrase is grepped back into the ADR whitespace-normalised, which is the same
    treatment `write_reader_gold.assert_transcribed` gives the team lead's reference."""
    said = RECORD["revision"]["ruling"]
    assert said["record"] == "knowledge/decisions/reader-sitting-16-08.md"
    assert said["which"].startswith("ruling 4")
    assert said["operator_words"], "a ruling block with no quote proves nothing"
    for quote in said["operator_words"]:
        assert quote in RULING, quote


def test_the_reference_did_not_move_and_v1_is_named_by_its_live_sha():
    """Ruling 4's other half: «pins do not move for a vocabulary reading». The reference this gold
    is transcribed from is hashed LIVE, so an edit to it reddens here rather than being absorbed."""
    source = RECORD["revision"]["source"]
    assert source["docs/REFERENCE-signals-w1.md"] == summary.sha256_of(gold.REFERENCE)
    assert RECORD["revision"]["supersedes"]["record"] == "results/reader_gold_w1.json"
    assert RECORD["revision"]["supersedes"]["sha256"] == summary.sha256_of(V1_PATH)


def test_the_producer_names_itself_and_borrows_the_one_that_wrote_the_rows():
    """A record whose `producer.sha256` pointed at `write_reader_gold.py` would name a script that
    never wrote it; one that dropped that script would lose the producer of every row in it."""
    producer = RECORD["producer"]
    assert producer["script"] == "scripts/write_reader_gold_r2.py"
    assert producer["sha256"] == summary.sha256_of(REPO_ROOT / producer["script"])
    assert producer["borrowed"]["scripts/write_reader_gold.py"] == summary.sha256_of(
        REPO_ROOT / "scripts" / "write_reader_gold.py"
    )
    for name, digest in producer["borrowed"].items():
        assert_pinned(name, digest)
