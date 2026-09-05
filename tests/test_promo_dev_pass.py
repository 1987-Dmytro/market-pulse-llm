"""S9's $0 half: the join back to the grader's row shape, and the record `--dry-run` writes.

An import proves nothing ([[stub_driven_script_verification]]) and `--dry-run` that stopped before
the write would leave the write path untested ([[exercise_the_write_path_not_just_the_compute]]), so
the entry point is DRIVEN here and the file it leaves behind is read back.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import promo_dev_pass as dev  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

ROW = {"channel": "@c", "thread_root": "1"}


def test_the_join_is_per_comment_and_a_silent_comment_is_not_invented():
    """Gold is one row per comment with a LIST of types; the model answers `about` + free-standing
    `signals`. The join is on `msg_id`, and a comment the model placed but said nothing about keeps
    its row with an empty list — that is a neutral answer, and the grader scores it as one."""
    answer = {
        "about": [
            {"msg_id": 10, "subject_type": "chain", "subject": "VARUS", "source": "explicit"},
            {"msg_id": 11, "subject_type": "post", "subject": "1", "source": "post_context"},
        ],
        "signals": [
            {"type": "жалоба", "msg_id": 10, "quote": "x"},
            {"type": "цена", "msg_id": 10, "quote": "y"},
            # a signal for a comment with NO about-row: it must not conjure one
            {"type": "спрос", "msg_id": 99, "quote": "z"},
        ],
    }
    rows = dev.predicted_rows(ROW, answer)
    assert [one["msg_id"] for one in rows] == ["10", "11"], "one row per about-row, and no more"
    assert rows[0]["signal_types"] == ["жалоба", "цена"]
    assert rows[1]["signal_types"] == [], "a neutral comment keeps its subject and no signal"
    assert all(one["channel"] == "@c" and one["thread_root"] == "1" for one in rows)


def test_a_comment_the_model_never_placed_produces_no_row():
    """Silence is an answer the grader must be able to see as a MISS ([[an_abstention_is_an_answer]]),
    so it is a row the gold has and the prediction does not — never a row invented here."""
    assert dev.predicted_rows(ROW, {"about": [], "signals": []}) == []


def test_the_dry_run_writes_the_record_and_every_number_in_it_is_derived(tmp_path):
    out = tmp_path / "prep.json"
    assert dev.main(["--dry-run", "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))

    assert record["law"]["codebook_version"] == promo_prompts.codebook_version()
    assert record["law"]["vocabulary"]["signal_types"] == list(promo_prompts.SIGNAL_TYPES)
    # ruling 05.09 (s) item 3 relabelled the spent holdout-40 as `dev-2`, so from iteration 4 the
    # dev leg is TWO arms of the first draw and `== 40` was a literal of the old population, not
    # the claim ([[a_shrunk_population_is_a_test_change]], read the other way). The claim is that
    # the record counts what the draw holds for the arms this leg IS, and dev-40 comes first.
    drawn = json.loads(dev.DRAW.read_text(encoding="utf-8"))["draw"]
    expected = sum(len(drawn[stratum][arm]) for arm in dev.ARMS for stratum in drawn)
    assert record["draw"]["arms"] == list(dev.ARMS) == ["dev", "holdout"]
    assert record["draw"]["dev_threads"] == len(dev.dev_threads()) == expected == 80
    first = {dev.unit_id(one) for one in dev.dev_threads()[:40]}
    assert first == {
        dev.unit_id(one) for one in dev.dev_threads(arms=("dev",))
    }, "dev-40 is answered first: what a hard stop cuts is dev-2's tail"

    bound = record["bound"]
    priced = bound["priced_from"]
    assert bound["seconds_at_the_mean"] == round(priced["value"] * bound["threads"], 1)
    assert bound["usd_at_the_max"] == round(
        priced["max"] * bound["threads"] * bound["usd_per_second"], 4
    )
    assert priced["source"] != "results/promo_dev40_prep.json", "a bound may not cite itself"
    # ruling 05.09 (t) item 4 retired the borrow on this leg, so the record's own sentence has to
    # follow the rate it actually used: it stays a BOUND either way, and it says BORROWED only
    # while a borrow is what priced it ([[identity_field_stops_covering_the_change]]).
    said = bound["is_a_bound_and_not_a_price"].upper()
    assert "BOUND" in said and "NOT A PRICE" in said
    assert ("BORROWED" in said) is (priced["sample"] != dev.WHOLE_RUN)

    corpus = record["corpus"]
    assert corpus["distinct_renders"] == bound["threads"], "40 threads, 40 different prompts"
    assert corpus["chars_max"] <= corpus["chars_total"]


def test_a_missing_rate_row_prices_nothing(tmp_path, monkeypatch):
    """The negative control on the borrow. A projection with no NAMED rate projects nothing — and a
    default that quietly stood in for the missing row is exactly the failure this refuses."""
    empty = tmp_path / "measurements.jsonl"
    empty.write_text('{"name": "something_else", "value": 1.0}\n', encoding="utf-8")
    monkeypatch.setattr(dev, "MEASUREMENTS", empty)
    with pytest.raises(SystemExit, match="no rate to borrow"):
        dev.borrowed_rate()


# --- the PAID half's $0 gates: driven without a pod, each with its negative control ---------------


class _Done:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


GUARD_SAYS = "CYCLE 3 SPENT     $3.5409 of $7.00\nREMAINING         $3.4591\n"


def test_the_smoke_is_a_rule_and_not_a_pick():
    """Shortest, median, longest by the prep record's own `chars` — and the ROLES are named, so a
    reader of the registration can re-derive the three without trusting this function."""
    threads = [
        {"channel": "@c", "thread_root": str(i), "chars": chars}
        for i, chars in enumerate([700, 100, 500, 900, 300])
    ]
    picked = dev.smoke_units([dict(one) for one in threads])
    assert [one["chars"] for one in picked] == [100, 500, 900]
    assert [one["smoke_role"] for one in picked] == ["shortest", "median", "longest"]


def test_the_guard_line_is_read_and_an_unreadable_headroom_refuses(monkeypatch):
    """The cycle's headroom is the guard's number. A run that cannot find the line refuses rather
    than reading a missing prior as unlimited — the negative control is the second half."""
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS))
    assert dev.guard_reading()["remaining_usd"] == 3.4591

    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done("nothing of the sort\n"))
    with pytest.raises(SystemExit, match="REMAINING"):
        dev.guard_reading()


def test_a_refusing_guard_stops_the_registration(monkeypatch):
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS, returncode=3))
    with pytest.raises(SystemExit, match="the guard refused"):
        dev.guard_reading()


def test_the_price_is_the_dearer_offer_and_a_missing_card_is_a_stop(monkeypatch):
    """The create response's `costPerHr` is what bills; a registration written at the cheaper of two
    offers would be a ceiling the run can exceed with no gate firing. And a card the datacenter does
    not have today is the operator's word, not a substitution this script may make."""
    offered = [
        {
            "displayName": "RTX 4090",
            "securePricePerHr": 0.74,
            "communityPricePerHr": 0.34,
            "dataCenterAvailability": [{"dataCenterId": "EU-RO-1", "stockStatus": "Medium"}],
        }
    ]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(offered)))
    assert dev.offered_price()["usd_per_hour"] == 0.74

    elsewhere = [dict(offered[0], dataCenterAvailability=[{"dataCenterId": "US-KS-2"}])]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(elsewhere)))
    with pytest.raises(SystemExit, match="not offered in EU-RO-1"):
        dev.offered_price()


def test_the_transport_gates_are_read_from_the_frozen_record_and_not_typed(tmp_path, monkeypatch):
    """Plan §9a's borrow: v5b's numbers — and the dead-man from the PRODUCTION sibling's record,
    ruling 03.09 (e) item 1, which names it and its measurements. v5b is a PROBE: its 180 s killed
    two healthy pods of this step before either could publish an ssh port."""
    v5b = dev.load(dev.BORROWED_GATES)
    gates = dev.borrowed_gates()
    assert gates["boot_kill_seconds"] == v5b["money"]["arithmetic"]["boot_kill_seconds"]
    assert gates["delete_margin_seconds"] == v5b["money"]["arithmetic"]["delete_margin_seconds"]
    assert gates["max_recreates"] == v5b["go_no_go"]["gates"]["0_transport_ssh_deadman"][
        "max_recreates"
    ]
    (ruled,) = [
        one
        for one in dev.load(dev.SIBLING_PREREG)["kill_clock"]
        if one.get("rung") == 2 and one.get("name") == "ssh dead-man"
    ]
    assert gates["ssh_deadman_seconds"] == ruled["deadline_seconds"]
    assert dev.rel(dev.SIBLING_PREREG) in gates["ssh_deadman_from"]
    assert gates["ssh_deadman_seconds"] > v5b["money"]["segments"][
        "a_dead_segment_costs_seconds"
    ] - v5b["money"]["arithmetic"]["delete_margin_seconds"], "the probe's 180 s is what fired"

    other = tmp_path / "sibling.json"
    other.write_text(
        json.dumps(
            {
                "kill_clock": [
                    {
                        "rung": 2,
                        "name": "ssh dead-man",
                        "deadline_seconds": 321.0,
                        "rule": "another record, another number",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(dev, "SIBLING_PREREG", other)
    assert dev.ssh_deadman()["seconds"] == 321.0, "the deadline is READ, not typed"
    other.write_text(json.dumps({"kill_clock": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match="unreadable gate"):
        dev.ssh_deadman()


def test_rung_zero_fits_at_the_dear_corner_and_refuses_when_the_cap_shrinks():
    """The gate's own inequality, all three directions. A rung-0 that can only say yes is not a rung
    ([[guard_selftest_negative_control]]): a cap of ten cents does not fit at any corner, and a cap
    the DEAR corner clears is issued on the dear corner and never on the cheap one.

    The wide cap is $5.00 and not iteration 3's $2.50 because ruling 05.09 (t) item 4 retired the
    borrow here: the dear rate went 135.232 -> 286.248 s/thread, so $2.50 no longer reaches the dear
    corner and the dear-issuing leg would have stopped being reachable at all
    ([[an_absolute_bar_needs_a_reachability_state]]). The claim did not move, its literal did.
    """
    price = {"card": dev.CARD, "datacenter": "EU-RO-1", "stock": "Medium", "usd_per_hour": 0.74}
    threads = [{"channel": "@c", "thread_root": str(i)} for i in range(40)]
    wide = dev.rung_0(cap=5.00, price=price, threads=threads, n_posts=16)
    assert wide["fits"] and wide["dear_usd"] < 5.00 and wide["issued_on"] == "dear"
    assert wide["threads"] == dev.SMOKE_N + 40

    narrow = dev.rung_0(cap=0.10, price=price, threads=threads, n_posts=16)
    assert not narrow["fits"]
    assert narrow["table"][0]["fits"] is False
    assert "FITS" in dev.render_rung_0(wide) and "DOES NOT FIT" in dev.render_rung_0(narrow)

    # ruling 05.09 (t) item 3 — the middle case, and the one iteration 4 is registered under: the
    # dear corner is over the cap, the MEAN corner is not, and the leg is issued FITS on the mean
    # with the cap as the hard stop. The `part != "dev"` condition that used to guard this branch
    # is exactly what made iteration 4 unregisterable under a cap the operator had already named.
    middle = dev.rung_0(cap=1.20, price=price, threads=threads, n_posts=0, part="dev")
    assert middle["issued_on"] == "mean" and middle["fits"] and not middle["dear_fits"]
    assert middle["table"][0]["usd"] <= 1.20 < middle["dear_usd"]


def test_the_bill_is_not_the_generation():
    """The sibling's overhead is a POSITIVE number read off a settled pod — boot, the 31B load, the
    scp and the delete. A corner that priced generation alone would price the wrong quantity."""
    overhead = dev.sibling_overhead()
    pod = dev.load(dev.SIBLING)["pods"][0]
    assert overhead["seconds"] > 0
    assert overhead["seconds"] == round(pod["billed_seconds"] - dev.borrowed_rate()["value"] * 75, 1)


def test_leg_b_pins_ids_and_not_a_count():
    """The 16 posts are enumerated from the store by S4's own subtraction; a count in prose is not
    the enumeration ([[count_in_prose_is_not_the_enumeration]])."""
    posts = dev.leg_b_posts()
    assert posts["posts"] == sum(len(ids) for ids in posts["by_channel"].values())
    assert posts["task"] == "positions_text_gm4"
    assert all(one.isdigit() for ids in posts["by_channel"].values() for one in ids)


REGISTERED = {
    "step": {"cap_usd": 2.5},
    "rung_0": {"price": {"usd_per_hour": 0.74, "card": dev.CARD}, "hard_stop_seconds": 12162.0},
    "gates": {"terminate_after_minutes": 90},
}


@pytest.fixture
def staged(tmp_path, monkeypatch):
    monkeypatch.setattr(dev, "RUN_RECORD", tmp_path / "run.json")
    monkeypatch.setattr(dev, "committed_registration", lambda: REGISTERED)
    return tmp_path / "run.json"


def test_rung_one_kills_a_pod_dearer_than_the_registration(staged):
    """The registration priced the cap at an offer read on the day; the meter bills what the create
    response says. A pod that came back dearer is a different pod's price, and the cap was computed
    against the other number — so the gate has to be able to say KILL, not only GO."""
    ok = dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=dev.CARD
    )
    assert ok["latest"]["verdict"] == "GO"
    assert ok["gates"][-1]["backstop_fits"] is True
    assert ok["gates"][-1]["usd_at_the_backstop"] < REGISTERED["step"]["cap_usd"]

    dev.close_segment(deleted_at="2026-09-03T18:10:00Z", billed_seconds=600, outcome="test")
    dear = dev.open_segment(
        pod_id="a2", created_at="2026-09-03T18:20:00Z", usd_per_hour=1.19, card=dev.CARD
    )
    assert dear["latest"]["verdict"] == "KILL"


def test_never_two_pods_is_checked_before_the_second_create(staged):
    """The ban's goal is that two meters never run at once, so it is a check BEFORE `pod create`
    and not a refusal after the second one has started billing."""
    dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=dev.CARD
    )
    with pytest.raises(SystemExit, match="still OPEN"):
        dev.open_segment(
            pod_id="a2", created_at="2026-09-03T18:01:00Z", usd_per_hour=0.74, card=dev.CARD
        )


def test_the_bill_is_the_segments_own_price_and_the_gates_append(staged):
    """Never a balance delta — that prices the account, not the leg
    ([[a_balance_delta_is_not_a_per_leg_cost]]). And no snapshot is overwritten."""
    dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=dev.CARD
    )
    state = dev.close_segment(
        deleted_at="2026-09-03T18:34:21Z", billed_seconds=2061.0, outcome="56 of 56 answered"
    )
    assert state["gates"][-1]["billed_usd"] == round(2061.0 * 0.74 / 3600, 6)
    assert state["gates"][-1]["left_usd"] == round(2.5 - 2061.0 * 0.74 / 3600, 6)
    assert [one["kind"] for one in state["gates"]] == ["price", "close"]
    assert json.loads(staged.read_text())["segments"][0]["deleted_at"] == "2026-09-03T18:34:21Z"


def test_the_pack_pins_exactly_what_the_pod_re_derives():
    """The dry contact, as a test: every shipped unit re-renders on this checkout to the sha the
    pack pinned. «Exactly» is both directions — every unit the committed registration names is in
    the pack, and the pack ships nothing the registration does not name — and the population is READ
    from that record, never typed: a literal here pins ONE registration's population, which a ruling
    moves ([[a_number_typed_into_its_own_checker]], PHASE §6.6).

    Leg B's pin is of the RENDERED request and not of the payload — the two differ by the whole
    positions instruction, and pinning the payload refused every leg-B unit on a healthy pod
    ([[the_fixture_and_the_artifact_share_anchors]]). Its loop runs over the record's own leg-B
    units, so it is empty exactly while ruling 04.09 (m) item 4 keeps the leg closed, and fills
    again the day a ruling puts ids back into `by_channel` — which is what `build_pack` iterates.
    """
    import promo_dev_pod_runner as pod
    import reader_v5_pod_runner as pod_runner

    from market_pulse import prompts

    population = dev.committed_registration()["population"]
    registered_a = list(population["leg_a"]["order"])
    registered_b = [
        f"{handle}:{msg_id}"
        for handle, ids in sorted(population["leg_b"]["by_channel"].items())
        for msg_id in ids
    ]

    pack = dev.load(dev.PACK)
    # the two reads are one record or the comparison below compares two populations
    assert pack["registration"]["sha256"] == dev.sha256_of(dev.PREREG)
    keep, pod_runner.render = pod_runner.render, pod.render
    try:
        items = pod_runner.check_requests(pack, prompts)
    finally:
        pod_runner.render = keep

    by_id = {one["id"]: one for one in items}
    assert len(by_id) == len(items), "an id twice is one unit shipped twice"
    assert len(items) == population["leg_a"]["threads"] + population["leg_b"]["posts"]
    assert sorted(by_id) == sorted(registered_a + registered_b)
    assert sum(1 for one in items if one["leg"] == "b") == population["leg_b"]["posts"]
    for one in registered_b:
        assert by_id[one]["leg"] == "b"
    assert [one["id"] for one in items[:3]] == pack["smoke_ids"]


def test_the_leak_check_finds_a_planted_quote_and_clears_a_corpus_that_has_none():
    """Ruling 04.09 (j) item 2's check, driven both ways on a SYNTHETIC corpus.

    A guard that only ever refuses reads as broken and a guard that only ever passes proves nothing
    ([[guard_selftest_negative_control]]), so the law's own strings are planted into a comment here
    and the check must name the unit they landed on. The strings are read out of the shipped module
    rather than retyped ([[a_number_typed_into_its_own_checker]]): a list beside the law would go on
    passing the day the law changed, which is exactly how the 11 dev-40 quotes survived iteration 1.
    """
    def comment(text, split="dev"):
        return {"split": split, "channel": "@c", "thread_root": "1", "msg_id": "2", "text": text}

    law = next(one for one in dev.quoted(promo_prompts.CODEBOOK) if len(one) >= dev.CODEBOOK_LITERAL_FLOOR)
    example = dev.quoted(promo_prompts.EXAMPLES)[0]

    clean = dev.leak_check([comment("нормальна ціна, дякую")])
    assert clean["verdict"] == "CLEAN" and clean["hits"] == []
    assert clean["populations"]["examples"]["literals"] == len(dev.quoted(promo_prompts.EXAMPLES))

    planted = dev.leak_check([comment(f"чесно кажучи {law} і по факту"), comment(example, "holdout")])
    assert planted["verdict"] == "LEAK"
    assert {one["population"] for one in planted["hits"]} == {"codebook", "examples"}
    assert all(one["unit"] == "@c:1:2" for one in planted["hits"]), "a hit names the thread it hit"
    assert {one["split"] for one in planted["hits"]} == {"dev", "holdout"}


def test_the_shipped_law_is_clean_against_every_set_it_will_be_graded_on():
    """The real run of the check above — the one ruling 04.09 (j) item 2 asks for, over the THREE
    sets ruling 05.09 (s) item 5 names. It reads `data/raw`, which is not in the repository, so on a
    machine without the frozen archive it says so instead of passing silently
    ([[a_checker_whose_failure_is_silence]]).

    The sizes are READ from the committed records rather than typed (PHASE §6.6): each labelled set
    must carry one row per comment with text (codebook §8), and the unlabelled holdout-2 is counted
    off its own draw's `n_comments − n_wordless`. A literal here would have gone on asserting 140 +
    188 the day a third set joined the corpus ([[a_number_typed_into_its_own_checker]]).
    """
    if not (REPO_ROOT / "data" / "raw" / "comments").is_dir():
        pytest.skip("the frozen v1 archive data/raw is not on this machine — nothing was checked")

    def gold_rows(path):
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

    draw2 = json.loads(dev.DRAW2.read_text(encoding="utf-8"))
    owed = {
        "dev-40": gold_rows(REPO_ROOT / "docs" / "labels-promo-dev.jsonl"),
        "dev-2": gold_rows(REPO_ROOT / "docs" / "labels-promo-dev2.jsonl"),
        "holdout-2": sum(
            row["n_comments"] - row["n_wordless"]
            for block in draw2["draw"].values()
            for row in block["holdout"]
        ),
    }
    record = dev.leak_check(dev.store_texts())
    assert record["corpus"]["by_split"] == owed
    assert record["corpus"]["comments_with_text"] == sum(owed.values())
    assert record["verdict"] == "CLEAN", record["hits"]
