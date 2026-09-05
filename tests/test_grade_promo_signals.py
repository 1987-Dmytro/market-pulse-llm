"""K8's grader on SYNTHETIC gold — the two agreements, and the split the stratification bought.

The bars are «subject agreement ≥ 0.80» and «signal-type agreement ≥ 0.75», and neither phrase has
a single meaning. What each one counts is pinned here, because a bar over an undefined metric is
not a bar ([[a_published_ratio_is_not_the_gates]]).
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

spec = importlib.util.spec_from_file_location(
    "grade_promo_signals", REPO_ROOT / "scripts" / "grade_promo_signals.py"
)
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

CH = "@VARUS_channel"


def gold(msg_id="101", subject="Яготинське", types=("цена",), root="4519", channel=CH):
    return {
        "channel": channel,
        "thread_root": root,
        "msg_id": msg_id,
        "subject_type": "brand",
        "subject": subject,
        "signal_types": list(types),
    }


def test_a_perfect_read_scores_one_on_both():
    got = grader.grade([gold()], [gold()], {})
    assert got["bars"]["subject_agreement"]["value"] == 1.0
    assert got["bars"]["signal_type_agreement"]["value"] == 1.0
    assert all(block["held"] for block in got["bars"].values())


def test_silence_on_a_gold_comment_is_a_disagreement_and_not_a_smaller_denominator():
    """The way a grader flatters an instrument: drop the rows it said nothing about and the rate
    rises over a population nobody chose ([[the_fix_widened_the_denominator]])."""
    got = grader.grade([gold("101"), gold("102")], [gold("101")], {})
    assert got["bars"]["subject_agreement"]["value"] == 0.5
    assert got["whole_40"]["subject_comments"] == 2


def test_the_subject_is_compared_after_normalisation_and_on_BOTH_halves():
    assert grader.grade([gold()], [gold(subject="  яготинське ")], {})["bars"]["subject_agreement"]["value"] == 1.0
    wrong_type = {**gold(), "subject_type": "chain"}
    assert grader.grade([gold()], [wrong_type], {})["bars"]["subject_agreement"]["value"] == 0.0


def test_signal_types_are_a_SET_per_thread_and_over_labelling_costs_as_much_as_missing():
    """Jaccard. A thread the model over-labels is not free, and a thread both sides leave empty is
    1.0 rather than a division by zero."""
    one_of_two = grader.grade(
        [gold(types=("цена", "жалоба"))], [gold(types=("цена",))], {}
    )
    assert one_of_two["bars"]["signal_type_agreement"]["value"] == 0.5
    over = grader.grade([gold(types=("цена",))], [gold(types=("цена", "похвала"))], {})
    assert over["bars"]["signal_type_agreement"]["value"] == 0.5
    empty = grader.grade([gold(types=())], [gold(types=())], {})
    assert empty["bars"]["signal_type_agreement"]["value"] == 1.0


def test_the_two_strata_are_reported_beside_the_bars_and_never_instead_of_them():
    """What stratifying the draw bought: if the `decimal`-only half grades worse, the number says
    so. The BAR stays on the whole 40 — that is what the bar is on."""
    strata = {(CH, "4519"): "currency", (CH, "7001"): "decimal_only"}
    good, bad = gold(root="4519"), gold(root="7001")
    got = grader.grade([good, bad], [good, {**bad, "subject": "Молокія"}], strata)
    assert got["bars"]["subject_agreement"]["value"] == 0.5, "the bar is on the whole set"
    assert got["by_stratum"]["currency"]["subject_agreement"] == 1.0
    assert got["by_stratum"]["decimal_only"]["subject_agreement"] == 0.0


def test_an_unsure_row_is_counted_and_stays_in_the_denominator():
    """An abstention is an answer. A grader that dropped `unsure` rows would report the instrument's
    willingness, not its accuracy ([[an_abstention_is_an_answer]])."""
    got = grader.grade([gold()], [{**gold(subject=""), "unsure": "no subject in the row"}], {})
    assert got["bars"]["subject_agreement"]["value"] == 0.0
    assert got["readings"]["unsure_rows"] == 1


def test_the_bars_are_the_phase_specs_and_the_definitions_are_written_into_the_record(tmp_path):
    assert grader.BARS == {"subject_agreement": 0.80, "signal_type_agreement": 0.75}
    g, p, out = tmp_path / "g.jsonl", tmp_path / "p.jsonl", tmp_path / "o.json"
    g.write_text(json.dumps(gold(), ensure_ascii=False) + "\n", encoding="utf-8")
    p.write_text(json.dumps(gold(), ensure_ascii=False) + "\n", encoding="utf-8")
    assert grader.main(
        ["--gold", str(g), "--predicted", str(p), "--out", str(out), "--draw", str(tmp_path / "no")]
    ) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert "per COMMENT" in record["definitions"]["subject_agreement"]
    assert "Jaccard" in record["definitions"]["signal_type_agreement"]
    assert record["by_stratum"]["note"], "a missing draw record is said, not silently unsplit"


def test_the_strata_come_from_the_draw_record_and_name_the_dev_arm(tmp_path):
    """The split is read off `results/promo_threads_draw.json` — the dev arm, which is what K8
    scores. A grader that read the holdout's rows here would be scoring the one shot."""
    draw = tmp_path / "draw.json"
    draw.write_text(
        json.dumps(
            {
                "draw": {
                    "currency": {"dev": [{"channel": CH, "thread_root": "4519"}], "holdout": [
                        {"channel": CH, "thread_root": "9999"}
                    ]},
                }
            }
        ),
        encoding="utf-8",
    )
    strata = grader.strata_of(draw)
    assert strata == {(CH, "4519"): "currency"}
    assert (CH, "9999") not in strata


# --- the shipped gold, and whether this grader can read IT ---------------------------------------

GOLD = REPO_ROOT / "docs" / "labels-promo-dev.jsonl"


def real_gold() -> list[dict]:
    return [json.loads(one) for one in GOLD.read_text(encoding="utf-8").splitlines() if one.strip()]


def test_the_grader_reads_the_shipped_gold_and_both_bars_are_independent():
    """Everything above drives SYNTHETIC gold. This drives the team lead's real one, so a schema
    drift between `docs/labels-promo-dev.jsonl` and this reader is caught BEFORE a paid iteration
    spends its money measuring the plumbing ([[drive_the_consumer_not_only_the_producer]]).

    Four directions, because a grader that answered 1.0 to everything would pass the first alone
    ([[guard_selftest_negative_control]]): the gold against itself scores 1.0 on both bars; wrong
    subjects redden ONLY the subject bar; stripped signals redden ONLY the signal bar; and silence
    reddens both, which is what «an abstention is an answer» has to mean in a number.
    """
    gold = real_gold()
    strata = grader.strata_of(grader.DRAW)

    perfect = grader.grade(gold, gold, strata)["whole_40"]
    assert perfect["subject_agreement"] == 1.0
    assert perfect["signal_type_agreement"] == 1.0

    wrong_subject = [{**row, "subject": "ZZZ", "subject_type": "post"} for row in gold]
    hit = grader.grade(gold, wrong_subject, strata)["whole_40"]
    assert hit["subject_agreement"] == 0.0, "a wrong subject is a miss"
    assert hit["signal_type_agreement"] == 1.0, "and it does not move the OTHER bar"

    # Threads whose gold carries no signal at all score 1.0 when the model also says nothing, so
    # stripping every signal must land on exactly that share — DERIVED here, never typed.
    threads = {(row["channel"], str(row["thread_root"])) for row in gold}
    silent_in_gold = {
        key
        for key in threads
        if not any(
            row.get("signal_types")
            for row in gold
            if (row["channel"], str(row["thread_root"])) == key
        )
    }
    stripped = [{**row, "signal_types": []} for row in gold]
    hit = grader.grade(gold, stripped, strata)["whole_40"]
    assert hit["signal_type_agreement"] == round(len(silent_in_gold) / len(threads), 4)
    assert hit["subject_agreement"] == 1.0, "stripping signals does not move the subject bar"

    silence = grader.grade(gold, [], strata)["whole_40"]
    assert silence["subject_agreement"] == 0.0
    assert silence["signal_type_agreement"] == round(len(silent_in_gold) / len(threads), 4)


def test_the_grade_folds_chain_spellings_on_both_sides_and_leaves_brands_alone():
    """Codebook v1.1 (б) and ruling 04.09 (j) item 1. The fold is applied to GOLD and PREDICTION
    alike — a fold on one side only would move the denominator's own answers
    ([[correcting_gold_moves_the_denominator]]) — and to `chain` rows only.

    Measured on iteration 1's own replies this is worth exactly one row,
    `@VARUS_channel:6216:8865` (gold «VARUS», model «Варус»): 114/140 → 115/140.
    """
    rows = [gold(msg_id="1", subject="VARUS"), gold(msg_id="2", subject="Яготинське")]
    said = [
        dict(gold(msg_id="1", subject="Варус"), subject_type="chain"),
        dict(gold(msg_id="2", subject="яготинське")),
    ]
    rows[0]["subject_type"] = "chain"
    assert grader.agree(rows, said)["subject_agreement"] == 1.0

    # and a BRAND written two ways is still two answers: the chain table has nothing to say here
    brand_gold = [dict(gold(msg_id="3", subject="VARUS"), subject_type="brand")]
    brand_said = [dict(gold(msg_id="3", subject="Варус"), subject_type="brand")]
    assert grader.agree(brand_gold, brand_said)["subject_agreement"] == 0.0


def test_k8_v2_agrees_on_a_dropped_modifier_token_and_refuses_a_substituted_one():
    """K8 v2, ruling 05.09 (s) item 3 — the caught grader defect PHASE §4 gives ONE test.

    The defect: seven of holdout-40's 53 subject misses were one product written two ways, and
    codebook v1.2 rule (в) now trims «ТМ», «від», volume and percent out of the form — so the two
    sides legitimately differ by a MODIFIER token. Both directions, because a comparison loose
    enough to agree with everything is not a comparison ([[guard_selftest_negative_control]]):
    a dropped token agrees, a SUBSTITUTED one does not, and neither `chain` nor `post` moves.
    """
    def sku(subject, msg_id="1"):
        return dict(gold(msg_id=msg_id, subject=subject), subject_type="sku")

    # fires: {морозиво, сніжинка} vs {морозиво} — Jaccard 0.5, the trimmed modifier
    assert grader.subjects_agree(sku("морозиво Сніжинка"), sku("морозиво"))
    assert grader.agree([sku("морозиво Сніжинка")], [sku("морозиво")])["subject_agreement"] == 1.0
    # and does NOT fire: {морозиво, сніжинка} vs {морозиво, зимова} — Jaccard 0.333, another product
    assert not grader.subjects_agree(sku("морозиво Сніжинка"), sku("морозиво Зимова"))
    said = [sku("морозиво Зимова")]
    assert grader.agree([sku("морозиво Сніжинка")], said)["subject_agreement"] == 0.0
    # the floor is a floor, not a "share a token" rule
    assert not grader.subjects_agree(sku("пиво світле Кварта"), sku("пиво"))

    # the two types K8 v2 does not touch: a chain still folds only through the registry, and a
    # `post` subject is the thread root — two roots that share no token stay two answers
    chain_gold = dict(gold(subject="VARUS"), subject_type="chain")
    assert grader.subjects_agree(chain_gold, dict(gold(subject="Варус"), subject_type="chain"))
    assert not grader.subjects_agree(chain_gold, dict(gold(subject="АТБ"), subject_type="chain"))
    post_gold = dict(gold(subject="4519"), subject_type="post")
    assert not grader.subjects_agree(post_gold, dict(gold(subject="4520"), subject_type="post"))

    # an `unsure` row carries no subject at all: no tokens, so it can never reach the floor
    assert not grader.subjects_agree(sku("морозиво"), dict(sku("morozyvo"), subject=None))

    assert grader.grade([sku("морозиво")], [sku("морозиво")], {})["k8_version"] == "v2"
