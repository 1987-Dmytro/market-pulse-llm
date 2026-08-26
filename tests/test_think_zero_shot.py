"""`think-zero-shot` D1 — the thinking instrument, driven at $0 on the Mac.

Ruling (ф) buys the same prompts over the same rows with Gemma 4's thinking channel OPEN. Nothing
about the measurement is new; what is new is that the model now writes its working-out INTO the
reply, and three shipped things read that reply: the parser, the transport's balanced-object stop,
and the row the runner persists. Each of the three is driven here in both directions.

**The stop is the one that costs money.** `reader_v5_pod_runner.stop_at_balanced` ends generation at
the first balanced top-level object; a thought that reasons about the object it is about to write
contains braces, so without the rule below generation stops MID-THOUGHT and the runner persists half
a thought as the verdict. That failure lives inside `model.generate` and a fake client replaces the
whole call — so `stops_here` is split out of the criterion and driven on strings, with the refusal
AND the control ([[a_stub_replaces_the_guard_it_should_trigger]], [[guard_selftest_negative_control]]).

Nothing here imports torch or transformers: the REAL template is exercised by
`scripts/preflight_serving_guards.py`, which renders it from the pinned revision on disk.
"""

import inspect
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

import build_think_packs as builder  # noqa: E402
import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import project_think_zero_shot as projector  # noqa: E402
import pass2_r2_pod_runner as pass2runner  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

import moved_pins  # noqa: E402
import write_pass1_prereg_b as prereg_b  # noqa: E402

from market_pulse import local_llm, prompts, reader_v5  # noqa: E402

RESULTS = REPO_ROOT / "results"
OPEN, CLOSE = prompts.THOUGHT_OPEN, prompts.THOUGHT_CLOSE
VERDICT = json.dumps(
    {
        "thread": {"channel": "@c", "post_id": 1},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
    },
    ensure_ascii=False,
)
PASS1_ANSWER = json.dumps(
    {"msg_id": 7, "subject_type": "сеть_ритейлер", "subject_id": "varus", "stance": "negative"},
    ensure_ascii=False,
)
BRACED_THOUGHT = (
    f'{OPEN}thought\nThe answer should be {{"subject_type": "категория_личное"}} — no, on second'
    f" reading the commenter names the shop.\n{CLOSE}"
)
"""A thought with a BALANCED object inside it, and a conclusion that contradicts it.

Not decoration: it is the whole failure mode in one string. `balanced_prefix` balances the object in
the working-out, `_object` reads the first brace, and both would answer `категория_личное` for a
reply whose verdict says something else."""


# --- the three states of the channel -------------------------------------------------------------


def test_a_reply_with_no_channel_is_returned_whole():
    """Today's shape, and every reply this repo has bought: `enable_thinking: false` closes the
    channel in the PROMPT, so the generated half carries neither marker."""
    assert prompts.split_thought(VERDICT) == ("", VERDICT)
    assert prompts.after_thought(VERDICT) == VERDICT


def test_a_closed_thought_is_split_at_its_closer():
    thought, answer = prompts.split_thought(BRACED_THOUGHT + VERDICT)
    assert thought.endswith(CLOSE) and thought.startswith(OPEN)
    assert answer == VERDICT
    assert prompts.after_thought(BRACED_THOUGHT + VERDICT) == VERDICT


def test_an_unclosed_thought_is_a_parse_failure_and_not_an_exception():
    """The contract's own words. A `ParseError` is what every driver counts by reason; anything else
    would end the run instead of costing it one row."""
    unclosed = f"{OPEN}thought\nstill working on {{it"
    with pytest.raises(prompts.ParseError) as raised:
        prompts.after_thought(unclosed)
    assert raised.value.reason == "unclosed thought channel"
    assert isinstance(raised.value, ValueError)


# --- D1.2: the parser, for BOTH families ---------------------------------------------------------


@pytest.mark.parametrize(
    "read",
    [
        pytest.param(lambda text: prompts.parse_reply(prompts.READER_TASK_V2, text), id="reader"),
        pytest.param(lambda text: prompts.parse_pass1(text, msg_id=7), id="pass1"),
    ],
)
def test_braces_inside_the_thought_still_parse_the_answer(read):
    """The contract names `parse_reply`; dev-200's 87/200 and 136/200 are read by `parse_pass1`.
    Both reach `_object`, which is where the rule is stated, so both are held to it here."""
    for text in (VERDICT, PASS1_ANSWER):
        try:
            straight = read(text)
        except (prompts.ParseError, ValueError):
            continue
        assert read(BRACED_THOUGHT + text) == straight, (
            "the answer after a closed thought must read exactly as the same answer with no"
            " thought in front of it"
        )


@pytest.mark.parametrize(
    "read",
    [
        pytest.param(lambda text: prompts.parse_reply(prompts.READER_TASK_V2, text), id="reader"),
        pytest.param(lambda text: prompts.parse_pass1(text, msg_id=7), id="pass1"),
    ],
)
def test_an_unclosed_thought_reaches_both_parsers_as_a_refusal(read):
    with pytest.raises(prompts.ParseError):
        read(f"{OPEN}thought\nI think {{ the subject is")


def test_a_closed_empty_thought_parses_as_before():
    """Today's rendered shape, arriving in the REPLY instead of the prompt: the closer is there and
    there is nothing in front of it. It has to read identically to no thought at all."""
    empty = f"{OPEN}thought\n{CLOSE}"
    assert prompts.parse_reply(prompts.READER_TASK_V2, empty + VERDICT) == prompts.parse_reply(
        prompts.READER_TASK_V2, VERDICT
    )
    assert prompts.parse_pass1(empty + PASS1_ANSWER, msg_id=7) == prompts.parse_pass1(
        PASS1_ANSWER, msg_id=7
    )


def test_the_readers_two_object_merge_never_reaches_into_the_thought():
    """`_top_level_objects` scans from the first brace and MERGES what it finds. A thought carrying
    an object would be merged into the verdict — repair (1) authoring structure out of notes."""
    merged = prompts.parse_reply(prompts.READER_TASK_V2, BRACED_THOUGHT + VERDICT)
    assert merged["repairs"] == [], "nothing in the thought may be repaired into the answer"


# --- the transport stop: the refusal and the control ---------------------------------------------


def test_the_stop_does_not_fire_inside_an_open_thought():
    """THE check this contract exists to add. Every prefix of a thought that is still open — braces
    and all — must leave generation running; the answer has not started."""
    growing = BRACED_THOUGHT[: BRACED_THOUGHT.index(CLOSE)]
    assert reader_v5.balanced_prefix(growing) is not None, (
        "the premise: this thought DOES balance an object, so the shipped rule would have stopped"
    )
    for cut in range(1, len(growing) + 1):
        assert runner.stops_here(growing[:cut], prompts, reader_v5) is False


def test_the_stop_fires_on_the_answer_after_the_closer():
    """The positive control. Without it the test above passes on a rule that never stops at all."""
    assert runner.stops_here(BRACED_THOUGHT + VERDICT, prompts, reader_v5) is True
    assert runner.stops_here(BRACED_THOUGHT, prompts, reader_v5) is False
    assert runner.stops_here(BRACED_THOUGHT + VERDICT[:-1], prompts, reader_v5) is False


def test_the_shipped_path_keeps_the_rule_it_always_had():
    """No channel in the text: the answer is the whole text, exactly as `balanced_prefix` read it
    before this contract existed."""
    assert runner.stops_here(VERDICT, prompts, reader_v5) is True
    assert runner.stops_here(VERDICT[:-1], prompts, reader_v5) is False
    assert runner.stops_here(f"{VERDICT}<turn|>", prompts, reader_v5) is True


def test_the_criterion_applies_that_rule_and_decodes_the_specials():
    """The negative control on the two above: they hold a rule, and this holds that the GPU path is
    the caller of it. `<channel|>` is a special token, so a criterion that kept
    `skip_special_tokens=True` would see no boundary and stop in the thought
    ([[a_moved_constant_fails_green]])."""
    source = inspect.getsource(runner.stop_at_balanced)
    assert "skip_special_tokens=False" in source
    assert "stops_here(text, prompts, reader_v5)" in source


# --- the clients ---------------------------------------------------------------------------------


class FakeTokenizer:
    """Ids that behave like the pinned tokenizer's for the one thing these tests read: the closer."""

    bos_token = None
    unk_token_id = 3
    pad_token_id = 0

    def convert_tokens_to_ids(self, token: str) -> int:
        return {prompts.THOUGHT_CLOSE: 101, prompts.THOUGHT_OPEN: 100}.get(token, self.unk_token_id)

    def decode(self, ids, skip_special_tokens=True):
        words = {100: OPEN, 101: CLOSE}
        return "".join(
            "" if (skip_special_tokens and one in words) else words.get(one, chr(one))
            for one in ids
        )


def test_the_default_template_is_the_shipped_one_and_it_did_not_move():
    """The srv-2d / CAPTION / POSITIONS half of D1.1: their clients take no argument at all, and
    the two that do default to the dict three sealed registrations pin."""
    assert local_llm.CHAT_TEMPLATE == {"add_generation_prompt": True, "enable_thinking": False}
    assert local_llm.THINK_CHAT_TEMPLATE == {"add_generation_prompt": True, "enable_thinking": True}
    for client in (local_llm.LocalClient, local_llm.ReaderClient):
        assert (
            inspect.signature(client.__init__).parameters["chat_template"].default
            is local_llm.CHAT_TEMPLATE
        )
    for untouched in (local_llm.CaptionClient, local_llm.PositionsClient):
        assert "chat_template" not in inspect.signature(untouched.__init__).parameters


def test_the_thought_is_counted_in_token_space():
    """`thought_tokens` is the INDEX of the closer in the ids the model emitted — never a second
    tokenization of the decoded string, which is a second instrument that can disagree."""
    ids = [100, 65, 66, 67, 101, 68, 69]
    fields = local_llm.thought_fields(FakeTokenizer(), ids, 101)
    assert fields["thought_tokens"] == 4
    assert fields["thought"] == "ABC"
    # a channel that never closed spent every token it had on working out
    assert local_llm.thought_fields(FakeTokenizer(), [100, 65, 66], 101)["thought_tokens"] == 3


def test_a_tokenizer_that_cannot_name_the_closer_is_refused():
    """Both directions. A closer resolving to <unk> would make every reply one unbroken thought, in
    a file that still looks like a file of answers — silently, on a paid pod."""
    assert local_llm.thought_close_id(FakeTokenizer()) == 101

    class Deaf(FakeTokenizer):
        def convert_tokens_to_ids(self, token):
            return self.unk_token_id

    with pytest.raises(RuntimeError, match="does not know"):
        local_llm.thought_close_id(Deaf())
    with pytest.raises(RuntimeError, match="needs a tokenizer"):
        local_llm.thought_close_id(None)


# --- the serving switch --------------------------------------------------------------------------


def test_the_serving_table_is_closed():
    assert runner.SERVING_TEMPLATES == {
        "READER": "CHAT_TEMPLATE",
        "READER_THINK": "THINK_CHAT_TEMPLATE",
    }
    assert runner.template_of("READER", local_llm) is local_llm.CHAT_TEMPLATE
    assert runner.template_of("READER_THINK", local_llm) is local_llm.THINK_CHAT_TEMPLATE
    with pytest.raises(SystemExit, match="not a serving name"):
        runner.template_of("READER_THINKING", local_llm)


def test_the_out_file_carries_the_instrument_and_the_default_does_not_move():
    assert runner.out_name("pass1_dev_v2.jsonl", "READER") == "pass1_dev_v2.jsonl"
    assert (
        runner.out_name("pass1_dev_v2.jsonl", "READER_THINK") == "pass1_dev_v2.READER_THINK.jsonl"
    )


def test_the_switch_writes_into_the_packs_own_field():
    pack = {"serving": {"serving_config": "READER", "output_tokens": 256}}
    moved = runner.with_serving(pack, "READER_THINK")
    assert moved["serving"]["serving_config"] == "READER_THINK"
    assert moved["serving"]["output_tokens"] == 256, "only the instrument moves"
    assert pack["serving"]["serving_config"] == "READER", "the caller's dict is not mutated"


# --- the packs -----------------------------------------------------------------------------------


THINK_PACKS = {
    name: json.loads((RESULTS / name).read_text(encoding="utf-8"))
    for name in (
        "pass1_dev_pack_think.json",
        "pass1_dev_smoke_think.json",
        "pass2_r2_pack_think_reference.json",
        "pass2_r2_pack_think_remainder.json",
        "pass2_r2_pack_think_smoke.json",
        "pass1_holdout_100_think.json",
    )
}


def test_the_packs_are_what_the_producer_builds_today():
    built = builder.build()
    assert set(built) == set(THINK_PACKS)
    for name, pack in built.items():
        assert pack == THINK_PACKS[name], f"{name} on disk is not what the producer emits today"


@pytest.mark.parametrize("name", sorted(THINK_PACKS))
def test_every_pack_names_its_instrument_and_its_source(name):
    pack = THINK_PACKS[name]
    serving = pack["serving"]
    assert serving["serving_config"] == "READER_THINK"
    assert serving["chat_template"] == local_llm.THINK_CHAT_TEMPLATE
    assert serving["was"]["chat_template"] == local_llm.CHAT_TEMPLATE
    assert serving["output_tokens"] in (builder.PASS1_OUTPUT_TOKENS, builder.PASS2_OUTPUT_TOKENS)
    paths, shas = pack["source"]["path"], pack["source"]["sha256"]
    for one in [paths] if isinstance(paths, str) else paths:
        assert (shas if isinstance(shas, str) else shas[one]) == builder.sha256_of(REPO_ROOT / one)
    assert pack["moved_from_the_shipped_pack"]["was"], "a moved pin that names nothing is not named"


@pytest.mark.parametrize("name", sorted(THINK_PACKS))
def test_every_pack_pins_the_parser_this_checkout_would_read_it_with(name):
    assert THINK_PACKS[name]["instruments"]["parser"]["sha256"] == builder.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "prompts.py"
    )


def test_the_pass_2_packs_carry_nothing_and_partition_the_79():
    reference = THINK_PACKS["pass2_r2_pack_think_reference.json"]
    remainder = THINK_PACKS["pass2_r2_pack_think_remainder.json"]
    for pack in (reference, remainder):
        assert pack["carried"]["ids"] == [], (
            "r1's four rows were answered with the channel CLOSED; seeding them here would put"
            " BEFORE-column replies into the thinking column"
        )
    ids = [one["id"] for pack in (reference, remainder) for one in pack["legs"][0]["items"]]
    shipped = json.loads((RESULTS / "pass2_r2_pack.json").read_text(encoding="utf-8"))
    assert sorted(ids) == sorted(one["id"] for one in shipped["legs"][0]["items"])
    assert len(reference["legs"][0]["items"]) == 11
    assert len(remainder["legs"][0]["items"]) == 68
    # every reference thread is one the shipped pack marks, and no other
    for one in reference["legs"][0]["items"]:
        assert any(one["membership"][kind] for kind in ("E", "F", "N"))
    for one in remainder["legs"][0]["items"]:
        assert not any(one["membership"][kind] for kind in ("E", "F", "N"))


def test_the_smokes_write_into_the_out_file_of_the_leg_they_belong_to():
    """A smoke row is a row the leg then RESUMES over. A smoke with an out-file of its own would be
    a row bought twice — the same money the carried clause exists to save."""
    dev = THINK_PACKS["pass1_dev_pack_think.json"]
    smoke = THINK_PACKS["pass1_dev_smoke_think.json"]["legs"][0]
    v2 = next(leg for leg in dev["legs"] if leg["name"] == "v2")
    assert smoke["out"] == v2["out"]
    assert [one["id"] for one in smoke["items"]] == [one["id"] for one in v2["items"][:3]]

    pass2_smoke = THINK_PACKS["pass2_r2_pack_think_smoke.json"]["legs"][0]
    holder = next(
        pack
        for name, pack in THINK_PACKS.items()
        if name.startswith("pass2_r2_pack_think_") and "smoke" not in name
        if pack["legs"][0]["out"] == pass2_smoke["out"]
    )
    (only,) = pass2_smoke["items"]
    assert only["id"] in {one["id"] for one in holder["legs"][0]["items"]}
    assert only["rendered_chars"] == max(
        one["rendered_chars"]
        for pack in THINK_PACKS.values()
        for leg in pack["legs"]
        for one in leg["items"]
        if "comments" in one
    ), "the smoke is the LONGEST thread — the worst case the projection is built on"


# --- both runners, end to end, on a fake client ---------------------------------------------------


def thinking_reply(payload: str) -> dict:
    """What the client hands the runner under READER_THINK: markers kept, thought counted."""
    return {
        "content": BRACED_THOUGHT + payload,
        "finish_reason": "stop",
        "cost": 0.0,
        "usage": {"prompt_tokens": 11, "completion_tokens": 22},
        "generation_id": None,
        "thought": "The answer should be … the commenter names the shop.",
        "thought_tokens": 37,
    }


def test_the_pass_1_runner_is_driven_end_to_end_under_the_thinking_switch(tmp_path):
    asked = []

    class Client:
        def read(self, task, items):
            asked.extend(one["id"] for one in items)
            return [
                thinking_reply(
                    json.dumps(
                        {
                            "msg_id": int(one["msg_id"]),
                            "subject_type": None,
                            "subject_id": None,
                            "stance": None,
                        }
                    )
                )
                for one in items
            ]

    code = fewshot.main(
        [
            "--pack",
            str(RESULTS / "pass1_dev_smoke_think.json"),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--serving",
            "READER_THINK",
        ],
        loader=lambda *a, **kw: Client(),
    )
    assert code == 0
    out = tmp_path / "pass1_dev_v2.READER_THINK.jsonl"
    assert out.exists(), "the out-file carries the instrument that produced it"
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    assert len(rows) == len(asked) == builder.SMOKE_DEV_ROWS
    for row in rows:
        assert row["thought_tokens"] == 37 and row["thought_chars"] == len(BRACED_THOUGHT)
        assert row["reply"].startswith(OPEN) and row["balanced"] is True
        # the verdict is readable THROUGH the persisted bytes, thought and all
        parsed = prompts.parse_pass1(row["reply"], msg_id=int(row["id"].rsplit("#", 1)[-1]))
        assert parsed["subject_type"] is None


def test_the_pass_2_runner_is_driven_end_to_end_under_the_thinking_switch(tmp_path):
    class Client:
        def read(self, task, items):
            return [thinking_reply(VERDICT) for _ in items]

    code = pass2runner.main(
        [
            "--pack",
            str(RESULTS / "pass2_r2_pack_think_smoke.json"),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--serving",
            "READER_THINK",
        ],
        loader=lambda *a, **kw: Client(),
    )
    assert code == 0
    out = tmp_path / "pass2_signals_r2_remainder.READER_THINK.jsonl"
    (row,) = [
        json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()
    ]
    assert row["thought_tokens"] == 37
    assert prompts.parse_reply(prompts.READER_TASK_V2, row["reply"])["repairs"] == []


def test_the_persisted_reply_is_cut_at_the_ANSWERS_brace_and_keeps_the_thought(tmp_path):
    """The runner's own half of the stop. `cut_chars` counts what was removed from the ANSWER; a
    count taken over the whole emitted string would read the thought as overshoot."""

    class Client:
        def read(self, task, items):
            return [thinking_reply(VERDICT + " and then it kept writing {")]

    code = pass2runner.main(
        [
            "--pack",
            str(RESULTS / "pass2_r2_pack_think_smoke.json"),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--serving",
            "READER_THINK",
        ],
        loader=lambda *a, **kw: Client(),
    )
    assert code == 0
    out = tmp_path / "pass2_signals_r2_remainder.READER_THINK.jsonl"
    (row,) = [
        json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()
    ]
    assert row["reply"] == BRACED_THOUGHT + VERDICT
    assert row["cut_chars"] == len(" and then it kept writing {")
    assert row["thought_chars"] == len(BRACED_THOUGHT)


def test_a_length_cut_thought_is_never_persisted_as_a_balanced_answer(tmp_path):
    """The other half of the same rule, on the rows where the stop by definition never fired.

    A `length` cut-off in this configuration is an UNCLOSED thought, and the reviewer's finding is
    that `run` read it with `split_thought` alone: no closer, so the whole working-out was handed to
    `balanced_prefix` as if it were the answer, the object the model reasoned about balanced, and
    the row went to disk `balanced: True` with the thought TRUNCATED at that brace and
    `thought_chars: 0`. Both readings are wrong in the same direction — a parse failure filed as an
    answer — and the thought-length distribution is a registered reading, so the row must carry
    every character it spent ([[the_empty_class_eats_the_parse_failures]]).
    """
    unclosed = BRACED_THOUGHT[: BRACED_THOUGHT.index(CLOSE)]
    assert reader_v5.balanced_prefix(unclosed) is not None, (
        "the premise: this thought DOES balance an object, so the shipped rule would have cut here"
    )

    class Client:
        def read(self, task, items):
            return [
                {
                    "content": unclosed,
                    "finish_reason": "length",
                    "cost": 0.0,
                    "usage": {"prompt_tokens": 11, "completion_tokens": 8000},
                    "generation_id": None,
                    "thought": "The answer should be …",
                    "thought_tokens": 8000,
                }
            ]

    code = pass2runner.main(
        [
            "--pack",
            str(RESULTS / "pass2_r2_pack_think_smoke.json"),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--serving",
            "READER_THINK",
        ],
        loader=lambda *a, **kw: Client(),
    )
    assert code == 0
    out = tmp_path / "pass2_signals_r2_remainder.READER_THINK.jsonl"
    (row,) = [
        json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()
    ]
    assert row["balanced"] is False, "an unclosed thought carries no answer to balance"
    assert row["cut_chars"] == 0 and row["reply"] == unclosed, "nothing may be trimmed off it"
    assert row["thought_chars"] == row["emitted_chars"] == len(unclosed)
    assert row["thought_chars"] > 0, "the registered reading is the LENGTH of the working-out"
    assert row["finish_reason"] == "length"


def test_one_rule_answers_the_stop_and_the_persistence(tmp_path):
    """The control on the test above: it must fail because the RULE is missing, not because a
    literal in `run` was tightened. Both callers read `thought_and_answer`, so the state the stop
    refuses to fire in is the same state the row is written from
    ([[two_values_for_one_input_get_quoted_kindly]])."""
    unclosed = BRACED_THOUGHT[: BRACED_THOUGHT.index(CLOSE)]
    thought, answer = runner.thought_and_answer(unclosed, prompts)
    assert (thought, answer) == (unclosed, None)
    assert runner.stops_here(unclosed, prompts, reader_v5) is False
    assert runner.thought_and_answer(VERDICT, prompts) == ("", VERDICT), "shipped path: identity"
    assert runner.thought_and_answer(BRACED_THOUGHT + VERDICT, prompts) == (
        BRACED_THOUGHT,
        VERDICT,
    )
    assert "thought_and_answer" in inspect.getsource(runner.run), (
        "`run` must read the rule, not a second copy of it"
    )


def test_the_holdout_pack_is_the_hundred_rows_the_before_column_answered():
    """The holdout is a hundred LABELS, not a pack, and its v2 column is TWO reply files — 88 rows
    from the r2 window and 12 from r1, disjoint. Each item comes from the pack that answered it, so
    the thinking column is over the same rendered request ([[trace_the_producer_not_the_result]])."""
    pack = THINK_PACKS["pass1_holdout_100_think.json"]
    (leg,) = pack["legs"]
    units = json.loads((RESULTS / "pass1_holdout_100.json").read_text(encoding="utf-8"))["units"]
    assert len(leg["items"]) == len(units) == 100
    assert {(one["thread"], int(one["msg_id"])) for one in leg["items"]} == {
        (one["thread"], int(one["msg_id"])) for one in units
    }
    answered = pack["before_column"]["answered_by"]
    counted = {
        name: sum(1 for one in answered.values() if one == name) for name in set(answered.values())
    }
    assert counted == {
        "results/pass1_window_r2_v2.jsonl": 88,
        "results/pass1_window_v2.jsonl": 12,
    }


# --- the registration and the measurement ledger ---------------------------------------------------


#: The files this registration PINS that `think-zero-shot-d2` step 0 ordered moved, each with the
#: witness that says the move happened rather than a rename: STATUS gained the §6t row the D2
#: contract exists to fill, the runner gained the unclosed-thought rule.
MOVED_BY_D2_STEP_0 = {
    "docs/STATUS.md": "D1 (\u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442, $0)",
    "scripts/reader_v5_pod_runner.py": "def thought_and_answer",
}


def test_the_registration_rebuilds_except_where_step_0_moved_a_pin():
    """The record is what its producer emits from the files it names — except at the two pins that
    D2's own step 0 moved, and a registration is NEVER re-pinned.

    Both moves are this contract's order: `docs/STATUS.md` (§6t, committed by path) and
    `scripts/reader_v5_pod_runner.py` (the `length`-cut fix above). The allowance is DERIVED from
    which paths carry each file's live sha and asserted in BOTH directions — a record that moved
    anywhere else fails, and an allowance that has gone stale fails too. The packs the pod actually
    reads pin `prompts.py`, `pass2.py` and `pass2_r2.py`, none of which moved, so the handshake on
    the pod is unaffected ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    import write_think_zero_shot_prereg as producer

    shipped = json.loads((RESULTS / producer.OUT_NAME).read_text(encoding="utf-8"))
    rebuilt = producer.build(RESULTS)
    expected: set[str] = set()
    for name, witness in MOVED_BY_D2_STEP_0.items():
        path = REPO_ROOT / name
        assert witness in path.read_text(encoding="utf-8"), f"{name} does not carry D2's own change"
        here = moved_pins.paths_holding(rebuilt, moved_pins.live_sha(path))
        assert here, f"no path in the rebuild carries {name}'s live sha — the check is vacuous"
        assert not here & moved_pins.paths_holding(shipped, moved_pins.live_sha(path)), (
            f"{name} has NOT moved since the seal — this allowance is stale, drop it"
        )
        expected |= here
    assert set(prereg_b.moved_paths(shipped, rebuilt, opaque=())) == expected


def test_what_the_pod_reads_did_not_move():
    """The positive half of the test above: the six packs are addressed by sha in the record and
    their parser is what every handshake refuses on. A step-0 fix that reached either would make
    every stage refuse before the model is loaded — at full pod price."""
    record = json.loads((RESULTS / "prereg_think_zero_shot.json").read_text(encoding="utf-8"))
    for stage in record["stages"]:
        assert moved_pins.live_sha(RESULTS / Path(stage["pack"]).name) == stage["sha256"], (
            f"{stage['pack']} moved — stage {stage['order']} would refuse on the pod"
        )
    for name in ("src/market_pulse/prompts.py", "src/market_pulse/pass2_r2.py"):
        assert record["instrument"]["shas"][name] == moved_pins.live_sha(REPO_ROOT / name)


def test_every_before_number_is_derived_and_the_contract_agrees_with_it():
    """The BEFORE column is the half of a paired table nobody re-measures, so it is the half a
    transcription error survives in. Each is recomputed and the contract's own citation is the
    CHECK, never the source ([[a_number_typed_into_its_own_checker]])."""
    record = json.loads((RESULTS / "prereg_think_zero_shot.json").read_text(encoding="utf-8"))
    before = record["before_columns"]
    assert (before["dev_200"]["base"]["agreed"], before["dev_200"]["base"]["our_agreed"]) == (
        87,
        31,
    )
    assert (before["dev_200"]["v2"]["agreed"], before["dev_200"]["v2"]["our_agreed"]) == (136, 38)
    assert before["dev_200"]["base"]["n"] == before["dev_200"]["v2"]["n"] == 200
    assert before["dev_200"]["base"]["our_n"] == 49
    assert (before["holdout_100"]["agreed"], before["holdout_100"]["n"]) == (64, 100)
    assert before["pass_2"]["1_flagships"]["cases_answered"] == 4
    assert before["pass_2"]["2_entity_cases"]["cases_answered"] == 3
    assert before["pass_2"]["3_noise"]["passed"] is False


def test_a_moved_transcription_is_refused():
    """The negative control on the test above: `agrees` has to FIRE, not merely be called."""
    import write_think_zero_shot_prereg as producer

    assert producer.agrees("x", 5, 5) == 5
    with pytest.raises(SystemExit, match="the files say"):
        producer.agrees("x", 5, 6)


def test_the_registration_registers_no_bar():
    """«Readings, not bars»: a threshold in this record would be a verdict the operator did not ask
    for. The words are the contract's own and are grepped back into it."""
    record = json.loads((RESULTS / "prereg_think_zero_shot.json").read_text(encoding="utf-8"))
    assert "bars" not in record and "gate" not in record
    assert "READINGS, not bars" in record["what_this_is"]
    assert record["money"]["cap_usd"] == 8.00
    assert len(record["money"]["rungs"]) == 4
    assert len(record["stages"]) == 7


def test_a_measurement_without_a_source_is_refused(tmp_path):
    import measurements

    ledger = tmp_path / "measurements.jsonl"
    good = {
        "name": "x",
        "value": 1.0,
        "unit": "seconds",
        "source": "results/x.jsonl",
        "measured_on": "n = 1",
        "contract": "think-zero-shot",
    }
    assert measurements.append(good, ledger) == good
    for field in measurements.REQUIRED:
        with pytest.raises(ValueError, match=field):
            measurements.append({**good, field: None}, ledger)
    assert len(measurements.rows(ledger)) == 1, "a refused row is not written"


def test_the_seeded_rates_are_the_reply_files_own(tmp_path):
    """The committed ledger against what the reply files say TODAY — read-only on `results/`.

    `seed()` is driven into a temp ledger and never against the tracked one: a test that appends to
    a file under `results/` is a test that writes during the verifier, which is the move
    `make check-stamped` exists to catch ([[a_gate_command_is_a_write]]).
    """
    import measurements

    on_disk = {one["name"]: one for one in measurements.rows()}
    derived = measurements.derive("think-zero-shot")
    for row in derived:
        assert on_disk[row["name"]] == row, f"{row['name']} on disk is not what the files say today"
    ledger = tmp_path / "measurements.jsonl"
    assert len(measurements.seed("think-zero-shot", ledger)) == len(derived)
    assert measurements.seed("think-zero-shot", ledger) == [], "seeding twice adds nothing"
    assert len(measurements.rows(ledger)) == len(derived)


# --- rung 2: the projection that fires seven times on a live clock ---------------------------------


RECORD = json.loads((RESULTS / "prereg_think_zero_shot.json").read_text(encoding="utf-8"))


def ledger_of(tmp_path: Path, **rates: float) -> Path:
    path = tmp_path / "measurements.jsonl"
    path.write_text(
        "".join(
            json.dumps({"name": name, "value": value, "unit": "seconds"}) + "\n"
            for name, value in rates.items()
        ),
        encoding="utf-8",
    )
    return path


def test_the_projection_prices_the_smokes_thread_once(tmp_path):
    """THE money check. Stage 1 buys the longest thread and writes it into the REMAINDER's out-file
    — `already_answered` will not re-ask it at stage 7, so a projection that charges 68 there is
    charging for a unit the pod will never generate. The same holds for the three dev rows against
    stage 3's 200 ([[check_the_step_was_not_already_done]])."""
    run = tmp_path / "run"
    run.mkdir()
    (run / "pass2_signals_r2_remainder.READER_THINK.jsonl").write_text(
        json.dumps({"id": "@mandziak:3679"}) + "\n", encoding="utf-8"
    )
    (run / "pass1_dev_v2.READER_THINK.jsonl").write_text(
        "".join(json.dumps({"id": f"row{n}"}) + "\n" for n in range(3)), encoding="utf-8"
    )
    rows = projector.plan(
        RECORD,
        run,
        projector.rates(ledger_of(tmp_path, **dict.fromkeys(projector.RATE_OF.values(), 10.0))),
        load_seconds=0,
    )
    owed = {row["order"]: row["units"] for row in rows}
    assert 1 not in owed and 2 not in owed, "both smokes are answered — they are not owed again"
    assert owed == {3: 197, 4: 11, 5: 200, 6: 100, 7: 67}
    assert sum(owed.values()) == 575


def test_nothing_is_owed_twice_when_the_run_directory_is_empty(tmp_path):
    """The control: with nothing answered, the seven stages are the 579 renderings the packs carry
    — and stages 3 and 5 share two out-files, so a plan that double-counted them would say more."""
    rows = projector.plan(
        RECORD,
        tmp_path,
        projector.rates(ledger_of(tmp_path, **dict.fromkeys(projector.RATE_OF.values(), 1.0))),
        load_seconds=0,
    )
    assert sum(row["units"] for row in rows) == 579
    assert [row["order"] for row in rows] == [1, 2, 3, 4, 5, 6, 7]


def test_a_rate_the_smoke_has_not_measured_refuses_to_be_projected(tmp_path):
    """A remembered number is not a prior. The 97 s/thread error of 26.08 was exactly this: a rate
    quoted from memory priced a stage 4.1x wrong ([[projected_rate_versus_measured_rate]])."""
    rows = projector.plan(RECORD, tmp_path, {}, load_seconds=0)
    assert all(row["rate"] is None for row in rows)
    with pytest.raises(SystemExit, match="is not in the ledger"):
        projector.project(RECORD, rows, usd_per_hour=0.79, elapsed=0)


@pytest.mark.parametrize(
    "pass1, pass2, verdict",
    [(10.0, 60.0, "GO"), (30.0, 200.0, "GO"), (40.0, 250.0, "ASK"), (90.0, 600.0, "KILL")],
)
def test_the_verdict_bands_are_the_records_own_rung(tmp_path, pass1, pass2, verdict):
    """GO at or under the cap, ASK within 20% over it, KILL beyond — and the band is read off the
    record's `cap_usd`, never a literal here."""
    rows = projector.plan(
        RECORD,
        tmp_path,
        projector.rates(
            ledger_of(
                tmp_path,
                think_pass1_seconds_per_call=pass1,
                think_pass2_seconds_per_thread=pass2,
            )
        ),
        load_seconds=60,
    )
    out = projector.project(RECORD, rows, usd_per_hour=0.79, elapsed=1800)
    assert out["cap_usd"] == RECORD["money"]["cap_usd"] == 8.0
    assert out["verdict"] == verdict
    assert (out["projected_usd"] <= out["cap_usd"]) is (verdict == "GO")


def test_stop_after_names_the_last_stage_that_fits_under_the_cap(tmp_path):
    """A KILL verdict on the whole programme is not the decision — the decision is where to stop,
    and the value order IS the drop order. `stop_after_stage` is that number, and it is None when
    even the first stage does not fit."""
    rows = projector.plan(
        RECORD,
        tmp_path,
        projector.rates(
            ledger_of(
                tmp_path,
                think_pass1_seconds_per_call=90.0,
                think_pass2_seconds_per_thread=600.0,
            )
        ),
        load_seconds=60,
    )
    out = projector.project(RECORD, rows, usd_per_hour=0.79, elapsed=1800)
    fits = [row for row in out["table"] if row["cumulative_usd"] <= out["cap_usd"]]
    assert out["stop_after_stage"] == fits[-1]["order"]
    assert out["table"][len(fits)]["cumulative_usd"] > out["cap_usd"], "the next one does not fit"

    broke = projector.project(RECORD, rows, usd_per_hour=0.79, elapsed=8.0 * 3600 / 0.79)
    assert broke["stop_after_stage"] is None and broke["verdict"] == "KILL"
