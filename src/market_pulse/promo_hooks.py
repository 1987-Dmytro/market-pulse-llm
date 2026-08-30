"""The four hooks between calls — and a failure is a COUNTED ROW, never an exception.

`docs/PHASE-promo-pulse-1.md` §2 S4: «Hooks between calls: msg_id exists · quote is a substring ·
brand ∈ registry or `unknown-brand` · schema valid; a hook failure is a counted row, not an
exception.» The counting is the whole design. An exception ends a paid pass on its worst row and
loses every good row before it; a counted row lets the pass finish and puts the failure rate in
front of the team lead, which is the number that says whether the instrument is usable.

`unknown-brand` is the one literal here that does NOT go on the wire. It appears nowhere in this
codebase, and the store already has the state: `positions.brand_id IS NULL` with the surface form
kept in `brand_raw` (65 of the 145 rows today). :func:`brand_is_resolvable` asserts that PAIR — a
brand either resolves to a watchlist id or is carried as raw text — and does not invent a third
value (plan §5.9). If the team lead wants the literal on the wire it is a rendering of this state,
never a second way to mean it.
"""

from __future__ import annotations

from dataclasses import dataclass

HOOKS = ("msg_id_exists", "quote_is_a_substring", "brand_is_resolvable", "schema_valid")
"""The four, in the order §2 S4 names them. Closed: a fifth check is a fifth name here, so a
report's per-hook counts cannot silently stop covering something."""

REQUIRED = {
    "about": ("msg_id", "subject_type", "subject", "source"),
    "signal": ("type", "subject_type", "subject", "msg_id", "quote"),
}
"""What a row of each kind must carry for `schema_valid` to hold. Presence and type only — the
closed VOCABULARIES are checked by :func:`schema_valid` against the lists the prompt renders, so
the prompt and the hook cannot drift into two definitions."""


@dataclass(frozen=True)
class Failure:
    """One row that did not pass one hook. Counted, carried, and never raised."""

    hook: str
    kind: str
    msg_id: object
    detail: str


def msg_id_exists(row: dict, texts: dict) -> Failure | None:
    """The row points at a comment the thread actually holds.

    Keyed on the id space the STORE uses: comment ids are strings in `raw_store.comment_record` and
    a model answers with an int, so both sides are stringified. Two int fields in two namespaces is
    how a join silently matches the wrong row ([[id_spaces_that_look_comparable]]).
    """
    if str(row.get("msg_id")) in texts:
        return None
    return Failure("msg_id_exists", row["_kind"], row.get("msg_id"), "no such comment in the thread")


def quote_is_a_substring(row: dict, texts: dict) -> Failure | None:
    """The quote is a substring of the comment it cites — the evidence hook.

    Compared after collapsing whitespace on both sides and nothing else. Case is NOT folded: a quote
    is meant to be what the person wrote, and a fold would let a paraphrase through on the one axis
    a reader would notice.
    """
    if row["_kind"] != "signal":
        return None
    text = texts.get(str(row.get("msg_id")))
    if text is None:
        return None  # msg_id_exists already counted this row; one failure per cause
    quote, source = " ".join((row.get("quote") or "").split()), " ".join(text.split())
    if quote and quote in source:
        return None
    return Failure("quote_is_a_substring", row["_kind"], row.get("msg_id"), f"quote {quote[:40]!r}")


def brand_state(row: dict, brand_ids: set) -> str | None:
    """`resolved` | `raw` | None — which of the store's two brand states this row lands in.

    Reported beside the hook counts, because "how many brands did not resolve" is the number that
    says whether the watchlist needs a row, and a hook that only refuses cannot answer it.
    """
    if row.get("subject_type") != "brand":
        return None
    subject = (row.get("subject") or "").strip()
    folded = {one.casefold() for one in brand_ids}
    return "resolved" if subject.casefold() in folded else "raw"


def brand_is_resolvable(row: dict, brand_ids: set) -> Failure | None:
    """A `brand` subject resolves to a watchlist id, or is carried as READABLE raw surface text.

    The store's own two-state answer (`brand_id IS NULL` + `brand_raw`), not a third literal. Only
    `subject_type == "brand"` is held to it: a chain, an sku or the post itself is not a watchlist
    row and never was. Unresolved is LEGAL — 65 of the store's 145 position rows are unresolved
    today — so the only way this hook fires is a brand row with nothing in it to resolve or to keep,
    which is the one state neither half of the pair can represent.
    """
    if row.get("subject_type") != "brand":
        return None
    if (row.get("subject") or "").strip():
        return None
    return Failure("brand_is_resolvable", row["_kind"], row.get("msg_id"), "empty brand subject")


def schema_valid(row: dict, vocabulary: dict) -> Failure | None:
    """Every required field present, and every closed field inside its own list."""
    kind = row["_kind"]
    missing = [name for name in REQUIRED[kind] if row.get(name) in (None, "")]
    if missing:
        return Failure("schema_valid", kind, row.get("msg_id"), f"missing {', '.join(missing)}")
    if row["subject_type"] not in vocabulary["subject_types"]:
        return Failure("schema_valid", kind, row.get("msg_id"), f"subject_type {row['subject_type']}")
    if kind == "about" and row.get("source") not in vocabulary["attribution_sources"]:
        return Failure("schema_valid", kind, row.get("msg_id"), f"source {row.get('source')}")
    if kind == "signal" and row.get("type") not in vocabulary["signal_types"]:
        return Failure("schema_valid", kind, row.get("msg_id"), f"type {row.get('type')}")
    return None


def screen(answer: dict, comments: list[dict], brand_ids: set, vocabulary: dict) -> dict:
    """Every emitted row through all four hooks. Returns the kept rows AND the counted failures.

    A row that fails any hook is dropped from `kept` and appears once per hook it failed, so the
    per-hook counts add up to something a reader can act on rather than to the number of bad rows.
    The parse failure, if the answer had one, is carried through as its own counted state: an empty
    `about` list from a refusal and an empty one from a thread with nothing to say are two different
    things ([[empty_field_hides_several_states]]).
    """
    texts = {str(row["msg_id"]): (row.get("text") or "") for row in comments}
    kept: dict[str, list[dict]] = {"about": [], "signal": []}
    failures: list[Failure] = []
    for kind, key in (("about", "about"), ("signal", "signals")):
        for row in answer.get(key) or []:
            row = {**row, "_kind": kind}
            found = [
                failure
                for failure in (
                    schema_valid(row, vocabulary),
                    msg_id_exists(row, texts),
                    quote_is_a_substring(row, texts),
                    brand_is_resolvable(row, brand_ids),
                )
                if failure is not None
            ]
            failures.extend(found)
            if not found:
                kept[kind].append({name: value for name, value in row.items() if name != "_kind"})
    states = [
        state
        for kind, key in (("about", "about"), ("signal", "signals"))
        for row in answer.get(key) or []
        if (state := brand_state({**row, "_kind": kind}, brand_ids)) is not None
    ]
    return {
        "kept": kept,
        "failures": [vars(failure) for failure in failures],
        "brand_states": {
            "resolved": states.count("resolved"),
            "raw": states.count("raw"),
            "note": "raw is the store's `brand_id IS NULL` + `brand_raw`, not a failure — 65 of the"
            " 145 position rows on disk are in that state (plan §5.9)",
        },
        "counts": {hook: sum(1 for f in failures if f.hook == hook) for hook in HOOKS},
        "rows_in": len(answer.get("about") or []) + len(answer.get("signals") or []),
        "rows_kept": len(kept["about"]) + len(kept["signal"]),
        "parse_failure": answer.get("parse_failure"),
        "unsure": answer.get("unsure") or [],
    }
