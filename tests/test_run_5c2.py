"""The paid session's driver — the selection it buys and the record its live seam builds.

The one test that matters here is the TWIN: the same recorded reply, through the stub the smokes
proved the record shape with and through the live transport this driver supplies, has to produce
byte-identical evidence rows. Anything the live path builds differently is a record no smoke ever
saw, and `docs/reports/5c2-prep-b.md` §4 is explicit that only the TRANSPORT may differ.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_5c2 as driver  # noqa: E402
import run_loop  # noqa: E402

from market_pulse import loop, serving  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402

from test_loop import ALIASES, CATEGORIES, jpeg  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_5c2_run.json").read_text(encoding="utf-8"))

PAGE_REPLY = {
    "content": '[{"brand": "Рудь", "category": "ice-cream", "size": "450 г",'
    ' "price_promo": "89,90 грн", "discount_pct_printed": "-31%"}]',
    "finish_reason": "stop",
    "cost": 0.0,
    "usage": {"prompt_tokens": 11, "completion_tokens": 22},
    "generation_id": None,
}


def a_page(tmp_path, msg_id=4340):
    return {
        "channel": "@atb_market_official",
        "msg_id": msg_id,
        "parent_msg_id": 4340,
        "path": str(jpeg(tmp_path / "media" / f"atb_{msg_id}.jpg", (7, 20, 30))),
    }


def run_page(page, send, root):
    return loop.page_pass(
        [page],
        send=send,
        derived=RawStore(root),
        state={},
        categories=CATEGORIES,
        aliases=ALIASES,
        model_revision=None,
        served_by="<test>",
    )


def rows_of(root):
    store = RawStore(root)
    return [
        store.rows(kind, "@atb_market_official")
        for kind in (loop.PAGE_RECORD_TYPE, loop.POSITION_RECORD_TYPE)
    ]


# --- the twin ------------------------------------------------------------------------------


def test_the_live_transport_builds_the_record_the_stub_builds(tmp_path):
    """One reply, two transports, one record. The seam is the only thing allowed to differ."""
    page = a_page(tmp_path)
    album = loop.render_page(loop.page_file(page))[2]

    live = driver.SliceTransport(driver.album_key)
    live.prime([driver.album_key(album)], [PAGE_REPLY])
    run_page(page, live, tmp_path / "live")

    run_page(page, lambda task, payload: PAGE_REPLY, tmp_path / "stub")

    assert rows_of(tmp_path / "live") == rows_of(tmp_path / "stub")
    assert live.calls == 1 and live.jobs == 1


def test_a_row_the_pack_never_bought_is_refused_rather_than_answered(tmp_path):
    """The failure a positional transport hides: one row's answer filed against another's record."""
    page = a_page(tmp_path)
    live = driver.SliceTransport(driver.album_key)
    live.prime([driver.album_key(["data:image/jpeg;base64,SOMETHINGELSE"])], [PAGE_REPLY])

    with pytest.raises(SystemExit, match="never bought"):
        run_page(page, live, tmp_path / "live")


def test_a_pack_whose_reply_count_is_wrong_is_refused(tmp_path):
    live = driver.SliceTransport(driver.text_key)
    with pytest.raises(SystemExit, match="mispaired"):
        live.prime(["a", "b"], [PAGE_REPLY])


def test_two_identical_payloads_get_one_reply_each(tmp_path):
    """A FIFO per key, not a single cached answer: two rows that render alike are still two rows."""
    live = driver.SliceTransport(driver.text_key)
    key = driver.text_key("k")
    live.prime([key, key], [PAGE_REPLY, {"content": "[]", "finish_reason": "stop"}])

    assert live("t", "k") == PAGE_REPLY
    assert live("t", "k")["content"] == "[]"
    with pytest.raises(SystemExit):
        live("t", "k")


# --- the money -----------------------------------------------------------------------------


def test_one_job_at_the_timeout_cannot_cross_the_registered_cap():
    """3.17 (10)(c), as the registration measured it: $0.2843 against $8.00."""
    rate = PREREG["rate"]["value"]
    drift = PREREG["drift"]["factor"]
    assert (
        driver.worst_case_job_usd(rate, drift)
        == (PREREG["stop_rules"]["per_job_ceiling"]["worst_case_job_usd_with_drift"])
    )


def test_the_cap_gate_refuses_the_job_it_cannot_absorb():
    rate, drift, cap = PREREG["rate"]["value"], PREREG["drift"]["factor"], 8.00
    room = (cap - 0.30) / rate  # a hair over one worst-case job left
    assert driver.cap_gate(billed=room, rate=rate, drift=drift, cap=cap) is None
    tight = (cap - 0.20) / rate  # less than one worst-case job left
    assert "execution timeout" in driver.cap_gate(billed=tight, rate=rate, drift=drift, cap=cap)


def test_a_pack_plans_for_less_than_the_execution_timeout():
    """A pack sized at the whole window ends TIMED_OUT, and that ends the RUN, not the job."""
    assert driver.pack_size(4.262, 4.262) * 4.262 <= driver.JOB_TIMEOUT_S
    assert driver.pack_size(10_000.0, 4.262) == 1


def test_a_fast_warm_up_cannot_inflate_a_pack_past_the_registered_marginal():
    """Dv180: one probe can be 3.64x off its population, in either direction.

    A warm-up ten times faster than the paid measurement must not buy a pack ten times bigger —
    a pack that overruns is not a slow job, it is the whole leg (3.17 (10)(c)) and its rows come
    back unbought. The slow warm-up direction still shrinks it, which is the asymmetry intended.
    """
    registered = 4.2794
    assert driver.pack_size(0.4, registered) == driver.pack_size(registered, registered)
    assert driver.pack_size(40.0, registered) < driver.pack_size(registered, registered)


def test_the_cap_is_priced_off_wall_clock_and_not_execution_time():
    """A worker with one slot bills between two sequential jobs; executionTime cannot see it."""

    class Clock:
        def timing(self):
            return {"worker_seconds": 100.0, "wall_seconds": 340.0}

    assert driver.billed_now(Clock()) == 340.0
    assert driver.billed_now(Clock()) > skub_billed(Clock())


def skub_billed(client):
    import positions_gm4_skub as skub

    return skub.billed_seconds(client)


# --- the selections ------------------------------------------------------------------------


def test_the_post_selection_is_the_d_cut_and_hashes_to_the_seal():
    selection = driver.post_selection(PREREG)

    assert sum(len(ids) for ids in selection.values()) == 44
    ids = [f"{handle}:{msg_id}" for handle, rows in selection.items() for msg_id in rows]
    assert len(set(ids)) == 44


def test_the_post_pin_is_the_newline_convention_and_the_comment_pin_is_not():
    """The census joins on a COMMA and the post cut on a NEWLINE; one shared helper picks one.

    Both directions are asserted: the newline hash reproduces the sealed post pin, and the same
    ids under the census's comma convention do NOT — which is the mistake this driver made once
    and the reason the two callers never share a separator.
    """
    cut = json.loads((REPO_ROOT / "results" / "postcut_c3b.json").read_text(encoding="utf-8"))
    ids = [row["id"] for row in cut["rows"]]
    import hashlib

    assert driver.newline_ids_sha256(ids) == PREREG["populations"]["post_text"]["selection_pin"]
    assert (
        hashlib.sha256(",".join(ids).encode()).hexdigest()
        != (PREREG["populations"]["post_text"]["selection_pin"])
    )


def test_the_leaflet_selection_is_the_pinned_manifests_pages():
    pages = driver.page_selection(PREREG)

    assert len(pages) == 159
    assert {page["channel"] for page in pages} == {"@atb_market_official"}
    assert len({page["parent_msg_id"] for page in pages}) == 19


def test_a_moved_pinned_input_is_a_stop_and_not_a_re_derivation():
    moved = json.loads(json.dumps(PREREG))
    moved["pinned_inputs"]["config/registry.yaml"] = "0" * 64

    with pytest.raises(SystemExit, match="have MOVED"):
        driver.preflight(moved)


def test_every_pinned_input_still_reads_as_the_seal_pinned_it():
    """Eight files hashed as they sit, and `docs/SPEC.md` through the strip the record names.

    The old assertion — every input "byte-identical" — was true until the law grew and had no way
    to stay true: amendment 3.19 landed 2026-08-14 over a run that was already complete and sealed,
    and clause (3) says out loud that nothing this run bought is re-scored under it. The label is
    asserted per input rather than as one set, because a stripped hash reported as "byte-identical"
    would be a false word in the run record and a set comparison cannot see which file it came from.
    """
    labels = driver.preflight(PREREG)

    assert labels["docs/SPEC.md"] == "derives through the 10-block keep"
    assert set(labels) == set(PREREG["pinned_inputs"]) and len(labels) == 9
    assert {path: label for path, label in labels.items() if label != "byte-identical"} == {
        "docs/SPEC.md": "derives through the 10-block keep"
    }


def test_a_spec_that_stopped_deriving_is_the_same_stop_as_a_moved_file():
    """The negative control for the branch above: the strip is not a way past the guard.

    Without this, `pinned_today` could return anything at all for `docs/SPEC.md` and the run would
    still start. Driven through the RECORD's pin rather than by editing the file, because the live
    SPEC is not a test's to write to.
    """
    moved = json.loads(json.dumps(PREREG))
    moved["pinned_inputs"]["docs/SPEC.md"] = "0" * 64

    with pytest.raises(SystemExit, match="have MOVED"):
        driver.preflight(moved)


# --- what a live pass must never do --------------------------------------------------------


def test_the_driver_writes_to_the_derived_root_and_never_to_the_smoke_store():
    """A live pass that read the smoke store would skip paid rows as already answered."""
    source = (REPO_ROOT / "scripts" / "run_5c2.py").read_text(encoding="utf-8")

    assert "SMOKE" not in source
    assert "run_loop.DERIVED_ROOT" in source


def test_the_comment_job_sends_the_row_text_and_not_the_rendering():
    """The worker renders with `prompts.build_messages`; a rendered prompt would be wrapped twice."""
    source = (REPO_ROOT / "scripts" / "run_5c2.py").read_text(encoding="utf-8")

    assert 'texts.append(row["text"])' in source
    assert "client.batch(loop.COMMENT_TASK, texts, context)" in source


def test_the_driver_registers_no_endpoint_of_its_own():
    """The endpoint arrives as an argument or an environment variable, never as a constant."""
    assert not hasattr(driver, "ENDPOINT")
    assert run_loop.ENDPOINT is None


def test_a_pack_never_exceeds_the_bodies_size_ceiling(monkeypatch):
    """RunPod refuses a `/run` body over 10 MiB with an HTTP 400, before any worker sees it.

    The clock is not the only ceiling a job has and it is not the one that bites first on the
    leaflet leg: a page travels as a base64 `data:` URL, and the first attempt of 5c2-run put 126
    of them in one pack and died on the body size with the boot already paid for (Dv309). The row
    count the marginal allows is the LOOSER bound here, so this asserts the tighter one holds.
    """
    big = "data:image/jpeg;base64," + "A" * 3_000_000
    monkeypatch.setattr(driver.loop, "render_page", lambda path: ([], "sha", [big]))
    monkeypatch.setattr(driver.loop, "page_file", lambda page: Path("/dev/null"))
    pages = [{"channel": "@c", "msg_id": n, "parent_msg_id": 1, "path": "x"} for n in range(9)]

    packs = driver.page_packs(pages, 126)

    budget = driver.MAX_PAYLOAD_MB * 1_000_000
    assert all(sum(len(item["album"][0]) for item in pack) <= budget for pack in packs)
    assert sum(len(pack) for pack in packs) == 9, "no page is dropped to make a pack fit"
    assert max(len(pack) for pack in packs) == 2, "3 MB pages, an 8 MB budget"


def test_the_count_bound_still_applies_inside_a_byte_pack(monkeypatch):
    """Both ceilings compose: whichever is tighter wins, per pack."""
    small = "data:image/jpeg;base64," + "A" * 1000
    monkeypatch.setattr(driver.loop, "render_page", lambda path: ([], "sha", [small]))
    monkeypatch.setattr(driver.loop, "page_file", lambda page: Path("/dev/null"))
    pages = [{"channel": "@c", "msg_id": n, "parent_msg_id": 1, "path": "x"} for n in range(10)]

    assert [len(pack) for pack in driver.page_packs(pages, 3)] == [3, 3, 3, 1]


def test_the_two_carriers_of_the_config_a_pin_agree():
    """Config A has no `expected_worker` block of its own — the expectation is ASSEMBLED.

    `results/serving_5b.json :: worker` is the house pin and `results/parity_srv2.json ::
    config.serving.worker` is the srv-2d session whose measured price the registration uses. Both
    describe the same configuration, so a disagreement means one of them is wrong and the driver
    must refuse rather than pick. Eleven fields today.
    """
    expected = driver.config_a_expected()

    assert expected["serving_config"] == "A"
    assert expected["merge_state"] == "unmerged-adapter"
    assert expected["max_new_tokens"] == 256
    assert not set(expected) & set(driver.SERVING_A_DROP), "provenance is not the measurement"
    assert len(expected) == 11


class RefusingEndpoint:
    """A client whose `info()` answers with ONE field wrong. Nothing past the handshake exists.

    Not a stub of the whole endpoint: everything after `assert_serving` is unreachable on this
    path by construction, and a fake that could answer a job would be able to hide a handshake
    that did not refuse.
    """

    def __init__(self, endpoint_id: str, observed: dict) -> None:
        self.endpoint_id = endpoint_id
        self.observed = observed
        self.calls = 0

    def info(self) -> dict:
        self.calls += 1
        return self.observed

    def timing(self) -> dict:
        return {"calls": self.calls, "rows": 0, "worker_seconds": 0.0, "wall_seconds": None}


def a_phase_ledger(tmp_path, *, last="2026-08-01T08:00:00+00:00") -> Path:
    """A phase-ledger FIXTURE. No test in this file reads or writes `results/spend_phase4.json`.

    That file is the money record of the whole phase, and a suite that appended to it on every run
    would be writing sessions that never happened into the ledger every later contract prices
    against. Every test that reaches `finalise` patches `driver.PHASE_LEDGER` at this path.
    """
    path = tmp_path / "spend_phase4.json"
    path.write_text(
        json.dumps(
            {
                "phase4_cap_usd": 33.0,
                "runpod_balance_at_phase4_start": 35.0,
                "anchored_at": "2026-08-01T08:34:09+00:00",
                "sessions": [{"at": last, "balance": 12.0, "spent_usd": 23.0, "note": "before"}],
            }
        ),
        encoding="utf-8",
    )
    return path


class Timing:
    """Everything `finalise` asks a client for, which is one method."""

    def timing(self) -> dict:
        return {"calls": 3, "rows": 0, "worker_seconds": 0.0, "wall_seconds": None}


def drive_finalise(tmp_path, monkeypatch, phase: Path) -> tuple[dict, list]:
    """`finalise` on the arm a COMPLETED leg takes, with every path pointed at `tmp_path`."""
    import positions_gm4_skub as skub

    step, record = tmp_path / "spend_5c2run.json", tmp_path / "run.json"
    monkeypatch.setattr(driver, "LEDGER", step)
    monkeypatch.setattr(driver, "PHASE_LEDGER", phase)
    monkeypatch.setattr(driver.guard, "balance", lambda: 9.0)
    ledger = {skub.anchor_key(driver.PHASE): 10.5, "cap_usd": 8.0, "runs": []}
    note: list[str] = []

    driver.finalise(argparse.Namespace(leg="comments", out=record), {}, note, Timing(), ledger)

    return json.loads(record.read_text(encoding="utf-8")), note


def test_finalise_witnesses_the_phase_ledger_from_the_runs_own_numbers(tmp_path, monkeypatch):
    """The team lead's ruling after 5c2-run, wired: no paid exit leaves the phase ledger silent.

    The property the permanent silence guard reads is that the phase entry and the step ledger's
    run carry the SAME balance READING — a re-read minutes later is a different number and the two
    records would stop matching. Both are asserted against each other rather than against literals.

    Delete the `witness_the_phase` call from `finalise` and this test fails on `len(sessions)`.
    """
    phase = a_phase_ledger(tmp_path)

    written, note = drive_finalise(tmp_path, monkeypatch, phase)

    sessions = json.loads(phase.read_text(encoding="utf-8"))["sessions"]
    run = json.loads((tmp_path / "spend_5c2run.json").read_text(encoding="utf-8"))["runs"][-1]
    assert len(sessions) == 2
    assert sessions[-1]["balance"] == run["balance"] == 9.0
    assert sessions[-1]["at"] == run["at"]
    assert sessions[-1]["spent_usd"] == 26.0, "35.00 anchor - 9.00, anchor-relative"
    assert sessions[-1]["remaining_usd"] == 7.0, "against the $33.00 cap in force"
    assert note == [f"the phase ledger was witnessed in {phase}"]
    assert written["notes"] == note


def test_a_witness_that_refuses_costs_the_run_record_nothing(tmp_path, monkeypatch):
    """The other direction: the witness refuses and the record is written anyway, saying so.

    `witness_phase_ledger` refuses on an entry that is not strictly after the last one — that
    refusal is what makes it idempotent, so it is a NORMAL outcome and not a crash. A driver that
    let it through would lose the run record to a bookkeeping stop.
    """
    phase = a_phase_ledger(tmp_path, last="2099-01-01T00:00:00+00:00")
    before = phase.read_bytes()

    written, note = drive_finalise(tmp_path, monkeypatch, phase)

    assert phase.read_bytes() == before, "a refused witness writes nothing"
    assert note[0].startswith("the phase ledger was NOT witnessed:")
    assert "not strictly after" in note[0]
    assert written["ledger"]["balance"] == 9.0 and written["timing"]["calls"] == 3


def test_a_refused_handshake_writes_the_ledger_row_and_the_record(monkeypatch, tmp_path):
    """What Dv307 says is open, MEASURED — the driver is driven into the refusal and the disk read.

    Dv307 recorded that `serving.assert_serving` raises `SystemExit` above `log_run`, so an endpoint
    serving the wrong configuration would bill its boot and append nothing to the ledger — and that
    it was NOT fixed mid-session. The crash fix of Dv309 (`79ae380`) then wrapped the whole of
    `run_the_legs` in `except BaseException` and called `finalise` from that arm. `SystemExit`
    derives from `BaseException`, so the refusal exit now lands in the same handler as a crash.

    A re-reading is not a measurement, so this drives `main()` into the refusal with a stubbed
    transport and reads what is on disk afterwards. Both directions: the handshake must still
    REFUSE (the guard is not being softened into a warning) and the two artifacts must exist.

    `driver.guard` and `positions_gm4_skub.guard` are the same module object, so patching
    `balance` once covers `main`'s anchor read and `spend_or_note`'s reconcile — no `runpodctl`
    call is made and the real `results/spend_5c2run.json` is never opened.
    """
    expected = driver.config_a_expected()
    ledger, record = tmp_path / "spend_5c2run.json", tmp_path / "run.json"
    phase = a_phase_ledger(tmp_path)
    client = RefusingEndpoint("e-fake", expected | {"merge_state": "merged-requantized"})
    monkeypatch.setattr(driver, "LEDGER", ledger)
    monkeypatch.setattr(driver, "PHASE_LEDGER", phase)
    monkeypatch.setattr(driver.guard, "balance", lambda: 9.0)
    monkeypatch.setattr(driver, "client_for", lambda endpoint, api_key, dump=None: client)
    monkeypatch.setenv(driver.API_KEY_ENV, "not-a-key")

    # the control: the worker's own answer, unaltered, passes the same guard — so what fires below
    # is the one changed field and not a refusal that refuses everything.
    assert serving.assert_serving(expected | {"gpu_name": "RTX 4090"}, expected)

    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        driver.main(["--leg", "comments", "--endpoint", "e-fake", "--out", str(record)])

    assert client.calls == 1, "the handshake is the only call the refusal path makes"
    runs = json.loads(ledger.read_text(encoding="utf-8"))["runs"]
    assert len(runs) == 1 and runs[0]["balance"] == 9.0
    assert runs[0]["note"].startswith("5c2-run comments — SystemExit:")
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["died"].startswith("SystemExit: the endpoint is not serving")
    # the second note is the witness, wired into `finalise` at the 5c2-close contract: a paid exit
    # that dies still lands in the phase ledger, from the row `log_run` has just appended.
    assert written["notes"] == [
        "the run ENDED on an exception: SystemExit",
        f"the phase ledger was witnessed in {phase}",
    ]
    assert json.loads(phase.read_text(encoding="utf-8"))["sessions"][-1]["balance"] == 9.0
    assert written["timing"]["calls"] == 1 and "go_no_go" not in written


def test_a_witness_failure_never_replaces_the_exception_that_killed_the_run(monkeypatch, tmp_path):
    """The hazard the wiring creates, planted: `finalise` runs inside `main`'s exception arm and
    the ORIGINAL exception is re-raised after it.

    A `SystemExit` escaping the witness would become the exception the caller sees, the re-raise
    would never happen, and a session killed by a wrong serving configuration would be reported as
    a bookkeeping failure. Here the phase ledger does not exist at all — the widest failure the
    witness can have — and the refusal the operator must see is still the handshake's.
    """
    expected = driver.config_a_expected()
    ledger, record = tmp_path / "spend_5c2run.json", tmp_path / "run.json"
    client = RefusingEndpoint("e-fake", expected | {"merge_state": "merged-requantized"})
    monkeypatch.setattr(driver, "LEDGER", ledger)
    monkeypatch.setattr(driver, "PHASE_LEDGER", tmp_path / "no-such-ledger.json")
    monkeypatch.setattr(driver.guard, "balance", lambda: 9.0)
    monkeypatch.setattr(driver, "client_for", lambda endpoint, api_key, dump=None: client)
    monkeypatch.setenv(driver.API_KEY_ENV, "not-a-key")

    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        driver.main(["--leg", "comments", "--endpoint", "e-fake", "--out", str(record)])

    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["died"].startswith("SystemExit: the endpoint is not serving")
    assert written["notes"][-1].startswith("the phase ledger was NOT witnessed:")
    assert not (tmp_path / "no-such-ledger.json").exists(), "a failed witness creates nothing"


def test_the_config_a_expectation_refuses_when_the_carriers_disagree(monkeypatch, tmp_path):
    house = json.loads((REPO_ROOT / "results" / "serving_5b.json").read_text(encoding="utf-8"))
    house["worker"]["max_new_tokens"] = 512
    forged = tmp_path / "serving_5b.json"
    forged.write_text(json.dumps(house), encoding="utf-8")
    monkeypatch.setattr(driver, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        driver, "PARITY_PIN", REPO_ROOT / "results" / "parity_srv2.json", raising=False
    )
    (tmp_path / "results").mkdir(exist_ok=True)
    (tmp_path / "results" / "serving_5b.json").write_text(json.dumps(house), encoding="utf-8")

    with pytest.raises(SystemExit, match="disagree"):
        driver.config_a_expected()
