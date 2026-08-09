"""`scripts/caption_gm4_5c1.py`: the GM4 caption driver, everything it refuses for free.

No network, no spend, no picture larger than a fixture. What it pins is the half of vis-b that
is expensive to discover on a billed endpoint: there is no default endpoint id, a paid artifact
is never overwritten, a post never travels without its album, and a slice stays under RunPod's
documented 10 MB `/run` ceiling — the pictures ride inside the job because `data/annotation/**`
is gitignored and cannot reach the worker on the network volume.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import parents, prompts, serving  # noqa: E402

RUNBOOK = (REPO_ROOT / "scripts" / "runbook_vis_b.md").read_text(encoding="utf-8")


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


driver = _script("caption_gm4_5c1")
pattern = _script("caption_posts")
handler = _script("serve_handler")


def test_what_the_driver_demands_of_the_worker_is_what_the_worker_answers():
    """The driver's expectation and the worker's `describe` are two files; `assert_serving`
    compares them, and this is the only place they can be checked against each other for free."""
    info = handler.describe(
        handler.settings({"SERVING_CONFIG": "CAPTION", "MODEL_REVISION": "842da379"}), {}, None, {}
    )
    assert serving.assert_serving(info, driver.expected_worker()) is info


def runbook_env() -> dict:
    """The `--env '{...}'` block of the runbook's `template create`, as the code will see it.

    Parsed rather than retyped: the point is that the document and the worker cannot drift, and
    a copy of the JSON in this file would drift with neither of them (the srv-2a pattern)."""
    match = re.search(r"--env '(\{.*?\})'", RUNBOOK, re.DOTALL)
    assert match, "the runbook no longer prints a template --env block"
    return json.loads(match.group(1))


def test_the_runbooks_template_env_is_exactly_what_the_caption_worker_reads():
    env = runbook_env()
    assert set(env) == {"SERVING_CONFIG", "BASE_WEIGHTS", "MODEL_REVISION"}
    assert not set(env) & set(handler.ADAPTER_ENV), "an adapter variable would refuse at boot"
    config = handler.settings(env)
    assert config["serving_config"] == serving.CAPTION_CONFIG
    assert config["adapter_dir"] is None
    parity = json.loads((REPO_ROOT / "results" / "parity_5b_a.json").read_text(encoding="utf-8"))
    assert config["revision"] == parity["config"]["runtime"]["model_revision"]


def test_the_runbook_quotes_the_prompt_sha_the_code_renders():
    """§A.4 and §B print it as the handshake's fourth field. A runbook naming another sha would
    send an operator looking for a staging fault that is not there."""
    assert prompts.prompt_sha256(prompts.CAPTION_TASK_GM4)[:12] in RUNBOOK


def test_the_runbook_does_not_reuse_the_pod_cost_anchor():
    """`smoke_5b.py --record` defaults to results/serving_5b.json, the block every serverless
    comparison is measured against. Every smoke line here names its own path."""
    for line in RUNBOOK.splitlines():
        if "--record" in line:
            assert "serving_5b.json" not in line


def test_the_driver_has_no_default_endpoint_id(monkeypatch, tmp_path):
    monkeypatch.delenv(driver.ENDPOINT_ENV, raising=False)
    with pytest.raises(SystemExit, match="no endpoint id"):
        driver.main(
            [
                "--scope",
                "probe",
                "--out",
                str(tmp_path / "o.jsonl"),
                "--record",
                str(tmp_path / "r.json"),
            ]
        )


def test_the_driver_refuses_to_overwrite_what_a_paid_run_bought(tmp_path):
    out, record = tmp_path / "o.jsonl", tmp_path / "r.json"
    out.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="already exists"):
        driver.main(["--scope", "probe", "--out", str(out), "--record", str(record)])


def test_the_driver_writes_its_source_and_its_slices(tmp_path):
    """`--smoke` stops before the record is written on some scripts; here it is driven to the
    file, and what the file says is what the test reads."""
    out, record = tmp_path / "o.jsonl", tmp_path / "r.json"
    assert driver.main(
        ["--scope", "probe", "--out", str(out), "--record", str(record)],
        client=driver.FakeEndpoint(),
    ) in (0, 3)
    written = json.loads(record.read_text(encoding="utf-8"))
    rows = parents.read_caption_rows(out)
    assert rows and {row["caption_source"] for row in rows} == {driver.SOURCE}
    assert written["caption_sources"] == [driver.SOURCE]
    assert written["task"] == prompts.CAPTION_TASK_GM4
    assert written["out_sha256"]
    assert sum(len(job["posts"]) for job in written["jobs"]) == 19
    assert parents.assert_one_source(out.name, rows, parents.sources_named(written)) == {
        driver.SOURCE
    }


def test_the_runbooks_smoke_invocation_runs_to_a_written_record(tmp_path):
    """§B is the first command an operator types on a billed endpoint. Its flag shape is driven
    here against the fake client, because a runbook step that fails on syntax fails after the
    endpoint exists — and `--only` must narrow the record's population, not just its work."""
    out, record = tmp_path / "gm4_smoke1.jsonl", tmp_path / "serving_visb_smoke.json"
    # The claim below is "this invocation did not touch the default path", NOT "nothing ever
    # writes there" — vis-b-r ran the real §B and the file now exists as bought evidence. An
    # absence assertion would have reddened the suite the moment the runbook was executed.
    default = REPO_ROOT / "results" / "smoke" / "gm4_smoke1.jsonl"
    before = default.read_bytes() if default.exists() else None
    assert (
        driver.main(
            [
                "--scope",
                "smoke1",
                "--only",
                "@atb_market_official:4340",
                "--dump-prefix",
                "/runpod-volume/captions_visb_smoke",
                "--record",
                str(record),
                "--out",
                str(out),
                "--smoke",
            ]
        )
        == 0
    )
    written = json.loads(record.read_text(encoding="utf-8"))
    assert len(written["jobs"]) == 1, "§B reads jobs[0]"
    # §B compares `[row["sha8"] for row in dump]` against this field, so it has to be the LIST
    # of the job's post digests and not one post's digest — a scalar would never compare equal
    digests = written["jobs"][0]["sha8"]
    assert isinstance(digests, list) and len(digests) == 1
    assert re.fullmatch(r"[0-9a-f]{8}", digests[0])
    assert written["jobs"][0]["dump_path"] == "/runpod-volume/captions_visb_smoke_00.jsonl"
    assert written["population"] == {
        "media_only_posts": 1,
        "captioned": 1,
        "transcribed_polls": 0,
        "unusable": [],
        "no_surrogate_at_all": [],
    }
    assert len(parents.read_caption_rows(out)) == 1
    # an explicit --out/--record survives --smoke: the redirect fires only on the defaults
    assert (default.read_bytes() if default.exists() else None) == before


def test_a_slice_stays_under_runpods_documented_run_ceiling():
    """RunPod documents 10 MB on `/run`; the pictures travel inside the job because
    `data/annotation/**` is gitignored and cannot ride to the worker on the volume."""
    packed = [{"name": f"p{n}", "bytes": 3_000_000} for n in range(5)]
    jobs = driver.slices(packed, driver.MAX_PAYLOAD_MB)
    assert driver.MAX_PAYLOAD_MB < 10.0
    assert all(sum(post["bytes"] for post in job) <= driver.MAX_PAYLOAD_MB * 1e6 for job in jobs)
    assert [len(job) for job in jobs] == [2, 2, 1]
    with pytest.raises(SystemExit, match="above the"):
        driver.slices([{"name": "huge", "bytes": 9_000_000}], driver.MAX_PAYLOAD_MB)


def test_the_driver_sends_batch_1_and_one_registered_source():
    assert driver.SOURCE in parents.CAPTION_SOURCES
    assert driver.TASK == prompts.CAPTION_TASK_GM4
    assert driver.MAX_IMAGES == pattern.MAX_IMAGES, "the bridge compares models, not inputs"
    assert driver.SESSIONS == {"vis-b": 1.00, "vis-c": 1.50}, "SPEC amendment 3.13 (4)"
    source = (REPO_ROOT / "scripts" / "caption_gm4_5c1.py").read_text(encoding="utf-8")
    assert "forward_batch_size=1" in source


def test_the_projection_subtracts_the_boot_before_taking_a_per_post_rate():
    """vis-b's re-pilot hid a whole cold start inside `worker_seconds` and its per-post rate came
    out 2x high. §C.1 prices the boot ONCE, as the pre-registered constant, and the measured
    start is reported beside it — never substituted into the line the stop is taken on."""
    rate = 0.00030669
    seen = driver.projection(
        boot_seconds=215.0, worker_seconds=215.0 + 60.0, rows_done=4, rows_total=100, rate=rate
    )
    assert seen["marginal_seconds_per_row"] == 15.0
    assert seen["projected_usd"] == round(100 * 15.0 * rate + driver.COLD_START_USD, 4)
    assert seen["cold_start_usd_preregistered"] == driver.COLD_START_USD
    assert seen["cold_start_usd_measured_here"] == round(215.0 * rate, 4)
    # the naive reading, which is what the retraction was about
    naive = (215.0 + 60.0) / 4 * 100 * rate
    assert naive > seen["projected_usd"] * 2, "the boot-in-every-post reading is the one to avoid"


def test_the_rate_is_read_from_the_settled_record_not_typed_in():
    assert driver.rate_usd_per_second() == 0.00030669


def test_the_gate_stops_the_run_and_names_what_was_never_asked_for():
    """A slice that was not bought is `unbought`, not `unusable`: nothing failed, the money ran
    out. The two must not merge — one is a finding about the model, the other about the cap."""
    calls = []

    class Client:
        dump_path = None

        def caption(self, task, albums):
            calls.append(len(albums))
            return [{"content": "морозиво", "finish_reason": "stop"} for _ in albums]

    jobs = [
        [
            {
                "name": f"@a:{n}",
                "urls": [],
                "bytes": 1,
                "images_sent": 1,
                "images_available": 1,
                "sha8": "00000000",
            }
        ]
        for n in range(4)
    ]
    outcomes = driver.run(Client(), jobs, None, lambda *a: None, lambda i, done: "over cap")
    assert calls == [1], "the gate fires before the SECOND slice, so exactly one was bought"
    assert [row["name"] for row in outcomes] == ["@a:0"]
    assert all(row["unusable"] is None for row in outcomes)
