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
    print()
    for label, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
