"""S9's $0 half: the join back to the grader's row shape, and the record `--dry-run` writes.

An import proves nothing ([[stub_driven_script_verification]]) and `--dry-run` that stopped before
the write would leave the write path untested ([[exercise_the_write_path_not_just_the_compute]]), so
the entry point is DRIVEN here and the file it leaves behind is read back.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import promo_dev_pass as dev  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

ROW = {"channel": "@c", "thread_root": "1"}

CARD = "NVIDIA RTX PRO 4500 Blackwell"
"""One card's gpu-id, for the tests that are about the PRICE gate and not about the card list.
It stopped being `dev.CARD` when ruling 05.09 (x) item 3 made the card a parameter read off
`runpodctl gpu list`: a test that reaches for the module's own choice cannot notice the day that
choice changes ([[a_number_typed_into_its_own_checker]] read the other way)."""


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


GUARD_SAYS = (
    "CYCLE 3 SPENT     $3.5409 of $7.00\n"
    "REMAINING         $3.4591\n"
    "PROMO-ITER4 SPENT      $0.0000 of $1.20  (anchor $8.95 from runpod_balance_at_promo-iter4_start)\n"
)


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
    """The cycle's headroom AND the step's own are the guard's numbers. A run that cannot find
    either line refuses rather than reading a missing prior as unlimited — ruling 05.09 (v) item 3
    added the second half, and the negative control is the second half of each."""
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS))
    reading = dev.guard_reading("promo-iter4", 1.20)
    assert reading["remaining_usd"] == 3.4591
    assert reading["step_remaining_usd"] == 1.20

    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done("nothing of the sort\n"))
    with pytest.raises(SystemExit, match="REMAINING"):
        dev.guard_reading("promo-iter4", 1.20)


def test_a_refusing_guard_stops_the_registration(monkeypatch):
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS, returncode=3))
    with pytest.raises(SystemExit, match="the guard refused"):
        dev.guard_reading("promo-iter4", 1.20)


def _gpu(name, gpu_id, gb, secure, community=None, stock="High", dc="EU-RO-1"):
    return {
        "displayName": name,
        "gpuId": gpu_id,
        "memoryInGb": gb,
        "securePricePerHr": secure,
        "communityPricePerHr": community,
        "dataCenterAvailability": [{"dataCenterId": dc, "stockStatus": stock}],
    }


def test_the_price_is_the_dearer_offer_and_a_missing_card_is_a_stop(monkeypatch):
    """The create response's `costPerHr` is what bills; a registration written at the cheaper of two
    offers would be a ceiling the run can exceed with no gate firing. And a card the datacenter does
    not have today is the operator's word, not a substitution this script may make.

    Ruling 05.09 (x) item 3 added the walk itself to what this test is about. The card is a
    PARAMETER now, so every condition that makes one candidate lose to the next needs a direction:
    the 24 GB that OOM'd, a card the cloud has no stock of, one over the operator's $0.90/h — and
    the EXACT name, because the listing carries `RTX PRO 4500 SE` at the same price and it is a
    different row in a different cloud ([[an_exclusion_by_id_is_not_an_exclusion_by_text]]).
    """
    listing = [
        _gpu("RTX PRO 4500", "NVIDIA RTX PRO 4500 Blackwell", 32, 0.72),
        _gpu("RTX PRO 4500 SE", "NVIDIA RTX PRO 4500 Blackwell SE", 32, 0.72, dc="EUR-IS-1"),
        _gpu("RTX A6000", "NVIDIA RTX A6000", 48, 0.53, 0.33, stock="none"),
        _gpu("L40S", "NVIDIA L40S", 48, 1.09, 0.79, dc="US-KS-2"),
        _gpu("RTX 4090", "NVIDIA GeForce RTX 4090", 24, 0.74, 0.34),
    ]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(listing)))

    # (w) item 2's own order, and the first name that clears every condition wins
    price = dev.offered_price()
    assert price["display_name"] == "RTX PRO 4500", "the SE row is a different card, not this one"
    assert price["card"] == "NVIDIA RTX PRO 4500 Blackwell", "the gpu-id is what `pod create` takes"
    assert price["usd_per_hour"] == 0.72 and price["vram_gb"] >= dev.MIN_VRAM_GB

    # the DEARER of two offers, never the cheaper: a 48 GB card at 0.53/0.33 registers 0.53
    plenty = [_gpu("RTX A6000", "NVIDIA RTX A6000", 48, 0.53, 0.33)]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(plenty)))
    assert dev.offered_price(("RTX A6000",))["usd_per_hour"] == 0.53

    # every direction of the walk, one at a time — each candidate loses for its OWN reason
    for row, why in (
        (_gpu("RTX A6000", "id", 24, 0.53), "24 GB"),
        (_gpu("RTX A6000", "id", 48, 0.53, stock="none"), "no stock"),
        (_gpu("RTX A6000", "id", 48, 0.53, dc="US-KS-2"), "no stock"),
        (_gpu("RTX A6000", "id", 48, 0.95), r"\$0.95/h"),
    ):
        monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps([row])))
        with pytest.raises(SystemExit, match=why):
            dev.offered_price(("RTX A6000",))

    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(listing)))
    with pytest.raises(SystemExit, match="no matching row at all"):
        dev.offered_price(("A CARD NOBODY OFFERS",))


def test_the_backstop_is_the_caps_own_minutes_and_never_a_borrowed_ninety():
    """Ruling 05.09 (x) item 3. `--terminate-after` used to be v5b's 90 minutes, and at iteration 5's
    $1.40 cap on a $0.72/h card the cap pays for 116 — so the borrowed number would have killed a
    run this record prices as FITS, at $1.08 ([[a_ceiling_derived_from_one_span_measured_over_another]]).

    Both directions, because a bound that only ever grows is not a bound: with a cap SMALLER than the
    borrowed 90 minutes the backstop shrinks with it, and `terminate_after_minutes * 60` stays at or
    under `hard_stop_seconds` — the inequality `open_segment` publishes as `backstop_fits` and the
    one thing «the cap is the hard stop» actually means ([[a_bound_the_meter_cannot_reach]]).
    """
    wide = 1.40 / 0.72 * 3600  # 7000 s — the cap's own seconds at the registered price
    grown = dev.backstop(90, wide)
    assert grown["terminate_after_minutes"] == 116
    assert grown["terminate_after_borrowed_minutes"] == 90
    assert "FIRST" in grown["terminate_after_rule"], "90 min bites before the cap's 116"
    assert grown["terminate_after_minutes"] * 60 <= wide

    narrow = dev.backstop(90, 0.50 / 0.72 * 3600)  # 2500 s: the cap bites long before the borrow
    assert narrow["terminate_after_minutes"] == 41
    assert narrow["terminate_after_minutes"] * 60 <= 0.50 / 0.72 * 3600
    assert "LAST" in narrow["terminate_after_rule"]


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
    price = {"card": CARD, "datacenter": "EU-RO-1", "stock": "Medium", "usd_per_hour": 0.74}
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
    "rung_0": {"price": {"usd_per_hour": 0.74, "card": CARD}, "hard_stop_seconds": 12162.0},
    "gates": {"terminate_after_minutes": 90},
}


@pytest.fixture
def staged(tmp_path, monkeypatch):
    # the record names its line's ledger and `close_segment` reads the anchor out of it (ruling
    # 06.09 (y) item 4, risk 3): anchored BEFORE every segment these tests create, so the sums
    # below are the line's — a stub record without one is refused, never summed over the batch
    ledger = tmp_path / "spend_test_line.json"
    ledger.write_text(json.dumps({"anchored_at": "2026-09-03T17:00:00+00:00"}), encoding="utf-8")
    record = {**REGISTERED, "step": {**REGISTERED["step"], "name": "test-line", "ledger": str(ledger)}}
    monkeypatch.setattr(dev, "RUN_RECORD", tmp_path / "run.json")
    monkeypatch.setattr(dev, "committed_registration", lambda: record)
    return tmp_path / "run.json"


def test_rung_one_kills_a_pod_dearer_than_the_registration(staged):
    """The registration priced the cap at an offer read on the day; the meter bills what the create
    response says. A pod that came back dearer is a different pod's price, and the cap was computed
    against the other number — so the gate has to be able to say KILL, not only GO."""
    ok = dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=CARD
    )
    assert ok["latest"]["verdict"] == "GO"
    assert ok["gates"][-1]["backstop_fits"] is True
    assert ok["gates"][-1]["usd_at_the_backstop"] < REGISTERED["step"]["cap_usd"]

    dev.close_segment(deleted_at="2026-09-03T18:10:00Z", billed_seconds=600, outcome="test")
    dear = dev.open_segment(
        pod_id="a2", created_at="2026-09-03T18:20:00Z", usd_per_hour=1.19, card=CARD
    )
    assert dear["latest"]["verdict"] == "KILL"


def test_never_two_pods_is_checked_before_the_second_create(staged):
    """The ban's goal is that two meters never run at once, so it is a check BEFORE `pod create`
    and not a refusal after the second one has started billing."""
    dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=CARD
    )
    with pytest.raises(SystemExit, match="still OPEN"):
        dev.open_segment(
            pod_id="a2", created_at="2026-09-03T18:01:00Z", usd_per_hour=0.74, card=CARD
        )


def test_the_bill_is_the_segments_own_price_and_the_gates_append(staged):
    """Never a balance delta — that prices the account, not the leg
    ([[a_balance_delta_is_not_a_per_leg_cost]]). And no snapshot is overwritten."""
    dev.open_segment(
        pod_id="a1", created_at="2026-09-03T18:00:00Z", usd_per_hour=0.74, card=CARD
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


def test_a_dead_unit_becomes_an_error_reply_the_mac_reads_as_the_smoke_not_coming_back(
    tmp_path, monkeypatch
):
    """Ruling 05.09 (w) item 3's ONE test, both directions, over BOTH halves of the transport.

    Iteration 4 died in `gemma4._norm` on `@VARUS_channel:8647` — the smoke's longest render — and
    said so only in the pod log. The out-file simply stopped at two rows, which is byte-for-byte
    what a third unit still generating looks like, so the Mac could not tell a dead pod from a slow
    one and waited out the GO deadline: $0.62 of the run's $0.69 was that wait. The drill is
    therefore the REAL shape — the committed registration's own three smoke units, two answered and
    the third killed where the OOM killed it — and the ids are read from that record, never typed
    ([[a_number_typed_into_its_own_checker]]).

    Both directions, because a reading that only ever says «gone» decides nothing
    ([[guard_selftest_negative_control]]): answered in full, the same file must read «3 replies are
    in» and exit 0. The artifact the POD half writes is the input the MAC half reads, so no fixture
    is invented between them ([[the_fixture_and_the_artifact_share_anchors]]).

    The last direction is the fix's own footgun, refused where it is made: `already_answered` counts
    any row carrying an `id` as ANSWERED, so a replacement pod resumed over the ERROR file would
    skip the very unit that killed the last one. The shipped reader is a PINNED pod runner (§4) and
    does not move, so the refusal lives in the runner whose pin moves with this fix.
    """
    import promo_dev_pod_runner as pod

    # the PART is stated, never inherited: `smoke_state` reads whichever registration `use_part`
    # last set, and the dev and holdout records share these three ids only by the accident of one
    # draw — holdout-2 is a NEW draw ((s) item 3) and would read three units nobody asked for
    dev.use_part("dev")
    assert dev.rel(dev.PREREG) == "results/prereg_promo_dev_loop.json"
    want = [
        one["unit_id"]
        for one in dev.committed_registration()["population"]["leg_a"]["smoke"]["units"]
    ]
    pack = {
        "instruments": {"leg_a": {"codebook_version": promo_prompts.codebook_version()}},
        "items": [{"id": one, "smoke": True} for one in want],
    }
    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    def answer(these, out):
        with out.open("a", encoding="utf-8") as handle:
            for one in these:
                row = {"id": one, "seconds": 9.5, "balanced": True, "finish_reason": "stop"}
                handle.write(json.dumps(row) + "\n")

    def argv(out):
        return ["--pack", str(pack_path), "--out", str(out), "--repo", str(REPO_ROOT),
                "--go", str(tmp_path / "never"), "--go-deadline", "0"]

    died = tmp_path / "died.jsonl"

    def crash(one_pack, out, repo, loader):
        answer(want[:2], out)
        raise RuntimeError("CUDA out of memory. Tried to allocate 338.00 MiB")

    monkeypatch.setattr(pod.runner, "run", crash)
    assert pod.main(argv(died), loader=lambda p, r: object(), sleep=lambda _: None) == 1

    rows = [json.loads(line) for line in died.read_text(encoding="utf-8").splitlines() if line]
    assert [one["id"] for one in rows[:2]] == want[:2], "the answered units are left as they were"
    error = rows[-1]
    assert error["id"] == want[2], "the ERROR reply names the unit the loop was generating"
    assert error["unanswered"] == [want[2]] and error["exception"] == "RuntimeError"
    assert "out of memory" in error["error"]

    gone = dev.smoke_state(died)
    assert gone["state"] == dev.SMOKE_GONE
    assert gone["action"] == dev.committed_registration()["decision_table"][
        "after_the_smoke_for_40_threads"
    ][dev.SMOKE_GONE], "the branch is the record's own prose, not a phrase beside it"
    assert dev.main(["--smoke", "--part", "dev", "--replies", str(died)]) == 1

    whole = tmp_path / "whole.jsonl"
    answer(want, whole)
    assert dev.smoke_state(whole)["state"] == dev.SMOKE_IN
    assert dev.smoke_state(whole)["missing"] == []
    assert dev.main(["--smoke", "--part", "dev", "--replies", str(whole)]) == 0

    partial = tmp_path / "partial.jsonl"
    answer(want[:2], partial)
    assert dev.smoke_state(partial)["state"] == "waiting", "a short file is a poll, not a verdict"
    assert dev.main(["--smoke", "--part", "dev", "--replies", str(partial)]) == 1

    with pytest.raises(SystemExit, match="give --out a NEW name"):
        pod.main(argv(died), loader=lambda p, r: object(), sleep=lambda _: None)

    # --- ruling 05.09 (x) item 4: the Mac reads an ERROR reply EVERYWHERE it reads replies -------

    # (a) the file is copied off a LIVE pod, so its last line can be half written. That is the scp
    # race and it reads as WAITING — a traceback here lands on the one command that decides whether
    # a billing pod is deleted, which is where iteration 4's $0.62 was lost in the first place.
    torn = tmp_path / "torn.jsonl"
    answer(want[:2], torn)
    with torn.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": want[2], "seconds": 9.5})[:-6])
    assert dev.smoke_state(torn)["state"] == "waiting"
    assert dev.smoke_state(torn)["missing"] == [want[2]]
    assert dev.main(["--smoke", "--part", "dev", "--replies", str(torn)]) == 1

    # (b) a crash AFTER the loop names no unit and writes `id: null` — still a death, and the row
    # that says so must not be keyed away by the id it deliberately does not have
    headless = tmp_path / "headless.jsonl"
    answer(want, headless)
    with headless.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": None, "error": "boom", "exception": "RuntimeError"}) + "\n")
    assert dev.smoke_state(headless)["state"] == dev.SMOKE_GONE

    # (c) the whole-run rate row counts a dead unit as UNANSWERED instead of dying on the `seconds`
    # an error reply never had. `--close-segment` appends its money gate BEFORE this row is written,
    # so a KeyError here keeps the bill and loses the measurement the next leg is priced on.
    order = dev.committed_registration()["population"]["leg_a"]["order"]
    assert set(want) <= set(order), "the smoke's three are registered leg-A units"
    monkeypatch.setattr(dev, "RUN_RECORD", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(
        json.dumps(
            {
                "phase": "promo-iter5",
                "segments": [{"pod_id": "a1", "card": CARD, "usd_per_hour": 0.72}],
                "gates": [],
            }
        ),
        encoding="utf-8",
    )
    row = dev.whole_run_row(died, "a1")
    assert row["n"] == 2, "two units answered, the third died — a rate over three would be invented"
    assert row["dead_units"] == [want[2]] and row["value"] == 9.5

    # (d) and the grader counts it the same way, without calling it a parse failure: a unit that
    # died has no answer to parse, and blaming the instrument for the serving is the wrong class
    pack = tmp_path / "scored_pack.json"
    pack.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": one,
                        "leg": "a",
                        "channel": one.split(":")[0],
                        "post_id": one.split(":")[1],
                    }
                    for one in want
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(dev, "PACK", pack)
    scored = tmp_path / "scored.jsonl"
    with scored.open("w", encoding="utf-8") as handle:
        for one in want[:2]:
            handle.write(
                json.dumps(
                    {
                        "id": one,
                        "seconds": 9.5,
                        "reply": '{"about": [], "signal": [], "unsure": []}',
                        "rendering_sha256": "deadbeef",
                    }
                )
                + "\n"
            )
        handle.write(
            json.dumps({"id": want[2], "error": "CUDA out of memory", "exception": "RuntimeError"})
            + "\n"
        )
    table = dev.score(scored, 5)
    assert table["answers"]["leg_a_units_answered"] == 2
    assert table["answers"]["leg_a_units_registered"] == 3
    assert table["answers"]["leg_a_units_dead"] == [want[2]]
    assert table["answers"]["parse_failures"] == 0, "a death is not an answer that failed to parse"

    # --- ruling 06.09 (y) item 4, the two risks, fixed under (z) item 3 on the Mac side only ------

    # (e) risk 2: every reader keyed on a TRUTHY `error`, and `error` is `str(exc)` — a death whose
    # exception carried an EMPTY message read as ANSWERED everywhere. `died` keys on the `exception`
    # field the pinned runner always writes. Both directions: the silent death is dead in every
    # reader, and a healthy row is never mistaken for one.
    silent = {"id": want[2], "error": "", "exception": "RuntimeError"}
    assert dev.died(silent) and dev.died({"id": None, "error": "boom", "exception": "KeyError"})
    assert not dev.died({"id": want[0], "seconds": 9.5, "balanced": True, "finish_reason": "stop"})
    quiet = tmp_path / "quiet.jsonl"
    answer(want[:2], quiet)
    with quiet.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(silent) + "\n")
    assert dev.smoke_state(quiet)["state"] == dev.SMOKE_GONE, "an empty message is still a death"
    assert f"ERROR RuntimeError on {want[2]}" in dev.render_smoke(dev.smoke_state(quiet))
    assert dev.dead_units(quiet) == [want[2]] and want[2] not in dev.answered_rows(quiet)
    assert dev.whole_run_row(quiet, "a1")["n"] == 2
    with pytest.raises(SystemExit, match=f"dead units: \\['{want[2]}'\\]"):
        dev.project(quiet)
    with scored.open("w", encoding="utf-8") as handle:
        for one in want[:2]:
            handle.write(json.dumps({"id": one, "seconds": 9.5, "reply": '{"about": [], "signal":'
                                     ' [], "unsure": []}', "rendering_sha256": "deadbeef"}) + "\n")
        handle.write(json.dumps(silent) + "\n")
    table = dev.score(scored, 5)
    assert table["answers"]["leg_a_units_answered"] == 2
    assert table["answers"]["leg_a_units_dead"] == [want[2]]
    assert table["answers"]["parse_failures"] == 0

    # (f) risk 3: `--close-segment` summed EVERY segment of the batch-scale run record against this
    # line's cap — iteration 5 printed `verdict OVER` on $2.874083 of seven pods while its line had
    # spent $0.9396 of $1.40. The segments counted are those created at or after the line's anchor,
    # READ from the ledger the committed registration names and never typed. Both directions: a pod
    # created before the anchor is another line's and stays out; one created after it is this
    # line's and is summed — over the cap, it is the OVER that is true.
    record = dev.committed_registration()
    cap = float(record["step"]["cap_usd"])
    anchor = datetime.fromisoformat(dev.load(REPO_ROOT / record["step"]["ledger"])["anchored_at"])
    before = (anchor - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    after = (anchor + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # the older pod's bill is the CAP itself, so «two pods over the cap» holds for any cap the
    # record carries and never by the accident of a typed price sitting above it
    def run_record(older_pod_created_at, live_pod_created_at=after):
        (tmp_path / "run.json").write_text(
            json.dumps(
                {
                    "phase": record["step"]["name"],
                    "segments": [
                        {"pod_id": "older", "created_at": older_pod_created_at, "deleted_at": before,
                         "usd_per_hour": 0.74, "card": CARD, "billed_seconds": cap / 0.74 * 3600,
                         "billed_usd": cap, "outcome": "another line's whole run"},
                        {"pod_id": "a1", "created_at": live_pod_created_at, "deleted_at": None,
                         "usd_per_hour": 0.72, "card": CARD},
                    ],
                    "gates": [],
                }
            ),
            encoding="utf-8",
        )

    run_record(before)
    gate = dev.close_segment(deleted_at=after, billed_seconds=3600.0, outcome="test")["gates"][-1]
    assert gate["line"] == record["step"]["name"]
    assert gate["line_anchored_at"] == anchor.isoformat(timespec="seconds")
    assert gate["segments_of_this_line"] == 1 and gate["spent_this_line_usd"] == 0.72
    assert gate["verdict"] == "GO" and gate["left_usd"] == round(cap - 0.72, 6)
    assert "spent_all_segments_usd" not in gate, "the false field is gone, not renamed beside"

    run_record(after)
    gate = dev.close_segment(deleted_at=after, billed_seconds=3600.0, outcome="test")["gates"][-1]
    assert gate["segments_of_this_line"] == 2 and gate["spent_this_line_usd"] == round(cap + 0.72, 6)
    assert gate["verdict"] == "OVER", "two pods of ONE line over its cap is the OVER that is true"

    # and the segment being CLOSED is inside its own line or the close refuses: a stamp before the
    # anchor would leave the bill just written out of the sum beside a GO (the fix's consequence)
    run_record(before, live_pod_created_at=before)
    with pytest.raises(SystemExit, match="predates its own line's anchor"):
        dev.close_segment(deleted_at=after, billed_seconds=1.0, outcome="test")

    # and a record that names no ledger cannot tell its line from the batch: refused, never summed
    monkeypatch.setattr(dev, "committed_registration", lambda: {"step": {"cap_usd": cap}})
    run_record(before)
    with pytest.raises(SystemExit, match="anchored_at"):
        dev.close_segment(deleted_at=after, billed_seconds=1.0, outcome="test")

    # (g) the verifier's bite on the holdout-2 leg (PHASE §4 v8): `register()` keyed its cap rule on
    # `--cap` being absent, not on the leg, so `--register --part holdout2` without `--cap` would
    # have opened the line at the DEV loop's $2.50 rule under a floor_rule calling it the operator's
    # number. Refused BEFORE the guard is read — no subprocess, no anchor — and the dev leg keeps its
    # derived cap: this refusal must not fire there.
    dev.use_part("holdout2")
    try:
        with pytest.raises(SystemExit, match="--part holdout2 needs --cap"):
            dev.register(None)
    finally:
        dev.use_part("dev")
    assert dev.PART == "dev" and dev.rel(dev.DRAW) == "results/promo_threads_draw.json"
