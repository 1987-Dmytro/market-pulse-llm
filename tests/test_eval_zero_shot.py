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

from market_pulse import prompts, zero_shot

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

LOST = (Path(__file__).resolve().parents[1] / "results" / "predictions" / "LOST.md").read_text(
    encoding="utf-8"
)
"""The ledger of dumps a record names and the repo cannot back. Read as text so a path
listed anywhere in it counts — the file is a document a human reads, not a schema."""


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
                if not artifact.exists() and claimed in LOST:
                    # A dump that was written and then lost is a recorded fact, not a
                    # missing file: it is in results/predictions/LOST.md with its sha256
                    # and how it went, and the record is never edited to hide it.
                    continue
                assert artifact.exists(), (
                    f"{record['model']} names a {key} that is not there: {claimed}."
                    " If it was written and lost, say so in results/predictions/LOST.md."
                )
                assert sha256(artifact.read_bytes()).hexdigest() == config[f"{key[:-5]}_sha256"], (
                    f"{record['model']}: {claimed} on disk is not the file the record hashed"
                )


# --- the fine-tuned branch: an ablation arm's gate eval -----------------------
#
# Phase 4c scores each arm exactly once, so the parts that decide a number get a
# test that can fail rather than a careful reading.

FT_COMMENTS = [
    {
        "id": "c1",
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": False,
        "language": "ua",
    }
]
FT_POSTS = [{"id": "p1", "relevant": True, "post_type": "promo", "brands": [], "unclear": False}]
FT_HOLDOUT = [
    {"id": "h1", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
    {"id": "h2", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
    {"id": "h3", "sentiment": "positive", "sarcasm": True, "unclear": False, "language": "ru"},
]


def ft_inputs(holdout_labels):
    return {
        "comments_test": (FT_COMMENTS, [{"sentiment": "neutral", "sarcasm": False, "intents": []}]),
        "posts_test": (FT_POSTS, [{"relevant": True, "post_type": "promo", "brands": []}]),
        "sarcasm_holdout": (FT_HOLDOUT, holdout_labels),
    }


def test_a_slice_row_counts_as_fixed_only_when_both_labels_are_right():
    """Amendment 3.5 (3): FIXED means the row leaves the union of sentiment and
    sarcasm errors. Right on one label and wrong on the other is not fixed, and
    a fix-rate that scored the labels separately would report 2 of 3 here."""
    labels = [
        {"sentiment": "negative", "sarcasm": True, "intents": []},  # both right -> fixed
        {"sentiment": "negative", "sarcasm": False, "intents": []},  # sarcasm wrong
        {"sentiment": "neutral", "sarcasm": True, "intents": []},  # sentiment wrong
    ]
    gates, _, slice_ids = runner.build_gates(
        ft_inputs(labels), {}, {"ids": ["h1", "h2", "h3"], "anchor_overall": 0.8918}
    )
    g1b = next(entry for entry in gates if entry["gate"] == "G1b")
    assert g1b["fixed"] == 1
    assert g1b["n"]["slice"] == 3
    assert g1b["value"] == pytest.approx(1 / 3)
    assert slice_ids is None, "an arm scores the pre-registered slice; it never writes one"


def test_the_fine_tuned_record_carries_no_base_errs_under_a_name_that_says_base():
    """On a fine-tuned run those counts would be THIS model's errors. Same trap
    as the two G1d rows: a plausible number nothing downstream can question."""
    labels = [{"sentiment": "negative", "sarcasm": True, "intents": []}] * 3
    gates, diagnostics, _ = runner.build_gates(
        ft_inputs(labels), {}, {"ids": ["h1"], "anchor_overall": 0.8918}
    )
    g1b = next(entry for entry in gates if entry["gate"] == "G1b")
    assert not [key for key in diagnostics if key.startswith("base_errs")]
    assert not [key for key in g1b["n"] if key.startswith("base_errs")]


def test_the_guard_delta_is_this_runs_macro_f1_minus_the_anchors():
    """G1b is 'fixes >=60% WHILE overall macro-F1 degrades <=2 pp'. The guard
    travels with the fix-rate because it is half of the gate."""
    labels = [{"sentiment": "negative", "sarcasm": True, "intents": []}] * 3
    gates, _, _ = runner.build_gates(ft_inputs(labels), {}, {"ids": ["h1"], "anchor_overall": 0.80})
    g1a = next(entry for entry in gates if entry["gate"] == "G1a")
    guard = next(entry for entry in gates if entry["gate"] == "G1b")["guard"]
    assert guard["anchor"] == 0.80
    assert guard["value"] == g1a["values"]["overall"]
    assert guard["delta"] == pytest.approx(g1a["values"]["overall"] - 0.80)
    assert guard["max_drop"] == 0.02


def test_a_slice_row_this_run_did_not_score_stops_the_record():
    """An incomplete run must not read as a failed gate — the scorer raises and
    the caller has a checkpoint to resume from, which is the point of both."""
    labels = [{"sentiment": "negative", "sarcasm": True, "intents": []}] * 2
    inputs = ft_inputs(labels)
    inputs["sarcasm_holdout"] = (FT_HOLDOUT[:2], labels)  # h3 failed to parse
    with pytest.raises(SystemExit, match="were not scored by this run"):
        runner.build_gates(inputs, {}, {"ids": ["h1", "h3"], "anchor_overall": 0.89})


SMOKE_PROVENANCE = Path(__file__).resolve().parents[1] / "results" / "train" / "4b-smoke"


def arm_dir(tmp_path, **overrides):
    """A trainer output directory: the adapter beside the run's provenance."""
    provenance = json.loads((SMOKE_PROVENANCE / "provenance.json").read_text(encoding="utf-8"))
    provenance |= overrides
    (tmp_path / "adapter").mkdir(parents=True)
    (tmp_path / "adapter" / "adapter_config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "adapter" / "adapter_model.safetensors").write_bytes(b"not really weights")
    (tmp_path / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    return tmp_path / "adapter"


def test_the_arm_preflight_reads_the_anchor_the_slice_and_the_dataset(tmp_path):
    """Everything that decides the gate, before 62 GB of weights and an hour of
    A6000 time: the anchor row, its slice, and what this adapter was trained on."""
    gate_slice, training = runner.arm_preflight(arm_dir(tmp_path), "real-only")
    assert len(gate_slice["ids"]) == 44
    assert 0 < gate_slice["anchor_overall"] < 1
    assert training["train_sha256"] and training["adapter_sha256"]
    assert training["arm"] == "real-only"


def test_an_adapter_cannot_be_scored_under_the_other_arms_name(tmp_path):
    """The ablation is decided by comparing two columns; mislabelling one of them
    decides it by accident."""
    with pytest.raises(SystemExit, match="'real-only' arm, not 'with-synthetic'"):
        runner.arm_preflight(arm_dir(tmp_path), "with-synthetic")


def test_an_adapter_trained_on_moved_prompts_is_refused(tmp_path):
    """The prompt is part of the measurement (SPEC §7): an adapter trained on a
    different one is fine-tuned for a different task than the gate scores."""
    adapter = arm_dir(tmp_path, prompt_sha256={"T1": "0" * 64, "T2": "0" * 64})
    with pytest.raises(SystemExit, match="trained on different prompts"):
        runner.arm_preflight(adapter, "real-only")


def test_an_adapter_without_its_run_provenance_is_refused(tmp_path):
    adapter = arm_dir(tmp_path)
    (tmp_path / "provenance.json").unlink()
    with pytest.raises(SystemExit, match="provenance.json is missing"):
        runner.arm_preflight(adapter, "real-only")


def test_an_arm_eval_refuses_any_batch_size_but_one(tmp_path):
    """Greedy is not batch-invariant on this stack — measured, not assumed."""
    with pytest.raises(SystemExit, match="not batch-invariant"):
        runner.main(
            [
                *("--model", GEMMA, "--backend", "local", "--smoke"),
                *("--adapter", str(arm_dir(tmp_path)), "--arm", "real-only"),
                *("--batch-size", "8"),
            ]
        )


def test_an_adapter_and_its_arm_travel_together(tmp_path):
    with pytest.raises(SystemExit):
        runner.main(
            [*("--model", GEMMA, "--backend", "local", "--smoke"), "--adapter", str(tmp_path)]
        )


# --- the eval checkpoint: a crashed eval resumes, and never re-scores ----------

HEADER = {"model": GEMMA, "arm": "real-only", "batch_size": 1}


def test_the_checkpoint_starts_empty_and_holds_what_it_is_given(tmp_path):
    path = tmp_path / "eval.jsonl"
    assert runner.open_checkpoint(path, HEADER) == {}
    runner.append_checkpoint(path, "comments_test", {"id": "c1", "labels": {"sentiment": "ok"}})
    assert runner.open_checkpoint(path, HEADER) == {
        ("comments_test", "c1"): {"id": "c1", "labels": {"sentiment": "ok"}}
    }


def test_the_checkpoint_refuses_a_file_another_run_wrote(tmp_path):
    """Arm A's file left in place must not quietly donate 400 of arm B's rows."""
    path = tmp_path / "eval.jsonl"
    runner.open_checkpoint(path, HEADER)
    with pytest.raises(SystemExit, match="differs on"):
        runner.open_checkpoint(path, HEADER | {"arm": "with-synthetic"})


def test_a_resumed_eval_asks_the_model_only_for_the_rows_it_is_missing(tmp_path):
    """The crash protocol: resume on what is left, re-score nothing."""
    path = tmp_path / "eval.jsonl"
    good = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'
    first = BatchClient([good] * 6)
    runner.open_checkpoint(path, HEADER)
    runner.classify_local(
        first, "T1", ROWS[:2], 1, lambda scored: runner.append_checkpoint(path, "x", scored)
    )
    assert first.batches == [["row 0"], ["row 1"]]

    done = runner.open_checkpoint(path, HEADER)
    pending = [row for row in ROWS if row["id"] not in {rid for _, rid in done}]
    second = BatchClient([good] * 6)
    fresh = runner.classify_local(second, "T1", pending, 1)
    assert second.batches == [[row["text"]] for row in ROWS[2:]], "a resumed row was re-asked"
    assert len(done) + len(fresh) == len(ROWS)


# --- the record a fine-tuned arm writes about itself --------------------------


def boom(*args, **kwargs):
    raise AssertionError("write_slice was called")


def test_an_arm_never_rewrites_the_pre_registered_slice(monkeypatch, tmp_path):
    """The slice is the gate's denominator (amendment 3.5 (3)). An arm that
    replaced it with its own error set would move the gate without moving one
    number in this record."""
    monkeypatch.setattr(runner, "write_slice", boom)
    _, training = runner.arm_preflight(arm_dir(tmp_path), "real-only")
    config = runner.local_config({}, 1, {}, training, True, None, {})
    assert config["fine_tune"]["adapter_sha256"] == training["adapter_sha256"]
    assert config["g1b_slice_sha256"] == sha256(runner.G1B_SLICE.read_bytes()).hexdigest()


def test_the_same_call_without_an_adapter_does_write_one(monkeypatch):
    """The negative control: the refusal above is about the arm, not about a
    write_slice nothing calls any more."""
    monkeypatch.setattr(runner, "write_slice", boom)
    with pytest.raises(AssertionError, match="write_slice was called"):
        runner.local_config({}, 1, {}, None, True, {"union": []}, {"sarcasm_holdout": ([], [])})


def test_an_arms_record_does_not_claim_it_trained_on_nothing(monkeypatch, tmp_path):
    """`records.anchor` narrows on `train_sources` precisely because Phase 4's
    arms are also `backend: local`. A row that lied here would hand a model
    itself as its own baseline."""
    monkeypatch.setattr(runner, "write_slice", boom)
    _, training = runner.arm_preflight(arm_dir(tmp_path), "real-only")
    shared = {"train_sources": runner.records.ANCHOR_TRAIN_SOURCES}
    config = runner.local_config(shared, 1, {}, training, True, None, {})
    assert config["train_sources"] != runner.records.ANCHOR_TRAIN_SOURCES
    assert config["train_sources"]["comments_train.jsonl"] == 895
    assert runner.local_config(shared, 1, {}, None, False, None, {})["train_sources"] == {
        "zero-shot": "no training data"
    }


class AlwaysAnswers:
    """A client that answers every row, so the whole arm path can run on a Mac.

    `--smoke`'s own client fails one row in five on purpose, which is right for
    exercising the failure counters and wrong for exercising the gate: a slice
    row it dropped would stop the run before G1b was ever computed.
    """

    REPLIES = {
        "T1": '{"sentiment": "negative", "sarcasm": true, "intents": ["price"]}',
        "T2": '{"relevant": true, "post_type": "promo", "brands": [{"mention": "Rud"}]}',
    }

    def __init__(self):
        self.usage = __import__("collections").Counter()

    def __call__(self, task, text):
        return {
            "content": self.REPLIES[task],
            "finish_reason": "stop",
            "cost": 0.0,
            "usage": {},
            "generation_id": "stub",
        }

    def batch(self, task, texts):
        return [self(task, text) for text in texts]

    def eval(self):  # a stubbed model stands in for the PeftModel the arm loads
        return self


def test_an_arms_gate_eval_runs_end_to_end_over_the_real_frozen_rows(monkeypatch, tmp_path, capsys):
    """Driven through `main` with a stub client: the 758 frozen rows, the
    pre-registered 44-id slice, the fix-rate and the guard — everything the pod
    will do except the weights. An arm eval that only type-checks is an arm eval
    nothing has run, and this phase gets one attempt."""
    monkeypatch.setattr(runner, "FakeClient", AlwaysAnswers)
    assert (
        runner.main(
            [
                *("--model", GEMMA, "--backend", "local", "--smoke"),
                *("--adapter", str(arm_dir(tmp_path)), "--arm", "real-only"),
                *("--batch-size", "1"),
            ]
        )
        == 0
    )
    printed = capsys.readouterr().out
    assert "arm real-only · adapter sha256" in printed
    assert "G1b slice 44 ids, sha256 verified against the anchor" in printed
    assert "comments_test: scored 400/400" in printed
    assert "sarcasm_holdout: scored 108/108" in printed
    # The smoke prints the record's head, so the assertions are on the text: the
    # G1b entry is the second gate and lands well inside it.
    assert '"slice": 44' in printed and '"fixed":' in printed and '"delta":' in printed
    assert "base_errs" not in printed, "a fine-tuned run must not report base error sets"


def test_an_arm_writes_a_complete_record_without_a_gpu(monkeypatch, tmp_path, capsys):
    """The record-writing path, driven end to end with stubbed weights.

    `--smoke` returns before the record is built and `--probe` before it is
    written, so until this test nothing had ever run an arm's `--record-out`.
    Discovering a defect there costs a 3.4 h training run; discovering it here
    costs a second.
    """
    import sys
    import types

    monkeypatch.setitem(
        sys.modules,
        "peft",
        types.SimpleNamespace(PeftModel=types.SimpleNamespace(from_pretrained=lambda m, p: m)),
    )
    monkeypatch.setattr(runner.local_llm, "load", lambda *a, **k: (None, AlwaysAnswers()))
    monkeypatch.setattr(runner.local_llm, "environment", lambda *a, **k: {"gpu": "stub"})
    monkeypatch.setattr(runner, "LocalClient", None, raising=False)
    monkeypatch.setattr(runner.local_llm, "LocalClient", lambda tok, model: model)
    # inside the repo, because the record stores the dump path relative to it —
    # `.pytest_cache/` is gitignored, so nothing lands in the tree
    dumps = runner.REPO_ROOT / ".pytest_cache" / "predictions"
    monkeypatch.setattr(runner, "PREDICTIONS", dumps)
    monkeypatch.setattr(runner, "write_slice", boom)

    out = tmp_path / "record.json"
    assert (
        runner.main(
            [
                *("--model", GEMMA, "--backend", "local", "--batch-size", "1"),
                *("--adapter", str(arm_dir(tmp_path / "run", arm="with-synthetic"))),
                *("--arm", "with-synthetic"),
                *("--eval-checkpoint", str(tmp_path / "eval.jsonl")),
                *("--record-out", str(out)),
            ]
        )
        == 0
    )
    record = json.loads(out.read_text(encoding="utf-8"))
    config = record["config"]
    assert config["backend"] == "local"
    assert config["generation"]["batch_size"] == 1
    assert config["fine_tune"]["arm"] == "with-synthetic"
    assert config["train_sources"] != {"zero-shot": "no training data"}
    assert config["g1b_slice_sha256"] == sha256(runner.G1B_SLICE.read_bytes()).hexdigest()
    g1b = next(entry for entry in record["gates"] if entry["gate"] == "G1b")
    assert g1b["n"]["slice"] == 44 and g1b["guard"]["max_drop"] == 0.02
    # the dump the record names, and the checkpoint that would have resumed it
    dump = runner.REPO_ROOT / config["predictions_path"]
    assert sha256(dump.read_bytes()).hexdigest() == config["predictions_sha256"]
    assert len(dump.read_text(encoding="utf-8").splitlines()) == 758
    assert len((tmp_path / "eval.jsonl").read_text(encoding="utf-8").splitlines()) == 759
    dump.unlink()


# --- test set v4: which files, which rendering, which slice (4.5h2) -----------


def test_the_v2_resolution_is_the_phase_4_one_file_for_file():
    """Every Phase 4 record was measured on these three files through the frozen v1
    prompts. The default has to reproduce that exactly, not approximately."""
    assert runner.inputs_for("v2") == (
        ("comments_test", "T1", "comments_test.jsonl"),
        ("posts_test", "T2", "posts_test.jsonl"),
        ("sarcasm_holdout", "T1", "sarcasm_holdout.jsonl"),
    )


def test_the_v4_resolution_moves_the_files_and_the_comment_rendering_together():
    """Not two choices: a v4 file's gold carries six intents and the frozen T1 parser
    refuses the sixth, so scoring v4 through v1 prompts is not a thing that can happen."""
    assert runner.inputs_for("v4") == (
        ("comments_test", "T1v2_with_post", "comments_test_v4.jsonl"),
        ("posts_test", "T2", "posts_test_v4.jsonl"),
        ("sarcasm_holdout", "T1v2_with_post", "sarcasm_holdout_v4.jsonl"),
    )


def test_each_version_writes_its_own_g1b_slice():
    """The slice is the gate's denominator. One path for two versions would let a v4
    anchor overwrite the 44 pre-registered ids Phase 4's verdict was decided against."""
    assert runner.SLICE_OF["v2"] == runner.G1B_SLICE
    assert runner.SLICE_OF["v4"] != runner.SLICE_OF["v2"]
    assert runner.SLICE_OF["v4"].name == "g1b_slice_v4.json"


def test_post_context_is_one_entry_per_row_for_a_with_post_task_and_none_otherwise():
    rows = runner.load(runner.FROZEN / "sarcasm_holdout_v4.jsonl")
    assert runner.post_context("T2", rows) is None
    contexts = runner.post_context("T1v2_with_post", rows)
    assert len(contexts) == len(rows)
    assert set(contexts[0]) == {"parent", "caption", "caption_kind"}


def test_a_v4_run_on_the_remote_backend_is_refused():
    """The OpenRouter path sends one text per row with no parent post; a v4 row asked
    without it is a different instrument, and the record could not say so."""
    with pytest.raises(SystemExit, match="own-pod run"):
        runner.main(["--model", GEMMA, "--smoke", "--testset-version", "v4"])


def test_a_v4_smoke_scores_the_v4_files_through_the_with_post_rendering(capsys):
    assert (
        runner.main(["--model", GEMMA, "--backend", "local", "--smoke", "--testset-version", "v4"])
        == 0
    )
    out = capsys.readouterr().out
    assert "test set v4 · rendering {'T1': 'T1v2_with_post', 'T2': 'T2'}" in out
    assert "comments_test_v4.jsonl" in out and "400 parent posts" in out


def test_an_adapter_rendered_through_another_revision_is_refused(tmp_path):
    """The guard above it hashes the FROZEN v1 prompts, which stay frozen through a
    rendering change — it cannot see this one. An arm scored through a prompt it was not
    trained on measures the rendering, not the data."""
    adapter = arm_dir(tmp_path, prompt_revision_sha256=prompts.revision_sha256("v4"))
    with pytest.raises(SystemExit, match="renders .* and this eval renders"):
        runner.arm_preflight(adapter, "real-only")


def test_an_adapter_that_predates_the_field_is_read_as_v2(tmp_path):
    """4c's two arms carry no `prompt_revision_sha256`; they were rendered through the
    frozen prompts, which is what v2 means."""
    provenance = json.loads((SMOKE_PROVENANCE / "provenance.json").read_text(encoding="utf-8"))
    assert "prompt_revision_sha256" not in provenance
    _, training = runner.arm_preflight(arm_dir(tmp_path), "real-only")
    assert training["prompt_revision_sha256"] is None


def test_the_arm_name_is_checked_against_the_adapter_not_a_hardcoded_list(tmp_path):
    """`--arm` carried Phase 4's two names as argparse `choices` and refused 4.5h2's
    outright, after the arm had trained. The adapter's own provenance is the authority
    and it already refuses a mismatch — before the weights, which is what matters."""
    adapter = arm_dir(tmp_path, arm="without-plast")
    with pytest.raises(SystemExit, match="'without-plast' arm, not 'with-plast'"):
        runner.arm_preflight(adapter, "with-plast")


def test_the_preflight_reads_the_provenance_the_trainer_writes_today(tmp_path):
    """The fixture above is a Phase-4-era `provenance.json`, so it cannot see the schema
    move — and it did not: 4.5h2 renamed `synthetic_ids_added` and the preflight died on
    the pod after the arm had trained. This one builds the record from the live trainer."""
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import yaml

    import train_qlora

    config = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config" / "qlora.yaml").read_text(encoding="utf-8")
    )
    _, record = train_qlora.build(config, False)
    adapter = arm_dir(tmp_path, **record)
    _, training = runner.arm_preflight(adapter, "without-plast", "v4")
    assert training["added_ids"] == record["added_ids"]
    assert training["n_train"] == record["n_train"]
    assert training["prompt_revision_sha256"] == record["prompt_revision_sha256"]


# --- Phase 5b: the endpoint backend -----------------------------------------
#
# The third backend is a *client* swap and nothing else: the rendering, the parser and
# the record builder stay 4.5h2's. What is checked here is the argument surface that
# decides which half of the pre-registered pair a run is, and the one record shape that
# could quietly turn a merged fine-tune into a gate anchor.


def endpoint_args(*extra):
    return ["--model", GEMMA, "--backend", "endpoint", "--testset-version", "v4", *extra]


def refuses(capsys, argv, message):
    """argparse writes its refusal to stderr and exits 2 — a bare SystemExit would let a
    typo in the argv pass as the check this test claims to be."""
    with pytest.raises(SystemExit):
        runner.main(argv)
    captured = capsys.readouterr()
    assert message in captured.err + captured.out, captured.err + captured.out


def test_an_endpoint_run_needs_an_endpoint(capsys):
    refuses(
        capsys,
        endpoint_args("--serving-config", "A", "--batch-size", "1"),
        "--backend endpoint needs --endpoint-id",
    )


def test_an_endpoint_run_needs_to_name_its_half_of_the_pair(capsys):
    refuses(
        capsys,
        endpoint_args("--endpoint-id", "ep-1", "--batch-size", "1"),
        "an unnamed half is not a pair",
    )


def test_an_endpoint_id_without_the_backend_is_refused(capsys):
    refuses(
        capsys,
        ["--model", GEMMA, "--endpoint-id", "ep-1", "--smoke"],
        "--endpoint-id is a serving run",
    )


def test_the_pair_is_scored_at_batch_one():
    """Greedy is not batch-invariant on this stack, and SPEC amendment 3.11 (2) fixes 1."""
    with pytest.raises(SystemExit, match="scored at batch 1"):
        runner.main(endpoint_args("--endpoint-id", "ep-1", "--serving-config", "A"))


def test_config_a_is_the_unmerged_adapter_and_must_name_it(capsys):
    refuses(
        capsys,
        endpoint_args("--endpoint-id", "ep-1", "--serving-config", "A", "--batch-size", "1"),
        "--serving-config A is the unmerged adapter",
    )


def test_config_b_refuses_an_adapter_it_cannot_load(capsys, tmp_path):
    refuses(
        capsys,
        endpoint_args(
            "--endpoint-id",
            "ep-1",
            "--serving-config",
            "B",
            "--batch-size",
            "1",
            "--adapter",
            str(tmp_path),
            "--arm",
            "without-plast",
        ),
        "config B has no adapter to load",
    )


def test_config_b_must_carry_the_merged_artifacts_own_provenance(capsys):
    refuses(
        capsys,
        endpoint_args("--endpoint-id", "ep-1", "--serving-config", "B", "--batch-size", "1"),
        "the artifact must name itself",
    )


class TimedClient:
    def usage_dict(self):
        return {}

    def timing(self):
        return {"calls": 758, "worker_seconds": 2100.0}


def serving_args(config, **kwargs):
    defaults = {"endpoint_id": "ep-9", "serving_config": config, "endpoint_url": ""}
    return type("Args", (), defaults | kwargs)


MERGED = {
    "adapter_sha256": "b3ca6308",
    "merged_sha256": "9f9f9f",
    "adapter_path": "results/train/45h2-arm-a/adapter",
    "merge": "peft merge_and_unload on a bf16 CPU load",
    "tools": {"peft": "0.18.0"},
}


def test_a_merged_config_b_record_can_never_read_as_a_zero_shot_anchor():
    """`records.anchor` narrows on train_sources — a merged fine-tune filed as "no
    training data" would hand a model itself as its own baseline (records.py)."""
    from market_pulse import records

    base = {"train_sources": records.ANCHOR_TRAIN_SOURCES, "testset_version": "v4"}
    config = runner.serving_config(
        base, serving_args("B"), {"merge_state": "merged-requantized"}, MERGED, TimedClient()
    )
    assert config["train_sources"] != records.ANCHOR_TRAIN_SOURCES
    assert config["fine_tune"]["adapter_sha256"] == "b3ca6308"
    assert config["fine_tune"]["merged_sha256"] == "9f9f9f"
    assert config["backend"] == "endpoint"


def test_config_a_keeps_the_fine_tune_block_the_pod_run_built():
    base = {
        "train_sources": {"comments_train_tax2.jsonl": 895},
        "fine_tune": {"arm": "without-plast", "adapter_sha256": "b3ca6308"},
        "testset_version": "v4",
    }
    config = runner.serving_config(
        base, serving_args("A"), {"merge_state": "unmerged-adapter"}, None, TimedClient()
    )
    assert config["fine_tune"] == base["fine_tune"]
    assert config["train_sources"] == base["train_sources"]


def test_the_serving_block_carries_the_endpoint_the_worker_and_the_billed_seconds():
    config = runner.serving_config(
        {"train_sources": {}, "testset_version": "v4"},
        serving_args("A"),
        {"merge_state": "unmerged-adapter", "adapter_sha256": "b3ca6308", "runtime": {"gpu": "x"}},
        None,
        TimedClient(),
    )
    assert config["serving"]["endpoint_id"] == "ep-9"
    assert config["serving"]["config"] == "A"
    assert config["serving"]["timing"]["worker_seconds"] == 2100.0
    assert config["serving"]["spend_ledger"] == "results/spend_5b.json"
    # the worker's own account travels with the record, minus the runtime block that
    # `local_config` already stores under its own key
    assert "runtime" not in config["serving"]["worker"]
    assert config["serving"]["worker"]["adapter_sha256"] == "b3ca6308"
    assert config["serving"]["transport"] == "serverless-api"


def test_the_record_names_the_runtime_that_produced_it():
    """SPEC amendment 3.11 (1) moved production onto a pod; the number has to say so.

    Two runs of the same config on two runtimes are the one comparison this phase exists
    to make, and a record that leaves the runtime to be inferred from an endpoint id has
    lost the only field that distinguishes them.
    """
    base = {"train_sources": {}, "testset_version": "v4"}
    info = {"merge_state": "unmerged-adapter"}
    served = runner.serving_config(
        base, serving_args("A", endpoint_url="http://127.0.0.1:8000"), info, None, TimedClient()
    )
    assert served["serving"]["transport"] == "pod-loopback"
    assert served["serving"]["endpoint_url"] == "http://127.0.0.1:8000"
    assert "pod runtime" in served["determinism_note"]
    assert (
        "serverless"
        in runner.serving_config(base, serving_args("A"), info, None, TimedClient())[
            "determinism_note"
        ]
    )
