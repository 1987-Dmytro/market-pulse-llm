#!/usr/bin/env python3
"""$0 integration preflight: the serving guards, against the REAL libraries. Run before paying.

`make check` deliberately imports no torch and no transformers (`pyproject.toml`, the `gpu`
extra), which keeps the suite fast and installable — and pushed the first meeting between this
repo's guards and their real dependencies into a **paid** session. vis-b is what that cost:
`serve_handler.assert_no_adapter` read `getattr(model, "active_adapters")` for truthiness, every
`PreTrainedModel` carries that name as a bound method through `PeftAdapterMixin`, and the guard
refused the NF4 base it exists to admit — on the endpoint, after the weights had loaded.

This is the middle rung that was missing. It builds a **real** model of the real class from a
tiny config (no download, no weights, CPU, seconds) and drives every guard the worker runs in
BOTH directions. A stub is not a valid subject here: a stub is built from the same assumption as
the guard, so it cannot contradict it.

sku-b-prep adds the POSITIONS half (SPEC 3.17 (9)) below it: the config's two `settings` refusals,
the adapter guard reached through the second base-only config, the whole config x op matrix, the
driver's payload guard at its numeric boundary, and the parser on a truncated tail — each with the
control that says the guard is discriminating rather than merely refusing. Those checks are pure
and would run with no GPU stack at all; they live here because this is the list that runs before a
paid session, not because they need one.

sku-b-v3-prep adds the RESUME half (SPEC 3.17 (11)) below that, on the same terms and for a sharper
reason: 17 of the 138 elements have already been paid for once, under a clause that gives them no
second draw. The registration, the selection, the warm-up inputs and the merged output are each
driven both ways before the second session opens.

sku-b-v4-prep re-drives that half against the v4 registration and adds the two subjects (12) made
possible: the pinned (10)(a) refusal record, which is the evidence the v4 population is still 121,
and the three constants of (12)(b) — a v4 run reading `results/spend_sku_b_v3.json` is the Dv167
trap and must refuse before it reads a balance.

    scripts/preflight_serving_guards.py

Needs `transformers` and `peft` — the versions the volume's venv carries, which the run prints
so a mismatch is visible rather than assumed. It exits 1 and says so if they are missing: an
unrunnable preflight is a finding, not a pass.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

VOLUME_STACK = "transformers 5.14.1 · peft 0.20.0"
"""What `/runpod-volume/venv` reports (srv-2c's boot log, re-read at vis-b staging). Printed
beside the local versions: this preflight is only as good as the libraries it exercises."""


def tiny_gemma4():
    """A real `Gemma4ForConditionalGeneration`, small enough to build on a laptop.

    The class matters — `local_llm.load_captioner` loads this one — but the size does not: the
    guards read what peft writes onto the model, not what the model computes.
    """
    from transformers import Gemma4Config, Gemma4ForConditionalGeneration

    config = Gemma4Config(
        text_config={
            "hidden_size": 32,
            "intermediate_size": 64,
            "num_hidden_layers": 2,
            "num_attention_heads": 2,
            "num_key_value_heads": 1,
            "head_dim": 16,
            "vocab_size": 512,
        },
        vision_config={
            "hidden_size": 32,
            "intermediate_size": 64,
            "num_hidden_layers": 2,
            "num_attention_heads": 2,
            "image_size": 32,
            "patch_size": 16,
        },
    )
    return Gemma4ForConditionalGeneration(config)


def vis_a_guard(model):
    """`assert_no_adapter` exactly as vis-a shipped it — the positive control.

    A preflight that only shows the current guard passing cannot tell a fixed guard from a guard
    that never looked. This one must REFUSE the bare model, and if it ever stops doing so the
    subject has drifted and the check above it means nothing.
    """
    marks = [name for name in ("peft_config", "active_adapters") if getattr(model, name, None)]
    if marks or type(model).__name__.startswith("Peft"):
        raise ValueError(
            f"the caption model carries an adapter ({type(model).__name__},"
            f" {', '.join(marks) or 'by class'})."
        )
    return model


def verdict(guard, model) -> tuple[bool, str]:
    try:
        guard(model)
        return True, "ACCEPT"
    except ValueError as err:
        return False, f"REFUSE — {err}"


def refuses(call, *args, **kwargs) -> tuple[bool, str]:
    """(did it refuse, what it said). SystemExit and ValueError are both refusals here — the
    worker's guards raise ValueError so a job can name the reason, and the driver's raise
    SystemExit so a run stops."""
    try:
        call(*args, **kwargs)
    except (ValueError, SystemExit) as err:
        return True, f"REFUSE — {str(err).splitlines()[0][:120]}"
    return False, "ACCEPT"


def positions_guards(handler, adapted_model) -> dict:
    """The POSITIONS half (SPEC 3.17 (9)), driven BOTH WAYS before a cent is spent.

    ``adapted_model`` is the tiny real model the section above has just attached a LoRA to — the
    same subject, so the adapter refusal is exercised through the POSITIONS config rather than
    assumed to be shared. The rest of this section is pure and would pass with no libraries
    installed at all; it lives here because this is the list that runs before the paid session,
    not because it needs a GPU stack.
    """
    import positions_gm4_skub as driver
    from market_pulse import positions, prompts, serving

    print("\n--- SPEC 3.17 (9): the POSITIONS configuration ---")
    checks: dict[str, bool] = {}

    clean = {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": "842da3794eaa"}
    config = handler.settings(clean)
    print(
        f"\n4. settings(POSITIONS)        {config['serving_config']} · adapter {config['adapter_dir']}"
    )
    checks["POSITIONS serves the base with no adapter directory"] = config["adapter_dir"] is None

    for variable in handler.ADAPTER_ENV:
        refused, how = refuses(handler.settings, clean | {variable: "/vol/adapter"})
        print(f"   {variable:<12} set            {how}")
        checks[f"POSITIONS refuses {variable}"] = refused
    refused, how = refuses(handler.settings, {"SERVING_CONFIG": "POSITIONS"})
    print(f"   MODEL_REVISION unset          {how}")
    checks["POSITIONS refuses an unpinned base"] = refused

    refused, how = refuses(handler.assert_no_adapter, adapted_model)
    print(f"\n5. the adapted real model     assert_no_adapter  {how}")
    checks["the adapter refusal reaches the POSITIONS config too"] = refused

    print("\n6. the config x op matrix (only the CONFIG_OPS cells may be answered)")
    jobs = {
        "batch": {"op": "batch", "task": "T1", "texts": ["a"]},
        "caption": {"op": "caption", "task": prompts.CAPTION_TASK_GM4, "images": [["data:x"]]},
        "positions": {
            "op": "positions",
            "task": prompts.POSITIONS_TASK_TEXT,
            "items": ["Рудь пломбір 450 г"],
        },
    }

    class Client:
        """Answers anything. If a cell that must refuse reaches it, the run is already wrong."""

        def batch(self, task, texts, posts=None):
            return [{"content": "row"} for _ in texts]

        def caption(self, task, albums):
            return [{"content": "prose"} for _ in albums]

        def positions(self, task, items):
            return [{"content": "[]"} for _ in items]

    matrix_ok = True
    for served in serving.CONFIGS:
        info = {"serving_config": served}
        line = []
        for op, job in jobs.items():
            allowed = op in serving.CONFIG_OPS[served]
            refused, _ = refuses(handler.handle, {"input": job}, Client(), info)
            matrix_ok = matrix_ok and (refused != allowed)
            mark = "ok" if refused != allowed else "WRONG"
            line.append(f"{op}={'answer' if not refused else 'refuse'}({mark})")
        print(f"   {served:<10} {'  '.join(line)}")
    checks["every config x op cell behaves as CONFIG_OPS says"] = matrix_ok

    budget = driver.MAX_PAYLOAD_MB
    edge = int(budget * 1_000_000)
    under, _ = refuses(driver.jobs, [{"file": "under.jpg", "bytes": edge}], budget)
    over, why = refuses(driver.jobs, [{"file": "over.jpg", "bytes": edge + 1}], budget)
    print(f"\n7. payload guard at {budget} MB")
    print(f"   {edge:>10} bytes            {'REFUSE' if under else 'ACCEPT'}")
    print(f"   {edge + 1:>10} bytes            {why}")
    checks["a job exactly at the payload budget passes"] = not under
    checks["a job one byte over it refuses rather than shortening the album"] = over

    truncated = '[{"brand": "Рудь", "category": "ice-cream", '
    refused, why = refuses(
        positions.parse_positions,
        truncated,
        categories=frozenset({"ice-cream"}),
        carrier="leaflet_page",
        price_origin="retail_leaflet",
        extraction_source="preflight",
        aliases={},
    )
    print(f"\n8. a reply truncated mid-JSON {why}")
    checks["a truncated tail is a parse REFUSAL, never an empty answer"] = refused

    empty, _ = refuses(
        positions.parse_positions,
        "[]",
        categories=frozenset({"ice-cream"}),
        carrier="leaflet_page",
        price_origin="retail_leaflet",
        extraction_source="preflight",
        aliases={},
    )
    print(f"   an empty array               {'REFUSE' if empty else 'ACCEPT'}   <- the control")
    checks["the control: an empty array is an ANSWER and is accepted"] = not empty
    checks |= parser_v2_guards(positions)
    return checks


def parse_one(positions, entry: dict):
    """One entry through the real parser, as the leaflet leg calls it. Returns (position, why)."""
    reply = json.dumps([{"brand": "Рудь", "category": "ice-cream", **entry}], ensure_ascii=False)
    try:
        return (
            positions.parse_positions(
                reply,
                categories=frozenset({"ice-cream"}),
                carrier="leaflet_page",
                price_origin="retail_leaflet",
                extraction_source="preflight",
                aliases={},
            )[0],
            "ACCEPT",
        )
    except ValueError as err:
        return None, f"REFUSE — {err}"


def parser_v2_guards(positions) -> dict:
    """SPEC 3.17 (13)(a): the three strings that used to cost a whole page, and what still refuses.

    Each of the three is the ACTUAL string a v4 page was refused on — read out of
    `results/sku_miss_decomposition.json`'s refusal reasons, not invented here — so this section is
    the before/after of the amendment on its own evidence. Every one is paired with a control:
    accepting them must not have widened the parser into salvage, and the truncated tail above must
    still be a refusal, because the token ceiling and the parser family are the two SEPARATE halves
    of (13)(a) and a parser that repaired truncation would hide whether the ceiling did anything.
    """
    print("\n--- SPEC 3.17 (13)(a): the parser family, warnings instead of page refusals ---")
    checks: dict[str, bool] = {}
    accepted = {
        # (entry, the warning it must carry, the field that must read this value)
        "-50%* (atb_market_official 4340 p3, 4467 p1)": (
            {"price_promo": 90.0, "price_old": 180.0, "discount_pct_printed": "-50%*"},
            "discount_footnote",
            ("discount_pct_printed", 50.0),
        ),
        "6х100 г (atb_market_official 4446 p1)": (
            {"size": "6х100 г"},
            "multipack",
            ("pack_count", 6),
        ),
        "від 39,90 (the one-sided range)": (
            {"price_promo": "від 39,90"},
            "price_from",
            ("price_qualifier", "from"),
        ),
    }
    for label, (entry, warning, (field, value)) in accepted.items():
        row, why = parse_one(positions, entry)
        ok = row is not None and warning in row.warnings() and getattr(row, field) == value
        got = "—" if row is None else f"{', '.join(row.warnings())} · {field}={getattr(row, field)}"
        print(f"   {label:<46} {why:<10} {got}")
        checks[f"(13)(a) ACCEPTS {label.split(' (')[0]} and records `{warning}`"] = ok

    # the unit size is kept and NEVER multiplied into a total: «6х100 г» is not «600 г»
    row, _ = parse_one(positions, {"size": "6х100 г"})
    kept = row is not None and (row.size_value, row.size_unit) == (100.0, "г")
    print(
        f"   the multipack's size is the UNIT size          {row and row.size_value} г  (not 600)"
    )
    checks["a pack count is read and the unit size is never multiplied into a total"] = kept

    still = {
        "2х0,5 л х 3 — not one count and one unit size": {"size": "2х0,5 л х 3"},
        "1х100 г — a pack starts at two": {"size": "1х100 г"},
        "80-90 — a written-out range is two prices": {"price_promo": "80-90"},
        "-50%*** — three asterisks is not a footnote": {"discount_pct_printed": "-50%***"},
        "39,90 від Рудь — «від» is not leading": {"price_promo": "39,90 від Рудь"},
    }
    print("   still refused, so the widening is not salvage:")
    for label, entry in still.items():
        row, why = parse_one(positions, entry)
        print(f"     {label:<46} {'REFUSE' if row is None else 'ACCEPT'}")
        checks[f"(13)(a) still REFUSES {label.split(' — ')[0]}"] = row is None

    clean, _ = parse_one(positions, {"size": "450 г", "discount_pct_printed": "-51%"})
    print(f"   the control: an unremarkable position          warnings {clean.warnings()}")
    checks["the control: a position with nothing to warn about carries no warnings"] = (
        clean.warnings() == ()
    )
    return checks


def resume_guards() -> dict:
    """The resume of SPEC 3.17 (11)/(12), driven BOTH WAYS before a cent of the session is spent.

    The first session bought 17 of 138 elements for $0.1965 under a one-attempt clause, and the v3
    session was refused at the (10)(a) gate for $0.1526 without buying any of the rest. Every guard
    below stands between the v4 session and either paying for one of those 17 again or paying for
    the refused session's overhead a second time — and every one of them is driven with its CONTROL,
    because a refusal proves something is blocked and never that the blocked set is the one that was
    meant.

    Five subjects, in the order a run meets them: the registration (are the pins still the bytes
    they name, including the refusal record's), the constants of (12)(b) (do the cap, the ledger and
    the phase name ONE session), the selection (is what is about to travel unbought), the warm-up
    inputs (are they real and still non-gold), and the merged output (does any source carry two
    answers). Pure checks, no GPU stack needed — they live here because this is the list that runs
    before the paid session, not because they need one.
    """
    import hashlib
    import json

    import positions_gm4_skub as driver

    print("\n--- SPEC 3.17 (11)/(12): the resume ---")
    checks: dict[str, bool] = {}
    prereg = json.loads(driver.PREREG_RESUME.read_text(encoding="utf-8"))
    # `driver.PIN_RESUME` and not `driver.PIN`: SPEC 3.17 (13)(a) moved the live pin to serving v2
    # at the 1200 ceiling, and (11)(b) freezes the RESUMED session's instrument at v1's. Reading
    # the live one here would make every check below fail on the pin before reaching its subject.
    pin_sha = hashlib.sha256(driver.PIN_RESUME.read_bytes()).hexdigest()

    def moved(mutate) -> dict:
        """The registration with one thing moved. The mutation gets the WHOLE record: (12) put a
        pin outside the `resume` block for the first time — the refusal record lives in
        `supersedes` — and a helper that could only reach `resume` would leave it undriven."""
        body = json.loads(json.dumps(prereg))
        mutate(body)
        return body

    plan = driver.resume_plan(prereg, pin_sha, REPO_ROOT)
    already = prereg["resume"]["bought_already"]
    print(
        f"\n9. the registration          {len(plan['to_buy'])} to buy,"
        f" {len(plan['already_asked'])} already bought   <- the control: it ACCEPTS"
    )
    checks["the honest registration is accepted and names 121 elements to buy"] = (
        len(plan["to_buy"]) == already["n_unbought"] == 121
        and len(plan["already_asked"]) == already["n_asked"] == 17
    )

    for label, mutate in (
        (
            "a moved dump pin",
            lambda b: b["resume"]["bought_already"]["dump"].update(sha256="0" * 64),
        ),
        (
            "a moved serving pin",
            lambda b: b["resume"]["bought_already"]["serving_pin"].update(sha256="0" * 64),
        ),
        (
            "an unbought id with an answer",
            lambda b: b["resume"]["bought_already"].update(
                unbought=[
                    b["resume"]["bought_already"]["asked"][0],
                    *b["resume"]["bought_already"]["unbought"],
                ]
            ),
        ),
        # new in v4: the refusal record is what says the v3 session bought nothing, and the whole
        # population this run buys is inherited from it rather than re-derived
        (
            "a moved (10)(a) refusal-record pin",
            lambda b: b["supersedes"]["refused_record"].update(sha256="0" * 64),
        ),
    ):
        refused, how = refuses(driver.resume_plan, moved(mutate), pin_sha, REPO_ROOT)
        print(f"   {label:<34} {how}")
        checks[f"the resume refuses {label}"] = refused

    print("\n9b. the (12)(b) constants    cap, ledger and phase against the registration")
    registered = prereg["attempts"]
    v3_ledger = REPO_ROOT / "results" / "spend_sku_b_v3.json"
    blocked, how = refuses(
        driver.check_the_constants_are_the_registrations,
        prereg,
        driver.RESUME_PHASE,
        driver.RESUME_CAP_USD,
        driver.RESUME_LEDGER,
    )
    print(
        f"    the registered set         {how}   <- the control"
        f" (${registered['cap_usd']:.2f} · {registered['phase']} · {registered['ledger']})"
    )
    checks["the control: the registered cap/ledger/phase are accepted together"] = not blocked
    for label, args in (
        ("the OLD ledger name", (driver.RESUME_PHASE, driver.RESUME_CAP_USD, v3_ledger)),
        ("the OLD cap", (driver.RESUME_PHASE, 0.45, driver.RESUME_LEDGER)),
        ("the OLD phase key", ("sku-b-v3", driver.RESUME_CAP_USD, driver.RESUME_LEDGER)),
    ):
        refused, how = refuses(driver.check_the_constants_are_the_registrations, prereg, *args)
        print(f"    {label:<26} {how}")
        checks[f"the run refuses {label}"] = refused
    # which guard fires matters: `read_ledger` also stops a v3 anchor, by its MISSING KEY and only
    # after a balance has been read. Driven here so the two messages are visibly different rather
    # than assumed to be, and so a reader can see the constants check is not standing in for it.
    also, how = refuses(
        driver.read_ledger, v3_ledger, 10.0, driver.RESUME_PHASE, driver.RESUME_CAP_USD
    )
    print(f"    read_ledger, for contrast  {how}")
    checks["read_ledger refuses the v3 anchor too, and for its own reason"] = also

    # 9c — the LIVE session, and the reason it is a separate block rather than a second argument
    # above: `check_the_constants_are_the_registrations` was called inside `if args.resume:`, so
    # nothing had ever driven it on the path skub2 takes. B′ has no resume block, so it is the only
    # path skub2 CAN take. Same three constants, its own registration, its own old sets to refuse.
    print("\n9c. the live session         skub2 against results/sku_pilot_prereg_b2.json")
    live = json.loads(driver.PREREG.read_text(encoding="utf-8"))
    signed = live["attempts"]
    blocked, how = refuses(
        driver.check_the_constants_are_the_registrations,
        live,
        driver.PHASE,
        driver.CAP_USD,
        driver.LEDGER,
    )
    print(
        f"    the registered set         {how}   <- the control"
        f" (${signed['cap_usd']:.2f} · {signed['phase']} · {signed['ledger']})"
    )
    checks["the control: skub2's registered cap/ledger/phase are accepted together"] = not blocked
    for label, args in (
        (
            "the FIRST session's ledger",
            (driver.PHASE, driver.CAP_USD, REPO_ROOT / "results" / "spend_sku_b.json"),
        ),
        ("(13)(d)'s superseded cap", (driver.PHASE, 0.40, driver.LEDGER)),
        ("the FIRST session's phase", ("sku-b", driver.CAP_USD, driver.LEDGER)),
    ):
        refused, how = refuses(driver.check_the_constants_are_the_registrations, live, *args)
        print(f"    {label:<26} {how}")
        checks[f"the live run refuses {label}"] = refused

    print("\n9d. the registered instrument the serving pin B′ names, by name and by sha")
    blocked, how = refuses(driver.check_the_serving_pin_is_the_registered_one, live, driver.PIN)
    print(f"    serving pin v2             {how}   <- the control")
    checks["the control: the registered serving pin is accepted"] = not blocked
    refused, how = refuses(
        driver.check_the_serving_pin_is_the_registered_one, live, driver.PIN_RESUME
    )
    print(f"    v1's pin (800 ceiling)     {how}")
    checks["the live run refuses v1's serving pin, before the boot is billed"] = refused
    blocked, how = refuses(driver.check_the_serving_pin_is_the_registered_one, prereg, driver.PIN)
    print(f"    v4, which names no pin     {how}   <- skipped, not failed")
    checks["a registration that names no serving pin is skipped rather than failed"] = not blocked

    bought, fresh = already["asked"][0], already["unbought"][0]
    asked = set(already["asked"])
    refused, how = refuses(
        driver.resume_population,
        [{"file": bought, "bytes": 1}],
        {"to_buy": {bought}, "already_asked": asked},
        "page",
    )
    kept = driver.resume_population(
        [{"file": fresh, "bytes": 1}], {"to_buy": {fresh}, "already_asked": asked}, "page"
    )
    print(f"\n10. the selection            a bought id     {how}")
    print(f"    an unbought id           {len(kept)} kept   <- the control")
    checks["a bought id that reaches the selection is refused"] = refused
    checks["the control: an unbought id passes the same selection"] = len(kept) == 1

    reference = json.loads(driver.REFERENCE.read_text(encoding="utf-8"))
    manifest = json.loads(driver.MANIFEST.read_text(encoding="utf-8"))
    honest = driver.resume_warmup_inputs(prereg["resume"], reference, manifest, REPO_ROOT)
    print(
        f"\n11. the (11)(c) warm-up      {honest['page']['file'].rsplit('/', 1)[-1]}"
        f" {honest['page']['bytes'] / 1e6:.2f} MB · row {honest['row']['id']}"
        f" ({len(honest['text'])} chars)   <- the control: ACCEPT"
    )
    checks["the registered warm-up inputs are real, full-size and accepted"] = (
        honest["page"]["bytes"] > 100_000 and len(honest["text"]) > 50
    )
    for label, mutate in (
        (
            "a page inside the sent 108",
            lambda b: b["resume"]["warmup"]["page"].update(
                file=reference["posts"][0]["pages_sent"][0]["file"]
            ),
        ),
        (
            "a row inside the 30",
            lambda b: b["resume"]["warmup"]["text"].update(id=manifest["ids"][0]),
        ),
    ):
        refused, how = refuses(
            driver.resume_warmup_inputs, moved(mutate)["resume"], reference, manifest, REPO_ROOT
        )
        print(f"    {label:<24} {how}")
        checks[f"the warm-up refuses {label}"] = refused

    run_record = REPO_ROOT / already["run_record"]["path"]
    merge_plan = {
        "run": json.loads(run_record.read_text(encoding="utf-8")),
        "run_record": run_record,
        "run_dump": REPO_ROOT / already["dump"]["path"],
    }

    def outcome(source):
        return [{"source": source, "unreadable": None, "n_positions": 1}]

    merged = driver.merge_sessions(merge_plan, outcome(fresh), [])
    refused, how = refuses(driver.merge_sessions, merge_plan, outcome(bought), [])
    print(f"\n12. the merged bar input     a source bought twice  {how}")
    print(f"    an unbought source       {len(merged['outcomes'])} outcomes   <- the control")
    checks["a source answered by both sessions is refused in the merge"] = refused
    checks["the control: the merged record carries 17 + what this session bought"] = (
        len(merged["outcomes"]) == already["n_asked"] + 1
    )
    return checks


def real_processor():
    """A processor stand-in whose template IS Gemma 4's, read from the pinned revision on disk.

    `AutoProcessor` cannot be built on this machine — the vision half needs a module the CPU stack
    does not ship — but the only thing `ReaderClient` asks a processor for at render time is
    `apply_chat_template`, and that lives on the tokenizer. So the subject here is the REAL
    template at the REAL revision, which is the thing a stub cannot honestly stand in for: whether
    the request starts with <bos> and whether `enable_thinking: false` really closes the thought
    channel are facts about that file and nothing else.
    """
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        "google/gemma-4-31b-it",
        revision="842da3794eaa0b77d5f08bae87a17459d91ff475",
        local_files_only=True,
    )
    return SimpleNamespace(
        tokenizer=tokenizer,
        apply_chat_template=tokenizer.apply_chat_template,
    )


def reader_guards(handler) -> dict:
    """The READER config's guards, each with the control that says it discriminates.

    The reader is one paid attempt under a cap the registration fixes, so every one of these has to
    be false before the endpoint exists rather than after: a refusal met on the endpoint is a
    refusal that was billed for the boot that reached it.

    Since probe-b the config serves TWO registered texts, so the checks that could hide a version —
    the real chat template and the request's shape — are run over `prompts.READER` rather than over
    the one this session reads with.
    """
    from market_pulse import local_llm, prompts

    checks: dict[str, bool] = {}
    revision = "842da3794eaa0b77d5f08bae87a17459d91ff475"
    config = handler.settings({"SERVING_CONFIG": "READER", "MODEL_REVISION": revision})
    print(
        f"\n13. the READER config         {config['serving_config']} ·"
        f" adapter {config['adapter_dir']} · revision {config['revision'][:12]}…"
    )
    checks["READER is the base at the pinned revision with no adapter"] = (
        config["adapter_dir"] is None
        and config["weights_dir"] == local_llm.MODEL_ID
        and config["revision"] == revision
    )
    refusals = []
    for variable in handler.ADAPTER_ENV:
        refused, _ = refuses(
            handler.settings,
            {"SERVING_CONFIG": "READER", "MODEL_REVISION": revision, variable: "/adapter"},
        )
        refusals.append(refused)
    unpinned, how = refuses(handler.settings, {"SERVING_CONFIG": "READER"})
    print(
        f"    every {'/'.join(handler.ADAPTER_ENV)} refused: {all(refusals)}"
        f" · an unpinned base {how}"
    )
    checks["READER inherits the adapter refusal for every variable"] = all(refusals)
    checks["READER refuses an unpinned base"] = unpinned

    processor = real_processor()
    client = local_llm.ReaderClient(processor, None)
    thread = {"channel": "@c", "post_id": 1, "post": "пост", "comments": [[2, "коментар"]]}
    bos = processor.tokenizer.bos_token
    rendered = {task: client.render(task, thread) for task in sorted(prompts.READER)}
    closed = {
        task: text.rstrip().endswith("<|channel>thought\n<channel|>")
        for task, text in rendered.items()
    }
    print(f"\n14. the REAL chat template    both registered texts, <bos> {bos}")
    for task, text in rendered.items():
        print(f"    {task:22s} <bos>: {text.startswith(bos)} · thought closed: {closed[task]}")
    checks["every reader request renders through the real template and keeps <bos>"] = all(
        text.startswith(bos) for text in rendered.values()
    )
    checks["enable_thinking:false closes the thought channel on every reader request"] = all(
        closed.values()
    )
    # the two texts are different instruments and the worker must not be able to blur them
    checks["the two registered reader texts render differently"] = len(set(rendered.values())) == 2
    wrong, how = refuses(client.render, prompts.POSITIONS_TASK_TEXT, thread)
    print(f"    another registered task                        {how}")
    checks["the reader client refuses a task it does not serve"] = wrong

    served = handler.describe(config, {}, None, {})["reader_prompt_sha256"]
    live = {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)}
    print(
        f"    info answers a sha per task    {sorted(served)} · equals this checkout: {served == live}"
    )
    checks["info names a sha for EVERY registered reader text"] = served == live

    big = {**thread, "comments": [[index, "х" * 400] for index in range(200)]}
    refused, how = refuses(client.render, prompts.READER_TASK_V2, big)
    print(f"\n15. the input ceiling         a {len(big['comments'])}-comment thread {how}")
    checks["a thread over the registered input ceiling is refused loudly"] = refused
    checks["the control: a thread inside it renders"] = bool(rendered)

    def verdict(**moves) -> str:
        return json.dumps(
            {
                "thread": {"channel": "@c", "post_id": 1},
                "post_summary": "п",
                "discussion_summary": "д",
                "entities": [],
                "signals": [],
                "per_comment": [],
                "noise": [],
                **moves,
            },
            ensure_ascii=False,
        )

    verdict_json = verdict()
    whole = prompts.parse_reply(prompts.READER_TASK_V2, verdict_json)
    cut, how = refuses(
        prompts.parse_reply, prompts.READER_TASK_V2, verdict_json[: len(verdict_json) // 2]
    )
    print(f"\n16. a verdict cut at the ceiling                   {how}")
    print(f"    the control: a whole verdict   {len(whole)} keys parsed")
    checks["a truncated verdict is a parse failure and not an empty answer"] = cut
    checks["the control: a whole verdict parses"] = whole["thread"]["post_id"] == 1

    # 17 — the two defects probe-b's D1 closes, on the parser that will read the paid replies
    signal = {
        "signal_type": "похвала",
        "subject_type": "категория",
        "subject_id": "сир",
        "aspect": "taste",
        "stance": "positive",
        "reading": "смачно",
        "quote": "смачно",
    }
    from_post = prompts.parse_reply(
        prompts.READER_TASK_V2, verdict(signals=[{**signal, "evidence": [], "from_post": True}])
    )
    nulls, how_null = refuses(
        prompts.parse_reply,
        prompts.READER_TASK_V2,
        verdict(signals=[{**signal, "evidence": [None], "from_post": True}]),
    )
    unflagged, how_unflagged = refuses(
        prompts.parse_reply, prompts.READER_TASK_V2, verdict(signals=[{**signal, "evidence": []}])
    )
    print(f"\n17. Dv394 a post signal       from_post + [] parses: {bool(from_post['signals'])}")
    print(f"    evidence [null]            {how_null}")
    print(f"    an empty evidence unflagged {how_unflagged}")
    checks["a signal read in the post parses with from_post and an empty evidence"] = (
        from_post["signals"][0]["from_post"] is True and from_post["signals"][0]["evidence"] == []
    )
    checks["evidence [null] is still refused — the defect probe-a measured"] = nulls
    checks["an empty evidence without from_post is refused"] = unflagged
    v2_text = prompts.PROMPTS[prompts.READER_TASK_V2]
    print(f"    Dv393 the entities line    LIST + brackets: {'a LIST of objects' in v2_text}")
    checks["the v2 text states the array shape the parser requires"] = (
        '"entities" — a LIST of objects' in v2_text and "[{" in v2_text
    )
    return checks


def main(argv: list[str] | None = None) -> int:
    try:
        import peft
        import torch
        import transformers
    except ImportError as err:
        print(
            f"cannot run: {err}. This preflight exercises the REAL libraries and there is no"
            f" honest way to fake them — a stub agrees with whatever the guard assumes. Install"
            f" the volume's stack ({VOLUME_STACK}) into a venv with --system-site-packages, or"
            " report that the check could not be run. Do NOT treat this as a pass.",
            file=sys.stderr,
        )
        return 1

    import serve_handler as handler
    from transformers.integrations.peft import PeftAdapterMixin

    print(
        f"local   transformers {transformers.__version__} · peft {peft.__version__}"
        f" · torch {torch.__version__}\nvolume  {VOLUME_STACK}"
    )

    model = tiny_gemma4()
    attr = getattr(model, "active_adapters")
    print(
        f"\nsubject {type(model).__name__} from config,"
        f" {sum(p.numel() for p in model.parameters()):,} params"
        f"\n  isinstance(model, PeftAdapterMixin)  {isinstance(model, PeftAdapterMixin)}"
        f"\n  getattr(model, 'active_adapters')    {type(attr).__name__} {attr.__qualname__},"
        f" bool() = {bool(attr)}   <- an API, not an answer"
        f"\n  getattr(model, 'peft_config', None)  {getattr(model, 'peft_config', None)!r}"
    )

    accepted, how = verdict(handler.assert_no_adapter, model)
    print(f"\n1. bare real model            assert_no_adapter  {how}")
    # `verdict` returns True for ACCEPT, so the control's pass condition is the negation.
    control_accepted, control_how = verdict(vis_a_guard, model)
    print(f"   control (the vis-a guard)                      {control_how}")

    # Through the mixin's own entry point, which is how a classification worker acquires one.
    # config/qlora.yaml's suffixes are `Gemma4ClippableLinear` wrappers on this architecture and
    # peft replaces the plain `nn.Linear` inside them; which module it wraps is irrelevant to a
    # guard that reads what peft writes ON THE MODEL.
    model.add_adapter(peft.LoraConfig(r=4, target_modules=["linear"], init_lora_weights=False))
    adapted, how = verdict(handler.assert_no_adapter, model)
    print(
        f"\n2. after add_adapter          peft_config {sorted(model.peft_config)}"
        f" · active_adapters() {model.active_adapters()}"
        f"\n   assert_no_adapter                              {how}"
    )

    checks = {
        "the fixed guard ACCEPTS a bare real model": accepted,
        "the fixed guard REFUSES an adapter-carrying one": not adapted,
        "the control fires: the vis-a guard refuses the bare model": not control_accepted,
    }
    checks |= positions_guards(handler, model)
    checks |= resume_guards()
    checks |= reader_guards(handler)
    print()
    for label, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
