"""`results/prereg_reader_probe_v5.json` — the v5 registration, checked before it can be spent.

Two legs and a raised ceiling, so this file checks exactly those three things and the split between
them: what is COPIED from v4 is asserted object-equal, what is RE-DERIVED is recomputed here, leg B
is held to the census it came out of, and the ceiling's arithmetic is redone from reader-v4's own
rows. The claims a reader cannot check by eye — that the raised ceiling is above the pessimistic
corner and that 2 000 would have made a bar unreachable, that leg B's three parts are a partition of
the 43 payable ids, and what the cap buys in SECONDS — are computed rather than read.
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_census_w1_reader as reader_cell  # noqa: E402
import probe_b_population as subset  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v5 as prereg  # noqa: E402

from market_pulse import prompts, reader_v5  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
V4 = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v4.json").read_text(encoding="utf-8"))
V4_ROWS = [
    json.loads(line)
    for line in (REPO_ROOT / "results" / "reader_v4_w1.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if line
]


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is the only witness that it preceded the pod."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


# --- what is copied, and what is re-derived ------------------------------------------------------


def test_the_instrument_is_RE_DERIVED_and_names_the_four_things_that_moved():
    """The inverse of v4's rule. A copied `instruments` block would be false in four places."""
    instruments = RECORD["instruments"]
    assert instruments["task"] == prompts.READER_TASK_V5 == "reader_thread_gm4_v5"
    assert instruments["prompt_sha256"] == {
        task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)
    }
    assert len(instruments["prompt_sha256"]) == 4
    assert "reader_thread_gm4_v4" not in instruments["prompt_sha256"]
    # the three v1/v2/v3 pins are the SAME numbers v4 registered — the older texts did not move
    for task in ("reader_thread_gm4", "reader_thread_gm4_v2", "reader_thread_gm4_v3"):
        assert instruments["prompt_sha256"][task] == V4["instruments"]["prompt_sha256"][task]
    assert instruments["parser"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "prompts.py"
    )
    assert instruments["parser"]["v5_additions"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "reader_v5.py"
    )
    assert instruments["ceilings"]["output_tokens"] == prereg.OUTPUT_CEILING == 4000
    assert set(instruments["v5_changes"]) == {
        "prompt",
        "transport",
        "render",
        "parser",
        "ceiling",
    }


def test_what_is_copied_is_copied_OBJECT_EQUAL_and_the_scorer_never_moved():
    """«Unchanged» is object equality with the frozen record, not a re-derivation that agrees
    today and is free to disagree tomorrow."""
    assert RECORD["instruments"]["gold"] == V4["instruments"]["gold"]
    assert RECORD["instruments"]["scorer"] == V4["instruments"]["scorer"]
    assert RECORD["scoring_rules"] == V4["scoring_rules"]
    for name in ("1_flagships", "2_entity_cases", "3_noise", "4_per_comment_agreement"):
        assert RECORD["bars"][name] == V4["bars"][name], name
    # the scorer's bytes really are still the registered ones — nothing in this contract touched it
    assert RECORD["instruments"]["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
    # serving is v4's plus exactly one key
    assert RECORD["instruments"]["serving"] == V4["instruments"]["serving"] | {
        "output_tokens": 4000
    }
    assert set(RECORD["instruments"]["serving"]) - set(V4["instruments"]["serving"]) == {
        "output_tokens"
    }


def test_the_serving_block_carries_the_ceiling_so_the_runner_cannot_default_to_2000():
    """A ceiling registered in a record and never passed to the client is a ceiling nobody lifted.
    The pack copies `instruments.serving`, so the field has to be IN it."""
    assert RECORD["instruments"]["serving"]["output_tokens"] == 4000
    from market_pulse import local_llm

    assert local_llm.READER_MAX_NEW_TOKENS == 2000, "the default the runner must not silently take"


# --- leg A ---------------------------------------------------------------------------------------


def test_leg_a_keeps_the_digest_and_RE_DERIVES_every_rendering():
    """The pairing three runs rest on is the digest, and it is over the threads and their payable
    ids — it carries no rendering, so it does not move when the prompt does. The per-thread request
    shas DO move and must: the same thread under a different instrument is a different request."""
    leg_a = RECORD["population"]["leg_a"]
    assert leg_a["enumeration"]["digest"] == V4["population"]["enumeration"]["digest"]
    assert leg_a["enumeration"]["digest"] == subset.digest(subset.population())
    assert (leg_a["threads"], leg_a["payable_comments"]) == (23, 134)

    v4_shas = {
        one["thread"]: one["rendering_sha256"] for one in V4["population"]["enumeration"]["threads"]
    }
    kept = {subset.key(one["channel"], one["post_id"]): one for one in subset.population()}
    moved = 0
    for one in leg_a["enumeration"]["threads"]:
        thread = kept[one["thread"]]
        content = prompts.reader_messages_gm4(
            thread["channel"],
            thread["post_id"],
            thread["post_text"],
            [(row["msg_id"], row["text"]) for row in thread["comments"]],
            task=prompts.READER_TASK_V5,
        )[0]["content"]
        assert one["rendering_sha256"] == hashlib.sha256(content.encode()).hexdigest(), one[
            "thread"
        ]
        assert one["rendered_chars"] == len(content)
        moved += one["rendering_sha256"] != v4_shas[one["thread"]]
        # and no chunk header reached leg A: these are whole threads
        assert "<part>" not in content, one["thread"]
    assert moved == 23, "every leg-A request moved, because the instrument did"


def test_no_leg_a_thread_renders_over_the_input_ceiling_under_the_longer_text():
    leg_a = RECORD["population"]["leg_a"]
    largest = max(one["rendered_chars"] for one in leg_a["enumeration"]["threads"])
    assert largest < prompts.READER_MAX_INPUT_CHARS
    # v5's text is ~3 200 characters longer than v3's, and the ceiling is a LOUD refusal
    v4_largest = max(one["rendered_chars"] for one in V4["population"]["enumeration"]["threads"])
    assert largest > v4_largest


# --- leg B ---------------------------------------------------------------------------------------


def test_leg_b_is_one_thread_out_of_the_census_and_never_a_typed_list():
    leg_b = RECORD["population"]["leg_b"]
    live = {
        subset.key(one["channel"], one["post_id"]): [row["msg_id"] for row in one["comments"]]
        for one in reader_cell.population()
    }
    assert leg_b["thread"] == prereg.LEG_B_THREAD == "@klopotenkofood:6040"
    assert leg_b["msg_ids"] == live[leg_b["thread"]]
    assert leg_b["payable_comments"] == len(leg_b["msg_ids"]) == 43
    assert leg_b["source"]["sha256"] == summary.sha256_of(reader_cell.OUT)
    assert leg_b["source"]["cell"] == reader_cell.CELL


def test_the_three_parts_are_a_PARTITION_of_the_43_payable_ids():
    """m1 is exactly this claim about the answer; here it is checked about the REQUEST, which is
    the half that has to be true before anything is sent."""
    leg_b = RECORD["population"]["leg_b"]
    parts = [one["msg_ids"] for one in leg_b["items"]]
    assert [len(one) for one in parts] == leg_b["chunks"] == [16, 16, 11]
    flat = [msg_id for one in parts for msg_id in one]
    assert flat == leg_b["msg_ids"], "in order, and every id exactly once"
    assert len(set(flat)) == len(flat) == 43
    assert parts == reader_v5.chunks(leg_b["msg_ids"], prereg.LEG_B_CHUNK)


def test_every_chunk_request_re_renders_to_its_pinned_sha_with_its_own_header():
    leg_b = RECORD["population"]["leg_b"]
    thread = next(
        one
        for one in reader_cell.population()
        if subset.key(one["channel"], one["post_id"]) == leg_b["thread"]
    )
    texts = {row["msg_id"]: row["text"] for row in thread["comments"]}
    for item in leg_b["items"]:
        index, total = item["part"]
        content = prompts.reader_messages_gm4(
            thread["channel"],
            thread["post_id"],
            thread["post_text"],
            [(msg_id, texts[msg_id]) for msg_id in item["msg_ids"]],
            task=prompts.READER_TASK_V5,
            part=(index, total),
        )[0]["content"]
        assert item["rendering_sha256"] == hashlib.sha256(content.encode()).hexdigest(), item["id"]
        assert f"<part>частина {index} з {total}</part>" in content
        assert content.count("<part>") == 1
        assert len(content) < prompts.READER_MAX_INPUT_CHARS
        # every id of this part is in this request and no id of another part is
        for msg_id in leg_b["msg_ids"]:
            assert (f'<comment msg_id="{msg_id}">' in content) is (msg_id in item["msg_ids"])


def test_the_thread_did_not_NEED_chunking_and_the_record_says_so():
    """A registration that let this read as a necessity would be teaching the next contract the
    wrong lesson: the mechanism is what is being bought, before the window's giants use it."""
    whole = RECORD["population"]["leg_b"]["renders_whole_under_the_ceiling"]
    assert whole["chars"] < whole["ceiling"] == prompts.READER_MAX_INPUT_CHARS
    assert "does NOT need chunking" in whole["reading"]


def test_leg_b_has_its_OWN_digest_and_cannot_be_folded_into_leg_as():
    leg_b = RECORD["population"]["leg_b"]
    line = "\n".join(
        f"{leg_b['thread']}\t{one['part'][0]}of{one['part'][1]}\t"
        + ",".join(str(msg_id) for msg_id in one["msg_ids"])
        for one in leg_b["items"]
    )
    assert leg_b["digest"] == hashlib.sha256(line.encode()).hexdigest()
    assert leg_b["digest"] != RECORD["population"]["leg_a"]["enumeration"]["digest"]
    # and the thread is not one of leg A's, so no row can be in both
    assert leg_b["thread"] not in {
        one["thread"] for one in RECORD["population"]["leg_a"]["enumeration"]["threads"]
    }


def test_the_mechanical_bars_read_no_gold_and_say_they_cannot_touch_leg_a():
    mechanical = RECORD["bars"]["leg_b_mechanical"]
    assert sorted(name for name in mechanical if name.startswith("m")) == [
        "m1_every_payable_id_exactly_once",
        "m2_every_chunk_finished",
        "m3_every_chunk_parses",
        "m4_the_merge_has_no_duplicate_signal",
    ]
    # over the four bars THEMSELVES: the `cannot_touch_leg_a` sentence names what they may not read,
    # so grepping it would be grepping the prohibition instead of the rules
    body = json.dumps(
        {name: block for name, block in mechanical.items() if name.startswith("m")},
        ensure_ascii=False,
    )
    for forbidden in ("reader_gold", "flagship", "REFERENCE-signals", "категория", "субъект"):
        assert forbidden not in body, forbidden
    assert "never enter bars 1-4" in mechanical["cannot_touch_leg_a"]
    assert (
        mechanical["m1_every_payable_id_exactly_once"]["threshold"]
        == "43 of 43, 0 extra, 0 duplicated"
    )
    assert mechanical["m4_the_merge_has_no_duplicate_signal"]["rule"].count("signal_type") == 1


# --- the ceiling ---------------------------------------------------------------------------------


def test_the_raised_ceiling_clears_the_pessimistic_corner_and_2000_would_not():
    """The reachability reading m2 needs. At 2 000 a 16-row chunk's pessimistic answer is over the
    ceiling, so the bar fails by arithmetic before the model is asked
    ([[an_absolute_bar_needs_a_reachability_state]])."""
    ceilings = RECORD["instruments"]["ceilings"]["output_arithmetic"]
    model = ceilings["model"]
    assert ceilings["registered"] == 4000 and ceilings["superseded"] == 2000

    def pessimistic(rows: int) -> float:
        return (
            model["envelope_tokens"]
            + model["largest_residual_tokens"]
            + model["tokens_per_row"] * rows
        )

    worst = max(one["pessimistic_tokens"] for one in ceilings["units"])
    assert worst == round(pessimistic(16))
    assert 2000 < worst < 4000
    assert ceilings["units_over_2000"] == sum(
        1 for one in ceilings["units"] if one["pessimistic_tokens"] > 2000
    )
    assert ceilings["units_over_2000"] >= 1, "otherwise the ceiling did not need to move"
    # every unit of the run is priced, both legs, and every one of them fits the raised ceiling
    assert len(ceilings["units"]) == 23 + 3
    assert all(one["pessimistic_tokens"] < 4000 for one in ceilings["units"])


def test_the_output_model_is_fitted_on_v4s_own_rows_and_can_be_recomputed():
    """The one number this producer computes rather than carries, recomputed here from the paid
    evidence so «from v4's own rows» is checkable."""
    model = RECORD["instruments"]["ceilings"]["output_arithmetic"]["model"]
    rows = [row for row in V4_ROWS if row["parsed"] and not row["parsed"]["noise"]]
    points = [
        (
            len(row["parsed"]["per_comment"]),
            int((row.get("usage") or {}).get("completion_tokens") or 0),
        )
        for row in rows
    ]
    n = len(points)
    sx, sy = sum(x for x, _ in points), sum(y for _, y in points)
    sxx, sxy = sum(x * x for x, _ in points), sum(x * y for x, y in points)
    marginal = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    envelope = (sy - marginal * sx) / n
    assert model["fitted_on"] == n == 14
    assert model["tokens_per_row"] == round(marginal, 2)
    assert model["envelope_tokens"] == round(envelope, 1)
    assert model["largest_residual_tokens"] == round(
        max(y - (envelope + marginal * x) for x, y in points), 1
    )


def test_v4s_largest_reply_really_was_against_the_old_ceiling():
    """The fact that makes «it never fired» not the same as «it had room»."""
    largest = max(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in V4_ROWS)
    assert largest == 1946
    assert largest / 2000 > 0.97
    assert all(row.get("finish_reason") != "length" for row in V4_ROWS)


# --- the money -----------------------------------------------------------------------------------


def test_the_cap_is_a_stopwatch_and_every_leg_is_hand_computable():
    meter, sums = RECORD["money"]["meter"], RECORD["money"]["arithmetic"]
    assert RECORD["money"]["cap_usd_all_in"] == 0.45
    assert meter["worked_example_usd_per_hour"] == 0.74
    assert "EXAMPLE and not the meter" in meter["worked_example_rule"]
    assert "READ ON THE DAY" in meter["price_rule"] and "Dv448" in meter["price_rule"]
    assert sums["seconds_the_cap_buys"] == round(0.45 * 3600 / 0.74, 3)
    assert sums["usable_seconds"] == round(sums["seconds_the_cap_buys"] - 60.0, 3)
    assert sums["reading_projection_seconds"] == round(
        sums["leg_a"]["projection_seconds"] + sums["leg_b"]["projection_seconds"], 1
    )


def test_leg_as_projection_is_the_pessimistic_of_the_floor_and_the_token_model():
    sums = RECORD["money"]["arithmetic"]
    v4 = RECORD["completeness"]["v4_baseline"]
    floor = round(v4["seconds_per_thread"] * 23, 1)
    assert sums["leg_a"]["floor_seconds"] == floor == 907.6
    assert sums["leg_a"]["projection_seconds"] >= floor
    assert sums["leg_a"]["projection_seconds"] == round(
        max(
            floor * sums["leg_a"]["growth_vs_v4"],
            sums["leg_a"]["projected_tokens"] / v4["tokens_per_second_slowest_thread"],
        ),
        1,
    )
    # probe-b's 31.6376 s a thread is explicitly NOT the floor any more
    assert "31.6376" in sums["v4_measured"]["rule"]


def test_leg_bs_projection_uses_the_contracts_own_rate_on_the_right_denominator():
    """137.83 and not 167.9: the per-row rate is over the PARSED threads' tokens. Getting the
    denominator wrong here over-prices leg B by 22% and is invisible in the result
    ([[the_fix_widened_the_denominator]])."""
    v4 = RECORD["completeness"]["v4_baseline"]
    assert v4["tokens_per_requested_row"] == 137.83
    assert v4["completion_tokens_over_parsed_threads"] == 15299 < v4["completion_tokens"] == 18637
    sums = RECORD["money"]["arithmetic"]["leg_b"]
    assert sums["tokens_by_the_contracts_rule"] == round(137.83 * 43)
    assert sums["projection_seconds"] == round(
        max(sums["tokens_by_the_contracts_rule"], sums["tokens_by_the_row_model"])
        / v4["tokens_per_second_slowest_thread"],
        1,
    )
    assert "ESTIMATE with its own gate" in sums["estimate_not_a_measurement"]


def test_the_affordability_deadline_binds_before_the_twelve_minute_ceiling():
    """A negative pre-generation budget is a legal state and it says exactly this: the contract's
    twelve minutes never gets to be the binding number on this registration."""
    sums = RECORD["money"]["arithmetic"]
    assert sums["affordability_deadline_as_create_elapsed"] == round(
        sums["usable_seconds"] - sums["reading_projection_seconds"], 1
    )
    assert sums["affordability_deadline_as_create_elapsed"] < sums["boot_kill_seconds"]
    assert sums["pre_generation_budget_seconds"] < 0
    assert "NEGATIVE" in sums["pre_generation_rule"]
    assert "NOT an elapsed" in sums["pre_generation_rule"]


def test_the_boot_table_is_worked_at_the_measured_pre_generation_and_names_where_it_stops_fitting():
    sums = RECORD["money"]["arithmetic"]
    usable, projection = sums["usable_seconds"], sums["reading_projection_seconds"]
    assert sums["pre_generation_measured_v4_seconds"] == 39.0
    table = {row["boot_seconds"]: row for row in sums["at_each_boot"]}
    assert sorted(table) == [180.0, 300.0, 480.0, 600.0, 720.0]
    for boot, row in table.items():
        left = usable - 39.0 - boot
        assert row["seconds_left_for_reading"] == round(left, 1)
        assert row["fits"] is (left >= projection)
    # the run fits at v4's own boot and does NOT at the twelve-minute ceiling — which is what the
    # kill rule is for, and a table that fitted everywhere would be pricing nothing
    assert table[180.0]["fits"] and not table[720.0]["fits"]
    assert all(row["all_in_usd_at_the_example"] <= 0.46 for row in table.values())


def test_the_runaway_corner_is_priced_and_handed_to_the_gate_not_to_the_ceiling():
    corner = RECORD["money"]["arithmetic"]["runaway_corner"]
    slow = RECORD["completeness"]["v4_baseline"]["tokens_per_second_slowest_thread"]
    assert corner["leg_b_seconds"] == round(3 * 4000 / slow, 1)
    assert corner["leg_a_seconds"] == round(23 * 4000 / slow, 1)
    assert corner["leg_a_seconds"] > RECORD["money"]["arithmetic"]["usable_seconds"]
    assert "re-checked after every unit" in corner["rule"]


# --- the rules that bind the reading of the result ------------------------------------------------


def test_the_programme_stop_rule_is_PRE_registered():
    """It binds the reading of this run's own result, so it cannot be written after the numbers."""
    rule = RECORD["programme_stop_rule"]
    assert "bars 1 and 4 are not BOTH taken" in rule
    assert "prompt-engineering" in rule and "CLOSES" in rule
    assert "never a v6" in rule
    assert RECORD["attempt"] == V4["attempt"]


def test_completeness_is_reported_and_never_a_bar():
    completeness = RECORD["completeness"]
    assert "NEVER gating bars 1-4" in completeness["rule"]
    assert completeness["scorer"] == "market_pulse.reader_v5.echo"
    assert completeness["v4_baseline"]["per_comment_rows_returned"] == 93
    # THREE numbers and they are not the same number — 21 noise rows, 18 ids answered only there,
    # and 3 the reader put in BOTH lists, which the prompt forbids and the parser does not refuse
    assert completeness["v4_baseline"]["noise_rows"] == 21
    assert completeness["v4_baseline"]["answered_only_in_noise"] == 18
    assert completeness["v4_baseline"]["in_both_lists"] == 3
    assert completeness["v4_baseline"]["per_comment_rows_requested"] == 111
    assert "111 of 111" in completeness["v4_baseline"]["union_coverage"]
    assert "ZERO" in completeness["v4_baseline"]["union_coverage"]


def test_the_gates_APPEND_and_the_staging_gate_knows_the_volume_must_move():
    gate = RECORD["go_no_go"]
    assert "LIST" in gate["gate_records_APPEND"] and "appended" in gate["gate_records_APPEND"]
    assert "MUST re-stage" in gate["gates"]["1_staging"]["differs_from_v4"]
    assert gate["gates"]["2_boot_kill"] == V4["go_no_go"]["gates"]["2_boot_kill"]
    assert "PESSIMISTIC" in gate["gates"]["3_the_full_pass"]["rule"]
    assert "leg A first, whole, then leg B" in gate["gates"]["3_the_full_pass"]["order"]
    assert gate["backstop"]["terminate_after_minutes"] == 90


def test_what_freezes_when_the_pod_exists():
    frozen = RECORD["frozen_when_the_pod_exists"]
    assert "results/prereg_reader_probe_v5.json" in frozen
    assert "src/market_pulse/reader_v5.py — the stop, the census and the merge" in frozen
    assert f"the {prompts.READER_TASK_V5} prompt text" in frozen
    assert RECORD["authority"]["docs/PROMPT-reader-v5-prep.md"] == summary.sha256_of(
        REPO_ROOT / "docs" / "PROMPT-reader-v5-prep.md"
    )
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
