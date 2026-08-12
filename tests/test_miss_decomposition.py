"""The team lead's decomposition of bar 1's 29 misses, transcribed onto the pack's rows.

The expensive failure is quiet: a row number that means a different pair than the team lead had in
front of them re-scopes the B′ gold with a verdict that was never given. So the sheet is pinned as
well as the record, the counts come from the contract rather than from the table, and every
`refusal:*` ruling is held against the reason the extractor itself wrote on that page.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import apply_miss_decomposition as apply  # noqa: E402


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    path = tmp_path_factory.mktemp("decomp") / "decomposition.json"
    assert apply.main(["--out", str(path)]) == 0
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pack():
    return json.loads(apply.PACK.read_text(encoding="utf-8"))


def test_the_counts_are_the_ones_the_contract_states(out):
    """`docs/PROMPT-skub2-prep.md`: «a=11 · b=12 · c=2 · pending=4» over the pack's 29 rows."""
    assert out["counts"] == {"a": 11, "b": 12, "c": 2, "pending": 4, "rows": 29}
    assert out["expected"] == apply.EXPECTED
    assert out["counts"] == {**apply.EXPECTED}
    assert len(apply.DICTATED) == 25 and len(apply.PENDING) == 4


def test_every_pack_row_is_ruled_on_or_deferred_exactly_once(out, pack):
    ruled = [row["n"] for row in out["rows"]]
    assert ruled == sorted(ruled) == [row["n"] for row in pack["missed"]]
    assert len(set(ruled)) == len(ruled) == 29
    for row, packed in zip(out["rows"], pack["missed"], strict=True):
        assert (row["item"], row["gold_key"]) == (packed["item"], packed["gold_key"])


def test_the_four_pending_pairs_are_deferred_and_carry_their_pages(out):
    """They are three `svoia-liniia` rows and a `try-vedmedi` — the classes ruled on the rows
    beside them are exactly what must NOT be copied onto these four."""
    pending = [row for row in out["rows"] if row["verdict"] == "PENDING_TEAM_LEAD"]
    assert [row["n"] for row in pending] == [4, 9, 28, 29] == list(apply.PENDING)
    assert out["pending_rows"] == [4, 9, 28, 29]
    for row in pending:
        assert row["mechanism"] is None, row["n"]
        assert row["pages"], row["n"]
        for page in row["pages"]:
            assert set(page) >= {"page", "file", "sha256", "answer"}
    assert all("pages" not in row for row in out["rows"] if row["verdict"] != "PENDING_TEAM_LEAD")


def test_the_b_prime_denominator_stays_open_while_a_pair_is_pending(out):
    block = out["b_prime_denominator"]
    assert block["bar_1_gold_pairs"] == 55
    assert block["removed_by_class"] == {"b": 12, "c": 2}
    assert block["remaining_if_no_pending_pair_leaves"] == 41
    assert block["pending"] == 4
    assert block["final"] is None


def test_every_refusal_ruling_names_the_page_the_extractor_refused(out):
    """The one check here that is not a transcription. 4401's page 5 came back `malformed JSON`
    (the truncated reply at the 800-token ceiling), 4446's page 1 on the multipack size and both
    `-50%*` pages on the asterisk — and the read's mechanisms have to land on those posts."""
    seen = {}
    for row in out["rows"]:
        if row["mechanism"] in apply.REFUSAL_REASON:
            reasons = {page["reason"] for page in row["unreadable_pages"]}
            assert reasons == {apply.REFUSAL_REASON[row["mechanism"]]}, row["n"]
            seen.setdefault(row["mechanism"], set()).add(row["msg_id"])
    assert seen == {
        "refusal:asterisk": {4340, 4467},
        "refusal:token-ceiling": {4401},
        "refusal:multipack": {4446},
    }
    assert out["mechanism_evidence"]["checked"] == 11  # the 10 refusals and the one alias gap


def test_the_alias_gap_sits_on_a_post_with_an_unmatched_extraction(out):
    """Row 2 is «Три Ведмеді» on 4340, where the instrument extracted `raw:three bears` and no gold
    key matched it. That is what makes the ruling an alias gap rather than a vision miss."""
    alias = [row for row in out["rows"] if row["mechanism"] == apply.ALIAS_MECHANISM]
    assert [row["n"] for row in alias] == [2]
    assert alias[0]["msg_id"] == 4340
    assert alias[0]["gold_key"] == "raw:try-vedmedi"
    assert alias[0]["unmatched_extractions_on_this_post"] == ["raw:three bears"]
    assert alias[0]["verdict"] == "a"


def test_the_by_pattern_caveat_is_carried_not_tidied(out):
    """Row 14 was ruled from the rows beside it, because its own page came back refused. The
    caveat is the difference between a verdict from an image and a verdict from a neighbour."""
    row = next(row for row in out["rows"] if row["n"] == 14)
    assert row["mechanism"] == "non-dairy, by-pattern"
    assert row["verdict"] == "b"
    assert [page["page"] for page in row["unreadable_pages"]] == [5]


def test_row_8_is_the_gold_key_artifact(out):
    """The team lead's own words: the brand WAS found — «Комо / Komo» is one reviewer string that
    became one gold key, and the instrument answered «Komo». Class c, and it leaves the B′ gold."""
    row = next(row for row in out["rows"] if row["n"] == 8)
    assert row["gold_key"] == "raw:комо / komo"
    assert row["verdict"] == "c"
    assert row["mechanism"] == "gold-key artifact — brand was found"
    assert row["unmatched_extractions_on_this_post"] == ["raw:komo"]


def test_the_mechanisms_add_up_to_the_rows(out):
    assert sum(out["by_mechanism"].values()) == 29
    assert out["by_mechanism"]["PENDING_TEAM_LEAD"] == 4
    assert out["by_mechanism"]["refusal:token-ceiling"] == 5


def test_nothing_here_claims_to_be_a_verdict(out):
    assert out["class"].startswith("TRANSCRIPTION")
    assert "SPEC §10" in out["authority"]
    assert out["read_by"] == "the team lead"
    assert "only the images can say" in out["mechanism_evidence"]["note"]


# --- the refusals ---------------------------------------------------------------------------------


def run(tmp_path, argv=()):
    return apply.main([*argv, "--out", str(tmp_path / "p.json")])


def test_a_moved_pack_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(apply, "PACK_SHA", "f" * 64)
    with pytest.raises(SystemExit, match="the rows the dictation numbers are not these rows"):
        run(tmp_path)


def test_a_moved_sheet_refuses(monkeypatch, tmp_path):
    """The numbers 1..29 are printed in the MARKDOWN, so the markdown is what has to be unmoved."""
    monkeypatch.setattr(apply, "SHEET_SHA", "f" * 64)
    with pytest.raises(SystemExit, match="the sheet the team lead had open has moved"):
        run(tmp_path)


def test_a_row_ruled_twice_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(apply, "DICTATED", apply.DICTATED + ((3, "a", "maker-logo"),))
    with pytest.raises(SystemExit, match="row 3 is ruled on twice"):
        run(tmp_path)


def test_a_row_nobody_ruled_on_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(apply, "DICTATED", apply.DICTATED[:-1])
    with pytest.raises(SystemExit, match=r"pack row\(s\) nobody ruled on"):
        run(tmp_path)


def test_a_pending_pair_quietly_ruled_refuses_on_the_count(monkeypatch, tmp_path):
    """Guessing #4 from the five `svoia-liniia` rows beside it is the failure this contract names
    by number, and the contract's own counts are what stop it. The guess moves TWO of them — the
    class it is guessed into and `pending` — and the class is the one checked first."""
    monkeypatch.setattr(apply, "DICTATED", apply.DICTATED + ((4, "b", "non-dairy watchlist item"),))
    monkeypatch.setattr(apply, "PENDING", (9, 28, 29))
    with pytest.raises(SystemExit, match="the read states b = 12 and the table joins to 13"):
        run(tmp_path)
    monkeypatch.setitem(apply.EXPECTED, "b", 13)  # and now `pending` is the one left standing
    with pytest.raises(SystemExit, match="the read states pending = 4 and the table joins to 3"):
        run(tmp_path)


def test_a_refusal_ruled_on_the_wrong_page_refuses(monkeypatch, tmp_path):
    """Row 20 is 4446, whose page refused on the multipack size. Called an asterisk refusal it has
    to fail — this is the check a slipped row numbering runs into."""
    swapped = tuple(
        (n, verdict, "refusal:asterisk" if n == 20 else mechanism)
        for n, verdict, mechanism in apply.DICTATED
    )
    monkeypatch.setattr(apply, "DICTATED", swapped)
    with pytest.raises(SystemExit, match=r"row 20 \(4446\) is ruled refusal:asterisk"):
        run(tmp_path)


def test_a_refusal_ruled_on_a_post_that_refused_nothing_refuses(monkeypatch, tmp_path):
    swapped = tuple(
        (n, verdict, "refusal:multipack" if n == 3 else mechanism)
        for n, verdict, mechanism in apply.DICTATED
    )
    monkeypatch.setattr(apply, "DICTATED", swapped)
    with pytest.raises(SystemExit, match=r"row 3 \(4350\) is ruled refusal:multipack"):
        run(tmp_path)


def test_an_unknown_refusal_mechanism_refuses(monkeypatch, tmp_path):
    """A new refusal family must be given its reason string, not waved through as prose."""
    swapped = tuple(
        (n, verdict, "refusal:blur" if n == 1 else mechanism)
        for n, verdict, mechanism in apply.DICTATED
    )
    monkeypatch.setattr(apply, "DICTATED", swapped)
    with pytest.raises(SystemExit, match="is a refusal this file has no reason string for"):
        run(tmp_path)


def test_an_alias_ruling_with_nothing_unmatched_refuses(monkeypatch, tmp_path):
    swapped = tuple(
        (n, verdict, apply.ALIAS_MECHANISM if n == 3 else mechanism)
        for n, verdict, mechanism in apply.DICTATED
    )
    monkeypatch.setattr(apply, "DICTATED", swapped)
    with pytest.raises(SystemExit, match="the instrument extracted nothing unmatched on that post"):
        run(tmp_path)


def test_a_class_outside_the_pack_vocabulary_refuses(monkeypatch, tmp_path):
    """The team lead owns the vocabulary; a fourth class invented here is not a verdict."""
    swapped = tuple(
        (n, "d" if n == 3 else verdict, mechanism) for n, verdict, mechanism in apply.DICTATED
    )
    monkeypatch.setattr(apply, "DICTATED", swapped)
    with pytest.raises(SystemExit, match=r"row 3: class 'd' is not one of \['a', 'b', 'c'\]"):
        run(tmp_path)


def test_a_moved_count_refuses(monkeypatch, tmp_path):
    monkeypatch.setitem(apply.EXPECTED, "b", 13)
    with pytest.raises(SystemExit, match="the read states b = 13 and the table joins to 12"):
        run(tmp_path)


# --- the shipped record ---------------------------------------------------------------------------


def test_the_shipped_decomposition_is_the_one_this_script_writes(out):
    """`git` is the only field that legitimately differs: it names the tree, not the rows."""
    shipped = json.loads(apply.OUT.read_text(encoding="utf-8"))
    assert shipped.pop("git")["commit"]
    assert shipped == {key: value for key, value in out.items() if key != "git"}


def test_the_pinned_pack_is_the_committed_pack():
    """The read was taken against `0001cd9`; a pack rebuilt since would move rows under numbers."""
    for path, pinned in ((apply.PACK, apply.PACK_SHA), (apply.SHEET, apply.SHEET_SHA)):
        rel = str(path.relative_to(REPO_ROOT))
        blob = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        ).stdout
        assert hashlib.sha256(blob).hexdigest() == pinned, rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == pinned, rel
