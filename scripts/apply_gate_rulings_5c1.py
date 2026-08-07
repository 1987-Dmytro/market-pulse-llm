#!/usr/bin/env python3
"""Apply the operator's 5c1 gate rulings, then write the registry (PROMPT-5c1 D1, second half).

The gate measured 63 candidates and stopped (`results/entry_gate_5c1.json`). The operator ruled
on its one FAIL and seven FLAGs on 2026-08-07 — the rulings are canon in
`docs/CHANNELS-launch.md`, section "Рулинги гейта 5c1". This script does the two things that
follow, and nothing else:

1. writes each ruling into its row's `ruling` field, so the record says what was decided about
   what was measured instead of leaving the measurement to be re-read by hand;
2. appends the surviving channels to `config/registry.yaml` under `sources:` — additive,
   `taxonomy:` and `watchlist:` untouched and checked byte-for-byte after the write.

The gate's rows are never edited or deleted. A channel the operator excluded was still measured,
and dropping its row would rewrite what the pass found; `ruling` is what says it is out.

    PYTHONPATH=src python3 scripts/apply_gate_rulings_5c1.py --plan   # print, write nothing
    PYTHONPATH=src python3 scripts/apply_gate_rulings_5c1.py
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse.registry import SOURCE_TYPES, load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"
CANON = "docs/CHANNELS-launch.md, sections 'Рулинги гейта 5c1 (2026-08-07)' and 'Рулинги, волна 2'"

EXCLUDED = {
    "@kolyastravinsky": "theme: a personal RU-language blog (Samara restaurants, ballet) — the"
    " pre-registered theme flag is confirmed",
    "@whowears": "theme: RU fashion and lifestyle, nothing in the tracked category",
    "@Mambabyua": "a supergroup, not a channel: its 280.75/week is member chat traffic. The"
    " chat-mining track is recorded as DEFERRED — nothing is built for it here",
    "@kulinariya_chat_a": "a supergroup, not a channel: 300/week of chat messages. Same deferred"
    " chat-mining track",
    "@marketopt_official": "late addition WITHDRAWN — the handle resolves to a dead"
    " 132-subscriber channel, and the canon's '41,518' had no source artifact behind it",
    "@akcii_skidki_plt": "late addition #2 EXCLUDED (operator, 2026-08-07 on the gate report):"
    " dead by canon's own conjunction — its ten sampled posts run 2024-04-19 to 2024-06-06, so"
    " 26 months of silence, and there is no discussion group. Same class as the six the operator"
    " excluded on 06.08",
    # --- the theme screen, operator ruling 2026-08-07 evening -------------------------------
    # results/theme_screen_5c1.json over the 28-day window each channel had already produced.
    # The gate grades capability and never graded theme; these five are what that gap admitted.
    "@znishkom": "EXCLUDED on the theme screen: 191 posts in the window and not one food term —"
    " it is Steam game discounts (STAR WARS Jedi, NieR:Automata, Disco Elysium). The same class"
    " as @Steam_free_1 and @Steam_Sale_Ua, excluded 06.08, and the biggest poster in the whole"
    " composition after the recipe feeds",
    "@whitecode_zny": "EXCLUDED on the theme screen: 25 posts, zero food terms — footwear resale"
    " («стара ціна 3099 ♡ НОВА 1499 ♡ розмір 37 ♡ дефект на фото»)",
    "@offspringrus": "EXCLUDED on the theme screen: 16 posts, zero food terms — a RUSSIAN"
    " baby-goods shop (Moscow exhibitions, offspring24.ru), so off-category and off-market",
    "@discountua1": "EXCLUDED as text-free: on topic and unreadable. Its 19 posts repeat one"
    " line, «Знижки в АТБ … Вигода до -56%», with the products inside the images — nothing for"
    " the category filter or brand extraction to read. The 28-day window the 06.08 ruling asked"
    " for is what measured it, and the gate's 0-of-7 comment share is the other half",
    "@ATB_FANatik": "EXCLUDED as text-free: 18 posts of «АНОНС АКЦІЙ АТБ … Частина N», products"
    " in the images, 2 of 7 sampled posts carrying comments",
    # --- wave 2 ratified, one ruling added (operator via the team lead, 2026-08-08) -----------
    "@uasaler": "EXCLUDED ENTIRELY (ruling 08.08, canon 'Рулинги, волна 2'): the 07.08 demotion"
    " left the channel in posts-only because the operator's word that day had named the CHAT («Чат"
    " Аліекспрес ( AliExpert )»), which was left. This ruling names the CHANNEL. Its 30 posts"
    " in the window carry zero food terms on the same theme screen that excluded the five"
    " above — AliExpress promo codes, not the tracked category",
}
"""Ruled out of the composition. Their gate rows stay in the record, carrying this text."""

MOVED = {
    "@maudau": (
        "posts",
        "moved to posts-only: the linked group bans everyone from sending, so 0 of 50 sampled"
        " posts carry comments and a join buys nothing. comments_enabled false, NO join",
    ),
}

PRIOR_RULINGS = {
    # @discountua1 was KEPT in the morning and EXCLUDED that evening, and the second write
    # overwrote the first: the record then read as if the reversal had never happened, and only
    # `git show` could say otherwise. Recovered verbatim from the record's own history and
    # seeded once — the guard is `replaced` already being non-empty.
    "@discountua1": {
        "at": "2026-08-07T11:14:29+00:00",
        "ruling": "KEPT — kept in the comments bucket WITH a join: 0 of 7 sampled posts is a"
        " thin denominator, and the 28-day window measures the real flow. Demotion is a"
        " cycle-1 review question, not this phase's",
        "recovered_from": "git 2970b71:results/entry_gate_5c1.json",
    },
}
"""Rulings overwritten in place before `replaced` existed, put back where they belong."""

KEPT = {
    # @discountua1's 06.08 "keep it, the window will measure it" ruling was superseded on 07.08
    # by what the window measured. It is not dead code here and it is not lost either: the
    # superseded text lives in that row's `replaced`, seeded from PRIOR_RULINGS above.
    "@prostetsofa": "stays in watch, recorded: its group admits by approval only. No watch join"
    " happens in this phase; this surfaces when the channel wakes up",
}

CITY_FEEDS = (
    "@mo3ambik",
    "@poltava_informue",
    "@poltava_misto",
    "@suspilnepoltava",
    "@telegraf_kremenchuk",
    "@kremenchug_live",
    "@gorishnie_plavni1",
    "@myrhorodtown",
    "@Hadiach_telegram",
    "@globine1",
    "@piryatingromada",
    "@Karlivka_live",
    "@PirOperative",
    "@dikankaa",
    "@zinkivnews",
    "@LHVC_info",
)
CITY_RULE = (
    "POSTS-ONLY by the standing ruling (canon 'Дозаявка №3', operator 2026-08-08): a city feed"
    " enters posts-only, comments_enabled false, and its discussion group is NOT joined until"
    " 5c2 rules on a category filter for threads — without one a city chat's whole traffic lands"
    " in a paid inference queue. 11 of the 16 do have a group; that is why the gate holds them in"
    " the `city` bucket, which measures a group without asserting one either way."
)
"""The bucket a city feed enters is a ruling, not a gate finding. It is applied after the gate so
the record still says what was measured, and it covers the whole batch: a `city` row this tuple
does not name has no ruling behind it and `final_bucket` refuses it."""

GATED_LATE = {
    "@marketopt_promo": "replaces the withdrawn late addition (operator, 2026-08-07)",
    "@akcii_skidki_plt": "late addition #2, a Poltava deals aggregator (canon 'Дозаявка №2')",
}
LATE_RULE = (
    "PASS with an open discussion group → comments bucket and the joins list; PASS without one →"
    " posts-only; FAIL or FLAG → stop and report before any further action on it."
)
"""The operator's routing rule for a late addition, written before its gate and applied after."""

SOURCE_TYPE_RULING = {
    "@uasaler": "aggregator",
    "@znishkom": "aggregator",
    "@whitecode_zny": "aggregator",
    "@atb_aktsiyi": "aggregator",
    "@ATB_FANatik": "aggregator",
    "@epicentrk_sale": "official_retail",
    "@dpssgovua": "government",
    # Operator amendment 2026-08-07, after the write: the ruling's "community — the rest" was
    # written while this channel was still at the gate, and it is the promo channel of the
    # Poltava/Kremenchuk chain whose official page the same ruling put in official_retail.
    "@marketopt_promo": "official_retail",
}
"""Team-lead ruling 2026-08-07; everything else is `community`, the ruling's own default."""

AUDIENCE = {
    # Operator ruling 2026-08-08, canon "Сегментация источников — audience". Transcribed from
    # that table and held to it by tests/test_gate_rulings_5c1.py — the table is the law and
    # nothing here is derived from what a channel looks like. Keyed by HANDLE, not by source id:
    # the four originals predate `source_entry` and their ids do not follow from their handles
    # (@VARUS_channel is `varus`, @silposilpo is `silpo`).
    # retail_official (5)
    "@silposilpo": "retail_official",
    "@atb_market_official": "retail_official",
    "@VARUS_channel": "retail_official",
    "@marketopt_promo": "retail_official",
    "@epicentrk_sale": "retail_official",
    # supermarket_deals (4)
    "@msuaaaa": "supermarket_deals",
    "@kopiyochka1": "supermarket_deals",
    "@maudau": "supermarket_deals",
    "@atb_aktsiyi": "supermarket_deals",
    # cooking_recipes (13)
    "@klopotenkofood": "cooking_recipes",
    "@retsepty": "cooking_recipes",
    "@rezeptmoi": "cooking_recipes",
    "@recepti": "cooking_recipes",
    "@mameni_recepti": "cooking_recipes",
    "@retsepty4": "cooking_recipes",
    "@konservacia_kulinaria": "cooking_recipes",
    "@retsepty5": "cooking_recipes",
    "@vylkachannel": "cooking_recipes",
    "@korolevakuchni": "cooking_recipes",
    "@netainaya_vecherya": "cooking_recipes",
    "@retsepty10": "cooking_recipes",
    "@chekh_yevheniia1982": "cooking_recipes",
    # mothers_kids (9)
    "@tretyakovaele": "mothers_kids",
    "@katyal55": "mothers_kids",
    "@kuksa2022": "mothers_kids",
    "@Pro_Detyintumama": "mothers_kids",
    "@intensiv_Mamiev": "mothers_kids",
    "@itsmamix": "mothers_kids",
    "@regina_tatlybaeva": "mothers_kids",
    "@prostetsofa": "mothers_kids",
    "@cozymotherhood": "mothers_kids",
    # baby_food (7)
    "@tarilka_malyuka": "baby_food",
    "@ya_Nenka": "baby_food",
    "@baby_broccoli_club": "baby_food",
    "@blwbabies": "baby_food",
    "@dutyache_menu": "baby_food",
    "@polinalykovagv": "baby_food",
    "@Evgenija_dutjache_menu": "baby_food",
    # health_fitness (17)
    "@smirnov108": "health_fitness",
    "@kkondr_fit": "health_fitness",
    "@polyakova_fitness": "health_fitness",
    "@HealthPsycholog": "health_fitness",
    "@sashafitnesslife": "health_fitness",
    "@chifit_family": "health_fitness",
    "@useful_healthy_fitness_menu": "health_fitness",
    "@olgaa_trainer": "health_fitness",
    "@denisovapro": "health_fitness",
    "@eftforhealth": "health_fitness",
    "@gaid_skobioale": "health_fitness",
    "@Wellosophy_Lesya": "health_fitness",
    "@anastasiiadavydiukfitness": "health_fitness",
    "@skhudnennya": "health_fitness",
    "@viktoria_sshh": "health_fitness",
    "@hydnem_prosto": "health_fitness",
    "@dimakaminskyifit": "health_fitness",
    # food_quality_gov (1)
    "@dpssgovua": "food_quality_gov",
    # regional — the canon's own words: "по прохождении гейта: 16 хендлов дозаявки №3", so the
    # value is written from the same tuple the gate reads, as each of them passes.
    **dict.fromkeys(CITY_FEEDS, "regional"),
}
"""Handle → audience segment. The canon's table, and the whole of it: `main` refuses a registry
source this dict does not name rather than shipping one with a null audience."""

UPDATABLE = ("comments_enabled", "watch", "source_type", "name", "audience")
"""Fields a later ruling may legitimately move on a source already written. A difference in
anything else is unexplained and stops the run — that is what the drift check is for."""


def final_bucket(row: dict) -> tuple[str | None, str | None]:
    """The bucket a channel enters the registry in, and the ruling that put it there.

    ``None`` means it does not enter. The replacement's bucket is not a ruling but a rule the
    operator wrote in advance, resolved against what the gate then measured.
    """
    handle, verdict = row["handle"], row["verdict"]
    if handle in EXCLUDED:
        return None, f"EXCLUDED — {EXCLUDED[handle]}"
    if handle in MOVED:
        bucket, text = MOVED[handle]
        return bucket, f"KEPT, bucket changed — {text}"
    if handle in GATED_LATE:
        if verdict != "PASS":
            raise SystemExit(
                f"{handle} came back {verdict}, and the operator's rule is to stop and report"
                f" before any further action on it. {LATE_RULE}"
            )
        group = row["checks"].get("discussion_group") or {}
        bucket = "comments" if group.get("open") else "posts"
        why = "an open discussion group" if group.get("open") else "no discussion group"
        return (
            bucket,
            f"LATE ADDITION — {GATED_LATE[handle]}; PASS with {why} → {bucket}. {LATE_RULE}",
        )
    if handle in KEPT:
        return row["bucket"], f"KEPT — {KEPT[handle]}"
    if verdict != "PASS":
        raise SystemExit(f"{handle} is {verdict} and no ruling covers it — refusing to guess")
    if handle in CITY_FEEDS:
        return "posts", f"CITY FEED — {CITY_RULE}"
    if row["bucket"] == "city":
        raise SystemExit(
            f"{handle} was gated as a city feed but CITY_FEEDS does not name it — the bucket is a"
            " ruling, and entering it on the strength of the gate's own label is guessing"
        )
    return row["bucket"], None


def record_reversal(row: dict, ruling: str | None, at: str) -> None:
    """A ruling that replaces an earlier one carries what it replaced, inside the row.

    `replaced` is `merge_sitting_returns`'s word for the value actually overwritten. It is
    appended to and never rewritten, so a re-run that changes no ruling adds nothing — which is
    the only way the record can be re-derived without losing what a reversal reversed.
    """
    if (seed := PRIOR_RULINGS.get(row["handle"])) and not row.get("replaced"):
        row["replaced"] = [seed]
    if (previous := row.get("ruling")) and previous != ruling:
        row.setdefault("replaced", []).append({"at": at, "ruling": previous})


def source_entry(row: dict, bucket: str) -> dict:
    """One registry source, built from the gate's own measurement.

    `name` is the title Telegram returned at the gate, not the canon table's truncated cell:
    the record is the artifact, the table is a reading of it. `verified: true` is this
    registry's meaning of the word — the entry check passed — not Telegram's blue check, which
    most of these channels do not carry.
    """
    handle = row["handle"]
    return {
        "id": handle[1:].lower(),
        "name": row["checks"]["title"],
        "source_type": SOURCE_TYPE_RULING.get(handle, "community"),
        "telegram_channels": [handle],
        "verified": True,
        # The gate's group finding, except where a ruling overrode it (@maudau).
        "comments_enabled": bucket != "posts" and bool(row["checks"].get("discussion_group")),
        "watch": bucket == "watch",
        "audience": audience_of(handle),
    }


def audience_of(handle: str) -> str:
    """The canon's segment for a channel, or a refusal. Never a guess from the channel itself."""
    if handle not in AUDIENCE:
        raise SystemExit(
            f"{handle} has no row in the audience table — the canon's"
            " «Сегментация источников» is the law and it does not name this channel"
        )
    return AUDIENCE[handle]


def render(entry: dict) -> str:
    """A YAML block in the file's own style. `json.dumps` doubles as a YAML string quoter."""
    lines = [
        f"  - id: {entry['id']}",
        f"    name: {json.dumps(entry['name'], ensure_ascii=False)}",
        f"    source_type: {entry['source_type']}",
        "    telegram_channels:",
        *[f"      - {json.dumps(channel)}" for channel in entry["telegram_channels"]],
        f"    verified: {str(entry['verified']).lower()}",
        f"    comments_enabled: {str(entry['comments_enabled']).lower()}",
    ]
    if entry["watch"]:
        lines.append("    watch: true")
    lines.append(f"    audience: {entry['audience']}")
    return "\n".join(lines)


def _sources_half(text: str) -> tuple[str, str, str]:
    """The file split at `taxonomy:`. Bounding every edit by this marker is what keeps the
    taxonomy and the watchlist unreachable from anything below."""
    marker = "\ntaxonomy:\n"
    if marker not in text:
        raise SystemExit(f"{REGISTRY}: no `taxonomy:` block — refusing to guess where sources end")
    head, tail = text.split(marker, 1)
    return head, marker, tail


def _blocks(head: str) -> list[list[str]]:
    """The sources half as blocks, each starting at a `  - id:` line (the first holds the header)."""
    blocks, current = [], []
    for line in head.splitlines(keepends=True):
        if line.startswith("  - id: "):
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    blocks.append(current)
    return blocks


def _block_id(block: list[str]) -> str | None:
    return block[0].removeprefix("  - id: ").strip() if block[0].startswith("  - id: ") else None


def update_sources(text: str, changes: dict[str, dict]) -> str:
    """Rewrite named scalar fields of sources already in the file.

    A ruling that changes after the write — @uasaler losing its group, so `comments_enabled`
    going false — has to be able to reach the file. Without this the drift check could only
    refuse, which is right for an unexplained difference and useless for an intended one. Only
    the named fields of the named blocks are touched; anything else is copied through.
    """
    if not changes:
        return text
    head, marker, tail = _sources_half(text)
    out, seen = [], set()
    for block in _blocks(head):
        sid = _block_id(block)
        if sid not in changes:
            out.extend(block)
            continue
        seen.add(sid)
        rendered, written = [], set()
        for line in block:
            key = line.strip().split(":", 1)[0]
            if line.startswith("    ") and key in changes[sid]:
                written.add(key)
                rendered.append(f"    {key}: {_scalar(changes[sid][key])}\n")
            else:
                rendered.append(line)
        for key, value in changes[sid].items():
            if key in written:
                continue
            # A field the block does not have yet — `audience`, added to the whole registry on
            # 2026-08-08. It goes after the block's LAST indented line, not at the block's end:
            # `_blocks` sweeps the removal comments that follow a source into the preceding
            # block, and a field appended after those would sit outside the entry it belongs to.
            last = max(i for i, line in enumerate(rendered) if line.startswith("    "))
            rendered.insert(last + 1, f"    {key}: {_scalar(value)}\n")
        out.extend(rendered)
    missing = set(changes) - seen
    if missing:
        raise SystemExit(f"{REGISTRY}: asked to update {sorted(missing)}, which is not in it")
    return "".join(out) + marker + tail


def _scalar(value) -> str:
    """YAML for a scalar field value. `True` renders `true`, not `True`."""
    return str(value).lower() if isinstance(value, bool) else str(value)


def remove_sources(text: str, ids: dict[str, str]) -> str:
    """Take the named source blocks out, leaving a comment where each one was.

    The convention `config/registry.yaml` already uses for @znizhki_ua, removed 2026-07-27: a
    source that leaves the registry leaves a line saying so. A silently shorter file cannot be
    told from one that never had the channel, and "why is this not collected any more" is the
    question a reader asks six weeks later.

    Blocks are found by their `  - id:` line and end at the next one (or at the block's end), so
    nothing outside `sources:` is reachable from here.
    """
    if not ids:
        return text
    head, marker, tail = _sources_half(text)

    blocks = _blocks(head)

    out, removed = [], set()
    for block in blocks:
        sid = block[0].removeprefix("  - id: ").strip() if block[0].startswith("  - id: ") else None
        if sid in ids:
            removed.add(sid)
            out.append(f"  # {sid} removed 2026-08-07: {ids[sid]}\n")
            continue
        out.extend(block)

    missing = set(ids) - removed
    if missing:
        raise SystemExit(f"{REGISTRY}: asked to remove {sorted(missing)}, which is not in it")
    return "".join(out) + marker + tail


def insert_sources(text: str, entries: list[dict]) -> str:
    """Put the new sources at the end of the `sources:` block and touch nothing else.

    Nothing to add means the file is already right, and returning it unchanged is the whole
    answer: an earlier version appended the section header anyway, so a re-run that added no
    source still dirtied the registry with a duplicate comment block.
    """
    if not entries:
        return text
    marker = "\ntaxonomy:\n"
    if marker not in text:
        raise SystemExit(f"{REGISTRY}: no `taxonomy:` block — refusing to guess where sources end")
    head, tail = text.split(marker, 1)
    block = "\n".join(render(entry) for entry in entries)
    return f"{head.rstrip()}\n\n{HEADER}\n{block}\n{marker}{tail}"


HEADER = """  # --- Phase 5c1 launch composition (operator verdict 2026-08-06, rulings 2026-08-07) ---
  # Every channel below entered through the track-R gate: results/entry_gate_5c1.json holds one
  # row per candidate with its checks, verdict and the ruling that placed it. Names and
  # comments_enabled come from that record, never typed here. `watch: true` = posts are
  # collected and the discussion group is NEVER joined until the channel posts again and the
  # operator says so (SPEC 3.11 (4)); those channels keep comments_enabled because the group
  # exists — the join is what they do not have."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply the 5c1 gate rulings and write sources.")
    parser.add_argument("--plan", action="store_true", help="print the composition, write nothing")
    args = parser.parse_args(argv)

    record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    before = load_registry(REGISTRY)
    held = {handle: source for source in before.sources for handle in source.telegram_channels}
    applied_at = datetime.now(UTC).isoformat(timespec="seconds")

    entries, updates = [], {}
    buckets = {"comments": [], "posts": [], "watch": [], "excluded": []}
    for row in record["candidates"]:
        bucket, ruling = final_bucket(row)
        record_reversal(row, ruling, applied_at)
        row["ruling"] = ruling
        if bucket is None:
            buckets["excluded"].append(row["handle"])
            continue
        buckets[bucket].append(row["handle"])
        expected = source_entry(row, bucket)
        if (existing := held.get(row["handle"])) is not None:
            # Written by an earlier run of this script. Re-derived and compared rather than
            # skipped on trust: if a ruling has changed since, the file is now wrong and saying
            # so is the whole point of running this again.
            drift = {
                field: (getattr(existing, field), expected[field])
                for field in ("name", "source_type", "comments_enabled", "watch")
                if getattr(existing, field) != expected[field]
            }
            if drift:
                # An intended change — a ruling that moved — is applied. The raise stays for the
                # case this check exists for: a difference nothing in the rulings explains.
                unexplained = {k: v for k, v in drift.items() if k not in UPDATABLE}
                if unexplained:
                    raise SystemExit(
                        f"{row['handle']} is in the registry with unexplained fields: {unexplained}"
                    )
                updates[existing.id] = {field: expected[field] for field in drift}
            continue
        entries.append(expected)

    # A channel the rulings excluded AFTER it was written has to come back out again.
    stale = {
        source.id: EXCLUDED[handle]
        for source in before.sources
        for handle in source.telegram_channels
        if handle in EXCLUDED
    }

    # The audience ruling covers all 56 sources, and the four originals predate the gate — the
    # candidate loop above never reaches them. Read off the canon's table by HANDLE: their ids do
    # not follow from their handles, so a source-id lookup would miss them silently.
    for handle, existing in held.items():
        if existing.id in stale:
            continue
        want = audience_of(handle)
        if existing.audience != want:
            updates.setdefault(existing.id, {})["audience"] = want

    for bucket, handles in buckets.items():
        print(f"{bucket:<10}{len(handles):>3}  {' '.join(handles)}")
    # `before.sources` already holds everything an earlier run wrote, so the four originals are
    # what is left once this composition is taken out of it — otherwise a re-run double-counts.
    # `stale` comes out too: on the run that performs a removal the channel is still in
    # `before.sources` and no longer in any bucket, and counting it as an original is how this
    # line printed `launch 43 = registry 5 + ...` on the run that excluded five channels.
    entered = set(buckets["comments"]) | set(buckets["posts"]) | set(buckets["watch"])
    originals = sum(
        1
        for src in before.sources
        if not entered & set(src.telegram_channels) and src.id not in stale
    )
    print(
        f"\nlaunch {originals + len(buckets['comments']) + len(buckets['posts'])}"
        f" = registry {originals} + comments {len(buckets['comments'])}"
        f" + posts {len(buckets['posts'])} · watch {len(buckets['watch'])}"
        f" · excluded {len(buckets['excluded'])}"
    )
    joins = buckets["comments"]
    print(f"joins Deliverable 2 may make: {len(joins)}")
    if args.plan:
        return 0

    if stale:
        print(f"\nremoving {len(stale)} source(s) the rulings excluded after the write:")
        for sid in stale:
            print(f"  - {sid}")

    if updates:
        print(f"updating {len(updates)} source(s) whose ruling moved: {sorted(updates)}")

    text = REGISTRY.read_text(encoding="utf-8")
    tail = text.split("\ntaxonomy:\n", 1)[1]
    REGISTRY.write_text(
        insert_sources(update_sources(remove_sources(text, stale), updates), entries),
        encoding="utf-8",
    )
    written = REGISTRY.read_text(encoding="utf-8")
    if written.split("\ntaxonomy:\n", 1)[1] != tail:
        raise SystemExit("taxonomy/watchlist changed — the write was supposed to be additive")

    after = load_registry(REGISTRY)
    kept = [source.id for source in before.sources if source.id not in stale]
    if [s.id for s in after.sources][: len(kept)] != kept:
        raise SystemExit("the sources that were kept moved or changed — refusing this write")
    if len(after.sources) != len(kept) + len(entries):
        raise SystemExit("source count does not match what was rendered")
    still_there = {handle for source in after.sources for handle in source.telegram_channels} & set(
        EXCLUDED
    )
    if still_there:
        raise SystemExit(f"excluded channels are still in the registry: {sorted(still_there)}")
    unknown = {s.source_type for s in after.sources} - set(SOURCE_TYPES)
    if unknown:
        raise SystemExit(f"unknown source_type written: {unknown}")

    record["registry_written"] = True
    record["rulings"] = {
        "applied_at": applied_at,
        "canon": CANON,
        "composition": {name: sorted(handles) for name, handles in buckets.items()},
        "counts": {
            "registry_before": len(before.sources),
            "comments": len(buckets["comments"]),
            "posts": len(buckets["posts"]),
            "watch": len(buckets["watch"]),
            "excluded": len(buckets["excluded"]),
            "sources_after": len(after.sources),
        },
        "joins_authorised": sorted(joins),
        "source_type_ruling": dict(SOURCE_TYPE_RULING),
        "note": (
            "The gate's rows are unchanged: an excluded channel was still measured, and its"
            " `ruling` is what says it is out. Registry names and comments_enabled are read off"
            " this record, not typed."
        ),
    }
    record["git"] = git_state(GATE_RECORD)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\nwrote {len(entries)} sources into config/registry.yaml; rulings into {GATE_RECORD.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
