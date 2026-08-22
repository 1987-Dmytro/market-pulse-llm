#!/usr/bin/env python3.11
"""r2's pack — r1's 79 units, same order, same renderings — and the seed of its out-file.

`docs/PROMPT-pass2-signals-r2.md` D0′. r2 carries FOUR replies r1 paid for, so this builder's whole
job is to prove that r2's request for each of those four is r1's request, byte for byte:

* the source is `results/pass2_pack.json` itself, checked against the sha
  `results/prereg_pass2_signals.json::instruments.population.sha256` — the sealed record of the
  closed session is what says which 79 units this is;
* every unit is RE-RENDERED through `pass2_r2.pass2_messages_gm4` and its `rendering_sha256`
  compared with r1's. **A moved rendering is a STOP at build time**, not a finding at scoring time:
  it would orphan the four carried replies, and a pack that silently re-rendered them would buy 75
  answers to a question four of the rows in the file were never asked.

Two named steps, one file:

    python3.11 scripts/build_pass2_r2_pack.py            # -> results/pass2_r2_pack.json
    python3.11 scripts/build_pass2_r2_pack.py --seed     # -> results/pass2_signals_r2_v1.jsonl

The seed is the second step and it reads the pack the first wrote: a carried row is copied only
after its id has been found in r2's own leg and its `rendering_sha256` matched there. `--seed`
refuses to overwrite a file that already carries a bought reply.
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import pass2_r2  # noqa: E402

R1_PACK = REPO_ROOT / "results" / "pass2_pack.json"
R1_PREREG = REPO_ROOT / "results" / "prereg_pass2_signals.json"
R1_OUT = REPO_ROOT / "results" / "pass2_signals_v1.jsonl"
OUT = REPO_ROOT / "results" / "pass2_r2_pack.json"
LEG_OUT = "pass2_signals_r2_v1.jsonl"
SEED = REPO_ROOT / "results" / LEG_OUT
LEG_NAME = "r2"

REFUSED_ID = "@matusi_ukr:22303"
"""F2 — answered by r1's pod and REFUSED by r1's parser on `per_comment.note`. A refused reply is a
TRANSPORT outcome and not a verdict, so the thread is owed and re-asked. It is named as a constant
because the whole difference between «74 owed» and «75 owed» is this one id, and a number typed on
its own would not say which thread it is ([[a_count_in_prose_is_not_the_enumeration]])."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    """Repo-relative where it can be, absolute where it cannot — a test writes to a tmp dir."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def r1_pack() -> dict:
    """r1's pack, checked against the sha the sealed r1 record pins for it."""
    pinned = json.loads(R1_PREREG.read_text(encoding="utf-8"))["instruments"]["population"]
    live = sha256_of(R1_PACK)
    if pinned["sha256"] != live:
        raise SystemExit(
            f"{rel(R1_PACK)} hashes {live} and {rel(R1_PREREG)} pins {pinned['sha256']}. r2's"
            " population IS r1's population, and a pack that has moved since the record sealed it"
            " is a different one. Stop and report."
        )
    return json.loads(R1_PACK.read_text(encoding="utf-8"))


def rendered(one: dict) -> str:
    return pass2_r2.pass2_messages_gm4(
        one["channel"],
        one["post_id"],
        one["post"],
        one["entities"],
        one["comments"],
        task=one["task"],
    )[0]["content"]


def units(pack: dict) -> list[dict]:
    """r1's items in r1's order, each re-rendered and held to r1's own sha and length."""
    out = []
    for one in pack["legs"][0]["items"]:
        try:
            content = rendered(one)
        except ValueError as err:
            # the renderer refuses at the same ceiling and its message is about ONE request. The
            # contract's STOP is about the registration, so it is said here and the cause is kept
            raise SystemExit(
                f"{one['id']}: {err}. That is the contract's STOP-before-any-pod: the derived"
                f" ceiling of {pass2_r2.PASS2_MAX_INPUT_CHARS} is below a unit of the population,"
                " and it returns to the operator."
            ) from None
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if digest != one["rendering_sha256"] or len(content) != one["rendered_chars"]:
            raise SystemExit(
                f"{one['id']} renders to {len(content)} chars / {digest} here and r1's pack pins"
                f" {one['rendered_chars']} / {one['rendering_sha256']}. The prompt or the renderer"
                " has moved. STOP: the four carried replies answer r1's request, and a request that"
                " is not r1's makes them answers to nothing."
            )
        if len(content) > pass2_r2.PASS2_MAX_INPUT_CHARS:
            raise SystemExit(
                f"{one['id']} renders to {len(content)} characters, over r2's derived ceiling of"
                f" {pass2_r2.PASS2_MAX_INPUT_CHARS}. That is the contract's STOP-before-any-pod and"
                " it returns to the operator."
            )
        out.append(dict(one))
    return out


def carried_rows() -> list[dict]:
    """r1's replies that PARSED, in r1's own file order. The refused one is not among them."""
    rows = [
        json.loads(line) for line in R1_OUT.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    return [one for one in rows if one["id"] != REFUSED_ID]


def length(items: list[dict]) -> dict:
    widest = max(items, key=lambda one: one["rendered_chars"])
    return {
        "ceiling_chars": pass2_r2.PASS2_MAX_INPUT_CHARS,
        "ceiling_is_derived_not_typed": pass2_r2.CEILING,
        "widest_request": widest["id"],
        "widest_request_chars": widest["rendered_chars"],
        "median_chars": int(statistics.median(one["rendered_chars"] for one in items)),
        "headroom_chars": pass2_r2.PASS2_MAX_INPUT_CHARS - widest["rendered_chars"],
        "headroom_under_pass_1s_constant": 12_000 - widest["rendered_chars"],
    }


def build() -> dict:
    source = r1_pack()
    items = units(source)
    carried = [one["id"] for one in carried_rows()]
    owed = [one["id"] for one in items if one["id"] not in set(carried)]
    if len(carried) != 4 or len(owed) != 75 or REFUSED_ID not in owed:
        raise SystemExit(
            f"carried {len(carried)} and owed {len(owed)} — the registration is 4 and 75 with"
            f" {REFUSED_ID} inside the owed. Stop and report."
        )
    return {
        "phase": "pass2-signals-r2",
        "contract": "docs/PROMPT-pass2-signals-r2.md D0′",
        "task": source["task"],
        "what_this_run_is": (
            "the 75 threads pass 2 still owes: the 74 rung S′ never authorised plus the one whose"
            " reply was REFUSED by r1's parser on a report-only field and therefore never read. The"
            " four replies that parsed are carried, re-verified by rendering, and never re-bought"
        ),
        "population": {
            **source["population"],
            "derived_from": {
                "r1_pack": rel(R1_PACK),
                "r1_pack_sha256": sha256_of(R1_PACK),
                "r1_pack_pinned_by": "results/prereg_pass2_signals.json::instruments.population.sha256",
                "rule": (
                    "r2 does not re-derive the population. r1's is sealed by a record of a paid"
                    " session, and re-running the census filter here would put a second producer"
                    " between the four carried replies and the requests they answer"
                ),
                "r1s_own_derivation": source["population"]["derived_from"],
            },
            "units": len(items),
        },
        "carried": {
            "units": len(carried),
            "ids": carried,
            "from": rel(R1_OUT),
            "sha256": sha256_of(R1_OUT),
            "rule": (
                "copied into this pack's out-file by `--seed`, each held to the id and the"
                " `rendering_sha256` of its unit HERE. Decoding is greedy"
                " (results/reader_v5b_pack.json::serving.decoding) and pass 1 answered 200 of 200"
                " identically across three pods, so re-asking them would buy the same strings"
            ),
        },
        "owed": {
            "units": len(owed),
            "ids": owed,
            "re_asked_after_a_refusal": REFUSED_ID,
            "rule": (
                "a refused reply is a transport outcome and not a verdict, so the thread is owed."
                " Every other owed unit is one rung S′ never authorised"
            ),
        },
        "legs": [
            {
                "name": LEG_NAME,
                "task": source["task"],
                "out": LEG_OUT,
                "reading": (
                    "the ONE leg, all 79 units in r1's order. The four carried rows are already in"
                    " the out-file when the pod starts, and the shipped resume-skip is what turns"
                    " «never re-bought» into a property of the transport instead of a promise"
                ),
                "items": items,
            }
        ],
        "length": length(items),
        "membership": source["membership"],
        "contamination": {
            **source["contamination"],
            "renderings_that_moved_since_r1": [],
            "rule": (
                source["contamination"]["rule"]
                + ". r2 adds one list: every unit re-rendered here and compared with r1's sha, and"
                " a non-empty list is a build-time STOP rather than a pack field"
            ),
        },
        "serving": source["serving"],
        "registration": {"record": "results/prereg_pass2_signals_r2.json"},
        "instruments": {
            "module": {
                "path": "src/market_pulse/pass2.py",
                "sha256": sha256_of(REPO_ROOT / "src" / "market_pulse" / "pass2.py"),
                "rule": "the TEXT and the RENDERER, r1's and unmoved — pinned here so a checkout that changed them is caught before the model is loaded",
            },
            "module_r2": {
                "path": "src/market_pulse/pass2_r2.py",
                "sha256": sha256_of(REPO_ROOT / "src" / "market_pulse" / "pass2_r2.py"),
                "rule": "the ceiling and the tolerant parser. A sibling because r1's pack pins `pass2.py` and that pack is pinned by a sealed record",
            },
            "parser": {
                "path": "src/market_pulse/prompts.py",
                "sha256": sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
                "entry_point": "market_pulse.pass2_r2.parse_pass2",
                "rule": (
                    "`prompts._reader_object`, then the thread's bought entity block, then every"
                    " REPORT-ONLY field checked with the pinned validator that owns it and repaired"
                    " where it refuses, then `prompts._reader`. The refusal set is closed:"
                    f" {list(pass2_r2.REFUSALS)}"
                ),
            },
            "prompt_sha256": source["instruments"]["prompt_sha256"],
            "r1_out_file": {"path": rel(R1_OUT), "sha256": sha256_of(R1_OUT)},
        },
        "producer": {
            "script": rel(Path(__file__)),
            "sha256": sha256_of(Path(__file__).resolve()),
            "borrowed": source["producer"],
        },
    }


def seed(argv: list[str]) -> int:
    """Step two — the four carried rows into r2's out-file, each verified against r2's own pack."""
    pack = json.loads(OUT.read_text(encoding="utf-8"))
    by_id = {one["id"]: one for one in pack["legs"][0]["items"]}
    rows = carried_rows()
    if [one["id"] for one in rows] != pack["carried"]["ids"]:
        raise SystemExit(
            f"{rel(R1_OUT)} carries {[one['id'] for one in rows]} and {rel(OUT)} registers"
            f" {pack['carried']['ids']}. Stop and report."
        )
    if SEED.exists():
        have = [
            json.loads(line)
            for line in SEED.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        bought = [one["id"] for one in have if not one.get("carried_from")]
        if bought:
            raise SystemExit(
                f"{rel(SEED)} already carries {len(bought)} BOUGHT repl(ies) — {bought[:5]}."
                " Seeding would rewrite a file a paid pod is appending to. Stop and report."
            )
    seeded = []
    for row in rows:
        item = by_id[row["id"]]
        if row["rendering_sha256"] != item["rendering_sha256"]:
            raise SystemExit(
                f"{row['id']} was answered against {row['rendering_sha256']} and r2's pack renders"
                f" {item['rendering_sha256']}. The carried reply answers a different request. STOP."
            )
        seeded.append(
            {
                **row,
                "index": pack["legs"][0]["items"].index(item),
                "carried_from": {
                    "file": rel(R1_OUT),
                    "sha256": pack["carried"]["sha256"],
                    "phase": "pass2-signals",
                    "pod_id": "9rquj8p0lelct3",
                    "rule": (
                        "bought by r1 and re-verified here by `rendering_sha256`. Its `seconds`"
                        " belong to r1's pod and are excluded from every rate this run measures"
                    ),
                },
            }
        )
    SEED.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in seeded), encoding="utf-8"
    )
    print(
        f"wrote {rel(SEED)} — {len(seeded)} carried rows: {', '.join(one['id'] for one in seeded)}"
    )
    print(f"owed after the seed: {pack['owed']['units']} units, first {pack['owed']['ids'][0]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--seed" in argv:
        return seed(argv)
    pack = build()
    OUT.write_text(
        json.dumps(pack, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    block = pack["length"]
    print(
        f"{pack['population']['units']} units · carried {pack['carried']['units']}"
        f" · owed {pack['owed']['units']} · every rendering matches r1\n"
        f"length: widest {block['widest_request_chars']} chars ({block['widest_request']})"
        f" · median {block['median_chars']}"
        f" · headroom {block['headroom_chars']} of {block['ceiling_chars']} (derived)"
        f" · {block['headroom_under_pass_1s_constant']} of 12000 (pass 1's constant)\n"
        f"wrote {rel(OUT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
