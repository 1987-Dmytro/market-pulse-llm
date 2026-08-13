---
type: decision
id: dec-2026-08-13-the-law-grows-inside-marked-blocks
date: 2026-08-13
status: accepted
tags: [decision]
---

# The law may only grow inside a marked block whose name the strip knows, and a sealed pre-registration is never re-pinned to make it green

**Who this is written for:** the **team lead**, who is the one who will next add an amendment. The
rule below is not advice about tidiness; it is the difference between an amendment that lands and
an amendment that turns a red test into a decision about whether to break a seal.

**Context.** Five pre-registrations of the sku programme pin `docs/SPEC.md` **whole**, by sha256, as
one entry of their `pinned_inputs`. They are sealed: they were signed before the sessions they
registered, and re-hashing one after the fact would destroy the only property that makes a
pre-registration worth anything — that it could not have been written to fit the result. So the
spec is a **living document under a byte-for-byte pin**, and those two facts do not obviously fit
together. They fit through one mechanism, and this record is that mechanism written down.

## The mechanism

`write_sku_prereg.registered_law(spec, keep=())` reads `docs/SPEC.md`, removes every HTML-comment
block the strip knows by name, and returns the remaining bytes. **That stripped text is the law the
sealed records registered** — not the file as it stands. One implementation, reached by four
callers: the v4 producer, the B′ producer (`write_sku_prereg_b2.py`, which passes `keep=`), and both
test modules. A second copy could disagree with the first, and the disagreement would land on a pin.

The family of names is one regular expression:

```python
RATIFICATION_NAME = re.compile(
    r"^<!-- (sku-b-ratification(?:-\d+)?|amendment-(?:index|3\.\d+)) begin", re.MULTILINE
)
```

`keep=` is the other half: `write_sku_prereg_b2.KEEP_BLOCKS` is `("sku-b-ratification-7",
"sku-b-ratification-8")`, because B′ was registered **under** (13) and (14) and its law contains
them. Same function, different `keep`, two different sealed pins — which is exactly why there is one
implementation and not two.

## What a future amendment must do

Three things, and the first two are mechanical:

1. **Wear markers.** `<!-- amendment-3.N begin — … -->` … `<!-- amendment-3.N end -->`, with the
   opening marker at the start of a line (the expression is `re.MULTILINE`-anchored). The name must
   match `amendment-3.<digits>`; the `sku-b-ratification[-N]` family is closed and belongs to a
   programme that is finished.
2. **Be added to the enumeration in `tests/test_sku_prereg.py`**, in **document order**. That list is
   a literal on purpose — see below.
3. **Nothing else.** No re-pin, no re-run of a producer against a sealed record, no edit to
   `results/sku_pilot_prereg_v4.json` or `results/sku_pilot_prereg_b2.json`.

**A name the expression does not know is not stripped.** It stays in the hashed text, the pin stops
re-deriving, and `tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says`
goes RED. That is the designed outcome and not a bug to work around: the red test is the amendment
announcing itself. The fix is always to teach the strip the new name, never to re-pin the record.

**The enumeration grows loudly on purpose.** The literal list in the test is what makes an amendment
impossible to land unseen — every one of (12), (13), (14) and 3.18 arrived one name short, and the
list is where that was caught each time. Generalising it into a regex would make the pin survive and
the amendment invisible; the point is the opposite.

**The `rev. 3.14` heading is FROZEN and must not be corrected.** `docs/SPEC.md` line 1 reads
"(rev. 3.14)" and the live revision is 3.18. Those bytes are inside the pinned region — the title
line is not in any marked block — so fixing the number would break every sealed pin for a cosmetic
gain. The live revision lives in the **`amendment-index`** block instead, which wears markers for
that reason and is a finding aid, never the law. **The BODY is the law.**

## prep-a's own evidence, 2026-08-13

The 3.18 amendment landed and reddened the pins, exactly as designed. `5c2-prep-a` taught the strip
the `amendment-*` family — one expression, one commit — and the numbers came back:

| what | sha256 | state |
|---|---|---|
| `docs/SPEC.md` as it stands on disk | `273e9dae9e37ba1a…` | the live file, matching no pin and not meant to |
| the registered law, v4's `keep=()` | `973c87890ad049d5…` | **re-derives** `sku_pilot_prereg_v4.json` |
| the registered law, B′'s `keep=(7, 8)` | `6818926d22b2a46b…` | **re-derives** `sku_pilot_prereg_b2.json` |

Not one byte of either sealed record was touched. Re-derive it yourself at $0:

```
PYTHONPATH=src:scripts python3 -c "
import hashlib, write_sku_prereg as p, write_sku_prereg_b2 as b2
print(hashlib.sha256(p.registered_law(p.SPEC)).hexdigest())
print(hashlib.sha256(p.registered_law(p.SPEC, keep=b2.KEEP_BLOCKS)).hexdigest())"
```

## Two traps this cost, both real

**The skip was positional and the new block landed at index 0.** The test's loop skipped
`blocks[1:]` because `sku-b-ratification` is a **prefix** of `sku-b-ratification-2` … `-8` and would
match inside them. Document order puts `amendment-index` first, so a `[1:]` slice would have stayed
GREEN while silently no longer checking the one name that had just been added. The skip is now by
NAME.

**"The pin re-derives" is not the whole check.** It says today's file strips to the registered
bytes; it says nothing about whether the hash would still NOTICE an amendment that forgot its
markers — which is the one failure this whole mechanism exists to catch.
`test_a_line_outside_every_marked_block_breaks_both_sealed_pins` supplies the other half: it appends
one unmarked line to a **copy** of the spec under `tmp_path` and asserts both pins now differ. The
copy matters — a control that edited the real file would break the seals it is checking.

## What this does not decide

Nothing about **what** may be amended, or by whom. This is the mechanical contract for how a
ratified amendment reaches a file that is pinned by five sealed records. The authority to write law
is the operator's and the team lead's, unchanged.

Related: [[sku-b-serving-and-cap-discipline]], [[skub2-b-prime-closed]],
[[sku-b-pilot-closed-by-measurement]].
