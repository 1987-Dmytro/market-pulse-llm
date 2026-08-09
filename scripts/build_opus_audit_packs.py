#!/usr/bin/env python3
"""The packs the Opus 5 review reads (SPEC amendment 3.16, REVIEW class).

A second instrument reads the first: the deterministic brand matcher and the GM4
captioner. Nothing built here may enter a gate, the screen or
`results/baselines.json` — 3.16 (1) — so this script draws a bounded population,
writes it down, and stops. The sessions themselves run under
`docs/PROMPT-opus-audit-protocol.md`, which is committed *before* any pack exists
and whose sha this refuses to run without.

Four strata, 3.16 (4), drawn with a fixed seed:

* **S1** every post whose screen v2 relevance was decided by a caption.
* **S2** per channel, up to 10 posts where the matcher found a watchlist brand
  (the precision probe).
* **S3** per channel, up to 10 relevant posts where it found none (recall).
* **S4** every committed caption row, beside the local paths of the images it was
  produced from, each verified against the sha256 the caption row recorded. The
  faithfulness question is asked of the 163 a model wrote; the 31 free poll
  transcriptions carry the brand questions only, and are in the pack because "all
  committed captions" is the contract's word and a row in no pack is a row nobody
  reviews.

An item is written ONCE and carries every stratum it belongs to: a caption-decided
brand hit is S1, S2 and S4, and asking three sessions to judge the same post three
times would buy nothing and would let one post vote three times in the reader.

What this refuses, because the review's authority rests on it:

- **the protocol is committed and unmodified.** 3.16 (2) requires its sha to exist
  before a pack is opened; `run_v22_probe.py` is the precedent, and
  tracked-but-edited is the case a shallow check misses.
- **the inputs are the ones screen v2 read.** Every sha256 the v2 record pins —
  lexicon, registry, both caption files, both caption run records — is re-checked
  against disk. A moved registry would put a different canon watchlist table at the
  top of the pack than the matcher was run with.
- **the re-derivation reproduces the screen.** The per-post hits are re-emitted
  through `yield_screen_5c1`'s own machinery, and every channel's six aggregate
  cells must come back equal to what `results/yield_screen_5c1_v2.json` holds
  before a single item is drawn. A pack drawn from a population that is not the
  screen's would review something nobody measured.
- **an evening's returns are not regenerable.** A rebuild stops if any
  `returns_NN.jsonl` exists; `--force` says what it destroyed.

    PYTHONPATH=src python3 scripts/build_opus_audit_packs.py

Writes `data/annotation/opus_audit_5c1/pack_NN.md` (gitignored data) and the
sha-pinned `results/opus_audit_manifest.json` (committed provenance).
"""

import argparse
import json
import random
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the screen is the re-derivation

import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import parents  # noqa: E402
from market_pulse import yield_screen as core  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

V2 = REPO_ROOT / "results" / "yield_screen_5c1_v2.json"
PROTOCOL = REPO_ROOT / "docs" / "PROMPT-opus-audit-protocol.md"
PACK_DIR = REPO_ROOT / "data" / "annotation" / "opus_audit_5c1"
MANIFEST = REPO_ROOT / "results" / "opus_audit_manifest.json"

SEED = 42
PER_CHANNEL = 10
"""S2 and S3 are per-channel samples, capped by 3.16 (4)'s "up to 10"."""

PACK_MAX = 20
PACK_MIN = 15
"""15–20 posts per pack. The item count is spread evenly over `ceil(n / PACK_MAX)`
packs rather than filled greedily, so the last one is not a four-item stub."""

STRATA = ("S1", "S2", "S3", "S4")
STRATUM_TEXT = {
    "S1": "the screen's relevance for this post was decided by its caption",
    "S2": "the matcher found at least one watchlist brand here (precision probe)",
    "S3": "the post is relevant and the matcher found NO watchlist brand (recall probe)",
    "S4": "a committed caption row standing in for a silent post; where a model wrote it"
    " over images, its faithfulness is judged too",
}

CELLS = (
    ("posts_in_window", lambda row: row["posts"]["in_window"]),
    ("relevant_posts", lambda row: row["relevant_posts"]),
    ("brand_hit_posts", lambda row: row["brand_hits"]["posts"]),
    ("category_hit_posts", lambda row: row["category_hits"]["posts"]),
    ("graded", lambda row: row["captions"]["graded"]),
    ("graded_on_a_caption", lambda row: row["captions"]["graded_on_a_caption"]),
)
"""The six v2 cells the re-derivation must reproduce, per channel.

Together they pin the window filter, the caption merge, the surrogate rule and both
matchers. Reproducing them is what makes "this pack is drawn from the screen's own
population" a checked statement rather than a claim about the code being the same."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def protocol_pin(path: Path = PROTOCOL) -> dict:
    """The audit protocol's sha — refused unless it is committed and unmodified.

    SPEC 3.16 (2): the protocol is committed with its sha BEFORE any pack is opened.
    Untracked and tracked-but-edited are both failures of that, and the second is the
    one a `Path.exists()` check would wave through. The sha recorded is sha256 of the
    file's bytes, not `git hash-object`'s blob sha1 — the reader recomputes it the
    same way, and HEAD is what makes the bytes fixed.
    """
    name = rel(path)
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", name], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if tracked.returncode != 0:
        raise SystemExit(
            f"{name} is not tracked. SPEC 3.16 (2) wants the audit protocol committed with its"
            " sha before any pack is opened — a pack drawn against an uncommitted protocol"
            " cannot say which instructions its sessions were given."
        )
    if git("diff", "HEAD", "--name-only", "--", name).strip():
        raise SystemExit(
            f"{name} is modified against HEAD. Committed-and-edited is the case that looks"
            " committed: the sha in the manifest would not be the protocol at HEAD. Commit the"
            " change first."
        )
    return {
        "path": name,
        "sha256": digest(path),
        "head": git("rev-parse", "HEAD").strip(),
        "rule": (
            "tracked and identical to HEAD at build time; sha256 of the file's bytes, which is"
            " what scripts/read_opus_audit.py recomputes"
        ),
    }


def check_pins(record: dict) -> dict:
    """Every input the v2 screen pinned, re-checked against disk. Drift is a stop."""
    pinned: dict[str, str] = {}
    for key in ("lexicon", "registry", "preregistration"):
        pinned[record[key]["path"]] = record[key]["sha256"]
    for entry in record["captions"]["files"] + record["captions"]["records"]:
        pinned[entry["path"]] = entry["sha256"]
    for name, expected in pinned.items():
        path = REPO_ROOT / name
        if not path.exists():
            raise SystemExit(f"{name}: not found — screen v2 read it and this pack cannot")
        found = digest(path)
        if found != expected:
            raise SystemExit(
                f"{name}: sha256 {found[:16]}…, screen v2 pins {expected[:16]}…. The pack would be"
                " drawn against inputs the screen never saw — and if it is the registry, the canon"
                " watchlist table at the top of every pack would not be the matcher's alias table."
            )
    return dict(sorted(pinned.items()))


def image_check(row: dict | None) -> dict:
    """A caption row's images: named, on disk, and hashing to what the row recorded.

    "the sha-matched sent sets" (3.16 (4)) is a property of bytes, not of a path. The
    media are gitignored, so this manifest is the only durable witness that the pack
    pointed the reviewer at the images GM4 was actually given.
    """
    named = list((row or {}).get("images") or [])
    files, missing, mismatched = [], [], []
    for entry in named:
        path = REPO_ROOT / entry["file"]
        if not path.exists():
            missing.append(entry["file"])
            files.append({"file": entry["file"], "state": "missing"})
            continue
        found = digest(path)
        state = "sha_matched" if found == entry["sha256"] else "sha_differs"
        if state == "sha_differs":
            mismatched.append(entry["file"])
        files.append({"file": entry["file"], "state": state})
    return {
        "files": files,
        "named": len(named),
        "sha_matched": sum(1 for entry in files if entry["state"] == "sha_matched"),
        "missing": missing,
        "sha_differs": mismatched,
    }


def caption_rows(paths: list[Path]) -> dict[tuple[str, int], dict]:
    """The caption files as written, keyed by post.

    `parents.load_captions` — what the screen reads — keeps `text`, `kind` and `source`
    and drops `images`, because what reaches a model is the same string either way. The
    pack needs the images, so the rows are read again here rather than by widening a
    function four other callers depend on.
    """
    rows: dict[tuple[str, int], dict] = {}
    for path in paths:
        for row in parents.read_caption_rows(path):
            key = (row["channel"], row["msg_id"])
            if key in rows:
                raise ValueError(f"{key[0]}:{key[1]} is captioned twice, so neither is the one")
            rows[key] = row
    return rows


def judgeable(item: dict) -> bool:
    """Can this item's caption be judged for faithfulness at all?

    Only if a model wrote it and every image it was written from is on disk under the
    sha the caption row recorded. 31 of the 194 committed rows are poll transcriptions:
    `model` and `caption_source` are null, they carry no image, and the text is a
    deterministic, free rendering of the poll's own question and options. They stand in
    for a silent post on the screen exactly like a caption does — so they can carry S1,
    S2 and S3 — but "is the caption faithful to the image" has no image to be asked
    about, and scoring them would put 31 free rows into GM4's faithfulness rate.
    """
    return bool(
        item["caption"]
        and item["caption_source"]
        and item["images"]["named"]
        and item["images"]["named"] == item["images"]["sha_matched"]
    )


def rederive(record: dict, captions: dict, rows: dict[tuple[str, int], dict]) -> dict:
    """Every in-window post of every screened channel, with the matcher's own verdict.

    The window, the surrogate rule and both matchers come from `yield_screen_5c1` and
    `market_pulse.yield_screen` — imported, never restated — so this is the screen
    re-emitted per post rather than a second implementation of it.
    """
    lexicon = json.loads((REPO_ROOT / record["lexicon"]["path"]).read_text(encoding="utf-8"))
    registry = load_registry(REPO_ROOT / record["registry"]["path"])
    compiled = core.compile_categories(lexicon)
    aliases = core.compile_aliases(watchlist_aliases(registry.watchlist))

    derived: dict[str, list[dict]] = {}
    for row in record["sources"]:
        handle = row["handle"]
        window = {key: row["window"][key] for key in ("since", "until", "source")}
        posts = screen.in_window(
            screen.load_jsonl(screen.POSTS / f"{handle.lstrip('@')}.jsonl"), window
        )
        readable = dict(
            (post["msg_id"], text) for post, text in screen.surrogates(handle, posts, captions)
        )
        items = []
        for post in posts:
            text = readable.get(post["msg_id"])
            caption = captions.get((handle, post["msg_id"]))
            row = rows.get((handle, post["msg_id"]))
            brands = core.brand_hits(text, aliases) if text is not None else []
            groups = core.category_hits(text, compiled) if text is not None else []
            item = {
                "item": f"{handle}:{post['msg_id']}",
                "channel": handle,
                "msg_id": post["msg_id"],
                "date": post.get("date"),
                "text": (post.get("text") or "").strip(),
                "caption": (caption or {}).get("text") or "",
                "caption_kind": (caption or {}).get("kind"),
                "caption_source": (caption or {}).get("source"),
                "read_as": text,
                "images": image_check(row),
                "matcher": {
                    "watchlist_brands": brands,
                    "category_groups": groups,
                    "relevant": bool(brands or groups),
                },
            }
            items.append({**item, "judgeable_caption": judgeable(item)})
        derived[handle] = items
    return derived


def reproduction(record: dict, derived: dict[str, list[dict]]) -> dict:
    """The six cells per channel, ours against the screen's. Any difference is a stop."""
    mismatches = []
    totals = {name: 0 for name, _ in CELLS}
    for row in record["sources"]:
        items = derived[row["handle"]]
        ours = {
            "posts_in_window": len(items),
            "relevant_posts": sum(1 for item in items if item["matcher"]["relevant"]),
            "brand_hit_posts": sum(1 for item in items if item["matcher"]["watchlist_brands"]),
            "category_hit_posts": sum(1 for item in items if item["matcher"]["category_groups"]),
            "graded": sum(1 for item in items if item["read_as"] is not None),
            "graded_on_a_caption": sum(
                1 for item in items if item["read_as"] is not None and not item["text"]
            ),
        }
        for name, cell in CELLS:
            theirs = cell(row)
            totals[name] += ours[name]
            if ours[name] != theirs:
                mismatches.append(
                    {"channel": row["handle"], "cell": name, "ours": ours[name], "screen": theirs}
                )
    if mismatches:
        first = mismatches[0]
        raise SystemExit(
            f"the re-derivation does not reproduce screen v2: {len(mismatches)} cell(s) differ,"
            f" first {first['channel']} {first['cell']} {first['ours']} against {first['screen']}."
            " The pack would be drawn from a population the screen never measured."
        )
    return {
        "checked": rel(V2),
        "channels": len(record["sources"]),
        "cells_per_channel": len(CELLS),
        "mismatches": [],
        "totals": totals,
        "note": (
            "every channel's six aggregate cells came back equal to the record's own. This is what"
            " makes the pack the screen's population rather than a second implementation's"
        ),
    }


def draw(
    derived: dict[str, list[dict]], seed: int, per_channel: int
) -> tuple[list[dict], dict[str, list[str]]]:
    """The four strata, deduplicated into one item list in a fixed order.

    Strata in `STRATA` order, channels in the screen's order, posts by msg_id, and one
    seeded generator for both samples: the draw is a function of the seed and the
    inputs alone. An item met a second time gains a stratum tag and is not re-emitted.
    """
    rng = random.Random(seed)
    ordered: dict[str, dict] = {}
    members: dict[str, list[str]] = {name: [] for name in STRATA}

    def take(item: dict, stratum: str) -> None:
        held = ordered.setdefault(item["item"], {**item, "strata": []})
        held["strata"].append(stratum)
        members[stratum].append(item["item"])

    for items in derived.values():
        for item in sorted(items, key=lambda item: item["msg_id"]):
            if item["matcher"]["relevant"] and not item["text"] and item["caption"]:
                take(item, "S1")
    for stratum, wanted in (("S2", True), ("S3", False)):
        for items in derived.values():
            pool = sorted(
                (
                    item
                    for item in items
                    if item["matcher"]["relevant"]
                    and bool(item["matcher"]["watchlist_brands"]) is wanted
                ),
                key=lambda item: item["msg_id"],
            )
            for item in sorted(
                rng.sample(pool, min(per_channel, len(pool))), key=lambda item: item["msg_id"]
            ):
                take(item, stratum)
    for items in derived.values():
        for item in sorted(items, key=lambda item: item["msg_id"]):
            if item["caption"]:
                take(item, "S4")
    return list(ordered.values()), members


def compose(items: list[dict], pack_max: int = PACK_MAX) -> list[list[dict]]:
    """Items spread evenly over as few packs as the 20-item ceiling allows.

    Greedy filling would leave a tail pack of whatever is left over; spreading keeps
    every pack inside the contract's 15–20 whenever that is arithmetically possible.

    It is not always possible, and the ceiling is the half that is kept. 21 items are
    either one pack of 21 or two of 11 — `ceil(n/20) > floor(n/15)` names that band, and
    inside it every split breaks one bound or the other. A pack over 20 is the worse
    break: it is a session longer than the contract sized, and the packs are the unit of
    work. So the packs come out short there, `main` prints the range it produced, and
    the manifest carries each pack's own count rather than an assurance.
    """
    if not items:
        return []
    count = -(-len(items) // pack_max)
    base, extra = divmod(len(items), count)
    packs, start = [], 0
    for index in range(count):
        size = base + (1 if index < extra else 0)
        packs.append(items[start : start + size])
        start += size
    return packs


def fence(text: str) -> str:
    """A code fence longer than any backtick run inside the text it has to hold."""
    longest, run = 0, 0
    for char in text:
        run = run + 1 if char == "`" else 0
        longest = max(longest, run)
    return "`" * max(3, longest + 1)


def watchlist_table(watchlist) -> str:
    lines = ["| `brand_id` | display names (all forms count, incl. declensions) |", "|---|---|"]
    for brand in watchlist:
        names = " · ".join(brand.display_names)
        lines.append(f"| `{brand.brand_id}` | {names} |")
    return "\n".join(lines)


def empty_row(pack_id: str, item: dict) -> str:
    """The item's returns row, empty. `n/a` is pre-filled where it is structural.

    An item with no model-written caption over sha-matched images has nothing to be
    faithful to, so its verdict is not the reviewer's to give and the validator refuses
    anything else there. Every other cell comes back empty on purpose: `[]` is an
    answer — "I looked and there is nothing" — and it is the answer this review most
    needs to be able to make.
    """
    return json.dumps(
        {
            "pack": pack_id,
            "item": item["item"],
            "watchlist_hits": [],
            "other_dairy_brands": [],
            "caption_verdict": "" if item["judgeable_caption"] else "n/a",
            "brands_visible_missed": [],
            "note": "",
        },
        ensure_ascii=False,
    )


def render_item(pack_id: str, item: dict) -> str:
    matcher = item["matcher"]
    brands = ", ".join(f"`{brand}`" for brand in matcher["watchlist_brands"]) or "— none"
    groups = ", ".join(f"`{group}`" for group in matcher["category_groups"]) or "— none"
    strata = " · ".join(f"**{name}** ({STRATUM_TEXT[name]})" for name in item["strata"])
    out = [
        f"## item `{item['item']}`",
        "",
        f"- strata: {strata}",
        f"- channel `{item['channel']}` · msg_id `{item['msg_id']}` · {item['date']}",
        "",
    ]
    if item["text"]:
        out += [
            "**post text**",
            "",
            f"{fence(item['text'])}\n{item['text']}\n{fence(item['text'])}",
            "",
        ]
    else:
        out += ["**post text** — `[image-only]` (the post carries no text of its own)", ""]
    if item["caption"]:
        title = (
            "**GM4 caption** — this is what you judge in S4"
            if item["judgeable_caption"]
            else f"**stand-in text** (`{item['caption_kind']}`, written by"
            f" `{item['caption_source'] or 'no model — a free transcription'}`)"
        )
        out += [
            title,
            "",
            f"{fence(item['caption'])}\n{item['caption']}\n{fence(item['caption'])}",
            "",
        ]
        if item["images"]["files"]:
            out += ["**images — open these BEFORE judging the caption**", ""]
            for entry in item["images"]["files"]:
                mark = {"sha_matched": "", "missing": " ⚠ MISSING", "sha_differs": " ⚠ SHA DIFFERS"}
                out.append(f"- `{entry['file']}`{mark[entry['state']]}")
            out.append("")
        else:
            out += [
                "No image: `caption_verdict` is `n/a` for this item and is pre-filled. The text"
                " above still counts as this post's content for the brand questions.",
                "",
            ]
    out += [
        f"**matcher's answer (the reference):** watchlist brands {brands} · category groups"
        f" {groups} · relevant: {'yes' if matcher['relevant'] else 'no'}",
        "",
        "**your row** — copy into the returns file and fill it:",
        "",
        f"```json\n{empty_row(pack_id, item)}\n```",
        "",
    ]
    return "\n".join(out)


def render_pack(pack_id: str, items: list[dict], watchlist, protocol: dict) -> str:
    """One self-contained pack. The protocol says not to read project docs, so it is all here."""
    judged = sum(1 for item in items if item["judgeable_caption"])
    header = f"""# Opus 5 audit — {pack_id}

> **Class: REVIEW, never measurement (SPEC 3.16 (1)).** Nothing you write here
> enters a gate, the screen or `results/baselines.json`. The deterministic matcher
> stays the judge of every number; you are the second instrument reading the first.
> An empty finding — "the matcher missed nothing here" — is a good finding.

- Session rules: `{protocol["path"]}` (sha256 `{protocol["sha256"][:16]}…`).
- **First line of your output: the model you are running as.** If it is not
  `claude-opus-5`, STOP and say so.
- Write one row per item into `data/annotation/opus_audit_5c1/returns_{pack_id.removeprefix("pack_")}.jsonl`.
  Never edit this file.
- Items: {len(items)} · of which carry a GM4 caption over sha-matched images: {judged}.

## What to fill

| field | what it is |
|---|---|
| `watchlist_hits` | **closed-book:** the `brand_id`s from the canon table below that are ACTUALLY mentioned in this post's text / visible in its images. Declensions and homoglyph variants count. Decide it yourself, then look at the matcher's answer. |
| `other_dairy_brands` | **open extraction:** any OTHER dairy or ice-cream brand names present, UA/RU spelling as seen. Free text. Dairy and ice cream only — not general food brands. |
| `caption_verdict` | `faithful` (describes what is there) · `partial` (true but misses category-relevant content) · `wrong` (describes things not present) · `n/a` (nothing to judge — pre-filled for you, leave it). |
| `brands_visible_missed` | `brand_id`s readable in the images that the caption does not carry. |
| `note` | one line, free text: anything patterned. A declension the lexicon would miss, a brand that only ever appears in images, a private-label spelling, a systematic caption blind spot. May quote UA/RU verbatim. |

Empty lists are answers. `[]` means "I looked and there is nothing", and that is the
finding this review most needs to be able to make.

## Canon watchlist

{watchlist_table(watchlist)}

---

"""
    return header + "\n---\n\n".join(render_item(pack_id, item) for item in items)


def returns_present(directory: Path) -> list[str]:
    """Returns files already in the pack directory — an evening that a rebuild destroys."""
    return (
        sorted(path.name for path in directory.glob("returns_*.jsonl"))
        if directory.exists()
        else []
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen", type=Path, default=V2)
    parser.add_argument("--pack", type=Path, default=PACK_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--force", action="store_true", help="rebuild even though returns are already being written"
    )
    args = parser.parse_args(argv)

    present = returns_present(args.pack)
    if present and not args.force:
        raise SystemExit(
            f"{rel(args.pack)}: {', '.join(present)} already exist. Rebuilding renumbers the items"
            " under them and this directory is gitignored, so there is no HEAD to restore from."
            " Pass --force only if discarding those sessions is what you mean."
        )

    protocol = protocol_pin()
    record = json.loads(args.screen.read_text(encoding="utf-8"))
    pinned = check_pins(record)
    caption_files = [REPO_ROOT / entry["path"] for entry in record["captions"]["files"]]
    captions, caption_block = screen.read_caption_files(
        caption_files, [REPO_ROOT / entry["path"] for entry in record["captions"]["records"]]
    )
    derived = rederive(record, captions, caption_rows(caption_files))
    reproduced = reproduction(record, derived)
    items, members = draw(derived, args.seed, PER_CHANNEL)
    packs = compose(items)

    registry = load_registry(REPO_ROOT / record["registry"]["path"])
    args.pack.mkdir(parents=True, exist_ok=True)
    for path in sorted(args.pack.glob("pack_*.md")):
        path.unlink()
    written = []
    for index, batch in enumerate(packs, start=1):
        pack_id = f"pack_{index:02d}"
        for item in batch:
            item["pack"] = pack_id
        path = args.pack / f"{pack_id}.md"
        path.write_text(render_pack(pack_id, batch, registry.watchlist, protocol), encoding="utf-8")
        written.append(
            {
                "pack": pack_id,
                "path": rel(path),
                "sha256": digest(path),
                "items": len(batch),
                "judgeable_captions": sum(1 for item in batch if item["judgeable_caption"]),
                "strata": {
                    name: sum(1 for item in batch if name in item["strata"]) for name in STRATA
                },
            }
        )

    images = [item["images"] for item in items if item["caption"]]
    stand_ins = [item for item in items if item["caption"]]
    manifest = {
        "built_by": "scripts/build_opus_audit_packs.py",
        "authority": "docs/SPEC.md amendment 3.16; docs/PROMPT-opus-audit-a.md",
        "class": (
            "REVIEW, never measurement (3.16 (1)). Nothing drawn here may enter a gate, the screen"
            " or results/baselines.json; the deterministic matcher stays the judge"
        ),
        "seed": args.seed,
        "protocol": protocol,
        "screen": {"path": rel(args.screen), "sha256": digest(args.screen)},
        "pinned_inputs": pinned,
        "captions": {k: v for k, v in caption_block.items() if k != "truncated_set"},
        "reproduction": reproduced,
        "caption_decided": {
            "rule": "a post with no text of its own whose caption made it relevant",
            "items": len(members["S1"]),
            "captions_over_a_post_that_had_text": sum(
                row["captions"]["captions_over_a_post_that_had_text"] for row in record["sources"]
            ),
            "texted_post_flipped_by_its_caption": 0,
            "note": (
                "the two readings of «decided by a caption» coincide on this corpus, and it is"
                " measured rather than assumed: no caption in the committed files sits over a post"
                " that had text, so the wider reading (a texted post the caption made relevant)"
                " cannot have a member. A measured zero and an unasked question look identical a"
                " month from now, so it is written down"
            ),
        },
        "strata": {
            name: {
                "asks": STRATUM_TEXT[name],
                "items": len(members[name]),
                "channels": len({item.split(":")[0] for item in members[name]}),
                "per_channel_cap": PER_CHANNEL if name in ("S2", "S3") else None,
                **(
                    {
                        "judgeable_captions": sum(1 for item in items if item["judgeable_caption"]),
                        "judgeable_note": (
                            "the faithfulness denominator. The rest are poll transcriptions with"
                            " no model and no image: in the pack for their brand questions, out of"
                            " the caption rate"
                        ),
                    }
                    if name == "S4"
                    else {}
                ),
            }
            for name in STRATA
        },
        "stand_in_text": {
            "rule": (
                "S4 is the captions a MODEL wrote over images it was sent. 31 of the 194 committed"
                " rows are poll transcriptions: `model` and `caption_source` are null, they carry"
                " no image, and the text is a free, deterministic rendering of the poll's own"
                " question and options"
            ),
            "rows_in_the_committed_files": len(caption_files) and caption_block["rows"],
            "items_carrying_a_stand_in": len(stand_ins),
            "judgeable_gm4_captions": sum(1 for item in items if item["judgeable_caption"]),
            "poll_transcriptions": sum(1 for item in stand_ins if not item["caption_source"]),
            "note": (
                "a transcription stands in for a silent post on the screen exactly like a caption"
                " does, so these items still carry S1/S2/S3 and their brand questions are asked."
                " Their `caption_verdict` is `n/a` and the validator refuses anything else there:"
                " «is the caption faithful to the image» has no image to be asked about, and"
                " scoring them would put 31 free rows into GM4's faithfulness rate"
            ),
        },
        "items_total": len(items),
        "items_note": (
            "an item appears once and carries every stratum it belongs to; the per-stratum counts"
            " above therefore sum to more than items_total"
        ),
        "images": {
            "named": sum(entry["named"] for entry in images),
            "sha_matched": sum(entry["sha_matched"] for entry in images),
            "missing": sorted({file for entry in images for file in entry["missing"]}),
            "sha_differs": sorted({file for entry in images for file in entry["sha_differs"]}),
            "path_note": (
                "the local paths come from the caption rows themselves, which is where the sent"
                " sets are recorded: data/annotation/captions_5c1/posts_media/…, not the"
                " data/annotation/posts_media/… of the contract's prose"
            ),
        },
        "packs": written,
        "pack_size": {"min": PACK_MIN, "max": PACK_MAX, "spread": "evenly, no short tail pack"},
        "returns_present_at_build": present,
        "items": [
            {
                "item": item["item"],
                "pack": item["pack"],
                "channel": item["channel"],
                "msg_id": item["msg_id"],
                "date": item["date"],
                "strata": item["strata"],
                "has_text": bool(item["text"]),
                "has_caption": bool(item["caption"]),
                "caption_source": item["caption_source"],
                "judgeable_caption": item["judgeable_caption"],
                "images": {
                    "named": item["images"]["named"],
                    "sha_matched": item["images"]["sha_matched"],
                },
                "matcher": item["matcher"],
            }
            for item in items
        ],
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"protocol {protocol['path']} sha256 {protocol['sha256'][:16]}… (tracked, clean at HEAD)")
    print(
        f"screen   {rel(args.screen)} reproduced on {reproduced['channels']} channels ×"
        f" {reproduced['cells_per_channel']} cells"
    )
    for name in STRATA:
        stratum = manifest["strata"][name]
        print(
            f"  {name}: {stratum['items']:>4} items over {stratum['channels']:>3} channels"
            f"  — {stratum['asks']}"
        )
    print(
        f"\n{len(items)} items (deduplicated) in {len(packs)} packs of"
        f" {min(len(p) for p in packs)}–{max(len(p) for p in packs)}"
    )
    print(
        f"images: {manifest['images']['sha_matched']}/{manifest['images']['named']} sha-matched"
        f" · missing {len(manifest['images']['missing'])}"
        f" · sha differs {len(manifest['images']['sha_differs'])}"
    )
    print(f"wrote {rel(args.pack)}/pack_NN.md and {rel(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
