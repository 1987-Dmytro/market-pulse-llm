"""The sku-b driver, everything about the paid attempt that can be proved for $0.

One session, one attempt, a $0.35 cap and a failed bar closes B by measurement — so every failure
here is expensive and most of them are quiet. What is pinned:

* the dump's columns are DERIVED from the pre-registration's own sentence, and the attribute column
  is the WIRE name, read through `positions.wire_key`;
* the page leg is exactly the 108 SENT pages, each verified against the bytes on disk;
* the text leg is the 30 adjudicated rows, given columns only — the ticks are gold and never travel;
* a job that would exceed the payload budget is a refusal, never a shortened album;
* a parse refusal is counted by reason and is never an empty answer;
* the identity stop reads `results/sku_pilot_serving.json` and restates nothing;
* `--smoke` writes no ledger, spends nothing, and prints one line per source.
"""

import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest
from market_pulse import positions, prompts, serving
from market_pulse.registry import load_registry
from market_pulse.zero_shot import ApiError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


driver = _script("positions_gm4_skub")


@pytest.fixture(scope="module")
def prereg() -> dict:
    return json.loads(driver.PREREG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(driver.MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reference() -> dict:
    return json.loads(driver.REFERENCE.read_text(encoding="utf-8"))


# --- the dump's columns -------------------------------------------------------------------------


def test_the_dump_columns_are_read_out_of_the_pre_registration(prereg):
    """Bar 2 is the team lead reading this dump against the page images, so the columns are the
    registered sentence's — derived from it rather than retyped beside it, because a retyped list
    drifts silently and the drift shows up as a field the reader expected and did not get."""
    assert driver.dump_fields(prereg) == (
        "item",
        "page",
        "file",
        "sha256",
        "brand_raw",
        "brand_id",
        "line",
        "category",
        "size",
        "fat",
        "price_promo",
        "price_old",
        "discount_pct_printed",
        "price_qualifier",
        "tier",
        "depth",
        "depth_disagrees_with_printed",
    )


def test_the_attribute_column_is_the_wire_name_and_not_the_schema_name(prereg):
    """The sentence says `fat`, because v2 keeps every bar byte-equal to v1 and was written before
    SPEC 3.17 (8) renamed the schema field. The dump carries the wire name through `wire_key` —
    `row["attribute"]` would be a lookup that returns a legal absent on every single row."""
    fields = driver.dump_fields(prereg)
    assert positions.wire_key("attribute", driver.FAMILY) in fields
    assert "attribute" not in fields
    assert "attribute_pct" not in fields


def test_prose_that_is_not_a_field_name_stops_the_writer(prereg):
    """The control that caught this for real: "the page's file and sha256" is one phrase with an
    `and` inside it, and splitting before looking it up produced a column literally called "the
    page's file" — legal-looking JSON nobody can address."""
    moved = json.loads(json.dumps(prereg))
    moved["bars"]["price_pair_accuracy"]["procedure"] = (
        "sku-b writes a per-position dump — one row per extracted position carrying item, the"
        " reviewer's own opinion, brand_raw. The team lead opens each cited page image."
    )
    with pytest.raises(SystemExit, match="as prose rather than as field names"):
        driver.dump_fields(moved)


def test_a_row_carries_every_registered_column_in_order(prereg):
    fields = driver.dump_fields(prereg)
    position = positions.Position(
        brand_id="rud",
        brand_raw="Рудь",
        line="Пломбір",
        category="ice-cream",
        size_value=450.0,
        size_unit="г",
        attribute_pct=12.0,
        price_promo=89.9,
        price_old=129.9,
        discount_pct_printed=31.0,
        price_qualifier="exact",
        price_origin="retail_leaflet",
        carrier="leaflet_page",
        extraction_source="positions_post_gm4",
    )
    source = {"item": "@atb:1", "page": 2, "file": "a.jpg", "sha256": "abc"}
    row = driver.row_for(position, source, fields)
    assert tuple(row) == fields
    assert row["fat"] == 12.0 and row["size"] == "450 г"
    assert row["tier"] == "position"
    assert row["depth"] == pytest.approx((129.9 - 89.9) / 129.9)
    assert row["depth_disagrees_with_printed"] is False


# --- the page leg -------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sent_pages(reference) -> list[dict]:
    return driver.pages(reference)


def test_the_page_leg_is_exactly_the_pages_that_were_sent(reference, sent_pages):
    """Never the 159 available. The gold is one reviewer's reading of the SENT set, so a brand on a
    page nobody sent is not in the gold and reading it would score as a false positive for being
    right (`sku_pilot_prereg_v2.json :: R2`)."""
    assert len(sent_pages) == reference["population"]["pages_sent"] == 108
    assert reference["population"]["pages_available"] == 159
    files = {page["file"] for page in sent_pages}
    never_sent = {name for post in reference["posts"] for name in post["pages_not_sent"]}
    assert never_sent and not (files & never_sent)


def test_every_page_is_checked_against_the_bytes_on_disk(reference, tmp_path):
    """`images_verified` in the reference records what was true when it was BUILT. A page whose
    bytes moved since is a different image under a gold set written against the old one."""
    moved = json.loads(json.dumps(reference))
    moved["posts"][0]["pages_sent"][0]["sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="no longer hash to what"):
        driver.pages(moved)

    absent = json.loads(json.dumps(reference))
    absent["posts"][0]["pages_sent"][0]["file"] = "data/annotation/nope.jpg"
    with pytest.raises(SystemExit, match="are not on disk"):
        driver.pages(absent)


def test_a_page_travels_as_its_own_one_image_album(sent_pages):
    for page in sent_pages[:5]:
        assert page["url"].startswith("data:image/")
        assert page["bytes"] == len(page["url"])


# --- the text leg -------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def text_rows(manifest) -> list[dict]:
    return driver.rows(manifest, REPO_ROOT / manifest["pack"])


def test_the_text_leg_is_the_thirty_adjudicated_rows(manifest, text_rows):
    assert len(text_rows) == manifest["rows"] == 30
    assert [row["id"] for row in text_rows] == manifest["ids"]


def test_the_gold_ticks_never_reach_the_model(manifest, text_rows):
    """The five tick columns ARE the answer to bar 3. Sending them would be asking the model to
    agree with itself, and nothing in the reply would say it had been told."""
    ticks = set(manifest["to_fill"])
    assert ticks and not (ticks & set(text_rows[0]))
    assert set(text_rows[0]) == set(manifest["given_columns"])


def test_a_pack_that_moved_under_the_manifest_is_refused(manifest, tmp_path):
    """Both readings: the ids and their order, and the hash over the columns the operator was told
    not to touch. A row whose `text` moved was adjudicated against a different question."""
    import csv

    pack_path = REPO_ROOT / manifest["pack"]
    with pack_path.open(encoding="utf-8-sig", newline="") as handle:
        table = list(csv.DictReader(handle, delimiter=";"))

    edited = tmp_path / "text30.csv"

    def write(rows):
        with edited.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=list(rows[0]), delimiter=";", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)

    short = json.loads(json.dumps(table))[:-1]
    write(short)
    with pytest.raises(SystemExit, match="the ids or their order moved"):
        driver.rows(manifest, edited)

    touched = json.loads(json.dumps(table))
    touched[0]["text"] = touched[0]["text"] + " (edited)"
    write(touched)
    with pytest.raises(SystemExit, match="adjudicated against a different question"):
        driver.rows(manifest, edited)


def test_the_warm_up_row_is_not_one_of_the_thirty(text_rows):
    """SPEC 3.17 (9) opens the paid session on inputs NO bar is scored on. A warm-up row that had
    drifted into the pack would spend gold on the cold start."""
    assert driver.WARMUP_ROW.strip() not in {row["text"].strip() for row in text_rows}


# --- packing ------------------------------------------------------------------------------------


def test_the_budget_is_numeric_and_under_the_documented_ceiling():
    assert isinstance(driver.MAX_PAYLOAD_MB, float)
    assert driver.MAX_PAYLOAD_MB < 10.0, "RunPod documents /run at 10 MB"


def test_an_oversized_item_is_refused_and_never_shortened():
    """A shortened album is a different instrument. The refusal names the file rather than dropping
    an image, resizing it, or splitting the page across two calls."""
    with pytest.raises(SystemExit, match="encode above the"):
        driver.jobs([{"file": "huge.jpg", "bytes": 9_000_000}], 8.0)


def test_items_are_packed_whole_and_in_order():
    items = [{"file": f"{n}.jpg", "bytes": 3_000_000} for n in range(5)]
    packed = driver.jobs(items, 8.0)
    assert [len(job) for job in packed] == [2, 2, 1]
    assert [item["file"] for job in packed for item in job] == [item["file"] for item in items]
    for job in packed:
        assert sum(item["bytes"] for item in job) <= 8_000_000


def test_the_real_page_population_packs_under_the_budget(sent_pages):
    packed = driver.jobs(sent_pages, driver.MAX_PAYLOAD_MB)
    assert sum(len(job) for job in packed) == len(sent_pages)
    assert max(sum(page["bytes"] for page in job) for job in packed) <= 8_000_000


# --- parsing: a refusal is a reason, never an empty answer ---------------------------------------

CATEGORIES = frozenset({"ice-cream", "milk"})
ALIASES = {"рудь": "rud"}


def reply(content: str) -> dict:
    return {"content": content, "finish_reason": "stop"}


def test_an_unreadable_reply_is_counted_by_reason():
    found, reason = driver.parse(
        reply('[{"brand": "Рудь", '), "leaflet_page", "t", CATEGORIES, ALIASES
    )
    assert found == [] and reason == "malformed JSON"


def test_an_empty_array_is_an_answer_and_not_a_failure():
    found, reason = driver.parse(reply("[]"), "leaflet_page", "t", CATEGORIES, ALIASES)
    assert found == [] and reason is None


def test_the_wire_key_is_what_carries_the_attribute():
    """The reply says `fat` because that is what the registered prompt asks for. If the parser were
    handed the schema name the percentage would vanish and every position would drop a rung."""
    found, reason = driver.parse(
        reply('[{"brand": "Рудь", "category": "milk", "fat": "2,5%"}]'),
        "leaflet_page",
        "t",
        CATEGORIES,
        ALIASES,
    )
    assert reason is None and found[0].attribute_pct == 2.5
    refused, why = driver.parse(
        reply('[{"brand": "Рудь", "category": "milk", "attribute": "2,5%"}]'),
        "leaflet_page",
        "t",
        CATEGORIES,
        ALIASES,
    )
    assert refused == [] and "unasked key" in why


# --- the run: identity stop, no ledger, per-source lines ------------------------------------------


@pytest.fixture(scope="module")
def pin() -> dict:
    return json.loads(driver.PIN.read_text(encoding="utf-8"))


def slow_endpoint(pin, *, gold_seconds_per_call):
    """The smoke's own fake, priced to get expensive once the two warm-up calls are behind it."""
    registry = load_registry(driver.REGISTRY)
    return driver.FakeEndpoint(
        pin["expected_worker"],
        positions.category_keys(registry.taxonomy),
        gold_seconds_per_call=gold_seconds_per_call,
    )


def run_smoke(tmp_path, extra=(), client=None):
    out = tmp_path / "dump.jsonl"
    record = tmp_path / "record.json"
    ledger = tmp_path / "ledger.json"
    code = driver.main(
        [
            "--leg",
            "text",
            "--out",
            str(out),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
            *(["--smoke"] if client is None else []),
            *extra,
        ],
        client=client,
    )
    return code, out, record, ledger


def test_the_smoke_drives_the_whole_write_path_and_spends_nothing(tmp_path, capsys):
    code, out, record, ledger = run_smoke(tmp_path)
    assert code == 0
    assert not ledger.exists(), "a $0 contract must not create the paid session's anchor"

    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["smoke"] is True
    assert written["cost"]["usd"] is None and written["cost"]["cap_usd"] == 0.35
    assert written["attempts_per_job"] == 1
    assert written["population"]["text_rows"] == 30

    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert rows and set(rows[0]) == set(written["dump"]["columns"])
    assert written["dump"]["sha256"] == sha256(out.read_bytes()).hexdigest()

    # per-source lines, not only aggregates — a runbook step can `test -s` this
    printed = capsys.readouterr().out
    assert printed.count("position(s)") + printed.count("UNREADABLE") >= 30


def test_the_record_keeps_unreadable_and_empty_apart(tmp_path):
    """The two outcomes a driver most easily conflates. The fake client breaks one reply in seven
    on purpose and empties one in five, so both branches are exercised rather than assumed."""
    _, _, record, _ = run_smoke(tmp_path)
    written = json.loads(record.read_text(encoding="utf-8"))["extraction"]
    assert written["unreadable"] and written["empty_answers"]
    assert set(written["unreadable_by_reason"])
    assert not set(row["source"] for row in written["unreadable"]) & set(written["empty_answers"])
    assert written["unreadable_share"] == pytest.approx(len(written["unreadable"]) / 30, abs=1e-4)


def test_the_identity_stop_refuses_a_worker_that_is_not_the_pin(tmp_path, pin):
    """The stop reads the committed pin and restates nothing. Driven with a client that answers
    like a CAPTION worker — the shape an endpoint updated from the wrong template would have."""

    class WrongWorker:
        dump_path = None

        def info(self):
            return dict(pin["expected_worker"]) | {"serving_config": "CAPTION"}

        def positions(self, task, items):  # pragma: no cover — never reached
            raise AssertionError("a paid call was made after the identity stop should have fired")

        def timing(self):
            return {}

    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        run_smoke(tmp_path, client=WrongWorker())


def test_a_dump_that_already_exists_is_never_overwritten(tmp_path):
    """It is what a paid run bought, and there is one attempt. Re-running would spend again."""
    run_smoke(tmp_path)
    with pytest.raises(SystemExit, match="already exists"):
        run_smoke(tmp_path)


def test_the_dry_run_reaches_no_client_at_all(tmp_path, capsys):
    class Exploding:
        dump_path = None

        def info(self):  # pragma: no cover
            raise AssertionError("--dry-run asked the endpoint something")

    code = driver.main(["--leg", "text", "--dry-run"], client=Exploding())
    assert code == 0
    assert "text leg   30 rows" in capsys.readouterr().out


# --- the projection gate: the one path that enforces the cap inside a run ------------------------


def test_the_projection_prices_what_is_left_and_never_re_adds_the_boot():
    """`caption_gm4_5c1.projection` adds a pre-registered cold-start constant on top of measured
    seconds. Here the boot has already been billed by the time any gate runs, so re-adding it would
    double-count; everything paid is inside `billed` and only what is LEFT is projected.

    The idle tail is the one term that is added rather than measured, and it belongs to the
    SESSION: it is inside `projected_usd`, outside `spent_usd` (it has not been billed yet) and
    outside the marginal (it is charged once, not once per call)."""
    tail = driver.IDLE_TAIL_SECONDS * 0.001
    seen = driver.projection(opened_seconds=200.0, billed=300.0, done=40, total=140, rate=0.001)
    assert seen["marginal_seconds_per_call"] == pytest.approx(2.5)
    assert seen["spent_usd"] == pytest.approx(0.3)
    assert seen["remaining_usd"] == pytest.approx(100 * 2.5 * 0.001)
    assert seen["projected_usd"] == pytest.approx(0.3 + 0.25 + tail)
    # nothing left to buy: the projection is what has been spent plus the tail still to come,
    # never a re-added cold start
    done = driver.projection(opened_seconds=200.0, billed=300.0, done=140, total=140, rate=0.001)
    assert done["remaining_usd"] == 0.0
    assert done["projected_usd"] == pytest.approx(done["spent_usd"] + tail)


def test_a_client_that_reports_no_clock_is_read_as_zero_and_never_raises():
    """The crash this replaced: `client.timing()["worker_seconds"]` raised `KeyError` on the first
    gate call, so the whole cap-enforcement path died the moment it was exercised."""

    class Silent:
        def timing(self):
            return {}

    assert driver.billed_seconds(Silent()) == 0.0

    class Nothing:
        def timing(self):
            return None

    assert driver.billed_seconds(Nothing()) == 0.0


def test_the_gate_stops_the_run_and_leaves_the_rest_unbought(tmp_path, capsys, pin):
    """A budget the run passes on its first job. What is skipped is `unbought` — not asked for,
    not failed — and the stop reaches the SECOND leg too.

    The fake gets EXPENSIVE after the warm-up, and that is the whole scenario the in-run gate
    exists for. On a flat clock the go/no-go of 3.17 (10)(a) and this gate compute the identical
    number by construction — so a budget low enough to trip this one would be refused before the
    first gold call, and this path could not be driven through `main` at all."""
    out, record, ledger = tmp_path / "d.jsonl", tmp_path / "r.json", tmp_path / "l.json"
    code = driver.main(
        [
            "--smoke",
            "--project-stop-usd",
            "0.30",
            "--out",
            str(out),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
        ],
        client=slow_endpoint(pin, gold_seconds_per_call=60.0),
    )
    assert code == 0
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["projection"]["stopped_early"] is True
    assert written["population"]["unbought"], "the pages never asked for must be named"
    assert written["population"]["asked"] < 138
    assert written["projection"]["per_gate"], "the gate must have run at all"
    printed = capsys.readouterr().out
    assert "STOP before positions_post_gm4" in printed
    assert "STOP before positions_text_gm4" in printed, "the stop must reach the second leg"


def test_a_generous_budget_buys_the_whole_population(tmp_path):
    out, record, ledger = tmp_path / "d.jsonl", tmp_path / "r.json", tmp_path / "l.json"
    driver.main(
        [
            "--smoke",
            "--project-stop-usd",
            "9.99",
            "--out",
            str(out),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
        ]
    )
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["population"]["asked"] == 138
    assert written["population"]["unbought"] == []
    assert written["projection"]["stopped_early"] is False


def test_the_gate_counts_calls_across_BOTH_legs(tmp_path):
    """The bug this pins: `run_leg` used to own its outcome list, so `done` restarted at 0 when the
    text leg opened while the billed clock carried the whole page leg — and the marginal the stop
    read was 108 pages' seconds divided by a handful of rows."""
    out, record, ledger = tmp_path / "d.jsonl", tmp_path / "r.json", tmp_path / "l.json"
    driver.main(
        [
            "--smoke",
            "--project-stop-usd",
            "9.99",
            "--out",
            str(out),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
        ]
    )
    gates = json.loads(record.read_text(encoding="utf-8"))["projection"]["per_gate"]
    counts = [gate["calls_done"] for gate in gates]
    assert counts == sorted(counts), "calls_done must never restart"
    # the LAST gate is the one before the text leg's first job, and it carries the whole page leg.
    # Under a per-leg counter it would have read 0 — and the old `and index` condition skipped a
    # leg's first job entirely, so this gate did not exist at all.
    assert counts[-1] == 108, "the text leg's first gate must carry the page leg's 108 calls"
    for gate in gates:
        assert gate["calls_total"] == 138
        # the warm-up's two non-gold calls are billed but are NOT in the marginal
        assert gate["marginal_seconds_per_call"] == pytest.approx(
            driver.FakeEndpoint.SMOKE_SECONDS_PER_CALL, abs=1e-6
        )
        assert gate["billed_seconds"] > gate["opened_seconds"] > 0


def test_the_smoke_clock_is_synthetic_and_says_so(tmp_path):
    """A fake whose `timing()` reported nothing left the gate with a marginal of zero — a gate
    that can never fire is a gate nothing proves. The seconds are made up; the record says so."""
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    driver.main(["--smoke", "--leg", "text", "--out", str(out), "--record", str(record)])
    timing = json.loads(record.read_text(encoding="utf-8"))["timing"]
    assert timing["smoke"] is True
    assert timing["worker_seconds"] > driver.FakeEndpoint.SMOKE_BOOT_SECONDS


def test_the_driver_names_the_two_registered_tasks_and_no_others():
    source = (REPO_ROOT / "scripts" / "positions_gm4_skub.py").read_text(encoding="utf-8")
    for task in prompts.POSITIONS:
        assert f"POSITIONS_TASK_{'PAGE' if 'post' in task else 'TEXT'}" in source
    assert "CAPTION_TASK" not in source


# --- the cap discipline of SPEC 3.17 (10) ---------------------------------------------------------


class OneBadJob:
    """The smoke's fake with ONE gold job replaced by a failure, and everything else answering.

    The wrapper counts the two non-gold warm-up calls of 3.17 (9) out first, so `kill_gold_job`
    numbers the jobs a reader of the run's own output sees.
    """

    def __init__(self, inner, *, kill_gold_job: int, error) -> None:
        self.inner, self.kill_gold_job, self.error = inner, kill_gold_job, error
        self.seen, self.dump_path = 0, None

    def info(self) -> dict:
        return self.inner.info()

    def timing(self) -> dict:
        return self.inner.timing()

    def positions(self, task: str, items: list) -> list[dict]:
        self.seen += 1
        if self.seen - driver.FakeEndpoint.WARMUP_CALLS == self.kill_gold_job:
            raise self.error  # it ran and it billed; only its answer is missing
        return self.inner.positions(task, items)


def test_a_job_the_clock_kills_ends_the_run_and_not_just_the_batch(tmp_path, capsys, pin):
    """SPEC 3.17 (10)(c). A TIMED_OUT job billed the WHOLE execution timeout, so nothing about it
    says the next job will be cheaper — and the projection gate cannot see inside a job. Its own
    items are forfeit under one attempt, everything after it is `unbought`, the second leg never
    opens, and the record is still written and says why."""
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    client = OneBadJob(
        slow_endpoint(pin, gold_seconds_per_call=2.5),
        kill_gold_job=3,
        error=serving.JobExpired(-1, "job abc ended TIMED_OUT: {'id': 'abc'}"),
    )
    code = driver.main(["--smoke", "--out", str(out), "--record", str(record)], client=client)
    assert code == 0

    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["ended_by"] and "TIMED_OUT" in written["ended_by"]
    assert {row["leg"] for row in written["outcomes"]} == {"page"}, "the text leg must never open"
    assert written["population"]["asked"] < 138
    assert len(written["population"]["unbought"]) > 30, "the whole text leg is unbought"
    forfeit = [
        row for row in written["outcomes"] if row["unreadable"] and "TIMED_OUT" in row["unreadable"]
    ]
    assert forfeit, "the killed job's own items are named, not silently dropped"
    printed = capsys.readouterr().out
    assert "RUN ENDS" in printed and "STOP AND REPORT" in printed


def test_an_ordinary_job_failure_names_its_items_and_the_leg_continues(tmp_path, pin):
    """The negative control for the test above, and the reason `JobExpired` is raised only for
    TIMED_OUT: a FAILED job is one batch's problem. Widening the type would have converted every
    job failure into a dead run — a much more expensive behaviour than the one it replaced."""
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    client = OneBadJob(
        slow_endpoint(pin, gold_seconds_per_call=2.5),
        kill_gold_job=3,
        error=ApiError(-1, "job abc ended FAILED: {'id': 'abc'}"),
    )
    driver.main(["--smoke", "--out", str(out), "--record", str(record)], client=client)

    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["ended_by"] is None
    assert {row["leg"] for row in written["outcomes"]} == {"page", "text"}
    assert written["population"]["asked"] == 138 and written["population"]["unbought"] == []
    assert any("ended FAILED" in (row["unreadable"] or "") for row in written["outcomes"])


def test_no_single_job_can_out_bill_the_cap():
    """The blocker (10)(c) was written for, as arithmetic. The gate re-prices BETWEEN jobs, so the
    execution timeout is the only thing bounding one wedged worker — and the value this replaced
    could bill more than the whole cap while every guard in the driver reported normally."""
    rate = driver.leader.rate_usd_per_second()
    assert driver.JOB_TIMEOUT_S * rate < driver.CAP_USD
    assert 1800.0 * rate > driver.CAP_USD, "the 1800 s this replaced — one job, 1.58x the cap"
    # and still more than twice the longest job the projection predicts: the text leg is ONE job
    # carrying all 30 rows at the stated decode uplift
    assert driver.JOB_TIMEOUT_S >= 2 * (30 * 4.262 * (800 / 256))
    assert serving.execution_policy(driver.JOB_TIMEOUT_S, driver.JOB_TTL_S) == {
        "executionTimeout": 900_000,
        "ttl": 3_600_000,
    }


def test_the_go_no_go_refuses_before_the_first_gold_call(tmp_path, capsys):
    """SPEC 3.17 (10)(a). The in-run gate cannot answer this question — it needs a gold call to
    have a marginal at all — and under one attempt a run stopped after two pages is the most
    expensive outcome available: the money is gone and no bar is scoreable. This is the only stop
    that leaves nothing half-bought, and (10)(a) says it consumes NO attempt."""
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    with pytest.raises(SystemExit, match="REFUSED before the first gold call"):
        driver.main(
            [
                "--smoke",
                "--project-stop-usd",
                "0.10",
                "--out",
                str(out),
                "--record",
                str(record),
            ]
        )
    assert not out.exists(), "a stop before gold must leave NO gold artifact on disk"
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["stopped_before_gold"] is True
    assert written["population"]["asked"] == 0
    assert len(written["population"]["unbought"]) == 138
    assert written["dump"]["rows"] == 0 and written["dump"]["path"] is None
    # "a re-registration", not "a v3 registration": the same stop can fire inside the RESUMED
    # session, which already runs under v3, and a message naming the version it is running would
    # send the next reader to the record they are holding
    assert "NO attempt" in written["why"] and "re-registration" in written["why"]
    assert written["projection"]["go_no_go"]["refuse"] is True
    assert written["warmup"]["replies"], "the warm-up happened and is recorded — it was paid for"
    assert "REFUSE" in capsys.readouterr().out


def test_a_warm_up_the_budget_can_afford_proceeds_to_gold(tmp_path):
    """The other way, on the same path: a go/no-go that only ever refused would be a gate nothing
    proves. The budget here is above the projection and every one of the 138 calls is made."""
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    code = driver.main(
        ["--smoke", "--project-stop-usd", "0.30", "--out", str(out), "--record", str(record)]
    )
    assert code == 0
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["stopped_before_gold"] is False
    assert written["projection"]["go_no_go"]["refuse"] is False
    assert written["population"]["asked"] == 138 and out.exists()


def test_the_go_no_go_prices_each_leg_from_its_own_warm_up_call():
    """108 images and 30 strings are not the same call, and the warm-up makes exactly one of each.
    A single blended figure would charge the image leg's seconds to the text leg's 30 calls."""
    args = dict(billed=100.0, n_pages=108, n_rows=30, rate=0.001)
    seen = driver.go_no_go(page_marginal=4.0, text_marginal=1.0, budget=None, **args)
    assert seen["gold_calls"] == 138
    assert seen["gold_seconds"] == pytest.approx(108 * 4.0 + 30 * 1.0)
    assert seen["projected_usd"] == pytest.approx(
        (100.0 + 462.0 + driver.IDLE_TAIL_SECONDS) * 0.001, abs=1e-6
    )
    blended = driver.go_no_go(page_marginal=2.5, text_marginal=2.5, budget=None, **args)
    assert blended["gold_seconds"] != seen["gold_seconds"]
    # both ways against a budget, and `refuse` is False when there is no budget to refuse against
    assert seen["refuse"] is False
    assert (
        driver.go_no_go(page_marginal=4.0, text_marginal=1.0, budget=1.0, **args)["refuse"] is False
    )
    assert (
        driver.go_no_go(page_marginal=4.0, text_marginal=1.0, budget=0.1, **args)["refuse"] is True
    )


def test_the_warm_up_reads_the_clock_between_its_two_calls():
    """One reading at the end would give a blend, and the go/no-go would price both legs at it."""

    class Answering:
        def positions(self, task, items):
            return [{"content": "[]", "finish_reason": "stop"}]

    ticks = iter([10.0, 40.0, 45.0])
    out = driver.warmup(Answering(), "page_task", "text_task", clock=lambda _client: next(ticks))
    assert out["page_task"]["marginal_seconds"] == 30.0
    assert out["text_task"]["marginal_seconds"] == 5.0


def test_the_idle_tail_is_a_named_term_in_the_go_no_go_too():
    """Serverless bills wall uptime plus the endpoint's idle tail, and a run of nothing still pays
    it. $0.0184 at the settled rate — larger than the headroom the stated corner had."""
    assert driver.IDLE_TAIL_SECONDS == 60.0
    empty = driver.go_no_go(
        billed=0.0,
        page_marginal=0.0,
        text_marginal=0.0,
        n_pages=0,
        n_rows=0,
        rate=0.001,
        budget=None,
    )
    assert empty["gold_seconds"] == 0.0
    assert empty["projected_usd"] == pytest.approx(driver.IDLE_TAIL_SECONDS * 0.001)


# --- the resume of SPEC 3.17 (11) -----------------------------------------------------------------


@pytest.fixture(scope="module")
def prereg_v3() -> dict:
    return json.loads(driver.PREREG_RESUME.read_text(encoding="utf-8"))


def run_resume(tmp_path, extra=(), prereg=None, client=None):
    """`--resume --smoke` through the whole write path: no network, no spend, real artifacts read."""
    out, record, ledger = tmp_path / "d.jsonl", tmp_path / "r.json", tmp_path / "l.json"
    code = driver.main(
        [
            "--resume",
            "--out",
            str(out),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
            *(["--prereg", str(prereg)] if prereg else []),
            *(["--smoke"] if client is None else []),
            *extra,
        ],
        client=client,
    )
    return code, out, record, ledger


def doctored(tmp_path, mutate) -> Path:
    """The registration with one thing moved, written where the driver will read it."""
    body = json.loads(driver.PREREG_RESUME.read_text(encoding="utf-8"))
    mutate(body["resume"])
    path = tmp_path / "prereg_moved.json"
    path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    return path


def test_the_resume_buys_only_the_unbought_and_merges_both_sessions(tmp_path, prereg_v3):
    """SPEC 3.17 (11)(a) end to end. The population narrows to the 121 the run record names as
    unbought, the 17 bought answers are never re-asked, and what the record holds afterwards is the
    MERGED bar input — 138 outcomes, both dumps, every row naming the session that bought it."""
    code, out, record, _ = run_resume(tmp_path)
    assert code == 0
    written = json.loads(record.read_text(encoding="utf-8"))
    already = prereg_v3["resume"]["bought_already"]

    assert written["population"]["asked_this_session"] == 121
    assert written["population"]["asked"] == 138
    assert written["population"]["unbought"] == []
    assert written["population"]["pages_sent"] == 108, "the merged record keeps R2's denominator"

    sources = [row["source"] for row in written["outcomes"]]
    assert len(sources) == len(set(sources)) == 138
    assert set(already["asked"]) < set(sources) and set(already["unbought"]) < set(sources)
    bought = {row["source"]: row[driver.BOUGHT_BY] for row in written["outcomes"]}
    assert {bought[source] for source in already["asked"]} == {driver.PHASE}
    assert {bought[source] for source in already["unbought"]} == {driver.RESUME_PHASE}

    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == written["dump"]["rows"] > already["dump"]["rows"]
    sealed = REPO_ROOT / already["dump"]["path"]  # the registration's own path, not a derived one
    assert rows[: already["dump"]["rows"]] == [
        json.loads(line) | {driver.BOUGHT_BY: driver.PHASE}
        for line in sealed.read_text(encoding="utf-8").splitlines()
    ], "the first session's rows travel into the merged dump unchanged but for their provenance"
    assert written["dump"]["columns"][-1] == driver.BOUGHT_BY
    assert written["resume"]["sessions"][0]["phase"] == driver.PHASE
    assert "sha256" not in written["resume"]["sessions"][1], "a record cannot carry its own hash"


def test_the_sealed_artifacts_of_the_first_session_are_never_touched(tmp_path, prereg_v3):
    """The whole reason the resumed session writes NEW files: `resume.bought_already` pins the first
    session's dump, so an in-place append would break the pin that proves the 17 answers were not
    re-asked — in the same commit the rows landed."""
    already = prereg_v3["resume"]["bought_already"]
    before = {
        path: sha256((REPO_ROOT / path).read_bytes()).hexdigest()
        for path in (already["run_record"]["path"], already["dump"]["path"])
    }
    run_resume(tmp_path)
    for path, digest in before.items():
        assert sha256((REPO_ROOT / path).read_bytes()).hexdigest() == digest, path
    assert driver.RESUME_DUMP != REPO_ROOT / already["dump"]["path"]
    assert driver.RESUME_RECORD != REPO_ROOT / already["run_record"]["path"]


def test_the_resume_refuses_a_registration_whose_pins_have_moved(tmp_path):
    """A resume registered against bytes that have since moved would buy around evidence nobody can
    re-derive. Driven on each pin separately, because they fail for different reasons: a moved dump
    is lost evidence and a moved serving pin is (11)(b) broken — the resumed half would be a
    different instrument from the bought half, under one set of bars."""

    def move_dump(resume):
        resume["bought_already"]["dump"]["sha256"] = "0" * 64

    def move_pin(resume):
        resume["bought_already"]["serving_pin"]["sha256"] = "0" * 64

    with pytest.raises(SystemExit, match="the resume is registered against bytes"):
        run_resume(tmp_path, prereg=doctored(tmp_path, move_dump))
    with pytest.raises(SystemExit, match="freezes the instrument"):
        run_resume(tmp_path, prereg=doctored(tmp_path, move_pin))


def test_the_resume_refuses_when_an_unbought_id_already_carries_an_answer(tmp_path, prereg_v3):
    """The registration and the record disagreeing about what was bought. Neither can then say
    which 121 elements are left, and the honest move is to stop rather than to pick one."""
    bought = prereg_v3["resume"]["bought_already"]["asked"][0]

    def claim_it_is_unbought(resume):
        resume["bought_already"]["unbought"] = [bought, *resume["bought_already"]["unbought"]]

    with pytest.raises(SystemExit, match="already carry an answer"):
        run_resume(tmp_path, prereg=doctored(tmp_path, claim_it_is_unbought))


def test_the_resume_refuses_a_registration_that_is_not_the_records_population(tmp_path):
    """121 of the WRONG ids is still 121, so the sets are compared and not counted."""

    def swap_one(resume):
        resume["bought_already"]["unbought"] = [
            "data/annotation/captions_5c1/posts_media/nope.jpg",
            *resume["bought_already"]["unbought"][1:],
        ]

    with pytest.raises(SystemExit, match="not the same set"):
        run_resume(tmp_path, prereg=doctored(tmp_path, swap_one))


def test_a_bought_id_that_reaches_the_selection_is_refused(prereg_v3):
    """The third refusal, and it guards the SELECTION rather than the registration: a filter that
    inverted its condition would send the paid run at pages somebody already paid for. Checked on
    what is about to travel, because that is the value that ends up on the wire."""
    already = prereg_v3["resume"]["bought_already"]
    bought = already["asked"][0]
    plan = {"to_buy": {bought}, "already_asked": set(already["asked"])}
    with pytest.raises(SystemExit, match="EXACTLY ONCE"):
        driver.resume_population([{"file": bought, "bytes": 1}], plan, "page")
    # the control: an id that is genuinely unbought passes the same call
    fresh = already["unbought"][0]
    plan = {"to_buy": {fresh}, "already_asked": set(already["asked"])}
    kept = driver.resume_population([{"file": fresh, "bytes": 1}], plan, "page")
    assert [item["file"] for item in kept] == [fresh]
    assert kept[0][driver.BOUGHT_BY] == driver.RESUME_PHASE


def test_the_merged_record_refuses_a_source_answered_by_both_sessions(prereg_v3):
    """The output-side control. The plan's refusals guard what goes on the wire; this one guards
    what gets scored, and a duplicate here is an element bought twice with no gate able to see it."""
    already = prereg_v3["resume"]["bought_already"]
    plan = {
        "run": json.loads((REPO_ROOT / already["run_record"]["path"]).read_text(encoding="utf-8")),
        "run_record": REPO_ROOT / already["run_record"]["path"],
        "run_dump": REPO_ROOT / already["dump"]["path"],
    }
    honest = [{"source": already["unbought"][0], "unreadable": None, "n_positions": 1}]
    merged = driver.merge_sessions(plan, list(honest), [])
    assert len(merged["outcomes"]) == 18 and merged["previous"]["asked"] == 17

    twice = [{"source": already["asked"][0], "unreadable": None, "n_positions": 1}]
    with pytest.raises(SystemExit, match="BOTH sessions"):
        driver.merge_sessions(plan, twice, [])


def test_the_registered_warm_up_is_refused_if_it_drifted_into_gold(tmp_path, prereg_v3):
    """SPEC 3.17 (11)(c) is two claims and only one of them is about realism. The other is that
    neither input is gold — and a registered page that had drifted into the 108, or a row into the
    30, would spend a warm-up on an input a bar scores. Both directions, plus the control."""
    reference = json.loads(driver.REFERENCE.read_text(encoding="utf-8"))
    manifest = json.loads(driver.MANIFEST.read_text(encoding="utf-8"))
    resume = json.loads(json.dumps(prereg_v3["resume"]))

    honest = driver.resume_warmup_inputs(resume, reference, manifest, REPO_ROOT)
    assert honest["page"]["file"] == resume["warmup"]["page"]["file"]
    assert honest["text"] and honest["page_url"].startswith("data:image/")

    gold_page = json.loads(json.dumps(resume))
    gold_page["warmup"]["page"]["file"] = reference["posts"][0]["pages_sent"][0]["file"]
    with pytest.raises(SystemExit, match="SENT pages"):
        driver.resume_warmup_inputs(gold_page, reference, manifest, REPO_ROOT)

    gold_row = json.loads(json.dumps(resume))
    gold_row["warmup"]["text"]["id"] = manifest["ids"][0]
    with pytest.raises(SystemExit, match="one of the 30 adjudicated rows"):
        driver.resume_warmup_inputs(gold_row, reference, manifest, REPO_ROOT)

    moved = json.loads(json.dumps(resume))
    moved["warmup"]["page"]["sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="would price a different image"):
        driver.resume_warmup_inputs(moved, reference, manifest, REPO_ROOT)


def test_the_resumed_warm_up_is_the_registered_page_and_row_not_a_thumbnail(tmp_path, prereg_v3):
    """The finding that stopped the first session, closed. Its warm-up recorded «a generated 64x64
    image»; this one records a real leaflet page and a real collected row, by file and by sha."""
    _, _, record, _ = run_resume(tmp_path)
    inputs = json.loads(record.read_text(encoding="utf-8"))["warmup"]["inputs"]
    assert inputs["page"] == {
        "file": prereg_v3["resume"]["warmup"]["page"]["file"],
        "sha256": prereg_v3["resume"]["warmup"]["page"]["sha256"],
        "bytes": prereg_v3["resume"]["warmup"]["page"]["bytes"],
    }
    assert inputs["page"]["bytes"] > 100_000
    assert inputs["text"]["id"] == prereg_v3["resume"]["warmup"]["text"]["id"]
    assert "64x64" not in json.dumps(inputs)


def test_a_resume_without_its_own_registration_refuses(tmp_path):
    """`--resume --prereg <v2>` is a resumed session claiming a $0.35 cap and a population v2 does
    not contain. The default follows the flag; an explicit mismatch is refused rather than obeyed."""
    with pytest.raises(SystemExit, match="carries no `resume` block"):
        run_resume(tmp_path, prereg=driver.PREREG)


def test_the_two_records_the_two_caps_and_the_two_anchors_never_cross(tmp_path, monkeypatch, pin):
    """Every default follows the mode. A resumed session enforcing (11)(d)'s $0.45 against the first
    session's anchor would start $0.1965 in the red on a cap priced without it, and one writing at
    the first session's paths would overwrite the evidence its own registration pins."""
    assert driver.RESUME_CAP_USD == 0.45 and driver.CAP_USD == 0.35
    assert driver.anchor_key(driver.RESUME_PHASE) == "runpod_balance_at_sku-b-v3_start"
    assert driver.anchor_key() == "runpod_balance_at_sku-b_start"
    assert driver.RESUME_LEDGER != driver.LEDGER

    ledger = ledgered(tmp_path, monkeypatch, pin, balance=10.0)
    record = tmp_path / "r.json"
    driver.main(
        [
            "--resume",
            "--leg",
            "text",
            "--out",
            str(tmp_path / "d.jsonl"),
            "--record",
            str(record),
            "--ledger",
            str(ledger),
        ]
    )
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["cost"]["cap_usd"] == 0.45
    assert driver.anchor_key(driver.RESUME_PHASE) in json.loads(ledger.read_text(encoding="utf-8"))
    assert written["projection"]["stop_at_usd"] == pytest.approx(0.45)


def test_the_job_count_says_what_it_planned_and_what_it_submitted(tmp_path):
    """Dv153: `cost.jobs` was the PLAN. The run that stopped at 17 of 138 recorded 8 while 4 jobs
    ran, and read as a job count it said the session did twice the work it did.

    The 4 is the number to reproduce, and it is what makes this test worth having: the real client
    counts the `info` handshake and both warm-up calls alongside the gold job, so the fake was given
    the same handshake counter. Without it the fake would answer 3 here while production answered 4,
    and the field's own prose — which says the handshake is inside it — would be checked by nothing.
    """
    _, _, record, _ = run_resume(tmp_path, extra=["--leg", "text"])
    cost = json.loads(record.read_text(encoding="utf-8"))["cost"]
    assert cost["jobs_planned"] == 1, "30 rows pack into one job"
    assert cost["jobs_submitted"] == 4, "the handshake, the two warm-up calls and the job"
    assert "jobs" not in cost, "the ambiguous name is gone, not aliased"
    assert "handshake" in cost["jobs_reading"] and "warm-up" in cost["jobs_reading"]
    # the same shape the interrupted session recorded: 1 + 2 + 1 against 8 planned
    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))
    assert run["timing"]["calls"] == 4 and run["cost"]["jobs"] == 8


# --- the ledgered paths: driven with the network client replaced, everything else real ------------


def ledgered(tmp_path, monkeypatch, pin, *, balance, anchor=None, fails_after=None):
    """A run that reaches the ledger branch of `main` — the one `--smoke` deliberately skips.

    Only `serving.EndpointClient` and `guard.balance` are replaced; `read_ledger`, the budget
    arithmetic, the record write and the ledger append all run for real.
    """
    reads = {"n": 0}

    def read_balance():
        reads["n"] += 1
        if fails_after is not None and reads["n"] > fails_after:
            raise RuntimeError("runpodctl: connection reset by peer")
        return balance

    monkeypatch.setattr(driver.guard, "balance", read_balance)
    monkeypatch.setattr(driver.serving, "EndpointClient", lambda *a, **k: fake)
    monkeypatch.setenv("RUNPOD_API_KEY", "test-key")
    monkeypatch.setenv(driver.ENDPOINT_ENV, "ep-fake")
    fake = slow_endpoint(pin, gold_seconds_per_call=2.5)

    ledger = tmp_path / "l.json"
    if anchor is not None:
        ledger.write_text(json.dumps({driver.anchor_key(): anchor, "runs": []}), encoding="utf-8")
    return ledger


def test_a_balance_read_that_crashes_after_the_paid_legs_keeps_the_record(
    tmp_path, monkeypatch, pin
):
    """The record is the only artifact of a one-attempt session, and `spend_now` shells out to
    `runpodctl` AFTER the paid legs. A network blip, an auth expiry or a schema change there used
    to abort `main` between the last paid call and the only write — throwing away the evidence
    rather than the money. The anchor survives either way, so the spend stays recoverable."""
    ledger = ledgered(tmp_path, monkeypatch, pin, balance=10.0, fails_after=2)
    out, record = tmp_path / "d.jsonl", tmp_path / "r.json"
    code = driver.main(
        ["--leg", "text", "--out", str(out), "--record", str(record), "--ledger", str(ledger)]
    )
    assert code == 0

    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["population"]["asked"] == 30, "the paid leg finished; only the balance read died"
    assert written["cost"]["usd"] is None
    assert "connection reset" in written["cost"]["read_failed"]
    assert out.exists(), "the dump the run paid for is on disk"
    anchored = json.loads(ledger.read_text(encoding="utf-8"))
    assert driver.anchor_key() in anchored
    assert anchored["runs"][-1]["step_spent_usd"] is None
    assert "connection reset" in anchored["runs"][-1]["note"]


def test_an_explicit_project_stop_tightens_the_cap_and_never_replaces_it(
    tmp_path, monkeypatch, pin
):
    """`--project-stop-usd` used to be taken as the budget outright, so a value above what is left
    of the $0.35 cap disabled the in-run stop entirely — a flag that reads like a safety knob and
    could only ever loosen the one guard. Here $0.30 of the cap is already spent, so $0.05 is left
    and the run must refuse against THAT, not against the 9.99 on the command line."""
    ledger = ledgered(tmp_path, monkeypatch, pin, balance=10.0, anchor=10.30)
    record = tmp_path / "r.json"
    with pytest.raises(SystemExit, match="REFUSED before the first gold call"):
        driver.main(
            [
                "--leg",
                "text",
                "--project-stop-usd",
                "9.99",
                "--out",
                str(tmp_path / "d.jsonl"),
                "--record",
                str(record),
                "--ledger",
                str(ledger),
            ]
        )
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["projection"]["go_no_go"]["budget_usd"] == pytest.approx(0.05)
    assert written["projection"]["stop_at_usd"] == pytest.approx(0.05)


def test_a_refusal_that_billed_a_boot_still_lands_in_the_ledger(tmp_path, monkeypatch, pin):
    """Measured on the paid sku-b-v3 session: the (10)(a) refusal wrote its record and left the
    anchor's `runs` EMPTY, so the ledger said nothing had happened after a boot and two warm-up
    calls had been billed. The record carried the spend; the ledger is what the next session reads
    to see what is left of the cap.

    The control is the completed path, which always appended its own entry: one function, two
    callers, and the two notes say which exit wrote them."""
    ledger = ledgered(tmp_path, monkeypatch, pin, balance=10.0, anchor=10.30)
    with pytest.raises(SystemExit, match="REFUSED before the first gold call"):
        driver.main(
            [
                "--leg", "text",
                "--out", str(tmp_path / "d.jsonl"),
                "--record", str(tmp_path / "r.json"),
                "--ledger", str(ledger),
            ]
        )  # fmt: skip
    refused = json.loads(ledger.read_text(encoding="utf-8"))["runs"]
    assert len(refused) == 1
    assert refused[0]["step_spent_usd"] == pytest.approx(0.30)
    assert "REFUSED by the (10)(a) go/no-go" in refused[0]["note"]
    assert "no attempt was consumed" in refused[0]["note"]

    other = ledgered(tmp_path / "ok", monkeypatch, pin, balance=10.0)
    (tmp_path / "ok").mkdir(exist_ok=True)
    assert (
        driver.main(
            [
                "--leg",
                "text",
                "--out",
                str(tmp_path / "ok.jsonl"),
                "--record",
                str(tmp_path / "ok.json"),
                "--ledger",
                str(other),
            ]
        )  # fmt: skip
        == 0
    )
    done = json.loads(other.read_text(encoding="utf-8"))["runs"]
    assert len(done) == 1 and "sources asked" in done[0]["note"]


def test_a_half_explicit_smoke_never_writes_at_the_real_record_default(tmp_path, monkeypatch):
    """`--smoke --out X` left `--record` at its real default, because the redirect fired only when
    BOTH were defaulted. The $0 path would then plant a FAKE record at the paid run's own path —
    the artifact the real run refuses to overwrite, and the only copy of what it bought."""
    monkeypatch.setattr(driver, "REPO_ROOT", tmp_path)
    real_record = tmp_path / "results" / "sku_b_positions.json"
    monkeypatch.setattr(driver, "RECORD", real_record)
    monkeypatch.setattr(driver, "DUMP", tmp_path / "results" / "sku_b_positions.jsonl")

    # --root still points at the checkout: what is being moved is where the DEFAULTS resolve to,
    # so the test can watch the real record path without writing inside the repo
    driver.main(
        [
            "--smoke",
            "--leg",
            "text",
            "--root",
            str(REPO_ROOT),
            "--out",
            str(tmp_path / "mine.jsonl"),
        ]
    )
    assert not real_record.exists(), "a smoke wrote at the paid run's record path"
    assert (tmp_path / "results" / "smoke" / real_record.name).exists()
    assert (tmp_path / "mine.jsonl").exists(), "the explicit path is still honoured"
