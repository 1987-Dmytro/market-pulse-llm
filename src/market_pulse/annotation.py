"""Sampling maths, row shapes and label validation for the annotation batches.

The emitted rows carry the record fields the annotator needs for context plus the
empty label fields defined in the guidelines — the two must stay in step, so the
label templates live here and nowhere else, and so does the checker that says
whether a filled-in batch still matches docs/annotation/.
"""

from collections import Counter
from dataclasses import dataclass, field

COMMENT_LABELS = {
    "sentiment": None,
    "sarcasm": None,
    "intents": [],
    "unclear": False,
    "annotator": None,
    "notes": "",
}

POST_LABELS = {
    "relevant": None,
    "post_type": None,
    "brands": [],
    "unclear": False,
    "annotator": None,
    "notes": "",
}


def blank_labels(template: dict) -> dict:
    """Fresh label fields — the list values must not be shared between rows."""
    return {
        key: list(value) if isinstance(value, list) else value for key, value in template.items()
    }


def allocate(capacity: dict, total: int, weight: dict | None = None) -> dict:
    """Split ``total`` across strata in proportion to size, capped by what exists.

    A stratum smaller than its proportional share gives the remainder back to the
    others instead of shrinking the batch. ``weight`` scales a stratum's share —
    weight 2 draws twice as many rows per available row, which is how posts that
    carry comments are oversampled.
    """
    weight = weight or {}
    quota = {key: 0 for key in capacity}
    remaining = min(total, sum(capacity.values()))

    while remaining > 0:
        room = {key: capacity[key] - quota[key] for key in capacity if capacity[key] > quota[key]}
        if not room:
            break
        effective = {key: capacity[key] * weight.get(key, 1) for key in room}
        pool = sum(effective.values())
        ideal = {key: remaining * effective[key] / pool for key in room}

        taken = 0
        for key, share in ideal.items():
            grant = min(int(share), room[key])
            quota[key] += grant
            taken += grant
        remaining -= taken

        if taken == 0:
            # Fewer rows left than strata: hand out one each, largest share first,
            # ties broken by key so the batch is reproducible.
            order = sorted(room, key=lambda key: (-ideal[key], str(key)))[:remaining]
            for key in order:
                quota[key] += 1
            remaining -= len(order)
    return quota


def stratified_sample(rows: list[dict], key, total: int, rng, weight_of=None):
    """Draw ``total`` rows spread over the strata ``key`` puts them in.

    ``weight_of(stratum) -> int`` oversamples a stratum — weight 3 on the sarcastic
    cells is how the review sample spends its budget where label quality is least
    certain. Returns the drawn rows and ``stratum -> (pool size, drawn)``.
    """
    strata: dict = {}
    for row in rows:
        strata.setdefault(key(row), []).append(row)
    for pool in strata.values():
        pool.sort(key=lambda row: str(row["id"]))

    weight = {name: weight_of(name) for name in strata} if weight_of else None
    quota = allocate({name: len(pool) for name, pool in strata.items()}, total, weight=weight)

    picked = []
    for name in sorted(strata, key=str):
        picked += rng.sample(strata[name], quota[name])
    table = {name: (len(strata[name]), quota[name]) for name in sorted(strata, key=str)}
    return picked, table


def comment_row(record: dict, language: str) -> dict:
    return {
        "id": f"{record['channel']}:{record['msg_id']}",
        "source_id": record["source_id"],
        "source_type": record["provenance"]["source_type"],
        "channel": record["channel"],
        "msg_id": record["msg_id"],
        "parent_msg_id": record["parent_msg_id"],
        "date": record["date"],
        "language": language,
        "text": record["text"],
        **blank_labels(COMMENT_LABELS),
    }


def post_row(record: dict, language: str) -> dict:
    return {
        "id": f"{record['channel']}:{record['msg_id']}",
        "source_id": record["source_id"],
        "source_type": record["provenance"]["source_type"],
        "channel": record["channel"],
        "msg_id": record["msg_id"],
        "date": record["date"],
        "language": language,
        "text": record["text"],
        "has_media": record["has_media"],
        "reply_count": record["reply_count"],
        **blank_labels(POST_LABELS),
    }


# --- validation -------------------------------------------------------------
# Legal values come straight from docs/annotation/comments.md and posts.md; a
# batch that disagrees with them cannot be scored, so the checker is the gate
# between labelling and every number downstream.

SENTIMENTS = ("positive", "negative", "neutral")
INTENTS = ("taste", "price", "packaging", "quality", "availability")
POST_TYPES = ("launch", "promo", "other")

TEMPLATES = {"comments": COMMENT_LABELS, "posts": POST_LABELS}
# Filled by hand for every labelled row; a row with some of them set and some
# still null is a half-done row, not a legal state.
REQUIRED = {
    "comments": ("sentiment", "sarcasm", "annotator"),
    "posts": ("relevant", "post_type", "annotator"),
}


@dataclass
class BatchReport:
    violations: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.violations


def row_state(row: dict, kind: str) -> str:
    """``unlabeled`` | ``labeled`` | ``partial`` — progress of one row."""
    filled = [row.get(name) is not None for name in REQUIRED[kind]]
    if not any(filled):
        return "unlabeled"
    return "labeled" if all(filled) else "partial"


def _check_common(row: dict) -> list[str]:
    bad = []
    if not isinstance(row.get("unclear"), bool):
        bad.append(f"unclear must be a bool, got {row.get('unclear')!r}")
    if not isinstance(row.get("notes"), str):
        bad.append(f"notes must be a string, got {row.get('notes')!r}")
    annotator = row.get("annotator")
    if not isinstance(annotator, str) or not annotator.strip():
        bad.append(f"annotator must be a non-empty string, got {annotator!r}")
    return bad


def check_labels(row: dict, kind: str, brand_ids: tuple[str, ...] = ()) -> list[str]:
    """Legal-value violations of one labelled row, empty when it is clean."""
    bad = _check_common(row)
    if kind == "comments":
        if row.get("sentiment") not in SENTIMENTS:
            bad.append(f"sentiment {row.get('sentiment')!r} not in {SENTIMENTS}")
        if not isinstance(row.get("sarcasm"), bool):
            bad.append(f"sarcasm must be a bool, got {row.get('sarcasm')!r}")
        intents = row.get("intents")
        if not isinstance(intents, list):
            bad.append(f"intents must be a list, got {intents!r}")
        else:
            unknown = [i for i in intents if i not in INTENTS]
            if unknown:
                bad.append(f"unknown intents {unknown} (legal: {list(INTENTS)})")
            if len(set(intents)) != len(intents):
                bad.append(f"duplicate intents in {intents}")
        return bad

    if not isinstance(row.get("relevant"), bool):
        bad.append(f"relevant must be a bool, got {row.get('relevant')!r}")
    # posts.md: post_type is labelled for every post, irrelevant ones included.
    if row.get("post_type") not in POST_TYPES:
        bad.append(f"post_type {row.get('post_type')!r} not in {POST_TYPES}")
    brands = row.get("brands")
    if not isinstance(brands, list):
        bad.append(f"brands must be a list, got {brands!r}")
        return bad
    for brand in brands:
        if not isinstance(brand, dict) or set(brand) != {"brand_id", "mention"}:
            bad.append(f"brand entry needs exactly brand_id and mention: {brand!r}")
            continue
        mention = brand["mention"]
        if not isinstance(mention, str) or not mention.strip():
            bad.append(f"brand mention must be a non-empty string: {brand!r}")
        if brand["brand_id"] is not None and brand["brand_id"] not in brand_ids:
            bad.append(f"brand_id {brand['brand_id']!r} is not in the watchlist")
    return bad


def check_batch(
    rows: list[dict],
    pristine: list[dict],
    kind: str,
    brand_ids: tuple[str, ...] = (),
) -> BatchReport:
    """Compare a batch against its pristine copy and the guidelines' value sets."""
    report = BatchReport()
    record_fields = (
        [name for name in pristine[0] if name not in TEMPLATES[kind]] if pristine else []
    )
    by_id = {}
    for row in rows:
        if row["id"] in by_id:
            report.violations.append(f"{row['id']}: duplicate id")
        by_id[row["id"]] = row

    original = {row["id"]: row for row in pristine}
    for missing in sorted(set(original) - set(by_id)):
        report.violations.append(f"{missing}: row lost — not in the batch any more")
    for added in sorted(set(by_id) - set(original)):
        report.violations.append(f"{added}: row is not in the pristine copy")

    for row_id in sorted(set(by_id) & set(original)):
        row, source = by_id[row_id], original[row_id]
        changed = [name for name in record_fields if row.get(name) != source[name]]
        if changed:
            report.violations.append(f"{row_id}: record fields edited: {', '.join(changed)}")
        missing = [name for name in TEMPLATES[kind] if name not in row]
        if missing:
            report.violations.append(f"{row_id}: label fields missing: {', '.join(missing)}")
            continue
        state = row_state(row, kind)
        if state == "partial":
            # One clear message beats "sarcasm must be a bool" about a null nobody
            # has reached yet — the row is unfinished, not wrong.
            blank = [name for name in REQUIRED[kind] if row.get(name) is None]
            report.violations.append(f"{row_id}: half-labelled, still null: {', '.join(blank)}")
        elif state == "labeled":
            report.violations += [f"{row_id}: {bad}" for bad in check_labels(row, kind, brand_ids)]

    report.stats = batch_stats(rows, kind)
    return report


# --- operator review --------------------------------------------------------
# The review CSV comes back with one verdict per row; `fix:` is the only way a
# label changes after the batch was labelled, so the syntax is parsed strictly
# and a typo raises instead of silently leaving the wrong label in place.

BOOL_FIELDS = ("sarcasm", "unclear", "relevant")
BOOL_WORDS = {"1": True, "true": True, "0": False, "false": False}


def parse_verdict(verdict: str, kind: str) -> dict | None:
    """The label changes one ``operator_verdict`` cell asks for.

    ``ok`` → no changes, an empty cell → ``None`` (the row was not reviewed),
    ``unclear`` → the escape hatch, ``fix:field=value[,field=value...]`` → those
    fields. Raises ``ValueError`` naming the defect on anything else.
    """
    text = verdict.strip()
    if not text:
        return None
    if text == "ok":
        return {}
    if text == "unclear":
        return {"unclear": True}
    if not text.startswith("fix:"):
        raise ValueError(f"verdict must be ok, unclear or fix:field=value — got {verdict!r}")

    changes: dict = {}
    for pair in text[len("fix:") :].split(","):
        name, sign, value = (part.strip() for part in pair.partition("="))
        if not sign or not name:
            raise ValueError(f"fix needs field=value, got {pair!r}")
        if name not in TEMPLATES[kind]:
            raise ValueError(f"{name!r} is not a {kind} label field")
        if isinstance(TEMPLATES[kind][name], list):
            raise ValueError(f"{name!r} is a list — fix it in the batch by hand, not by verdict")
        if name in changes:
            raise ValueError(f"{name!r} fixed twice in {verdict!r}")
        if name in BOOL_FIELDS:
            if value.lower() not in BOOL_WORDS:
                raise ValueError(f"{name}={value!r} is not a boolean")
            value = BOOL_WORDS[value.lower()]
        changes[name] = value
    return changes


def _list_field(row: dict, name: str, of_dicts: bool = False) -> list:
    """The list a row holds under ``name``, tolerating whatever a bad row holds.

    Stats are printed next to the violations, so they must survive the very rows
    the violations are about.
    """
    value = row.get(name)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)] if of_dicts else value


def batch_stats(rows: list[dict], kind: str) -> dict:
    """Coverage and per-label distributions over the rows that carry labels."""
    states = Counter(row_state(row, kind) for row in rows)
    labeled = [row for row in rows if row_state(row, kind) == "labeled"]
    dist: dict[str, Counter] = {}
    if kind == "comments":
        dist["sentiment"] = Counter(row["sentiment"] for row in labeled)
        dist["sarcasm"] = Counter(str(row["sarcasm"]) for row in labeled)
        intents = [_list_field(row, "intents") for row in labeled]
        dist["intents"] = Counter(intent for row in intents for intent in row)
        dist["intents"]["(none)"] = sum(1 for row in intents if not row)
    else:
        brands = [_list_field(row, "brands", of_dicts=True) for row in labeled]
        dist["relevant"] = Counter(str(row["relevant"]) for row in labeled)
        dist["post_type"] = Counter(row["post_type"] for row in labeled)
        dist["brand_id"] = Counter(
            brand.get("brand_id") or "(off-watchlist)" for row in brands for brand in row
        )
        dist["brand_id"]["(no brands)"] = sum(1 for row in brands if not row)
    dist["unclear"] = Counter(str(row["unclear"]) for row in labeled)
    dist["annotator"] = Counter(row["annotator"] for row in labeled)
    unclear = sum(1 for row in labeled if row["unclear"])
    return {
        "total": len(rows),
        "labeled": states["labeled"],
        "partial": states["partial"],
        "unlabeled": states["unlabeled"],
        "unclear": unclear,
        "unclear_share": unclear / len(labeled) if labeled else 0.0,
        "dist": dist,
    }
