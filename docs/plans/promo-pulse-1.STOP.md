# STOP — `promo-pulse-1-s2s3`, at the ONE authorised paid step

**The smoke cannot be run from this session: no credential and no endpoint.** `scripts/run_5c2.py` needs `$RUNPOD_API_KEY` and `$RUNPOD_5C2_ENDPOINT`; neither is in the environment (`.env` carries only the Telegram keys, the store salt and OpenRouter) and `runpodctl pod list -a` prints `[]` with no serverless endpoint registered. Building one is a worker deploy — a design step with its own bill — and the review authorised **one smoke**, not an endpoint build. So `results/measurements.jsonl` still has no `vision_seconds_per_page` row and K4 emits the RANGE it was written to emit.

**The question, for the operator:** the key plus a live endpoint id relayed into the next session, or the endpoint build authorised as its own step with its own cap? Nothing else in the slice is blocked by it.

**The table SP-1 is decided on now exists, at $0:** 968 leaflet posts → **1 022…9 653 pages**; at the realised 10.408 s/page that is **$3.26…$30.81** against a remainder re-read at **$2.3908** — it fits at neither end, and only the page floor of the two cheaper rates fits at all. §6.1's «ASK, do not trim silently» is what this is, not a defect.

**Tree:** six commits, all by path — `05cf96c` plan · `134eaba` registry · `80a9d10` store · `258ba61` draw · `466a08f` chain refusal · `ea3cf47` top-up + census + projection. `data/` is gitignored and holds the top-up (`shasum -c results/raw_v1_baseline.sha256` → 6 of 6 OK). `collect_r2.py --join` reached 1 of N at 900 s pacing and was stopped with the slice; `results/joins_r2.jsonl` is its cursor and it resumes with one command. Report: `docs/reports/promo-pulse-1-s2s3.md`.
