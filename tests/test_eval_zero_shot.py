"""The runner's own bookkeeping: which rows were scored, and which were not.

`scripts/eval_zero_shot.py` runs as a script, so it is loaded here the way the
script loads itself. No network — every test drives it with a fake client, which
is also the only way to prove the failure counters are wired to something.
"""

import importlib.util
import json
from hashlib import sha256
from pathlib import Path

import pytest

from market_pulse import zero_shot

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "eval_zero_shot.py"
spec = importlib.util.spec_from_file_location("eval_zero_shot", SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

ROWS = [{"id": f"@ch:{i}", "text": f"row {i}"} for i in range(6)]


class ScriptedClient:
    """Replies in order; an ``ApiError`` entry stands for an endpoint that failed."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def __call__(self, task, text):
        self.seen.append(text)
        reply = self.replies[len(self.seen) - 1]
        if isinstance(reply, Exception):
            raise reply
        return {
            "content": reply,
            "finish_reason": "stop",
            "cost": 0.0,
            "usage": {},
            "generation_id": None,
        }


def test_classify_pairs_every_row_with_an_outcome():
    good = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'
    client = ScriptedClient([good] * 6)
    outcomes = runner.classify(client, "T1", ROWS, concurrency=1)
    assert [o["id"] for o in outcomes] == [row["id"] for row in ROWS]
    assert all("labels" in o for o in outcomes)


def test_classify_counts_parse_and_api_failures_apart():
    good = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'
    client = ScriptedClient(
        [good, "sorry, no", zero_shot.ApiError(503, "down"), good, '{"sentiment": "x"}', good]
    )
    outcomes = runner.classify(client, "T1", ROWS, concurrency=1)
    scored, labels, failures = runner.split(ROWS, outcomes)
    block = runner.failure_block("comments_test", outcomes, failures)

    assert block["rows"] == 6
    assert block["scored"] == 3 == len(scored) == len(labels)
    assert block["parse_failures"] == 2
    assert block["api_failures"] == 1
    assert block["failed_ids"] == ["@ch:1", "@ch:2", "@ch:4"]
    assert "no JSON object in reply" in block["reasons"]


def test_split_keeps_rows_and_labels_positionally_paired():
    good = '{"sentiment": "positive", "sarcasm": false, "intents": ["taste"]}'
    client = ScriptedClient(["bad", good, "bad", good, "bad", good])
    outcomes = runner.classify(client, "T1", ROWS, concurrency=1)
    scored, labels, _ = runner.split(ROWS, outcomes)
    assert [row["id"] for row in scored] == ["@ch:1", "@ch:3", "@ch:5"]
    assert all(label["sentiment"] == "positive" for label in labels)


def test_truncation_is_counted_separately_from_the_parse_failure_it_causes():
    class Truncating(ScriptedClient):
        def __call__(self, task, text):
            return {
                "content": '{"sentiment": "neu',
                "finish_reason": "length",
                "cost": 0.0,
                "usage": {},
                "generation_id": None,
            }

    outcomes = runner.classify(Truncating([]), "T1", ROWS, concurrency=1)
    block = runner.failure_block("comments_test", outcomes, runner.split(ROWS, outcomes)[2])
    assert block["parse_failures"] == 6
    assert block["truncated"] == 6, "max_tokens too small reads differently from a bad format"


def test_a_tripped_budget_stops_the_run_instead_of_failing_every_row():
    """The cap is not one more kind of failed row: a partial run must not be
    silently scored as if the model had refused those rows."""

    class Broke:
        def __call__(self, task, text):
            raise zero_shot.BudgetExceeded("cap tripped")

    with pytest.raises(zero_shot.BudgetExceeded):
        runner.classify(Broke(), "T1", ROWS, concurrency=1)


def test_scored_ids_hash_pins_the_paired_subset():
    """Phase 4 has to be able to reproduce the exact rows a gate was anchored on."""
    assert runner.scored_ids_sha256(ROWS[:3]) == runner.scored_ids_sha256(ROWS[:3])
    assert runner.scored_ids_sha256(ROWS[:3]) != runner.scored_ids_sha256(ROWS[:4])
    assert len(runner.scored_ids_sha256(ROWS)) == 64


def test_the_smoke_client_exercises_every_counter():
    """A smoke run that prints zeros in the failure table would be the bug."""
    rows = [{"id": str(i), "text": "x"} for i in range(10)]
    outcomes = runner.classify(runner.FakeClient(), "T1", rows, concurrency=1)
    block = runner.failure_block("smoke", outcomes, runner.split(rows, outcomes)[2])
    assert block["parse_failures"] > 0
    assert block["api_failures"] > 0
    assert block["scored"] > 0


def test_the_batch_slug_explains_itself_instead_of_burning_a_run():
    """OpenRouter serves :batch only through /api/beta/batches; every row would
    404. The guard fires before a single file is read, let alone a request sent."""
    with pytest.raises(SystemExit) as caught:
        runner.main(["--model", "anthropic/claude-haiku-4.5:batch", "--reference-only"])
    assert "anthropic/claude-haiku-4.5" in str(caught.value)
    assert "/api/beta/batches" in str(caught.value)


def test_every_pinned_row_is_fp8_or_an_explicitly_unpinnable_reference():
    """The pre-registered rule: one precision for all three candidates, never mixed."""
    candidates = {slug: row for slug, row in runner.ROWS.items() if not row.get("ref")}
    assert len(candidates) == 3
    assert {row["quantization"] for row in candidates.values()} == {"fp8"}
    references = {slug: row for slug, row in runner.ROWS.items() if row.get("ref")}
    assert all(row["quantization"] is None for row in references.values())
    assert all(slug.startswith("anthropic/") for slug in references)


# --- the per-row prediction dump (step 3c) -----------------------------------
#
# 3b stored a hash of the scored ids and called a paired re-score "reproducible
# from the file". It was not: a hash cannot re-score anything. These tests hold
# the fix in place.

SCORED_INPUTS = {
    "posts_test": (
        [{"id": "@ch:9", "text": "друга посилка"}, {"id": "@ch:2", "text": "перша посилка"}],
        [{"relevant": True, "post_type": "launch"}, {"relevant": False, "post_type": "promo"}],
    ),
    "comments_test": (
        [{"id": "@ch:5", "text": "смачно"}],
        [{"sentiment": "positive", "sarcasm": False, "intents": ["taste"]}],
    ),
}


def test_the_dump_is_sorted_so_its_hash_belongs_to_the_data_not_the_thread_pool(tmp_path):
    """Rows come back from four workers. A hash that depends on who finished
    first is not a hash of the run."""
    shuffled = {
        name: ([r for r in reversed(rows)], [x for x in reversed(labels)])
        for name, (rows, labels) in reversed(SCORED_INPUTS.items())
    }
    assert runner.prediction_lines(shuffled) == runner.prediction_lines(SCORED_INPUTS)
    a = runner.write_predictions(tmp_path / "a.jsonl", SCORED_INPUTS)
    b = runner.write_predictions(tmp_path / "b.jsonl", shuffled)
    assert a == b
    ordering = [
        (json.loads(x)["input"], json.loads(x)["id"])
        for x in runner.prediction_lines(SCORED_INPUTS)
    ]
    assert ordering == sorted(ordering)


def test_the_dump_carries_ids_and_predictions_only(tmp_path):
    """Ids and predicted labels. No gold label, no source text — a prediction
    dump must never become a second copy of a frozen file."""
    path = tmp_path / "d.jsonl"
    runner.write_predictions(path, SCORED_INPUTS)
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        assert set(json.loads(line)) == {"input", "id", "pred"}
    for row, _ in SCORED_INPUTS.values():
        for source in row:
            assert source["text"] not in text


def test_the_dump_rebuilds_the_scored_id_hash_the_record_already_carries(tmp_path):
    """The reconstruction whose absence caused the 3b correction: read the dump,
    recover the exact scored subset, and land on the same SHA256."""
    path = tmp_path / "d.jsonl"
    runner.write_predictions(path, SCORED_INPUTS)
    dumped = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        dumped.setdefault(entry["input"], []).append({"id": entry["id"]})
    for name, (rows, _) in SCORED_INPUTS.items():
        assert runner.scored_ids_sha256(dumped[name]) == runner.scored_ids_sha256(
            sorted(rows, key=lambda r: r["id"])
        )


def test_the_recorded_hash_is_the_hash_of_the_file_on_disk(tmp_path):
    path = tmp_path / "d.jsonl"
    digest = runner.write_predictions(path, SCORED_INPUTS)
    assert digest == sha256(path.read_bytes()).hexdigest()
    assert path.read_text(encoding="utf-8").endswith("\n")


def test_the_dump_path_is_one_file_per_run_and_survives_a_filesystem():
    a = runner.predictions_path("google/gemma-4-31b-it", "2026-07-31T18:04:05+00:00")
    b = runner.predictions_path("google/gemma-4-31b-it", "2026-08-01T06:00:00+00:00")
    assert a != b
    assert a.parent == runner.PREDICTIONS
    assert a.name == "google-gemma-4-31b-it--20260731T180405Z.jsonl"
    assert not {"/", ":"} & set(a.name)


def test_every_record_that_claims_a_dump_points_at_a_real_one():
    """A ratchet, empty until the first 3c-era run: the six 3b records carry no
    dumps and must not be backfilled, but any record that names one must not lie.
    See implementation-notes.md, "Correction (2026-07-31, team-lead review)"."""
    results = Path(__file__).resolve().parents[1] / "results" / "baselines.json"
    if not results.exists():
        pytest.skip("no results yet")
    for runs in json.loads(results.read_text(encoding="utf-8")).values():
        for record in runs:
            claimed = record["config"].get("predictions_path")
            if claimed is None:
                continue
            dump = results.parents[1] / claimed
            assert dump.exists(), f"{record['model']} names a dump that is not there: {claimed}"
            assert (
                sha256(dump.read_bytes()).hexdigest() == record["config"]["predictions_sha256"]
            ), f"{record['model']}: the dump on disk is not the one the record hashed"
