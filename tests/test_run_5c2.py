"""The paid session's driver — the selection it buys and the record its live seam builds.

The one test that matters here is the TWIN: the same recorded reply, through the stub the smokes
proved the record shape with and through the live transport this driver supplies, has to produce
byte-identical evidence rows. Anything the live path builds differently is a record no smoke ever
saw, and `docs/reports/5c2-prep-b.md` §4 is explicit that only the TRANSPORT may differ.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_5c2 as driver  # noqa: E402
import run_loop  # noqa: E402

from market_pulse import loop  # noqa: E402
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


def test_every_pinned_input_is_byte_identical_today():
    assert set(driver.preflight(PREREG).values()) == {"byte-identical"}


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
