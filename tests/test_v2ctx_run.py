"""What the v2ctx run sends, and what it is allowed to spend before it sends it.

The revision this run measures lives in the request and nowhere else — no prompt text moved, so
no hash moved. That makes one test load-bearing above all the others: the flags the committed
plan pre-registered have to reach the wire, and a row the plan calls featureless has to go out
as the v2 request byte for byte. The rest is the money: three readings of what the closed phases
spent have to agree before a request is made, because the headroom under the shared cap is the
only thing standing between a pre-registered hundred and an unpriced run.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_v2ctx_probe as run  # noqa: E402
from recheck_with_captions import Asker  # noqa: E402

from market_pulse import prompts, zero_shot  # noqa: E402

REPLY = '{"sentiment": "neutral", "sarcasm": false, "intents": [], "unclear": false}'


def sent_by(monkeypatch, row, task=run.TASK):
    """The request body the real Asker builds for one row — captured, never re-rendered here."""
    bodies = []

    def fake_post(path, payload, key, **kwargs):
        bodies.append(payload)
        return ({"choices": [{"message": {"content": REPLY}}], "usage": {"cost": 0.0}}, {})

    monkeypatch.setattr(zero_shot, "post", fake_post)
    ask = Asker("key", "model", "tag", "fp8", zero_shot.Budget(1.0, 1.0))
    ask(task, row)
    return bodies[0]["messages"][0]["content"]


def row(**over):
    base = {
        "id": "@VARUS_channel:1",
        "text": "текст",
        "parent": "Акція на молоко",
        "caption": None,
        "caption_kind": None,
        "reply": False,
        "sender": None,
    }
    return {**base, **over}


def test_the_planned_flags_reach_the_wire(monkeypatch):
    """One render path from plan to request. A probe whose context lived only in a plan file
    would measure v2 under a new name and nothing in the record could tell."""
    content = sent_by(monkeypatch, row(reply=True, sender="@msuaaaa"))
    assert prompts.REPLY_CONTEXT in content
    assert prompts.SENDER_CONTEXT["@msuaaaa"] in content
    assert (
        content.index("</post>") < content.index(prompts.REPLY_CONTEXT) < content.index("<comment>")
    )


def test_a_featureless_row_goes_out_as_the_v2_request(monkeypatch):
    """The byte-identity property, on the wire rather than on a rendered string."""
    ctx = sent_by(monkeypatch, row())
    v2 = sent_by(monkeypatch, row(), task="precheck_v2_with_post")
    assert ctx == v2
    assert "[reply]" not in ctx and "[sender]" not in ctx


def test_one_flag_renders_one_line(monkeypatch):
    only_sender = sent_by(monkeypatch, row(sender="@VARUS_channel"))
    assert prompts.SENDER_CONTEXT["@VARUS_channel"] in only_sender
    assert prompts.REPLY_CONTEXT not in only_sender


def test_the_context_counters_count_what_is_about_to_be_sent():
    rows = [row(reply=True), row(sender="@msuaaaa"), row(reply=True, sender="@msuaaaa"), row()]
    assert run.rendered_context(rows) == {
        "reply": 2,
        "sender": 2,
        "both": 1,
        "neither": 1,
        "lines": 4,
    }


def ledger(tmp_path, name, usd):
    path = tmp_path / name
    path.write_text(json.dumps({"runs": [{"usd": usd}]}), encoding="utf-8")
    return path


def record(tmp_path, name, usd):
    path = tmp_path / name
    path.write_text(json.dumps({"runs": [{"cost": {"phase_spend_usd": usd}}]}), encoding="utf-8")
    return path


def empty(tmp_path, name="spend_45g5.json", runs=()):
    path = tmp_path / name
    path.write_text(json.dumps({"runs": list(runs)}), encoding="utf-8")
    return path


def test_the_prior_spend_is_three_readings_that_have_to_agree(tmp_path):
    pairs = (
        (ledger(tmp_path, "a.json", 0.7429), record(tmp_path, "ar.json", 0.7429)),
        (ledger(tmp_path, "b.json", 0.0365), record(tmp_path, "br.json", 0.0365)),
    )
    assert run.prior_total(pairs, empty(tmp_path)) == pytest.approx(0.7794, abs=1e-6)


def test_a_ledger_that_disagrees_with_its_record_stops_the_run(tmp_path):
    pairs = ((ledger(tmp_path, "a.json", 0.7429), record(tmp_path, "ar.json", 0.60)),)
    with pytest.raises(SystemExit, match="disagree"):
        run.prior_total(pairs, empty(tmp_path))


def test_a_total_the_briefing_does_not_recognise_stops_the_run(tmp_path):
    """The number stated in passing is the check: if the closed phases sum to something else,
    the headroom this run thinks it has is not the headroom it has."""
    pairs = ((ledger(tmp_path, "a.json", 0.50), record(tmp_path, "ar.json", 0.50)),)
    with pytest.raises(SystemExit, match="states"):
        run.prior_total(pairs, empty(tmp_path))


def test_a_zero_spend_phase_with_a_run_in_it_stops_the_run(tmp_path):
    """4.5g5 pre-registered itself at $0.00. A run in that ledger means the tripwire fired and
    nobody noticed, and every headroom computed since is wrong by that amount."""
    pairs = (
        (ledger(tmp_path, "a.json", 0.7429), record(tmp_path, "ar.json", 0.7429)),
        (ledger(tmp_path, "b.json", 0.0365), record(tmp_path, "br.json", 0.0365)),
    )
    with pytest.raises(SystemExit, match="pre-registered at \\$0.00"):
        run.prior_total(pairs, empty(tmp_path, runs=[{"usd": 0.01}]))


def test_the_real_ledgers_agree_with_the_briefing():
    """Not a fixture: the files this phase will actually read."""
    assert run.prior_total() == pytest.approx(run.PRIOR_EXPECTED, abs=0.01)


def test_a_template_edit_after_the_plan_is_an_instrument_change(tmp_path, monkeypatch):
    """The plan pins the three sentences because the prompt hash cannot. Editing one and running
    anyway would score a rendering nobody registered."""
    plan = json.loads((REPO_ROOT / "results" / "v2ctx_probe_plan.json").read_text())
    plan["rendering"]["templates"][0] = "[reply] Something else entirely."
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit, match="does not render"):
        run.main(["--plan", str(path), "--skip-git-check", "--dry-run"])


def test_a_plan_for_another_task_is_refused(tmp_path):
    plan = json.loads((REPO_ROOT / "results" / "v22_probe_plan.json").read_text())
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit, match="plans precheck_v2.2_with_post"):
        run.main(["--plan", str(path), "--skip-git-check", "--dry-run"])
