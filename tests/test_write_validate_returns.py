"""The sitting's returns: what came back, and every way the record refuses to answer another pack.

The verdicts are the operator's and nothing here re-scores them. What is tested is the JOIN — that
these verdicts are attached to the rows the operator actually saw — because a returns record whose
pack moved under it is indistinguishable from a correct one by reading it.

Every structural refusal below re-pins `PACK_SHA256` to the fixture it built. Without that the
sha guard fires first and each test passes for the wrong reason.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import write_validate_returns as writer  # noqa: E402

RECORD = json.loads(
    (REPO_ROOT / "results" / "validate_5c2_returns.json").read_text(encoding="utf-8")
)
PACK = json.loads((REPO_ROOT / "results" / "validate_5c2_pack.json").read_text(encoding="utf-8"))


def forged(tmp_path, monkeypatch, mutate) -> Path:
    """A copy of the pack with one thing changed, and the sha guard re-pinned to it."""
    pack = json.loads(json.dumps(PACK))
    mutate(pack)
    path = tmp_path / "validate_5c2_pack.json"
    path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(writer, "PACK_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    return path


# --- what came back -----------------------------------------------------------------------------


def test_the_record_answers_the_pack_the_sitting_read():
    answers = RECORD["answers"]

    assert answers["pack"] == "results/validate_5c2_pack.json"
    assert (
        answers["sha256"]
        == writer.PACK_SHA256
        == (
            hashlib.sha256(
                (REPO_ROOT / "results" / "validate_5c2_pack.json").read_bytes()
            ).hexdigest()
        )
    )
    assert answers["seed"] == PACK["seed"] == 42


def test_every_slot_the_pack_printed_carries_a_verdict_and_all_of_them_are_ratified():
    """47 slots, resolved against the pack's own keys rather than against a count typed here."""
    resolved = RECORD["resolved"]
    slots = {name: set(group) for name, group in resolved.items()}

    assert slots == {
        name: set(group) for name, group in PACK["findings"].items() if name != "verdicts"
    }
    assert sum(len(group) for group in resolved.values()) == 47 == RECORD["totals"]["slots"]
    assert RECORD["totals"]["tally"] == {"ratified": 47}
    assert {slot["verdict"] for group in resolved.values() for slot in group.values()} == {
        "ratified"
    }
    assert all(
        slot["verdict"] in PACK["findings"]["verdicts"]
        for group in resolved.values()
        for slot in group.values()
    )


def test_the_two_halves_are_ratified_and_the_sitting_issued_no_order():
    """Zero disputed is REPORTED, not left out: an absent field reads as a question nobody asked."""
    halves, totals = RECORD["halves"], RECORD["totals"]

    assert halves["leaflet"]["verdict"] == "ratified"
    assert (halves["leaflet"]["posts"], halves["leaflet"]["positions"]) == (6, 36)
    assert halves["comment"]["verdict"] == "ratified"
    assert halves["comment"]["comments"] == halves["comment"]["of"] == 5
    assert totals["disputed"] == 0 and totals["orders_issued"] == 0 and totals["orders"] == []


def test_the_verbatim_is_the_contracts_own_words_and_is_not_translated():
    """Grepped back at its source, whitespace normalised — the line wraps in the contract."""
    contract = (REPO_ROOT / "docs" / "PROMPT-5c2-close.md").read_text(encoding="utf-8")
    quote = RECORD["halves"]["leaflet"]["verbatim"]

    assert quote == "распознавание SKU идеальное"
    assert " ".join(quote.split()) in " ".join(contract.split())
    assert RECORD["halves"]["leaflet"]["verbatim_language"] == "ru"
    assert "PROMPT-5c2-close.md" in RECORD["halves"]["leaflet"]["verbatim_source"]


def test_the_operator_time_is_null_because_nothing_relayed_one():
    """A plan is not a measurement. `docs/STATUS.md` named ~45 minutes BEFORE the sitting and no
    actual came back, so the field is empty and says why — a plausible number written here would be
    this executor's invention wearing the operator's name."""
    sitting = RECORD["sitting"]

    assert sitting["operator_minutes"] is None
    assert "plan is not a measurement" in sitting["operator_minutes_note"]
    assert sitting["held"] == "2026-08-14"


def test_the_ruling_is_referenced_and_never_restated():
    """The sitting produced one ruling and it is LAW, so the record points at it.

    The negative leg is the one that matters: no clause of 3.19 is copied in, because two copies of
    a law drift on the first correction and the SPEC is the one that binds.
    """
    spec = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
    dump = json.dumps(RECORD, ensure_ascii=False)

    assert RECORD["ruling"]["amendment"] == "3.19"
    assert writer.MARKER in spec
    assert "Text-less comments are SKIPPED before payment" in spec
    assert "Text-less comments are SKIPPED before payment" not in dump
    assert "Reporting denominators follow the rule" in spec
    assert "Reporting denominators follow the rule" not in dump


# --- the refusals -------------------------------------------------------------------------------


def test_a_pack_that_moved_under_the_record_is_refused(tmp_path):
    """The strongest one: the pack is DRAWN, so a redraw is the same filename and other rows."""
    path = tmp_path / "validate_5c2_pack.json"
    path.write_text(json.dumps(PACK | {"seed": 43}, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(SystemExit, match="the sitting read"):
        writer.build(path)


def test_a_slot_the_pack_never_printed_is_refused(tmp_path, monkeypatch):
    """A verdict on a row that was not on the table. The count still matches — the id does not."""

    def rename_one(pack):
        slots = pack["findings"]["positions"]
        victim = next(iter(slots))
        slots[f"{victim}:ghost"] = slots.pop(victim)

    with pytest.raises(SystemExit, match="not the .positions. rows it printed"):
        writer.build(forged(tmp_path, monkeypatch, rename_one))


def test_a_group_larger_than_the_sitting_ruled_on_is_refused(tmp_path, monkeypatch):
    """Both the skeleton and the printed rows grow, so only the SIZE is wrong.

    This is what makes «the half was ratified» a bounded statement: the operator ruled on 36
    positions and a 37th is not covered by it, however consistent the pack is with itself.
    """

    def add_a_row(pack):
        block = pack["leaflet_posts"][0]
        extra = json.loads(json.dumps(block["positions"][0]))
        extra["row_id"] = f"{extra['row_id']}:extra"
        block["positions"].append(extra)
        pack["findings"]["positions"][extra["row_id"]] = {"verdict": "", "note": ""}

    with pytest.raises(SystemExit, match="the sitting ruled on 36"):
        writer.build(forged(tmp_path, monkeypatch, add_a_row))


def test_a_pack_whose_skeleton_is_already_filled_is_refused(tmp_path, monkeypatch):
    """The team lead's ruling: the returns are a new record and the pack is never written over."""

    def fill_one(pack):
        first = next(iter(pack["findings"]["comments"]))
        pack["findings"]["comments"][first] = {"verdict": "ratified", "note": "by someone"}

    with pytest.raises(SystemExit, match="ships every slot EMPTY"):
        writer.build(forged(tmp_path, monkeypatch, fill_one))


def test_a_group_nobody_ruled_on_is_refused(tmp_path, monkeypatch):
    def add_a_group(pack):
        pack["findings"]["captions"] = {"@c:1": {"verdict": "", "note": ""}}

    with pytest.raises(SystemExit, match="the sitting ruled on"):
        writer.build(forged(tmp_path, monkeypatch, add_a_group))


def test_a_verdict_form_the_pack_does_not_carry_is_refused(tmp_path, monkeypatch):
    """The form has to mean the same thing on both sides of the table."""

    def narrow_the_forms(pack):
        pack["findings"]["verdicts"] = ["accepted", "disputed"]

    with pytest.raises(SystemExit, match="is not one of the pack's own"):
        writer.build(forged(tmp_path, monkeypatch, narrow_the_forms))


def test_a_dispute_on_a_row_the_pack_does_not_carry_is_refused(monkeypatch):
    """The other direction of the dispute map: it is empty today and it is not a decoration."""
    monkeypatch.setattr(writer, "DISPUTED", {"@nobody:1": "a note about nothing"})

    with pytest.raises(SystemExit, match="which the pack does not carry"):
        writer.build(writer.PACK)


def test_a_dispute_lands_on_its_row_and_leaves_the_rest_ratified(monkeypatch):
    """The control for the test above — the map WORKS, so its emptiness is a fact about the
    sitting and not about a producer that can only ratify."""
    victim = next(iter(PACK["findings"]["comments"]))
    monkeypatch.setattr(writer, "DISPUTED", {victim: "this one is sarcasm"})

    resolved = writer.resolve(PACK)

    assert resolved["comments"][victim] == {"verdict": "disputed", "note": "this one is sarcasm"}
    assert writer.tally(resolved) == {"disputed": 1, "ratified": 46}


def test_a_ruling_that_is_not_in_the_spec_is_refused(tmp_path, monkeypatch):
    """A reference to nothing would leave the sitting's one ruling written down nowhere."""
    stripped = tmp_path / "SPEC.md"
    spec = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
    stripped.write_text(spec.replace(writer.MARKER, "<!-- amendment-3.19-was-here"), "utf-8")
    monkeypatch.setattr(writer, "SPEC", stripped)

    with pytest.raises(SystemExit, match="carries no .* block"):
        writer.build(writer.PACK)


def test_a_verbatim_the_contract_does_not_carry_is_refused(monkeypatch):
    monkeypatch.setattr(writer, "VERBATIM", "распознавание SKU превосходное")

    with pytest.raises(SystemExit, match="does not carry"):
        writer.build(writer.PACK)


# --- house hygiene ------------------------------------------------------------------------------


def test_the_record_carries_no_clock_and_names_its_producer():
    assert "generated_at" not in RECORD and "git" not in RECORD and "at" not in RECORD
    assert (
        RECORD["producer"]["sha256"]
        == hashlib.sha256(Path(writer.__file__).read_bytes()).hexdigest()
    )
    assert RECORD["producer"]["borrows"] == {}
    assert "imports no module of this repo" in RECORD["producer"]["borrows_note"]


def test_two_writes_of_the_same_inputs_are_byte_identical(tmp_path):
    """The determinism pair. A record with a clock in it would fail here on the second."""
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    writer.main(["--out", str(first)])
    writer.main(["--out", str(second)])

    assert first.read_bytes() == second.read_bytes()
    assert (
        hashlib.sha256(first.read_bytes()).hexdigest()
        == hashlib.sha256(
            (REPO_ROOT / "results" / "validate_5c2_returns.json").read_bytes()
        ).hexdigest()
    ), "the shipped record is not what the producer writes today"
