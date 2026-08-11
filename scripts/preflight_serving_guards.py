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

    scripts/preflight_serving_guards.py

Needs `transformers` and `peft` — the versions the volume's venv carries, which the run prints
so a mismatch is visible rather than assumed. It exits 1 and says so if they are missing: an
unrunnable preflight is a finding, not a pass.
"""

import sys
from pathlib import Path

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
    print()
    for label, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
