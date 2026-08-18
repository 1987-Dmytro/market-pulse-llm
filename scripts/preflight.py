#!/usr/bin/env python3
"""What a contract's names already touch, before the contract touches them.

Pilot H1 of the 2026-08-18 weekly retro (docs/reviews/2026-08-18-weekly-retro.md).
The retro's pattern P1 — «grep-invisible consumers» — is four measured episodes in one
week: a consumer table built by grepping a NAME does not see the two consumers that
actually break, which are a sha pin in a sealed record and a line of prose quoting the
old VALUE. This module is that table, built the other way round.

Four blocks per query, in the order a contract needs them:

1. **hits** — `git grep` counts, split by root, so «who consumes this» is a number and
   not an impression. Untracked files are searched too: the next contract in `docs/` is
   a consumer before it is committed ([[queued_prompt_claims_files]]).
2. **prose** — the same walk over `docs/` and `knowledge/`, matching the query's VALUE
   as well as its name. A note that quotes `20.00` never mentions `CYCLE2_CAP_USD`, and
   it is exactly the consumer that goes stale.
3. **pins** — which sealed records pin which files, seeded from the sha fields of
   `results/*.json` and joined against the query's OWN hits: the answer to «may I edit
   this file» is a list of records, not a feeling. `docs/STATUS.md` «Пины —
   потребители» names four files and one class (PLAN-*); the four are asserted
   present rather than trusted.
4. **digests** — sha256 of every pinned file named, against the value pinned. A
   comment-only edit moves the hash and breaks the record with no row changed
   ([[a_comment_only_edit_moves_the_files_hash]]), so DIFFERS is printed, never
   inferred.

    $ python3.11 scripts/preflight.py closing_record scripts/runpod_guard.py
    $ python3.11 scripts/preflight.py --limit 4 -- --until   # a dashed query needs `--`
    $ make preflight ARGS='--limit 4 -- --until'

The output is designed to be pasted into a contract, so listings are capped by
`--limit` and every cap prints what it dropped — a truncation nobody sees reads as
«covered everything».
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# The roots a consumer count is split by. Anything outside them lands under `other`, so
# the split is a partition of the hits and never a filter on them.
ROOTS = ("src/", "tests/", "scripts/", "docs/", "knowledge/", "config/", "results/")
PROSE_ROOTS = ("docs/", "knowledge/")

SHA = re.compile(r"[0-9a-f]{32,64}")
# The sibling key that names the file a sha field pins, across every shape the sealed
# records actually use. Measured off `results/prereg_*.json` rather than assumed: a
# `sha256` whose siblings are `thread` or `id` pins a RENDERING and no file at all.
PATH_KEYS = ("record", "module", "script", "source", "path", "file")

# docs/STATUS.md «Пины — потребители» names these four files by hand (its fifth entry,
# «PLAN-файлы», is a class and not a path). They are not the
# registry — the registry is built from the records — they are the CONTROL on it: if the
# walk stops finding one of them, the walk broke, not the prose.
STATUS_NAMED_PINS = (
    "src/market_pulse/prompts.py",
    "src/market_pulse/brands.py",
    "src/market_pulse/local_llm.py",
    "scripts/window_summary_5c2.py",
)


def git_grep(query: str, paths: tuple[str, ...] = ()) -> list[tuple[str, int, str]]:
    """Fixed-string hits as (path, line number, text). Untracked files included.

    `--untracked` is the point and not a nicety: the file a contract is about is
    frequently the one `git status` still calls `??`.
    """
    cmd = ["git", "-C", str(REPO_ROOT), "grep", "-n", "-I", "-F", "--untracked", "-e", query]
    if paths:
        cmd += ["--", *paths]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):  # 1 is «no match», which is an answer
        raise RuntimeError(f"git grep failed for {query!r}: {result.stderr.strip()}")
    hits = []
    for line in result.stdout.splitlines():
        path, _, rest = line.partition(":")
        number, _, text = rest.partition(":")
        if number.isdigit():
            hits.append((path, int(number), text.strip()))
    return hits


def split_by_root(hits: list[tuple[str, int, str]]) -> Counter:
    counts = Counter()
    for path, _, _ in hits:
        counts[next((r for r in ROOTS if path.startswith(r)), "other")] += 1
    return counts


def literals_for(name: str) -> list[str]:
    """The right-hand sides of `NAME = <literal>` in `src/` and `scripts/`.

    This is what turns a name into the VALUE prose quotes. Deliberately textual: the
    module is not imported, because importing a script to find out whether it is safe to
    edit is the wrong direction of dependency.
    """
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return []
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*(?::[^=]+)?=\s*(.+?)\s*$")
    values = []
    for path, _, text in git_grep(f"{name} =", ("src/", "scripts/")):
        match = pattern.match(text)
        if match and (value := match.group(1).rstrip(",")) not in values:
            if value and not value.startswith(("(", "[", "{")):
                values.append(value.strip("\"'"))
    return values


def looks_like_a_repo_path(text: str) -> bool:
    return "/" in text and not text.startswith(("http", "@")) and " " not in text.split(" :: ")[0]


def pin_registry() -> dict[str, list[tuple[str, str, str | None]]]:
    """`{pinned path: [(record, field, sha or None), ...]}`, built from every sealed record.

    THREE shapes, because the records use three and a walk that knew one was the first
    thing this instrument's own STATUS control caught:

    * `{"sha256": …, "module": "src/…"}` — a sibling key NAMES the file. The rendering
      pins (`thread`, `id`) name no file and are left out rather than guessed at.
    * `{"borrowed": {"src/…": "<sha>"}}` — the path is the KEY and the sha the value.
      This is how `producer.borrowed` pins every module a producer read, and it is the
      shape `docs/STATUS.md` «Пины — потребители» is actually describing.
    * `{"frozen_when_the_pod_exists": ["src/…", …]}` — a freeze with no digest. Carried
      with `sha=None`: «this file may not move» is a pin even when nothing hashed it,
      and dropping it would answer «may I edit this» with silence.

    A path may carry a ` :: subpath` selector, which is stripped — the digest is of the
    file. `git.dirty` lists are NOT pins and do not match any of the three.
    """
    registry: dict[str, list[tuple[str, str, str | None]]] = {}

    def add(path: str, record: str, field: str, sha: str | None) -> None:
        registry.setdefault(path.split(" :: ")[0], []).append((record, field, sha))

    def walk(node, record: str, field: str) -> None:
        if isinstance(node, dict):
            named = next(
                (
                    str(node[key])
                    for key in PATH_KEYS
                    if isinstance(node.get(key), str) and looks_like_a_repo_path(node[key])
                ),
                None,
            )
            for key, value in node.items():
                if isinstance(value, str) and SHA.fullmatch(value) and "sha" in key.lower():
                    if named:
                        add(named, record, f"{field}.{key}", value)
                elif (
                    isinstance(value, str) and SHA.fullmatch(value) and looks_like_a_repo_path(key)
                ):
                    add(key, record, field or ".", value)  # the `borrowed` map
                elif "frozen" in key.lower() and isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and looks_like_a_repo_path(item):
                            add(item, record, f"{field}.{key}", None)
                else:
                    walk(value, record, f"{field}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, record, f"{field}[{index}]")

    for path in sorted((REPO_ROOT / "results").glob("*.json")):
        try:
            walk(json.loads(path.read_text(encoding="utf-8")), f"results/{path.name}", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  ! {path.name} is not readable JSON — skipped", file=sys.stderr)
    return registry


def digest(path: str) -> str | None:
    target = REPO_ROOT / path
    if not target.is_file():
        return None
    return hashlib.sha256(target.read_bytes()).hexdigest()


def show(hits: list[tuple[str, int, str]], limit: int, indent: str = "    ") -> None:
    for path, number, text in hits[:limit]:
        print(f"{indent}{path}:{number}  {text[:110]}")
    if len(hits) > limit:
        print(f"{indent}… +{len(hits) - limit} more (raise --limit to see them)")


def preflight(query: str, registry: dict[str, list[tuple[str, str, str]]], limit: int) -> None:
    print(f"\n{'=' * 78}\nQUERY  {query}\n{'=' * 78}")

    hits = git_grep(query)
    counts = split_by_root(hits)
    print(f"\n[1] hits — {len(hits)} in {len({p for p, _, _ in hits})} files")
    if counts:
        print("    " + "  ".join(f"{root} {counts[root]}" for root in counts))
    show(hits, limit)

    # The VALUE channel, and only it: block 1 already listed every line that names the
    # query. What this block is for is the consumer that does NOT name it — the note
    # that quotes `20.00` and goes stale when the constant moves.
    values = literals_for(query)
    if not values and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_./-]*", query):
        values = [query]  # the query IS a literal — grep prose for it directly
    print(f"\n[2] prose — docs/ + knowledge/ lines quoting the VALUE {values or '(no literal)'}")
    prose: list[tuple[str, int, str]] = []
    seen: set[tuple[str, int]] = set()
    for token in values:
        for path, number, text in git_grep(token, PROSE_ROOTS):
            if (path, number) not in seen:
                seen.add((path, number))
                prose.append((path, number, f"[{token}] {text}"))
    if values:
        print(f"    {len(prose)} lines in {len({p for p, _, _ in prose})} files")
        show(prose, limit)
    else:
        print("    no module-level literal resolves for this query, so there is no value to trace")

    # The join P1 is about: a file this query TOUCHES may be pinned under a name the
    # query never mentions, so the pins are looked up by the HITS and not by the query.
    # Code first — the file about to be edited is the one the answer is needed for.
    touched = {path for path, _, _ in hits} | {query.split(" :: ")[0]}
    pinned = {path: pins for path, pins in registry.items() if path in touched}
    order = {root: index for index, root in enumerate(ROOTS)}
    ranked = sorted(pinned, key=lambda p: (p != query, order.get(p.split("/")[0] + "/", 9), p))
    print(f"\n[3] pins — {len(pinned)} of the {len(touched)} touched paths are pinned by a record")
    for path in ranked[:limit]:
        marks = ", ".join(
            f"{record}{field}" + (f" {sha[:12]}…" if sha else " FROZEN (no digest)")
            for record, field, sha in pinned[path][:4]
        )
        extra = f" … +{len(pinned[path]) - 4} more" if len(pinned[path]) > 4 else ""
        print(f"    {path}  <- {len(pinned[path])} pin(s): {marks}{extra}")
    if len(ranked) > limit:
        print(f"    … +{len(ranked) - limit} more pinned paths (raise --limit to see them)")
    if not pinned:
        print("    none — no sealed record names any file this query lands in")

    # Every pinned path is hashed, not just the ones block 3 had room to print: a
    # truncation nobody sees reads as «nothing has moved».
    print(f"\n[4] digests — sha256 of all {len(pinned)} pinned paths, against what is pinned")
    matched = 0
    for path in ranked:
        live = digest(path)
        if live is None:
            print(f"    {path}  MISSING on disk — every pin on it is dangling")
            continue
        stale = [(record, field, sha) for record, field, sha in pinned[path] if sha and sha != live]
        if not stale:
            matched += 1
            continue
        print(f"    {path}  live {live[:16]}…  DIFFERS")
        for record, field, sha in stale:
            print(f"        {record}{field} pins {sha[:16]}… — the file has moved since")
    print(f"    {matched} of {len(pinned)} pinned paths match every digest on them")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consumers, prose, pins and digests for a name.")
    parser.add_argument("queries", nargs="*", help="names, constants or paths (use -- first)")
    parser.add_argument("--from-file", type=Path, help="one query per line, # comments ignored")
    parser.add_argument("--limit", type=int, default=12, help="lines per listing (default 12)")
    args = parser.parse_args(argv)

    queries = list(args.queries)
    if args.from_file:
        queries += [
            line.strip()
            for line in args.from_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    if not queries:
        parser.error("nothing to preflight: give at least one query or --from-file")

    registry = pin_registry()
    print(f"pin registry: {len(registry)} paths pinned by results/*.json")
    missing = [p for p in STATUS_NAMED_PINS if p not in registry]
    if missing:
        # The control on the walk, not on the prose: STATUS names these as pinned, so a
        # walk that cannot find them has stopped seeing pins and must say so loudly.
        print(
            f"  ! STATUS names these as pinned and the walk missed them: {missing}", file=sys.stderr
        )

    for query in queries:
        preflight(query, registry, args.limit)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
