#!/usr/bin/env bash
# One headless Opus session per pack, pilot first (SPEC 3.16; docs/PROMPT-opus-audit-a.md
# addendum 2). The protocol file is the prompt, the pack is the assignment, and the only
# thing a session may write is its own returns file.
#
#   scripts/run_opus_packs.sh                # the pilot: packs 01 and 02, then STOP
#   scripts/run_opus_packs.sh --after-pilot  # the remaining packs, once the pilot is reviewed
#   scripts/run_opus_packs.sh --only 07      # one pack, by number
#   scripts/run_opus_packs.sh --dry-run      # print the invocations, spend nothing
#
# Why it stops after two: the packs are 25 sessions of the operator's subscription and the
# instrument has never been run. Two returns files are enough to see whether the rows come
# back in the shape the validator wants, and the other 23 are cheaper to not have run.
#
# What each session may do is the allowlist and nothing else: read ITS pack, read the sent
# images, write ITS returns file. Everything else is denied by omission -- in print mode an
# unallowed tool is refused rather than prompted for, so a session that tries to open
# another pack or edit the one it was given simply cannot.
#
# Three ways a run stops rather than continuing into a wasted afternoon: the model's first
# line is not Opus (the protocol's rule 1, checked here instead of trusted), the returns
# file does not validate, or the pilot has not been reviewed. A broken setup costs one
# session, not twenty-five.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Overridable so the driver itself can be exercised against a stub instead of against the
# operator's real packs and their subscription. Defaults are the only paths in production.
PACK_DIR="${OPUS_PACK_DIR:-data/annotation/opus_audit_5c1}"
MANIFEST="${OPUS_MANIFEST:-results/opus_audit_manifest.json}"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
PROTOCOL="docs/PROMPT-opus-audit-protocol.md"
MEDIA="data/annotation/captions_5c1/posts_media"
PILOT=(01 02)

dry_run=0
after_pilot=0
only=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --after-pilot) after_pilot=1 ;;
    --only) shift; only+=("$1") ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

[[ -f "$PROTOCOL" ]] || { echo "$PROTOCOL is missing -- the sessions have no rules" >&2; exit 1; }
compgen -G "$PACK_DIR/pack_*.md" >/dev/null || {
  echo "no packs in $PACK_DIR. Build them first:" >&2
  echo "  PYTHONPATH=src python3 scripts/build_opus_audit_packs.py" >&2
  exit 1
}

all=()
for pack in "$PACK_DIR"/pack_*.md; do
  number="${pack##*/pack_}"
  all+=("${number%.md}")
done

validate() {  # one returns file, through the schema check that guards the reader
  PYTHONPATH=src python3 scripts/validate_opus_returns.py --manifest "$MANIFEST" "$1"
}

tool_path() {  # a permission rule's path: `./relative` in the repo, `//absolute` outside it
  case "$1" in /*) printf '/%s' "$1" ;; *) printf './%s' "$1" ;; esac
}

run_pack() {
  local number="$1"
  local pack="$PACK_DIR/pack_${number}.md"
  local returns="$PACK_DIR/returns_${number}.jsonl"
  local log="$PACK_DIR/session_${number}.log"

  [[ -f "$pack" ]] || { echo "pack_${number}: no such pack" >&2; return 1; }
  if [[ -f "$returns" ]]; then
    echo "pack_${number}: $returns already exists -- skipping, an evening is not re-runnable"
    validate "$returns"
    return 0
  fi

  local prompt
  prompt="$(cat "$PROTOCOL")

---

## Your assignment for THIS session

- Your pack: \`$pack\` -- read it first, in full.
- Write your rows to: \`$returns\` -- one JSON object per line, exactly the schema each
  item's empty row shows. Create the file; do not edit the pack.
- Read every image path the pack names before you judge that item's caption.
- The pack does not tell you what any other instrument found. That is deliberate: your
  answer is the second reading, and it is only worth having if it is your own."

  local tools
  tools="Read($(tool_path "$pack")) Read($(tool_path "$MEDIA")/**) Write($(tool_path "$returns"))"
  local -a command=("$CLAUDE_BIN" -p "$prompt" --model opus --allowedTools "$tools")

  if [[ $dry_run -eq 1 ]]; then
    # The prompt is the whole protocol and would bury the line that matters, which is the
    # allowlist -- that is what a reader of a dry run is checking.
    echo "pack_${number}: $CLAUDE_BIN -p <protocol + assignment, ${#prompt} chars> --model opus"
    echo "               --allowedTools '$tools'"
    return 0
  fi

  echo "pack_${number}: running (transcript -> $log)"
  "${command[@]}" | tee "$log"

  local first
  first="$(grep -m1 -v '^[[:space:]]*$' "$log" || true)"
  if ! printf '%s' "$first" | grep -qi 'opus'; then
    echo "pack_${number}: STOP. The session's first line does not name Opus:" >&2
    echo "  ${first:-(no output at all)}" >&2
    echo "The protocol's rule 1 exists because the whole review is the stronger model." >&2
    return 1
  fi
  echo "pack_${number}: first line -- $first"

  [[ -f "$returns" ]] || { echo "pack_${number}: STOP. No $returns was written." >&2; return 1; }
  validate "$returns"
}

if [[ ${#only[@]} -gt 0 ]]; then
  for number in "${only[@]}"; do run_pack "$number"; done
  exit 0
fi

if [[ $after_pilot -eq 0 ]]; then
  echo "PILOT: packs ${PILOT[*]} of ${#all[@]}."
  for number in "${PILOT[@]}"; do run_pack "$number"; done
  cat <<EOF

STOP -- the pilot is done and the remaining $((${#all[@]} - ${#PILOT[@]})) packs have NOT been run.

Team lead reviews before the rest go:
  PYTHONPATH=src python3 scripts/validate_opus_returns.py
  less $PACK_DIR/returns_01.jsonl $PACK_DIR/returns_02.jsonl

Then, and only then:
  scripts/run_opus_packs.sh --after-pilot
EOF
  exit 0
fi

for number in "${PILOT[@]}"; do
  if [[ ! -f "$PACK_DIR/returns_${number}.jsonl" ]]; then
    echo "--after-pilot, but pack_${number} has no returns file. The pilot is what the" >&2
    echo "remaining packs are authorised on; run it first, without the flag." >&2
    exit 1
  fi
  validate "$PACK_DIR/returns_${number}.jsonl" >/dev/null
done

echo "pilot reviewed. Running the remaining packs."
for number in "${all[@]}"; do
  case " ${PILOT[*]} " in *" $number "*) continue ;; esac
  run_pack "$number"
done
