---
type: decision
date: 2026-08-24
status: accepted
tags: [decision, phase6, pass1, lora, vram, transport, money, pod]
---

# 32 GB cannot train this line at 3 072 — and the base columns say the prompt already moved

`lora-c-run r2` executed on 2026-08-24 under rulings (н) and (о). One pod, **3 803 s = $0.7606** of
a $4.00 cap, KILLED on a pre-registered rung with the attempt intact. This record is the English
long form; `docs/reports/lora-c-run-r2.md` is the report.

## The ruling this executed

> карта — **RTX PRO 4500, 32 GB, $0.72/ч, EU-RO-1** (A6000 в датацентре тома none; 32 GB — запас
> против OOM при замороженном micro_batch; фолбэк 4090 преавторизован)

The ruling's own reasoning was that 32 GB is *headroom* against OOM at a frozen `micro_batch`. The
smoke measured the opposite, and it measured it for $0.76 before a training dollar was spent.

## What the smoke found

Six optimizer steps of arm A's config at `max_seq_len` 3 072. Zero completed.

```
OOM: micro_batch -> 1, grad_accum -> 16 (effective batch held)
torch.OutOfMemoryError: Tried to allocate 1.72 GiB. GPU 0 has a total capacity of 31.37 GiB
of which 1.66 GiB is free. ... this process has 29.70 GiB memory in use.
```

The order of those two lines is the finding. `config/qlora.yaml` says «on OOM the trainer halves one
and doubles the other», and the shipped trainer did exactly that on its own — `micro_batch 2 → 1`,
`grad_accum 8 → 16`, effective batch held — and then OOMed **again at micro_batch 1**, in
`backward()`. Nothing was edited on the pod and nothing needed to be: the config's own smallest step
does not fit on this card.

**What it does not say.** It does not say 3 072 is wrong. Every s/step reading this stack holds was
taken on 48 GB, and the ceiling is a property of the rows, which have not moved. The remedies are
the operator's and none was taken: a 48 GB card (A6000 reads `none` in the volume's datacenter, in
two readings a day apart), a different datacenter (a different volume, unpriced), a bigger card
(`RTX PRO 6000` 96 GB at $2.09/h re-prices the whole plan), or
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` — 1.33 GiB of fragmentation against a 1.72 GiB
allocation, which is a guess until a pod measures it.

## What the same $0.76 kept

Both base legs, 198 replies each, hashed on the pod and again on the Mac before the delete, parsed
with **zero refusals**, scored by `scorer.reader_comment_agreement` called per thread.

| leg | every labelled row of E | the 98 holdout rows inside E | realised s/call |
|---|---|---|---|
| base v2 | 85 / 133 = 0.639 | **61 / 98 = 0.622** | 5.32 |
| base v3 | 91 / 133 = 0.684 | **66 / 98 = 0.673** | **9.20** |

**The control column did what it was registered for.** base v3 is base v2 plus one clause asking for
a sentence of reasoning before the label. It moves the holdout subset by five rows with no adapter
anywhere, and the whole gain sits in `не_наш_рынок` (35 → 41 of 66) with `сеть_ритейлер` giving one
back. Had an arm run and come out ahead, this is the share that would have been credited to the
adapter and belongs to the prompt. The 64 the bar names is context here and not a verdict — base v3
takes no bar, the denominator is 98, and the bar is registered per ARM.

The mention cell barely moves: 20 of 66 under v2, 19 under v3, on E's denominator — which is not
holdout-100's 52 and is not comparable to the registered 18/52.

## The rate the contract charged and the rate the card ran

| | charged | measured | ratio |
|---|---|---|---|
| pass-1 v2 | 6.14 s/call | 5.32 | 0.87 |
| pass-1 v3 | 6.14 s/call | **9.20** | **1.50** |

The contract says «v3 is WIDER» in prose and charges 6.14 anyway. Three of the four eval legs and
the marker census are v3. **The next money block carries 9.20.** Rung 3 — this line's own addition,
which grades a base leg on the rate it is REALISING while it bills — returned GO on both legs and is
where that number came from; without it the first spend decision would have been the projection
after the smoke, four thousand charged seconds in.

## Seven transport gaps, all found at $0

Four registered legs had no working producer. `prompts.PASS1` is `{v1, v2}` and v3 may not be added
to it, so the pass-1 handshake refused this line's pack — the v2 leg with it — and the render sent a
v3 item to the READER's renderer (`KeyError: 'post'`, the shape that killed pass1-probe at 427
billed seconds). The leg runner had no `--adapter`. The pass-2 pack carried neither the instrument
block its runner reads, nor the `carried` block, nor `serving`.

The seventh has a reachability answer worth keeping. That pack **declared** `pass2_r2`'s 15 569-char
ceiling and **rendered** at `pass2`'s 12 000. It is rebuilt from an ARM's pass-1 answers while a pod
bills, and a thread's size grows with the rows pass 1 marks `OURS` — so the gap is reachable by an
adapter and not by the base leg that built it. Bounded rather than hoped for: every reference thread
rendered with EVERY row filtered in, which no labelling can exceed.

| | r1's 12 000 | r2's 15 569 |
|---|---|---|
| threads over it, worst case | **1 of 15** — `@matusi_ukr:22272` at 12 399 | **0 of 15**, 3 170 headroom |

That thread is a FLAGSHIP thread of bar 1, so dropping it would make the bar unscoreable. Both sides
now render at 15 569.

Every one of the seven was found by DRIVING the shipped chain against this line's frozen packs with
a fake client, on the Mac, before the create. A pack built at $0 by an earlier contract is an INPUT
to shipped code, and nobody had ever run it through that code.

## Step 0.75 — the marker, moved and not removed

`prompts.NO_POST_TEXT` — «this post has no text of its own, it is an image or a video» — is TRUE of
the real image posts the eval contains and FALSE of a synthetic row, and it marked 160 of 160
against 0 of 506. Ruling (о) forbids it there. `build_lora_c_data.SYNTHETIC_NO_POST` replaces it and
now reads 160/0 where the false one reads 0/0. The 506 prefix re-renders byte-identical; the encode
census holds at 666 encoded, 0 refused, max 2 975, headroom 97, widest row still the real
`@tarilka_malyuka:746#83`.

**The confound remains and is registered.** All 160 are still marked, and those 160 carry all 32
`молочный_бренд` targets. The census that separates «synthetic did not help» from «the adapter
learned the marker» — 40 requests, 20 pairs differing in the header alone — was built, priced and
driven at $0, and never ran: rung 4 fired first.

## Status

The registration is **FROZEN** by this session's create and **the attempt is NOT SPENT**: rung 8
spends it at the first reply an ADAPTER leg generates against E, and no adapter exists. No bar was
scored and none could be — the registered three are per arm.

Related: [[lora-c-arm-b-rendering-and-the-two-leg-pass-2]] ·
[[lora-c-rationale-supervision-and-the-shared-pool]] · `docs/reports/lora-c-run-r2.md`
