"""OpenRouter plumbing for the Phase 3b zero-shot baselines.

Everything here is either pure or a thin wrapper over ``urllib`` — no SDK, no new
runtime dependency, so `make check` stays runnable on a bare checkout. The parts
that decide a number (routing, the request body, the budget, the shape of a
result record) are pure functions with tests; the two functions that touch the
network do nothing else.

The rules this module exists to enforce, all from
`knowledge/decisions/3b-infra-and-precision.md`:

- one precision, pinned on **every** request, with fallbacks off. A silent
  reroute to a different quantization would swap the model under the number;
- the $8 cap for all of 3b is arithmetic, not discipline: the local counter can
  only ever be corrected *upwards* by what OpenRouter itself reports;
- a reference-only run can never be read as a gate anchor, and that is enforced
  where the record is built rather than left to whoever reads the file later.
"""

import json
import time
import urllib.error
import urllib.request

BASE_URL = "https://openrouter.ai/api/v1"

RETRYABLE = frozenset({-1, 408, 409, 429, 500, 502, 503, 504, 520, 522, 524})
"""HTTP statuses worth another attempt. ``-1`` is a reply we could not decode."""


class ApiError(RuntimeError):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status
        self.detail = detail


class BudgetExceeded(RuntimeError):
    """The cap tripped. The caller stops and reports; it never spends 'a little more'."""


def routing(tag: str, quantization: str | None) -> dict:
    """The ``provider`` block pinning one endpoint, with fallbacks off.

    ``quantization`` is omitted only where the provider reports none to pin —
    the Anthropic reference row, which anchors no gate. For the three candidates
    it is always the precision the pre-registered rule selected.
    """
    block = {"order": [tag], "allow_fallbacks": False}
    if quantization:
        block["quantizations"] = [quantization]
    return block


def request_body(
    *,
    model: str,
    messages: list[dict],
    tag: str,
    quantization: str | None,
    max_tokens: int,
    temperature: float = 0.0,
    seed: int | None = 42,
) -> dict:
    """One chat request. Identical in every field but ``model``/``messages``.

    ``reasoning: {"enabled": False}`` is not an optimisation: Qwen3.5 and Qwen3.6
    are hybrid-reasoning models, and left thinking they spend the whole
    ``max_tokens`` budget and return empty content — every row a parse failure,
    paid for at output-token prices. ``usage.include`` makes each response carry
    the cost OpenRouter charged for it, which is what the budget guard counts.
    """
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "reasoning": {"enabled": False},
        "provider": routing(tag, quantization),
        "usage": {"include": True},
    }
    if seed is not None:
        body["seed"] = seed
    return body


def _request(url: str, key: str, timeout: float, payload: dict | None) -> tuple[dict, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "market-pulse-llm phase-3b",
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            headers = dict(response.headers)
    except urllib.error.HTTPError as err:  # 4xx/5xx carry a body worth reporting
        raise ApiError(err.code, err.read().decode("utf-8", "replace")[:400]) from None
    try:
        payload = json.loads(raw)
    except ValueError:
        raise ApiError(-1, f"undecodable body: {raw[:200]}") from None
    # OpenRouter also reports upstream failures as 200 + {"error": ...}
    if isinstance(payload, dict) and "error" in payload and "choices" not in payload:
        error = payload["error"]
        detail = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        code = error.get("code") if isinstance(error, dict) else None
        raise ApiError(code if isinstance(code, int) else -1, detail[:400])
    return payload, headers


def post(path: str, payload: dict, key: str, timeout: float = 180.0, base_url: str = BASE_URL):
    return _request(f"{base_url}{path}", key, timeout, payload)


def get(path: str, key: str, timeout: float = 60.0, base_url: str = BASE_URL) -> dict:
    return _request(f"{base_url}{path}", key, timeout, None)[0]


def call_with_retry(caller, attempts: int = 4, sleeper=time.sleep, base_delay: float = 1.5):
    """Retry a call on transient failures with exponential backoff.

    Fallbacks are off by operator decision, so a pinned endpoint having a bad
    minute is our problem to wait out rather than route around. What cannot be
    waited out becomes an ``api_failure``: a counted, reported, excluded row —
    never a guessed label.
    """
    for attempt in range(1, attempts + 1):
        try:
            return caller()
        except ApiError as err:
            if err.status not in RETRYABLE or attempt == attempts:
                raise
        except OSError:  # URLError, timeouts, connections reset mid-stream
            if attempt == attempts:
                raise
        sleeper(base_delay * 2 ** (attempt - 1))
    raise AssertionError("unreachable")


def total_usage(key: str, base_url: str = BASE_URL) -> float:
    """Lifetime spend on the key, as OpenRouter accounts for it."""
    return float(get("/credits", key, base_url=base_url)["data"]["total_usage"])


class Budget:
    """The $8 cap for all of 3b plus a per-run cap, enforced on every row.

    Two counters, and the pessimistic one wins. ``add`` accumulates the cost each
    response reports, which is immediate but local; :meth:`reconcile` takes the
    provider's own lifetime usage and can only ever push the number *up*. That
    ordering matters: a row whose response was lost still cost money, and a
    budget guard that trusted the local sum would under-count exactly the rows it
    failed to record.
    """

    def __init__(self, total_cap: float, run_cap: float, spent_before: float = 0.0) -> None:
        self.total_cap = total_cap
        self.run_cap = run_cap
        self.spent_before = spent_before
        self.run_spend = 0.0

    @property
    def phase_spend(self) -> float:
        return self.spent_before + self.run_spend

    def add(self, cost: float) -> None:
        self.run_spend += max(cost, 0.0)
        self._enforce()

    def reconcile(self, phase_spend: float) -> None:
        """Adopt the provider's number for this phase when it is the larger one."""
        self.run_spend = max(self.run_spend, phase_spend - self.spent_before)
        self._enforce()

    def headroom(self) -> float:
        return min(self.run_cap - self.run_spend, self.total_cap - self.phase_spend)

    def _enforce(self) -> None:
        if self.run_spend > self.run_cap:
            raise BudgetExceeded(
                f"per-run cap ${self.run_cap:.2f} tripped at ${self.run_spend:.4f}"
            )
        if self.phase_spend > self.total_cap:
            raise BudgetExceeded(f"3b cap ${self.total_cap:.2f} tripped at ${self.phase_spend:.4f}")


def estimate_cost(
    *, rows: list[str], prompt_chars: int, pricing: dict, completion_tokens: int
) -> dict:
    """Rough cost of a run, printed before anything is spent.

    Deliberately crude: a character heuristic (Latin instructions ~4 chars per
    token, Cyrillic bodies ~2.5) with no tokenizer downloaded. It exists so the
    operator sees an order of magnitude before the first request, and the live
    probe replaces it with measured usage before the full run.
    """
    prompt_tokens = len(rows) * (prompt_chars / 4 + 8) + sum(len(text) for text in rows) / 2.5
    completion = len(rows) * completion_tokens
    return {
        "requests": len(rows),
        "prompt_tokens": round(prompt_tokens),
        "completion_tokens": completion,
        "usd": prompt_tokens * float(pricing["prompt"]) + completion * float(pricing["completion"]),
    }


def build_record(
    *,
    model: str,
    timestamp: str,
    git: dict,
    config: dict,
    gates: list[dict],
    diagnostics: dict,
    reference_only: bool,
) -> dict:
    """Assemble the results record, enforcing the one rule a reader must not have to.

    A reference row never anchors a gate ([[frontier-api-reference-baseline]]), and
    the cheapest way to guarantee that is to make the record unable to claim one:
    every entry's ``gate`` field becomes ``"ref"`` here, so a lookup for ``G1d``
    cannot find it however carelessly it is written. The metric names survive, so
    the row still reads next to the others.
    """
    if reference_only:
        gates = [{**entry, "gate": "ref", "reference_metric": entry["gate"]} for entry in gates]
        diagnostics = {
            **diagnostics,
            "note": "REFERENCE ONLY — never anchors a gate. " + diagnostics.get("note", ""),
        }
    return {
        "model": model,
        "timestamp": timestamp,
        "reference_only": reference_only,
        "git": git,
        "config": config,
        "gates": gates,
        "diagnostics": diagnostics,
    }
