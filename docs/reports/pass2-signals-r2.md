# pass2-signals r2 — the 75 threads still owed

`docs/PROMPT-pass2-signals-r2.md`, executed. Step 0.5 (the r1 acceptance addendum, $0) → D0′ at $0
on a committed tree → D1 paid, cap $2.50 → D2 at $0 over all 79 units.

## Read back — one line each

- **What step 0.5 corrects.** Three things, all landed before r2's first line of code and all in
  `docs/reports/pass2-signals.md`'s ADDENDUM: Dv681–Dv703 re-tagged on the closed enum so the tally
  can be run (**contract health 16 · paid 7 · 23 of 23**); the pack's headroom is **144 characters
  of 12 000, not 603**, because the D0 section quoted the pre-review pack and `4d60d33` grew the
  prompt +459; and «a smoke mean of 43.09 would have been a GO» is **false by 0.29 s** — the
  break-even mean is **43.087**, whose 1.5× is the live knife edge 64.63.
- **The 75, the four carried rows, and why the prompt must not move a byte.** Owed: the 74 never
  bought plus `@matusi_ukr:22303` (F2), whose reply was REFUSED on a report-only field and never
  read — a transport outcome, not a verdict. The four replies that parsed are COPIED into r2's
  out-file as its first four rows and never re-bought; that copy is only legitimate if the request
  they answered is the request r2 would send, so `pass2_thread_gm4_v1` is byte-identical and every
  carried row is re-verified against the r2 pack's own `rendering_sha256`.
- **Which fields can no longer refuse, and which still can.** Report-only fields are read through a
  tolerant reader that records `unreadable` beside the value and never raises: `per_comment.note`,
  `subject_doubt`, `subject_id`, `stance`, `aspects`, `signals.signal_type` (the scorer says in as
  many words that it is not compared), `signals.reading`, `signals.quote`, `noise.class`,
  `post_summary` and `discussion_summary`. What still refuses, and only this: a relabel; an id that
  was not in the request; a signal citing no comment; a reply about another thread; an
  unbalanced or unreadable object; a domain violation on a SCORED field — `thread`,
  `signals.evidence`, `signals.subject_type`, `signals.aspect`, `per_comment.subject_type` and the
  three answer lists being lists at all.
- **The ceiling and where it is derived from.** **15 569 characters**, and it is measured rather
  than typed: no record on this stack carries the model's context, so the anchor is the largest
  prompt this exact serving config has been PROVEN to serve — `@matusi_ukr:22272` in the reader's
  v5b run, **4 510 prompt tokens, `finish_reason: stop`, 1 896 completion tokens against the
  `serving.output_tokens` reservation of 4 000** — converted into the unit the renderer refuses in
  at pass 2's own worst measured density, **3.4523 chars per prompt token**. 15 569 ≥ **11 856**,
  the widest r2 unit, so there is no STOP; headroom 3 713 characters, 23.8 %.
- **The rate, its two factors, and why the MAX.** `charged = 58.07 × 1.67 = 96.98 → 97 s/thread`:
  the smoke's slowest call, times v2's measured pod-class spread on pass 1 (2.694 → 4.498 s/call
  over three pods). The MAX and not a row-weighted mean because the population's widest unit is 26
  filtered rows (`@klopotenkofood:6040`) against the smoke's widest 10 — a fit over the smoke would
  extrapolate beyond its own range, and the max is the only reading that covers the heavy tail
  without a model of it.
- **The worst case, the cap, the hard stop, the recovery, the step sum.** Generation 75 × 97 =
  **7 275 s**; + ssh 500 + stage/launch 150 + load 450 + overhead 1 300 = **9 675 s = 2.6875 h →
  $2.15** at the $0.80/h price ceiling ($1.4244 at the measured $0.53). Cap **$2.50**; cumulative
  hard stop **11 000 s = $2.4444**; session ceiling 11 250 s ≥ the stop, so the seconds bind first.
  Recovery: one dead pod at rung 2 (500 s, $0.1111) + the worst case = 10 175 s ≤ 11 000 and
  **$2.2611 ≤ $2.50**; the widest dead pod that still fits is **1 325 s**. Step sum: r1's
  $0.108122 on the clock + r2's $2.50 cap = **$2.608122**, on a fresh guard step
  `pass2-signals-r2` with `--step-cap 2.50`.
- **What a KILL after the first new reply means.** The session closes. The rows already bought
  stand in the out-file as evidence, nothing is deleted and nothing is re-asked, and the remainder
  is a new registration — never a second pod after a reply, never a third pod at all.
- **Why the review reads a committed tree.** r1's five-lens review reported «3 confirmed, 12
  refuted» and the split measured nothing but the timing of my own commits: I was fixing the tree
  while the skeptics read it, so twelve of them refuted with «already fixed at HEAD» and named the
  commit that fixed it. Every finding was real. This time the finders are given a COMMIT SHA and
  quote it, the fixes land on top, and a second skeptic pass reads the fixed sha with the tree
  frozen — so the tally is a tally.
