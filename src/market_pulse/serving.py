"""The production serving endpoint, as a client the eval cannot tell from the pod (Phase 5b).

SPEC amendment 3.11 (2) pre-registers one measurement: the EXACT production configuration,
scored once against test v4 beside the 4.5h2 gate numbers. That only means anything if the
one thing that changes between the two runs is *where the weights live*. So:

- the prompts, the rendering, the parser, the failure taxonomy, the record builder and the
  scorer are 4.5h2's, untouched;
- generation happens through `local_llm.LocalClient` — on the worker, not here. This module
  ships ``(task, texts, posts)`` over HTTP and returns the reply dicts that come back, in
  the shape `classify_local` already reads. A client that re-rendered the prompt on this
  side would be measuring two stacks at once;
- what the worker is actually serving is **asserted**, not assumed. :meth:`EndpointClient.info`
  makes the worker name its adapter sha, its quantization and its merge state, and the eval
  refuses before the first paid row if any of them is not the configuration the phase
  registered. A serving-parity number produced against an unknown config measures nothing.

Cost is deliberately *measured* rather than priced from a table: RunPod's published
per-second rates move, and the phase's $4 stop is enforced against `runpod_guard`'s balance
delta either way. :func:`project_pair_usd` therefore takes a dollars-per-second that the
smoke observed — the balance the guard says was actually spent, divided by the **wall-clock**
seconds the client held the endpoint — so the projection the abort rule reads is arithmetic
over two measurements, not a quoted price. Wall clock and not summed ``executionTime``: a
worker bills while it is up, including the gaps between sequential rows.
"""

import json
import time
import urllib.error
import urllib.request
from collections import Counter

from market_pulse.zero_shot import RETRYABLE, ApiError

BASE_URL = "https://api.runpod.ai/v2"

POD_BASE_URL = "http://127.0.0.1:8000"
"""Where the same worker answers when it runs on a pod (SPEC amendment 3.11 (1), 2026-08-06).

The runtime ruling moved production off serverless and onto a stop-after pod, and the RunPod
SDK serves the *same* handler over HTTP with ``--rp_serve_api``: `POST /runsync` and
`POST /status/<id>`, the identical job envelope, one process further down the same
``start.sh → serve_handler → local_llm`` stack. So the runtime moved and the client did not —
which is the only reason a number produced through it is comparable to 4.5h2's at all.

Loopback on purpose: the driver runs on the pod beside the worker. A pod's HTTP port is
reachable through RunPod's public proxy, and an unauthenticated model server on it is not
something this phase needs.
"""

DEFAULT_TIMEOUT = 300.0
"""One row, batch 1, greedy, 256 new tokens: ~3 s warm on the 4.5h2 pod. A per-row budget."""

HANDSHAKE_TIMEOUT = 1800.0
"""What :meth:`EndpointClient.info` waits, and it is deliberately not the per-row budget.

The first job on a cold endpoint pays for a 31 B model arriving and quantizing to NF4 —
minutes, and tens of minutes if the weights are not cached on the endpoint. With
``retries=0`` a 300 s deadline would raise `ApiError(408)` on the handshake, abort the run,
and still be billed for the boot: the most expensive way to learn nothing.
"""

POLL_SECONDS = 5.0
TERMINAL = frozenset({"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"})


def endpoint_url(endpoint_id: str, path: str) -> str:
    return f"{BASE_URL}/{endpoint_id}/{path}"


def _post(url: str, key: str, payload: dict | None, timeout: float) -> dict:
    """One RunPod call. The only function here that touches the network."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        raise ApiError(err.code, err.read().decode("utf-8", "replace")[:400]) from None
    except OSError as err:  # a socket timeout is not an answer, and must not read as one
        raise ApiError(-1, f"{type(err).__name__}: {err}") from None
    try:
        return json.loads(raw)
    except ValueError:
        raise ApiError(-1, f"undecodable body: {raw[:200]}") from None


class EndpointClient:
    """`local_llm.LocalClient`'s interface over a RunPod serverless endpoint.

    ``batch`` returns one reply dict per text, in order, with the keys
    ``content`` / ``finish_reason`` / ``cost`` / ``usage`` / ``generation_id`` —
    the same dict the OpenRouter and pod clients return, so nothing downstream
    can tell which backend ran.

    ``cost`` is 0.0 per row for the same reason the pod's is: serverless bills
    the worker's uptime, not rows. What this counts instead is :meth:`timing` —
    RunPod's per-job ``executionTime`` and ``delayTime`` beside the wall-clock span
    the client actually held the endpoint, which is the quantity the bill tracks.
    """

    def __init__(
        self,
        endpoint_id: str,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        handshake_timeout: float = HANDSHAKE_TIMEOUT,
        retries: int = 0,
    ) -> None:
        self.endpoint_id, self.api_key = endpoint_id, api_key
        # None means RunPod's own API, which keys the endpoint in the path. A base URL
        # means the worker's own server on a pod, where there is no endpoint to key by and
        # `endpoint_id` is a label for the record — the pod id, not a routable thing.
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout, self.handshake_timeout = timeout, handshake_timeout
        self.retries = retries
        self.usage = Counter()
        self.worker_seconds = 0.0
        self.queue_seconds = 0.0
        self.calls = 0
        self.worker_ids: set[str] = set()
        self.started_at: float | None = None
        self.finished_at: float | None = None

    # -- the transport -----------------------------------------------------

    def url(self, path: str) -> str:
        """Where this client's jobs go. Two runtimes, one job envelope."""
        return (
            endpoint_url(self.endpoint_id, path)
            if self.base_url is None
            else f"{self.base_url}/{path}"
        )

    def _run(self, payload: dict, timeout: float | None = None) -> dict:
        """One ``/runsync`` job, polled through ``/status`` if it outlives the call.

        ``retries`` defaults to 0 and 5b passes it: SPEC amendment 3.11 (2) gives
        the phase one attempt, and a client that quietly re-asked a row would turn
        a failed run into a slower one.
        """
        timeout = self.timeout if timeout is None else timeout
        if self.started_at is None:
            self.started_at = time.monotonic()
        job = _post(self.url("runsync"), self.api_key, payload, timeout)
        deadline = time.monotonic() + timeout
        while job.get("status") not in TERMINAL:
            if "id" not in job:
                raise ApiError(-1, f"no job id and no terminal status: {str(job)[:200]}")
            if time.monotonic() > deadline:
                raise ApiError(408, f"job {job['id']} still {job.get('status')} after the timeout")
            time.sleep(POLL_SECONDS)
            # RunPod's API answers `/status` on GET; the SDK's own server registers it POST-only.
            # A pod's `runsync` returns terminal, so this loop should never run there — and if it
            # ever does, it must fail on the job, not on a 405 that reads like a dead worker.
            status_payload = None if self.base_url is None else {}
            job = _post(self.url(f"status/{job['id']}"), self.api_key, status_payload, 60.0)
        self.calls += 1
        self.finished_at = time.monotonic()
        self.worker_seconds += float(job.get("executionTime") or 0) / 1000.0
        self.queue_seconds += float(job.get("delayTime") or 0) / 1000.0
        if job.get("workerId"):
            self.worker_ids.add(job["workerId"])
        if job["status"] != "COMPLETED":
            raise ApiError(-1, f"job {job.get('id')} ended {job['status']}: {str(job)[:300]}")
        return job.get("output") or {}

    def _run_with_retry(self, payload: dict, timeout: float | None = None) -> dict:
        attempt = 0
        while True:
            try:
                return self._run(payload, timeout)
            except ApiError as err:
                attempt += 1
                if attempt > self.retries or err.status not in RETRYABLE:
                    raise
                time.sleep(min(2**attempt, 30))

    # -- what the eval calls -----------------------------------------------

    def info(self) -> dict:
        """The worker's own account of what it loaded. Read before the first scored row."""
        return self._run_with_retry({"input": {"op": "info"}}, self.handshake_timeout)

    def batch(self, task: str, texts: list[str], posts: list[dict] | None = None) -> list[dict]:
        """Generate for a batch of rows; one reply dict per text, in order.

        Length-checked against ``posts`` the way the pod client is, and against the
        replies that come back: a worker that answered a different number of rows
        than it was asked has mispaired every label after the gap, and no gate
        number downstream could see it.
        """
        if posts is not None and len(posts) != len(texts):
            raise ValueError(f"{len(posts)} parent posts for {len(texts)} rows")
        output = self._run_with_retry(
            {"input": {"op": "batch", "task": task, "texts": texts, "posts": posts}}
        )
        replies = output.get("replies")
        if not isinstance(replies, list) or len(replies) != len(texts):
            raise ApiError(
                -1,
                f"the worker answered {len(replies) if isinstance(replies, list) else 'no'} rows"
                f" for {len(texts)} texts — the batch is mispaired, stop and report",
            )
        for reply in replies:
            usage = reply.get("usage") or {}
            self.usage["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
            self.usage["completion_tokens"] += int(usage.get("completion_tokens") or 0)
        return replies

    def timing(self) -> dict:
        """What the run cost, in the unit serverless actually bills in.

        ``worker_seconds`` is what RunPod reports per job and is NOT the billed
        quantity: a worker is up — and charged — between two sequential jobs as well
        as during them, and the idle-to-execution ratio of an 8-row smoke is nothing
        like that of a 758-row run. ``wall_seconds`` is the span the client held the
        endpoint, first request to last reply, and it is what the projection divides
        the measured dollars by. Both are reported, because their ratio is the thing
        a reader has to be able to see.
        """
        wall = (
            round(self.finished_at - self.started_at, 3)
            if self.started_at is not None and self.finished_at is not None
            else None
        )
        return {
            "calls": self.calls,
            "worker_seconds": round(self.worker_seconds, 3),
            "queue_seconds": round(self.queue_seconds, 3),
            "wall_seconds": wall,
            "seconds_per_call": round(self.worker_seconds / self.calls, 3) if self.calls else None,
            "wall_per_call": round(wall / self.calls, 3) if wall and self.calls else None,
            "idle_share": (
                round(1 - self.worker_seconds / wall, 4) if wall and self.worker_seconds else None
            ),
            "worker_ids": sorted(self.worker_ids),
        }


def assert_serving(observed: dict, expected: dict) -> dict:
    """Refuse unless the worker is serving the configuration this phase registered.

    ``expected`` names only the fields that decide the measurement — the adapter
    sha, the merge state, the quantization dict and the batch size. A field the
    worker does not report at all is a refusal too: an endpoint that cannot say
    what it loaded is not a configuration, it is a guess (the guard that
    `results/verdict_45h2.json`'s adapter sha exists for, one hop further out).
    """
    wrong = {
        field: (observed.get(field, "<absent>"), value)
        for field, value in expected.items()
        if observed.get(field, "<absent>") != value
    }
    if wrong:
        lines = "; ".join(
            f"{f}: worker says {got!r}, expected {want!r}" for f, (got, want) in wrong.items()
        )
        raise SystemExit(
            f"the endpoint is not serving the registered configuration — {lines}."
            " SPEC amendment 3.11 (2) scores the EXACT production configuration; stop and report."
        )
    return observed


RUNTIME_LIBRARIES = ("torch", "transformers", "bitsandbytes")
"""The three whose release moves a generated token, and therefore a gate number.

Not the GPU: which card the worker got is exactly the runtime delta 5b exists to
report, and pinning it would refuse the measurement instead of making it. A library
version, though, is not a runtime difference — it is a different instrument, and it
would land in the record silently beside numbers that look comparable.
"""


def assert_runtime_matches(observed: dict, anchor: dict) -> dict:
    """Refuse unless the worker's stack is the one the 4.5h2 arm was scored on.

    `assert_serving` checks what the worker loaded; this checks what it loads *with*.
    A fresh `pip install transformers` on a newly staged volume pulls whatever is
    current, and config A would stop being the 4.5h2 replica — the runtime delta
    confounded with a library delta, which is the precise thing serving this repo's
    own `local_llm` instead of vLLM was meant to avoid.
    """
    drift = {
        library: (observed.get(library, "<absent>"), anchor.get(library))
        for library in RUNTIME_LIBRARIES
        if anchor.get(library) and observed.get(library, "<absent>") != anchor[library]
    }
    if drift:
        lines = "; ".join(
            f"{lib}: worker {got!r}, 4.5h2 {want!r}" for lib, (got, want) in drift.items()
        )
        raise SystemExit(
            f"the worker's stack is not the one 4.5h2 measured — {lines}. Config A is the"
            " 4.5h2 replica by construction; a library that moved makes the parity number a"
            " comparison of two instruments. Pin the versions on the volume and re-stage."
        )
    return observed


def project_pair_usd(
    *,
    seconds_per_row: float,
    rows: int,
    runs: int,
    usd_per_second: float,
    cold_start_seconds: float,
    merge_usd: float = 0.0,
    spent_usd: float = 0.0,
) -> dict:
    """What the pre-registered pair would cost, from what the smoke measured.

    Committed before the smoke runs, so the abort rule of SPEC amendment 3.11 (2)
    — "if the smoke projects the pair over $4, stop before the paid run" — is
    arithmetic over two observations rather than a judgement made once the number
    is inconvenient. ``usd_per_second`` is the smoke's own dollars divided by the
    smoke's own billed seconds; ``merge_usd`` is config B's merge/requantize job,
    which the same $4 stop covers.

    ``spent_usd`` is what 5b has *already* cost when the projection is taken —
    staging, the cold-start proof, the smoke itself. The cap is on the phase and not
    on the pair, so a projection comparing only the pair against $4 would authorise a
    run the phase cannot afford. ``total_usd`` is the number the abort rule reads;
    ``projected_usd`` stays beside it because that is what the rule is worded in.

    Every input is reported back beside the total: a projection whose inputs are
    not in the record cannot be re-derived, and this one decides whether the
    phase's one paid event happens at all.
    """
    per_run = rows * seconds_per_row + cold_start_seconds
    scored_usd = per_run * runs * usd_per_second
    projected = scored_usd + merge_usd
    return {
        "inputs": {
            "seconds_per_row": seconds_per_row,
            "rows": rows,
            "runs": runs,
            "usd_per_second": usd_per_second,
            "cold_start_seconds": cold_start_seconds,
            "merge_usd": merge_usd,
            "spent_usd": spent_usd,
        },
        "seconds_per_run": round(per_run, 3),
        "scored_usd": round(scored_usd, 4),
        "merge_usd": round(merge_usd, 4),
        "projected_usd": round(projected, 4),
        "spent_usd": round(spent_usd, 4),
        "total_usd": round(projected + spent_usd, 4),
    }
