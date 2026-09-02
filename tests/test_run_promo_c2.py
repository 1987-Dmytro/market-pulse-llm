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


def test_the_order_is_the_specs_list_then_the_rest_sorted():
    assert len(set(driver.ORDER)) == len(driver.ORDER)
    assert driver.ordered({"@kopiyochka1", "@kop1chat", "@atb_aktsiyi", "@zzz"}) == [
        "@atb_aktsiyi",
        "@kop1chat",
        "@kopiyochka1",
        "@zzz",
    ]


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
    assert "run_loop.DERIVED_ROOT" in source


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


@pytest.fixture
def staged(tmp_path, monkeypatch):
    """Two pages and one text post, every path the driver reads pointed into tmp_path."""
    media = tmp_path / "data" / "media"
    media.mkdir(parents=True)
    for msg_id in (101, 102):
        (media / f"a_{msg_id}.jpg").write_bytes(b"\xff\xd8 not really a jpeg " + bytes([msg_id]))
    manifest = {
        "entries": {
            f"{CHANNEL}:101": {
                "channel": CHANNEL,
                "msg_id": 101,
                "images": [
                    {"msg_id": one, "file": f"data/media/a_{one}.jpg"} for one in (101, 102)
                ],
            }
        }
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "pagecount.json").write_text(
        json.dumps({"channels": [{"channel": CHANNEL, "pages_exact": 2}]}), encoding="utf-8"
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
    monkeypatch.setattr(run_loop, "CURSOR", tmp_path / "cursor.json")
    monkeypatch.setattr(driver, "MANIFEST", tmp_path / "manifest.json")
    monkeypatch.setattr(driver, "PAGECOUNT", tmp_path / "pagecount.json")
    monkeypatch.setattr(driver, "CENSUS", tmp_path / "census.json")
    monkeypatch.setattr(driver, "PREREG", tmp_path / "prereg.json")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "record.json")
    monkeypatch.setattr(driver, "live_store", lambda: FakeStore())
    monkeypatch.setattr(driver, "guard_says_go", lambda: 0)
    monkeypatch.setattr(driver.fivec2, "client_for", lambda endpoint, key, dump=None: client)
    monkeypatch.setenv(driver.API_KEY_ENV, "stub")
    return client


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

    derived = RawStore(run_loop.DERIVED_ROOT)
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
