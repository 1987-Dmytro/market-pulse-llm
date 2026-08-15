#!/usr/bin/env python3
"""The RunPod serverless worker: this repo's own generation path, behind an HTTP job (5b).

The parity measurement of SPEC amendment 3.11 (2) is only a measurement if the production
runtime differs from the 4.5h2 pod in *one* way — where the process runs. So the worker
imports `market_pulse.local_llm` and answers through `LocalClient`: the same chat template,
the same `add_special_tokens=False`, the same greedy `generate`, the same trim-at-first-stop
and the same reply dict. Nothing is re-implemented here, and a serving stack with a
different generation library (vLLM, TGI) was rejected for exactly that reason — it would
confound the runtime delta with a library delta in the one paid run the phase gets.

Two ops, and the first one is a guard rather than a convenience:

``info``
    what this worker actually loaded — the served config, the adapter or merged-artifact
    sha, the quantization dict, the weights and the environment. `serving.assert_serving`
    refuses the run before the first paid row if any of it is not what 5b registered.
``batch``
    ``(task, texts, posts)`` → one reply dict per text, in order.

``caption``
    ``(task, images)`` → one prose caption per album, in order. Config CAPTION only.

``positions``
    ``(task, items)`` → one JSON-array reply per page or row, in order. Config POSITIONS only
    (SPEC 3.17 (9)). ``task`` picks the leg: `positions_post_gm4` items are one-image albums,
    `positions_text_gm4` items are row texts.

Which op each config answers is `serving.CONFIG_OPS`, read as a whole table — a job on the wrong
configuration is refused rather than answered by whatever client happens to be loaded.

Configuration is environment, because a serverless worker has no argv:

    SERVING_CONFIG   A (NF4 base + unmerged adapter), B (merged, requantized to NF4),
                     CAPTION or POSITIONS (NF4 base at the pinned revision, NO adapter)
    ADAPTER_DIR      config A: the arm-A adapter directory
    BASE_WEIGHTS     A, CAPTION, POSITIONS: the base checkpoint, defaulting to the HF repo id
    MERGED_DIR       config B: the merged+requantized checkpoint directory
    MODEL_REVISION   A, CAPTION, POSITIONS: the base weights revision to pin (required for the
                     two base-only configs)

The model loads once per cold start, at the first job — not at import, so that `info` on a
misconfigured worker reports the refusal instead of the container dying before it can.
"""

import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import local_llm, prompts, records, serving  # noqa: E402

CONFIGS = serving.CONFIGS
"""Read from `market_pulse.serving` rather than restated: the driver asserts what the worker
answers, and two tuples that could disagree is the one shape `assert_serving` cannot catch."""

BASE_ONLY = {
    serving.CAPTION_CONFIG: "SPEC amendment 3.13 (3)",
    serving.POSITIONS_CONFIG: "SPEC amendment 3.17 (9)",
    # NOT an amendment, and the value says so: probe-a registers a PROBE, and a pre-registration
    # is a registration rather than law. The layer's amendment comes after the adjudication
    # sitting; a number invented here would put a ruling in the record nobody made.
    serving.READER_CONFIG: (
        "docs/PROMPT-probe-b.md with results/prereg_reader_probe_v2.json"
        " (probe-a's docs/PROMPT-probe-a.md D4 registration is what it supersedes)"
    ),
}
"""The configs that serve the NF4 BASE with the adapter OFF, each beside the amendment that fixes
it there. Both refusals below read this table rather than naming one config, so the second
adapter-free instrument inherits the first one's guards instead of restating them — the failure
that costs money is a new config whose refusals were copied and then narrowed by one word."""

ADAPTER_ENV = ("ADAPTER_DIR", "MERGED_DIR")
"""Every environment variable that puts trained weights on this worker.

Enumerated in one tuple because the CAPTION refusal is a check against the WHOLE set, not
against two names spelled out at the call site: the failure this guards is a third variable
added later that the refusal never learned about. A test holds the tuple against the names
`settings` actually reads."""

REPORTED_LIBRARIES = ("peft", "accelerate", "runpod")
"""Recorded, never asserted — the wheels `local_llm.environment` does not name.

`serving.RUNTIME_LIBRARIES` pins torch, transformers and bitsandbytes because the 4.5h2
anchor records those three, and `assert_runtime_matches` compares against that anchor. It
cannot grow: an anchor that carries no `peft` field would make a fourth entry a guard that
never fires. But config A *is* `peft` applying a LoRA to an NF4 base, and until now a parity
record could not say which peft did it — the staging instructions of two runbooks disagree
(`scripts/runbook_5b2.md` §fresh staging pins `peft==0.18.0`; the run it describes reports
0.20.0 in implementation-notes D7). Reporting is the cheap half of the fix; the pin is the
other half and lives in `scripts/runbook_srv2b.md`.

`runpod` rides along because the 5b wall was a delivery-path failure with no version of the
SDK written down anywhere, and the next post-mortem should not start from that.
"""


def settings(env: dict) -> dict:
    """The worker's configuration, or a ValueError naming what is missing.

    Read once and reported in ``info``, so that "which config is this endpoint"
    is answered by the worker's own environment rather than by the endpoint name
    someone typed — an endpoint is updatable, and a name is not a checksum.
    """
    config = (env.get("SERVING_CONFIG") or "").strip().upper()
    if config not in CONFIGS:
        raise ValueError(f"SERVING_CONFIG must be one of {CONFIGS}, got {config!r}")
    revision = (env.get("MODEL_REVISION") or "").strip() or None
    if config in BASE_ONLY:
        authority = BASE_ONLY[config]
        # The refusal is against the whole set, not against the variable this config happens
        # to have no use for: an endpoint updated from an A template keeps A's environment,
        # and a caption worker that quietly loaded a classification adapter would answer every
        # job without a single number downstream being able to see which model wrote it.
        loaded = [name for name in ADAPTER_ENV if (env.get(name) or "").strip()]
        if loaded:
            raise ValueError(
                f"config {config} serves the base with the ADAPTER OFF ({authority})"
                f" and {', '.join(loaded)} is set. Answers written through the classification"
                " adapter are a third instrument — clear it from the endpoint's environment."
            )
        if not revision:
            raise ValueError(
                f"config {config} needs MODEL_REVISION and it is unset: {authority} fixes this"
                " instrument at the PINNED base revision, and an unpinned base is a"
                " different model that every record would still call gm4-nf4-base"
            )
        return {
            "serving_config": config,
            "weights_dir": (env.get("BASE_WEIGHTS") or local_llm.MODEL_ID),
            "adapter_dir": None,
            "revision": revision,
        }
    needed = "ADAPTER_DIR" if config == "A" else "MERGED_DIR"
    path = (env.get(needed) or "").strip()
    if not path:
        raise ValueError(f"config {config} needs {needed} and it is unset")
    merged = config == "B"
    return {
        "serving_config": config,
        # A serves the base checkpoint and loads the adapter onto it; B serves the merged
        # checkpoint and has no adapter at all. Keeping both fields, one of them None, is
        # what lets `describe` answer the same questions about either config.
        "weights_dir": path if merged else (env.get("BASE_WEIGHTS") or local_llm.MODEL_ID),
        "adapter_dir": None if merged else path,
        "revision": revision,
    }


BASE_ONLY_CLIENT = {
    serving.CAPTION_CONFIG: local_llm.CaptionClient,
    serving.POSITIONS_CONFIG: local_llm.PositionsClient,
    serving.READER_CONFIG: local_llm.ReaderClient,
}
"""Which client each adapter-free config builds. A test holds its keys to :data:`BASE_ONLY`, so a
sixth base-only configuration cannot be added without saying what answers its jobs."""


def assert_no_adapter(model):
    """Refuse a base-only model that arrived with trained weights on it.

    `settings` refuses the *environment* that would load one; this refuses the object, and the
    two are not the same check. peft attaches itself to the model it wraps, so a `PeftModel` —
    or a base someone called `load_adapter` on — carries `peft_config` and answers every job
    looking exactly like the base. SPEC amendment 3.13 (3) fixes the instrument as the NF4 BASE
    with the adapter off; a caption written through the classification adapter would land in
    the same file under the same `caption_source`.

    Takes the model rather than reading it off `self` so a test can drive it with a stub: the
    real load needs the GPU extra and 62 GB of weights.

    `active_adapters` has to be CALLED, not read. transformers gives every model a bound method
    of that name (`PeftAdapterMixin`), and a bound method is truthy — so reading it as a flag
    refuses the very base this config exists to serve. vis-b's first paid handshake was refused
    by exactly that, on a `Gemma4ForConditionalGeneration` with no `peft_config` at all.
    """
    marks = sorted(getattr(model, "peft_config", None) or ())
    active = getattr(model, "active_adapters", None)
    if callable(active):
        try:
            active = active()
        except (ValueError, ImportError):
            # transformers raises ValueError("No adapter loaded") when none is, and ImportError
            # when peft is absent. Both answer the question. Anything else propagates: reading
            # an unknown failure as "clean" is the same defect in the other direction.
            active = ()
    marks += [str(name) for name in (active or ()) if str(name) not in marks]
    if marks or type(model).__name__.startswith("Peft"):
        raise ValueError(
            f"the base-only model carries an adapter ({type(model).__name__},"
            f" {', '.join(marks) or 'by class'}). SPEC amendments 3.13 (3) and 3.17 (9) serve"
            " the NF4 BASE with the adapter OFF — answers written through a classification"
            " adapter are another instrument and nothing in the output file could say so."
        )
    return model


def repo_commit() -> str | None:
    """The commit the worker is actually serving, as its own checkout reports it.

    The record's `git_state()` names the *Mac's* HEAD, and the worker runs whatever
    was staged to the volume — two different things the moment either moves. A
    provenance block that describes code which did not serve is not provenance
    ([[provenance_cannot_name_itself]] one hop out), so the worker answers for itself.
    ``None`` off a checkout rather than a raise: an unknown commit must be visible in
    the record, not fatal to a run that is otherwise fine.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def library_versions(names: tuple[str, ...] = REPORTED_LIBRARIES) -> dict:
    """Installed versions from the metadata database, ``None`` for what is absent.

    Read rather than imported: `peft` costs seconds and RAM to import, and config B
    does not load it at all. ``None`` is a fact and not a hole — the question asked
    here is "is this distribution installed", which has exactly two answers.
    """
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


MAX_NEW_TOKENS = {
    "A": local_llm.MAX_NEW_TOKENS,
    "B": local_llm.MAX_NEW_TOKENS,
    serving.CAPTION_CONFIG: local_llm.CAPTION_MAX_NEW_TOKENS,
    serving.POSITIONS_CONFIG: local_llm.POSITIONS_MAX_NEW_TOKENS,
    serving.READER_CONFIG: local_llm.READER_MAX_NEW_TOKENS,
}
"""What each config's client actually generates, which is what ``info`` has to report.

Until now `describe` answered `local_llm.MAX_NEW_TOKENS` for every configuration, and that was
false for one of them: `CaptionClient` has generated 400 tokens since vis-a while `info` said 256.
Nothing broke, because no caller compares the field — `caption_gm4_5c1.expected_worker()` asserts
four fields and this is not one of them — which is precisely why it survived two paid sessions and
sits wrong in `results/captions_gm4_atb19.json` and `results/serving_visc_smoke.json`. Those two
records are NOT re-pinned: they say what the worker said, and a record edited after the fact is
worse than a record that names a bug. A test holds every value here against the client class the
config builds, so the table cannot drift from the generation call again.
"""


def describe(config: dict, runtime: dict, artifact_sha: str, merged_provenance: dict) -> dict:
    """What ``info`` answers — every field `serving.assert_serving` can be asked to check.

    ``adapter_sha256`` means the same thing in every config and that is the point:
    for A it is the unmerged adapter this worker loaded, for B it is the adapter
    the merge consumed, copied out of the merged artifact's own provenance, and for
    the two base-only configs it is ``None`` because there is no adapter to name. A
    field that changed meaning between the configs could not compare them.
    """
    served = config["serving_config"]
    merged = served == "B"
    caption = served == serving.CAPTION_CONFIG
    positions = served == serving.POSITIONS_CONFIG
    reader = served == serving.READER_CONFIG
    return {
        "serving_config": served,
        "merge_state": serving.MERGE_STATE[served],
        "adapter_sha256": None
        if served in BASE_ONLY
        else (merged_provenance.get("adapter_sha256") if merged else artifact_sha),
        "merged_sha256": artifact_sha if merged else None,
        # What CAPTION has instead of an adapter sha: the registered prompt as THIS checkout
        # spells it. The volume carries its own `repo/`, and a fetch that names a missing ref
        # leaves it on the previous session's commit while printing "Already up to date" —
        # so the driver compares this against its own copy before the first paid caption.
        #
        # Added for CAPTION only, and absent rather than null elsewhere: `results/serving_5b.json
        # :: worker` pins the schema A and B answer with, and `assert_serving` reads a missing
        # field as `<absent>` and refuses — so asking an A endpoint to name a caption prompt is
        # a refusal for free instead of a null that compares equal to nothing.
        **(
            {"caption_prompt_sha256": prompts.prompt_sha256(prompts.CAPTION_TASK_GM4)}
            if caption
            else {}
        ),
        # POSITIONS' equivalent, and a dict because the config serves TWO registered prompts
        # (SPEC 3.17 (5)): the page leg and the text leg are one instrument in two halves, and a
        # worker a session behind on one of them would extract happily under the other's text.
        # `results/sku_pilot_serving.json` pins exactly this dict and the driver compares it whole.
        **(
            {
                "positions_prompt_sha256": {
                    task: prompts.prompt_sha256(task) for task in sorted(prompts.POSITIONS)
                }
            }
            if positions
            else {}
        ),
        # the READER's equivalent, and a dict for POSITIONS' reason: since `docs/PROMPT-probe-b.md`
        # D1 the config serves TWO registered prompts — v1, which three probe-a verdicts were bought
        # under and which stays servable so its evidence can be re-rendered, and v2, which closes
        # Dv393 and Dv394. A scalar could only name one of them, and a worker a session behind would
        # answer with a sha that matches the registration while the OTHER text had moved.
        #
        # The volume carries its own `repo/`, a fetch that names a missing ref leaves it on the
        # previous session's commit while printing "Already up to date", and the driver refuses
        # before the first paid thread unless this dict equals what the Mac renders.
        **(
            {
                "reader_prompt_sha256": {
                    task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)
                }
            }
            if reader
            else {}
        ),
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "max_new_tokens": MAX_NEW_TOKENS[served],
        "model": local_llm.MODEL_ID,
        "repo_commit": repo_commit(),
        "weights_dir": config["weights_dir"],
        "adapter_dir": config["adapter_dir"],
        "revision_requested": config["revision"],
        "merged_provenance": merged_provenance or None,
        # Merged INTO runtime rather than added beside it: `assert_serving` compares the
        # top-level fields the phase registered, and 5b's request/response schema is one of
        # the few things srv-2 must not move. `runtime` is free-form provenance — the guard
        # that reads it, `assert_runtime_matches`, walks a fixed list of three keys.
        "runtime": runtime | library_versions(),
    }


MIN_RUNPOD_SDK = (1, 10, 1)
"""RunPod's own troubleshooting page: 1.7.11–1.10.0 "could corrupt per-worker job tracking".

The symptom is the one srv-2b spent $1.00 failing to explain — jobs stay IN_QUEUE while
workers are available — and the documented fix is `pip install --upgrade "runpod>=1.10.1"`.
The volume already carries 1.11.0 (`results/srv2c_bootlog.json :: worker_info.runtime.runpod`),
so this guard is not a diagnosis of srv-2b; it is a boot-time refusal that stops a re-staged
volume from silently reintroducing a delivery bug no downstream number could see.
"""


def assert_sdk_version(version: str | None) -> str:
    """Refuse to serve on an SDK release whose job tracking is documented broken.

    An absent version is a refusal too: a worker that cannot say which SDK is
    dispatching its jobs cannot be cleared of the bug either.
    """
    if not version:
        raise SystemExit(
            "the runpod SDK does not report a version — a worker that cannot name its"
            f" dispatcher cannot be cleared of the {'.'.join(map(str, MIN_RUNPOD_SDK))} job-"
            "tracking bug. Install runpod and re-stage."
        )
    parts = tuple(int(number) for number in re.findall(r"\d+", version)[:3])
    if parts < MIN_RUNPOD_SDK:
        # A floor, not a range test. RunPod documents the breakage in 1.7.11–1.10.0 and the
        # fix in 1.10.1; nothing says an older release is safe, and this endpoint has no
        # reason to run one. So the message names the fix rather than claiming every
        # refused version sits inside the documented range.
        raise SystemExit(
            f"runpod {version} is below {'.'.join(map(str, MIN_RUNPOD_SDK))}, the release that"
            " fixes the per-worker job tracking RunPod documents as corrupted in 1.7.11–1.10.0"
            " (jobs stay IN_QUEUE while workers are available). Re-stage the volume's venv."
        )
    return version


def dump_rows(path: str, start: int, keys: list[str], replies: list[dict]) -> None:
    """Append this chunk's replies to a file on the network volume, one JSON row each.

    The API result of an async job is deleted 30 minutes after it completes, and the
    parity pass is one job that runs for the better part of an hour — so until it
    returns, the only durable copy of the rows already generated is this file. Opened
    and closed per chunk on purpose: at batch 1 that is one fsync-able write per row,
    which is what makes a job that dies at row 700 still worth 699 rows.

    ``sha8`` is the row's own input, not its index: a dump recovered without the job that
    produced it can then be *checked* against the test set rather than trusted to be in
    the order someone remembers sending. For a `batch` job the input is the row's text; for
    a `caption` job it is `serving.album_key` over the post's images.
    """
    with open(path, "a", encoding="utf-8") as handle:
        for offset, (key, reply) in enumerate(zip(keys, replies)):
            handle.write(
                json.dumps(
                    {
                        "i": start + offset,
                        "sha8": hashlib.sha256(key.encode("utf-8")).hexdigest()[:8],
                        "reply": reply,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


OP_FIELD = {"batch": "texts", "caption": "images", "positions": "items", "reader": "threads"}
"""Each generation op and the payload field that carries its inputs.

``positions`` takes ``items`` rather than a shape-specific name because the op serves two legs:
`positions_post_gm4` sends one-image albums and `positions_text_gm4` sends row texts. What decides
which is the registered ``task``, never an inspection of the payload — the client refuses a task it
does not serve, and a worker guessing the leg from the type of the first element would answer a
mixed job silently."""


def handle(job: dict, client, info: dict) -> dict:
    """Dispatch one job against an already-loaded client. Pure — the tests drive it.

    An unknown ``op`` is an error rather than a default: a typo that silently
    returned ``info`` would score zero rows and look like an empty test set.

    ``batch_size`` splits the job's texts into forward passes; it defaults to all of
    them, which is what every caller before srv-2d sent and what the smoke measured.
    srv-2d ships one input's whole slice in a single job and passes 1, so each forward
    receives a one-element list — the identical call the 8-row smoke and `_one_row`
    already make. The transport changed; the compute path did not.
    """
    payload = job.get("input") or {}
    op = payload.get("op")
    if op == "info":
        return info
    if op in OP_FIELD:
        field = OP_FIELD[op]
        items = payload.get(field)
        if not isinstance(items, list) or not items:
            raise ValueError(f"{op} needs a non-empty list of {field}, got {type(items).__name__}")
        served = info.get("serving_config")
        allowed = serving.CONFIG_OPS.get(served, ())
        if op not in allowed:
            # Every direction, and none of them is a typo: a caption job on config A would be
            # answered by the classification adapter, a batch job on CAPTION would score rows on
            # the bare base, and a batch job on POSITIONS would score them on the base at an
            # 800-token ceiling. All three produce replies, and all three land in a record that
            # names the configuration the endpoint's environment claims. The table is read whole
            # rather than compared pairwise — see `serving.CONFIG_OPS` for what that cost once.
            routing = "; ".join(
                f"{name} serves {'/'.join(ops)}" for name, ops in serving.CONFIG_OPS.items()
            )
            raise ValueError(
                f"op {op!r} on config {served!r}: this configuration answers"
                f" {'/'.join(allowed) or 'nothing but info'} — {routing}. Stop and report"
            )
        posts = payload.get("posts")
        asked = payload.get("batch_size")
        size = len(items) if asked is None else int(asked)
        if size < 1:
            raise ValueError(f"batch_size must be at least 1, got {size}")
        dump = payload.get("dump_path")
        replies: list[dict] = []
        for start in range(0, len(items), size):
            window = items[start : start + size]
            if op == "caption":
                fresh = client.caption(payload["task"], window)
                keys = [serving.album_key(album) for album in window]
            elif op == "positions":
                fresh = client.positions(payload["task"], window)
                keys = [serving.positions_key(item) for item in window]
            elif op == "reader":
                fresh = client.read(payload["task"], window)
                keys = [serving.reader_key(item) for item in window]
            else:
                context = posts[start : start + size] if posts else None
                fresh = client.batch(payload["task"], window, context)
                keys = window
            replies.extend(fresh)
            if dump:
                dump_rows(dump, start, keys, fresh)
        out = {"replies": replies, "n": len(replies)}
        return out | {"dump_path": dump, "forward_batch_size": size} if dump else out
    raise ValueError(f"unknown op {op!r} — this worker answers 'info' and {sorted(OP_FIELD)}")


class Worker:
    """Load-once, answer-many. The load is lazy so a bad config reports instead of crashing."""

    def __init__(self, env: dict | None = None, loader=None) -> None:
        self.env = os.environ if env is None else env
        self.loader = loader or self._load
        self.client = None
        self.info = None

    def _load(self, config: dict):  # pragma: no cover — needs the GPU extra and the weights
        weights = config["weights_dir"]
        if config["serving_config"] in BASE_ONLY:
            # `load_captioner` is named for its first caller and is the NF4 image-text base with
            # no adapter and no causal-LM fallback — which is what BOTH base-only configs serve.
            # The positions page leg needs the same processor for the same reason: a tokenizer
            # would render the template and drop the picture.
            processor, model = local_llm.load_captioner(weights, revision=config["revision"])
            assert_no_adapter(model)
            # a TABLE and not a chain of conditionals, the same reason `serving.CONFIG_OPS` is
            # one: with three base-only configs an `if CAPTION else` answers every other one
            # with the last branch, and the reply would be a legal answer from the wrong client
            client = BASE_ONLY_CLIENT[config["serving_config"]](processor, model)
            runtime = local_llm.environment(model, weights=weights, revision=config["revision"])
            # No artifact sha: there is no adapter to hash and hashing the base checkpoint
            # would walk 62 GB at every cold start. What pins this instrument is the revision,
            # which `environment` reports as requested AND as transformers resolved it.
            return client, describe(config, runtime, None, {})
        merged = config["serving_config"] == "B"
        tokenizer, model = local_llm.load(
            weights, revision=None if merged else config["revision"], prequantized=merged
        )
        provenance, walked = {}, Path(weights)
        if merged:
            source = Path(weights) / "merge_provenance.json"
            if not source.exists():
                raise ValueError(
                    f"{source} is missing — a merged artifact that cannot name the adapter it"
                    " consumed is not the pre-registered config B"
                )
            provenance = json.loads(source.read_text(encoding="utf-8"))
        else:
            from peft import PeftModel

            walked = Path(config["adapter_dir"])
            model = PeftModel.from_pretrained(model, str(walked))
            model.eval()
        client = local_llm.LocalClient(tokenizer, model)
        runtime = local_llm.environment(model, weights=weights, revision=config["revision"])
        return client, describe(config, runtime, records.artifact_sha256(walked), provenance)

    def __call__(self, job: dict) -> dict:
        if self.client is None:
            config = settings(self.env)
            self.client, self.info = self.loader(config)
        return handle(job, self.client, self.info)


def main() -> int:  # pragma: no cover — the RunPod entrypoint, exercised on the worker
    import runpod

    # Before the job loop, not inside it: an SDK that mis-tracks jobs fails by never
    # delivering one, and a refusal printed into the boot log is readable where a
    # silently-swallowed job is not.
    print(f"runpod SDK {assert_sdk_version(library_versions(('runpod',))['runpod'])}", flush=True)
    runpod.serverless.start({"handler": Worker()})
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
