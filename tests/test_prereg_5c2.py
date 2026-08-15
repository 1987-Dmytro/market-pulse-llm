"""The 5c2-run pre-registration, pinned BY VALUE — SPEC 3.18 (7)(f).

"The prep-c2 review's finding that the caps table is pinned by inequalities binds here: the
registered cap row gets equality tests, not ceilings." So every registered number below is an `==`,
and `session_cap.fits` — the only inequality in the record — is asserted BESIDE them rather than in
place of them. A suite that carried only `cap <= remaining` would pass on a registration that named
any cap at all under $9.1690, which is the defect the clause was written about.

The refusals are measured through an injected verdict AND against the Makefile, because a producer
whose `make check` branch is only ever driven by a monkeypatch has tested the monkeypatch.
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

import write_prereg_5c2 as writer  # noqa: E402

from market_pulse import evidence  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_5c2_run.json").read_text(encoding="utf-8"))


class Verdict:
    """A `subprocess.run` stand-in that answers with one returncode and remembers the command."""

    def __init__(self, returncode=0, stdout="2211 passed, 2 skipped"):
        self.returncode, self.stdout, self.calls = returncode, stdout, []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, self.returncode, self.stdout, "")


# --- the registered numbers, one equality each --------------------------------------------------


def test_the_three_populations_are_pinned_by_value():
    populations = RECORD["populations"]

    assert populations["comment"]["rows"] == 5075
    assert populations["leaflet_page"]["rows"] == 159
    assert populations["post_text"]["rows"] == 44


def test_the_three_prices_are_pinned_by_value_and_each_names_its_model():
    prices = RECORD["prices"]

    assert prices["comment"]["usd_model"]["value"] == 1.4281
    assert prices["comment"]["seconds_model"]["value"] == 4.262
    assert prices["leaflet_page"]["seconds_model"]["value"] == 4.2794
    assert prices["post_text"]["seconds_model"]["value"] == 2.8132
    # the two legs skub2 measured in SECONDS say so instead of printing a unit cost nothing measured
    assert prices["leaflet_page"]["usd_model"]["value"] is None
    assert prices["post_text"]["usd_model"]["value"] is None
    for leg in prices.values():
        for corner in leg.values():
            assert corner["source"] and corner["why"]


def test_the_session_cap_is_pinned_by_value_and_the_ceiling_is_a_second_assertion():
    """The equality is the pin. The inequality is an extra, and asserting only it would pass any
    cap under the remainder — the c2 review's finding, which 3.18 (7)(f) binds here."""
    cap = RECORD["session_cap"]

    assert cap["cap_usd"] == 8.00
    assert cap["projected_usd_with_drift"] == 7.8546
    assert cap["remaining_usd"] == 9.1690
    assert cap["headroom_usd"] == 1.1690
    assert cap["fits"] is True and cap["cap_usd"] <= cap["remaining_usd"]


def test_the_three_legs_add_up_to_the_projected_total():
    legs = RECORD["legs"]

    assert [legs[name]["usd_with_drift"] for name in ("comment", "leaflet_page", "post_text")] == [
        7.4840,
        0.3125,
        0.0581,
    ]
    assert round(sum(leg["usd_with_drift"] for leg in legs.values()), 4) == 7.8546
    assert round(sum(leg["billed_seconds"] for leg in legs.values()), 1) == 23101.9


def test_the_cap_is_the_projection_rounded_up_to_the_next_half_dollar():
    """Re-derived rather than trusted, and the direction matters: rounding DOWN would name a cap the
    projection already exceeds."""
    cap = RECORD["session_cap"]

    assert cap["cap_usd"] >= cap["projected_usd_with_drift"]
    assert cap["cap_usd"] - cap["projected_usd_with_drift"] < 0.50
    assert cap["cap_usd"] % 0.50 == 0


def test_the_wall_clock_is_registered_beside_the_dollars():
    """A cap that fits in dollars can still name a session the transport cannot run in one sitting —
    one worker, a 900 s execution timeout, and the job count is what makes that visible."""
    whole = RECORD["whole_session"]

    assert whole["billed_seconds"] == 23101.9
    assert whole["hours"] == 6.42
    assert whole["jobs_at_the_execution_timeout"] == 26
    assert whole["workers_max"] == 1


def test_no_single_job_can_bill_past_the_session_cap():
    """SPEC 3.17 (10)(c), against the REGISTERED cap and not the phase cap: the phase cap is a
    larger line several sessions share, and the clause bounds one wedged job against this run."""
    ceiling = RECORD["stop_rules"]["per_job_ceiling"]

    assert ceiling["execution_timeout_s"] == 900.0
    assert ceiling["worst_case_job_usd_with_drift"] == 0.2843
    assert ceiling["against_the_session_cap_usd"] == 8.00
    assert ceiling["satisfied"] is True
    assert ceiling["worst_case_job_usd_with_drift"] == round(
        900.0 * RECORD["rate"]["value"] * 1.03, 4
    )


# --- the selections, not only their sizes -------------------------------------------------------


def test_the_comment_leg_is_pinned_by_the_nineteen_hashes_the_census_records():
    """A hash-of-hashes would be a number no other reader in this repo could rebuild, so the pin is
    the census's own per-channel shape — checked back against the census itself."""
    census = json.loads((REPO_ROOT / "results" / "census_5c2.json").read_text(encoding="utf-8"))
    pin = RECORD["populations"]["comment"]["selection_pin"]

    assert len(pin) == 19
    assert pin == {
        row["handle"]: row["comments"]["ids_sha256"]
        for row in census["channels"]
        if row["comments"] != "CANNOT ANSWER"
    }
    assert (
        sum(row["comments"]["in_window"] for row in census["channels"] if row["handle"] in pin)
        == 5075
    )


def test_the_post_leg_is_pinned_by_which_rows_and_not_only_how_many():
    cut = json.loads((REPO_ROOT / "results" / "postcut_c3b.json").read_text(encoding="utf-8"))
    pin = RECORD["populations"]["post_text"]

    assert pin["selection_pin"] == cut["kept"]["ids_sha256"]
    assert (
        pin["selection_pin"]
        == hashlib.sha256("\n".join(row["id"] for row in cut["rows"]).encode("utf-8")).hexdigest()
    )
    assert pin["cut_from"] == 349 and pin["rows"] == 44


def test_the_leaflet_leg_supersedes_the_c2_projections_78_and_says_so():
    """Two records, two populations, and neither is wrong: 3.18 (7)(d) is what overrides."""
    supersedes = RECORD["populations"]["leaflet_page"]["supersedes"]
    projection = json.loads(
        (REPO_ROOT / "results" / "projection_5c2.json").read_text(encoding="utf-8")
    )

    assert supersedes["was"] == projection["window"]["leaflet_pages_unanswered"] == 78
    assert RECORD["populations"]["leaflet_page"]["rows"] == 159
    assert "3.18 (7)(d)" in supersedes["why"]


def test_a_larger_total_that_fits_is_explained_where_a_reader_meets_it():
    """c2 ends at $7.6870 `fits: false`; this ends at $7.8546 `fits: true`. Without the two
    supersessions named in one place that reads as an arithmetic error."""
    projection = json.loads(
        (REPO_ROOT / "results" / "projection_5c2.json").read_text(encoding="utf-8")
    )
    why = RECORD["whole_session"]["why_it_is_larger_than_the_c2_projection_and_still_fits"]

    assert projection["whole_window"]["usd_with_drift"] == 7.687
    assert projection["whole_window"]["fits"] is False
    assert RECORD["whole_session"]["usd_with_drift"] > 7.687
    assert "78 → 159" in why and "30 → 33" in why


# --- the budget: the field that could not be used -----------------------------------------------


def test_the_remainder_is_derived_from_the_live_cap_and_not_read_off_the_ledger():
    """`sessions[-1].remaining_usd` is 6.1690 and it is TRUE — of the 30 cap it was written beside.
    3.18 (7)(b) forbids re-scoring it, so the producer derives instead, and carries both numbers
    with the cap each answers under. Reading the field would have refused an $8.00 cap that fits."""
    ledger = json.loads((REPO_ROOT / "results" / "spend_phase4.json").read_text(encoding="utf-8"))
    money = RECORD["budget"]
    # BY ITS TIMESTAMP, not by position. The registration names this row — `budget.read_at` — and
    # `sessions[-1]` was the same row only until the next paid session was witnessed. 5c2-run's own
    # Endpoint A entry pushed it off the end, and a positional read would then have compared the
    # sealed numbers against a DIFFERENT row and failed on a ledger that had done nothing wrong.
    named = [row for row in ledger["sessions"] if row["at"] == money["read_at"]]
    assert len(named) == 1, f"{len(named)} sessions at {money['read_at']} — the pin is ambiguous"
    last = named[0]

    assert last["remaining_usd"] == 6.1690, "the field, unchanged and never re-scored"
    assert last["spent_usd"] == 23.8310
    assert money["remaining_usd"] == round(33.00 - last["spent_usd"], 4) == 9.1690
    assert money["ledger_remaining_usd_under_its_own_cap"] == last["remaining_usd"]
    assert money["cap_in_force_when_the_ledger_row_was_written"] == 30.00
    assert money["phase_cap_usd"] == 33.00
    assert 8.00 > last["remaining_usd"], "the cap the ledger's own field would have refused"


# --- the law, the inputs and the strip ----------------------------------------------------------


def test_the_sealed_pin_still_derives_through_the_ten_block_keep():
    """The law grew and the pin survived, which is the design rather than damage to it.

    What this test used to assert — that the pin equals the RAW file, because the keep held every
    block the file carried — was true on the day the registration was written and had a shelf life
    of one amendment. 3.19 ended it. What replaces it is the pair `test_sku_prereg.py` checks its
    own pins with, because either leg alone passes for the wrong reason: a live hash equal to the
    pin would mean 3.19 never landed, and a stripped hash equal to the pin is what proves the
    registered law is the bytes that were registered.

    The keep stays TEN. Growing it to green this file would re-pin a sealed record through
    `pinned_sha256`, which is the one thing the producer's refusals exist to prevent.
    """
    import write_sku_prereg as prereg

    spec = REPO_ROOT / "docs" / "SPEC.md"
    pin = RECORD["pinned_inputs"]["docs/SPEC.md"]

    assert RECORD["strip"]["keep"] == list(writer.KEEP_BLOCKS) == list(writer.BLOCKS_TODAY[:10])
    assert tuple(prereg.RATIFICATION_NAME.findall(spec.read_text(encoding="utf-8"))) == (
        writer.BLOCKS_TODAY
    )
    assert writer.BLOCKS_TODAY[10:] == ("amendment-3.19", "amendment-3.20"), "after the seal"
    assert hashlib.sha256(spec.read_bytes()).hexdigest() != pin, "3.19 is not in the file"
    assert hashlib.sha256(prereg.registered_law(spec, keep=writer.KEEP_BLOCKS)).hexdigest() == pin
    # and the block that carries the stop rules this record cites is one of the ten it keeps
    assert "sku-b-ratification-4" in writer.KEEP_BLOCKS
    assert "3.17 (10)" in json.dumps(RECORD["stop_rules"], ensure_ascii=False)


def test_every_pinned_input_still_hashes_to_what_it_says():
    for path, digest in RECORD["pinned_inputs"].items():
        assert writer.pinned_sha256(REPO_ROOT / path) == digest, path
    assert set(RECORD["pinned_inputs"]) == {
        "docs/SPEC.md",
        "results/census_5c2.json",
        "results/census_c3a_posts.json",
        "results/postcut_c3b.json",
        "results/projection_5c2.json",
        "results/srv2d_cost.json",
        "config/registry.yaml",
        "config/lexicon.yaml",
        "src/market_pulse/positions.py",
    }


def test_the_strip_is_blind_to_3_19_and_to_nothing_the_keep_holds(tmp_path):
    """The other direction of the decoupling, planted on a copy: the bytes of a block that arrived
    AFTER the seal may move under the pin and a KEPT block's may not.

    One line per post-seal block, and each names a phrase that block alone carries — 3.19's
    parenthetical about stickers, 3.20's about the metric dictionary. A loop over
    `BLOCKS_TODAY[10:]` would pass on a strip that had stopped finding either of them.

    Without this the reformulation above would be satisfied by a strip that hides the whole file,
    and the pin would have stopped being a pin. `docs/SPEC.md` itself is never written to — every
    edit here is made to a copy in `tmp_path`.
    """
    import write_sku_prereg as prereg

    pin = RECORD["pinned_inputs"]["docs/SPEC.md"]
    text = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")

    def derived(edited: str) -> str:
        copy = tmp_path / "SPEC.md"
        copy.write_text(edited, encoding="utf-8")
        return hashlib.sha256(prereg.registered_law(copy, keep=writer.KEEP_BLOCKS)).hexdigest()

    assert derived(text) == pin, "the control: an unedited copy derives the pin"
    assert derived(text.replace("stickers, photos, voice notes", "stickers and photos")) == pin
    assert derived(text.replace("one home for names, formulas", "one home for the names")) == pin
    for kept in ("**Amendment 3.18", "amendment 3.15 (the vis program moves"):
        assert text.count(kept) == 1
        assert derived(text.replace(kept, kept + " ")) != pin, kept


def test_a_twelfth_marked_block_is_refused_rather_than_stripped(monkeypatch, tmp_path):
    """The negative control for the strip: a block whose name the family MATCHES would be cut out of
    the registered law silently, so the producer refuses on the block set rather than on the names
    it happens to know.

    The intruder was `amendment-3.19`, then `amendment-3.20`, and each time that name became law it
    moved on. It has to: a second block under a name the producer already knows would test DUPLICATE
    detection, and what is being tested is that a name nobody has looked at cannot arrive quietly.
    The second line is the direction that keeps this a control rather than a refusal that refuses
    everything: the file as it stands must still pass.
    """
    grown = tmp_path / "SPEC.md"
    grown.write_text(
        (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
        + "<!-- amendment-3.21 begin -->\n(1) whatever.\n<!-- amendment-3.21 end -->\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="add its name here and look at it"):
        writer.check_the_strip_family_is_what_it_says(grown)
    writer.check_the_strip_family_is_what_it_says(REPO_ROOT / "docs" / "SPEC.md")


# --- the refusals -------------------------------------------------------------------------------


def test_the_registration_refuses_while_the_suite_is_red(tmp_path):
    red = Verdict(returncode=1, stdout="1 failed, 2210 passed")

    with pytest.raises(SystemExit, match="exited 1"):
        writer.main(["--out", str(tmp_path / "prereg.json")], run=red)

    assert not (tmp_path / "prereg.json").exists(), "a refused registration wrote nothing"
    assert red.calls[0][0] == writer.CHECK


def test_the_command_the_refusal_runs_is_the_makefiles_own_verifier():
    """The injected verdict proves the BRANCH and says nothing about the command, so the command is
    checked against the file that defines it."""
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert writer.CHECK == ("make", "check")
    assert "\ncheck:\n" in makefile
    body = makefile.split("\ncheck:\n")[1].split("\n\n")[0]
    assert "ruff check ." in body and "pytest -q" in body
    assert RECORD["verifier"]["command"] == "make check"
    assert RECORD["verifier"]["green"] is True and RECORD["verifier"]["returncode"] == 0


def test_the_registration_refuses_when_the_cut_was_computed_over_another_census(
    monkeypatch, tmp_path
):
    """The chain this record inherits and cannot see: the D cut names the census it read."""
    stale = tmp_path / "postcut.json"
    cut = json.loads((REPO_ROOT / "results" / "postcut_c3b.json").read_text(encoding="utf-8"))
    cut["input"]["sha256"] = "0" * 64
    stale.write_text(json.dumps(cut, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(writer, "POSTCUT", stale)

    with pytest.raises(SystemExit, match="does not belong to the census this registration pins"):
        writer.check_the_inputs_have_not_moved(tmp_path / "nothing.json")


def test_the_registration_refuses_when_a_producer_moved_under_its_own_record(monkeypatch, tmp_path):
    """9c723a7's finding as a guard: a record names the code that wrote it, so an edit to that code
    after the record was written is caught here rather than at the sitting.

    Driven through the CUT rather than the census, so the census-identity guard above cannot fire
    first and pass this test for the wrong reason.
    """
    moved = tmp_path / "postcut.json"
    cut = json.loads((REPO_ROOT / "results" / "postcut_c3b.json").read_text(encoding="utf-8"))
    cut["producer"]["borrows"]["scripts/projection_5c2.py"] = "f" * 64
    moved.write_text(json.dumps(cut, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(writer, "POSTCUT", moved)

    with pytest.raises(SystemExit, match="was written by code that has changed since"):
        writer.check_the_inputs_have_not_moved(tmp_path / "nothing.json")


def test_a_sealed_registration_is_not_re_pinned_to_make_it_green(monkeypatch, tmp_path):
    """The strongest refusal in the file: an existing record whose inputs moved is not rewritten."""
    sealed = tmp_path / "prereg.json"
    sealed.write_text(
        json.dumps({"pinned_inputs": {"config/lexicon.yaml": "0" * 64}}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="is not re-pinned to make it green"):
        writer.check_the_inputs_have_not_moved(sealed)


# --- the sitting's fields, and what the run must persist ----------------------------------------


def test_the_registration_names_the_fields_the_3_18_6_sitting_needs():
    """ "The run persists evidence" is satisfied by a run that persists three fields. The table is
    named here field by field, from the one module that owns it."""
    consequence = RECORD["validate_consequence"]

    assert consequence["the_run_must_persist"]["every_row"] == list(evidence.REQUIRED)
    assert consequence["the_run_must_persist"]["by_kind"] == {
        kind: list(fields) for kind, fields in evidence.KIND_FIELDS.items()
    }
    assert consequence["kinds"] == ["comment", "leaflet_page", "position_row", "post_text"]
    assert "rendering" in consequence["the_run_must_persist"]["every_row"]
    assert "reply" in consequence["the_run_must_persist"]["every_row"]


def test_the_resume_discipline_names_the_watermark_and_the_fourth_kind():
    resume = RECORD["stop_rules"]["resume"]

    assert "watermark" in resume["rule"] and "post_text" in resume["rule"]
    assert "written LAST" in resume["rule"]


SEALING_COMMIT = "0e390ffceae5c14733c19afb4ab77d78dba98f4c"
"""The commit that landed `results/prereg_5c2_run.json` and the producer it names, together.

Written out in full and not as `0e390ff`. An abbreviation is valid until the day a seventh hex
digit collides with another object, and on that day this test errors for a reason nobody would
connect to a pre-registration. The short form is fine in the human-facing command below, which a
person runs once and reads the answer to.

`scripts/write_prereg_5c2.py` moved on 2026-08-14 — the write-path enumeration learned
`amendment-3.19`, so a future registration can be made over the grown law — and the record is NOT
re-pinned to follow it. That is the producer's own strongest refusal turned on itself. What keeps
`producer.sha256` a checkable claim instead of a dead literal is that the bytes are RECOVERABLE:

    git show 0e390ff:scripts/write_prereg_5c2.py

The record has never been rewritten and the producer had never been touched until today, so this is
the only commit either of them needs."""


def test_the_record_carries_no_clock_and_names_the_producer_that_wrote_it():
    """The producer moved under a sealed record, and the record is the one that stays put.

    Checked both ways, because either leg alone passes for the wrong reason: a live hash equal to
    the pin would mean the write-path enumeration never learned 3.19, and the recovered hash equal
    to the pin is what proves the record names the bytes that actually wrote it. The recovered file
    is read for the amendment's name too — a recovery that already carried it would mean this test
    is checking the wrong commit.

    `borrows` is still hashed LIVE: none of those five modules moved, and the day one of them does
    is the day this line has to be looked at rather than relaxed.
    """
    assert "generated_at" not in RECORD and "git" not in RECORD
    sealed = subprocess.run(
        ["git", "show", f"{SEALING_COMMIT}:scripts/write_prereg_5c2.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout
    live = hashlib.sha256(Path(writer.__file__).read_bytes()).hexdigest()

    assert RECORD["producer"]["sha256"] != live, "the producer never learned amendment-3.19"
    assert RECORD["producer"]["sha256"] == hashlib.sha256(sealed).hexdigest()
    assert b"amendment-3.19" not in sealed, "the recovered producer predates the amendment"
    assert "amendment-3.19" in Path(writer.__file__).read_text(encoding="utf-8")
    for path, digest in RECORD["producer"]["borrows"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == digest, path


def test_the_record_says_what_this_session_does_not_buy():
    """A registration that named only what it buys reads as authorising everything else."""
    scope = RECORD["not_in_scope"]

    assert "the price-pair leg" in scope and "0.4125" in scope["the price-pair leg"]
    assert "9 158" in scope["the 8 809 posts the cut removes"]
    assert 9158 - 349 == 8809
