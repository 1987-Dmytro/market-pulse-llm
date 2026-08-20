"""The pass-1 SFT datasets — the transport's own request, the team lead's answer, and the mask.

Three properties carry the money here. The pairs are the request the eval path sends, rebuilt from
the frozen prompt and re-parsed by the parser the pod reads replies with. The supervised span stops
at the label, so the two fields nobody labelled teach nothing — the test below computes what
training them WOULD cost against the sealed bar, because that arithmetic is the reason the mask
exists. And every row fits `config/qlora.yaml`'s frozen `max_seq_len`, bounded here at $0 instead
of discovered inside a training loop on a billed pod.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_sft as sft  # noqa: E402

from market_pulse import prompts  # noqa: E402

GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
BASE_VERDICT = json.loads((REPO_ROOT / "results" / "pass1_probe_b_verdict.json").read_text("utf-8"))


@pytest.fixture(scope="module")
def state():
    return sft.measure()


@pytest.fixture(scope="module")
def built(state):
    return sft.build(state)


def test_every_target_is_read_back_by_the_parser_the_pod_reads_replies_with(state):
    for row in state["rows"]:
        parsed = prompts.parse_pass1(row["target"], msg_id=row["msg_id"])
        assert parsed["subject_type"] == row["subject_type"]
        assert parsed["msg_id"] == row["msg_id"]
        assert parsed["subject_id"] is None and parsed["stance"] is None


def test_every_prompt_is_the_frozen_pass1_request(state):
    for row in state["rows"][:40]:
        assert row["prompt"].startswith(prompts.PASS1_COMMENT_PROMPT)
        assert row["prompt"].count("<comment ") == 1
        assert f'<comment msg_id="{row["msg_id"]}"' in row["prompt"]
        assert row["task"] == prompts.PASS1_TASK


def test_the_supervised_span_ends_at_the_label_and_never_reaches_the_unlabelled_fields(state):
    for row in state["rows"]:
        head = row["target"][: row["learn_chars"]]
        tail = row["target"][row["learn_chars"] :]
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        assert head.endswith(f"{label}{sft.SEPARATOR}"), row["id"]
        assert "subject_id" not in head and "stance" not in head
        assert tail.startswith(' "subject_id": null') and tail.endswith("}")


def test_the_boundary_runs_one_character_past_the_value_and_that_character_is_the_separator(state):
    """D3a's tightening, asserted in BOTH directions on every row.

    The mask in `scripts/train_qlora.py` is applied on token END offsets, so a boundary sitting ON
    the value lets a `",` merge end one character past it and fall out of the loss whole. One
    character further and that merge ends exactly on the boundary. The direction is checked as well
    as the value: a boundary two characters past would be inside the space before `"subject_id"`,
    and the guard that would catch it is the same `endswith` above.
    """
    for row in state["rows"]:
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        value_ends = row["target"].index(label) + len(label)
        assert row["learn_chars"] == value_ends + 1, row["id"]
        assert row["target"][value_ends] == sft.SEPARATOR, row["id"]
        assert row["target"][: row["learn_chars"] - 1].endswith(label), row["id"]


def test_training_the_unlabelled_stance_would_put_the_bar_out_of_reach():
    """Why the mask exists, computed rather than argued.

    Three of the fourteen sealed gold rows score `stance` against a NON-NULL gold value, so a
    target that taught `stance: null` would put all three out of reach whatever the model answered
    about the subject — 21629 scores stance alone, and the other two score it beside subject_type.
    14 − 3 = 11 against a threshold of 12: the gate would be unreachable before the pod was
    created. Two of the three are rows the base agrees on TODAY, which is what the arm would be
    spending them for.
    """
    scored_stance = [row for row in GOLD["per_comment"] if "stance" in row["scored_fields"]]
    assert len(scored_stance) == 3
    assert {row["msg_id"]: row["stance"] for row in scored_stance} == {
        21626: "negative",
        21629: "positive",
        580124: "negative",
    }
    assert all(row["stance"] is not None for row in scored_stance)
    agreed = {
        row["msg_id"]
        for row in BASE_VERDICT["bars"]["P1_per_comment_agreement"]["rows"]
        if row["agreed"]
    }
    assert {row["msg_id"] for row in scored_stance} & agreed == {21626, 21629}
    reachable = len(GOLD["per_comment"]) - len(scored_stance)
    assert reachable == 11 < BASE_VERDICT["bars"]["P1_per_comment_agreement"]["minimum_agreed"]


def test_no_row_can_exceed_the_frozen_max_seq_len(state):
    assert state["max_seq_len"] == 1408
    assert all(row["bound_tokens"] <= state["max_seq_len"] for row in state["rows"])
    assert all(row["bound_tokens"] > state["max_seq_len"] for row in state["dropped"])
    # branch C: with the substituted topic cut to a bought one's envelope, nothing is dropped and
    # every labelled unit trains. `dropped` stays because the ceiling has not moved — the guard is
    # what proves the bound holds, not the fact that it currently catches nothing.
    assert state["dropped"] == []
    assert len(state["rows"]) == 650


def test_a_substituted_topic_is_cut_to_the_envelope_a_bought_one_occupies(state):
    budget = state["envelope"]
    # the envelope is measured over the BOUGHT summaries, and branch B bought 99 more threads:
    # 24 verdicts -> 123, and the longest summary among them is 161 characters
    assert budget["limit"] == 161 and budget["measured_over"] == 123
    substituted = [row for row in state["rows"] if row["context"]["topic_from"].endswith("bounded")]
    bought = [row for row in state["rows"] if row["context"]["topic_from"] == "reader verdict"]
    # after branch B: 630 of the 650 topics are bought summaries and 20 are still substituted
    assert len(substituted) == 20 and len(bought) == 630
    for row in substituted:
        topic = row["prompt"].split("<topic>\n")[1].split("\n</topic>")[0]
        assert len(topic) <= budget["limit"] + 1, row["id"]  # +1 for the ellipsis
    for row in bought:
        topic = row["prompt"].split("<topic>\n")[1].split("\n</topic>")[0]
        assert not topic.endswith("…"), row["id"]  # a bought topic is never cut


def test_the_cut_marks_itself_and_keeps_whole_words():
    limit = 20
    assert sft.bound_topic("short enough", limit) == "short enough"
    assert sft.bound_topic("a sentence that runs well past the budget", limit) == "a sentence that…"
    # a single unbroken token is cut hard rather than thrown away
    assert sft.bound_topic("x" * 60, limit) == "x" * 20 + "…"
    assert sft.bound_topic("", limit) == ""


def test_the_bound_is_the_worst_ratio_probe_b_measured_not_the_mean(state):
    per = state["ratio"]
    assert per["rows"] == 64
    assert 0.29 < per["tokens_per_char_max"] < 0.30
    assert "maximum" in per["rule"]
    # and it really is the maximum of the file, re-derived here off the same two records
    pack = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
    chars = {one["id"]: int(one["rendered_chars"]) for one in pack["items"]}
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    ]
    worst = max(int(row["usage"]["prompt_tokens"]) / chars[row["id"]] for row in rows)
    assert round(worst, 6) == per["tokens_per_char_max"]


def test_arm_a_is_a_subset_of_arm_b_and_that_is_the_whole_ablation(state):
    a = {row["id"] for row in sft.arm_rows(state, "a")}
    b = {row["id"] for row in sft.arm_rows(state, "b")}
    assert a < b
    assert (len(a), len(b)) == (500, 650)  # every labelled unit of each pack
    assert {row["pack"] for row in sft.arm_rows(state, "a")} == {"r1"}
    assert {row["pack"] for row in sft.arm_rows(state, "b")} == {"r1", "r2"}


def test_no_gold_row_and_no_exam_thread_is_trained_on(state):
    gold = {int(row["msg_id"]) for row in GOLD["per_comment"]}
    r1 = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))
    exam = set(r1["exclusion"]["threads"])
    everything = state["rows"] + state["dropped"]
    assert [row for row in everything if row["msg_id"] in gold] == []
    assert [row for row in everything if row["thread"] in exam] == []


def test_the_sampler_weights_are_the_pre_registered_formula(state):
    """One implementation: the builder publishes what the trainer will sample with."""
    import train_qlora

    for arm in ("a", "b"):
        rows = sft.arm_rows(state, arm)
        assert sft.sampler_weights(rows) == train_qlora.class_weights(rows)
        weights = sft.sampler_weights(rows)
        assert weights["молочный_бренд"] == 8.0  # the cap bites on the two rows of the class
        assert all(0 < value <= 8.0 for value in weights.values())
        total = len(rows)
        counts = {name: n for name, n in sft.distribution(rows).items() if n}
        for name, n in counts.items():
            assert weights[name] == round(min(total / (5 * n), 8.0), 6)


def test_the_record_names_the_context_the_gate_carries_and_the_training_set_does_not(built):
    """The finding this record exists to publish, asserted so it cannot quietly stop being true."""
    record, _ = built
    gate = record["census"]["the_gate_s_own_rows"]
    arm_b = record["census"]["arms"]["b"]["context"]
    assert gate["n"] == 14 and gate["with_an_entity_block"] == 12
    assert record["census"]["eval_pack"]["with_an_entity_block"] == 55
    # branch B was bought and executed: 39 of 650 rows carried a block before it, 282 after — the
    # projection said ~279 and it was right to within 1%. The gate's own rows sit at 12 of 14, so
    # what is left is the structural half: a verdict resolves entities only where the thread HAS
    # them, and recipe and marketplace threads name nobody
    assert (arm_b["with_an_entity_block"], arm_b["of"]) == (282, 650)
    assert 0.40 < arm_b["with_an_entity_block"] / arm_b["of"] < 0.45
    # and the branch-C cut all but disappeared with it: 630 bought topics, 6 still shortened
    assert arm_b["with_a_bought_topic"] == 630
    assert arm_b["with_a_topic_the_cut_shortened"] == 6
    assert "leaves the entity-block one open" in record["census"]["topic_rule"]
    assert record["length"]["topic_envelope"]["limit"] == 161


def test_the_record_names_which_reader_files_supplied_the_context(built):
    """A rendering that reads an optional input has to say whether it was there.

    The branch-B top-up file is read when it exists; until it does, the row for it says so with a
    null digest and zero threads. Traceability of the rendering to its sources, not a clock: the
    producer renders either way, and what it renders when the file is absent is the state the
    census block already publishes.
    """
    record, _ = built
    sources = {one["record"]: one for one in record["context_sources"]}
    assert set(sources) == {
        "results/reader_v5b_w1.jsonl",
        "results/reader_topup_w1.jsonl",
        "results/reader_v4_w1.jsonl",
    }
    # v5b 21 · the branch-B top-up 99 · v4 3 — the middle row IS the buy
    assert sum(one["threads_it_supplied"] for one in sources.values()) == 123
    assert sources["results/reader_topup_w1.jsonl"]["threads_it_supplied"] == 99
    for one in sources.values():
        assert one["exists"] is ((REPO_ROOT / one["record"]).exists())
        assert (one["sha256"] is None) is not one["exists"]
    assert sft.TOPUP.name == "reader_topup_w1.jsonl"


def test_the_datasets_rebuild_byte_identical(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert sft.main(["--outdir", str(first)]) == 0
    assert sft.main(["--outdir", str(second)]) == 0
    for name in (*sft.ARM_NAMES.values(), sft.RECORD_NAME):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert str(tmp_path) not in (first / sft.RECORD_NAME).read_text("utf-8")


def shipped_at(record: dict, dotted: str):
    """One dotted path out of a record — the shipped value a rebuilt pin is compared against."""
    for name in dotted.split("."):
        record = record[name]
    return record


def moved_paths(old, new, where=""):
    """Every leaf path at which two records differ, as dotted names."""
    if isinstance(old, dict) and isinstance(new, dict):
        for name in sorted(set(old) | set(new)):
            yield from moved_paths(
                old.get(name), new.get(name), f"{where}.{name}" if where else name
            )
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for index, (one, two) in enumerate(zip(old, new)):
            yield from moved_paths(one, two, f"{where}[{index}]")
    elif old != new:
        yield where


def test_the_shipped_datasets_are_what_the_producer_builds_today(tmp_path):
    """The SEALED bytes — both arms and the smoke pack — rebuild identically. Those are the
    artefacts `results/prereg_lora_b.json` freezes and `results/lora_b_verdict.json` scored."""
    assert sft.main(["--outdir", str(tmp_path)]) == 0
    for name in (*sft.ARM_NAMES.values(), sft.SMOKE_NAME):
        assert (tmp_path / name).read_bytes() == (REPO_ROOT / name).read_bytes(), name


def test_the_record_moves_only_where_it_quotes_a_file_that_moved(tmp_path):
    """The enumerated diff, asserted in BOTH directions.

    `results/pass1_sft.json` is not regenerated — two sealed records pin it — so what a rebuild
    would write has to be checked against it by name. Every path that moves is a pin of a file that
    moved (`prompts.py` grew the v2 prompt, this producer grew the holdout refusal) or the holdout
    block that refusal publishes; and every moved pin equals the LIVE sha of what it pins, so a
    «moved since» cannot hide a wrong value ([[the_checksum_field_the_join_forces]]).
    """
    assert sft.main(["--outdir", str(tmp_path)]) == 0
    shipped = json.loads((REPO_ROOT / sft.RECORD_NAME).read_text("utf-8"))
    rebuilt = json.loads((tmp_path / sft.RECORD_NAME).read_text("utf-8"))

    def live(path):
        return subprocess.run(
            ["shasum", "-a", "256", path], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.split()[0]

    # the expected set is DERIVED from which pinned file has actually moved, never typed: a list of
    # three names would be right at the commit that wrote it and wrong at the one before it
    pins = {
        "instruments.parser.sha256": (
            "src/market_pulse/prompts.py",
            rebuilt["instruments"]["parser"],
        ),
        "producer.sha256": ("scripts/build_pass1_sft.py", rebuilt["producer"]),
    }
    expect = {"holdout"} | {
        name for name, (path, block) in pins.items() if block["sha256"] != shipped_at(shipped, name)
    }
    assert set(moved_paths(shipped, rebuilt)) == expect, sorted(moved_paths(shipped, rebuilt))
    for name, (path, block) in pins.items():
        assert block["sha256"] == live(path), name
    # and the other direction: everything the record pins that did NOT move still matches
    assert rebuilt["datasets"] == shipped["datasets"]
    assert rebuilt["smoke"]["sha256"] == shipped["smoke"]["sha256"]


def test_a_holdout_row_in_a_new_arm_is_REFUSED_and_the_sealed_arms_are_not(state, built):
    """Both directions of D0.1's rule, on the one producer that can break it.

    The sealed arms are exempt because they rebuild to the shas `results/pass1_sft.json` pins — the
    positive control, and it is what the test above already proved byte for byte. A new arm is not,
    and the negative control is that the SAME rows refuse under a name the record does not pin.
    """
    _, files = built
    sealed = sft.sealed_arm_shas()
    holdout = sft.holdout_units()
    assert len(holdout) == 100
    rows = sft.arm_rows(state, "b")
    assert any((row["thread"], int(row["msg_id"])) in holdout for row in rows), (
        "arm B is the 650 labels the holdout was drawn from — an empty intersection would make the"
        " refusal below unreachable and this test vacuous"
    )
    # positive control: the sealed arm, at its pinned bytes, is carried past the rule
    assert sft.assert_no_holdout("b", rows, sft.sha_text(files["b"]), sealed) == (
        "sealed-before-the-holdout"
    )
    # the rule: the same rows under an arm nothing pins
    with pytest.raises(SystemExit, match="EVALUATION ONLY"):
        sft.assert_no_holdout("c", rows, sft.sha_text(files["b"]), sealed)
    # and a sealed name whose bytes have moved loses the exemption with them
    with pytest.raises(SystemExit, match="EVALUATION ONLY"):
        sft.assert_no_holdout("b", rows, "0" * 64, sealed)
    # a future arm drawn WITHOUT the holdout builds
    clean = [row for row in rows if (row["thread"], int(row["msg_id"])) not in holdout]
    assert len(clean) == len(rows) - 100
    assert sft.assert_no_holdout("c", clean, "0" * 64, sealed) == "checked-and-clear"


def test_the_census_run_writes_nothing(capsys):
    before = sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
    assert sft.main(["--census"]) == 0
    after = sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
    assert after == before
    out = capsys.readouterr().out
    assert "DROPPED FOR LENGTH" in out and "wrote" not in out


def test_the_producer_pins_itself(tmp_path):
    """On the record a rebuild WRITES, not on the shipped one.

    The shipped `results/pass1_sft.json` is sealed — two records of line B pin its bytes — and this
    contract edited the producer to add the holdout refusal, so its pin there is a «moved since»
    like every other pin of a file that has been extended. What has to stay true is the property:
    the record this producer writes names it and hashes it ([[provenance_cannot_name_itself]])."""
    assert sft.main(["--outdir", str(tmp_path)]) == 0
    record = json.loads((tmp_path / sft.RECORD_NAME).read_text("utf-8"))
    live = subprocess.run(
        ["shasum", "-a", "256", "scripts/build_pass1_sft.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()[0]
    assert record["producer"]["sha256"] == live
    assert record["producer"]["script"] == "scripts/build_pass1_sft.py"
    shipped = json.loads((REPO_ROOT / sft.RECORD_NAME).read_text("utf-8"))
    assert shipped["producer"]["script"] == record["producer"]["script"]
