---
type: decision
id: dec-2026-08-03-45g2-captions-and-quiz-rulings
date: 2026-08-03
status: accepted
tags: [decision]
---

# The quiz failed its bar, the media-only post gets a voice, and the sitting is resealed

**Context:** [[45g-parent-context-and-uplabel]] registered the with-post prompts, re-asked the 97
rows the taxonomy-v2 re-label had emptied, and pre-registered the check that would accept or
refuse them: a seeded 40-row contrastive sample, `new / 40 >= 0.90`, all 97 to the operator by
hand below the bar. The team lead ran that check as a 20-row chat quiz instead — 14 rows
proposing the v1 label back, 6 proposing the with-post model's — with the bar declared at
**18/20 before the first block**. It came back **11/20** (`docs/quiz-45g-verdicts.md`).

## (a) The bar failed, and two things survive it

**Auto-remedy is rejected.** 11/20 is not 18/20 and the pre-registered fallback stands: the batch
of 97 is not accepted wholesale. Per arm the failure is not uniform — restore 8/14, model 3/6 —
and the shape of it is the finding:

- **the dish/filling family holds: 10 of 11 `taste` proposals confirmed.** The one refusal is
  `@msuaaaa:11941` *"Вацак 🤮"* — a brand name, not a dish.
- **every other v1 label on this class collapses.** `price` proposals 0/5, of which two became
  `service` (v2's wide boundary reaching rows the re-labeller never touched) and two became `[]`;
  `availability` 0/2.
- consistency check passed: the two identical *«З вишнею»* rows got identical verdicts.

So `scripts/apply_quiz_rulings.py` writes exactly two things. **(a)** The 11 matched rows,
authority `operator-quiz-45g` — the operator's set equals the policy's, so the label written is
the one they wrote down. **(b)** The taste family by mechanical rule, authority
`quiz-validated-pattern`: v1 was exactly `["taste"]`, the comment is at most 30 characters
(`build_sitting_pack.SHORT_CHARS`, the bound the sitting strata already use), it names no
watchlist brand, and its parent post has no text of its own. 17 rows match; 6 are quiz rows
already, 2 are 4.5f operator rulings and are held; **9 are closed by the pattern alone and no
operator has seen them**. Applied: 15 rows moved, 5 already carried the label.

**The 9 divergent rows are not applied**, and neither is anything else in the 97. That is not a
softening of "the verdicts are operator law for their rows": those nine were ruled **blind**, and
the whole reason this class exists is that the parent post could not be read. They go back with
it.

**55% is a property of this class, not of the corpus.** Every row in it was emptied by the
re-labeller and hangs under a post with no text. The corpus-level calibration gate stands at
100/100 (`results/calib_45e_verdict.json`).

## (b) A media-only post gets a voice — and half of them were never pictures

The operator's decision (2026-08-03) was to fetch the parent images and caption them with a
vision model, so a description enters the with-post prompts where the post's own text is empty.
`scripts/fetch_post_media.py` fetched the parents of the 97, of the 424 media-only up-label rows
and of the 14 unreadable rows: **117 posts, 426 images**, albums expanded item by item because
`raw_store.collapse_albums` stores an album under the id of its *first* message and the
informative image is often not that one.

**What the fetch found is the phase's real result: of the 41 media-only parents, only 21 are
pictures. 16 are polls.** A poll's question and options live in a field the collector never
read — `raw_store.post_record` stores `message.raw_text`, which Telegram leaves empty for a poll
— so the corpus recorded these posts as having said nothing while the API had been carrying the
question all along. And the polls are not a tail: `@VARUS_channel:7146` (*«Вареники з якою
начинкою смакують більше?»*) and `@VARUS_channel:7249` (*«Млинці з якою начинкою…»*) are the
parents of 8 of the 20 quiz rows and of the whole confirmed taste family. Captioning alone would
have left exactly the class this phase exists for still blind.

So there are two surrogates, and they are tagged apart in the prompt
(`prompts.POST_SURROGATE`): `[image description] …` for what a vision model saw, `[poll] …` for
what Telegram was already carrying. A transcript is not a description, and a labeller told
otherwise would weigh it as if it were. Four posts get neither — a video, an audio message and
two giveaways — and are named in the record rather than guessed at.

**The captioner is `qwen/qwen3.5-flash-02-23` at `alibaba/fp8`**, chosen by captioning the same
real images with three candidates and reading the output, not by reputation:

| model | on a 6-image promo leaflet | why not |
|---|---|---|
| `qwen/qwen3.5-flash-02-23` | headline, dates, brands, prices, then a summary sentence | **chosen** |
| `google/gemini-2.5-flash-lite` | degenerated into a list of country names on one post; bled marketing copy the prompt forbids on another | and its endpoint reports quantization `unknown`, so it cannot be pinned the way every other endpoint here is |
| `mistralai/mistral-small-3.2-24b-instruct` | HTTP 429 on all three attempts | upstream rate limit |

The gemma family captions nothing and labels nothing: a description written by the model under
test would make its own eval partly a measure of agreement with itself.

The prompt itself was tuned on that evidence and is registered as `caption_post` in
`prompts.PROMPTS` — hashed like the label prompts, `TASKS` untouched, and the one entry that
`build_messages` and `parse_reply` refuse by name because its answer is prose. Its first draft
said "transcribe every piece of text" and "at most two sentences", which a six-image leaflet
makes contradictory: the answer ran past 600 tokens mid-word and never reached its summary. It
now says *do not list every item on a price leaflet* and asks for the whole answer in the
image's own language.

## (c) The sitting is resealed, before a single verdict existed

`results/sitting_45g_manifest.json` sealed a pack that is now wrong in two ways: 300 of its rows
carry labels the caption-fed re-precheck moved, and `emptied40.csv` asks a contrastive question
the quiz already answered. The pack is rebuilt — **the same 300 ids** (the population did not
change, so the seed-42 draw does not either; the new manifest carries the id set and its strata
map so that "same draw" is a fact and not a claim), refreshed labels, and `emptied_redo.csv` in
place of `emptied40.csv`.

Supersession is by naming and never by editing: the old manifest is untouched, the new one
records it as superseded with both shas, and `emptied40.csv` is left byte-identical on disk so
that what the old manifest pinned still verifies. `verdicts_present: 0` is measured at rebuild
time and written into the new manifest — "rebuilt before any verdict existed" is a claim the
artifact has to carry as evidence, not a sentence in a report.

## Consequences

- The 97 are closed at 22 rows (11 operator, 9 pattern, 2 earlier rulings) and **75 go back to
  the operator by hand**, which is the 4.5g fallback minus what the quiz validated — not the ~40
  the prompt estimated. Every one of them now arrives with its post: text, image description or
  poll question.
- `data/annotation/post_captions.jsonl` is a new input to a labelling prompt, so it is committed
  and hashed like the precheck batch beside it.
- Nothing merges anywhere. The strata gates in the resealed sitting still decide the up-label,
  and the redo file still decides the 97.
- **Polls are a corpus-level defect, not a 4.5g2 one.** 16 of 41 here; how many across the whole
  store, and whether the collector should read `message.poll` on the next pass, is a Phase-5
  question this ADR does not answer.

## Amendment (same day) — what the surrogate bought, split, and its variance floor

The aggregate "153 of 424 rows moved a field" understates the effect and hides which surrogate
did the work. Split by what actually stood in the `<post>` block:

| what the post said | rows | moved a field | intents | unclear | sentiment | sarcasm |
|---|---|---|---|---|---|---|
| `[poll]` question | 322 | **140 (43%)** | 81 | 90 | 33 | 10 |
| `[image description]` | 77 | **13 (17%)** | 6 | 5 | 4 | 1 |
| nothing — video, audio, giveaway | 25 | **0 (0%)** | 0 | 0 | 0 | 0 |

Two things follow. **The denominator for "what the surrogate bought" is 399, not 424** — 38%,
not 36% — because 25 of the rows were handed the same `(this post has no text of its own)` as
in 4.5g and had nothing new to read.

And those 25 are a **free negative control**: their rendered prompt was byte-identical to the
4.5g one, so anything moving there would have been run-to-run variance, which this repo knows
is real (`relabel_intents.py`: greedy decoding is not deterministic across a provider's
batches). **Nothing moved — 0 of 25.** So the 153 are the instrument and not the weather, and
the effect is concentrated where the finding said it would be: the poll question moves 43% of
its rows against the image description's 17%. 36 of the 300 gate rows carry a label this moved.
