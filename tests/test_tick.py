"""K10 — `make tick && make tick` writes zero new rows, counted per table, on a POPULATED store.

The check the phase spec asks for is worthless over an empty database: five of the six promo tables
are at zero in the repo today, and «zero new rows» over zero rows is a saturated proxy that cannot
discriminate ([[a_saturated_proxy_cannot_discriminate]]). So this module builds a store with rows in
ALL SIX — attribution, signal, evidence, digest, unsure, rollup — runs the tick twice over it, and
only then asserts the zeros. The negative control is the other half: a store that DID change must
write rows, or a tick that silently did nothing would pass every assertion here.
"""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import tick as tick_script  # noqa: E402

from market_pulse import aggregates  # noqa: E402

NOW = "2026-09-02T12:00:00+00:00"
CHANNEL = "@atb_market_official"
ROOT = 4342

SIGNAL_RECORD = {
    "channel": CHANNEL,
    "thread_root": ROOT,
    "extractor_version": "sha256:deadbeef",
    "kept": {
        "about": [
            {"msg_id": 101, "subject_type": "brand", "subject": "Рудь", "source": "explicit"},
            {"msg_id": 102, "subject_type": "chain", "subject": "АТБ", "source": "post_context"},
        ],
        "signal": [
            {
                "msg_id": 101,
                "type": "цена",
                "subject_type": "brand",
                "subject": "Рудь",
                "quote": "дорого стало",
            },
            {
                "msg_id": 102,
                "type": "похвала",
                "subject_type": "chain",
                "subject": "АТБ",
                "quote": "нарешті знижка",
            },
        ],
    },
    "unsure": [{"msg_id": 103, "candidates": ["цена", "жалоба"], "reason": "no subject in the row"}],
}


def store_with(tmp_path: Path, comments: list[dict]) -> Path:
    """A raw root holding one post and the comments handed in."""
    root = tmp_path / "raw_r2"
    (root / "posts").mkdir(parents=True)
    (root / "comments").mkdir(parents=True)
    (root / "posts" / "atb_market_official.jsonl").write_text(
        json.dumps(
            {
                "record_type": "post",
                "channel": CHANNEL,
                "msg_id": ROOT,
                "date": "2026-08-25T09:00:00+00:00",
                "text": "промо",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "comments" / "atb_market_official.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in comments), encoding="utf-8"
    )
    return root


def comment(msg_id: int, date: str) -> dict:
    return {
        "record_type": "comment",
        "channel": CHANNEL,
        "parent_msg_id": ROOT,
        "msg_id": msg_id,
        "date": date,
        "text": "…",
    }


def database(tmp_path: Path) -> Path:
    """A pulse.db with one window, one channel and two priced positions — so `rollup` is not empty
    either. Written with SQL rather than through `add_positions` on purpose: this module is about
    the tick, and a fixture that went through the producer would fail for the producer's reasons."""
    path = tmp_path / "pulse.db"
    conn = aggregates.connect(path)
    conn.execute(
        "INSERT INTO windows (window_id, anchor, days, since, until, bought, payable,"
        " text_less, leaflet_pages, post_texts, registry_channels)"
        " VALUES ('w1', '2026-08-31', 28, '2026-08-03', '2026-08-31', 2, 2, 0, 1, 0, 1)"
    )
    conn.execute(
        "INSERT INTO channels (window_id, channel, source_id, source_type, segment)"
        " VALUES ('w1', ?, 'atb', 'channel', 'retail')",
        (CHANNEL,),
    )
    for ordinal, (price, depth) in enumerate(((75.9, 0.5), (38.9, 0.32))):
        conn.execute(
            "INSERT INTO positions (window_id, row_id, channel, carrier, msg_id, ordinal, tier,"
            " price_promo, discount_pct_printed, depth, presence_brand, presence_line,"
            " presence_category, presence_size, presence_attribute, brand_raw, line, size_value,"
            " size_unit)"
            " VALUES ('w1', ?, ?, 'leaflet_page', ?, ?, 'position', ?, 50.0, ?, 1, 1, 0, 1, 0,"
            " 'Рудь', 'Чорниця', 500, 'г')",
            (f"{CHANNEL}:{ROOT}:{ordinal}", CHANNEL, ROOT, ordinal, price, depth),
        )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def world(tmp_path):
    """A store with rows waiting for all six tables: two ticks over it is the real K10."""
    signals = tmp_path / "signals"
    signals.mkdir()
    (signals / "thread.json").write_text(json.dumps(SIGNAL_RECORD), encoding="utf-8")
    comments = [comment(101, "2026-08-25T10:00:00+00:00"), comment(102, "2026-08-25T11:00:00+00:00")]
    return {
        "db": database(tmp_path),
        "store": store_with(tmp_path, comments),
        "signals": signals,
        "out": tmp_path / "promo_screen_data.json",
        "state": tmp_path / "promo_tick.json",
        "schedule": tmp_path / "schedule.json",
        # an EMPTY archive: the production default unions `data/raw/`, and a test that inherited it
        # would be measuring the repo's 2 006 real threads rather than its own fixture
        "archive": tmp_path / "empty_archive",
    }


def run(world, now: str = NOW, window: str | None = "w1") -> int:
    """`window=None` passes no `--window` at all — the only way to exercise the flag's DEFAULT."""
    return tick_script.main(
        [
            "--db", str(world["db"]),
            "--store", str(world["store"]),
            "--signals", str(world["signals"]),
            "--out", str(world["out"]),
            "--state", str(world["state"]),
            "--schedule", str(world["schedule"]),
            "--archive", str(world["archive"]),
            "--now", now,
        ]
        # named, not inherited: the fixture builds `w1` and the script's default is now the UNION
        # of every window ([[a_moved_constant_fails_green]]).
        + ([] if window is None else ["--window", window])
    )


def counts(world) -> dict:
    conn = sqlite3.connect(world["db"])
    try:
        return aggregates.promo_counts(conn)
    finally:
        conn.close()


def test_the_first_tick_fills_all_six_tables(world):
    """The population K10 is measured on. Asserted table by table so a zero cannot hide in a total."""
    assert run(world) == 0
    after = counts(world)
    assert after == {
        "attribution": 2,
        "signal": 2,
        "evidence": 2,
        "digest": 1,
        "unsure": 1,
        "rollup": 3,
    }
    for table in aggregates.PROMO_TABLES:
        assert after[table] > 0, f"{table} is empty — K10 over it would prove nothing"


def test_a_second_tick_on_an_unchanged_store_writes_zero_new_rows(world):
    """K10 itself, per table, plus the export's bytes: two ticks, one file, one sha."""
    run(world)
    before, first = counts(world), world["out"].read_bytes()
    run(world, now="2026-09-02T18:00:00+00:00")
    assert counts(world) == before
    assert world["out"].read_bytes() == first, "the export moved on an unchanged store"


def test_the_negative_control_a_changed_store_does_write_rows(world):
    """The half that makes the zeros mean something: a tick that wrote nothing whatever happened
    would pass the assertion above, and this is the test that would still fail."""
    run(world)
    before = counts(world)
    # a DIFFERENT thread means different comments: `attribution` and `unsure` are keyed on
    # (channel, msg_id, …) with no thread in the key (SP-5), so reusing 101/102 would correctly
    # collapse onto the rows already written and the control would be testing the key, not the tick
    record = {
        "channel": CHANNEL,
        "thread_root": 4343,
        "extractor_version": "sha256:deadbeef",
        "kept": {
            "about": [
                {"msg_id": 201, "subject_type": "brand", "subject": "Яготинське",
                 "source": "explicit"},
            ],
            "signal": [
                {"msg_id": 201, "type": "жалоба", "subject_type": "brand",
                 "subject": "Яготинське", "quote": "зникло з полиці"},
            ],
        },
        "unsure": [{"msg_id": 202, "candidates": ["спрос"], "reason": "no subject in the row"}],
    }
    (world["signals"] / "second.json").write_text(json.dumps(record), encoding="utf-8")
    run(world, now="2026-09-02T18:00:00+00:00")
    after = counts(world)
    assert after["signal"] > before["signal"] and after["attribution"] > before["attribution"]
    assert after["evidence"] > before["evidence"] and after["unsure"] > before["unsure"]


def test_a_late_comment_joins_through_the_digest_and_bumps_its_version(world):
    """Phase spec §2 S4: «late comments join via the thread digest (children ids), never by
    re-reading raw». The digest keeps its id, gains the child, and its version moves."""
    run(world)
    conn = sqlite3.connect(world["db"])
    conn.row_factory = sqlite3.Row
    first = dict(conn.execute("SELECT * FROM digest").fetchone())
    conn.close()
    assert json.loads(first["children_ids"]) == [101, 102]

    late = [
        comment(101, "2026-08-25T10:00:00+00:00"),
        comment(102, "2026-08-25T11:00:00+00:00"),
        comment(103, "2026-08-26T09:00:00+00:00"),
    ]
    store_with(world["store"].parent / "again", late)
    world["store"] = world["store"].parent / "again" / "raw_r2"
    run(world, now="2026-09-02T18:00:00+00:00")

    conn = sqlite3.connect(world["db"])
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute("SELECT * FROM digest")]
    conn.close()
    assert len(rows) == 1, "a late comment must not mint a second digest for the same thread"
    assert rows[0]["digest_id"] == first["digest_id"]
    assert rows[0]["version"] == first["version"] + 1
    assert json.loads(rows[0]["children_ids"]) == [101, 102, 103]
    assert rows[0]["covers_up_to_msg_id"] == 103


def test_a_cooled_thread_nobody_read_is_a_queue_entry_and_not_an_empty_digest(world, tmp_path):
    """«Read and said nothing» and «never read» are different states, so the second writes no row."""
    (world["signals"] / "thread.json").unlink()
    assert run(world) == 0
    assert counts(world)["digest"] == 0
    assert counts(world)["signal"] == 0


def test_the_schedule_is_read_and_reports_due_without_gating_the_tick(world, capsys):
    """The file is created with the phase spec's numbers, and it is a READING: a minimum interval
    that refused the second tick would make K10 pass over a run that never happened."""
    run(world)
    assert json.loads(world["schedule"].read_text())["min_interval_hours"] == 1
    assert json.loads(world["schedule"].read_text())["default_interval_hours"] == 6
    capsys.readouterr()
    run(world, now="2026-09-02T12:01:00+00:00")
    out = capsys.readouterr().out
    assert "not due" in out
    assert "wrote" in out, "the schedule reports; it does not gate"


def test_if_due_is_the_gate_for_a_scheduler_and_writes_nothing(world, capsys):
    run(world)
    stamp = world["out"].stat().st_mtime_ns
    tick_script.main(
        [
            "--db", str(world["db"]), "--store", str(world["store"]),
            "--signals", str(world["signals"]), "--out", str(world["out"]),
            "--state", str(world["state"]), "--schedule", str(world["schedule"]),
            "--archive", str(world["archive"]),
            "--now", "2026-09-02T12:01:00+00:00", "--if-due",
        ]
    )
    assert world["out"].stat().st_mtime_ns == stamp
    assert "nothing written" in capsys.readouterr().out


def test_the_cooled_queue_is_the_24_hour_rule_in_both_directions():
    """§5.10's threshold, and the clock is an argument so the answer does not depend on today."""
    from datetime import datetime

    rows = [comment(101, "2026-09-01T12:00:00+00:00")]
    just_cold = datetime.fromisoformat("2026-09-02T12:00:00+00:00")
    still_warm = datetime.fromisoformat("2026-09-02T11:59:00+00:00")
    assert len(tick_script.cooled_threads(rows, just_cold)) == 1
    assert tick_script.cooled_threads(rows, still_warm) == []


def test_a_window_the_table_lacks_refuses_and_the_union_is_the_default(world):
    """Ruling 10.09 (mm) 2(c), both ways on the id the store's `windows` table decides.

    The positive half is that `all` and a real id BOTH build a screen; the negative half is the
    defect this rung exists for. On 09.09 `--window all` matched no row of `windows`, the screen was
    written with `positions 1113 → 0`, and the exit code was zero — a checker whose failure is
    silence ([[a_checker_whose_failure_is_silence]]). So the refusal is asserted on the ARTEFACTS as
    well as the exception: both files and all six tables come back untouched, which is what
    «nothing written» has to mean when the guard sits in front of a writer
    ([[a_guard_that_runs_after_the_write]]).
    """
    assert run(world, window=None) == 0, "no --window at all: the DEFAULT is the union"
    union = json.loads(world["out"].read_text(encoding="utf-8"))
    assert union["window_id"] == aggregates.ALL_WINDOWS
    assert [row["id"] for row in union["windows"]] == ["w1"], "the export names what it unioned"
    assert run(world, window="w1") == 0
    one = json.loads(world["out"].read_text(encoding="utf-8"))
    assert one["window_id"] == "w1"
    assert one["screen"]["positions"] == union["screen"]["positions"], "one window IS the union here"

    kept, state, before = world["out"].read_bytes(), world["state"].read_bytes(), counts(world)
    with pytest.raises(SystemExit, match="the store's `windows` table carries"):
        run(world, window="w9")
    assert world["out"].read_bytes() == kept, "the refusal left the screen alone"
    assert world["state"].read_bytes() == state
    assert counts(world) == before, "the refusal wrote no row either"
