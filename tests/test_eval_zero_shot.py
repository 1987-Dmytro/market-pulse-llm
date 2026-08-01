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


# --- the local GPU backend (step 4a) -----------------------------------------
#
# The run that anchors G1d/G1e happens on a rented pod, so what can be tested
# here is everything except the weights: that the prompts are provably 3b's,
# that a failed generation is counted rather than guessed, and that the G1b
# slice leaves the run as an id list and not as a number in a report.

GEMMA = "google/gemma-4-31b-it"


class BatchClient:
    """Replies per batch; an entry that is an exception stands for one bad row."""

    def __init__(self, replies, explode=False):
        self.replies = list(replies)
        self.explode = explode
        self.batches = []

    def batch(self, task, texts):
        self.batches.append(list(texts))
        if self.explode:
            raise RuntimeError("CUDA kernel died")
        taken = [self.replies.pop(0) for _ in texts]
        return [
            item
            if isinstance(item, Exception)
            else {
                "content": item,
                "finish_reason": "stop",
                "cost": 0.0,
                "usage": {},
                "generation_id": None,
            }
            for item in taken
        ]


def test_the_prompt_check_reads_the_recorded_run_not_itself():
    """The assertion that would pass forever is `prompt_sha256 == prompt_sha256`.
    This one has to find the hash the OpenRouter run stored and match it."""
    stored = runner.recorded_prompt_sha256(GEMMA)
    assert stored, "the 3b gemma row is what the local run claims to be identical to"
    assert runner.assert_prompt_sha_matches_3b(GEMMA) == stored[0]


def test_a_prompt_that_moved_refuses_to_run(monkeypatch):
    """The negative control: without it, the check above proves nothing."""
    drifted = dict(runner.recorded_prompt_sha256(GEMMA)[0], T1="0" * 64)
    monkeypatch.setattr(runner, "recorded_prompt_sha256", lambda model: [drifted])
    with pytest.raises(SystemExit) as caught:
        runner.assert_prompt_sha_matches_3b(GEMMA)
    assert "T1" in str(caught.value)


def test_a_model_with_no_recorded_run_has_nothing_to_be_identical_to():
    with pytest.raises(SystemExit) as caught:
        runner.assert_prompt_sha_matches_3b("qwen/qwen3.5-9b-nonexistent")
    assert "prompt_sha256" in str(caught.value)


def test_batched_classification_keeps_every_row_in_its_own_place():
    good = '{"sentiment": "positive", "sarcasm": false, "intents": ["taste"]}'
    client = BatchClient([good] * 6)
    outcomes = runner.classify_local(client, "T1", ROWS, batch_size=4)
    assert [o["id"] for o in outcomes] == [row["id"] for row in ROWS]
    assert [len(b) for b in client.batches] == [4, 2]


def test_a_row_the_model_could_not_generate_is_counted_not_guessed():
    good = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'
    client = BatchClient([good, RuntimeError("no output"), good, "not json", good, good])
    outcomes = runner.classify_local(client, "T1", ROWS, batch_size=3)
    block = runner.failure_block("sarcasm_holdout", outcomes, runner.split(ROWS, outcomes)[2])
    assert block["generation_failures"] == 1
    assert block["parse_failures"] == 1
    assert block["api_failures"] == 0, "there is no API here — the bucket must stay empty"
    assert block["failed_ids"] == ["@ch:1", "@ch:3"]


def test_a_batch_that_dies_is_charged_to_its_own_rows():
    outcomes = runner.classify_local(BatchClient([], explode=True), "T1", ROWS, batch_size=6)
    block = runner.failure_block("comments_test", outcomes, runner.split(ROWS, outcomes)[2])
    assert block["generation_failures"] == 6
    assert block["scored"] == 0


def test_the_smoke_client_drives_the_batched_path_too():
    rows = [{"id": str(i), "text": "x"} for i in range(10)]
    outcomes = runner.classify_local(runner.FakeClient(), "T1", rows, batch_size=4)
    block = runner.failure_block("smoke", outcomes, runner.split(rows, outcomes)[2])
    assert block["generation_failures"] > 0
    assert block["parse_failures"] > 0
    assert block["scored"] > 0


def test_a_transient_batch_failure_costs_its_own_rows_and_no_others():
    """The OpenRouter client retries every row six times; without a per-row
    fallback here one transient would cost a whole batch. The 2% limit is two
    rows on the 108-row holdout, so a batch of eight would end the run."""

    class FlakyOnce(BatchClient):
        def __init__(self, replies):
            super().__init__(replies)
            self.failed = False

        def batch(self, task, texts):
            if len(texts) > 1 and not self.failed:
                self.failed = True
                raise RuntimeError("transient kernel hiccup")
            return super().batch(task, texts)

    good = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'
    outcomes = runner.classify_local(FlakyOnce([good] * 6), "T1", ROWS, batch_size=3)
    block = runner.failure_block("sarcasm_holdout", outcomes, runner.split(ROWS, outcomes)[2])
    assert block["scored"] == 6
    assert block["generation_failures"] == 0


def test_a_row_that_fails_alone_is_still_charged():
    """The retry must not swallow a genuine failure into a scored row."""

    class AlwaysDies(BatchClient):
        def batch(self, task, texts):
            raise RuntimeError("this row really is broken")

    outcomes = runner.classify_local(AlwaysDies([]), "T1", ROWS[:2], batch_size=2)
    block = runner.failure_block("comments_test", outcomes, runner.split(ROWS[:2], outcomes)[2])
    assert block["generation_failures"] == 2
    assert block["scored"] == 0


def test_an_out_of_memory_is_never_charged_to_a_row():
    """A batch size that does not fit is a fact about the machine. Turning it
    into 758 counted failures would bury the one line that says what happened."""

    class Oom(BatchClient):
        def batch(self, task, texts):
            raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")

    with pytest.raises(RuntimeError, match="out of memory"):
        runner.classify_local(Oom([]), "T1", ROWS, batch_size=6)


def test_the_local_smoke_run_scores_every_frozen_row_without_a_gpu():
    """Driven through `main`, not imported: a backend that only imports is a
    backend nothing has run."""
    assert runner.main(["--model", GEMMA, "--backend", "local", "--smoke"]) == 0


def test_a_local_probe_prints_the_labels_a_batch_check_has_to_compare(capsys):
    """The batch-invariance check diffs two probes. Aggregate counts are equal
    whenever both parse, so a probe that printed only counts could not fail —
    and this path used to crash outright on a null budget."""
    assert runner.main(["--model", GEMMA, "--backend", "local", "--smoke", "--probe", "2"]) == 0
    printed = capsys.readouterr().out
    assert '"pred"' in printed and '"id"' in printed


def test_the_reference_row_cannot_be_run_on_our_own_weights():
    with pytest.raises(SystemExit) as caught:
        runner.main(["--model", "anthropic/claude-haiku-4.5", "--backend", "local"])
    assert "reference row" in str(caught.value)


# --- the G1b slice ------------------------------------------------------------

HOLDOUT = [{"id": f"@ch:{i}"} for i in range(4)]
SLICE_IDS = {"sentiment": ["@ch:1"], "sarcasm": ["@ch:1", "@ch:3"], "union": ["@ch:1", "@ch:3"]}


def test_the_slice_is_an_id_list_and_its_hash_is_the_file_on_disk(tmp_path):
    """Counts chose a base model; a gate needs the rows. Phase 4's fix-rate is
    computed against exactly this list, so it has to be a file with a hash."""
    path = tmp_path / "g1b_slice.json"
    digest = runner.write_slice(path, HOLDOUT, SLICE_IDS)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["ids"] == ["@ch:1", "@ch:3"]
    assert payload["n"] == 2
    assert payload["n_holdout_scored"] == 4
    assert digest == sha256(path.read_bytes()).hexdigest()


def test_build_gates_reports_the_union_as_the_set_union_it_is():
    """The union is `len(sentiment | sarcasm)`, never the sum: the sentiment
    errors are largely a subset of the sarcasm ones."""
    holdout = [
        {"id": "a", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
        {"id": "b", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
    ]
    labels = [
        {"sentiment": "positive", "sarcasm": False, "intents": []},  # wrong on both
        {"sentiment": "negative", "sarcasm": False, "intents": []},  # wrong on sarcasm only
    ]
    comments = [
        {
            "id": "c",
            "sentiment": "neutral",
            "sarcasm": False,
            "intents": [],
            "unclear": False,
            "language": "ua",
        }
    ]
    posts = [
        {
            "id": "p",
            "relevant": True,
            "post_type": "promo",
            "brands": [],
            "unclear": False,
        }
    ]
    _, diagnostics, slice_ids = runner.build_gates(
        {
            "comments_test": (
                comments,
                [{"sentiment": "neutral", "sarcasm": False, "intents": []}],
            ),
            "posts_test": (posts, [{"relevant": True, "post_type": "promo", "brands": []}]),
            "sarcasm_holdout": (holdout, labels),
        },
        {},
    )
    assert slice_ids == {"sentiment": ["a"], "sarcasm": ["a", "b"], "union": ["a", "b"]}
    assert diagnostics["base_errs_union"] == 2


# --- transporting a record off the pod ----------------------------------------


def test_a_record_written_on_the_pod_appends_here(tmp_path, monkeypatch):
    """The pod's `results/baselines.json` is a throwaway checkout's file and must
    never travel over the project's append-only anchor. The record does."""
    monkeypatch.setattr(runner, "RESULTS", tmp_path / "baselines.json")
    record = {"model": GEMMA, "timestamp": "2026-08-01T12:00:00+00:00", "config": {}}
    incoming = tmp_path / "record.json"
    incoming.write_text(json.dumps(record), encoding="utf-8")

    assert runner.append_record_file(incoming) == 0
    history = json.loads((tmp_path / "baselines.json").read_text(encoding="utf-8"))
    assert history[GEMMA] == [record]

    with pytest.raises(SystemExit) as caught:
        runner.append_record_file(incoming)
    assert "already in" in str(caught.value)


def test_every_record_carries_what_show_results_prints():
    """`show_results.py` is the only sanctioned reader of the file, and it reads
    these by key. A record that lacks one makes the whole table unreadable."""
    results = Path(__file__).resolve().parents[1] / "results" / "baselines.json"
    for runs in json.loads(results.read_text(encoding="utf-8")).values():
        for record in runs:
            config = record["config"]
            assert {"seed", "heads", "train_sources"} <= set(config)
            assert {"T1", "T2"} <= set(config["heads"])


def test_every_record_that_claims_a_file_points_at_a_real_one():
    """A ratchet, empty until the first 3c-era run: the six 3b records carry no
    dumps and must not be backfilled, but any record that names one must not lie.
    See implementation-notes.md, "Correction (2026-07-31, team-lead review)".

    Every `*_path` with a matching `*_sha256` is checked, not just the dump —
    the G1b slice goes to a fixed filename that a later local run overwrites in
    place, and an overwrite has to fail loudly here rather than leave the record
    pointing at a file that is no longer the one it hashed."""
    results = Path(__file__).resolve().parents[1] / "results" / "baselines.json"
    if not results.exists():
        pytest.skip("no results yet")
    for runs in json.loads(results.read_text(encoding="utf-8")).values():
        for record in runs:
            config = record["config"]
            claims = [
                key for key in config if key.endswith("_path") and f"{key[:-5]}_sha256" in config
            ]
            for key in claims:
                claimed = config[key]
                artifact = results.parents[1] / claimed
                assert artifact.exists(), (
                    f"{record['model']} names a {key} that is not there: {claimed}"
                )
                assert sha256(artifact.read_bytes()).hexdigest() == config[f"{key[:-5]}_sha256"], (
                    f"{record['model']}: {claimed} on disk is not the file the record hashed"
                )
