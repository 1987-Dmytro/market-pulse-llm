"""`caption_source`: every new caption record names the instrument that wrote it.

SPEC amendment 3.13 (3) creates a comparability seam — the 4.5g2 API captions on disk and the
captions the project's own GM4 writes are two instruments, and "numbers with different caption
sources are never compared without saying so" is only enforceable if every row says which one it
is. What is pinned here: the field is required on a new record, an old file without it resolves
to the instrument that actually wrote it, a poll is not a third instrument, and neither reader
will average two of them in silence.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import local_llm, parents, prompts  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pattern = _script("caption_posts")
rematch = _script("rematch_with_captions_5c1")
recheck = _script("recheck_with_captions")

GM4_SOURCE = "gm4-nf4-base"


# --- caption_source provenance ----------------------------------------------


def entry(msg_id: int = 1) -> dict:
    return {"channel": "@c", "msg_id": msg_id, "images": [{"file": "a.jpg", "sha256": "x"}]}


def test_a_new_caption_record_must_name_its_instrument():
    with pytest.raises(TypeError):
        pattern.record_for(entry(), "text", "image", "m", 1)
    with pytest.raises(ValueError, match="disagree"):
        pattern.record_for(entry(), "text", "image", "some/model", 1, None)
    with pytest.raises(ValueError, match="disagree"):
        pattern.record_for(entry(), "text", "image", None, 0, "gm4-nf4-base")


def test_the_two_instruments_write_the_two_registered_values():
    qwen = pattern.record_for(entry(), "t", "image", pattern.MODEL, 1, pattern.SOURCE)
    gm4 = pattern.record_for(
        entry(), "t", "image", local_llm.MODEL_ID, 1, GM4_SOURCE, task=prompts.CAPTION_TASK_GM4
    )
    assert {qwen["caption_source"], gm4["caption_source"]} == set(parents.CAPTION_SOURCES)
    assert qwen["prompt_sha256"] == prompts.prompt_sha256(prompts.CAPTION_TASK)
    assert gm4["prompt_sha256"] == prompts.prompt_sha256(prompts.CAPTION_TASK_GM4)


def test_a_poll_row_is_not_a_third_instrument():
    """Its text is Telegram's own question and options, transcribed. No model, so no source —
    and the fallback keys on `model`, not on the mere absence of the field."""
    poll = pattern.record_for(
        {**entry(), "poll": {"question": "q", "options": ["a"]}, "images": []},
        "q\n— a",
        "poll",
        None,
        0,
        None,
    )
    assert poll["caption_source"] is None and parents.caption_source(poll) is None


def test_an_old_caption_row_resolves_to_the_instrument_that_wrote_it():
    """Amendment 3.13 (3): the bought 4.5g2 captions stand as history and their files are not
    rewritten, so the field is missing rather than wrong."""
    assert parents.caption_source({"model": "qwen/qwen3.5-flash-02-23"}) == parents.LEGACY_SOURCE
    assert parents.caption_source({"model": None}) is None
    with pytest.raises(ValueError, match="not one of"):
        parents.caption_source({"caption_source": "gpt-whatever"})


def test_the_committed_caption_files_still_read_as_one_instrument():
    """The negative control the fixtures cannot give: the real 4.5g2 and 5c1 caption files."""
    for captions, record in (
        (
            REPO_ROOT / "data" / "annotation" / "post_captions.jsonl",
            REPO_ROOT / "results" / "captions_45g2.json",
        ),
        (
            REPO_ROOT / "data" / "annotation" / "captions_5c1" / "atb_captions.jsonl",
            REPO_ROOT / "results" / "captions_5c1.json",
        ),
    ):
        if not captions.exists():  # gitignored payload, absent on a bare checkout
            continue
        rows = parents.read_caption_rows(captions)
        named = parents.sources_named(json.loads(record.read_text(encoding="utf-8")))
        assert parents.assert_one_source(captions.name, rows, named) == {parents.LEGACY_SOURCE}


# --- the readers refuse a silent mix ----------------------------------------


def caption_file(path: Path, sources: list[str | None]) -> Path:
    path.write_text(
        "".join(
            json.dumps(
                {
                    "channel": "@atb_market_official",
                    "msg_id": 100 + n,
                    "kind": "image",
                    "caption": f"c{n}",
                    "model": "m" if source else None,
                    "caption_source": source,
                    "images": [],
                    "poll": None,
                }
            )
            + "\n"
            for n, source in enumerate(sources)
        ),
        encoding="utf-8",
    )
    return path


def test_a_mixed_caption_file_is_refused_unless_the_record_names_both():
    rows = [{"caption_source": s, "model": "m"} for s in parents.CAPTION_SOURCES]
    with pytest.raises(SystemExit, match="mixes caption instruments"):
        parents.assert_one_source("x.jsonl", rows, set())
    with pytest.raises(SystemExit, match="mixes caption instruments"):
        parents.assert_one_source("x.jsonl", rows, {parents.LEGACY_SOURCE})
    assert parents.assert_one_source("x.jsonl", rows, set(parents.CAPTION_SOURCES)) == set(
        parents.CAPTION_SOURCES
    )


def test_one_instrument_never_needs_declaring():
    rows = [{"model": "m"}, {"caption_source": parents.LEGACY_SOURCE, "model": "m"}]
    assert parents.assert_one_source("x.jsonl", rows, set()) == {parents.LEGACY_SOURCE}


def test_the_rematch_reader_refuses_a_mix(tmp_path):
    captions = caption_file(tmp_path / "mixed.jsonl", list(parents.CAPTION_SOURCES))
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"caption_sources": [parents.LEGACY_SOURCE]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="mixes caption instruments"):
        rematch.load_captions(captions, record)
    record.write_text(
        json.dumps({"caption_sources": list(parents.CAPTION_SOURCES)}), encoding="utf-8"
    )
    assert set(rematch.load_captions(captions, record)) == {100, 101}


def test_the_recheck_reader_refuses_a_mix(tmp_path):
    """The same guard on the other path. A guard on one path is not a guard."""
    captions = caption_file(tmp_path / "mixed.jsonl", list(parents.CAPTION_SOURCES))
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"runs": [{"kinds": {"image": 2}}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="mixes caption instruments"):
        recheck.caption_input(captions, record)
    record.write_text(
        json.dumps(
            {"runs": [{"kinds": {"image": 2}, "caption_sources": list(parents.CAPTION_SOURCES)}]}
        ),
        encoding="utf-8",
    )
    _, written, sources = recheck.caption_input(captions, record)
    assert written == {"image": 2} and sources == set(parents.CAPTION_SOURCES)


def test_a_record_that_predates_the_field_names_nothing_and_that_is_correct():
    assert parents.sources_named({"runs": [{"kinds": {"image": 21}}]}) == set()
    assert parents.sources_named({"kinds": {"image": 19}}) == set()
    assert parents.sources_named({"caption_sources": ["gm4-nf4-base"]}) == {"gm4-nf4-base"}
    assert parents.sources_named({"runs": [{"caption_sources": ["gm4-nf4-base"]}]}) == {
        "gm4-nf4-base"
    }
