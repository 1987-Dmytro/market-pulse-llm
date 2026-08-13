"""The per-row evidence the 5c2-validate sitting is built from — the ONE place that names it.

SPEC amendment 3.18 (6) makes an operator sitting a condition of closing Phase 5c2: five leaflet
posts and five comments, original beside verdict, drawn under a recorded seed from the window's own
output. Its binding consequence for the loop is a sentence in the amendment itself — **the pack is
unbuildable unless the run PERSISTS its per-row evidence**, so the persistence is a prep deliverable
and not an afterthought. `results/predictions/LOST.md` is the precedent it exists to stop repeating:
a per-row dump that was never written and cannot be reconstructed at any price.

:data:`REQUIRED` and :data:`KIND_FIELDS` are that one place. A field is deleted from the pack by
deleting it here, which is what makes :func:`assert_complete` — and not an evening with the
operator — the thing that notices.

Presence, not truthiness. ``model_revision`` has no answer at $0 and ``parent_msg_id`` is legitimately
``None`` for a row that is not a comment; an ABSENT key and a key holding ``None`` are different
states, and only the second one can be read later. So every check below asks whether the key is
there, never what it holds.
"""

from datetime import UTC, datetime

from market_pulse import positions, prompts

KINDS = ("comment", "leaflet_page", "position_row")
"""The three row shapes 3.18 (6) asks the sitting to show. A `comment` is one audience reaction with
its parent post; a `leaflet_page` is one page as it was sent; a `position_row` is one SKU the page or
the row yielded."""

REQUIRED = (
    "row_kind",
    "at",
    "channel",
    "msg_id",
    "parent_msg_id",
    "task",
    "prompt_sha256",
    "model_revision",
    "served_by",
    "rendering",
    "reply",
)
"""What EVERY row carries, whatever its kind.

``rendering`` is the exact request handed to the model, not a description of it, and ``reply`` is
what came back before any parsing — those two are what let the sitting read "original beside
verdict" rather than a verdict alone. ``task`` and ``prompt_sha256`` name the instrument, and
``served_by`` names the transport that answered: a row served by a stub and a row served by a
registered endpoint must never be indistinguishable in the file they land in."""

KIND_FIELDS = {
    "comment": (),
    "leaflet_page": ("image_path", "image_sha256"),
    # SPEC 3.18 (6) asks the sitting to see "what made each a POSITION rather than a
    # product_mention" — field by field. `presence` is those five booleans and `tier` is what the
    # ladder assigned, so the rung can be RE-DERIVED at the sitting instead of trusted; `warnings`
    # is SPEC 3.17 (13)(a)'s three, which the skub2 run computed and dropped (Dv232).
    "position_row": ("presence", "tier", "warnings"),
}
"""What each kind carries on top of :data:`REQUIRED`. A kind with nothing of its own says so with an
empty tuple rather than by being absent — the table is read whole, and a kind the table does not
know is a refusal."""


def presence(position: positions.Position) -> dict:
    """One position as the five booleans :func:`positions.tier_from_presence` reads.

    Written here rather than in `market_pulse.positions` for one reason and it is not taste:
    `src/market_pulse/positions.py` is pinned by sha256 inside `results/sku_pilot_prereg_b2.json`,
    and a sealed pre-registration is not re-pinned to make room for a new function.

    That makes this a SECOND implementation of a mapping the ladder already owns, which is exactly
    the drift `tier_from_presence` was built to prevent — so the drift is closed by a test rather
    than by a comment: `tests/test_evidence.py::test_the_presence_fields_re_derive_the_ladders_own_tier`
    asserts ``tier_from_presence(**presence(p)) == p.tier()`` over every combination of the four
    optional fields. If they ever disagree, the sitting would re-derive a rung from inputs that do
    not produce it, and nothing in the record could say so.

    The keys are :data:`positions.PRESENCE_FIELDS` and the same test holds them to it: a key spelled
    differently here is a `TypeError` at the ladder, which is the loud direction.
    """
    return {
        "brand": bool(position.brand_id or position.brand_raw),
        "line": position.line is not None,
        "category": position.category is not None,
        "size": positions.has_size(position),
        "attribute": position.attribute_pct is not None,
    }


def record(
    row_kind: str,
    *,
    channel: str,
    msg_id: int,
    parent_msg_id,
    task: str,
    model_revision,
    served_by: str,
    rendering,
    reply,
    **extra,
) -> dict:
    """One evidence row, with its prompt sha DERIVED rather than passed in.

    ``prompt_sha256`` is computed from ``task`` here and nowhere else: a caller that could pass both
    could pass a sha that does not belong to the prompt it names, and a record whose instrument
    fields disagree is worse than one that lacks them — it reads as provenance.

    ``extra`` carries the kind's own fields (:data:`KIND_FIELDS`) and anything a caller wants beside
    them. Extras are not refused — 3.18 (6) says "at minimum" — but they do not satisfy the table
    either: :func:`assert_complete` is what decides, and it runs on the result before it is returned,
    so a row that could not be shown at the sitting never reaches the disk.
    """
    if row_kind not in KINDS:
        raise ValueError(f"row_kind {row_kind!r} is not one of {list(KINDS)}")
    # `**extra` sits LAST in the dict below, so without this a caller passing `prompt_sha256=` would
    # silently replace the derived one and the docstring above would be a lie the record carries.
    # Found by `tests/test_evidence.py::test_the_prompt_sha_is_derived_from_the_task_and_cannot_be
    # _passed_in`, which asserted the refusal before this existed.
    if clash := sorted(set(extra) & set(REQUIRED)):
        raise ValueError(
            f"{clash} are fields this record builds itself and cannot be handed in — a caller that"
            " could pass `prompt_sha256` could pass one that does not belong to the task it names"
        )
    return assert_complete(
        {
            "row_kind": row_kind,
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "channel": channel,
            "msg_id": msg_id,
            "parent_msg_id": parent_msg_id,
            "task": task,
            "prompt_sha256": prompts.prompt_sha256(task),
            "model_revision": model_revision,
            "served_by": served_by,
            "rendering": rendering,
            "reply": reply,
            **extra,
        }
    )


def missing(row: dict) -> list[str]:
    """Which fields of the pack's table this row does not carry. Empty means it is showable."""
    kind = row.get("row_kind")
    if kind not in KINDS:
        return ["row_kind"]
    return [field for field in (*REQUIRED, *KIND_FIELDS[kind]) if field not in row]


def assert_complete(row: dict) -> dict:
    """Return the row, or raise naming every field the sitting would have asked for and not found.

    Every field at once rather than the first one: a writer fixing these one exception at a time
    learns the table one field per run, and the run that teaches it is the paid one.
    """
    absent = missing(row)
    if absent:
        raise ValueError(
            f"a {row.get('row_kind')!r} evidence row is missing {absent} — SPEC 3.18 (6) builds the"
            " validation pack out of these fields and it cannot be rebuilt afterwards from rows"
            " that never kept them (results/predictions/LOST.md is the precedent). Add the field or"
            " take it out of market_pulse.evidence, which is the one place that names it."
        )
    return row
