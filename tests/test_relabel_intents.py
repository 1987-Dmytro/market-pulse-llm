"""The re-labeller, judged on what it refuses.

Three refusals carry the whole design and each is tested with its negative control:
one column may move, no test row may be drawn, and nothing is spent before the
ledger says what the balance was. The fourth thing worth a test is arithmetic —
the drift split and the per-row cost that the projection multiplies.
"""

import json
import sys
from pathlib import Path

import pytest
from market_pulse import prompts, zero_shot

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import relabel_intents as relabel  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


def row(row_id="@c:1", intents=(), text="текст"):
    return {
        "id": row_id,
        "channel": "@c",
        "language": "ua",
        "text": text,
        "sentiment": "negative",
        "sarcasm": False,
        "intents": list(intents),
        "unclear": False,
        "annotator": "llm-precheck",
        "notes": "",
    }


def line_of(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def test_a_produced_row_moves_intents_and_nothing_else():
    source = row(intents=["price"])
    produced = relabel.relabelled(source, line_of(source), ["price", "service"])
    after = json.loads(produced)
    assert after["intents"] == ["price", "service"]
    assert {k: v for k, v in after.items() if k != "intents"} == {
        k: v for k, v in source.items() if k != "intents"
    }


def test_a_row_whose_source_line_says_something_else_stops_the_run():
    """The negative control: the check is against the source *bytes*, so a row
    edited anywhere else on its way in cannot pass."""
    source = row(intents=["price"])
    tampered = line_of({**source, "sarcasm": True})
    with pytest.raises(SystemExit, match="byte for byte"):
        relabel.relabelled(source, tampered, ["service"])


def test_the_draw_is_seeded_and_keeps_each_row_with_its_own_line():
    rows = [row(f"@c:{n}", intents=["price"] if n % 2 else []) for n in range(20)]
    lines = [line_of(r) for r in rows]
    drawn, drawn_lines = relabel.draw(rows, lines, 5, seed=42)
    again, _ = relabel.draw(rows, lines, 5, seed=42)
    assert [r["id"] for r in drawn] == [r["id"] for r in again]
    assert [json.loads(line)["id"] for line in drawn_lines] == [r["id"] for r in drawn]
    assert [r["id"] for r in relabel.draw(rows, lines, 5, seed=7)[0]] != [r["id"] for r in drawn]


def test_the_real_probe_sample_touches_no_test_row():
    assert relabel.main(["--source", "comments_train", "--limit", "50", "--dry-run"]) == 0


def test_a_source_holding_test_rows_is_refused(tmp_path, monkeypatch):
    test_rows = relabel.load(relabel.FROZEN / "comments_test.jsonl")[0][:3]
    planted = tmp_path / "planted.jsonl"
    planted.write_text("\n".join(line_of(r) for r in test_rows) + "\n", encoding="utf-8")
    monkeypatch.setitem(relabel.SOURCES, "comments_train", planted)
    with pytest.raises(SystemExit, match="forbids labelling a test row"):
        relabel.main(["--limit", "3", "--dry-run"])


def test_a_forbidden_file_that_cannot_be_read_stops_instead_of_shrinking(monkeypatch):
    """Without this the guard passes by having nothing to forbid."""
    monkeypatch.setattr(relabel, "NEVER", (*relabel.NEVER, relabel.FROZEN / "not_here.jsonl"))
    with pytest.raises(SystemExit, match="would let test rows through"):
        relabel.forbidden_ids()


def test_the_forbidden_set_is_every_frozen_test_row():
    banned = relabel.forbidden_ids()
    assert len(banned) == 400 + 108  # comments_test and the holdout, v2 and v3 sharing ids
    assert banned & {r["id"] for r in relabel.load(relabel.FROZEN / "comments_test.jsonl")[0]}


def test_drift_separates_the_taxonomy_from_the_disagreement():
    rows = [
        row("@c:1", []),  # [] -> service: the taxonomy, and only the taxonomy
        row("@c:2", ["price"]),  # price -> price+service: same
        row("@c:3", ["price"]),  # price -> quality: nothing in v2 explains this
        row("@c:4", ["taste"]),  # unchanged
    ]
    outcomes = [
        {"id": "@c:1", "intents": ["service"]},
        {"id": "@c:2", "intents": ["price", "service"]},
        {"id": "@c:3", "intents": ["quality"]},
        {"id": "@c:4", "intents": ["taste"]},
        {"id": "@c:5", "intents": None, "unusable": "parse: empty reply"},
    ]
    found = relabel.drift(rows, outcomes)
    assert (found["rows"], found["scored"], len(found["unusable"])) == (5, 4, 1)
    assert found["changed"] == 3 and found["service_rows"] == 2
    assert found["changed_without_service"] == 1, "gaining `service` is a move v2 explains"
    assert found["service_came_from"] == {"[]": 1, "price": 1}
    assert found["labels_added"] == {"service": 2, "quality": 1}
    assert found["labels_removed"] == {"price": 1}


def test_a_smoke_run_writes_the_record_the_gate_reads(tmp_path):
    record, rows_out = tmp_path / "probe.json", tmp_path / "rows.jsonl"
    assert (
        relabel.main(
            [
                "--smoke",
                "--limit",
                "20",
                "--record",
                str(record),
                "--rows-out",
                str(rows_out),
            ]
        )
        == 0
    )
    written = json.loads(record.read_text(encoding="utf-8"))["runs"][0]
    assert written["smoke"] is True and written["task"] == relabel.TASK
    assert written["prompt_sha256"][relabel.TASK] == prompts.prompt_sha256(relabel.TASK)
    assert written["drift"]["rows"] == 20
    # the unusable row is counted and is not among the rows that were produced
    produced = [line for line in rows_out.read_text(encoding="utf-8").splitlines() if line]
    assert len(produced) == written["drift"]["scored"] < 20
    assert written["cost"]["usd_per_row"] == pytest.approx(
        written["cost"]["usd"] / written["drift"]["scored"]
    )
    assert 0 < written["cost"]["usd"] <= relabel.CAP_USD


def test_nothing_is_requested_before_the_ledger_is_anchored(tmp_path, monkeypatch):
    """The ordering *is* the guard: a crash after the first request must not leave
    the next run counting from a balance that already includes this one."""
    ledger = tmp_path / "spend_45d.json"
    monkeypatch.setattr(relabel, "LEDGER", ledger)
    monkeypatch.setattr(relabel.evaluator, "api_key", lambda: "key")
    monkeypatch.setattr(relabel.evaluator, "verify_pin", lambda *a, **k: {"quantization": "fp8"})
    monkeypatch.setattr(zero_shot, "total_usage", lambda key, **k: 12.5)

    def refuse(*args, **kwargs):
        assert ledger.exists(), "a request left before the anchor was written"
        raise zero_shot.ApiError(500, "no requests in a test")

    monkeypatch.setattr(zero_shot, "post", refuse)
    # zero_shot's own backoff is tested in test_zero_shot.py; waiting it out here
    # would spend 90 seconds proving nothing about the ordering
    monkeypatch.setattr(zero_shot, "call_with_retry", lambda caller, **kwargs: caller())
    assert (
        relabel.main(
            [
                "--limit",
                "2",
                "--record",
                str(tmp_path / "probe.json"),
                "--rows-out",
                str(tmp_path / "rows.jsonl"),
            ]
        )
        == 0
    )
    anchored = json.loads(ledger.read_text(encoding="utf-8"))
    assert anchored["openrouter_total_usage_at_45d_start"] == 12.5
    assert anchored["cap_usd"] == relabel.CAP_USD
    assert anchored["runs"][0]["usd"] == 0.0  # every row failed, so nothing was charged


def test_the_budget_cap_stops_a_run_that_would_overspend():
    budget = zero_shot.Budget(relabel.CAP_USD, relabel.CAP_USD)
    ask = relabel.FakeAsker(budget)
    with pytest.raises(zero_shot.BudgetExceeded):
        for _ in range(30_000):  # $0.0001 a row: the cap is 20,000 rows away
            ask("текст")
