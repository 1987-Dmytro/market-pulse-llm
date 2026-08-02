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
    assert (
        relabel.main(["--phase", "45d", "--source", "comments_train", "--limit", "50", "--dry-run"])
        == 0
    )


def test_a_source_holding_test_rows_is_refused(tmp_path, monkeypatch):
    test_rows = relabel.load(relabel.FROZEN / "comments_test.jsonl")[0][:3]
    planted = tmp_path / "planted.jsonl"
    planted.write_text("\n".join(line_of(r) for r in test_rows) + "\n", encoding="utf-8")
    monkeypatch.setitem(relabel.SOURCES, "comments_train", planted)
    with pytest.raises(SystemExit, match="a test row is never labelled here"):
        relabel.main(["--phase", "45e", "--limit", "3", "--dry-run"])


def test_skip_frozen_drops_those_rows_and_counts_them_instead_of_stopping(tmp_path, monkeypatch):
    """The full pass needs the holdout pool, 54 rows of which are the frozen holdout.

    Dropping them and refusing the run are the same promise — no test row is ever
    labelled — and the flag chooses which one. It cannot turn the guard off: the
    check after the draw runs either way, and the dropped rows are counted.
    """
    test_rows = relabel.load(relabel.FROZEN / "sarcasm_holdout.jsonl")[0][:2]
    mixed = tmp_path / "mixed.jsonl"
    keep = [row("@c:1", ["price"]), row("@c:2", [])]
    mixed.write_text(
        "\n".join(line_of(r) for r in [keep[0], *test_rows, keep[1]]) + "\n", encoding="utf-8"
    )
    monkeypatch.setitem(relabel.SOURCES, "comments_train", mixed)

    record, rows_out = tmp_path / "probe.json", tmp_path / "rows.jsonl"
    args = ["--phase", "45e", "--limit", "0", "--smoke", "--skip-frozen"]
    args += ["--record", str(record), "--rows-out", str(rows_out)]
    assert relabel.main(args) == 0
    written = json.loads(record.read_text(encoding="utf-8"))["runs"][0]
    counted = written["accounting"][relabel.rel(mixed)]
    assert counted["source_rows"] == 4 and counted["skipped_frozen"] == 2
    assert counted["labelled"] + counted["unusable"] == 2 and counted["full_pass"]
    assert {r["id"] for r in relabel.load(rows_out)[0]} == {"@c:1", "@c:2"}


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
        row("@c:5", ["price"]),  # the reply came back unreadable
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


def test_drift_splits_the_rows_a_gate_scores_from_the_rows_it_never_will():
    """Half a train sample is `unclear`; a prevalence over all of it answers a
    question about a file, not about what G1c is measured on."""
    rows = [
        {**row("@c:1", []), "unclear": False},
        {**row("@c:2", ["price"]), "unclear": False},
        {**row("@c:3", []), "unclear": True},
        {**row("@c:4", ["taste"]), "unclear": True},
    ]
    outcomes = [
        {"id": "@c:1", "intents": ["service"]},
        {"id": "@c:2", "intents": ["quality"]},
        {"id": "@c:3", "intents": ["service"]},
        {"id": "@c:4", "intents": ["taste"]},
    ]
    parts = relabel.drift(rows, outcomes)["by_unclear"]
    assert parts["scoreable"]["scored"] == 2 and parts["unclear"]["scored"] == 2
    assert parts["scoreable"]["service_prevalence"] == 0.5
    assert parts["scoreable"]["changed_without_service_rate"] == 0.5
    assert parts["unclear"]["changed_rate"] == 0.5
    assert "by_unclear" not in parts["scoreable"], "one level of splitting, not a recursion"


def test_the_churn_matrix_says_which_old_class_the_movement_came_out_of():
    """`labels_added` is a margin; the calibration is read against the transitions."""
    old_of = {"@c:1": {"price"}, "@c:2": {"availability"}, "@c:3": set(), "@c:4": {"taste"}}
    scored = [
        {"id": "@c:1", "intents": ["price", "service"]},
        {"id": "@c:2", "intents": ["service"]},
        {"id": "@c:3", "intents": ["service"]},
        {"id": "@c:4", "intents": ["taste"]},
    ]
    found = relabel.churn(old_of, scored)
    assert found["old_to_new"]["availability"]["service"] == 1
    assert found["old_to_new"]["availability"]["availability"] == 0, "it lost the label"
    assert found["old_to_new"]["price"] == {
        **dict.fromkeys(relabel.LABELS, 0),
        "price": 1,
        "service": 1,
    }
    assert found["margins"]["availability"] == {
        "before": 1,
        "after": 0,
        "kept": 0,
        "lost": 1,
        "gained": 0,
    }
    assert found["margins"]["service"]["gained"] == 3
    assert found["margins"]["[]"]["before"] == 1 and found["margins"]["[]"]["lost"] == 1


def test_a_full_pass_stages_a_copy_that_diffs_against_its_source_line_for_line(
    tmp_path, monkeypatch
):
    """The staged file is evidence only if it can be read beside its source.

    Same order, same count, same every column but one — which makes verifying the
    run a `diff` rather than a script nobody wrote."""
    source = tmp_path / "comments_train.jsonl"
    rows = [row(f"@c:{n}", ["price"] if n % 2 else [], text=f"розіграш {n}") for n in range(30)]
    source.write_text("\n".join(line_of(r) for r in rows) + "\n", encoding="utf-8")
    monkeypatch.setitem(relabel.SOURCES, "comments_train", source)

    out = tmp_path / "staged.jsonl"
    args = ["--phase", "45e", "--limit", "0", "--smoke", "--concurrency", "4"]
    assert relabel.main([*args, "--record", str(tmp_path / "r.json"), "--rows-out", str(out)]) == 0

    produced = relabel.load(out)[0]
    kept = [r for r in rows if r["id"] in {p["id"] for p in produced}]
    assert [p["id"] for p in produced] == [r["id"] for r in kept], "source order, not arrival order"
    for before, after in zip(kept, produced):
        assert {k: v for k, v in after.items() if k != "intents"} == {
            k: v for k, v in before.items() if k != "intents"
        }


def test_a_resume_re_checks_what_is_on_disk_and_asks_only_for_the_rest(tmp_path, monkeypatch):
    source = tmp_path / "comments_train.jsonl"
    rows = [row(f"@c:{n}", ["price"]) for n in range(6)]
    source.write_text("\n".join(line_of(r) for r in rows) + "\n", encoding="utf-8")
    monkeypatch.setitem(relabel.SOURCES, "comments_train", source)
    out = tmp_path / "staged.jsonl"
    # two rows survived a run that died; the third line is one somebody else wrote
    out.write_text(
        "\n".join(line_of({**r, "intents": ["service"]}) for r in rows[:2]) + "\n", encoding="utf-8"
    )

    args = ["--phase", "45e", "--limit", "0", "--smoke", "--resume", "--rows-out", str(out)]
    record = tmp_path / "r.json"
    assert relabel.main([*args, "--record", str(record)]) == 0
    written = json.loads(record.read_text(encoding="utf-8"))["runs"][0]
    assert written["cost"]["requests"] == 4, "the four rows that were missing, not all six"
    assert written["accounting"][relabel.rel(source)]["labelled"] == 6
    assert [r["id"] for r in relabel.load(out)[0]] == [r["id"] for r in rows]

    out.write_text(line_of(row("@elsewhere:1", ["service"])) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not in this source"):
        relabel.main([*args, "--record", str(record)])


def test_a_run_can_never_write_over_the_file_it_reads(tmp_path):
    with pytest.raises(SystemExit, match="read-only input"):
        relabel.main(
            [
                "--phase",
                "45e",
                "--smoke",
                "--limit",
                "0",
                "--rows-out",
                str(relabel.SOURCES["comments_train"]),
                "--record",
                str(tmp_path / "r.json"),
            ]
        )


def test_a_finished_run_is_re_derived_from_its_own_rows(tmp_path, monkeypatch):
    source = tmp_path / "source.jsonl"
    rows = [{**row("@c:1", []), "unclear": False}, {**row("@c:2", ["price"]), "unclear": True}]
    source.write_text("\n".join(line_of(r) for r in rows) + "\n", encoding="utf-8")
    produced = tmp_path / "produced.jsonl"
    produced.write_text(
        "\n".join(line_of({**r, "intents": ["service"]}) for r in rows) + "\n", encoding="utf-8"
    )
    monkeypatch.setitem(relabel.SOURCES, "comments_train", source)

    record = tmp_path / "probe.json"
    args = ["--phase", "45d", "--from-rows", str(produced), "--record", str(record)]
    assert relabel.main(args) == 0
    written = json.loads(record.read_text(encoding="utf-8"))["runs"][0]
    assert written["cost"]["requests"] == 0 and written["cost"]["usd"] == 0.0
    assert written["drift"]["service_rows"] == 2
    assert written["drift"]["by_unclear"]["scoreable"]["service_prevalence"] == 1.0
    assert written["per_file"][relabel.rel(produced)]["service_rows"] == 2

    stray = tmp_path / "stray.jsonl"
    stray.write_text(line_of(row("@c:9", ["service"])) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="came from elsewhere"):
        relabel.main(["--phase", "45d", "--from-rows", str(stray), "--record", str(record)])

    tampered = tmp_path / "tampered.jsonl"
    tampered.write_text(
        line_of({**rows[0], "intents": ["service"], "sentiment": "positive"}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="more than `intents`"):
        relabel.main(["--phase", "45d", "--from-rows", str(tampered), "--record", str(record)])

    backwards = tmp_path / "backwards.jsonl"
    backwards.write_text(
        "\n".join(line_of({**r, "intents": ["service"]}) for r in reversed(rows)) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="not in its source's order"):
        relabel.main(["--phase", "45d", "--from-rows", str(backwards), "--record", str(record)])


def test_a_smoke_run_writes_the_record_the_gate_reads(tmp_path):
    record, rows_out = tmp_path / "probe.json", tmp_path / "rows.jsonl"
    assert (
        relabel.main(
            [
                "--phase",
                "45d",
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
    assert 0 < written["cost"]["usd"] <= relabel.PHASES["45d"]["cap_usd"]
    counted = written["accounting"]["data/frozen/comments_train.jsonl"]
    assert counted["labelled"] + counted["unusable"] == counted["drawn"] == 20
    assert counted["full_pass"] is False


def test_nothing_is_requested_before_the_ledger_is_anchored(tmp_path, monkeypatch):
    """The ordering *is* the guard: a crash after the first request must not leave
    the next run counting from a balance that already includes this one."""
    ledger = tmp_path / "spend_45d.json"
    monkeypatch.setitem(relabel.PHASES["45d"], "ledger", ledger)
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
                "--phase",
                "45d",
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
    assert anchored["cap_usd"] == relabel.PHASES["45d"]["cap_usd"]
    assert anchored["runs"][0]["usd"] == 0.0  # every row failed, so nothing was charged


def test_a_phase_cannot_spend_against_another_phases_anchor(tmp_path):
    """Two phases, two caps, two balances — and one ledger that says which it is."""
    ledger = tmp_path / "spend_45e.json"
    fresh = relabel.read_ledger(ledger, "45e", 1.50, 9.0)
    assert fresh["openrouter_total_usage_at_45e_start"] == 9.0 and fresh["cap_usd"] == 1.50
    relabel.write_json(ledger, fresh)
    assert (
        relabel.read_ledger(ledger, "45e", 1.50, 99.0)["openrouter_total_usage_at_45e_start"] == 9.0
    )
    with pytest.raises(SystemExit, match="another phase's anchor"):
        relabel.read_ledger(ledger, "45d", 2.00, 9.0)


def test_the_budget_cap_stops_a_run_that_would_overspend():
    cap = relabel.PHASES["45e"]["cap_usd"]
    budget = zero_shot.Budget(cap, cap)
    ask = relabel.FakeAsker(budget)
    with pytest.raises(zero_shot.BudgetExceeded):
        for _ in range(30_000):  # $0.0001 a row: the cap is 15,000 rows away
            ask("текст")
