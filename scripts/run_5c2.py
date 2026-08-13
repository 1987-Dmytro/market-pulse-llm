#!/usr/bin/env python3
"""5c2-run — the sealed registration's three legs, served for real.

`results/prereg_5c2_run.json` is the authority and this driver is its executor: it does not decide
a population, a price or a cap, it READS them and refuses when what is on disk has moved.

**Why this file exists.** `scripts/run_loop.py` built the three legs against stub transports and
was forbidden to register an endpoint — «the writer belongs to the paid session's contract»
(`docs/reports/5c2-prep-b.md` §4, `run_loop.py:628`). This is that writer. It changes nothing in
`market_pulse.loop`: the rendering, the evidence table, the parser and the record-before-watermark
ordering are the passes' own, exactly as the smokes measured them, and the only thing supplied here
is a live ``send``.

**The selection is the registration's, not the queue's.** `run_loop.posts_of` says it in its own
docstring: "the WINDOW is not applied here and that is deliberate — the population is the
pre-registration's to name". So the queues answer 16 218 / 159 / 717 and the registered populations
are 5 075 / 159 / 44. This driver intersects the queue with the registered selection and proves the
intersection by hash before a cent is spent:

- comments — 19 per-channel `ids_sha256`, re-derived through `census_5c2.ids_in_window` over the
  census's OWN anchor string (a bare date parses local and yields a different window);
- leaflet pages — the pinned `results/post_media_5c1.json`, whose sha the registration carries;
- posts — the 44 ids of `results/postcut_c3b.json :: rows`, whose newline-joined sha is the pin.

**One job per pack, one row per record.** The passes call ``send`` per row; the endpoint bills by
worker uptime, so a job per row would pay the round trip 5 075 times. :class:`SliceTransport`
answers the pack in ONE job and hands the pass its rows one at a time out of the reply, keyed by
content — so the durable-before-watermark ordering is untouched and the wire shape is skub2's.

    PYTHONPATH=src python3 scripts/run_5c2.py --dry-run          # $0: selections + hashes
    PYTHONPATH=src python3 scripts/run_5c2.py --leg positions --endpoint <id>
    PYTHONPATH=src python3 scripts/run_5c2.py --leg comments  --endpoint <id>
"""

import argparse
import hashlib
import json
import os
import sys
from collections import deque
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import census_5c2 as census  # noqa: E402
import positions_gm4_skub as skub  # noqa: E402
import run_loop  # noqa: E402
import runpod_guard as guard  # noqa: E402

from market_pulse import loop, parents, positions, serving  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

PHASE = "5c2run"
PREREG = REPO_ROOT / "results" / "prereg_5c2_run.json"
LEDGER = REPO_ROOT / "results" / "spend_5c2run.json"
RECORD = REPO_ROOT / "results" / "run_5c2.json"
POSITIONS_PIN = REPO_ROOT / "results" / "sku_pilot_serving_v2.json"
PARITY_PIN = REPO_ROOT / "results" / "parity_srv2.json"
POSTCUT = REPO_ROOT / "results" / "postcut_c3b.json"
CENSUS = REPO_ROOT / "results" / "census_5c2.json"

ENDPOINT_ENV = "RUNPOD_5C2_ENDPOINT"
API_KEY_ENV = "RUNPOD_API_KEY"

JOB_TIMEOUT_S = skub.JOB_TIMEOUT_S
JOB_TTL_S = skub.JOB_TTL_S
MAX_PAYLOAD_MB = skub.MAX_PAYLOAD_MB
IDLE_TAIL_SECONDS = skub.IDLE_TAIL_SECONDS

JOB_FILL = 0.6
"""How much of the execution timeout a pack is allowed to plan for.

A pack sized at the whole 900 s would end TIMED_OUT on any row slower than the marginal, and
`serving.JobExpired` ends the RUN (3.17 (10)(c)) rather than the job — and the pack is bought
before a row is written, so its rows come back unbought too. The 40% of the window this leaves is
how wrong :func:`pack_size`'s marginal is allowed to be before a leg dies rather than slows.

It is not free: fewer rows per pack means more inter-job gaps, and the worker bills through every
one of them. That is the trade this number IS, and `billed_now` is what keeps the cost of it
inside the cap arithmetic instead of outside it."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def newline_ids_sha256(ids) -> str:
    """`scripts/postcut_c3b.py`'s convention: the kept ids, NEWLINE-joined, in the record's order.

    Deliberately not shared with the comment leg's pin. `census_5c2.leg` joins on a COMMA, and one
    helper serving both would have to pick a separator — which is how a selection check goes green
    against the wrong convention. The comment leg calls `census.leg` itself rather than restate it.
    """
    return hashlib.sha256("\n".join(str(one) for one in ids).encode("utf-8")).hexdigest()


# --- the registration, and its refusals -----------------------------------------------------


def preflight(prereg: dict) -> dict:
    """Every pinned input re-hashed. A moved input is a STOP and never a re-derivation.

    The registration was sealed against these bytes; a run that priced itself from a moved census
    or scored through a moved `positions.py` would be a different experiment wearing the sealed
    numbers. The contract says it in one line: nothing is re-derived in-session to make a sealed
    number green.
    """
    moved = {}
    for path, want in prereg["pinned_inputs"].items():
        target = REPO_ROOT / path
        got = sha256_of(target) if target.exists() else "<absent>"
        if got != want:
            moved[path] = (got, want)
    if moved:
        lines = "; ".join(
            f"{name}: {got[:12]}… != {want[:12]}…" for name, (got, want) in moved.items()
        )
        raise SystemExit(
            f"the registration's pinned inputs have MOVED — {lines}. results/prereg_5c2_run.json"
            " prices this session against those bytes; stop and take it to the team lead."
        )
    return {path: "byte-identical" for path in prereg["pinned_inputs"]}


def registered_cap(prereg: dict) -> float:
    """The session cap, read from the seal rather than typed. 3.18 (7)(f) pins it by VALUE."""
    return float(prereg["session_cap"]["cap_usd"])


def phase_remaining() -> tuple[float, float]:
    """(spent, remaining) of the PHASE cap, derived — never read out of the ledger's own field.

    `spend_phase4.json :: sessions[-1].remaining_usd` is 6.1690, a true sentence about the $30 cap
    it was written beside, and 3.18 (7)(b) forbids re-scoring records under a later cap. Reading it
    would refuse an $8.00 session that fits with room.
    """
    balance = guard.balance()
    ledger = guard.read_ledger(balance)
    spent = float(ledger["runpod_balance_at_phase4_start"]) - balance
    return spent, guard.PHASE_CAP_USD - spent


# --- the three selections ---------------------------------------------------------------------


def comment_selection(store, prereg: dict) -> dict:
    """``{handle: [msg_id]}`` — the 5 075 in-window comments, per-channel hash-gated.

    The window comes from the census's own ``anchor`` STRING, passed to the census's own
    `window_of`. Neither is retyped: a bare date parses as local time and selects a different
    population, and `refuse_to_move_the_anchor` does not fire on a path it was not given.
    """
    record = json.loads(CENSUS.read_text(encoding="utf-8"))
    window = record["anchor"]
    derived_window = census.window_of(window["anchor"])
    if {key: window[key] for key in derived_window} != derived_window:
        raise SystemExit("the census's recorded window is not the one its own window_of derives")
    pins = prereg["populations"]["comment"]["selection_pin"]
    out, wrong = {}, []
    for handle, want in pins.items():
        rows = store.rows("comment", handle)
        if census.leg(rows, window)["ids_sha256"] != want:
            wrong.append(handle)
        out[handle] = census.ids_in_window(rows, window)
    if wrong:
        raise SystemExit(
            f"{len(wrong)} of {len(pins)} channels re-derive a different comment selection"
            f" ({', '.join(wrong[:4])}…). The registration pins WHICH rows, not only how many."
        )
    total = sum(len(ids) for ids in out.values())
    registered = prereg["populations"]["comment"]["rows"]
    if total != registered:
        raise SystemExit(f"{total} comments selected against {registered} registered")
    return out


def page_selection(prereg: dict) -> list[dict]:
    """The 159 leaflet pages, from the manifest whose sha the registration pins."""
    pin = prereg["populations"]["leaflet_page"]["selection_pin"]
    got = sha256_of(REPO_ROOT / pin["path"])
    if got != pin["sha256"]:
        raise SystemExit(f"{pin['path']} has moved: {got[:12]}… != {pin['sha256'][:12]}…")
    manifest = json.loads((REPO_ROOT / pin["path"]).read_text(encoding="utf-8"))
    handles = sorted({entry["channel"] for entry in manifest["entries"].values()})
    pages = [page for handle in handles for page in run_loop.pages_of(manifest, handle)]
    registered = prereg["populations"]["leaflet_page"]["rows"]
    if len(pages) != registered:
        raise SystemExit(f"{len(pages)} pages on disk against {registered} registered")
    return pages


def post_selection(prereg: dict) -> dict:
    """``{handle: [msg_id]}`` — the D cut's 44 ids, read off the record and hash-gated.

    Read, never re-derived: `scripts/postcut_c3b.py` applied 3.18 (7)(g) once and the record is
    what the registration pinned. Re-running the rule here would be a second implementation of a
    ruling, and the two could disagree without either failing.
    """
    cut = json.loads(POSTCUT.read_text(encoding="utf-8"))
    ids = [row["id"] for row in cut["rows"]]
    if newline_ids_sha256(ids) != prereg["populations"]["post_text"]["selection_pin"]:
        raise SystemExit("the post cut's ids do not re-hash to the registered selection pin")
    if len(ids) != prereg["populations"]["post_text"]["rows"]:
        raise SystemExit(f"{len(ids)} post ids against the registered population")
    out: dict[str, list[int]] = {}
    for one in ids:
        handle, _, msg_id = one.rpartition(":")
        out.setdefault(handle, []).append(int(msg_id))
    return {handle: sorted(msg_ids) for handle, msg_ids in out.items()}


def restrict(rows: list[dict], keep: set) -> list[dict]:
    """The queue, intersected with the registered selection. Order is the queue's — oldest first."""
    return [row for row in rows if row["msg_id"] in keep]


# --- the live transport -------------------------------------------------------------------------


class SliceTransport:
    """One job per pack; the pass still asks — and records — one row at a time.

    The passes were built and measured with a per-row ``send`` and that ordering is the deliverable
    of prep-b/c1: append the evidence row, let the write close, then move the watermark. Serverless
    bills the worker's uptime, so a job per row would pay 5 075 round trips on a leg whose whole
    slack is $0.12. Both hold at once here: :meth:`load` buys the pack in a single job and
    ``__call__`` hands the pass its rows out of the answer.

    Replies are keyed by the CONTENT of what was sent, in a FIFO per key, and never by position in
    the pack. Two rows that render identically get identical requests and either reply answers
    either row; a row whose key is absent is a REFUSAL, because a transport that guessed would
    file one row's answer against another's record and nothing downstream could see it.
    """

    def __init__(self, key) -> None:
        self.key = key
        self.replies: dict[str, deque] = {}
        self.calls = 0
        self.jobs = 0

    def prime(self, keys: list[str], replies: list[dict]) -> None:
        """One pack's answers, keyed by what was sent. Called by the leg, never by the pass."""
        if len(keys) != len(replies):
            raise SystemExit(
                f"{len(replies)} replies for {len(keys)} sent rows — the pack is mispaired"
            )
        self.jobs += 1
        for key, reply in zip(keys, replies):
            self.replies.setdefault(key, deque()).append(reply)

    def __call__(self, task: str, payload) -> dict:
        key = self.key(payload)
        waiting = self.replies.get(key)
        if not waiting:
            raise SystemExit(
                f"the pass asked for a row this pack never bought (key {key[:16]}…). The job and"
                " the queue have diverged — stop rather than file an answer against the wrong row."
            )
        self.calls += 1
        return waiting.popleft()


def comment_key(rendering) -> str:
    return hashlib.sha256(
        json.dumps(rendering, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def album_key(album) -> str:
    return serving.album_key(album)


def text_key(text) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


# --- the money ----------------------------------------------------------------------------------


def worst_case_job_usd(rate: float, drift: float) -> float:
    """What ONE job can bill if the clock kills it — 3.17 (10)(c)'s quantity.

    A job's row count does not bound it; the endpoint's execution timeout does. So the clause is
    checked against this constant and not against the pack in hand.
    """
    return round(JOB_TIMEOUT_S * rate * (1 + drift), 4)


def cap_gate(*, billed: float, rate: float, drift: float, cap: float) -> str | None:
    """Refuse the NEXT job when what is left of the cap cannot absorb a wedged one."""
    spent = billed * rate
    left = cap - spent
    worst = worst_case_job_usd(rate, drift)
    if left < worst:
        return (
            f"${left:.4f} left of the ${cap:.2f} session cap and one job at the {JOB_TIMEOUT_S:.0f}s"
            f" execution timeout can bill ${worst:.4f}. SPEC 3.17 (10)(c) refuses the job rather"
            " than discovering the overrun inside it"
        )
    return None


def pack_size(warmup_marginal: float, registered_marginal: float) -> int:
    """How many rows a job may plan for — from the PESSIMISTIC of the two marginals there are.

    Two reasons neither one alone may size a pack.

    A pack that overruns the execution timeout ends TIMED_OUT, and 3.17 (10)(c) ends the RUN on
    that — so a pack is not merely a slow job, it is the whole leg. It is also bought BEFORE the
    pass writes a row (:class:`SliceTransport`), so a timed-out pack loses everything it paid for
    and the rows come back unbought.

    The warm-up marginal is ONE call, and Dv180 measured a single probe over-pricing its population
    3.64x — which means it can under-price one just as easily. The registered marginal is a
    population measurement from a paid session (skub2's last in-run gate, srv-2d's counted
    seconds), and it cannot see today's endpoint. Taking the larger keeps a fast warm-up from
    inflating a pack past what a population has ever supported, and a slow one still shrinks it.
    """
    seconds = max(warmup_marginal, registered_marginal, 1e-6)
    return max(1, int(JOB_FILL * JOB_TIMEOUT_S / seconds))


def billed_now(client) -> float:
    """What this session has been billed, in the unit serverless actually charges: WALL seconds.

    `skub.billed_seconds` reads `worker_seconds`, RunPod's per-job `executionTime` summed — which
    is what the job spent computing and NOT what the worker cost. A worker with `workersMax: 1` is
    up and charged between two sequential jobs as well as inside them, and this run submits tens of
    packs where srv-2d submitted four. Pricing the cap off `worker_seconds` would leave every
    inter-job gap outside the arithmetic, all of it in the direction of spending more than the line.

    The larger of the two is taken rather than the wall alone: `wall_seconds` is None until the
    first call returns, and a gate that read None early would compare against nothing.
    """
    timing = client.timing() or {}
    return max(float(timing.get("worker_seconds") or 0.0), float(timing.get("wall_seconds") or 0.0))


# --- the legs ------------------------------------------------------------------------------------


def client_for(endpoint: str, api_key: str, dump: str | None = None):
    """srv-2d's job shape with THIS run's execution timeout — 900 s, not srv-2d's 3600 s."""
    return serving.EndpointClient(
        endpoint,
        api_key,
        retries=0,
        forward_batch_size=1,
        policy=serving.execution_policy(JOB_TIMEOUT_S, JOB_TTL_S),
        job_timeout=JOB_TIMEOUT_S,
        submit="run",
        dump_path=dump,
    )


def nongold_post(store, registry, selection: dict) -> str:
    """A real pre-filtered post the D cut REMOVED — representative, and registered by nothing.

    The post leg's population is 44 of the 349 that pass the pre-filter (3.18 (7)(g)); the other
    305 are the same instrument's same input shape and no gold row is spent measuring the clock.
    """
    compiled, screen_aliases = run_loop.prefilter_instruments(registry)
    for _, handle in run_loop.channels_of(registry, None):
        keep = set(selection.get(handle, []))
        for post in run_loop.posts_of(store, handle, compiled, screen_aliases):
            if post["msg_id"] not in keep:
                return loop.render_post(post)[1]
    raise SystemExit("no pre-filtered post outside the D cut — the warm-up has no non-gold input")


def nongold_comment(store, selection: dict) -> dict:
    """A real comment row OUTSIDE the registered window — the same shape, none of the population."""
    for handle, ids in selection.items():
        keep = set(ids)
        for row in store.rows("comment", handle):
            if row["msg_id"] not in keep and row.get("text"):
                return row | {"channel": handle}
    raise SystemExit("no comment outside the window — the warm-up has no non-gold input")


def packs_of(items: list, size: int) -> list[list]:
    """The queue cut into jobs. Order is the queue's, so a pack is always a contiguous prefix."""
    return [items[start : start + size] for start in range(0, len(items), size)]


def page_packs(pages: list[dict], count: int) -> list[list[dict]]:
    """The leaflet leg's packs, bounded by BYTES first and by the clock second.

    The clock is not the only ceiling a job has and it is not the one that bites first here. A page
    travels as a base64 `data:` URL inside the job body, and RunPod's `/run` refuses a body over
    **10 MiB** with an HTTP 400 before any worker sees it — which is what ended the first attempt of
    this session with 126 pages in one pack (Dv309). `positions_gm4_skub.jobs` is the packer that
    already knows this, at :data:`MAX_PAYLOAD_MB` = 8.0, and it never splits or re-encodes a page:
    a single page over the budget is a refusal, because dropping resolution to fit would silently
    change the instrument for exactly the densest pages.

    Both bounds compose rather than compete — pack by bytes, then cut each byte-pack by the row
    count the marginal allows. Whichever is tighter wins, per pack.
    """
    sized = [
        {"page": page, "album": album, "bytes": len(album[0])}
        for page, album in ((page, loop.render_page(loop.page_file(page))[2]) for page in pages)
    ]
    return [
        chunk
        for by_bytes in skub.jobs(sized, MAX_PAYLOAD_MB)
        for chunk in packs_of(by_bytes, count)
    ]


def measure(client, call) -> tuple[object, float]:
    """``call()``'s answer and what the worker billed for it, from the client's own clock."""
    before = skub.billed_seconds(client)
    answer = call()
    return answer, skub.billed_seconds(client) - before


def page_leg(
    client,
    transport,
    pages,
    *,
    derived,
    cursor,
    categories,
    aliases,
    revision,
    endpoint,
    marginal,
    registered_marginal,
    cap,
    rate,
    drift,
    note,
):
    """The 159 registered pages, one job per pack, the pass writing row by row."""
    handle = pages[0]["channel"]
    state = loop.channel_state(cursor, handle)
    done = []
    packs = page_packs(pages, pack_size(marginal, registered_marginal))
    print(f"  leaflet: {len(pages)} pages in {len(packs)} packs", flush=True)
    for index, pack in enumerate(packs):
        if reason := cap_gate(billed=billed_now(client), rate=rate, drift=drift, cap=cap):
            note.append(f"leaflet pack {index:02d} refused: {reason}")
            break
        albums = [item["album"] for item in pack]
        pack = [item["page"] for item in pack]
        transport.prime(
            [album_key(album) for album in albums], client.positions(loop.PAGE_TASK, albums)
        )
        summary = loop.page_pass(
            pack,
            send=transport,
            derived=derived,
            state=state,
            categories=categories,
            aliases=aliases,
            model_revision=revision,
            served_by=endpoint,
        )
        loop.save_cursor(run_loop.CURSOR, cursor)
        done.append({"pack": index} | summary)
        print(f"  leaflet pack {index:02d}: {summary}", flush=True)
    return {"channel": handle, "packs": done}


def post_leg(
    client,
    transport,
    queue,
    *,
    derived,
    cursor,
    categories,
    aliases,
    revision,
    endpoint,
    marginal,
    registered_marginal,
    cap,
    rate,
    drift,
    note,
):
    """The D cut's 44 posts, per channel, one job per pack."""
    out = []
    for handle, posts in queue.items():
        state = loop.channel_state(cursor, handle)
        for index, pack in enumerate(packs_of(posts, pack_size(marginal, registered_marginal))):
            if reason := cap_gate(billed=billed_now(client), rate=rate, drift=drift, cap=cap):
                note.append(f"post pack {handle} {index:02d} refused: {reason}")
                return out
            payloads = [loop.render_post(post)[1] for post in pack]
            transport.prime(
                [text_key(one) for one in payloads], client.positions(loop.POST_TASK, payloads)
            )
            summary = loop.post_pass(
                pack,
                send=transport,
                derived=derived,
                state=state,
                categories=categories,
                aliases=aliases,
                model_revision=revision,
                served_by=endpoint,
            )
            loop.save_cursor(run_loop.CURSOR, cursor)
            out.append({"channel": handle, "pack": index} | summary)
            print(f"  post {handle} pack {index:02d}: {summary}", flush=True)
    return out


def comment_leg(
    client,
    transport,
    queue,
    *,
    posts_map,
    captions,
    derived,
    cursor,
    revision,
    endpoint,
    marginal,
    registered_marginal,
    cap,
    rate,
    drift,
    note,
):
    """The 5 075 in-window comments, per channel, one job per pack.

    The job carries the ROW TEXT and the parent-post keywords, not the rendering: the worker builds
    the prompt from them with `prompts.build_messages`, which is the same function `render_comment`
    calls here. Sending a rendered prompt as a `text` would have the worker wrap it a second time —
    a different prefix, invisible in every record downstream.
    """
    out = []
    for handle, rows in queue.items():
        state = loop.channel_state(cursor, handle)
        for index, pack in enumerate(packs_of(rows, pack_size(marginal, registered_marginal))):
            if reason := cap_gate(billed=billed_now(client), rate=rate, drift=drift, cap=cap):
                note.append(f"comment pack {handle} {index:02d} refused: {reason}")
                return out
            keys, texts, context = [], [], []
            for row in pack:
                rendering, _ = loop.render_comment(posts_map, captions, row)
                keys.append(comment_key(rendering))
                texts.append(row["text"])
                context.append(parents.post_kwargs(parents.context(posts_map, captions, row)))
            transport.prime(keys, client.batch(loop.COMMENT_TASK, texts, context))
            summary = loop.inference_pass(
                pack,
                send=transport,
                posts=posts_map,
                captions=captions,
                derived=derived,
                state=state,
                model_revision=revision,
                served_by=endpoint,
            )
            loop.save_cursor(run_loop.CURSOR, cursor)
            out.append({"channel": handle, "pack": index} | summary)
            print(f"  comment {handle} pack {index:02d}: {summary}", flush=True)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="$0: selections, hashes, plan")
    parser.add_argument(
        "--anchor",
        action="store_true",
        help="write results/spend_5c2run.json — the balance BEFORE anything bills (Dv149). One"
        " read-only runpodctl call; the file is never regenerated once it exists.",
    )
    parser.add_argument("--leg", choices=("positions", "comments"), help="which endpoint's legs")
    parser.add_argument("--endpoint", help=f"the serving endpoint id (or ${ENDPOINT_ENV})")
    parser.add_argument("--out", type=Path, default=RECORD)
    parser.add_argument(
        "--already-usd",
        type=float,
        default=0.0,
        help="what this SESSION has already spent outside the endpoint (the staging pod, the"
        " other endpoint's legs). It comes straight off the (10)(a) budget — skub2's gate 2.",
    )
    args = parser.parse_args(argv)

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    pins = preflight(prereg)
    cap = registered_cap(prereg)
    rate = float(prereg["rate"]["value"])
    drift = float(prereg["drift"]["factor"])

    registry = load_registry(run_loop.REGISTRY)
    channels = run_loop.channels_of(registry, None)
    store = RawStore(run_loop.STORE_ROOT)
    cursor = loop.load_cursor(run_loop.CURSOR)
    derived = RawStore(run_loop.DERIVED_ROOT)

    comments = comment_selection(store, prereg)
    pages = page_selection(prereg)
    posts = post_selection(prereg)

    plan = {
        "phase": "5c2-run",
        "authority": rel(PREREG),
        "pinned_inputs": pins,
        "session_cap_usd": cap,
        "rate_usd_per_second": rate,
        "drift": drift,
        "worst_case_job_usd": worst_case_job_usd(rate, drift),
        "selection": {
            "comment": {
                "rows": sum(len(ids) for ids in comments.values()),
                "channels": len(comments),
                "pins_matched": f"{len(comments)}/{len(comments)}",
            },
            "leaflet_page": {
                "rows": len(pages),
                "posts": len({page["parent_msg_id"] for page in pages}),
                "channels": sorted({page["channel"] for page in pages}),
            },
            "post_text": {
                "rows": sum(len(ids) for ids in posts.values()),
                "channels": len(posts),
            },
        },
    }

    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        spent, left = phase_remaining()
        print(
            f"\nphase 4: ${spent:.4f} spent of ${guard.PHASE_CAP_USD:.2f},"
            f" ${left:.4f} remaining; session cap ${cap:.2f}"
        )
        print("--dry-run: no client built, nothing sent, nothing written")
        return 0

    if args.anchor:
        if LEDGER.exists():
            raise SystemExit(
                f"{rel(LEDGER)} already exists — an anchor is written ONCE. Regenerating it"
                " restarts the session counter at today's balance and hides everything spent."
            )
        balance = guard.balance()
        ledger = skub.read_ledger(LEDGER, balance, phase=PHASE, cap=cap)
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"anchored {rel(LEDGER)} at ${balance:.4f}, cap ${cap:.2f}")
        return 0

    endpoint = args.endpoint or os.environ.get(ENDPOINT_ENV)
    api_key = os.environ.get(API_KEY_ENV)
    if not endpoint or not api_key:
        raise SystemExit(f"--endpoint (or ${ENDPOINT_ENV}) and ${API_KEY_ENV} are both required")
    if not args.leg:
        raise SystemExit("--leg positions|comments: one endpoint at a time, never both (contract)")

    balance_at_start = guard.balance()
    ledger = skub.read_ledger(LEDGER, balance_at_start, phase=PHASE, cap=cap)
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    budget = cap - args.already_usd

    client = client_for(endpoint, api_key)
    categories = positions.category_keys(registry.taxonomy)
    aliases = watchlist_aliases(registry.watchlist)
    note: list[str] = []
    outcome = plan | {"leg": args.leg, "endpoint": endpoint, "already_usd": args.already_usd}

    try:
        run_the_legs(
            args,
            outcome=outcome,
            note=note,
            client=client,
            prereg=prereg,
            registry=registry,
            channels=channels,
            store=store,
            cursor=cursor,
            derived=derived,
            comments=comments,
            pages=pages,
            posts=posts,
            categories=categories,
            aliases=aliases,
            budget=budget,
            rate=rate,
            drift=drift,
        )
    except BaseException as err:  # noqa: BLE001 — the record outranks the reason (skub2's rule)
        # The boot and the warm-ups are BILLED by the time anything here can fail, and a driver
        # that dies without writing the ledger leaves a session whose spend nothing on disk names.
        # skub2 closed this hole for the (10)(a) refusal exit ("the two exits used to disagree");
        # a crash is the third exit, and the first attempt of this session hit it (Dv309). The
        # record is written below either way, and the exception is re-raised after it.
        outcome["died"] = f"{type(err).__name__}: {err}"
        note.append(f"the run ENDED on an exception: {type(err).__name__}")
        finalise(args, outcome, note, client, ledger)
        raise
    finalise(args, outcome, note, client, ledger)
    return 0


def run_the_legs(
    args,
    *,
    outcome,
    note,
    client,
    prereg,
    registry,
    channels,
    store,
    cursor,
    derived,
    comments,
    pages,
    posts,
    categories,
    aliases,
    budget,
    rate,
    drift,
):
    """The served half, one endpoint's legs. Raises; :func:`main` is what records the death."""
    endpoint = client.endpoint_id
    if args.leg == "positions":
        pin = json.loads(POSITIONS_PIN.read_text(encoding="utf-8"))["expected_worker"]
        info = serving.assert_serving(client.info(), pin)
        revision = info.get("revision_requested")
        page_queue = restrict(
            run_loop.queued_pages_by_channel(channels, cursor, derived)[pages[0]["channel"]],
            {page["msg_id"] for page in pages},
        )
        post_queue = {
            handle: restrict(rows, set(posts.get(handle, [])))
            for handle, rows in run_loop.queued_posts_by_channel(
                channels, store, cursor, derived, registry
            ).items()
            if handle in posts
        }
        # The two warm-ups of 3.17 (10)(a): REPRESENTATIVE inputs, answered OUTSIDE the passes so
        # no evidence row is written and no registered row is marked answered by an unrecorded
        # call. The page is a real leaflet page (there is no non-registered leaflet on disk — the
        # corpus IS the population) and the post is a real pre-filtered post the D cut removed.
        warm_page = loop.render_page(loop.page_file(page_queue[0]))[2]
        _, page_seconds = measure(client, lambda: client.positions(loop.PAGE_TASK, [warm_page]))
        warm_post = nongold_post(store, registry, posts)
        _, post_seconds = measure(client, lambda: client.positions(loop.POST_TASK, [warm_post]))
        gate = skub.go_no_go(
            billed=billed_now(client),
            page_marginal=page_seconds,
            text_marginal=post_seconds,
            n_pages=len(page_queue),
            n_rows=sum(len(rows) for rows in post_queue.values()),
            rate=rate,
            budget=budget,
        )
        outcome["go_no_go"] = gate
        print(json.dumps(gate, indent=1), flush=True)
        if gate["refuse"]:
            note.append("REFUSED at the (10)(a) gate — no gold call was made")
        else:
            outcome["leaflet"] = page_leg(
                client,
                SliceTransport(album_key),
                page_queue,
                derived=derived,
                cursor=cursor,
                categories=categories,
                aliases=aliases,
                revision=revision,
                endpoint=endpoint,
                marginal=page_seconds,
                registered_marginal=prereg["prices"]["leaflet_page"]["seconds_model"]["value"],
                cap=budget,
                rate=rate,
                drift=drift,
                note=note,
            )
            outcome["post_text"] = post_leg(
                client,
                SliceTransport(text_key),
                post_queue,
                derived=derived,
                cursor=cursor,
                categories=categories,
                aliases=aliases,
                revision=revision,
                endpoint=endpoint,
                marginal=post_seconds,
                registered_marginal=prereg["prices"]["post_text"]["seconds_model"]["value"],
                cap=budget,
                rate=rate,
                drift=drift,
                note=note,
            )
    else:
        pin = json.loads(PARITY_PIN.read_text(encoding="utf-8"))["config"]["serving"]["worker"]
        expected = {
            key: pin[key]
            for key in (
                "serving_config",
                "merge_state",
                "adapter_sha256",
                "max_new_tokens",
                "revision_requested",
            )
        }
        info = serving.assert_serving(client.info(), expected)
        revision = info.get("revision_requested")
        posts_map = parents.load(run_loop.STORE_ROOT / "posts")
        captions = parents.load_captions(run_loop.CAPTIONS)
        queue = {
            handle: restrict(
                loop.queued(
                    store, derived, handle, loop.channel_state(cursor, handle).get(loop.INFERENCE)
                ),
                set(ids),
            )
            for handle, ids in comments.items()
        }
        warm_row = nongold_comment(store, comments)
        rendering, _ = loop.render_comment(posts_map, captions, warm_row)
        _, row_seconds = measure(
            client,
            lambda: client.batch(
                loop.COMMENT_TASK,
                [warm_row["text"]],
                [parents.post_kwargs(parents.context(posts_map, captions, warm_row))],
            ),
        )
        gate = skub.go_no_go(
            billed=billed_now(client),
            page_marginal=0.0,
            text_marginal=row_seconds,
            n_pages=0,
            n_rows=sum(len(rows) for rows in queue.values()),
            rate=rate,
            budget=budget,
        )
        outcome["go_no_go"] = gate | {
            "registered_corner_usd": prereg["legs"]["comment"]["usd_with_drift"]
        }
        print(json.dumps(outcome["go_no_go"], indent=1), flush=True)
        if gate["refuse"]:
            note.append("REFUSED at the (10)(a) gate — no gold call was made")
        else:
            outcome["comment"] = comment_leg(
                client,
                SliceTransport(comment_key),
                queue,
                posts_map=posts_map,
                captions=captions,
                derived=derived,
                cursor=cursor,
                revision=revision,
                endpoint=endpoint,
                marginal=row_seconds,
                registered_marginal=prereg["prices"]["comment"]["seconds_model"]["value"],
                cap=budget,
                rate=rate,
                drift=drift,
                note=note,
            )


def finalise(args, outcome: dict, note: list, client, ledger: dict) -> None:
    """The ledger row and the run record, on EVERY exit that could have billed.

    Called from both arms of `main`'s try: a completed leg and a dead one leave the same two
    artifacts, because the question "what did this session spend" has to be answerable from disk
    whichever way the session ended. The balance read goes through `spend_or_note`, which refuses
    to let a failed `runpodctl` call take the record down with it (Dv33: the delta is a FLOOR).
    """
    outcome["timing"] = client.timing()
    outcome["notes"] = note
    balance, spent, why = skub.spend_or_note(ledger, phase=PHASE)
    outcome["ledger"] = {"balance": balance, "session_spent_usd_floor": spent, "unread": why}
    skub.log_run(
        ledger,
        LEDGER,
        balance,
        spent,
        f"5c2-run {args.leg}",
        cost_note=outcome.get("died"),
    )
    args.out.write_text(
        json.dumps(
            {"at": datetime.now(UTC).isoformat(timespec="seconds")} | outcome,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {rel(args.out)}")


if __name__ == "__main__":
    raise SystemExit(main())
