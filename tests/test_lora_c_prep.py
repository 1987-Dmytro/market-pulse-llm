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


def test_no_v3_row_fits_max_seq_len_at_any_measured_ratio(record):
    """The second STOP, as a number rather than as a sentence."""
    tokens = record["tokens"]
    assert tokens["max_seq_len"] == data.MAX_SEQ_LEN
    for name, cell in tokens["by_ratio"].items():
        assert cell["over_max_seq_len"] == cell["of"], name
        assert cell["pods_own_count_of_the_shortest"] > tokens["max_seq_len"], name


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
        "no_row_fits_max_seq_len",
        "arm_a_has_no_молочный_бренд_target",
        "the_pinned_trainer_refuses_a_v3_dataset",
    }
    for name, cell in reach.items():
        assert any("remed" in key for key in cell), name


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


def test_the_synthetic_sample_carries_the_executors_own_concern():
    """The 15 rows flagged against the codebook reach the gate-2 file, and none was rewritten."""
    record = json.loads(
        (REPO_ROOT / "results" / "lora_c_synthetic.json").read_text(encoding="utf-8")
    )
    flag = record["self_flagged"]
    assert flag["n"] == len(flag["rows"]) > 0
    assert flag["action_taken"].startswith("NONE")
    text = SAMPLE_2.read_text(encoding="utf-8")
    assert "What this file believes may be wrong" in text
    for one in flag["rows"]:
        assert one in text


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
    (
        "scripts/build_lora_c_data.py",
        ["--sample"],
        {
            "--train-out": "results/pass1_sft_v3_train.jsonl",
            "--record-out": "results/lora_c_data.json",
            "--sample-out": "docs/reviews/lora-c-rationales-sample.md",
        },
    ),
    (
        "scripts/build_lora_c_synthetic.py",
        ["--sample"],
        {
            "--record-out": "results/lora_c_synthetic.json",
            "--sample-out": "docs/reviews/lora-c-synthetic.md",
        },
    ),
    ("scripts/build_lora_c_eval_pack.py", [], {"--out": "results/lora_c_eval_pack.json"}),
    (
        "scripts/build_lora_c_pass2_pack.py",
        ["--leg", "window_v2"],
        {"--out": "results/lora_c_pass2_pack.json"},
    ),
    ("scripts/write_lora_c_prereg.py", [], {"--out": "results/prereg_lora_c.json"}),
]


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
