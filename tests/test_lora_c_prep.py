"""`lora-c-prep`: the v3 prompt, the shared pool, the rationales, the packs and the two STOPs.

Every guard here is driven in BOTH directions — the clean state passes and a PLANTED violation is
refused. A guard tested only on data that satisfies it is a guard nobody has seen fire
([[guard_selftest_negative_control]]), and three of the ones below (the holdout exclusion, the
synthetic isolation, the balance rule) exist precisely to stop a mistake that would otherwise go
green all the way to a billed pod.

The fixtures BUILD what they check rather than reading the shipped artifact where the artifact is
something a later step rewrites — pass2-signals-r2 lost seventeen tests to a fixture that copied a
file which grows during the run ([[a_test_that_reads_a_shipped_artifact]]).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_lora_c_data as data  # noqa: E402
import build_lora_c_eval_pack as evalpack  # noqa: E402
import build_lora_c_pass2_pack as p2pack  # noqa: E402
import build_lora_c_synthetic as syn  # noqa: E402
import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import train_qlora as trainer  # noqa: E402
import write_lora_c_prereg as prereg  # noqa: E402
from market_pulse import pass1_v3, prompts  # noqa: E402

TRAIN = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
RATIONALES = REPO_ROOT / "results" / "rationales_pass1_v1.jsonl"
SYNTHETIC = REPO_ROOT / "results" / "synthetic_pass1_v1.jsonl"
EVAL_PACK = REPO_ROOT / "results" / "lora_c_eval_pack.json"
DATA_RECORD = REPO_ROOT / "results" / "lora_c_data.json"
PREREG = REPO_ROOT / "results" / "prereg_lora_c.json"
SAMPLE_1 = REPO_ROOT / "docs" / "reviews" / "lora-c-rationales-sample.md"
SAMPLE_2 = REPO_ROOT / "docs" / "reviews" / "lora-c-synthetic.md"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(DATA_RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def train_rows() -> list[dict]:
    return jsonl(TRAIN)


@pytest.fixture(scope="module")
def pack() -> dict:
    return json.loads(EVAL_PACK.read_text(encoding="utf-8"))


# --- the prompt ----------------------------------------------------------------------------------


def test_v3_is_a_strict_prefix_extension_of_v2():
    """v3 = v2's bytes + one paragraph, and NOT the other way round.

    Both directions: v2 is a prefix of v3, and v3 is not a prefix of v2. The one-sided assertion
    would pass if the two strings were equal, which is the state that makes the base-v3 column
    meaningless.
    """
    assert pass1_v3.PASS1_COMMENT_PROMPT_V3.startswith(prompts.PASS1_COMMENT_PROMPT_V2)
    assert not prompts.PASS1_COMMENT_PROMPT_V2.startswith(pass1_v3.PASS1_COMMENT_PROMPT_V3)
    added = pass1_v3.PASS1_COMMENT_PROMPT_V3[len(prompts.PASS1_COMMENT_PROMPT_V2) :]
    assert added.strip() == pass1_v3.PASS1_RATIONALE_CLAUSE_V3


def test_v3_carries_no_gold_row():
    """No gold msg_id, thread or answer in the prompt text — v1 and v2 are asserted the same way."""
    gold = json.loads(
        (REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8")
    )
    text = pass1_v3.PASS1_COMMENT_PROMPT_V3
    for key in ("flagships", "entity_cases", "noise_threads"):
        for case in gold[key]:
            assert str(case["post_id"]) not in text
            assert case["channel"] not in text


def test_rendered_item_cannot_take_v3_and_that_is_why_the_sibling_exists():
    """The contract's own question, answered by DRIVING the shipped renderer at v3.

    `build_pass1_fewshot_packs.rendered_item` dispatches straight into `prompts.pass1_messages_gm4`,
    which refuses any task outside `prompts.PASS1`. That refusal is the whole justification for
    `src/market_pulse/pass1_v3.py` being a second module, so it is a test and not a paragraph.
    """
    fields = {
        "channel": "@x",
        "post_id": 1,
        "topic": "тема",
        "entities": [],
        "msg_id": 7,
        "text": "текст",
    }
    with pytest.raises(ValueError, match="not a registered pass-1 prompt"):
        fewshot.rendered_item(fields, pass1_v3.PASS1_TASK_V3, [])
    assert pass1_v3.PASS1_TASK_V3 not in prompts.PROMPTS


# --- the parser: the rationale can never refuse ---------------------------------------------------


@pytest.mark.parametrize(
    "reply, state",
    [
        ('{"rationale": "коментар ПРО сир (cue: «сир»)", %s}', "read"),
        ('{"rationale": "", %s}', "empty"),
        ('{"rationale": null, %s}', "not_a_string"),
        ('{"rationale": 17, %s}', "not_a_string"),
        ("{%s}", "omitted"),
        ('{"rationale": "' + "я" * 200 + '", %s}', "over_length"),
    ],
)
def test_the_rationale_can_never_refuse_a_reply(reply, state):
    """Six states of the report-only field, and not one of them costs the row its label.

    This is pass2-r2's rule applied BEFORE the money instead of after it: `prompts._text` would
    refuse three of these six, and a field the record calls report-only must not be able to refuse
    a whole answer ([[a_report_only_field_can_refuse_the_whole_row]]).
    """
    tail = '"msg_id": 7, "subject_type": "молочный_бренд", "subject_id": "Рудь", "stance": null'
    row = pass1_v3.parse_pass1_v3(reply % tail, msg_id=7)
    assert row["subject_type"] == "молочный_бренд"
    assert row["subject_id"] == "Рудь"
    assert row["rationale_state"] == state


def test_the_scored_fields_are_still_strict():
    """The wrapper relaxes the fifth field and NOTHING else — the negative control for the above."""
    tail = '"msg_id": 7, "subject_id": null, "stance": null'
    with pytest.raises(prompts.ParseError, match="outside its domain"):
        pass1_v3.parse_pass1_v3('{"rationale": "x", "subject_type": "кефир", %s}' % tail, msg_id=7)
    with pytest.raises(prompts.ParseError, match="msg_id echoes"):
        pass1_v3.parse_pass1_v3(
            '{"rationale": "x", "msg_id": 9, "subject_type": null, "subject_id": null,'
            ' "stance": null}',
            msg_id=7,
        )


# --- the pool and the training set ----------------------------------------------------------------


def test_the_pool_holds_no_holdout_row_and_no_reference_thread_row():
    pool, census = data.shared_pool()
    holdout = sft.holdout_units()
    reference = set(data.reference_threads())
    assert len(reference) == 16
    assert not [one for one in pool if (one["thread"], one["msg_id"]) in holdout]
    assert not [one for one in pool if one["thread"] in reference]
    assert census["pool"] == len(pool)
    left, right = census["arithmetic"].split("=")
    assert int(right.split("—")[0]) == len(pool)
    assert eval(left.replace("−", "-")) == len(pool)  # noqa: S307 — the record's own arithmetic


def test_a_planted_holdout_row_is_refused(monkeypatch):
    """The negative control: shrink the holdout by one row and the pool GROWS by that row.

    A membership guard that is only ever run on a compliant set proves nothing about the day the
    set stops complying. Driven by moving the holdout rather than the pool, because the pool is
    derived and the holdout is the input the rule keys on.
    """
    pool, _ = data.shared_pool()
    holdout = sft.holdout_units()
    reference = set(data.reference_threads())
    victim = next(key for key in sorted(holdout) if key[0] not in reference)
    monkeypatch.setattr(sft, "holdout_units", lambda: holdout - {victim})
    widened, _ = data.shared_pool()
    assert len(widened) == len(pool) + 1
    assert victim in {(one["thread"], one["msg_id"]) for one in widened}


def test_the_holdout_exclusion_is_keyed_on_the_PAIR_and_not_the_msg_id(monkeypatch):
    """The discriminating victim: a holdout row whose msg_id ALSO lives on a pool row elsewhere.

    The test above proves the pool is a function of the holdout and would pass on a mutant that
    excluded by `msg_id` alone. `@klopotenkofood:6040#21239` is a holdout row and `21239` is also
    the id of a pool row in `@VARUS_channel:10470`, so releasing it must add ONE row and leave the
    sibling standing. Under a msg_id-keyed exclusion the sibling would never have been in the pool
    at all ([[select_one_row_refuse_ambiguity]], [[id_spaces_that_look_comparable]]).
    """
    pool, _ = data.shared_pool()
    victim = ("@klopotenkofood:6040", 21239)
    sibling = ("@VARUS_channel:10470", 21239)
    holdout = sft.holdout_units()
    assert victim in holdout
    assert sibling in {(one["thread"], one["msg_id"]) for one in pool}
    monkeypatch.setattr(sft, "holdout_units", lambda: holdout - {victim})
    widened, _ = data.shared_pool()
    keys = {(one["thread"], one["msg_id"]) for one in widened}
    assert len(widened) == len(pool) + 1
    assert victim in keys and sibling in keys


def test_every_training_row_has_a_rationale_whose_cue_is_in_its_own_comment(train_rows):
    for row in train_rows:
        assert data.norm(row["cue"]) in data.norm(row["prompt"])
        assert f"(cue: «{row['cue']}»)" in row["rationale"]
        assert len(row["rationale"]) <= pass1_v3.RATIONALE_MAX_CHARS


def test_a_rationale_whose_cue_is_not_in_the_comment_is_refused(tmp_path, monkeypatch):
    """A rationale written from the LABEL rather than from the text — the failure this line exists
    to avoid, planted and refused."""
    rows = jsonl(RATIONALES)
    rows[0]["cue"] = "цього рядка тут немає"
    rows[0]["rationale"] = "коментар ПРО щось (cue: «цього рядка тут немає»)"
    planted = tmp_path / "rationales.jsonl"
    planted.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    monkeypatch.setattr(data, "RATIONALES", planted)
    pool, _ = data.shared_pool()
    with pytest.raises(SystemExit, match="written from the LABEL"):
        data.joined(pool)


def test_a_duplicate_pair_in_the_rationale_file_is_refused(tmp_path, monkeypatch):
    rows = jsonl(RATIONALES)
    planted = tmp_path / "rationales.jsonl"
    planted.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows + [rows[0]]),
        encoding="utf-8",
    )
    monkeypatch.setattr(data, "RATIONALES", planted)
    with pytest.raises(SystemExit, match="appears twice"):
        data.rationales()


def test_the_rationales_do_not_collapse_to_a_template(record):
    """Distinct cues per class, and the majority class is the one that matters.

    If `не_наш_рынок`'s rationales collapsed to a handful of strings the target would be a
    deterministic function of the label again and the whole line would be line B in a new costume.
    The bar here is deliberately loose — 90 % distinct — because the finding is a COLLAPSE, not a
    coincidence between two short comments.
    """
    for name, cell in record["rationales"]["distinct"]["per_class"].items():
        if cell["rows"] < 5:
            continue
        assert cell["distinct_cues"] >= 0.9 * cell["rows"], name


# --- the SFT row: one rendering for training and inference -----------------------------------------


def test_the_sft_prompt_is_the_v3_inference_request_byte_for_byte(train_rows):
    """Re-render every row through the inference renderer and compare the STRING, not only its sha.

    Not a re-read of the file's own field: the builder is driven, the fields it kept are handed
    back to `pass1_v3.pass1_messages_gm4_v3`, and the two strings are compared
    ([[build_the_training_prompt_with_the_inference_call]]).
    """
    built = data.build()
    rows = {one["id"]: one for one in built["rows_data"]}
    assert sorted(rows) == sorted(one["id"] for one in train_rows)
    for shipped in train_rows:
        one = rows[shipped["id"]]
        again = data.render_v3(one["fields"], one["examples"])
        assert again == one["prompt"]
        assert again == shipped["prompt"]
        assert data.sha_text(again) == shipped["rendering_sha256"]


def test_the_supervised_span_covers_the_rationale_and_ends_at_the_label(train_rows):
    """The +1 END-offset boundary, inherited by CALL and shifted by the prefix.

    `train_qlora.load_sft` re-derives the same boundary from the label, so this asserts the property
    that guard checks — and then drives the guard itself below.
    """
    for row in train_rows:
        head = row["target"][: row["learn_chars"]]
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        assert head.endswith(f"{label}{trainer.SUPERVISED_SEPARATOR}")
        assert head.startswith('{"rationale": ')
        assert row["rationale"] in head
        assert 0 < row["learn_chars"] < len(row["target"])
        assert (
            prompts.parse_pass1(row["target"], msg_id=row["msg_id"])["subject_type"]
            == (row["subject_type"])
        )


def test_the_pinned_trainer_refuses_a_v3_row_by_name(tmp_path):
    """The registered reachability fact, DRIVEN — and what passes is asserted beside what fails.

    `train_qlora.load_sft` refuses on the task name; give it v1's name and the SAME row passes,
    which is what makes the refusal a statement about the task field and not about the row's shape
    ([[a_registered_bar_may_have_no_producer]]).
    """
    row = jsonl(TRAIN)[0]
    path = tmp_path / "v3.jsonl"
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="is not 'pass1_comment_gm4_v1'"):
        trainer.load_sft(path)
    path.write_text(
        json.dumps({**row, "task": prompts.PASS1_TASK}, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    assert trainer.load_sft(path)[0]["id"] == row["id"]


def test_the_ratio_model_clears_2816_and_the_real_tokenizer_does_not(record):
    """The second STOP after amendment 3.25 (1), as the two numbers that disagree.

    The model that DERIVED 2 816 says every row now fits it. The tokenizer, run for real at the
    pinned revision, says three rows cross the amendment's own 2 800 stop and the widest needs more
    than `max_seq_len` itself. Both directions are asserted, because either alone passes for the
    wrong reason: a model that still refused every row would mean the raise never landed, and a
    count under 2 800 would mean there is nothing to take back to the operator
    ([[projected_rate_versus_measured_rate]]).
    """
    tokens = record["tokens"]
    counted = json.loads((REPO_ROOT / "results" / "lora_c_tokens.json").read_text("utf-8"))
    assert tokens["max_seq_len"] == data.MAX_SEQ_LEN == 2816
    for name, cell in tokens["by_ratio"].items():
        assert cell["over_max_seq_len"] == 0, name

    assert counted["rows"] == len(jsonl(TRAIN)) == 506
    assert counted["max_seq_len"] == tokens["max_seq_len"]
    assert counted["stop_threshold"] == 2800
    assert counted["rows_over_the_stop_threshold"] == len(counted["over"]) == 3
    assert counted["pod_count_plus_template_slack"]["max"] > counted["max_seq_len"]
    assert counted["verdict"].startswith("STOP")
    # and the model is LOW, which is the reason the amendment ordered the count at all
    assert counted["the_model_this_replaces"]["the_model_underpredicts_by"] > 0


def test_the_smallest_class_has_no_fifth_neighbour(record):
    """The first STOP: the refused rows are exactly the rows of one thread, and that thread is the
    one holding the pool's only `молочный_бренд` row."""
    blocked = record["unreachable"]
    assert blocked["rows_in_the_pool"] == 1
    assert blocked["rows_in_the_650"] == 2
    refused = {one["id"] for one in record["rows"]["refused"]}
    assert refused == {f"{thread}#{msg_id}" for thread, msg_id, _ in blocked["blocked_pool_rows"]}
    assert {one.split("#")[0] for one in refused} == set(blocked["threads"])
    assert "молочный_бренд" not in record["rows"]["distribution"]


def test_neighbours_refuses_a_query_in_that_thread():
    """The refusal itself, driven — not inferred from the count above."""
    pool, _ = data.shared_pool()
    victim = next(one for one in pool if one["subject_type"] == "молочный_бренд")
    with pytest.raises(SystemExit, match="no labelled молочный_бренд comment outside"):
        fewshot.neighbours(victim["thread"], victim["grams"], pool)


# --- the synthetic rows ---------------------------------------------------------------------------


def test_the_synthetic_rows_are_balanced_inside_every_error_class():
    """`classes_over_tolerance` is a TAUTOLOGY on any record that can exist — `balance()` raises on
    that same list before returning it — so the assertion that matters is the spread itself."""
    written = syn.rows()
    assert len(written) == 160
    table = syn.balance(written)
    for name, cell in table["by_class"].items():
        assert cell["spread"] <= syn.BALANCE_TOLERANCE, name
        assert cell["rows"] == 40, name


def test_a_synthetic_prior_is_refused(monkeypatch):
    """Plant a prior — every row of one class the same label — and the balance rule fires."""
    written = syn.rows()
    skewed = [
        {**one, "subject_type": "не_наш_рынок", "subject_id": "x"}
        if one["error_class"] == "brand_vs_retailer"
        else one
        for one in written
    ]
    with pytest.raises(SystemExit, match="synthetic that carries a prior teaches the prior"):
        syn.balance(skewed)


def test_the_four_contamination_lists_are_empty():
    written = syn.rows()
    report = syn.contamination(written)
    for name in ("labelled_rows", "holdout_rows", "reference_thread_comments", "gold_quotes"):
        assert report[name] == [], name
        assert report[f"{name}_n"] > 0, name


def test_a_planted_PARTIAL_echo_is_caught_and_the_producer_now_refuses_it():
    """A partial echo, not a copy — one shared 6-gram with everything around it rewritten.

    The instrument is stronger than a copy test and the control should say so. And
    `contamination()` now RAISES rather than reporting: the STOP used to live only in this test,
    so a producer could write a non-empty list and exit 0 ([[a_checker_whose_failure_is_silence]]).
    """
    long_enough = next(
        one for one in sft.labelled_units() if len(one["text"].split()) >= syn.SHINGLE + 4
    )
    words = long_enough["text"].split()
    start = len(words) // 2 - syn.SHINGLE // 2
    borrowed = " ".join(words[start : start + syn.SHINGLE])
    written = syn.rows()
    planted = [{**written[0], "text": f"зовсім інший початок {borrowed} і зовсім інший кінець"}]
    planted += written[1:]
    with pytest.raises(SystemExit, match="synthetic rows echo real text"):
        syn.contamination(planted)


def test_a_paraphrase_with_no_shared_six_gram_is_NOT_caught():
    """The other direction: the check bounds echoes, not similarity, and says so by passing here."""
    written = syn.rows()
    planted = [{**written[0], "text": "цілком новий текст без жодного спільного шестиграма"}]
    planted += written[1:]
    assert syn.contamination(planted)["labelled_rows"] == []


def test_a_synthetic_thread_can_never_collide_with_a_real_one():
    written = syn.rows()
    real = {one["thread"] for one in sft.labelled_units()}
    assert all(one["thread"].startswith(syn.PREFIX) for one in written)
    assert not {one["thread"] for one in written} & real


def test_no_synthetic_row_reaches_the_pool_or_the_eval_set(pack):
    pool, _ = data.shared_pool()
    assert not [one for one in pool if one["thread"].startswith(syn.PREFIX)]
    for leg in pack["legs"]:
        assert not [one for one in leg["items"] if one["thread"].startswith(syn.PREFIX)]


def test_a_synthetic_row_planted_in_the_pool_is_refused(monkeypatch):
    """The eval builder's own guard, driven — a synthetic row in the neighbour pool STOPS it."""
    pool, census = data.shared_pool()
    fake = {**pool[0], "thread": f"{syn.PREFIX}planted"}
    monkeypatch.setattr(data, "shared_pool", lambda: (pool + [fake], census))
    with pytest.raises(SystemExit, match="synthetic threads reached the neighbour pool"):
        evalpack.build()


# --- eval set E -----------------------------------------------------------------------------------


def test_e_is_the_union_and_the_two_legs_are_paired(pack):
    made = pack["made"]
    assert (
        made["arithmetic"] == f"{made['holdout']} + {made['reference_payable']}"
        f" − {made['overlap']} = {made['e']}"
    )
    assert made["e"] == 200
    v2 = evalpack.leg_of(pack, "v2")["items"]
    v3 = evalpack.leg_of(pack, "v3")["items"]
    assert [one["id"] for one in v2] == [one["id"] for one in v3]
    assert all(one["rendering_sha256"] != other["rendering_sha256"] for one, other in zip(v2, v3))
    assert evalpack.leg_of(pack, "v2")["task"] == prompts.PASS1_TASK_V2
    assert evalpack.leg_of(pack, "v3")["task"] == pass1_v3.PASS1_TASK_V3


def test_no_e_row_sees_a_neighbour_from_its_own_thread(pack):
    for leg in pack["legs"]:
        for one in leg["items"]:
            assert all(pick["thread"] != one["thread"] for pick in one["examples_chosen"])


def test_the_fourteen_are_inside_e_and_take_no_bar(pack):
    assert len(pack["membership"]["gold_14"]) == 14
    assert "NEVER a bar" in pack["membership"]["gold_14_rule"]
    registration = json.loads(PREREG.read_text(encoding="utf-8"))
    assert registration["bars"]["report_only"]["gold_14"].startswith("the SIXTH look")
    for name, leg in registration["legs"].items():
        assert leg["bar"] in (None, "the registered three, all-or-RED"), name


def test_dev_200_is_SPLIT_and_the_record_says_which_half_gives_which_reading(pack):
    """dev-200 is not disjoint from E — 80 of its 200 rows are in it — and the record used to deny
    that in the same document that listed them ([[a_count_in_prose_is_not_the_enumeration]])."""
    split = pack["membership"]["dev_200_split"]
    assert split["in_train"] + split["in_E"] + split["in_neither"] == split["of"] == 200
    assert split["in_E"] == len(pack["membership"]["dev_200_in_e"]) == 80
    rule = pack["membership"]["dev_200_rule"]
    assert "SPLIT" in rule and "legitimate EVAL reading" in rule
    # assert the CORRECTED claim, not the absence of a string the correction legitimately quotes
    assert "not disjoint from it either" in pack["made"]["rule"]


# --- the pass-2 builder ---------------------------------------------------------------------------


def test_the_pass_2_builder_reproduces_r2_on_the_window_out_files():
    """The contract names this as the builder's test, so it is one — bars, not a thread count."""
    check = p2pack.reproduce()
    assert check["bar_1_reading"] == p2pack.EXPECTED_BAR_1
    assert check["bar_3_signals"] == p2pack.EXPECTED_BAR_3_SIGNALS
    assert check["agrees"]
    assert check["replies_refused"] == []


# --- the registration -----------------------------------------------------------------------------


def test_the_rulings_are_quoted_verbatim_and_a_paraphrase_is_refused():
    assert prereg.quoted(prereg.RULING_V)
    assert prereg.quoted(prereg.RULING_K)
    with pytest.raises(SystemExit, match="not in STATUS.md"):
        prereg.quoted("(в) Затем — LoRA поверх v2, примерно так")


def test_the_registration_carries_no_price():
    registration = json.loads(PREREG.read_text(encoding="utf-8"))
    money = registration["money"]
    assert money["cap_usd_all_in"] == 4.00
    assert money["state"].startswith("OPEN")
    keys = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            keys.update(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(money)
    # the FIELD names, not the prose: the block says in words that it carries none of these, and a
    # grep of the flat JSON would read that sentence as the thing it forbids
    for forbidden in ("worst_case_usd", "total_seconds", "projected_usd_at_the_price_ceiling"):
        assert forbidden not in keys
    for name in (
        "pass_1_seconds_per_call",
        "pass_2_seconds_per_thread",
        "training_seconds_per_step",
    ):
        assert money["rates_and_what_would_invalidate_them"][name]["invalidating_condition"]


def test_the_registration_is_a_draft_while_the_verdicts_are_absent():
    registration = json.loads(PREREG.read_text(encoding="utf-8"))
    assert registration["state"].startswith("DRAFT")
    for cell in registration["instruments"]["written_inputs"].values():
        assert cell["verdict_present"] == (REPO_ROOT / cell["review_gate"]).exists()
        if not cell["verdict_present"]:
            assert cell["reviewed"] == [False]


def test_the_four_reachability_blocks_are_registered():
    """Four blocks, and each carries either its own remedies or a pointer to the block that does."""
    registration = json.loads(PREREG.read_text(encoding="utf-8"))
    reach = registration["reachability"]
    assert set(reach) == {
        "the_smallest_class_has_no_fifth_neighbour",
        "three_rows_do_not_fit_max_seq_len",
        "arm_a_has_no_молочный_бренд_target",
        "the_pinned_trainer_refuses_a_v3_dataset",
    }
    for name, cell in reach.items():
        assert any("remed" in key for key in cell) or any(
            "remed" in key for value in cell.values() if isinstance(value, dict) for key in value
        ), name


def test_arm_a_has_no_dairy_brand_target_and_arm_b_has_thirty_two():
    """The fourth block, re-derived from the two datasets — and from the sampler's own table.

    A class absent from `train_qlora.class_weights` cannot be drawn by `sampling_order` at all, so
    «arm A has zero targets» is a statement about what the run CAN emit and not only about a count.
    """
    train = jsonl(TRAIN)
    synthetic = jsonl(SYNTHETIC)
    assert not [one for one in train if one["subject_type"] == "молочный_бренд"]
    assert len([one for one in synthetic if one["subject_type"] == "молочный_бренд"]) == 32
    assert "молочный_бренд" not in trainer.class_weights(train)
    assert "молочный_бренд" in trainer.class_weights(
        train + [{"subject_type": one["subject_type"]} for one in synthetic]
    )
    block = json.loads(PREREG.read_text(encoding="utf-8"))["reachability"][
        "arm_a_has_no_молочный_бренд_target"
    ]
    assert block["arm_a_targets"] == 0
    assert block["arm_b_targets"] == 32


def test_the_executors_own_concern_reached_the_gate_and_the_ruling_closed_it():
    """The 15 rows reached the gate-2 file, R1 ruled for them, and the instrument now finds none.

    Both ends are asserted. The FROZEN sample still names all fifteen — that file is the evidence
    the verdict rests on and it is never re-rendered — and the live instrument that raised them
    matches nothing after R1's rewrites. A test that only checked the zero could not tell «fixed»
    from «the matcher stopped working», so the sample's fifteen are the negative control.
    """
    record = json.loads(
        (REPO_ROOT / "results" / "lora_c_synthetic.json").read_text(encoding="utf-8")
    )
    flag = record["self_flagged"]
    assert flag["n"] == len(flag["rows"]) == 0
    assert flag["rows_at_the_gate_2_sample"] == 15
    assert flag["action_taken"].startswith("RULING R1")
    text = SAMPLE_2.read_text(encoding="utf-8")
    assert "What this file believes may be wrong" in text
    section = text.split("## What this file believes may be wrong")[1]
    assert "**15 of 160 rows.**" in section
    assert len(re.findall(r"`synthetic:\w+:\d+`", section)) == 15


# --- the two review gates -------------------------------------------------------------------------


def test_review_gate_1_shows_every_our_row_and_forty_boundary_rows(record):
    text = SAMPLE_1.read_text(encoding="utf-8")
    gate = record["review_gate_1"]
    assert gate["our_rows"] == record["rows"]["our_rows"]
    assert gate["boundary"]["total"] == data.BOUNDARY_TARGET
    assert gate["boundary"]["seed"] == data.BOUNDARY_SEED
    assert str(data.BOUNDARY_SEED) in text
    assert text.count("|  |") == gate["our_rows"] + gate["boundary"]["total"]
    assert "docs/reviews/lora-c-rationales-verdict.md" in text


def test_review_gate_2_shows_all_160_rows_with_a_blank_verdict_column():
    text = SAMPLE_2.read_text(encoding="utf-8")
    assert text.count("|  |") == 160
    assert "docs/reviews/lora-c-synthetic-verdict.md" in text
    for name, _ in syn.CLASSES:
        assert f"`{name}`" in text


PRODUCERS = [
    # `--sample` is still PASSED, so the sample renderer and the freeze guard are both driven; the
    # sample FILES are no longer compared, because a verdict closes its own sample and the producer
    # now refuses to rewrite one. `test_a_sample_is_closed_by_its_verdict` is that guard's control.
    (
        "scripts/build_lora_c_data.py",
        ["--sample"],
        {
            "--train-out": "results/pass1_sft_v3_train.jsonl",
            "--record-out": "results/lora_c_data.json",
        },
    ),
    (
        "scripts/build_lora_c_synthetic.py",
        ["--sample"],
        {"--record-out": "results/lora_c_synthetic.json"},
    ),
    ("scripts/build_lora_c_eval_pack.py", [], {"--out": "results/lora_c_eval_pack.json"}),
    (
        "scripts/build_lora_c_pass2_pack.py",
        ["--leg", "window_v2"],
        {"--out": "results/lora_c_pass2_pack.json"},
    ),
    ("scripts/write_lora_c_prereg.py", [], {"--out": "results/prereg_lora_c.json"}),
]


def test_a_sample_is_closed_by_its_verdict(tmp_path):
    """Both directions of the freeze, on both samples.

    The file a team lead read is the evidence their ruling rests on. Re-rendering it from data the
    ruling has since moved would hand a later reader a document nobody reviewed under the name of
    one that was — so with the verdict present the producer writes nothing, and with it absent it
    writes as before. A guard tested only in the state that satisfies it is a guard nobody has seen
    fire ([[guard_selftest_negative_control]]).
    """
    for verdict, out in (
        (data.VERDICT, tmp_path / "one.md"),
        (syn.VERDICT, tmp_path / "two.md"),
    ):
        assert verdict.exists(), verdict
        assert data.sample_is_closed(verdict, out) is True
        assert data.sample_is_closed(tmp_path / "no-such-verdict.md", out) is False

    # and end to end: the shipped samples are untouched by a full `--sample` run
    before = {one: one.read_bytes() for one in (SAMPLE_1, SAMPLE_2)}
    for script, flags in (
        ("scripts/build_lora_c_data.py", ["--sample", "--train-out", str(tmp_path / "t.jsonl")]),
        ("scripts/build_lora_c_synthetic.py", ["--sample"]),
    ):
        done = subprocess.run(
            [sys.executable, script, *flags, "--record-out", str(tmp_path / "r.json")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        assert done.returncode == 0, done.stderr[-2000:]
        assert "is CLOSED by" in done.stdout, done.stdout[-500:]
    assert {one: one.read_bytes() for one in (SAMPLE_1, SAMPLE_2)} == before


@pytest.mark.parametrize("script, flags, outputs", PRODUCERS, ids=[one[0] for one in PRODUCERS])
def test_every_producer_is_driven_end_to_end_and_rebuilds_its_shipped_bytes(
    script, flags, outputs, tmp_path
):
    """Each producer is RUN, and what it emits is compared BYTE FOR BYTE with what is committed.

    Two properties in one command, and neither is free without the other. Running it proves the
    entry point's preamble executes at all — an import proves the module parses and nothing more
    ([[the_entry_points_preamble_is_untested_code]], [[stub_driven_script_verification]]). Comparing
    the bytes proves the committed record is what TODAY's producer emits: these five scripts were
    patched repeatedly and rebuilt by hand each time, and a hand-rebuild that was skipped once
    leaves a record describing a producer that no longer exists. This repo already has the shape —
    `test_the_pack_rebuilds_byte_for_byte_from_its_own_inputs`.

    Writes go to a temporary directory, so a green suite can never depend on having overwritten a
    committed artifact as a side effect of running the tests.
    """
    command = [sys.executable, script, *flags]
    for flag, shipped in outputs.items():
        command += [flag, str(tmp_path / Path(shipped).name)]
    done = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert done.returncode == 0, done.stderr[-2000:]
    for shipped in outputs.values():
        again = tmp_path / Path(shipped).name
        assert again.exists(), f"{script} did not write {shipped}"
        assert again.read_bytes() == (REPO_ROOT / shipped).read_bytes(), (
            f"{shipped} on disk is NOT what {script} emits today — the committed record describes a"
            " producer that has moved since it was written. Re-run the producer and commit."
        )


def test_the_pass_2_reproduction_command_is_driven_end_to_end():
    """`--reproduce` writes nothing, so it is driven for its EXIT CODE — which is the verdict."""
    done = subprocess.run(
        [sys.executable, "scripts/build_lora_c_pass2_pack.py", "--reproduce"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    assert "AGREES: True" in done.stdout


# --- lora-c-apply: the two verdicts and amendment 3.25 --------------------------------------------


def test_the_r3_delta_is_a_layer_and_refuses_to_be_a_draw():
    """The delta corrects a drawn unit and may not introduce one — both directions.

    r2 composes with r1 by being a second disjoint DRAW of 150 units; r3 is neither a draw nor
    disjoint — it is one correction laid over the same keys, last wins. The distinction is not
    cosmetic: a row that arrived through a «delta» would be a unit nobody drew, sitting in the
    training pool with no pack behind it ([[select_one_row_refuse_ambiguity]]).
    """
    delta = data.labels_r3()
    assert delta == {("@retsepty:7342", 49685): "не_наш_рынок"}

    units = [
        {"thread": "@retsepty:7342", "msg_id": 49685, "subject_type": None},
        {"thread": "@retsepty:7342", "msg_id": 49686, "subject_type": "не_наш_рынок"},
    ]
    applied, census = data.apply_r3([dict(one) for one in units])
    assert applied[0]["subject_type"] == "не_наш_рынок"
    assert applied[1]["subject_type"] == "не_наш_рынок"
    assert census["rows_moved"] == 1
    assert census["moved"] == [{"row": "@retsepty:7342#49685", "was": None, "now": "не_наш_рынок"}]
    # the negative control: the same delta over rows that never drew it
    with pytest.raises(SystemExit, match="a delta may only CORRECT a drawn unit"):
        data.apply_r3([{"thread": "@nobody:1", "msg_id": 2, "subject_type": None}])


def test_the_r3_delta_reaches_the_pool_and_not_line_bs_sealed_arms():
    """The correction is lora-c's. Line B's datasets were sealed before it existed."""
    record = json.loads(DATA_RECORD.read_text(encoding="utf-8"))
    assert record["population"]["labels_r3"]["rows_moved"] == 1
    rows = {(one["thread"], one["msg_id"]): one for one in jsonl(TRAIN)}
    assert rows[("@retsepty:7342", 49685)]["subject_type"] == "не_наш_рынок"
    sealed = jsonl(REPO_ROOT / "results" / "pass1_sft_arm_b.jsonl")
    theirs = [one for one in sealed if one["id"].endswith("49685")]
    assert theirs and theirs[0]["subject_type"] is None, (
        "line B's sealed arm still carries the pre-correction label, which is what «sealed» means"
    )


def test_the_equality_refusal_removes_only_an_identical_text():
    """Amendment 3.25 (2), both directions and at the boundary.

    The threshold is EQUALITY and nothing below it, so the row that proves the rule is the one at
    similarity 0.9875 — the highest strictly below 1.0 anywhere in this window — which must still
    be eligible. Whitespace and case are collapsed first, because that is the form the amendment
    names.
    """
    pool = [
        {
            "thread": "@a:1",
            "msg_id": 1,
            "text": "порожній рядок",
            "subject_type": None,
            "grams": fewshot.grams("порожній рядок"),
        },
        {
            "thread": "@a:1",
            "msg_id": 2,
            "text": "те   САМЕ",
            "subject_type": "не_наш_рынок",
            "grams": fewshot.grams("те   САМЕ"),
        },
        {
            "thread": "@a:1",
            "msg_id": 6,
            "text": "те саме, але не зовсім",
            "subject_type": "не_наш_рынок",
            "grams": fewshot.grams("те саме, але не зовсім"),
        },
        {
            "thread": "@a:1",
            "msg_id": 3,
            "text": "Те саме, майже",
            "subject_type": "категория_личное",
            "grams": fewshot.grams("Те саме, майже"),
        },
        {
            "thread": "@a:1",
            "msg_id": 4,
            "text": "зовсім інше",
            "subject_type": "сеть_ритейлер",
            "grams": fewshot.grams("зовсім інше"),
        },
        {
            "thread": "@a:1",
            "msg_id": 5,
            "text": "ще одне",
            "subject_type": "молочный_бренд",
            "grams": fewshot.grams("ще одне"),
        },
    ]
    query = "ТЕ   саме"
    plain = fewshot.neighbours("@q:9", fewshot.grams(query), pool)
    assert any(data.norm(one["text"]) == data.norm(query) for one in plain), (
        "the unamended rule must show the twin, or this test proves nothing"
    )
    amended = data.neighbours_v3("@q:9", query, fewshot.grams(query), pool)
    assert not any(data.norm(one["text"]) == data.norm(query) for one in amended)
    # the near-twin is untouched: equality, and nothing below it
    assert ("@a:1", 3) in [(one["thread"], one["msg_id"]) for one in amended]
    # and a class emptied by the refusal is a NEW instance of STOP 1, raised rather than patched
    with pytest.raises(SystemExit, match="cannot be given one example of each class"):
        data.neighbours_v3("@q:9", "зовсім інше", fewshot.grams("зовсім інше"), pool)


def test_no_pack_shows_a_query_its_own_text():
    """The leak, measured over the SHIPPED packs rather than trusted to the filter."""
    pack = json.loads(EVAL_PACK.read_text(encoding="utf-8"))
    leak = pack["own_text_in_examples"]
    assert leak["n"] == 0 and leak["on_the_gating_bar"] == 0
    assert leak["remedy"]["state"] == "CLOSED"
    assert leak["remedy"]["measured_at_97548df"]["e_items"] == 22
    own = 0
    for row in jsonl(TRAIN):
        for one in row["examples_chosen"]:
            if one.get("similarity") == 1.0:
                own += 1
    assert own == 0, "a training row is still shown a neighbour identical to its own text"


def test_the_newline_pass_is_seeded_idempotent_and_never_trailing():
    rows = jsonl(SYNTHETIC)
    texts = [one["text"] for one in rows]
    assert syn.newline_pass(texts) == texts, (
        "re-running the pass on its own output must reproduce it"
    )
    assert len([one for one in texts if "\n" in one]) == syn.NEWLINE_TARGET == 30
    assert not [one for one in texts if one.endswith("\n") or one.startswith("\n")]
    # a different seed picks different rows, or the seed is decorative
    assert syn.newline_pass(texts, seed=syn.NEWLINE_SEED + 1) != texts


def test_no_skeleton_covers_more_than_a_third_of_the_dairy_brand_rows():
    rows = jsonl(SYNTHETIC)
    census = syn.skeletons(rows)
    assert census["rows"] == 32 and census["ceiling"] == 10
    assert census["largest"]["rows"] <= census["ceiling"]
    assert census["passes"]
    # the instrument is not vacuous: it separates the 32 into more than two frames
    assert len(census["by_skeleton"]) >= 4


def test_the_tokenizer_check_refuses_a_substitute_template(monkeypatch):
    """The three states of «is this file in the cache», and only one of them licenses the count.

    A path means present, a sentinel means the Hub answered «no such file», and None means nobody
    ever asked. Absent and unasked are different answers ([[unreadable_now_versus_never]]), and a
    substitute chat template would look exactly like a measurement.
    """
    import tokenize_lora_c_rows as tok

    for state in (
        {"chat_template.jinja": "/x", "chat_template.json": "UNASKED"},
        {"chat_template.jinja": "/x", "chat_template.json": "/y"},
        {"chat_template.jinja": "PROVEN-ABSENT", "chat_template.json": "PROVEN-ABSENT"},
    ):
        monkeypatch.setattr(tok, "templates_of", lambda *a, **k: dict(state))
        with pytest.raises(SystemExit):
            tok.measure([])


def test_the_registration_carries_the_count_and_quotes_the_amendment():
    registration = json.loads(PREREG.read_text(encoding="utf-8"))
    check = registration["training"]["tokenizer_reality_check"]
    assert check["ran"] is True and check["verdict"].startswith("STOP")
    assert check["rows_over"] == 3
    assert registration["training"]["config_agrees_with_lora_b"] is False
    assert registration["training"]["config_revision"] == 2
    assert "FALSE ON PURPOSE" in registration["training"]["config_agrees_with_lora_b_reading"]

    spec = " ".join((REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8").split())
    quoted = registration["authority"]["amendment_3_25"]
    for key in ("1_max_seq_len", "2_the_neighbour_refusal", "3_stop_1_as_built"):
        assert " ".join(quoted[key].split()) in spec, key


def _tokenizer_is_obtainable() -> bool:
    try:
        import transformers  # noqa: F401
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    import tokenize_lora_c_rows as tok

    return isinstance(
        try_to_load_from_cache(
            "google/gemma-4-31b-it", "chat_template.jinja", revision=tok.revision()
        ),
        str,
    )


@pytest.mark.skipif(
    not _tokenizer_is_obtainable(),
    reason="the model tokenizer is not on this machine — amendment 3.25 (1)'s other branch, and"
    " results/lora_c_tokens.json then describes a measurement this suite cannot re-run",
)
def test_the_tokenizer_producer_rebuilds_its_shipped_bytes(tmp_path):
    """The fifth producer, driven end to end like the other four — it writes a REGISTERED number."""
    done = subprocess.run(
        [
            sys.executable,
            "scripts/tokenize_lora_c_rows.py",
            "--out",
            str(tmp_path / "lora_c_tokens.json"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert done.returncode == 0, done.stderr[-2000:]
    shipped = REPO_ROOT / "results" / "lora_c_tokens.json"
    assert (tmp_path / "lora_c_tokens.json").read_bytes() == shipped.read_bytes()
