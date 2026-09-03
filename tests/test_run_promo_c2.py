"""The C2 backfill driver's $0 half — the registration, rung 0, and the served path on a stub."""

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import fetch_promo_media_c2 as fetch  # noqa: E402
import run_loop  # noqa: E402
import run_promo_c2 as driver  # noqa: E402

from market_pulse import loop  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402

CHANNEL = "@atb_aktsiyi"


def test_rung_0_prices_the_whole_step_and_the_dear_corner_decides():
    """Three corners in price order, the verdict is the dear one's, and the rung CAN refuse.

    The negative control matters more than the pass: a projection that could not go over the cap
    would be a rung that never fires ([[guard_selftest_negative_control]]).
    """
    verdict = driver.rung_0(3008, 405)
    cheap, priced, dear = (row["usd"] for row in verdict["table"])
    assert cheap < priced < dear
    assert verdict["fits"] == verdict["table"][-1]["fits"]
    assert verdict["realised_5c2"]["usd"] > dear, "the reading beside the table is the dearest"
    assert driver.rung_0(30, 0)["fits"]
    assert not driver.rung_0(30_000, 0)["fits"]


def test_the_step_cap_is_the_rulings_number():
    """The LAST cap the rulings file names — an older ruling's number must not keep this green."""
    ruling = (REPO_ROOT / "docs" / "reviews" / "2026-08-30-plan-promo-pulse-1.md").read_text(
        "utf-8"
    )
    caps = re.findall(rf"--step {driver.STEP} --step-cap (\d+\.\d+)", ruling)
    assert caps, "no ruling names the step cap"
    assert float(caps[-1]) == driver.STEP_CAP_USD


def test_the_order_is_ruling_02_09_cs_own_sequence_derived_from_the_files():
    """«АТБ → дешёвые → малые» — the derivation is checked against the team lead's printed list.

    The ruling names the head and the smoke-measured trio as handles and the tail as short names
    with their page counts, so both halves are grepped: a channel that drifts into the wrong band —
    or a fourteenth one appearing in the tail — fails here rather than in a paid run.
    """
    ruling = (REPO_ROOT / "docs" / "reviews" / "2026-08-30-plan-promo-pulse-1.md").read_text(
        "utf-8"
    )
    section = ruling.split("## Ruling 02.09 (c)")[-1].split("3. **Order")[1]
    head = re.findall(r"`(@\w+)`", section.split("→ every other channel")[0])
    tail = re.findall(r"(\w+) (\d+)", section.split("ascending by page count (")[1].split(")")[0])
    exact = {
        row["channel"]: row["pages_exact"] for row in driver.load(driver.PAGECOUNT)["channels"]
    }
    order = driver.stage_order()
    assert order[: len(head)] == head, "the leaflet carrier, then the smoke-measured channels"
    assert len(order) == len(head) + len(tail) == len(exact)
    for handle, (name, pages) in zip(order[len(head) :], tail):
        assert exact[handle] == int(pages), f"{handle} is not where the ruling's count puts it"
        assert name.lower() in handle.lower(), f"{handle} is not the ruling's {name}"


def test_a_channel_the_smoke_barely_touched_is_not_a_measured_channel():
    """The trio is derived by a THRESHOLD, and the threshold is what makes it three.

    `@marketopt_promo` and `@educationwithloven` are one smoke page each; one page is a row, not a
    rate, and the ruling puts marketopt in the tail by page count. The negative control is the
    point: a rule that admitted every channel the smoke touched would name five.
    """
    smoke = driver.smoke_rows_per_channel()
    assert smoke["@marketopt_promo"] < driver.MEASURED_MIN_ROWS <= smoke["@msuaaaa"]
    order = driver.stage_order()
    assert order.index("@marketopt_promo") > order.index("@msuaaaa")


def test_the_selection_hashes_do_not_depend_on_dict_order():
    a = {
        "@x": [
            {"channel": "@x", "msg_id": 2, "path": "p2"},
            {"channel": "@x", "msg_id": 1, "path": "p1"},
        ]
    }
    b = {"@y": [{"channel": "@y", "msg_id": 9, "path": "p9"}]}
    assert driver.pages_sha256(a | b) == driver.pages_sha256(b | a)
    assert driver.posts_sha256(a | b) == driver.posts_sha256(b | a)
    assert driver.pages_sha256(a) != driver.pages_sha256(b)


def test_albums_group_members_under_the_min_id_the_store_keyed_them_by():
    msg = lambda id_, group=None: SimpleNamespace(id=id_, grouped_id=group)  # noqa: E731
    grouped = fetch.albums([msg(12, "g"), msg(10, "g"), msg(11, "g"), msg(20), msg(30, "h")])
    assert set(grouped) == {10, 20, 30}
    assert [m.id for m in grouped[10]] == [10, 11, 12], "members sorted, the first is the key"
    assert [m.id for m in grouped[20]] == [20]


def test_a_download_killed_mid_write_is_not_a_page(tmp_path):
    whole, cut = tmp_path / "whole.jpg", tmp_path / "cut.jpg"
    whole.write_bytes(b"\xff\xd8 pixels \xff\xd9")
    cut.write_bytes(b"\xff\xd8 pixels")
    assert fetch.intact(whole)
    assert not fetch.intact(cut)
    assert not fetch.intact(tmp_path / "absent.jpg")


def test_the_driver_writes_to_the_derived_root_and_never_to_the_smoke_store():
    source = (REPO_ROOT / "scripts" / "run_promo_c2.py").read_text(encoding="utf-8")
    assert "SMOKE_DERIVED" not in source
    # Ruling 03.09 (b) fork 1: the driver WRITES to the live root and reads the sealed w1 root as
    # an archive, so the dedupe still sees what window 1 answered. Both names, both roles.
    assert "run_loop.LIVE_DERIVED_ROOT, archives=(run_loop.DERIVED_ROOT,)" in source


def test_a_moved_pinned_input_is_a_stop_and_not_a_re_derivation(tmp_path):
    (tmp_path / "pinned.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="moved"):
        driver.preflight({"pinned_inputs": {str(tmp_path / "pinned.json"): "0" * 64}})


# --- the served half, on a stub ------------------------------------------------------------------


class StubClient:
    """Serves the pin, answers every page with two positions and every post with `[]`."""

    endpoint_id = "stub-endpoint"

    def __init__(self, pin: dict) -> None:
        self.pin, self.worker, self.calls, self.rows = pin, 0.0, 0, 0
        self.tasks: list[str] = []

    def info(self) -> dict:
        self.calls += 1
        self.worker += 100.0
        return dict(self.pin)

    def positions(self, task: str, items: list) -> list[dict]:
        self.calls += 1
        self.tasks.append(task)
        self.rows += len(items)
        self.worker += 2.0 * len(items)
        content = run_loop.StubPageTransport.ANSWERS[1] if task == loop.PAGE_TASK else "[]"
        return [
            {
                "content": content,
                "finish_reason": "stop",
                "cost": 0.0,
                "usage": {},
                "generation_id": None,
            }
            for _ in items
        ]

    def timing(self) -> dict:
        return {
            "calls": self.calls,
            "rows": self.rows,
            "worker_seconds": self.worker,
            "wall_seconds": self.worker * 1.1,
            "queue_seconds": 0.0,
            "worker_ids": ["w"],
        }


class FakeStore:
    def rows(self, record_type: str, channel: str) -> list[dict]:
        assert record_type == "post" and channel == CHANNEL
        return [{"msg_id": 7, "text": "Молоко 1 л 45,90 грн"}, {"msg_id": 8, "text": "not pinned"}]


def stage(tmp_path, monkeypatch, page_ids):
    """The pages of one channel and one text post, every path the driver reads inside tmp_path."""
    media = tmp_path / "data" / "media"
    media.mkdir(parents=True)
    for msg_id in page_ids:
        (media / f"a_{msg_id}.jpg").write_bytes(b"\xff\xd8 not really a jpeg " + bytes([msg_id]))
    manifest = {
        "entries": {
            f"{CHANNEL}:{page_ids[0]}": {
                "channel": CHANNEL,
                "msg_id": page_ids[0],
                "images": [
                    {"msg_id": one, "file": f"data/media/a_{one}.jpg"} for one in page_ids
                ],
            }
        }
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "pagecount.json").write_text(
        json.dumps({"channels": [{"channel": CHANNEL, "pages_exact": len(page_ids)}]}),
        encoding="utf-8",
    )
    (tmp_path / "census.json").write_text(
        json.dumps({"channels": [{"channel": CHANNEL, "text_price_msg_ids": ["7"]}]}),
        encoding="utf-8",
    )
    pin = json.loads(driver.POSITIONS_PIN.read_text(encoding="utf-8"))["expected_worker"]
    client = StubClient(pin)
    monkeypatch.setattr(run_loop, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(loop, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(run_loop, "DERIVED_ROOT", tmp_path / "derived")
    monkeypatch.setattr(run_loop, "LIVE_DERIVED_ROOT", tmp_path / "derived_w2")
    monkeypatch.setattr(run_loop, "CURSOR", tmp_path / "cursor.json")
    monkeypatch.setattr(driver, "MANIFEST", tmp_path / "manifest.json")
    monkeypatch.setattr(driver, "PAGECOUNT", tmp_path / "pagecount.json")
    monkeypatch.setattr(driver, "CENSUS", tmp_path / "census.json")
    monkeypatch.setattr(driver, "PREREG", tmp_path / "prereg.json")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "record.json")
    monkeypatch.setattr(driver, "MEASUREMENTS", tmp_path / "measurements.jsonl")
    monkeypatch.setattr(driver, "live_store", lambda: FakeStore())
    monkeypatch.setattr(driver, "guard_says_go", lambda: (0, 0.0))
    monkeypatch.setattr(driver.fivec2, "client_for", lambda endpoint, key, dump=None: client)
    monkeypatch.setenv(driver.API_KEY_ENV, "stub")
    # DERIVED: every DERIVED root this module owns, checked to be under `tmp_path`, rather than the
    # two names above trusted to be all of them. `LIVE_DERIVED_ROOT` was added on 03.09 and this
    # fixture went on patching only its sibling, so the stub run appended 13 rows into the REAL
    # `data/derived_w2/` ([[a_probe_must_not_create_what_it_measures]]). A third derived root would
    # have done it again; now it stops the fixture instead. The RAW `STORE_ROOT` is deliberately
    # not in scope: `driver.live_store` is replaced by `FakeStore` above, so nothing reads it and
    # nothing has ever written it.
    stray = [
        name
        for name in dir(run_loop)
        if name.endswith("_ROOT")
        and "DERIVED" in name
        and isinstance(getattr(run_loop, name), Path)
        and not getattr(run_loop, name).is_relative_to(tmp_path)
    ]
    assert not stray, f"{stray} still point outside {tmp_path} — a stub run would write into them"
    return client


@pytest.fixture
def staged(tmp_path, monkeypatch):
    """Two pages and one text post."""
    return stage(tmp_path, monkeypatch, (101, 102))


@pytest.fixture
def staged_40(tmp_path, monkeypatch):
    """Forty pages: enough that a channel's REMAINDER can miss a room its first pack fits."""
    return stage(tmp_path, monkeypatch, tuple(range(101, 141)))


def test_the_registration_pins_the_worker_the_smoke_asserts_and_the_population(staged):
    record = driver.register()
    pinned = json.loads(driver.POSITIONS_PIN.read_text(encoding="utf-8"))["expected_worker"]
    assert record["expected_worker"] == pinned
    assert record["population"]["pages"]["by_channel"] == {CHANNEL: 2}
    assert record["population"]["posts"]["by_channel"] == {CHANNEL: 1}
    assert record["rung_0"]["fits"], "two pages fit any cap this step could have"


def test_rung_0_refuses_before_the_guard_or_a_client_exists(staged, monkeypatch):
    record = driver.register()
    record["rung_0"]["fits"] = False
    driver.PREREG.write_text(json.dumps(record), encoding="utf-8")

    def never():
        raise AssertionError("the guard was called after rung 0 said no")

    monkeypatch.setattr(driver, "guard_says_go", never)
    with pytest.raises(SystemExit, match="rung 0"):
        driver.main(["--run", "--endpoint", "e"])
    assert staged.calls == 0


def test_the_served_half_writes_the_rows_durably_and_a_second_run_re_asks_nothing(staged):
    """The write path, not only the compute: markers and positions land in the derived root,
    and a second `--run` finds nothing queued — the loop's own idempotence, through this driver."""
    driver.register()
    assert driver.main(["--run", "--endpoint", "e"]) == 0

    derived = RawStore(run_loop.LIVE_DERIVED_ROOT)
    assert derived.index(loop.PAGE_RECORD_TYPE, CHANNEL).ids == {101, 102}
    assert derived.index(loop.POST_RECORD_TYPE, CHANNEL).ids == {7}
    positions_file = derived.path(loop.POSITION_RECORD_TYPE, CHANNEL)
    assert len(positions_file.read_text(encoding="utf-8").splitlines()) == 4, "2 per page"
    record = json.loads(driver.RECORD.read_text(encoding="utf-8"))
    first = record["runs"][0]
    assert first["queued"] == {"pages": 2, "posts": 1}
    assert not first["go_no_go"]["refuse"]
    assert first["leaflet"][0]["channel"] == CHANNEL
    assert first["post_text"][0]["posts_read"] == 1
    assert "died" not in first
    rows_after_first = staged.rows

    assert driver.main(["--run", "--endpoint", "e"]) == 0
    record = json.loads(driver.RECORD.read_text(encoding="utf-8"))
    assert record["runs"][1]["queued"] == {"pages": 0, "posts": 0}
    assert staged.rows == rows_after_first, "nothing was sent the second time"
    assert len(positions_file.read_text(encoding="utf-8").splitlines()) == 4


def test_the_text_leg_is_stage_0_and_is_bought_before_any_page(staged, capsys):
    """Ruling 02.09 (b): the cheapest, surest, cross-chain data goes first under the cap gate —
    `--dry-run` says so, the record says so, and the stub saw the posts before the pages."""
    driver.register()
    assert driver.main(["--dry-run"]) == 0
    stages = [
        line for line in capsys.readouterr().out.splitlines() if line.strip().startswith("stage")
    ]
    assert "post_text" in stages[0] and CHANNEL in stages[1]

    assert driver.main(["--run", "--endpoint", "e"]) == 0
    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))["runs"][0]
    assert [stage["after"] for stage in run["stages"]] == ["post_text", CHANNEL]
    after_warmups = staged.tasks[2:]
    assert after_warmups[0] == loop.POST_TASK, "the first pass is the text leg"
    assert set(after_warmups[1:]) == {loop.PAGE_TASK}, "then the pages, nothing else"


def test_a_refusing_gate_makes_no_gold_call_and_still_writes_the_record(staged, monkeypatch):
    driver.register()
    record = json.loads(driver.PREREG.read_text(encoding="utf-8"))
    record["step"]["cap_usd"] = 0.0001  # the (10)(a) gate must refuse on any warm-up
    driver.PREREG.write_text(json.dumps(record), encoding="utf-8")

    assert driver.main(["--run", "--endpoint", "e"]) == 0
    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))["runs"][0]
    assert run["go_no_go"]["refuse"]
    assert "leaflet" not in run and "post_text" not in run
    assert run["unbought"] == {
        "pages": {CHANNEL: 2},
        "posts": {CHANNEL: 1},
        "pages_total": 2,
        "posts_total": 1,
    }, "a stop on ANY gate records what is left (ruling 02.09 (b) item 3)"
    assert staged.rows == 2, "the two warm-ups and nothing else"
    assert not (run_loop.DERIVED_ROOT / "leaflet_pages").exists()


def test_a_channel_that_fits_the_room_runs_whole_after_its_first_pack(staged, monkeypatch):
    """Ruling 02.09 (c) item 2, the direction that BUYS: the first pack measures the channel, the
    remainder is priced at that rate against the room, and it fits — so the channel runs whole and
    the measurement lands as one row per channel in the ledger.

    `pack_size` is pinned to one page so a two-page channel really has a first pack and a rest;
    with the transport's own size the whole channel is a single pack and neither half is exercised.
    """
    monkeypatch.setattr(driver.fivec2, "pack_size", lambda *args: 1)
    driver.register()
    assert driver.main(["--run", "--endpoint", "e"]) == 0

    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))["runs"][0]
    leg = run["leaflet"][0]
    assert leg["measured_n"] == 1 and leg["measured_seconds_per_page"] == 2.0, "the FIRST pack"
    assert leg["pages_bought"] == 2 and leg["pages_left"] == 0
    assert leg["remainder_pages"] == 1 and leg["remainder_bought"]
    assert leg["remainder_usd_at_its_rate"] < leg["room_usd_after_first_pack"]
    assert [pack["pack"] for pack in leg["packs"]] == [0, 1], "two jobs, one cut"
    assert run["unbought"]["pages_total"] == 0 and run["unbought"]["posts_total"] == 0

    rows = [
        json.loads(one)
        for one in driver.MEASUREMENTS.read_text(encoding="utf-8").splitlines()
        if one.strip()
    ]
    assert [(row["name"], row["value"], row["n"]) for row in rows] == [
        ("page_seconds_atb_aktsiyi", 2.0, 1)
    ]
    assert rows[0]["source"] == driver.rel(driver.RECORD) and rows[0]["max"] == rows[0]["value"]


def test_a_channel_whose_remainder_does_not_fit_the_room_is_skipped_whole(staged_40, monkeypatch):
    """The direction that costs money — ruling 02.09 (c) item 2(b), and item 1 beside it.

    The cap is computed from the stub's OWN clock (100 s of boot, 2 s a warm-up, 2 s a row) so it
    leaves room for about five more pages and not for the other thirty-nine: the first pack is
    bought and measured, the remainder is refused WHOLE, and the text leg — the cheapest, surest
    data — is bought anyway, which is the whole point of gating the legs apart.
    """
    monkeypatch.setattr(driver.fivec2, "pack_size", lambda *args: 1)
    driver.register()
    prereg = json.loads(driver.PREREG.read_text(encoding="utf-8"))
    rate = float(prereg["rung_0"]["rates"]["rate_usd_per_second"])
    drift = float(driver.load(driver.PREREG_5C2)["drift"]["factor"])
    billed = (100 + 2 + 2 + 2 + 2) * 1.1  # boot · two warm-ups · the text row · the first page
    prereg["step"]["cap_usd"] = round(
        billed * rate
        + driver.fivec2.worst_case_job_usd(rate, drift)
        + driver.skub.IDLE_TAIL_SECONDS * rate
        + 5 * 2.0 * rate,
        6,
    )
    driver.PREREG.write_text(json.dumps(prereg), encoding="utf-8")

    assert driver.main(["--run", "--endpoint", "e"]) == 0
    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))["runs"][0]
    assert not run["go_no_go"]["refuse"], "the text leg is never refused for the page rate"
    assert run["go_no_go"]["gold_calls"] == 1, "its own rows only — n_pages is 0 by the law"
    assert run["post_text"][0]["posts_read"] == 1

    leg = run["leaflet"][0]
    assert leg["pages_bought"] == 1 and leg["pages_left"] == 39
    assert leg["measured_seconds_per_page"] == 2.0 and leg["measured_n"] == 1
    assert not leg["remainder_bought"]
    assert leg["remainder_usd_at_its_rate"] > leg["room_usd_after_first_pack"] > 0
    assert run["unbought"]["pages"] == {CHANNEL: 39} and run["unbought"]["posts_total"] == 0
    assert any("pages left UNBOUGHT" in one for one in run["notes"])
    assert staged_40.rows == 4, "two warm-ups, one post, one page — and no thirty-ninth"


# --- the addendum (ruling 02.09 (d) item 1) -------------------------------------------------------


def test_the_addendum_adds_the_registry_pin_once_and_refuses_to_re_pin(tmp_path, monkeypatch):
    """Both directions on a sealed record's ONE growable field.

    The ruling lets the registration's own writer ADD the registry it was bought under and forbids
    re-pinning what is already there — so the branch that decides between those two is a provenance
    path, and a transcript demonstration is not a check that runs next week
    ([[a_self_pinning_producer_cannot_grow_a_parameter]]). The negative direction asserts the BYTES,
    not just the exception: a refusal that had already written half the record would pass an
    exception-only test.
    """
    prereg = tmp_path / "prereg.json"
    prereg.write_text(
        json.dumps({"pinned_inputs": {"results/x.json": "0" * 64}}, indent=2), encoding="utf-8"
    )
    registry = tmp_path / "registry.yaml"
    registry.write_text("watchlist: []\n", encoding="utf-8")
    monkeypatch.setattr(driver, "PREREG", prereg)
    monkeypatch.setattr(driver, "REGISTRY", registry)

    record = driver.register_addendum()
    key = driver.rel(registry)
    assert record["pinned_inputs"][key] == driver.sha256_of(registry)
    assert record["pinned_inputs"]["results/x.json"] == "0" * 64, "nothing already pinned moved"
    assert record["addendum"][0]["window_id"] == driver.WINDOW_ID
    assert record["addendum"][0]["dated"]

    sealed = prereg.read_bytes()
    with pytest.raises(SystemExit, match="an addendum adds, it never re-pins"):
        driver.register_addendum()
    assert prereg.read_bytes() == sealed, "a refusal writes nothing"
