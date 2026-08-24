"""`docs/PROMPT-lora-c-armb.md` — the stamped verifier, arm B's dataset, and the re-derived money.

Everything here is $0. The heavy readings — the encode census over 666 rows and the rendering of
the 160 synthetic queries — are bought once by the producers and asserted here from their result
files; a test that re-rendered them would be a second answer the day one of them moved.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_stamped  # noqa: E402

ARM_B_RECORD = REPO_ROOT / "results" / "lora_c_arm_b.json"
ARM_B_FILE = REPO_ROOT / "results" / "pass1_sft_v3_arm_b.jsonl"
TRAIN_FILE = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
CENSUS = REPO_ROOT / "results" / "lora_c_encode_census_arm_b.json"
REGISTRATION = REPO_ROOT / "results" / "prereg_lora_c.json"


def record() -> dict:
    return json.loads(ARM_B_RECORD.read_text(encoding="utf-8"))


def registration() -> dict:
    return json.loads(REGISTRATION.read_text(encoding="utf-8"))


# --- step 0.5: the moving-tree verifier as an instrument -----------------------------------------


def test_the_whitelisted_directory_is_read_by_no_test():
    """The check that licenses the whitelist, RUN rather than written down beside it.

    `scripts/check_stamped.py` lets `knowledge/daily_logs/` move under a suite because no test opens
    it. That is an assertion about a directory that grows every week, so it is measured here
    ([[a_claim_no_number_can_check]]). A plain grep cannot do it — this file names the directory in
    its own prose — so every test module is parsed and only string constants that are NOT docstrings
    are counted: a path literal is caught, a sentence is not.

    What counts as reading it is a CALL that carries the name — `open(...)`, `Path(...)`,
    `subprocess.run([... ])` — and not a string that merely spells it: the test below this one uses
    day-log paths as porcelain fixtures, which is naming the directory, not opening it.

    Its ceiling, named rather than hidden: a test that assembled the path from parts, or bound it to
    a name first, would evade this exactly as it would evade a grep. What it does catch is the way
    anyone actually writes it.

    The two files in the repo that DO read the directory — `scripts/refresh-hot-cache.py` and
    `scripts/brain-session-end.py` — are hooks, and the second half of this test is that no test
    drives either of them. That is the caveat `check_stamped.py` carries: the whitelist licenses the
    hook outputs appearing, never a cache refresh mid-run.

    `knowledge/index.md` joined the whitelist on 2026-08-24 by ruling (о), which licensed it on THIS
    criterion — so the criterion runs over it too. It is scanned by its full path: a bare
    `index.md` would match half the repo and would fail on a name that has nothing to do with the
    vault ([[the_subject_of_a_query_never_names_itself]]).
    """
    import ast

    # Spelled in halves so this file's own assertions are not what the scan finds.
    needles = (
        "daily" + "_logs",
        "refresh-hot" + "-cache",
        "brain-session" + "-end",
        "knowledge/" + "index.md",
    )
    for path in sorted((REPO_ROOT / "tests").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        }
        opened = [
            inner.value
            for call in ast.walk(tree)
            if isinstance(call, ast.Call)
            for inner in ast.walk(call)
            if isinstance(inner, ast.Constant)
            and isinstance(inner.value, str)
            and any(needle in inner.value for needle in needles)
            and id(inner) not in docstrings
        ]
        assert opened == [], (
            f"{path.name} passes {opened} to a call — the whitelisted directory, or a hook that"
            " reads it and writes hot.md, is now a suite input and may not move under a reading"
        )


def test_the_stamped_verifier_voids_a_reading_when_a_suite_input_moves():
    """Both Stop-hook outputs pass and `hot.md` is refused — both directions, one assertion each.

    `knowledge/hot.md` is the case the instrument exists for: `scripts/volume_calc_5c1.py` greps a
    price literal out of it and nine tests read the result, so a mid-run edit there is exactly the
    move that voided Dv785 and Dv792 ([[while_a_verifier_runs_the_repo_is_read_only]]).

    `knowledge/index.md` is the case Dv802 found: the SAME hook regenerates it whenever a vault file
    is added, so a session that adds an ADR gets a VOID over a green suite. Ruling (о) widened the
    whitelist to it on the registered criterion, tested above. The two names are one line apart in
    the same directory and land on opposite sides of the list, which is why this asserts each
    direction rather than «the whitelist works».
    """
    before = [" M docs/STATUS.md"]
    day_log_appeared = before + ["?? knowledge/daily_logs/2026-08-24.md"]
    day_log_changed = before + [" M knowledge/daily_logs/2026-08-24.md"]
    index_changed = before + [" M knowledge/index.md"]
    hot_changed = before + [" M knowledge/hot.md"]
    both_hooks = before + [" M knowledge/index.md", "?? knowledge/daily_logs/2026-08-24.md"]

    assert check_stamped.moved(before, day_log_appeared) == []
    assert check_stamped.moved(before, day_log_changed) == []
    assert check_stamped.moved(before, index_changed) == []
    assert check_stamped.moved(before, both_hooks) == []
    assert check_stamped.moved(before, hot_changed) == [" M knowledge/hot.md"]
    assert check_stamped.moved(before, hot_changed + index_changed[1:]) == [" M knowledge/hot.md"]
    assert check_stamped.moved(before, before) == []
    assert check_stamped.moved(day_log_appeared, before) == [], "a line DISAPPEARING is also a move"
    assert check_stamped.moved(index_changed, before) == [], "and so is the index line disappearing"


def test_the_stamped_verifier_reports_the_suites_own_exit_code():
    """Driven end to end on a trivial command, both directions.

    The instrument is worth nothing if it swallows a red suite, so it is run for real — twice, on
    `true` and on `false` — rather than reasoned about ([[guard_selftest_negative_control]]). The
    tree does not move under either, so both readings HOLD and the exit code is the command's own.
    """
    assert check_stamped.main(["true"]) == 0
    assert check_stamped.main(["false"]) == 1


def test_the_stamped_verifier_parses_a_rename_and_a_quoted_path():
    """`path_of` reads the porcelain line's TARGET, which is what a whitelist is about."""
    lines = {
        " M knowledge/hot.md": "knowledge/hot.md",
        "?? knowledge/daily_logs/2026-08-24.md": "knowledge/daily_logs/2026-08-24.md",
        'R  a.md -> "knowledge/hot.md"': "knowledge/hot.md",
    }
    for line, want in lines.items():
        assert check_stamped.path_of(line) == want


# --- D1: arm B's dataset ------------------------------------------------------------------------


def test_the_arm_b_file_opens_with_the_506_real_rows_byte_for_byte():
    """The prefix claim, checked on the BYTES of both shipped files.

    Not on a count and not on a hash of ids: «byte-identical prefix» is a statement about the file
    on disk, and the only way to check it is to slice it ([[reproducible_means_try_it]]).
    """
    shipped = TRAIN_FILE.read_bytes()
    arm_b = ARM_B_FILE.read_bytes()
    assert arm_b.startswith(shipped)
    assert len(shipped.splitlines()) == 506
    assert len(arm_b.splitlines()) == 666
    assert record()["rows"]["arithmetic"] == "506 + 160 = 666"


def test_the_producer_refuses_a_prefix_that_drifted():
    """The STOP the contract asks for, driven in both directions on the comparison itself."""
    import build_lora_c_data as data

    rebuilt = "a\nb\n"
    data.refuse_a_drifted_prefix(rebuilt.encode("utf-8"), rebuilt, TRAIN_FILE)
    data.refuse_a_drifted_prefix(None, rebuilt, TRAIN_FILE)
    with pytest.raises(SystemExit, match="first differing at line 2"):
        data.refuse_a_drifted_prefix(b"a\nX\n", rebuilt, TRAIN_FILE)


def test_every_synthetic_row_is_provenance_tagged_and_no_real_row_is():
    """`synthetic: true` and the error class ride on the 160 and on nothing else.

    A provenance key on a real row would move the prefix's bytes, and the prefix is what the whole
    ablation rests on — arm A's rows are a SUBSET of arm B's, so the one variable is the top-up.
    """
    rows = [
        json.loads(line) for line in ARM_B_FILE.read_text(encoding="utf-8").splitlines() if line
    ]
    real, synthetic = rows[:506], rows[506:]
    assert all("synthetic" not in row for row in real)
    assert all(row["synthetic"] is True and row["error_class"] for row in synthetic)
    assert all(row["thread"].startswith("synthetic:") for row in synthetic)
    assert sorted({row["error_class"] for row in synthetic}) == [
        "brand_vs_retailer",
        "mention_vs_about",
        "non_dairy_brand",
        "retailer_non_dairy",
    ]


def test_the_arm_b_class_weights_are_five_and_the_dairy_brand_weight_is_its_own_arithmetic():
    """FIVE classes, and 4.1625 re-derived from the counts rather than compared to a literal."""
    import train_qlora as trainer

    rows = [
        json.loads(line) for line in ARM_B_FILE.read_text(encoding="utf-8").splitlines() if line
    ]
    weights = trainer.class_weights([{"subject_type": row["subject_type"]} for row in rows])
    dairy = [row for row in rows if row["subject_type"] == "молочный_бренд"]
    assert len(weights) == 5
    assert weights["молочный_бренд"] == round(len(rows) / (trainer.PASS1_K * len(dairy)), 6)
    assert record()["class_weights"]["arm_b"] == weights
    assert record()["class_weights"]["молочный_бренд"] == weights["молочный_бренд"]
    assert all(row["synthetic"] is True for row in dairy), (
        "every молочный_бренд target in this line is synthetic — arm A has none, and that is what"
        " makes the header tell below a confound and not a footnote"
    )


def test_no_synthetic_row_is_ever_an_example_and_every_example_is_a_pool_row():
    """Isolation rows 1, 2 and 4 — read off the record as the counts the producer measured."""
    isolation = record()["isolation"]
    assert isolation["1_every_example_of_the_160_is_a_pool_row"]["outside_the_pool"] == []
    assert isolation["1_every_example_of_the_160_is_a_pool_row"]["examples"] == 160 * 5
    assert isolation["2_no_synthetic_row_is_an_example_anywhere"]["checked_over_rows"] == 666
    assert (
        isolation["2_no_synthetic_row_is_an_example_anywhere"]["synthetic_ids_used_as_examples"]
        == []
    )
    assert isolation["3_no_example_text_equals_its_query"]["equal_pairs"] == []
    assert isolation["4_synthetic_meets_no_eval_set"]["eval_E"] == []
    assert isolation["4_synthetic_meets_no_eval_set"]["holdout_100"] == []
    assert isolation["4_synthetic_meets_no_eval_set"]["gold_14"] == []


def test_the_header_tell_is_measured_and_the_record_names_what_it_found():
    """The fifth isolation row: which header lines are in all 160 prompts and in none of the 506.

    The assertion is that the measurement EXISTS and is consistent, not that it came back clean —
    it did not, and a test written to pass on a clean answer would have to be edited the day the
    finding landed ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
    """
    tell = record()["isolation"]["5_the_header_tell"]
    assert tell["real_rows"] == 506
    assert tell["synthetic_rows"] == 160
    counted = {
        cell["line"]: cell["real_rows_carrying_it"] for cell in tell["header_lines_of_the_160"]
    }
    assert counted, "the 160 synthetic headers share no line at all — the measurement is broken"
    assert tell["tells"] == [line for line, seen in counted.items() if seen == 0]
    rows = [
        json.loads(line) for line in ARM_B_FILE.read_text(encoding="utf-8").splitlines() if line
    ]
    for line in tell["tells"]:
        assert not any(line in row["prompt"] for row in rows[:506])
    marked = {
        row["id"] for row in rows[506:] if any(line in row["prompt"] for line in tell["tells"])
    }
    assert len(marked) == tell["synthetic_rows_marked_by_at_least_one_tell"]

    slots = record()["isolation"]["6_the_example_slots"]
    assert slots["real_506"]["молочный_бренд"] == slots["synthetic_160"]["молочный_бренд"] == 1, (
        "the pool holds one молочный_бренд row, so that example slot is the SAME row for every"
        " query in this line — the examples block is not where the tell is"
    )


def test_the_encode_census_covers_all_666_and_refuses_none():
    """Census 1, from the file `train_qlora_v3.py --census` wrote."""
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    assert census["rows"] == 666
    assert census["encoded"] == 666
    assert census["refused"] == []
    assert census["max_seq_len"] == 3072
    assert census["headroom"] == census["max_seq_len"] - census["tokens"]["max"]
    assert census["sha256"] == hashlib.sha256(ARM_B_FILE.read_bytes()).hexdigest()
    assert census["file"] == "results/pass1_sft_v3_arm_b.jsonl"


def test_the_widest_arm_b_request_is_inside_the_input_ceiling():
    """Census 4 — the char ceiling, which is a different instrument from the token one."""
    from market_pulse import prompts

    length = record()["length"]
    assert length["ceiling_chars"] == prompts.PASS1_MAX_INPUT_CHARS
    assert length["headroom_chars"] == length["ceiling_chars"] - length["widest_request_chars"]
    assert length["synthetic_headroom_chars"] > 0


# --- D2: the registration and the re-derived money block -----------------------------------------


def test_the_registration_names_both_training_files_with_their_shas():
    """The gap `test_the_registration_names_no_arm_b_dataset` pinned (Dv786) is closed by a FILE.

    That test's name is cited by `docs/reports/lora-c-run.md`; it is superseded by this one and by
    `test_the_registration_now_names_arm_bs_dataset` in `tests/test_lora_c_run.py`, which keeps the
    old finding greppable rather than deleting the trail.
    """
    train = registration()["population"]["train"]
    files = {one["file"]: one for one in train["files"]}
    assert set(files) == {
        "results/pass1_sft_v3_train.jsonl",
        "results/pass1_sft_v3_arm_b.jsonl",
    }
    for name, cell in files.items():
        on_disk = hashlib.sha256((REPO_ROOT / name).read_bytes()).hexdigest()
        assert cell["sha256"] == on_disk, f"{name} has moved under its registration"
    assert files["results/pass1_sft_v3_train.jsonl"]["rows"] == 506
    assert files["results/pass1_sft_v3_arm_b.jsonl"]["rows"] == 666
    legs = registration()["legs"]
    assert legs["arm_a"]["train_file"] == "results/pass1_sft_v3_train.jsonl"
    assert legs["arm_b"]["train_file"] == "results/pass1_sft_v3_arm_b.jsonl"
    assert legs["arm_b"]["train_rows"] == 666
    assert "results/pass1_sft_v3_arm_b.jsonl" in registration()["frozen_when_the_pod_exists"]


def test_the_sibling_trainer_reads_both_shas_and_refuses_to_guess_which_arm_to_census():
    """Two registered datasets make «the first one» a silent arm pick, so it is a refusal instead."""
    import train_qlora_v3 as sibling

    shas = sibling.registered_training_shas()
    assert len(shas) == 2
    assert sibling.arm_of(506) == "arm_a"
    assert sibling.arm_of(666) == "arm_b"
    with pytest.raises(SystemExit, match="--data"):
        sibling.registered_first()


def test_the_pass_2_leg_count_is_two_and_the_record_quotes_the_ruling_that_made_it_so():
    """Ruling (н), grepped back into `docs/STATUS.md` by the producer's own `quoted`."""
    import write_lora_c_prereg as prereg

    money = registration()["money"]["pre_pod_arithmetic"]
    ruled = money["the_pass_2_leg_count_was_ruled"]
    assert ruled["now"] == 2
    assert ruled["ruling"] == prereg.RULING_N_PASS_2
    assert prereg.quoted(prereg.RULING_N_PASS_2) == prereg.RULING_N_PASS_2
    threads = registration()["ready_to_price"]["pass_2_threads_per_leg"]
    assert money["fixed_seconds"]["pass_2"] == 2 * threads * prereg.PASS_2_SECONDS_PER_THREAD
    assert ruled["saved_seconds"] == 2 * threads * prereg.PASS_2_SECONDS_PER_THREAD


def test_the_break_even_is_the_cap_inequality_solved_backwards_at_both_prices():
    """Every cell of the two-price table re-derived from the record's own fixed part."""
    money = registration()["money"]["pre_pod_arithmetic"]
    cap = registration()["money"]["cap_usd_all_in"]
    fixed = money["fixed_seconds"]
    steps = money["steps"]["total"]
    assert fixed["total"] == round(sum(v for k, v in fixed.items() if k != "total"), 2)
    assert steps == money["steps"]["arm_a"] + money["steps"]["arm_b"] == 144
    for price, cell in money["at_each_price"].items():
        budget = cap / float(price) * 3600
        assert cell["budget_seconds"] == round(budget, 2) or cell["budget_seconds"] == round(
            budget, 1
        )
        assert cell["left_for_training_seconds"] == round(budget - fixed["total"], 1)
        assert cell["break_even_seconds_per_step"] == round((budget - fixed["total"]) / steps, 2)
    assert money["rates_used"]["training_seconds_per_step"].startswith("NONE")


def test_the_two_columns_price_the_smoke_the_same_way():
    """One accounting for one quantity — lora-c-run's version divided by 144 and by 144 + 6."""
    money = registration()["money"]["pre_pod_arithmetic"]
    steps = money["steps"]["total"]
    scenario = money["what_the_projection_rung_would_see"]
    fixed = scenario["fixed_seconds_at_sibling_rates"]
    cap = registration()["money"]["cap_usd_all_in"]
    for price, value in scenario["break_even_seconds_per_step"].items():
        assert value == round((cap / float(price) * 3600 - fixed) / steps, 2)
    assert money["fixed_seconds"]["training_smoke"] > 0
    assert scenario["one_accounting_for_the_smoke"]


def test_the_registration_is_still_a_draft_with_its_attempt_unspent_and_no_price():
    """What this contract may NOT move: the state, the bars, the attempt, and any price key."""
    record_now = registration()
    assert record_now["state"].startswith("DRAFT")
    assert record_now["bars"]["attempt"].startswith("ONE.")
    assert record_now["money"]["cap_usd_all_in"] == 4.00
    assert isinstance(record_now["money"]["hard_stop_seconds"], str)
    assert "spent" not in record_now["money"]
    assert "price_usd" not in record_now["money"]


def test_the_stock_probe_is_a_listing_and_creates_nothing():
    """The probe's own record: a reading with a timestamp, and the caveat that dates it."""
    probe = json.loads(
        (REPO_ROOT / "results" / "lora_c_stock_probe.json").read_text(encoding="utf-8")
    )
    assert probe["region"] == "EU-RO-1"
    assert probe["read_at"].endswith("+00:00")
    assert all(command.startswith("runpodctl") for command in probe["commands"])
    assert not any(
        word in " ".join(probe["commands"]) for word in ("create", "start", "stop", "remove")
    )
    assert probe["caveat"]
    in_region = registration()["money"]["pre_pod_arithmetic"]["stock_probe"][
        "in_the_volumes_region"
    ]
    assert in_region, "the probe read no card at all in the volume's region — that is a finding"
