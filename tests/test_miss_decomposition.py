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
    """`docs/PROMPT-skub2-fix.md`: «a=11 · b=16 · c=2 · pending=0» over the pack's 29 rows.

    The first read's line was «a=11 · b=12 · c=2 · pending=4», and the delta is exactly the four
    that were pending: b gains four and nothing else moves.
    """
    assert out["counts"] == {"a": 11, "b": 16, "c": 2, "pending": 0, "rows": 29}
    assert out["expected"] == apply.EXPECTED
    assert out["counts"] == {**apply.EXPECTED}
    assert len(apply.DICTATED) == 29 and apply.PENDING == ()
    was = {"a": 11, "b": 12, "c": 2, "pending": 4}
    moved = {name for name in was if out["counts"][name] != was[name]}
    assert moved == {"b", "pending"}


def test_every_pack_row_is_ruled_on_or_deferred_exactly_once(out, pack):
    ruled = [row["n"] for row in out["rows"]]
    assert ruled == sorted(ruled) == [row["n"] for row in pack["missed"]]
    assert len(set(ruled)) == len(ruled) == 29
    for row, packed in zip(out["rows"], pack["missed"], strict=True):
        assert (row["item"], row["gold_key"]) == (packed["item"], packed["gold_key"])


def test_the_four_that_were_pending_came_back_as_class_b_with_their_pages(out):
    """SPEC 3.17 (14)(a). Three `svoia-liniia` rows and a `try-vedmedi`, deferred because the
    classes ruled on the rows beside them were exactly what must NOT be copied onto them — and read
    back page by page. The page citations are what makes the second read evidence rather than the
    guess the first read refused to make."""
    four = [row for row in out["rows"] if row["n"] in (4, 9, 28, 29)]
    assert [row["n"] for row in four] == [4, 9, 28, 29]
    assert out["pending_rows"] == [] and apply.PENDING == ()
    assert not [row for row in out["rows"] if row["verdict"] == "PENDING_TEAM_LEAD"]
    for row in four:
        assert row["verdict"] == "b", row["n"]
        assert row["mechanism"] == "non-dairy watchlist item", row["n"]
        assert row["pages_read"]["pages"] and row["pages_read"]["saw"], row["n"]
    assert [row["gold_key"] for row in four] == [
        "raw:svoia-liniia",
        "raw:svoia-liniia",
        "raw:svoia-liniia",
        "raw:try-vedmedi",
    ]
    assert {row["n"] for row in out["rows"] if "pages_read" in row} == {4, 9, 28, 29}
    assert out["mechanism_evidence"]["page_reads_checked"] == 4
    # the deferral machinery is what the record no longer exercises: nothing is pending, so no row
    # carries the pack's `pages` block. Its control is `test_a_pending_row_still_defers_and_...`
    assert all("pages" not in row for row in out["rows"])


def test_the_b_prime_denominator_is_the_37_the_contract_states(out):
    """55 gold pairs less the 18 (13)(c) removes. `final` is non-null for the first time — which is
    the whole point of (14)(a), and the condition `write_sku_prereg_b2.py` refused on."""
    block = out["b_prime_denominator"]
    assert block["bar_1_gold_pairs"] == 55
    assert block["removed_by_class"] == {"b": 16, "c": 2}
    assert block["removed_so_far"] == 18
    assert block["pending"] == 0
    assert block["final"] == 37
    assert block["remaining_if_no_pending_pair_leaves"] == 37
    assert "3.17 (14)(b)" in block["rule"]


def test_a_pending_row_still_defers_and_still_holds_the_denominator_open(monkeypatch, tmp_path):
    """The control for the branch (14)(a) retired. `PENDING` is empty today, so nothing in the
    shipped record proves a deferral still defers — and this file's whole point is that a row
    nobody read is not guessed from the rows beside it. Row 4 is put back into the tuple.
    """
    monkeypatch.setattr(apply, "DICTATED", tuple(r for r in apply.DICTATED if r[0] != 4))
    monkeypatch.setattr(apply, "PENDING", (4,))
    monkeypatch.setattr(apply, "EXPECTED", {**apply.EXPECTED, "b": 15, "pending": 1})
    monkeypatch.setattr(apply, "PAGE_READS", {n: r for n, r in apply.PAGE_READS.items() if n != 4})
    path = tmp_path / "p.json"
    assert apply.main(["--out", str(path)]) == 0
    record = json.loads(path.read_text(encoding="utf-8"))

    deferred = next(row for row in record["rows"] if row["n"] == 4)
    assert deferred["verdict"] == "PENDING_TEAM_LEAD"
    assert deferred["mechanism"] is None
    assert "pages_read" not in deferred  # a deferred row cites nothing; it was not read
    assert deferred["pages"]
    for page in deferred["pages"]:
        assert set(page) >= {"page", "file", "sha256", "answer"}
    assert record["pending_rows"] == [4]
    assert record["b_prime_denominator"]["final"] is None
    assert record["b_prime_denominator"]["pending"] == 1
    assert record["mechanism_evidence"]["page_reads_checked"] == 3


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
    assert "PENDING_TEAM_LEAD" not in out["by_mechanism"]
    assert out["by_mechanism"]["refusal:token-ceiling"] == 5
    # (14)(a)'s four wear the mechanism the first read already used, so this is ONE bucket of nine
    # and not five plus four buckets of one. What each of the four saw lives in `pages_read`.
    assert out["by_mechanism"]["non-dairy watchlist item"] == 9


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
    """Guessing a deferred row from the rows beside it is the failure this file names by number,
    and the contract's own counts are what stop it. Re-pointed after (14)(a) closed the four: row 4
    goes back into `PENDING` under the first read's checksums, and is then quietly ruled anyway.
    The guess moves TWO counts — the class it is guessed into and `pending` — and the class is
    checked first."""
    monkeypatch.setattr(apply, "PENDING", (4,))
    monkeypatch.setattr(apply, "EXPECTED", {**apply.EXPECTED, "b": 15, "pending": 1})
    monkeypatch.setattr(apply, "PAGE_READS", {n: r for n, r in apply.PAGE_READS.items() if n != 4})
    with pytest.raises(SystemExit, match="row 4 is ruled on twice"):
        run(tmp_path)

    monkeypatch.setattr(apply, "PENDING", ())  # the deferral dropped, the guess left standing
    with pytest.raises(SystemExit, match="the read states b = 15 and the table joins to 16"):
        run(tmp_path)
    monkeypatch.setitem(apply.EXPECTED, "b", 16)  # and now `pending` is the one left standing
    with pytest.raises(SystemExit, match="the read states pending = 1 and the table joins to 0"):
        run(tmp_path)


def test_a_page_read_citing_a_page_that_is_not_on_the_post_refuses(monkeypatch, tmp_path):
    """4360 has six sent pages. A verdict citing page 9 was read against something else."""
    monkeypatch.setattr(apply, "PAGE_READS", {**apply.PAGE_READS, 4: ((2, 9), "fish p2, ? p9")})
    with pytest.raises(SystemExit, match=r"row 4 \(4360\) cites page\(s\) \[9\] and that post has"):
        run(tmp_path)


def test_a_page_read_citing_a_page_the_extractor_refused_refuses(monkeypatch, tmp_path):
    """Row 14's caveat, in the words of a full read. 4401's page 5 came back `malformed JSON`, so a
    verdict that cites it read the rows beside it — which is a `by-pattern` ruling and says so."""
    monkeypatch.setattr(apply, "PAGE_READS", {14: ((5,), "invented: read on 4401 p5")})
    with pytest.raises(SystemExit, match=r"row 14 \(4401\) cites page\(s\) \[5\] the extractor"):
        run(tmp_path)


def test_a_page_read_on_a_row_the_table_does_not_rule_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(apply, "PAGE_READS", {**apply.PAGE_READS, 99: ((1,), "no such row")})
    with pytest.raises(SystemExit, match=r"PAGE_READS names row\(s\) the table does not rule on"):
        run(tmp_path)


def test_a_deferred_row_that_cites_a_page_read_refuses(monkeypatch, tmp_path):
    """A row nobody has ruled on cannot carry the pages it was read on — that pair of states is a
    transcription that put the verdict and the deferral in different places."""
    monkeypatch.setattr(apply, "DICTATED", tuple(r for r in apply.DICTATED if r[0] != 4))
    monkeypatch.setattr(apply, "PENDING", (4,))
    with pytest.raises(SystemExit, match="cite the pages they were read on"):
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
    monkeypatch.setitem(apply.EXPECTED, "b", 17)
    with pytest.raises(SystemExit, match="the read states b = 17 and the table joins to 16"):
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
