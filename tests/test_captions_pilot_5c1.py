"""Offline tests for the ATB caption pilot — no Telegram, no OpenRouter, no spend.

Both scripts under test spend something real (a network session, then money), so what is guarded
here is the two ways a pilot silently buys the wrong thing: fetching a population that is not the
one the census priced, and letting a cap or a retry arrive by import from another phase.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import caption_atb_5c1 as captioner  # noqa: E402
import caption_posts as pattern  # noqa: E402
import fetch_atb_media_5c1 as fetcher  # noqa: E402

CENSUS = json.loads((REPO_ROOT / "results" / "image_census_5c1.json").read_text("utf-8"))


# --- the population is the one the census priced --------------------------------------------------


def test_the_fetch_reads_its_population_out_of_the_committed_census():
    """The census named 19 ids and is committed; a fetch that re-derived its own list could buy
    captions for a different 19 and nothing downstream would see the substitution."""
    ids = fetcher.population(CENSUS, fetcher.HANDLE)
    assert len(ids) == 19
    assert ids == sorted(set(ids))
    atb = next(row for row in CENSUS["sources"] if row["handle"] == fetcher.HANDLE)
    assert ids == sorted(atb["uncaptioned_msg_ids"])


def test_the_fetch_refuses_a_census_whose_count_and_ids_disagree():
    """The negative control: a record that counts 19 and names 18 is a record of a population
    that was priced and a population that would be bought, and they are not the same one."""
    doctored = json.loads(json.dumps(CENSUS))
    row = next(r for r in doctored["sources"] if r["handle"] == fetcher.HANDLE)
    row["uncaptioned_msg_ids"] = row["uncaptioned_msg_ids"][:-1]
    with pytest.raises(SystemExit, match="is not the one that was priced"):
        fetcher.population(doctored, fetcher.HANDLE)


def test_the_fetch_writes_a_manifest_the_captioner_can_read(tmp_path):
    """The write path, driven with a stub instead of Telegram: an import proves nothing, and the
    manifest's shape is a contract between two scripts that never run in the same process."""
    media, manifest = tmp_path / "media", tmp_path / "manifest.json"
    media.mkdir()
    image = media / "atb_market_official_4340.jpg"
    image.write_bytes(b"not really a jpeg")

    def runner():
        return {
            (fetcher.HANDLE, 4340): {
                "items": [{"msg_id": 4340, "file": str(image), "sha256": "0" * 64, "bytes": 17}],
                "poll": None,
            }
        }, [4350]

    assert (
        fetcher.main(
            ["--media", str(media), "--manifest", str(manifest)],
            runner=runner,
        )
        == 1  # posts still owed is a non-zero exit: an incomplete fetch is not a finished step
    )
    written = json.loads(manifest.read_text(encoding="utf-8"))
    assert written["still_owed"] == [4350]
    assert written["population"]["asked"] == 19
    entry = written["entries"][f"{fetcher.HANDLE}:4340"]
    assert entry["post_has_text"] is False and len(entry["images"]) == 1

    # The manifest is read by `caption_posts.population`, which sorts posts into the three classes
    # the pilot pays for, transcribes free, or cannot speak for at all.
    images, polls, blind = pattern.population(written)
    assert [entry["name"] for entry in images] == [f"{fetcher.HANDLE}:4340"]
    assert polls == [] and len(blind) == 18


def test_a_flood_wait_longer_than_the_cap_is_not_slept_through():
    """`fetch_post_media` sleeps a wall out in full. This account lost 20 hours to one, so the
    pilot stops and reports the ids it still owes instead."""
    assert fetcher.MAX_FLOOD_SLEEP <= 600
    source = Path(fetcher.__file__).read_text(encoding="utf-8")
    assert "if exc.seconds > MAX_FLOOD_SLEEP:" in source
    assert "still owed" in source


# --- the paid step's constants are its own --------------------------------------------------------


def test_the_pilot_declares_its_own_cap_anchor_and_output_paths():
    """A cap or an output path imported from another phase is the whole footgun: 4.5g2's ledger
    holds a $0.75 budget and its caption file is a committed labelling input."""
    assert captioner.CAP_USD == 0.10
    assert captioner.PHASE == "5c1captions"
    assert captioner.LEDGER != pattern.LEDGER
    assert captioner.CAPTIONS != pattern.CAPTIONS
    assert captioner.RECORD != pattern.RECORD
    assert captioner.CAP_USD < pattern.CAP_USD
    # The anchor key is the phase's own, so spending against another phase's balance is a refusal
    # rather than a silent re-baselining of this cap.
    assert captioner.anchor_key() == "openrouter_total_usage_at_5c1captions_start"


def test_the_pilot_asks_once_and_does_not_retry_a_paid_call():
    """The brief says one attempt, no retry loops. 4.5g2's `Asker` carries `attempts=6`, and
    importing it verbatim would import a six-fold re-bill of every failing request."""
    assert captioner.ATTEMPTS == 1
    calls = []

    class Boom(Exception):
        pass

    def caller():
        calls.append(1)
        raise OSError("connection reset")

    with pytest.raises(OSError):
        captioner.ask_once(caller)
    assert len(calls) == 1


def test_the_pilot_uses_the_registered_prompt_and_the_45g2_model(tmp_path):
    """An instrument swap is not a pilot of the same instrument. The model, the endpoint pin and
    the prompt hash all have to be 4.5g2's, or step 4's before/after compares two things."""
    from market_pulse import prompts

    assert captioner.MODEL == pattern.MODEL
    assert captioner.PINNED == pattern.VISION[pattern.MODEL]
    assert captioner.TASK == prompts.CAPTION_TASK == "caption_post"
    assert (
        prompts.prompt_sha256(captioner.TASK)
        == "5dd76ab27fe574a7cf345d82c13f9e69e1683a385c2a9241172b214ea6366193"
    ), "the registered caption_post prompt moved — this is an instrument swap, not a pilot"


def test_the_pilot_stops_when_the_cap_would_be_crossed(tmp_path):
    """The cap is the operator's, and a budget guard that only warned would be a suggestion."""
    from market_pulse import zero_shot

    budget = zero_shot.Budget(captioner.CAP_USD, captioner.CAP_USD)
    budget.add(0.09)
    with pytest.raises(zero_shot.BudgetExceeded):
        budget.add(0.02)


def test_the_pilot_writes_captions_and_a_record_without_touching_the_network(tmp_path):
    """`--smoke` drives the whole write path with a fake asker: the captions file, the record and
    the cost block all exist before a cent is spent."""
    manifest = tmp_path / "manifest.json"
    media = tmp_path / "media"
    media.mkdir()
    (media / "atb_market_official_4340.jpg").write_bytes(b"not really a jpeg")
    manifest.write_text(
        json.dumps(
            {
                "channel": fetcher.HANDLE,
                "entries": {
                    f"{fetcher.HANDLE}:4340": {
                        "channel": fetcher.HANDLE,
                        "msg_id": 4340,
                        "post_has_text": False,
                        "images": [
                            {
                                "file": str(media / "atb_market_official_4340.jpg"),
                                "sha256": "0" * 64,
                            }
                        ],
                        "poll": None,
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out, record = tmp_path / "captions.jsonl", tmp_path / "record.json"
    assert (
        captioner.main(
            [
                "--manifest",
                str(manifest),
                "--out",
                str(out),
                "--record",
                str(record),
                "--smoke",
            ]
        )
        == 0
    )
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert [row["msg_id"] for row in rows] == [4340]
    assert rows[0]["kind"] == "image" and rows[0]["caption"]
    written = json.loads(record.read_text(encoding="utf-8"))
    assert written["smoke"] is True
    assert written["cost"]["cap_usd"] == captioner.CAP_USD
    assert written["prompt_sha256"][captioner.TASK]


def test_a_smoke_run_on_the_default_paths_lands_in_the_smoke_directory(tmp_path, monkeypatch):
    """Otherwise the rehearsal fills the paid artifacts with fake captions, and the real run then
    refuses to overwrite the fake ones — the pilot buys nothing and the file looks bought."""
    captured = {}
    monkeypatch.setattr(
        captioner, "refuse_to_overwrite", lambda out, record: captured.update(out=out, rec=record)
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"entries": {}}), encoding="utf-8")
    assert captioner.main(["--manifest", str(manifest), "--smoke", "--dry-run"]) == 0
    assert captured["out"].parent.name == "smoke"
    assert captured["rec"].parent.name == "smoke"


# --- step 4: the matcher over the captions --------------------------------------------------------


REMATCH = json.loads((REPO_ROOT / "results" / "caption_rematch_5c1.json").read_text("utf-8"))


def test_the_rematch_reproduces_the_signed_screens_zero_before_reporting_an_after():
    """The before is a control, not a quote. If this file cannot re-derive the zero the operator
    signed against, its after is a number about a different instrument."""
    screen = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    atb = next(row for row in screen["sources"] if row["handle"] == "@atb_market_official")
    assert REMATCH["verdicts_reportable"] is True
    assert all(control["ok"] for control in REMATCH["controls"].values())
    assert REMATCH["before"]["relevant_posts"] == atb["relevant_posts"] == 0
    assert REMATCH["posts_in_window"] == atb["posts"]["in_window"] == 25
    assert REMATCH["window"]["source"] == atb["window"]["source"]


def test_reading_the_images_turns_the_failed_control_into_a_pass():
    """The pilot's whole question. 0 → 13 of 25, against a bar of 4."""
    bars = json.loads(
        (REPO_ROOT / "results" / "yield_bars_5c1.preregistration.json").read_text("utf-8")
    )
    assert REMATCH["instrument"]["preregistration"]["bar_A_relevant_posts_28d"] == 4
    assert bars["bar_A_relevant_posts_28d"] == 4, "the bars did not move for this reading"
    assert REMATCH["before"]["bar_A"] == "FAIL"
    assert REMATCH["after"]["bar_A"] == "PASS"
    assert REMATCH["after"]["relevant_posts"] == 13


def test_the_pass_does_not_hang_on_the_private_label_or_on_any_single_term():
    """«Своя Лінія» is ATB's own label and is printed on a leaflet's diapers as readily as on its
    cheese. A pass that needed it would be a pass about the leaflet's header, so the strict
    category-only reading is published beside the headline and clears the bar on its own."""
    assert REMATCH["after"]["by_term"]["brand:svoia-liniia"] == 12
    assert REMATCH["after"]["relevant_on_category_alone"] == 10
    assert REMATCH["after"]["bar_A_on_category_alone"] == "PASS"
    assert REMATCH["after"]["bar_A_sole_carriers"] == []


def test_every_miss_is_named_and_the_word_is_defined():
    """«Промах» has two readings and only one of them is a count; the other is a judgement about a
    quoted line, so every post in the record carries its evidence."""
    assert REMATCH["captioned_posts"]["misses"]["definition"].startswith("a post whose surrogate")
    assert REMATCH["captioned_posts"]["misses"]["msg_ids"] == [4370, 4391, 4415, 4455, 4519]
    assert REMATCH["captioned_posts"]["n"] == 18
    for post in REMATCH["posts"]:
        assert bool(post["terms"]) == bool(post["evidence"]), post["msg_id"]


def test_the_quoted_captions_are_in_the_file_they_are_quoted_from():
    """The three captions the report shows the operator, grepped back to the paid artifact."""
    captions = (
        REPO_ROOT / "data" / "annotation" / "captions_5c1" / "atb_captions.jsonl"
    ).read_text("utf-8")
    for quote in (
        "Морозиво пломбір, у вафельному стаканчику, 80 г ТМ «Київський Пломбір» — 21.90 грн",
        "Підгузки-трусики/ Підгузки дитячі «MiniBee», в асортименті, 25 шт/28 шт/ 40 шт/ 44 шт",
        "АТБ з 23.07.26 по 29.07.26 АКЦІЯ «7 ДНІВ» до -43%* Літак-планер",
    ):
        assert captions.count(quote) == 1, quote


def test_the_paid_record_and_the_rematch_read_the_same_captions():
    """One caption file, two readers. A rematch over a different set would be unprovable later."""
    import hashlib

    paid = json.loads((REPO_ROOT / "results" / "captions_5c1.json").read_text("utf-8"))
    path = REPO_ROOT / paid["out"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == paid["out_sha256"]
    assert REMATCH["instrument"]["captions"]["sha256"] == paid["out_sha256"]
    assert REMATCH["instrument"]["captions"]["rows"] == paid["population"]["captioned"] == 18
