---
type: decision
date: 2026-09-01
status: open
tags: [decision, harness, process, promo-pulse-1]
---

# The `/goal` loop never engaged — §8's resume protocol rests on an unverified mechanism

**Finding, not a ruling.** Recorded because `docs/PHASE-promo-pulse-1.md` §8 (team lead's, v2 of
01.09) makes ONE constant `/goal` paste the way the phase starts and resumes after every STOP, and
that design assumes the native command engages. In the session of 2026-09-01 it did not.

## What was measured

The operator's paste is recorded in `~/.claude/projects/…/0d59d94c….jsonl` as an ordinary prompt:

```
promptSource = "typed"   origin = {"kind":"human"}   version = "2.1.251"
content      = "/goal Phase promo-pulse-1 …"   ← index 0, 3334 chars
```

`/clear` and `/reload-plugins` in the same session arrive as `<command-name>…</command-name>` blocks
with `<local-command-stdout>`; the `/goal` text does not. It reached the model as instructions.

**Consequences.** No evaluator verdict, no auto-continuation, no «Goal active» indicator — which is
what the operator noticed. The «Or stop after 80 turns» bound was counted by the executor by hand,
so it bounded nothing. The predicate was followed as an ordinary instruction, and it was followed;
what did not happen is the LOOP.

## What was ruled out, with the check

| hypothesis | check | verdict |
|---|---|---|
| condition over the cap | 3 328 chars | under |
| something shadows `/goal` | no `~/.claude/commands/goal.md`, no skill named `goal` | no |
| version predates the feature | `name:"goal"` present in 2.1.248 / 250 / 251 / 252 | no |
| workspace untrusted | `hasTrustDialogAccepted: true` | no |
| hooks restricted | no `disableAllHooks` / `allowManagedHooksOnly`, no managed policy | no |
| feature flag off | 0 goal keys in the Statsig / GrowthBook caches | no |

And the registration itself carries no gate on the interactive variant:

```js
{ type:"local-jsx", name:"goal", argumentHint:"[<condition> | clear]", immediate:true }  // no isEnabled
{ type:"local", name:"goal", isEnabled: () => Le() || $n() }                             // non-interactive
```

## What is NOT established

Why the input missed the slash parser. The likeliest remaining path is delivery through the message
queue rather than the TUI input handler — `remoteControlAtStartup: true` is set, and the session's
three human messages carry `origin: {"kind":"human"}` while local commands carry `origin: null`.
**That is a hypothesis, not a reading**, and it is written down as one.

## What the next session should do

Type `/goal` with no arguments: it prints `Goal active: <condition> (N iterations)` or `No goal set`.
That is the one-second live test, and an active goal also shows a ` Goal active ` footer with
`/goal clear to stop early`. If a hand-typed paste in the TUI does light the indicator, §8 needs one
added line — «paste into the TUI, confirm the indicator» — and the protocol is sound as designed.

§8 is the team lead's file and is not edited here; this record and
`docs/reports/promo-pulse-1.md` are how the fact travels. See
[[a-claim-no-number-can-check]], [[gate_verdicts_need_an_artifact]].
