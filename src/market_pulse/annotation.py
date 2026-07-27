"""Sampling maths and row shapes for the annotation batches (docs/annotation/).

The emitted rows carry the record fields the annotator needs for context plus the
empty label fields defined in the guidelines — the two must stay in step, so the
label templates live here and nowhere else.
"""

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
