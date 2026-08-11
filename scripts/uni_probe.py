#!/usr/bin/env python3
"""The universality dry run: what follows `config/registry.yaml` when the domain changes ($0).

ONE-SHOT, deliverable B of `docs/PROMPT-uni-a.md`, re-run as the regression proof of uni-b
deliverable D(4). It answers one question with measurements
instead of a reading of the code: if the operator swapped the tracked category from dairy to
coffee tomorrow, which instruments would follow the registry, which would need a new
registration, and which carry the old domain hard-coded.

The method is a TOY registry materialised in a tempdir — category «кава», four subcategories,
three real coffee brands, the live `sources` block carried over unchanged — driven through the
shipped library functions. **No live file is written and no live file is read for anything but
its bytes**: the corpus under `data/raw/` is read, never modified, the live registry, the live
lexicon and every registered prompt are read and their shas recorded beside the toy ones. The
only artifact is `results/uni_probe_v2.json` — uni-a's `results/uni_probe.json` is a DATED
measurement of the code as it stood before SPEC 3.17 (8) and is never overwritten (the default
`--out` refuses it by name).

No model is called and no money is spent: every step below is a deterministic function of the
repository's own code.

    PYTHONPATH=src python3 scripts/uni_probe.py

A step that cannot be measured writes the verdict UNMEASURED with its reason. It never guesses.
"""

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse import lexicon, positions, prompts, scorer, yield_screen  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = lexicon.LAW
POSTS = REPO_ROOT / "data" / "raw" / "posts"
RECORD = REPO_ROOT / "results" / "uni_probe_v2.json"
SEALED = REPO_ROOT / "results" / "uni_probe.json"

SAMPLE_ROWS = 2000
"""The floor the brief sets for step 2. The sample is taken deterministically — channel files in
sorted order, rows in file order, texted rows only — and the draw stops at the first row that
takes it to or past this number, so the count is a property of the corpus and not of a seed."""

FOLLOWS = "follows-registry"
FOLLOWS_LAW = "follows-registry(law)"
"""uni-b's verdict for the pre-filter's category half: the vocabulary is a FILE, so a registry edit
alone is still not enough — but the file is law now (`config/lexicon.yaml`), and it REFUSES to load
against a taxonomy whose display names its stems do not name. One edit, checked, instead of a
silent carry-over."""

NEEDS_REGISTRATION = "needs-new-registration"
HARD_CODED = "hard-coded"
UNMEASURED = "UNMEASURED"

# --- the toy domain ---------------------------------------------------------------------------

TOY_TAXONOMY = {
    "coffee": {
        "name": "Кава",
        "subcategories": {
            "ground-coffee": "Кава мелена",
            "coffee-beans": "Кава в зернах",
            "instant-coffee": "Кава розчинна",
            "coffee-capsules": "Кава в капсулах",
        },
    }
}
"""One tracked group and four subcategories — five category names against the live eleven."""

TOY_WATCHLIST = [
    {"brand_id": "halka", "display_names": ["Галка"], "own": False},
    {"brand_id": "chorna-karta", "display_names": ["Чорна карта", "Черная карта"], "own": False},
    {"brand_id": "nescafe", "display_names": ["Nescafé"], "own": False},
]
"""Three real Ukrainian-market coffee brands. «Nescafé» is registered with its diacritic and
WITHOUT an ASCII alias on purpose: the matcher is an exact casefolded lookup, so whether the
common spelling «Nescafe» resolves is a measurement this probe takes rather than assumes."""

TOY_STEMS = ["кав", "еспресо", "лате", "капучино"]
"""The toy lexicon's `tracked` half — the coffee equivalent of the live «сир»/«молок» stems. The
`endings` list is copied from the live lexicon so the matcher is the shipped one, unchanged."""

# --- step 3: ten synthetic coffee replies, and what the ladder should make of them --------------

COFFEE_REPLIES = [
    (
        "a full page position: brand, line, category, size and both prices",
        '[{"brand": "Галка", "line": "Люкс", "category": "ground-coffee", "size": "250 г",'
        ' "price_promo": "89,90", "price_old": "129,90", "discount_pct_printed": "-31%"}]',
        ["position"],
    ),
    (
        "two offers on one page, one of them a capsule pack",
        '[{"brand": "Чорна карта", "category": "coffee-beans", "size": "1 кг",'
        ' "price_promo": "499,00"},'
        ' {"brand": "Nescafé", "category": "coffee-capsules", "size": "100 г",'
        ' "price_promo": "159,90"}]',
        ["position", "position"],
    ),
    (
        "the group key itself, which the taxonomy also carries",
        '[{"brand": "Галка", "category": "coffee", "size": "500 г", "price_promo": "179,00"}]',
        ["position"],
    ),
    (
        "a brand and a category with no attribute — the middle rung",
        '[{"brand": "Nescafé", "category": "instant-coffee"}]',
        ["product_mention"],
    ),
    (
        "a brand and a size with no category — the middle rung from the other side",
        '[{"brand": "Чорна карта", "size": "230 г"}]',
        ["product_mention"],
    ),
    (
        "a bare brand — the bottom rung",
        '[{"brand": "Галка"}]',
        ["brand_mention"],
    ),
    (
        "nothing of the tracked category on the page",
        "[]",
        [],
    ),
    (
        "a hedged price — and a price does not move a rung, so this is the middle one",
        '[{"brand": "Галка", "category": "ground-coffee", "price_promo": "по 90"}]',
        ["product_mention"],
    ),
    (
        "an unregistered brand — kept as brand_raw, never dropped",
        '[{"brand": "Lavazza", "category": "coffee-beans", "size": "1 кг",'
        ' "price_promo": "649,00"}]',
        ["position"],
    ),
    (
        "a line without a category — a line is a differentiating attribute",
        '[{"brand": "Nescafé", "line": "Gold"}]',
        ["product_mention"],
    ),
]
"""Ten replies of the shape the page prompt asks for, written against the TOY taxonomy. The third
column is what SPEC 3.17 (2)'s ladder must return; the probe asserts it rather than printing it,
because a tier list nobody checked is a list of plausible strings."""

DAIRY_REPLY = (
    '[{"brand": "Яготинське", "category": "milk", "size": "900 г", "price_promo": "39,90"}]'
)
"""The negative control of step 3: under the toy taxonomy the parser must REFUSE `milk`. If it
does not, the parser is not reading the registry it was handed."""

# --- step 2 and step 4: the controls ------------------------------------------------------------

TOY_POSITIVE = "Кава мелена Галка 250 г — 89,90 грн"
"""A leaflet line of the shape the toy frame exists to catch: a brand, a category term, a size
and a price, all on one line. The dairy census's positive control, translated."""

TOY_NEGATIVES = {
    "a category with no number beside it": "Люблю каву і чай!",
    "a price with no category and no brand": "Кросівки, розмір 37, 1499 грн",
    "a fitness post with a discount and no taxonomy": (
        "Розклад тренувань на тиждень: понеділок — ноги, середа — спина, п'ятниця — руки."
        " Реєстрація за посиланням, знижка 20% до кінця місяця."
    ),
}

DAIRY_LINE = "Молоко Яготинське 2,5% 900 г — 39,90 грн"
"""The live census's own positive control. Under the TOY lexicon it must NOT pass — and under the
live lexicon beside a toy registry it must still pass, which is the leak step 2 is measuring."""

BRAND_STRINGS = [
    ("Галка", "the display name exactly as registered"),
    ("галка", "the same name casefolded"),
    ("ГАЛКА", "the same name upper-cased"),
    ("Чорна карта", "a two-word display name"),
    ("Черная карта", "the registered RU spelling"),
    ("Чорна Карта", "the UA name with the second word capitalised"),
    ("Nescafé", "the Latin brand as registered, with its diacritic"),
    ("Nescafe", "the same brand as a keyboard writes it, without the diacritic"),
    ("NESCAFÉ", "the Latin brand upper-cased"),
    ("Галку", "the accusative — Slavic inflection"),
    ("Lavazza", "a coffee brand outside the toy watchlist"),
    ("Яготинське", "a DAIRY watchlist brand — must not resolve under the toy registry"),
]
"""What step 4 puts through `scorer.normalise_brand` and `positions.resolve_brand`. Every row is a
string a Ukrainian leaflet or comment plausibly carries; the point is which of them the shipped
exact-match table resolves and which it leaves as raw text."""

# --- helpers -------------------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def write_toy_registry(directory: Path) -> Path:
    """The live registry with its taxonomy and watchlist swapped for coffee, in a tempdir.

    `sources` is carried over unchanged — the brief fixes the sources — so the toy file is a
    registry the shipped loader accepts rather than a fixture shaped like one.
    """
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    toy = {
        "sources": data["sources"],
        "taxonomy": {"tracked_groups": TOY_TAXONOMY},
        "watchlist": TOY_WATCHLIST,
    }
    path = directory / "registry_toy.yaml"
    path.write_text(yaml.safe_dump(toy, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def toy_stems_the_law_accepts(toy_registry) -> tuple[list[str], list[str]]:
    """TOY_STEMS split by the law's own rule: a stem must be a PREFIX of a display name.

    Measured, not chosen. «еспресо», «лате» and «капучино» are words a Ukrainian coffee post
    actually uses and NONE of them is a prefix of «Кава» / «Кава мелена» / «Кава в зернах» /
    «Кава розчинна» / «Кава в капсулах», so the law refuses them — correctly, and that refusal is
    a cost a new domain pays: either the registry names those subcategories, or each stem is
    exempted by name the way `ru_variants` exempts the Russian forms. Never by loosening the rule.
    """
    unmatched = lexicon.unmatched_stems({"coffee": TOY_STEMS}, toy_registry.taxonomy)
    rejected = unmatched.get("coffee", [])
    return [stem for stem in TOY_STEMS if stem not in rejected], rejected


def write_toy_lexicon(directory: Path, live: dict, stems: list[str]) -> Path:
    """A toy vocabulary law in the shipped shape: the live `endings` and `units`, coffee stems.

    A separate file because the pre-filter's category half reads a LEXICON, not the registry —
    which is the finding this probe priced in uni-a. Since SPEC 3.17 (8) that file is LAW
    (`config/lexicon.yaml`) rather than a draft nobody could reach from a registry edit, so the
    toy is written in the law's own shape and loaded through the law's own loader, guard included.
    """
    toy = {
        "status": "toy-not-law — built at run time by scripts/uni_probe.py, never committed",
        "note": "the coffee equivalent of config/lexicon.yaml's tracked half",
        "matcher": live["matcher"],
        "endings": live["endings"],
        "units": live["units"],
        "known_collision": "«кав» + «а» matches «кава» and also the surname «Кавун» is NOT matched"
        " (the stem is bounded by the ending list, as shipped)",
        "tracked": {"coffee": stems},
        "ru_variants": [],
    }
    path = directory / "lexicon_toy.yaml"
    path.write_text(yaml.safe_dump(toy, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def corpus_sample(limit: int) -> tuple[list[dict], dict]:
    """`limit` texted post rows, drawn deterministically from `data/raw/posts/`.

    Sorted file names, rows in file order, rows carrying text only. The provenance dict names
    every file the draw touched and how many rows it took from each, so the sample is a thing a
    reader can rebuild rather than a number to take on trust.
    """
    rows: list[dict] = []
    taken: dict[str, int] = {}
    for path in sorted(POSTS.glob("*.jsonl")):
        if len(rows) >= limit:
            break
        count = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if len(rows) >= limit:
                break
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (row.get("text") or "").strip():
                rows.append({"id": f"@{path.stem}:{row['msg_id']}", "text": row["text"]})
                count += 1
        if count:
            taken[f"@{path.stem}"] = count
    ids = "\n".join(row["id"] for row in rows)
    return rows, {
        "rows": len(rows),
        "files_read": len(taken),
        "rows_per_channel": taken,
        "ids_sha256": hashlib.sha256(ids.encode("utf-8")).hexdigest(),
        "draw": (
            "data/raw/posts/*.jsonl in sorted file-name order, rows in file order, rows carrying"
            f" text only, stopping at {limit}. No seed and no shuffle: the draw is reproducible"
            " from the corpus alone"
        ),
    }


def prefilter_over(rows: list[dict], compiled: dict, aliases: list) -> dict:
    """The shipped pre-filter over a row sample: how many pass, and by which pattern kind."""
    passed, kinds, by_hit = [], dict.fromkeys(("currency", "percent", "size"), 0), {}
    for row in rows:
        found = positions.prefilter(row, compiled, aliases)
        if found is None:
            continue
        present = sorted(
            {positions.pattern_kind(p) for p in positions.size_price_patterns(row["text"])}
        )
        for kind in present:
            kinds[kind] += 1
        by_hit[found["hit"]] = by_hit.get(found["hit"], 0) + 1
        passed.append({"id": row["id"], **found})
    return {
        "passed": len(passed),
        "share_of_sample": round(len(passed) / len(rows), 4) if rows else 0.0,
        "passed_carrying": kinds,
        "by_hit": dict(sorted(by_hit.items(), key=lambda pair: (-pair[1], pair[0]))[:10]),
        "examples": passed[:5],
    }


def controls_for(compiled: dict, aliases: list, positive: str, negatives: dict) -> dict:
    """The filter's exam, taken before its yield is read — the census's own shape."""
    out = {
        f"positive :: {positive}": {
            "kind": "positive",
            "measured": positions.prefilter({"text": positive}, compiled, aliases),
        }
    }
    for name, text in negatives.items():
        out[f"negative :: {name}"] = {
            "kind": "negative",
            "line": text,
            "measured": positions.prefilter({"text": text}, compiled, aliases),
        }
    for entry in out.values():
        entry["ok"] = bool(entry["measured"]) == (entry["kind"] == "positive")
    return out


# --- the five steps ---------------------------------------------------------------------------


def step_1_category_keys(toy, live) -> dict:
    """Does the position schema accept a vocabulary it has never seen? Its docstring says yes."""
    toy_keys = positions.category_keys(toy.taxonomy)
    live_keys = positions.category_keys(live.taxonomy)
    expected = set(TOY_TAXONOMY) | set(TOY_TAXONOMY["coffee"]["subcategories"])
    return {
        "verdict": FOLLOWS if toy_keys == expected else HARD_CODED,
        "asks": "does positions.category_keys read the toy taxonomy, both levels?",
        "toy_keys": sorted(toy_keys),
        "live_keys": sorted(live_keys),
        "overlap_with_live": sorted(toy_keys & live_keys),
        "evidence": (
            "positions.category_keys(taxonomy) returns the tracked group keys plus every"
            " subcategory key, read off the Taxonomy object it is handed. Handed the toy taxonomy"
            f" it returns {len(toy_keys)} names and none of the live {len(live_keys)}"
        ),
        "caveat": (
            "this is the PARSER's accepted vocabulary only. What the model is ASKED for is the"
            " registered prompt's own enum — step 5, and it does not move with the registry"
        ),
    }


def step_2_prefilter(
    rows, sample, toy_registry, live_lexicon, toy_lexicon, toy_lexicon_path
) -> dict:
    """The pre-filter over the corpus, under the toy vocabulary and under the live one."""
    toy_aliases = yield_screen.compile_aliases(watchlist_aliases(toy_registry.watchlist))
    toy_compiled = yield_screen.compile_categories(toy_lexicon)
    live_compiled = yield_screen.compile_categories(live_lexicon)

    toy_yield = prefilter_over(rows, toy_compiled, toy_aliases)
    # the leak, measured: the registry says coffee, the lexicon file still says dairy
    leak_yield = prefilter_over(rows, live_compiled, toy_aliases)

    controls = controls_for(toy_compiled, toy_aliases, TOY_POSITIVE, TOY_NEGATIVES)
    dairy_under_toy = positions.prefilter({"text": DAIRY_LINE}, toy_compiled, toy_aliases)
    dairy_under_live = positions.prefilter({"text": DAIRY_LINE}, live_compiled, toy_aliases)
    controls["negative :: the live census's dairy control, under the toy lexicon"] = {
        "kind": "negative",
        "line": DAIRY_LINE,
        "measured": dairy_under_toy,
        "ok": dairy_under_toy is None,
    }
    # the law's own guard, MEASURED rather than described: the live vocabulary refuses to load
    # against the toy taxonomy, which is what stops a domain change from carrying dairy stems
    # forward in silence. This is the difference between uni-a's HARD_CODED and uni-b's
    # FOLLOWS_LAW, and it is computed here, not asserted in the record.
    try:
        lexicon.load_lexicon(LEXICON, taxonomy=toy_registry.taxonomy)
        guard = {"refused": False, "reason": None}
    except ValueError as error:
        guard = {"refused": True, "reason": str(error)}
    toy_loads = lexicon.load_lexicon(toy_lexicon_path, taxonomy=toy_registry.taxonomy)
    verdict = FOLLOWS_LAW if guard["refused"] and toy_loads["tracked"] else HARD_CODED
    return {
        "verdict": verdict,
        "asks": "does the deterministic pre-filter follow a registry change?",
        "halves": {
            "brand half — yield_screen.compile_aliases(watchlist_aliases(registry.watchlist))": (
                FOLLOWS
            ),
            "category half — yield_screen.compile_categories(load_lexicon(config/lexicon.yaml))": (
                verdict
            ),
        },
        "the_law_refuses_a_taxonomy_its_stems_do_not_name": guard,
        "sample": sample,
        "under_the_toy_lexicon": toy_yield,
        "under_the_live_lexicon_with_the_toy_registry": leak_yield,
        "controls": controls,
        "controls_ok": all(entry["ok"] for entry in controls.values()),
        "the_leak": {
            "dairy_line": DAIRY_LINE,
            "passes_under_the_toy_lexicon": dairy_under_toy is not None,
            "passes_under_the_live_lexicon": dairy_under_live is not None,
            "reading": (
                "the pre-filter's brand half IS registry-driven — the aliases come from the"
                " watchlist it was handed. Its category half still reads a FILE: yield_screen."
                "compile_categories takes a lexicon, never a Taxonomy, and the toy run needs a"
                " second toy file to have any coffee stems at all. What changed in uni-b is what"
                " happens when the two disagree. In uni-a the file was data/category_lexicon_"
                "draft.json, `status: draft-not-law`, unreachable from any registry edit, and a"
                " coffee registry beside a dairy lexicon produced a silent yield of dairy rows."
                " Now the file is config/lexicon.yaml, law, and loading it against the toy"
                " taxonomy RAISES — see the_law_refuses_a_taxonomy_its_stems_do_not_name. The"
                " vocabulary is still one hand-authored file; it is no longer one nobody notices"
            ),
        },
        "evidence": (
            "positions.prefilter(row, compiled, aliases) — `compiled` comes from"
            " yield_screen.compile_categories(lexicon), never from a Taxonomy"
        ),
    }


def step_3_parser_and_ladder(toy_registry) -> dict:
    """Ten synthetic coffee replies through the shipped parser and the shipped ladder."""
    categories = positions.category_keys(toy_registry.taxonomy)
    aliases = watchlist_aliases(toy_registry.watchlist)
    rows, failures = [], []
    for name, reply, expected in COFFEE_REPLIES:
        try:
            parsed = positions.parse_positions(
                reply,
                categories=categories,
                carrier="leaflet_page",
                price_origin="retail_leaflet",
                extraction_source="uni-a probe fixture, no model",
                aliases=aliases,
            )
        except positions.SchemaError as error:
            failures.append({"case": name, "reason": error.reason})
            continue
        tiers = [position.tier() for position in parsed]
        row = {
            "case": name,
            "positions": len(parsed),
            "tiers": tiers,
            "expected_tiers": expected,
            "ok": tiers == expected,
            "brand_ids": [position.brand_id for position in parsed],
            "brand_raw": [position.brand_raw for position in parsed],
        }
        rows.append(row)

    # the negative control: a dairy category is outside the toy taxonomy and must be refused
    refusal = None
    try:
        positions.parse_positions(
            DAIRY_REPLY,
            categories=categories,
            carrier="leaflet_page",
            price_origin="retail_leaflet",
            extraction_source="uni-a probe fixture, no model",
            aliases=aliases,
        )
    except positions.SchemaError as error:
        refusal = error.reason
    ladder_ok = all(row["ok"] for row in rows) and not failures
    return {
        "verdict": FOLLOWS if ladder_ok and refusal else HARD_CODED,
        "asks": "do the parser and the tier ladder work on a domain they have never seen?",
        "replies": len(COFFEE_REPLIES),
        "parsed": rows,
        "parse_failures": failures,
        "tiers_all_as_expected": ladder_ok,
        "dairy_control": {
            "reply": DAIRY_REPLY,
            "refused": refusal is not None,
            "reason": refusal,
            "why": (
                "`milk` is a live subcategory and is NOT in the toy taxonomy, so the parser must"
                " refuse the whole reply. A parser that accepted it would be carrying the dairy"
                " vocabulary rather than reading the registry"
            ),
        },
        "ladder_sha256": positions.ladder_sha256(),
        "evidence": (
            "positions.parse_positions(..., categories=positions.category_keys(toy.taxonomy));"
            " the rung comes from positions.tier, a pure function of which fields are filled in,"
            " and no branch of it names a category"
        ),
    }


def step_4_brand_resolution(toy_registry) -> dict:
    """The alias table and the two brand resolvers, on Cyrillic and Latin spellings."""
    aliases = watchlist_aliases(toy_registry.watchlist)
    rows = []
    for text, note in BRAND_STRINGS:
        resolved = positions.resolve_brand(text, aliases)
        normalised = scorer.normalise_brand({"mention": text}, aliases)
        rows.append(
            {
                "string": text,
                "note": note,
                "resolve_brand": resolved,
                "normalise_brand": normalised,
                "resolved": resolved is not None,
            }
        )
    compiled = yield_screen.compile_aliases(aliases)
    found = yield_screen.brand_hits("Сьогодні Галка і Nescafé, а завтра Чорна карта", compiled)
    return {
        "verdict": FOLLOWS,
        "asks": "does brand resolution follow the watchlist, and what does its exactness cost?",
        "alias_table": dict(sorted(aliases.items())),
        "alias_count": len(aliases),
        "strings": rows,
        "resolved": sum(1 for row in rows if row["resolved"]),
        "unresolved": [row["string"] for row in rows if not row["resolved"]],
        "brand_hits_over_a_sentence": found,
        "cost_of_exactness": (
            "the table is a casefolded exact lookup with no stemming, no diacritic folding and no"
            " transliteration (market_pulse.brands.watchlist_aliases). Every unresolved string"
            " above is a spelling a new domain would have to register as its own display_name —"
            " and for a Latin-script category that is structural, not marginal: «Nescafe» and"
            " «Nescafé» are two different keys"
        ),
        "evidence": (
            "positions.resolve_brand(name, aliases) and scorer.normalise_brand(entry, aliases)"
            " both take the alias table as an argument; neither names a brand"
        ),
    }


def step_5_prompt_instantiation() -> dict:
    """What a new domain would have to WRITE. Measured off the registered prompt text."""
    body = prompts.POSITIONS_BODY
    lines = [line for line in body.splitlines() if line.strip()]
    enum_line = next(line for line in lines if line.strip().startswith('- "category"'))
    intro_page = prompts.POSITIONS_PAGE_INTRO
    intro_text = prompts.POSITIONS_TEXT_INTRO
    live_enum = [
        "dairy",
        "milk",
        "kefir-ryazhanka",
        "yogurt",
        "curd",
        "sour-cream",
        "butter",
        "cheese",
        "dairy-desserts",
        "plant-based-analogs",
        "ice-cream",
    ]
    quoted = [name for name in live_enum if name in enum_line]
    # A generator would have to be handed the taxonomy. Nothing in the module takes one: this
    # walks every public callable's signature rather than guessing from its name.
    import inspect

    domain_aware = []
    for name in dir(prompts):
        if name.startswith("_"):
            continue
        value = getattr(prompts, name)
        if not callable(value):
            continue
        try:
            params = set(inspect.signature(value).parameters)
        except (TypeError, ValueError):
            continue
        if params & {"taxonomy", "registry", "categories", "category", "watchlist", "aliases"}:
            domain_aware.append(name)
    return {
        "verdict": NEEDS_REGISTRATION,
        "asks": "is a prompt for a new category generated, or written and registered by hand?",
        "measured_fact": (
            "there is no generator. market_pulse.prompts.PROMPTS is a dict of literal strings and"
            " the two position prompts are built by string concatenation at import time"
            " (POSITIONS_POST_PROMPT = POSITIONS_PAGE_INTRO + POSITIONS_BODY, and the text prompt"
            " is _swap'ped from it). Nothing in the module reads a Taxonomy"
        ),
        "public_callables_taking_a_domain_argument": sorted(domain_aware),
        "public_callables_taking_a_domain_argument_note": (
            "measured by walking every public callable's signature for a taxonomy / registry /"
            " categories / watchlist / aliases parameter — not by reading function names. An"
            " empty list means no function in the module can be handed a domain"
        ),
        "registered_prompts": len(prompts.PROMPTS),
        "position_prompt_shas": {
            task: prompts.prompt_sha256(task)[:12] for task in sorted(prompts.POSITIONS)
        },
        "what_would_have_to_be_written_anew": {
            "intro (page leg)": {
                "lines": len(intro_page.splitlines()),
                "chars": len(intro_page),
                "domain_bound": "«promotional leaflet from a Ukrainian food-retail chain» — the"
                " leg, not the category. Reusable as written",
            },
            "intro (text leg)": {
                "lines": len(intro_text.splitlines()),
                "chars": len(intro_text),
                "domain_bound": "same: the leg. Reusable as written",
            },
            "category paragraph": {
                "text": lines[0],
                "domain_bound": "names the eleven dairy kinds AND excludes coffee BY NAME."
                " Rewritten in full for a new category",
            },
            "category enum": {
                "text": enum_line.strip(),
                "names_quoted": quoted,
                "count": len(quoted),
                "domain_bound": "the eleven category values the model may answer, written as"
                " literals. A toy registry offering five coffee keys changes nothing here",
            },
            "the shape example": {
                "text": lines[-1],
                "domain_bound": "«Рудь · Пломбір · ice-cream» — a dairy brand, a dairy line and a"
                " dairy category key. A format illustration, but written in the live domain",
            },
            "the schema rules": {
                "lines": sum(1 for line in lines if line.strip().startswith("- ")) - 1,
                "domain_bound": "OMIT-a-key, COMPUTE-NOTHING, the two-price rule, the empty-array"
                " rule: domain-free. Reusable as written",
            },
        },
        "the_coffee_clause": {
            "quote": "chocolate, sausage, coffee, nappies and cheese-flavoured snacks are not"
            " dairy",
            "grepped_back": "chocolate, sausage, coffee, nappies and cheese-flavoured snacks are"
            " not dairy" in " ".join(body.split()),
            "why_it_matters": (
                "the toy domain is coffee, and the registered page prompt instructs the model to"
                " refuse coffee BY NAME. Step 1's parser would accept a coffee category; this"
                " prompt would never produce one. The pair is the finding, and either half read"
                " alone is misleading"
            ),
        },
        "evidence": (
            "src/market_pulse/prompts.py POSITIONS_PAGE_INTRO / POSITIONS_TEXT_INTRO /"
            " POSITIONS_BODY, read at run time from the imported module — not transcribed"
        ),
    }


# --- the record ----------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    parser.add_argument(
        "--rows", type=int, default=SAMPLE_ROWS, help="corpus rows for the step-2 sample"
    )
    args = parser.parse_args(argv)

    if args.out.resolve() == SEALED.resolve():
        raise SystemExit(
            f"{rel(SEALED)} is uni-a's dated measurement of the code BEFORE SPEC 3.17 (8) and is"
            " not re-derivable under today's schema. Write beside it, never over it."
        )

    live_registry = load_registry(REGISTRY)
    live_lexicon = lexicon.load_lexicon(LEXICON, taxonomy=live_registry.taxonomy)

    with tempfile.TemporaryDirectory(prefix="uni-a-") as tmp:
        directory = Path(tmp)
        toy_registry_path = write_toy_registry(directory)
        toy_registry = load_registry(toy_registry_path)
        accepted_stems, rejected_stems = toy_stems_the_law_accepts(toy_registry)
        toy_lexicon_path = write_toy_lexicon(directory, live_lexicon, accepted_stems)
        toy_lexicon = lexicon.load_lexicon(toy_lexicon_path, taxonomy=toy_registry.taxonomy)

        rows, sample = corpus_sample(args.rows)
        steps = {
            "1 · positions.category_keys over the toy taxonomy": step_1_category_keys(
                toy_registry, live_registry
            ),
            "2 · the deterministic pre-filter over the corpus": step_2_prefilter(
                rows, sample, toy_registry, live_lexicon, toy_lexicon, toy_lexicon_path
            ),
            "3 · the strict parser and the tier ladder": step_3_parser_and_ladder(toy_registry),
            "4 · brand resolution over the toy watchlist": step_4_brand_resolution(toy_registry),
            "5 · prompt instantiation": step_5_prompt_instantiation(),
        }
        toy = {
            "registry": {
                "path": "a tempdir, deleted at exit — never committed",
                "sha256": sha256_of(toy_registry_path),
                "sources": len(toy_registry.sources),
                "sources_note": "the live sources block, carried over unchanged (the brief fixes"
                " the sources); only taxonomy and watchlist were swapped",
                "tracked_groups": list(TOY_TAXONOMY),
                "category_keys": sorted(positions.category_keys(toy_registry.taxonomy)),
                "watchlist": [brand["brand_id"] for brand in TOY_WATCHLIST],
            },
            "lexicon": {
                "path": "a tempdir, deleted at exit — never committed",
                "sha256": sha256_of(toy_lexicon_path),
                "tracked": {"coffee": accepted_stems},
                "stems_the_law_refused": rejected_stems,
                "why_they_were_refused": (
                    "config/lexicon.yaml's guard: a tracked stem must be a prefix of one of its"
                    " group's display names. «еспресо», «лате» and «капучино» are words a coffee"
                    " post uses and none of them is a prefix of «Кава …», so a real coffee"
                    " taxonomy either names those subcategories or exempts each stem by name, the"
                    " way ru_variants exempts «кефир»/«творог»/«морожен». Measured here rather"
                    " than worked around: this is what the law costs, and it is the cost of not"
                    " being able to carry dairy stems forward in silence"
                ),
                "why_it_exists": (
                    "the brief anticipated one toy file. The pre-filter's category half reads a"
                    " lexicon and not the registry, so a second toy file had to be built for step"
                    " 2 to run at all — that necessity is itself a finding (Dv121). Since SPEC"
                    " 3.17 (8) the toy is written in the LAW's shape and loaded through the law's"
                    " loader, guard included"
                ),
            },
        }

    verdicts = {name: step["verdict"] for name, step in steps.items()}
    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "uni-b — the universality dry run, re-run (deliverable D(4))",
        "contract": "docs/PROMPT-uni-a.md deliverable B; re-run per docs/PROMPT-uni-b.md D(4)",
        "supersedes": {
            "record": "results/uni_probe.json",
            "sha256": sha256_of(SEALED),
            "reason": (
                "uni-a's run, kept as the dated measurement of the code before SPEC 3.17 (8). It"
                " is not overwritten and not re-derivable: step 2 read a draft lexicon that is no"
                " longer what the pre-filter loads, and the schema's fifth presence field was"
                " named fat"
            ),
        },
        "asks": "what follows config/registry.yaml when the tracked category changes",
        "cost_usd": 0.0,
        "no_model": "every number here is a deterministic function of this repository's code."
        " No request was sent anywhere and no model was loaded",
        "writes": (
            "this file only. The toy registry and the toy lexicon were materialised in a tempdir"
            " and deleted at exit; data/raw/ was READ and not written; config/, src/, tests/ and"
            " every other results/ file are untouched"
        ),
        "verdict_vocabulary": {
            FOLLOWS: "the value flows from the registry it was handed — a registry edit is enough",
            FOLLOWS_LAW: "a second file carries it, but that file is LAW: it must agree with the"
            " registry's display names and refuses to load when it does not",
            NEEDS_REGISTRATION: "a new domain needs a new registered artifact, authored by hand",
            HARD_CODED: "the domain is fixed in code or in a second file the registry cannot reach",
            UNMEASURED: "the step could not be measured; the reason is stated and never guessed",
        },
        "verdicts": verdicts,
        "steps": steps,
        "toy": toy,
        "live": {
            "registry": {"path": rel(REGISTRY), "sha256": sha256_of(REGISTRY), "untouched": True},
            "lexicon": {
                "path": rel(LEXICON),
                "sha256": sha256_of(LEXICON),
                "status": "law (SPEC 3.17 (8)) — uni-a read data/category_lexicon_draft.json here",
                "untouched": True,
            },
            "prompts": {
                "count": len(prompts.PROMPTS),
                "positions": {
                    task: prompts.prompt_sha256(task) for task in sorted(prompts.POSITIONS)
                },
            },
        },
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for name, step in steps.items():
        print(f"{step['verdict']:<24} {name}")
    controls = steps["2 · the deterministic pre-filter over the corpus"]["controls_ok"]
    print(f"\nstep 2 controls: {'OK' if controls else 'FAILED'}")
    print(f"wrote {rel(args.out)}")
    return 0 if controls else 1


if __name__ == "__main__":
    raise SystemExit(main())
