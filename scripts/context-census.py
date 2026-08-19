#!/usr/bin/env python3
"""Boot-budget census (brain-init generic, module M3): a rough estimate of the Tier-0 tax.

Sum of bytes//4 over: ~/.claude/CLAUDE.md · ~/CLAUDE.md · ./CLAUDE.md (+@import, 1 level) ·
MEMORY.md (what the LOADER injects, not the file on disk) · knowledge/hot.md · .claude/rules/*.md
WITHOUT paths: (those load every session). One line of output; warns above `TARGET_KTOK`.
Exits 0.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
TARGET_KTOK = 10.7
"""Re-registered 2026-08-19 by the joint sitting's PRE-REGISTERED FORMULA — the measured
post-debloat floor × 1.1, rounded half-up to one decimal. The floor is this script's OWN printed
reading once groups A–E had left: **9.7K**, identical across three consecutive runs, so
9.7 × 1.1 = 10.67 → **10.7**. The number was written from the measurement and never before it, and
the suspension the 19.08 ruling put on the old ≤9.0K target ENDS here
(knowledge/decisions/boot-tax-re-registered-from-the-measured-floor.md)."""

MEMORY_LINES = 200
MEMORY_UNITS = 25_000
"""The loader's own `vee` and `dde`, re-derived from the binary in `docs/reports/vault-dream.md`
(«Step 1 — the constants»). `dde` is compared against `String.length` — UTF-16 code units, not the
UTF-8 bytes a `stat()` returns, and not 25 * 1024 either (Dv526)."""

JS_TRIM = "\t\n\v\f\r \u00a0\u1680\u2028\u2029\u202f\u205f\u3000\ufeff" + "".join(
    map(chr, range(0x2000, 0x200B))
)
"""What `String.trim()` strips: JS WhiteSpace + LineTerminator, which is NOT `str.strip()`'s set.
Python also takes U+001C–U+001F and U+0085, which JS keeps, and leaves U+FEFF, which JS takes — so
a BOM'd file would be counted three bytes too heavy and a NEL-edged one three bytes too light."""


def nbytes(p):
    try:
        return p.stat().st_size
    except OSError:
        return 0


def loaded_memory(p):
    """The bytes of MEMORY.md the loader actually injects — the census's share of it.

    The loader trims the text with `String.trim()` (`JS_TRIM`, not `str.strip()`), keeps the first
    `MEMORY_LINES` lines, and if the result still
    exceeds `MEMORY_UNITS` code units cuts it back to the last newline at or before the cap (a
    first line longer than the cap has none, and is cut mid-line). What comes back is a BYTE count,
    because that is the unit the census sums: returning the unit count would be the same defect
    Dv526 names, pointing the other way.
    """
    try:
        text = p.read_text(encoding="utf-8", errors="replace").strip(JS_TRIM)
    except OSError:
        return 0
    lines = text.split("\n")
    if len(lines) > MEMORY_LINES:
        text = "\n".join(lines[:MEMORY_LINES])
    units = text.encode("utf-16-le")
    if len(units) // 2 > MEMORY_UNITS:
        head = units[: (MEMORY_UNITS + 1) * 2].decode("utf-16-le", errors="ignore")
        kept, newline, _ = head.rpartition("\n")
        text = kept if newline else units[: MEMORY_UNITS * 2].decode("utf-16-le", errors="ignore")
    return len(text.encode("utf-8"))


def main():
    total = 0
    srcs = 0
    claude_mds = [HOME / ".claude" / "CLAUDE.md", HOME / "CLAUDE.md", ROOT / "CLAUDE.md"]
    for p in claude_mds:
        b = nbytes(p)
        if b:
            total += b
            srcs += 1
            # @import, 1 level (inline expansion counts toward the budget)
            try:
                for m in re.finditer(
                    r"(?:^|\s)@([\w./~-]+\.md)", p.read_text(encoding="utf-8", errors="replace")
                ):
                    total += nbytes((p.parent / m.group(1)).resolve())
            except OSError:
                pass
    slug = re.sub(r"[^a-zA-Z0-9]", "-", str(ROOT))
    total += loaded_memory(HOME / ".claude" / "projects" / slug / "memory" / "MEMORY.md")
    total += nbytes(ROOT / "knowledge" / "hot.md")
    for p in (ROOT / ".claude" / "rules").glob("*.md"):
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:300]
        except OSError:
            continue
        if "paths:" not in head:  # without paths: — always loaded
            total += nbytes(p)
    ktok = total / 4 / 1000
    warn = (
        f"  ⚠️ > {TARGET_KTOK}K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md"
        if ktok > TARGET_KTOK
        else ""
    )
    print(f"brain-census: {ktok:.1f}Ktok boot tax{warn}")


if __name__ == "__main__":
    sys.exit(main())
