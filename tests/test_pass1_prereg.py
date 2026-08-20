"""`results/prereg_pass1_probe.json` and its pack — checked before they can be spent.

The claims this registration lives or dies on are that its population was ENUMERATED rather than
chosen, that the entity context it sends was already bought, that the bar it gates on is reachable
with a loss budget stated in advance, and that the full-pass gate clears over the order the pack is
actually in. Each of them is recomputed here from the same files the producer read — a registration
checked by eye is a registration whose fourth claim nobody verified.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import moved_pins  # noqa: E402
import probe_b_population as subset  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_pass1_prereg as prereg  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_pass1_probe.json"
PACK_PATH = REPO_ROOT / "results" / "pass1_probe_pack.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
PACK = json.loads(PACK_PATH.read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
V5B = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v5b.json").read_text(encoding="utf-8")
)


def test_the_committed_registration_and_pack_are_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so both files re-derive from their own producer and their date is the
    date of the commit that carries them — the only witness that they preceded the first pod.

    The rebuild differs at exactly the paths that pin `src/market_pulse/prompts.py`, whose bytes
    moved when D0.2 registered a second pass-1 text. The registered TEXT did not move, and that is
    what the two attempts are compared through ([[tests/moved_pins.py]]).
    """
    out, pack = tmp_path / "again.json", tmp_path / "pack.json"
    assert prereg.main(["--out", str(out), "--pack", str(pack)]) == 0
    for shipped_path, rebuilt_path in ((RECORD_PATH, out), (PACK_PATH, pack)):
        shipped = json.loads(shipped_path.read_text(encoding="utf-8"))
        rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))
        moved_pins.assert_only_the_prompts_pin_moved(shipped, rebuilt)
        assert shipped["instruments"]["prompt_sha256"] == rebuilt["instruments"]["prompt_sha256"]
    for path in (RECORD_PATH, PACK_PATH):
        assert "generated_at" not in path.read_text(encoding="utf-8")


# --- the population, enumerated -------------------------------------------------------------------


def test_the_gating_rows_are_bar_4s_own_fourteen_and_nothing_was_chosen():
    """Read out of gold r2 the same way the bar reads them, and compared as a SET of (thread, id) —
    a producer that dropped one and added another would agree on the count."""
    wanted = {
        (f"{row['channel']}:{row['evidence_row']['post_id_in_the_store']}", int(row["msg_id"]))
        for row in GOLD["per_comment"]
    }
    got = {(row["thread"], row["msg_id"]) for row in RECORD["population"]["gold"]["rows"]}
    assert got == wanted
    assert RECORD["population"]["gold"]["n"] == len(wanted) == 14
    assert RECORD["population"]["gold"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "results" / "reader_gold_w1_r2.json"
    )


def test_the_census_is_every_OTHER_payable_comment_of_the_same_threads():
    """The census's definition is a set difference over the STORE, so it is recomputed from the
    store — and both halves are asserted: nothing gold leaked in, nothing payable was left out."""
    threads = {f"{one['channel']}:{one['post_id']}": one for one in subset.population()}
    gold = {(row["thread"], row["msg_id"]) for row in RECORD["population"]["gold"]["rows"]}
    wanted = {
        (name, int(comment["msg_id"]))
        for name in RECORD["population"]["threads"]
        for comment in threads[name]["comments"]
        if (name, int(comment["msg_id"])) not in gold
    }
    got = {(row["thread"], row["msg_id"]) for row in RECORD["population"]["census"]["rows"]}
    assert got == wanted
    assert not got & gold, "a gold row is in the census, so the census would carry an answer"
    assert RECORD["population"]["census"]["n"] == len(wanted) == 50
    assert RECORD["population"]["units"] == 64 == 14 + 50
    # and the per-thread table sums to both halves
    per = RECORD["population"]["per_thread"]
    assert sum(one["gold_rows"] for one in per.values()) == 14
    assert sum(one["census_rows"] for one in per.values()) == 50
    assert all(
        one["gold_rows"] + one["census_rows"] == one["payable_comments"] for one in per.values()
    )


def test_the_entity_context_is_already_bought_and_10613_is_the_one_that_comes_from_v4():
    """The contract's routing, asserted per thread rather than described: six threads from v5b's
    verdicts and `@VARUS_channel:10613` from v4's, because v5b REFUSED it."""
    context = RECORD["population"]["entity_context"]
    assert set(context) == set(RECORD["population"]["threads"]) and len(context) == 7
    from_v4 = sorted(
        name for name, one in context.items() if one["source"] == "results/reader_v4_w1.jsonl"
    )
    assert from_v4 == ["@VARUS_channel:10613"]
    assert all(
        one["source"] == "results/reader_v5b_w1.jsonl"
        for name, one in context.items()
        if name not in from_v4
    )
    for one in context.values():
        assert one["sha256"] == summary.sha256_of(REPO_ROOT / one["source"])
    # the premise of the routing: v5b really did refuse that thread, and v4 really did parse it
    refused = {
        f"{row['channel']}:{row['post_id']}"
        for row in _rows("results/reader_v5b_w1.jsonl")
        if not row.get("parsed")
    }
    assert "@VARUS_channel:10613" in refused
    assert context["@VARUS_channel:10613"]["entities"] == 10
    # an entity block may legitimately be EMPTY, and one of the seven is
    assert context["@mandziak:3703"]["entities"] == 0


def _rows(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (REPO_ROOT / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# --- the bar, and what it can afford to lose ------------------------------------------------------


def test_bar_P1_states_its_threshold_and_the_loss_budget_that_follows_from_it():
    """«≥12 of 14» tolerates exactly two losses, and a refusal costs the same as a disagreement.
    Registered BEFORE the run so the result cannot be re-read against a budget nobody wrote."""
    bar = RECORD["bars"]["P1_per_comment_agreement"]
    assert bar["gating"] is True
    assert bar["n"] == 14 and bar["minimum_agreed"] == 12
    assert bar["loss_budget"]["rows_that_may_be_lost"] == 2 == bar["n"] - bar["minimum_agreed"]
    assert "ABSENT" in bar["loss_budget"]["rule"]
    # the thread that carries the most gold rows is the largest single loss the bar can take
    worst = bar["loss_budget"]["the_thread_that_carries_the_most"]
    per = RECORD["population"]["per_thread"]
    assert per[worst]["gold_rows"] == max(one["gold_rows"] for one in per.values()) == 4
    assert per[worst]["gold_rows"] > bar["loss_budget"]["rows_that_may_be_lost"], (
        "one refused thread would exceed the budget on its own — that fact belongs in the report"
    )
    assert RECORD["bars"]["census"]["gating"] is False


def test_the_bar_borrows_bar_4s_comparison_and_bar_4s_collapse():
    """The contract's «call the registered scorer's comparison, do not restate it» — and the
    collapse map is the one v5b scored under, not a fresh spelling of it."""
    bar = RECORD["bars"]["P1_per_comment_agreement"]
    assert "reader_comment_agreement" in bar["comparison"]
    assert hasattr(__import__("market_pulse.scorer", fromlist=["x"]), "reader_comment_agreement")
    v5b_verdict = json.loads(
        (REPO_ROOT / "results" / "reader_v5b_verdict.json").read_text(encoding="utf-8")
    )
    collapse = v5b_verdict["scoring_rules"]["vocabulary_collapse"]
    assert bar["collapse"]["map"] == collapse["map"]
    assert bar["collapse"]["symmetric"] is collapse["symmetric"] is True
    assert RECORD["instruments"]["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )


# --- the instrument -------------------------------------------------------------------------------


def test_the_instrument_names_the_pass1_text_the_four_readings_and_the_borrowed_serving():
    instruments = RECORD["instruments"]
    assert instruments["task"] == prompts.PASS1_TASK == "pass1_comment_gm4_v1"
    assert instruments["prompt_sha256"] == {
        prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)
    }
    assert instruments["subject_types"] == list(prompts.PASS1_SUBJECT_TYPES)
    assert len(instruments["subject_types"]) == 4
    # The module sha is a «moved since» pin. `docs/PROMPT-pass1-fewshot.md` D0.2 registered a
    # SECOND pass-1 text in prompts.py and ruled old records' pins of it never re-pinned, so this
    # one no longer equals the live module — and what the record MEANS rests on the TEXT sha
    # asserted above, which has not moved ([[the_identity_field_stops_covering_the_change]]).
    assert len(instruments["parser"]["sha256"]) == 64
    assert instruments["parser"]["module"] == "src/market_pulse/prompts.py"
    assert instruments["parser"]["sha256"] != summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "prompts.py"
    ), "prompts.py has not moved, so this «moved since» reading is stale — restore the equality"
    # serving is v5b's block and exactly one key of it moved
    assert instruments["serving"] == V5B["instruments"]["serving"] | {"output_tokens": 256}
    moved = {
        key
        for key in instruments["serving"]
        if instruments["serving"][key] != V5B["instruments"]["serving"].get(key)
    }
    assert moved == {"output_tokens"}
    assert instruments["ceilings"]["input_chars"] == prompts.PASS1_MAX_INPUT_CHARS


def test_the_return_to_sitting_clause_is_registered_and_names_both_options():
    clause = RECORD["return_to_sitting"]
    assert "never to a prompt iteration" in clause
    assert "labelled" in clause and "different base" in clause
    assert "no pass1-v2 prompt" in clause
    assert "ONE attempt" in RECORD["attempt"]
    assert "FREEZES at the FIRST `pod create`" in RECORD["class"]


# --- the money, and the gate solved backwards -----------------------------------------------------


def test_the_registered_per_call_cost_is_a_BOUND_and_not_an_extrapolation():
    """The fitted line would extrapolate below the range it was fitted on; the registered number is
    v5b's own cheapest call, which is heavier than any pass-1 call on both axes."""
    reading = RECORD["money"]["reading"]
    ceiling, fitted = reading["ceiling"], reading["fitted"]
    assert ceiling["gates"] is True
    assert (
        RECORD["money"]["arithmetic"]["seconds_per_call_registered"]
        == (ceiling["seconds_per_pass1_call"])
    )
    assert fitted["seconds_per_pass1_call"] < ceiling["seconds_per_pass1_call"], (
        "the bound has to be the pessimistic one or it is not a bound"
    )
    assert fitted["expected_completion_tokens"] < fitted["fitted_over_completion_tokens"][0]
    # the bound really is heavier than a pass-1 call on BOTH axes
    assert ceiling["completion_tokens"] > fitted["expected_completion_tokens"]
    longest = max(one["rendered_chars"] for one in PACK["items"])
    assert ceiling["prompt_tokens"] * reading["v5b_totals"]["chars_per_completion_token"] > longest
    # and it is a row that exists, at the seconds that row actually took
    row = next(one for one in _rows("results/reader_v5b_w1.jsonl") if one["id"] == ceiling["unit"])
    assert round(float(row["seconds"]["worker"]), 3) == ceiling["seconds_per_pass1_call"]
    assert int(row["usage"]["completion_tokens"]) == ceiling["completion_tokens"]


def test_the_cap_arithmetic_re_derives_and_the_projection_fits_inside_it():
    arithmetic = RECORD["money"]["arithmetic"]
    rate = prereg.CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    assert RECORD["money"]["cap_usd_all_in"] == 0.20
    assert arithmetic["seconds_the_cap_buys"] == round(0.20 / rate, 3)
    assert arithmetic["usable_seconds"] == round(0.20 / rate - 60.0, 3)
    assert arithmetic["units"] == 64
    assert arithmetic["reading_projection_seconds"] == round(
        arithmetic["seconds_per_call_registered"] * 64, 3
    )
    # the budget is POSITIVE, which is the thing v5's $0.45 did not have
    assert arithmetic["pre_generation_budget_seconds"] > 0
    assert arithmetic["affordability_deadline_seconds"] > arithmetic["boot_seconds_charged"]
    assert arithmetic["boot_free_corner_seconds_per_unit"] == round(
        arithmetic["usable_seconds"] / 64, 3
    )


def test_the_full_pass_gate_clears_every_unit_of_the_order_the_pack_is_in():
    """Dv471's method, and the reason it is not optional: v5b's ruled order STOPped at unit 1 and
    the table found it for $0. This one has to clear, and the tightest margin has to be named."""
    table = RECORD["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    assert table["first_stop_after_units"] is None
    assert len(table["per_unit"]) == 64
    assert {one["verdict"] for one in table["per_unit"]} == {"GO"}
    assert table["tightest"]["margin_seconds_per_unit"] > 0
    assert table["tightest"] == min(
        table["per_unit"], key=lambda one: one["margin_seconds_per_unit"]
    )
    # the corner with no provisioning forecast in it
    corner = table["unit_one_without_any_boot"]
    assert corner["clears"] is True
    assert corner["expected_seconds"] < corner["zero_boot_ceiling_seconds"]
    assert corner["unit"] == PACK["items"][0]["id"]
    # and the reason there is no knife-edge to find: the gate's two legs are one leg here
    assert {one["payable_comments"] for one in PACK["items"]} == {1}
    assert {one["binding_leg"] for one in table["per_unit"]} == {"by_unit"}


# --- the pack -------------------------------------------------------------------------------------


def test_the_pack_is_the_population_in_the_stores_own_order_with_gold_interleaved():
    assert len(PACK["items"]) == 64
    assert PACK["task"] == prompts.PASS1_TASK
    assert len({one["id"] for one in PACK["items"]}) == 64
    counts = {"gold": 0, "census": 0}
    for one in PACK["items"]:
        counts[one["leg"]] += 1
    assert counts == {"gold": 14, "census": 50}
    # thread-grouped, in `channel:post_id` order
    order = [one["thread"] for one in PACK["items"]]
    assert order == sorted(order, key=lambda name: RECORD["population"]["threads"].index(name))
    # and inside a thread, the STORE's comment order — not the gold rows first
    threads = {f"{one['channel']}:{one['post_id']}": one for one in subset.population()}
    for name in RECORD["population"]["threads"]:
        mine = [one["msg_id"] for one in PACK["items"] if one["thread"] == name]
        assert mine == [int(one["msg_id"]) for one in threads[name]["comments"]], name
    # «interleaved» is an empty claim unless a census row really does come BEFORE a gold row
    # somewhere: a pack that put the gold rows first would make the gate's opening units
    # unrepresentative of the rest, and would still pass every assertion above
    legs = [one["leg"] for one in PACK["items"]]
    assert legs.index("census") < legs.index("gold")
    assert any(
        legs[start] == "census" and "gold" in legs[start:]
        for start in range(len(legs))
        if legs[start] == "census"
    )


def test_every_pinned_rendering_sha_is_what_the_renderer_produces_from_the_packs_own_fields():
    """The pod renders from these fields and refuses unless its sha matches, so the pin has to be
    derivable from what the pack ships — not from something only this machine had."""
    import hashlib

    for one in PACK["items"]:
        content = prompts.pass1_messages_gm4(
            one["channel"],
            one["post_id"],
            one["topic"],
            one["entities"],
            one["msg_id"],
            one["text"],
        )[0]["content"]
        assert hashlib.sha256(content.encode("utf-8")).hexdigest() == one["rendering_sha256"], one[
            "id"
        ]
        assert len(content) == one["rendered_chars"]
        assert len(content) <= prompts.PASS1_MAX_INPUT_CHARS
    assert len({one["rendering_sha256"] for one in PACK["items"]}) == 64, (
        "two units render identically — their answers would be indistinguishable"
    )
