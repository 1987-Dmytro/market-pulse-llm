"""D2's union census — DRIVEN AT $0, before the pod, on a fabricated out-file.

The census is the artefact written when the evidence can no longer be re-bought, and r1's was where
the same defect turned up three times in one sitting: never-asked rows folded into a refusal class,
one `threads_total` over two denominators, and a `None` column meaning both «said null» and «never
reached». All three came from a run that ended early — and a run that ends early makes every count
in a census ambiguous at once ([[a_run_that_ends_early_adds_a_third_state_everywhere]]).

So the producer exists and is exercised BEFORE the money, on two shapes: a complete run (the union
is 1 032 and the window is closed) and a run that stopped half way (the union is short and every
count has to say so). The paid session then only fills it in.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import census_pass1_window_r2 as census  # noqa: E402
import gate_pass1_window_r2 as gate  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_window_r2.json").read_text("utf-8"))
PACK = json.loads((REPO_ROOT / "results" / "pass1_window_r2_pack.json").read_text("utf-8"))
R1_OUT = REPO_ROOT / "results" / "pass1_window_v2.jsonl"
CREATE = "2026-08-22T09:00:00+00:00"


def fake_replies(items: list[dict], seconds: float = 5.0) -> str:
    lines = []
    for index, item in enumerate(items):
        lines.append(
            json.dumps(
                {
                    "index": index,
                    "id": item["id"],
                    "thread": item["thread"],
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": json.dumps(
                        {
                            "msg_id": int(item["msg_id"]),
                            "subject_type": "сеть_ритейлер" if index % 3 else "категория_личное",
                            "subject_id": None,
                            "stance": None,
                        },
                        ensure_ascii=False,
                    ),
                    "balanced": True,
                    "emitted_chars": 110,
                    "seconds": seconds,
                    "elapsed_since_start": 170.0 + index * seconds,
                    "boot_seconds": 170.0,
                },
                ensure_ascii=False,
            )
        )
    return "".join(one + "\n" for one in lines)


def drive(tmp_path, monkeypatch, answered: int, *, tail: list[str] | None = None) -> dict:
    """The census over a fabricated r2 out-file, with every path redirected into tmp_path."""
    results = tmp_path / "results"
    results.mkdir()
    (results / "pass1_window_r2_v2.jsonl").write_text(
        fake_replies(PACK["legs"][0]["items"][:answered]), encoding="utf-8"
    )
    (results / "pass1_window_r2_pod.log").write_text(
        "".join(
            f"[{170.0 + i * 5.0:8.1f}s] reply {i + 1}/901 {one['id']}"
            "                5.0s ·   110 chars · cut    4 · balanced True · finish stop\n"
            for i, one in enumerate(PACK["legs"][0]["items"][:answered])
        ),
        encoding="utf-8",
    )
    state = {
        "pods": [
            {
                "pod_id": "fake-pod",
                "card": "NVIDIA GeForce RTX 4090",
                "usd_per_hour": 0.74,
                "created_at": CREATE,
                "deleted_at": "2026-08-22T10:20:00+00:00",
                "launched_at": "2026-08-22T09:01:23+00:00",
                "billed_seconds": 4800.0,
                "billed_usd": 0.986667,
            }
        ],
        "gates": [
            {"kind": "gate0", "verdict": "GO", "elapsed_on_this_pod_seconds": 41.5},
            {
                "kind": "boot",
                "verdict": "GO",
                "first_reply_at_create_elapsed_seconds": 253.0,
            },
            {"kind": "watch", "verdict": "GO", "watched_seconds": 4500.0, "answered": answered},
        ],
        "latest": {"kind": "watch", "verdict": "GO", "pod": 1},
    }
    record_path = results / "pass1_window_r2_run.json"
    record_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(census, "RESULTS", results)
    monkeypatch.setattr(census, "OUT", results / "census.json")
    monkeypatch.setattr(census, "VOLUME_TAIL", results / "pass1_window_volume_tail.jsonl")
    monkeypatch.setattr(gate.r1, "RECORD", record_path)
    monkeypatch.setattr(gate.r1, "POD_LOG", results / "pass1_window_r2_pod.log")
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    if tail is not None:
        census.VOLUME_TAIL.write_text(
            "".join(
                json.dumps({"id": one, "reply": "{}"}, ensure_ascii=False) + "\n" for one in tail
            ),
            encoding="utf-8",
        )
    return census.build()


def test_a_COMPLETE_run_closes_the_window_and_every_reading_is_over_1032(tmp_path, monkeypatch):
    out = drive(tmp_path, monkeypatch, answered=901)

    assert out["completeness"]["verdict"] == "GO"
    assert out["completeness"]["answered"] == out["completeness"]["owed"] == 901
    window = out["the_windows_completeness"]
    assert (
        window["owed"],
        window["answered"],
        window["answered_by_r1"],
        window["answered_here"],
    ) == (
        1032,
        1032,
        131,
        901,
    )
    assert window["complete"] is True
    assert window["not_a_bar_of_this_registration"] is True

    # the three states, and no row is left out of them
    dist = out["label_distribution"]["over_the_window"]
    assert sum(dist.values()) == 1032
    assert not any("UNANSWERED" in key for key in dist)
    assert out["label_distribution"]["answered"] == 1032

    # every report-only reading is over the WINDOW's own denominator, not the leg's
    readings = out["report_only"]
    assert readings["the_650_labelled_rows"]["n"] == 650
    assert readings["the_450_not_in_dev_200"]["n"] == 450
    assert readings["the_dev_200"]["n"] == 200
    assert readings["the_fourteen"]["n"] == 14
    for name in ("the_650_labelled_rows", "the_450_not_in_dev_200", "the_dev_200"):
        one = readings[name]
        assert one["absent"] == 0, name
        assert one["rows_the_pod_actually_answered"] == one["n"], name
        assert one["not_a_bar"] is True, name
    assert readings["the_450_not_in_dev_200"]["our_n"] == 0, "zero by construction, Dv652"
    assert "PAIR" in readings["keyed_on"]

    # the pass-2 filter table now covers the WHOLE window — the output r1 could not buy
    table = out["pass_2_filter"]
    assert sum(one["payable_comments"] for one in table["per_thread"]) == 1032
    assert table["threads_carrying_a_payable_comment"] == 127
    assert table["filtered_rows_total"] == sum(one["filtered_rows"] for one in table["per_thread"])
    assert table["filtered_rows_total"] > 0


def test_a_run_that_stops_HALF_WAY_says_so_in_every_count(tmp_path, monkeypatch):
    """The r1 shape, driven before the money instead of discovered after it."""
    out = drive(tmp_path, monkeypatch, answered=400)

    assert out["completeness"]["verdict"] == "RED"
    assert out["completeness"]["answered"] == 400
    assert out["completeness"]["unanswered"] == 501
    window = out["the_windows_completeness"]
    assert (window["answered"], window["owed"], window["complete"]) == (531, 1032, False)

    dist = out["label_distribution"]["over_the_window"]
    unanswered = [key for key in dist if "UNANSWERED" in key]
    assert unanswered and dist[unanswered[0]] == 501
    assert sum(dist.values()) == 1032

    # both denominators on every labelled reading, and the unasked rows counted as absent
    for name in ("the_650_labelled_rows", "the_450_not_in_dev_200", "the_dev_200"):
        one = out["report_only"][name]
        assert one["absent"] > 0, name
        assert one["rows_the_pod_actually_answered"] == one["n"] - one["absent"], name
        assert one["rate_over_the_rows_answered"] is not None, name
        assert "TWO rates" in one["denominator_rule"], name
    assert out["report_only"]["the_fourteen"]["rows_the_pod_actually_reached"] < 14


def test_the_volume_tail_is_counted_and_priced_and_never_merged(tmp_path, monkeypatch):
    held = [json.loads(one)["id"] for one in R1_OUT.read_text("utf-8").splitlines() if one.strip()]
    extra = [one["id"] for one in PACK["legs"][0]["items"][:5]]
    out = drive(tmp_path, monkeypatch, answered=901, tail=held + extra)
    tail = out["the_volume_tail"]
    assert tail["rows_on_the_volume"] == 136
    assert tail["rows_beyond_the_mac"] == 5
    assert tail["merged"] is False
    assert tail["bought_twice_seconds"] == 25.0  # 5 rows x this pod's measured 5.0 s/call
    assert tail["seconds_per_call_used"] == out["spans"]["measured"]["seconds_per_call_mean"]


def test_a_missing_volume_tail_is_a_READING_and_not_a_crash(tmp_path, monkeypatch):
    out = drive(tmp_path, monkeypatch, answered=901)
    assert "not on disk" in out["the_volume_tail"]["reading"]
    assert "Dv657's lower bound stays" in out["the_volume_tail"]["reading"]


def test_the_spans_are_measured_beside_the_charge_and_the_rate_names_its_class(
    tmp_path, monkeypatch
):
    out = drive(tmp_path, monkeypatch, answered=901)
    spans = out["spans"]
    assert spans["charged"]["seconds_per_call"] == 6.14
    assert spans["charged"]["total_seconds"] == 7932.14
    assert spans["measured"]["seconds_per_call_mean"] == 5.0
    assert spans["measured"]["ssh_publish_seconds"] == 41.5
    assert spans["measured"]["first_reply_at_create_elapsed_seconds"] == 253.0
    assert spans["measured"]["per_poll_copy_back"]["watched_seconds"] == 4500.0
    assert spans["measured"]["per_poll_copy_back"]["rows_at_the_end"] == 901

    rate = out["the_rate_of_this_pod"]
    assert rate["charged_here"] == 6.14
    assert rate["over_the_charge"] == round(5.0 / 6.14, 4)
    assert set(rate["the_readings_this_class_has"].values()) == {
        5.161578,
        2.293075,
        2.725780,
        4.498473,
    }
    assert "property of the POD" in rate["rule"]


def test_the_log_names_what_the_out_file_does_not(tmp_path, monkeypatch):
    """Dv657 on THIS pod — and an empty list is what a clean GO looks like."""
    out = drive(tmp_path, monkeypatch, answered=901)
    block = out["replies_the_mac_does_not_hold"]
    assert block["rows_in_the_copied_back_file"] == 901
    assert block["replies_the_pod_log_reports"] == 901
    assert block["replies_named_by_the_log_and_absent_from_the_file"] == []


def test_the_shipped_census_is_what_the_producer_writes_today(tmp_path):
    """The real artefact, regenerated — a census nobody can re-derive is a census nobody can check."""
    assert census.main(["--out", str(tmp_path / "again.json")]) == 0
    assert (tmp_path / "again.json").read_text("utf-8") == (
        REPO_ROOT / "results" / "pass1_window_r2_census.json"
    ).read_text("utf-8")


def test_the_shipped_census_closes_the_window_and_carries_the_readings_as_readings():
    out = json.loads((REPO_ROOT / "results" / "pass1_window_r2_census.json").read_text("utf-8"))
    assert out["completeness"]["verdict"] == "GO"
    assert out["completeness"]["answered"] == out["completeness"]["owed"] == 901
    assert out["completeness"]["sha_mismatches"] == 0
    assert out["completeness"]["parse_refusals"] == 0
    window = out["the_windows_completeness"]
    assert (window["answered"], window["owed"], window["complete"]) == (1032, 1032, True)
    assert (window["answered_by_r1"], window["answered_here"]) == (131, 901)

    # every report-only reading is over its FULL denominator and none of them is a bar
    for name in ("the_650_labelled_rows", "the_450_not_in_dev_200", "the_dev_200"):
        one = out["report_only"][name]
        assert one["absent"] == 0, name
        assert one["not_a_bar"] is True, name
        assert "passed" not in one and "threshold" not in one, name
    assert out["report_only"]["the_dev_200"]["agreed"] == 136
    assert out["report_only"]["the_dev_200"]["our_agreed"] == 38
    assert out["report_only"]["the_dev_200"]["r2_reported"] == {
        "agreed": 136,
        "n": 200,
        "our_agreed": 38,
        "our_n": 49,
    }
    assert out["report_only"]["the_450_not_in_dev_200"]["our_n"] == 0, "Dv652"
    fourteen = out["report_only"]["the_fourteen"]
    assert fourteen["rows_the_pod_actually_reached"] == 14
    assert fourteen["agreed"] == 11
    assert fourteen["not_a_bar"] is True
    assert "never a bar" in fourteen["caption"].lower()

    # the volume tail: counted, priced, NEVER merged
    tail = out["the_volume_tail"]
    assert (tail["rows_on_the_volume"], tail["rows_the_mac_already_held"]) == (134, 131)
    assert tail["rows_beyond_the_mac"] == 3
    assert tail["merged"] is False
    assert tail["sha256"] == "f52f63f3adb726859815aad8379fa142f8f4ae54ecb52e7c2172108aa2d073ae"


def test_the_dev_200_reproduces_r2_ROW_FOR_ROW_across_three_pods():
    """Not the count — the rows. Greedy decoding on a pinned rendering is deterministic here.

    r2 answered these 200 on pod 8tpx8lf05n6skc; r1's pod answered 48 of them and this run's the
    other 152. If a single label differed the census's 136/200 would be a coincidence of counts, and
    the whole reading of Dv647 — «the pod class varies in SECONDS and not in ANSWERS» — would be an
    assertion instead of a measurement.
    """
    import score_reader_probe_b as probe_b

    from market_pulse import prompts

    window = json.loads((REPO_ROOT / "results" / "pass1_window_pack.json").read_text("utf-8"))
    items = {one["id"]: one for one in window["legs"][0]["items"]}
    dev = set(window["membership"]["dev_200"]["ids"])

    dev_pack = json.loads((REPO_ROOT / "results" / "pass1_dev_pack.json").read_text("utf-8"))
    leg = next(one for one in dev_pack["legs"] if one["name"] == "v2")
    dev_items = {one["id"]: one for one in leg["items"]}

    def labels(path: Path, keep=None, lookup=None):
        out = {}
        for line in path.read_text("utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if keep is not None and row["id"] not in keep:
                continue
            item = (lookup or items)[row["id"]]
            answer = prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
            out[row["id"]] = probe_b.collapse(answer["subject_type"])
        return out

    on_the_dev_pod = labels(REPO_ROOT / "results" / "pass1_dev_v2.jsonl", lookup=dev_items)
    union = labels(REPO_ROOT / "results" / "pass1_window_v2.jsonl", keep=dev)
    union |= labels(REPO_ROOT / "results" / "pass1_window_r2_v2.jsonl", keep=dev)

    assert len(on_the_dev_pod) == len(union) == 200 == len(dev)
    assert union == on_the_dev_pod, "200 of 200, one for one, across three pods"
