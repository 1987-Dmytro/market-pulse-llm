<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-11 23:09:41 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
1f196f6 docs(report): sku-b-v3-run -- name the commit the previous row could not
c265918 docs(report): sku-b-v3-run -- Dv167, Dv168 and the settled balance
9e0be97 fix(sku-b-v3-run): bar 3's denominator drops the rows nobody adjudicated
545fe1b docs(report): sku-b-v3-run
5dd9e1a feat(sku-b-v3-run): the session's whole output -- a (10)(a) refusal
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `sku-b-run-acceptance-and-resume.md` — sku-b-run accepted at 17 of 138: the probe priced the run, not the cap, and the (10)(b) stop resolves as a resume
- `sku-b-serving-and-cap-discipline.md` — sku-b's serving configuration and its cap discipline: the prep/run split, the base-off pin, and the three readings that keep one job from out-billing the cap

## 📅 Recent daily logs

- `2026-08-11.md`
- `2026-08-10.md`
- `2026-08-09.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-11 23:20 (arch-a ✅, uni-a ✅, uni-b ✅, sku-b-prep ✅, sku-b-run ✅ ПРИНЯТ,
sku-b-v3-prep ✅, **sku-b-v3-run ⛔ ОТКАЗ go/no-go — 0 голд-вызовов, попытка НЕ израсходована**).
**sku-a ✅, R1–R5 ратифицированы, голд text30 размечен, SPEC 3.17 (7)(8)(9)(10)(11) — закон** —
`docs/ARCHITECTURE.md`, граф кода, отчёты `uni-a.md` + `uni-b.md` + `sku-b-prep.md` + `sku-b-run.md`
+ `sku-b-v3-prep.md` + **`sku-b-v3-run.md`**, `docs/PORTING.md`, `config/lexicon.yaml`,
**`results/sku_pilot_prereg_v3.json`**, `results/sku_pilot_serving.json`,
`results/sku_projection_v3.json`, `results/sku_b_positions.json`, **`results/sku_b_positions_v3.json`**.
**Next: решение тимлида — перерегистрация v4 под измеренную цену** (детали в блоке Next).
Блок правится руками; секция выше — авто-ген, маркер НЕ
трогать. Длинная форма: `implementation-notes.md` (Dv100–120 и указатели
Dv133–147), `docs/reports/uni-a.md` (Dv121–124), `uni-b.md` (Dv125–132), `sku-b-prep.md`
(Dv133–147), `sku-b-run.md` (Dv148–153), `sku-b-v3-prep.md` (Dv154–160),
**`sku-b-v3-run.md` (Dv161–168)**, дневники [[2026-08-11]] / [[2026-08-10]], ADR ниже.

## 🔥 What's Hot

**⛔ v3-RUN ОТКАЗАЛ НА go/no-go (10)(a), 20:44. НИ ОДНОГО ГОЛД-ВЫЗОВА, ПОПЫТКА ЦЕЛА.**
121 вызов спроецирован в **$0.5964** против $0.4500 остатка капа → отказ ДО первого голд-вызова.
Дампа на диске нет, `stopped_before_gold: true`, куплено по-прежнему 17 из 138.
**Отказала та самая поправка, которая для этого и писалась:** (11)(c) заменила синтетическую
картинку 64×64 реальной неотправленной страницей — и та померила **14.808 с/страницу** против
1.436 с синтетики и 5.0772 с/вызов, которые первая сессия измерила на 17 реальных страницах.
Break-even = **9.5622 с/страницу**; на маргинале первой сессии ран проецируется в $0.3248 и прошёл бы.
**Оба числа — измерения одного замороженного инструмента, n=1 против n=17.** Первая сессия: 10 из 17
страниц ответили `[]` (14 позиций всего), т.е. её средний маргинал занижен «пустыми» страницами;
warm-up-страница ответила плотным списком. Глубина страниц НЕ разделяет выборки (17 — это стр. 1–6
трёх постов, 91 — стр. 1–6 остальных шестнадцати). Выбор маргинала = перерегистрация = решение
тимлида. **Ничего не перезапускалось ради другого числа.** Отчёт: `docs/reports/sku-b-v3-run.md`.

**СЛЕДУЮЩАЯ ПОПЫТКА СЕЙЧАС ОТКАЗАЛА БЫ ДАЖЕ ПО ОПТИМИСТИЧНОМУ МАРГИНАЛУ (Dv167).**
`RESUME_CAP_USD = 0.45`, `RESUME_LEDGER = spend_sku_b_v3.json`, `RESUME_PHASE = "sku-b-v3"` —
три константы модуля; `read_ledger` возвращает СУЩЕСТВУЮЩИЙ якорь, `--project-stop-usd` умеет
только ужимать (F5). Итого бюджет второго `--resume` = 0.45 − 0.1526 = **$0.2974 < $0.3248**.
Потраченное отказавшей сессией молча ложится на следующую. v4 нужны СВОИ три константы вместе,
а не поднятое число в одной. Считает ли отказ (10)(a) в счёт следующей попытки — решение тимлида.

**БУТ ДИАГНОСТИРОВАН (391.369 с, лог снят со стейдж-пода до создания шаблона).** Лог именует
**11.76 с** SDK-fitness-проверок и **112 с** загрузки 1188 шардов; остальные **267.6 с (68%)** —
вычитание, лог без таймстемпов и не может разделить старт контейнера / импорт torch+transformers /
конструирование модели. Единственная содержательная находка: первые 822 шарда идут **7.61/с за
108 с**, последние 366 — **за 4 с (91.5/с)**, ×12 ступенька = холодное чтение сетевого тома, потом
кэш. Веса лежат на `qw4nwleanc` (`HF_HOME=/runpod-volume/hf`). Сегодняшний бут **402.586 с** на
ДРУГОМ воркере (+2.9%) — режим 390–400 с воспроизводится, 175.8/183.58 с это другой режим.

**RESUME ГОТОВ К ЗАПУСКУ (sku-b-v3-prep ✅, 21:38, $0).** `results/sku_pilot_prereg_v3.json`
зарегистрирована РЯДОМ с v2 — ровно четыре сдвига (`attempts.verbatim` (6)→(11), `cap_usd`
0.35→0.45, `resume.warmup`, `resume.bought_already`), всё остальное байт-в-байт, проверяется лист за
листом. Драйвер: `--resume` покупает только 121 некупленный элемент, **четыре отказа** (сдвинутый
пин / некупленный-с-ответом / купленный в ВЫБОРКЕ / источник, отвеченный обеими сессиями в
СЛИТОЙ записи), варм-ап по (11)(c) читается из прережки и НЕ перевыбирается. Слитая запись —
`results/sku_b_positions_v3.{json,jsonl}` (новые файлы: аппенд в старый дамп сломал бы пин, который
и доказывает, что 17 ответов не переспрашивались). Прелёт: 24 проверки, 0 FAIL, exit 0.
ADR: [[sku-b-run-acceptance-and-resume]].

**ЦЕНА RESUME: $0.3300 В ХУДШЕМ УГЛУ ПРОТИВ $0.45** (`results/sku_projection_v3.json`, шесть углов,
все влезают). Решение — НЕРАВЕНСТВО, а не оценка: страничный маргинал должен дорасти до
**8.26 с/вызов (×1.63)** от измеренных 5.0772, чтобы кап исчерпался. Ошибка прошлой сессии была
×3.54 ровно в этой величине — запас реален и не безграничен. Текстовая нога всё ещё НЕ измерена:
она ОГРАНИЧЕНА страничным маргиналом (тот же инструмент, тот же потолок 800, без картинки на
проводе), srv-2d 4.262 с/строка стоит рядом как сосед, а не как ставка.

**ПРОБА НЕ СТОИТ ТОГО, ЧТО СТОИТ ПРОГОН — ГЛАВНАЯ НАХОДКА ПЛАТНОЙ СЕССИИ (20:30).** go/no-go
(10)(a) померил warm-up на СИНТЕТИЧЕСКОЙ картинке 64×64 (1.436 с) и на строке (0.756 с),
спроецировал 138 голд-вызовов в **$0.1936** против $0.3403 остатка и **пропустил ран**. Реальная
страница листовки — **5.0772 с/вызов, ×3.54 от warm-up**; ин-ран гейт пере-оценил тот же ран в
**$0.3540** и остановил его на **17 из 138**. Гейт, существующий ради «никогда не покупать полпилота»,
купил 12% пилота. Арифметика гейта была ВЕРНА (бут 391 с = $0.12 лёг на `info`, F2 держится) — врал
ВХОД. Урок в память: [[the-probe-must-cost-what-the-run-costs]]. **$0.3540 > $0.35 и без вычета
стейдж-пода — якорь Dv149 стоп НЕ вызвал.**

**ЧТО КУПЛЕНО И ЧТО НЕТ.** Измерено: бут **391.369 с = $0.1200** (регресс ×2.13 против vis-c
183.58 с — см. Blockers: 175.8 с из старых записей это ПОД, другой транспорт), страничный голд-маргинал **5.0772 с/вызов** (n=17), хвост idle 60 с =
$0.0184. **Текстовый голд-маргинал НЕ ИЗМЕРЕН ВООБЩЕ** — текстовая нога не сделала ни одного вызова,
и единственное текстовое число (0.756 с warm-up) эта же сессия опровергла. v3, экстраполирующий
текстовую ногу из warm-up, повторит ровно ту ошибку.

**ЗАКОН КАПА ИСПОЛНЕН В КОДЕ (SPEC 3.17 (10), фикс-пасс).** (a) go/no-go после двух warm-up вызовов,
каждая нога по СВОЕЙ мерке, отказ ДО первого голд-вызова: дамп не пишется вообще, запись несёт
`stopped_before_gold: true`. (b) стоп посреди ноги — находка про КАП, не про инструмент. (c)
`JOB_TIMEOUT_S` 1800 → **900** (1800 с = $0.5520 = 1.58× капа при гейте только МЕЖДУ джобами; 900 с
= $0.2760), и джоб, убитый ЧАСАМИ (`serving.JobExpired`, только `TIMED_OUT` + дедлайн клиента),
кончает ВЕСЬ ран. `--project-stop-usd` теперь `min()`, а не замена. Арифметика F2 держится на том,
что бут биллится на `info`-хендшейке — **проверено в `serve_handler.Worker.__call__`** (загрузка на
первом джобе любого op), это единственное допущение, ломающее go/no-go, если бы было иначе.

**ПРАВИЛО РАСТУЩЕГО ЗАКОНА ПОДТВЕРЖДЕНО ВТОРОЙ РАЗ (`-4`).** Стрип name-agnostic → пин
`973c8789…` воспроизводится при любом числе блоков; перечисление имён в `test_sku_prereg.py`
НАРОЧНО буквальное → каждая новая поправка красит ровно один тест. Лечение всегда одно: ОДНА строка
в перечислении + одна `not in law`, step 0 брифа. **Никогда не пере-пиннивать прережку.**

**NEW REPORT PROTOCOL, IN FORCE FROM uni-a (operator, 11.08).** The phase report is a FILE —
`docs/reports/<phase>.md`, own commit `docs(report): <phase>` — and **chat gets only the path**, not
a summary beside it. Two relayed reports arrived mangled on 11.08; the team lead reads from disk.

**sku-b's ЧЕТЫРЕ ПУНКТА ПОСТРОЕНЫ (sku-b-prep, $0):** пер-позиционный дамп (17 колонок ВЫВЕДЕНЫ из
собственного предложения прережки), op `positions` + `PositionsClient`, пин серв-конфига
`results/sku_pilot_serving.json`, числовой гард пейлоада. Ранний стоп — НЕ более дешёвый пилот:
набор страниц планки 1 — ровно 108 (R2), меньше страниц двигает числитель и не двигает знаменатель.

**TWO FOOTGUNS sku-b-run MUST NOT "FIX".** (1) `max_new_tokens: 256` in
`results/captions_gm4_atb19.json` and `results/serving_visc_smoke.json` is what `info` REPORTED,
not what was generated (400) — `describe()` is fixed in code; those two records stay wrong on
purpose. (2) The preflight now needs a venv carrying `peft` (`--system-site-packages`); under the
plain interpreter it exits 1, and that is the correct behaviour, not a failure.

**`git_state()` IS ONE FUNCTION NOW: `market_pulse.provenance.git_state` (sku-b-prep).** The five
copies delegate and `build_audit_pack.git_state` KEEPS ITS NAME — **51** scripts import it from
there. They had drifted two ways, invisible on a clean tree: three sorted the dirty list and two
did not, and each ignored a different set. `sort` is a named parameter, NOT a thing to standardise:
every record on disk was written under one of the two readings.

**THE CATEGORY VOCABULARY IS LAW NOW: `config/lexicon.yaml` (SPEC 3.17 (8), uni-b).** 14+2 stems,
36 endings, six `units` ORDERED longest-first («г» before «грн»). `data/category_lexicon_draft.json`
is frozen history — five sealed records pin `1225ad75…` and the 5c1 SCREEN instruments still read it
(Dv129). The law REFUSES a taxonomy its stems do not name (`lexicon.unmatched_stems`); a NEW
category must name its subcategories or exempt each stem (3 of 4 coffee stems failed the probe,
Dv130). **sku-b changes nothing because of this.** Long form: `docs/reports/uni-b.md`.

**`fat` → `attribute` IS DONE, AT THE SCHEMA ONLY, AND THE WIRE KEPT THE DOMAIN WORD.** Ladder
`b497c072…` → **`6a257e04…`**; the renamed table is a BIJECTION onto the old one, so no rung moved.
The registered prompts still ask for `"fat"`, the adjudicated `text30.csv` still has a `fat` column,
and `positions.WIRE_KEYS = {"dairy": {"attribute": "fat"}}` is the single place the two meet — the
validator maps the column, and reading `row["attribute"]` off that CSV would score 30 rows of
`none` in silence. Regression held: 11 position · 3 product_mention · 16 none, unchanged.

**v1's MANIFEST PIN IS STALE BY DESIGN AND MUST NOT BE RE-PINNED.** `results/sku_pilot_prereg.json`
pins the pack manifest at `2b941243…`; uni-b rebuilt it over the renamed ladder and disk says
`80e4e12c…`. Four of v1's five pins still hold; that one does not, and that is what superseding
means. The chain to today's bytes is `supersedes` inside v2 — same shape as
`sitting_45g2_manifest.json` and `calib_45e_manifest.json`, same instruction: **do not re-pin.**

**THE FIVE RATIFIED READINGS LIVE IN `results/sku_pilot_prereg_v2.json`, NOT HERE** (long form:
[[sku-b-pilot-readings-ratified]]; v1 `b1bfa40d…` is SEALED beside it and byte-equal on every bar,
threshold, cap and reading). **R1** recall per POST over the 15 non-empty-gold posts, macro.
**R2** the **108 SENT** pages, never the 159. **R3** the four empty-gold posts are a precision
probe. **R4** bar 2 scores at n ≥ 10, reports at 1–9, NOT_REACHABLE at 0. **R5** unreadable replies
excluded and counted (>10% blocks bar 3), n ≥ 20, carriers pooled.

**BAR 3's DENOMINATOR IS ALL 30 ADJUDICATED ROWS, AND 14 WAS REFUSED (team lead, 11.08).** Gold `none`
is a VALUE — the prereg's `comparison` clause makes the model answer `[]` to match it. The 16 `none`
rows price refusal discipline, the 14 rung rows price tiering, and the bar catches both failure modes
(always-`[]` = 16/30 = 0.53, always-a-position = 14/30 = 0.47). Composition from the registered
validator: 11 position · 3 product_mention · 0 brand_mention · 16 none, of the none-rows 12 carry
ticks without a brand and 4 are all-empty pre-filter false positives.

**SPEC 3.17 (7)(8)(9) ARE IN THE FILE AND THE PIN HOLDS THE STRIPPED TEXT.** Each wears
`<!-- sku-b-ratification[-N] begin/end -->`; `write_sku_prereg.registered_law` cuts out **every**
marked block and the pin `973c8789…` is the sha of what is left. ONE strip function, called by the
producer AND by the pin test. **Never re-pin the prereg** — a fourth block is `-4` and its only
legal landing is one more name in the test's enumeration (sku-b-prep did exactly that for `-3`).

**THE PRE-FILTER'S FRAME IS MOSTLY RECIPES — THE RULE WORKING AS WRITTEN.** 769 of 31 638 rows
(posts 4.98%, comments 0.48%; `results/sku_prefilter_census.json`). Recipe feeds firing on «сир»
beside an ingredient quantity dominate; 4 of the 30 drawn rows are direct false positives. Comments
are 6.8% of the frame, so bar 3 prices the POST leg; a comment bar is a team-lead ruling after the
pilot.

**THE SIGNATURE STAMP MOVED `config/registry.yaml`'s SHA; FIVE SEALED RECORDS PIN THE OLD BYTES.**
`validate_opus_returns.py` and `read_opus_audit.py` REFUSE to run — correctly. **Do not re-pin any
manifest.** To re-derive `results/opus_audit_5c1.json`: registry at `d832477`, and
`tests/test_registry.py::registry_without_the_signature_stamp` reproduces the signed `c82d0cff…`.

**THE AUDIT'S AND THE SITTING'S NUMBERS LIVE IN ADRs, NOT HERE.**
[[opus-review-programme-close]]: 25/25 packs, 498/498 rows, `fn_matcher` **0**, all 102 misses
image-only — so `recall_candidate` 0.4769 is about the CAPTIONS, never the matcher.
[[sitting-2026-08-10-composition-signed]]: «Варто» text-matching OFF, «Селянське» anchored-only, the
141 names deferred into the position layer. Both are 5c3's **NAMED** revision and **neither is
applied in sku-a or sku-b** — brand resolution there is the plain alias table.

**A CAPTION IS A SAMPLE OF A LEAFLET PAGE, AND NO BETTER CAPTIONER FIXES IT.** GM4 vs qwen agree on
terms for 8 of 18 posts on byte-identical inputs ([[5c1-vis-b-caption-instrument]]) — why the
position layer exists. Captions stay in for **themes and coverage, never brands**.

**THE HARNESS KILLS LONG BACKGROUND WORK.** A 2.7 h driver on Bash `run_in_background` was stopped
from outside at 36 min. Past half an hour: `nohup … & disown`, and watch the **process**
(`pgrep -f "[r]un_x.sh"` — the bracket stops it matching the watcher), never `tail -f`, which is
silent through a dead process exactly as through a quiet one.

**ONLY `deny` NARROWS A SESSION, AND `Write(path)` IS NOT A RULE** — only `Edit(path)` matches, and
it covers every file-editing tool. Allow rules **union** with `~/.claude/settings.json`, so
`--allowedTools` cannot narrow a headless session; `--disallowedTools` can. `permissions.deny` is 4
entries covering all four team-lead file classes (STATUS, SPEC, PRODUCT, PROMPT-*).

**EVERY RATE sku-b NEEDS IS IN `results/sku_projection.json`, WITH ITS SOURCE PINNED.** Per-IMAGE
marginal 2.3432 s (vis-b, the same 108 pages) corroborated at 2.3523 s (vis-c, 478 images, 0.4%
apart); text row 4.262 s (srv-2d); rate $0.00030669/s; cold start $0.0563 measured / $0.0733
pre-registered, carried as a RANGE. Never multiply an all-in session figure by a count — vis-b's
$0.3869 is a balance delta and the record names it in `never_used`. Bill on `worker_seconds`.

**A JOB CARRIES ITS IMAGES AS BASE64 AND RunPod's `/run` CEILING IS 10 MB.** One ATB post at six
images is 3.68 MB, a slice of three up to 7.83 MB → the 19 ATB posts are 8 jobs. No volume path for
the pictures (`data/annotation/**` is gitignored, they exist only on this Mac). The driver refuses
rather than dropping images: a shortened album is a different instrument for that post.

**GREEDY IS NOT BYTE-REPRODUCIBLE ACROSS WORKERS** (164 vs 172 chars on identical inputs, n = 1),
**and a stable `worker_id` is not a warm worker** — a slot keeps its id across scale-to-zero, which
retracted vis-b's "one cold start". Find the boot, subtract once, quote all-in and marginal apart.

**THE MIDDLE RUNG: `scripts/preflight_serving_guards.py`, $0, RUN BEFORE PAYING.** A REAL
`Gemma4ForConditionalGeneration` from a tiny config (no download, CPU, seconds) drives every serving
guard both ways — CAPTION's and, since sku-b-prep, POSITIONS' whole 3x4 op matrix, the payload
boundary and the parser — each with a control that says it discriminates rather than merely refuses.
13/13 PASS. `make check` stays torch-free: no test imports it.

**THE VOLUME IS THE ONLY STANDING RESOURCE AND ITS CONTENTS ARE KNOWN.** `qw4nwleanc`, 100 GB, EU-RO-1,
**$0.009722/h settled**. It holds `hf/` at revision `842da379…`, `venv/` with the pinned stack (`runpod
1.11.0`), `repo/` at **`d408034`**, the adapter at `b3ca6308…`, the caption dumps, and `start.sh`
byte-identical to `scripts/start_5b_worker.sh`. Everything else is deleted and proven deleted by
listing. **Two 5b-era serverless TEMPLATES also survive** (`unfcr3ja0t`, `0g6zg73ptq`): no charge, but
they were invisible until vis-b — `--type user` is the only listing that can prove a template
deletion, which is why deletion proofs are positive-controlled (show it live, then gone).

**5c1: THE REGISTRY IS 66 = launch 59 + watch 7**, signed by the operator 10.08 (the stamp moves the
file's sha and no row of it). The window is **9 393 posts and 4 880 comments** over 63 channels and the
queue 5c2 prices is **16 218 rows**. Screen v2 reports (`results/yield_screen_5c1_v2.json`, prereg
`1aa89818…` re-hashed and unmoved): **pass_A 32 of 66**, below-both 33, **67 blind** named and counted,
of which 42 are video. **This executor signed nothing** — the composition is the operator's word.

## ⏭️ Next

**СЛЕДУЮЩЕЕ — РЕШЕНИЕ ТИМЛИДА ПО ПЕРЕРЕГИСТРАЦИИ. Кода к написанию нет, пока не решено.**
v3-run отказал на go/no-go, попытка (11) ЦЕЛА, куплено 17 из 138. На столе три числа и один вопрос:
$0.5964 (по маргиналу 14.808 с/стр., n=1) · $0.3248 (по 5.0772 с/стр., n=17) · break-even
9.5622 с/стр. Вопрос: считать ли $0.1526, потраченные отказавшей сессией, в счёт следующей (Dv167 —
сейчас драйвер считает их МОЛЧА, и тогда бюджет второй попытки $0.2974, ниже даже оптимистичной
проекции). v4 = новая прережка РЯДОМ с v3 + свои `RESUME_*` константы (кап, путь якоря, ключ фазы)
вместе. Всё остальное готово: том стейджится в 2 минуты, шаблон/эндпойнт по рецепту
`sku-b-v3-run.md`, продюсер планок написан и протестирован (`scripts/sku_bar_verdicts.py`).

**РУЛИНГ 11.08 НОЧЬЮ: sku-b-run ПРИНЯТ, исход = RESUME.** SPEC 3.17 **(11)**, пять чтений: (a) каждый элемент
популяции покупается РОВНО ОДИН раз за программу — докупаются только **121** некупленный, 17
существующих ответов (включая parse refusal) входят как есть и НИКОГДА не переспрашиваются;
(b) инструмент **ЗАМОРОЖЕН** — суперскрипт/звёздочка идут в пост-пилотную ИМЕНОВАННУЮ ревизию, не в
правку на лету; (c) warm-up возобновлённой сессии **РЕПРЕЗЕНТАТИВЕН** — реальная неотправленная
страница (из 51 вне R2) + реальная строка вне пакета, ответы не скорятся; (d) кап **$0.45**, все
чтения (10) в силе; (e) калибровка тимлида 6/13 — НЕ-гейтящая. Прережка **v3 РЯДОМ с v2** до
запуска. Дальше: v3-run (платный, отдельный контракт) → приёмка планок → **брифинг 5c2**.

**КАЛИБРОВКА ТИМЛИДА (n=13, один лейаут — инференс, не приговор):** промо **13/13** ✓, печатный %
**13/13** ✓, бренды читаются отлично; **вся ошибка в зачёркнутой старой цене и вся — в суперскрипте
копеек** (264⁹⁰→264.5, 39⁹⁰→39.99, 71⁵⁰→71.9, 19⁹⁰→19.99, 44⁴⁰→44.9, 42⁹⁰→42.5). Плюс дубль
«Каштан 75г» в n и промо-без-старой (два товара под одним ценником). Если 91 оставшаяся страница
ведёт себя так же, планка 2 (0.80) провалится и B закроется ИЗМЕРЕНИЕМ.

**ЧТО НЕЛЬЗЯ ДЕЛАТЬ И ПОСЛЕ РУЛИНГА.** Не переспрашивать ни один из 17 ответов; не править
промпты/парсер/пин (заморозка (11)(b)); не пере-пиннивать v2 — v3 регистрируется РЯДОМ. Драйвер сам
откажется перезаписать `results/sku_b_positions.jsonl`.

**WHAT sku-b-run MUST NOT DO.** Re-run a bar after seeing its result; read the 159 available pages
instead of the 108 the gold covers; score its own sample (SPEC §10 — bar 2 is the team lead's read
of the per-position dump against the page images); or read a parse failure as an empty answer. The
driver refuses all four by construction; the one it cannot refuse is the first.

**DEFERRED, DECIDED AFTER THE PILOT AND NOT BEFORE:** a two-stage leaflet read (OCR transcript → SKU
from the text) — the operator's 10.08 proposal, recorded under "Отложено СОЗНАТЕЛЬНО" in
`docs/STATUS.md`; and whether `carrier=comment` earns a bar of its own. The pre-registration does not
change either way.

## 🚧 Blockers

**СЮИТА ЗЕЛЁНАЯ: 1806 passed, 2 skipped; `ruff format --check` 228 файлов. Дерево чистое,
восемь коммитов `84a7d22..1f196f6`; почекаутная таблица зелёная на каждом (контроль — родитель
`6888de7`, 1780).** Красный тест пятого
блока закрыт step 0.2. **Поправка к записи 20:50:** предсказание брифа было ТОЧНЫМ — ассерт
перечисления маркеров живёт ВНУТРИ `test_every_pinned_input_still_hashes_to_what_it_says`, это один
и тот же тест, а не два. Ничего не биллится: платных вызовов в v3-prep не было вообще.
This file is **over arch-a's 6.0K bar**; said, not hidden.

**ОДИН ДОЛГ ОСТАЛСЯ ИЗ ДВУХ.** (1) `cost.jobs` — **ЗАКРЫТ** (Dv153): поле разделено на
`jobs_planned` / `jobs_submitted`, старая запись `results/sku_b_positions.json` НЕ правлена руками —
она улика. Заодно фейку добавлен счёт `info`-хендшейка: прод-клиент его считает, фейк не считал, и
единственный тест поля проверял семантику фикстуры. (2) Холодный старт **391.369 с против
исторических 183.58 с у vis-c (×2.13)** — ОТКРЫТ; `worker-boot.log` на томе `qw4nwleanc`, читается
почти бесплатно в v3-run. Внимание: 175.8 с из старых записей — это **под**, другой транспорт.

**Budget is the live constraint.** Phase 4 stands at **$22.7780 of $25.00, $2.2220 left** (read
2026-08-11T18:23:45Z, ~7 min after the sku-b-run teardown — still settling, Dv33). sku-b's own
anchor `results/spend_sku_b.json` says the session cost **$0.1965** of its $0.35 (floor).
`pod list -a` → `[]`, `serverless list` → `[]`, `template list --type user` → the two 5b leftovers
(`unfcr3ja0t`, `0g6zg73ptq`); only the volume `qw4nwleanc` stands and only it bills.
Re-read the guard before each session rather than trusting this line.

**Recorded rather than open:** the CA-MTL-3 volume is deleted, so its **~$0.24/day** idle billing has
stopped — that literal is load-bearing, not decoration: `scripts/volume_calc_5c1.py` greps it out of
THIS file as a priced input, and a rewrite that drops it reddens ten tests. Arm A's 4.5h2 per-row dump
is permanently lost (`results/predictions/LOST.md`). Two billed rows nobody claims: a 4090 pod row
$0.5098 / 2 470 s on 08-08 (Dv38) and srv-2b's 30-second A4500 row — neither moves a number.

**SUPERSEDED, kept so the old line is not re-read as current:** `results/parity_verdict_5b.json`
says no serverless endpoint here reaches a job-consuming worker — true on **2026-08-06** and
overturned since (parity 758/758, worst head movement 0.0000, [[srv2-program-close]]).

## ⚠️ Footguns for the next run

- **The caption endpoint cannot be made by editing the srv-2d template — `settings()` refuses it, by
  design.** `SERVING_CONFIG=CAPTION` beside `ADAPTER_DIR` or `MERGED_DIR` raises before the model
  loads. Create a NEW template with the three variables of `runbook_vis_b.md` §A.1 and nothing else.
  The refusal is against `serve_handler.ADAPTER_ENV` as a whole, so a third such variable still fires.
- **A RUNNING WORKER HOLDS THE CODE IT BOOTED WITH — a `git merge` on the volume reaches nothing.**
  vis-b paid $0.1581 to learn it. `serverless update` does not restart a worker, `--idle-timeout 60`
  does not stop one that failed a job, and **only `serverless delete` stops it**. **Stage the volume
  BEFORE the endpoint exists** and treat the code as frozen from the first request onward.
- **A failing serverless worker bills exactly like a working one** — srv-2b's ran 31 min at
  $0.00031/s with its job stuck in the queue. Watch **the first job's status**, not worker health.
  Also: `runpod_guard` walks pods and volumes only, so **serverless spend is invisible to it**; and a
  remote `pgrep -f` inside an ssh command **matches its own shell**.
- **A `git fetch` naming a missing ref leaves the OLD `FETCH_HEAD`,** so the merge "succeeds" and
  moves nothing (`Already up to date.` is also a no-op's signature). End every deploy with a
  **content** check of what the runtime executes; `git bundle list-heads` names the real ref.
- **`smoke_5b.py --record` defaults to `results/serving_5b.json` — the pod's cost anchor** ($0.5993/1000,
  $0.4611/pass, 4.071 s/row). Always pass an explicit path.
- **RunPod's request policy is in MILLISECONDS and every briefing writes seconds.**
  `serving.execution_policy(3600, 7200)` is the one conversion point; the endpoint's own
  `--execution-timeout` takes **seconds** and stores ms. Set the endpoint-level timeout too.
- **`assert_runtime_matches` pins three libraries and cannot be taught a fourth** — it skips any the
  frozen anchor (`results/verdict_45h2.json`) lacks, so a `peft` entry would pass every test and never
  fire. peft's pin is in `scripts/runbook_srv2b.md` (**0.20.0**), only REPORTED at runtime.
- **`relabel.read_ledger` writes a provenance string that is wrong for anything past phase 4** — for a
  5c1 phase name it renders `docs/PROMPT-5.c1captions.md` INSIDE a money record. Copy
  `scripts/caption_atb_5c1.py`'s own three-key anchor, not the helper.
- **A caption's price is not stable across phases: 4.5g2 measured $0.000483/post, the pilot paid
  $0.000948.** Same model, endpoint, prompt and images-per-request. Any projection from an old record
  carries a factor-of-two error bar; reprice from the most recent run that actually paid.
- **Two Telethon clients must never share `marketpulse.session`.** `seconds_until_next_join` reads the
  last timestamp in `results/joins_5c1.jsonl`, so the fifteen-minute gap is wall-clock and survives a
  restart — `--join --max 1` can be fired between phases, but a `--join` left in the background while a
  collection runs puts two clients on one SQLite file. Interleave, never overlap.
- **A bare `--posts` or `--comments` resolves the WHOLE registry** — `run()` calls `get_entity(handle)`
  before it checks `comments_enabled and not watch`. That request is what the 2026-08-07 FloodWait wall
  was on. Every collection run carries `--only`.
- **`language_census_5c1.py` and `market_screen_5c1.py` refuse their own default path.** Their shipped
  records are dated measurements a ruling cites and two of those channels have LEFT the registry. Pass
  `--out` with a new path; the day-2 passes are the `_day2.json` pair.
- **`apply_gate_rulings_5c1.remove_sources` stamps `removed 2026-08-07` from a hardcoded literal.** A
  test pins the string; the next channel that leaves the registry gets yesterday's date on its tombstone.
- **The harvest's «already ours» marker does not know the canon's «Исключены — 12» table.**
  `late_batch_5c1.known_handles()` reads the registry and the 5c1 gate record only, so
  `results/harvest_mothers_ua.json` offers back @prikorm_kids_menu — dead by the 06.08 ruling.
- **A pod has no template, so it has no configuration** — whatever boots it carries the worker's
  environment (`SERVING_CONFIG`, `ADAPTER_DIR`, `BASE_WEIGHTS`, `MODEL_REVISION`). 5c2's pod runner
  inherits this: the loop is what must pass them now.
- **Read `runpodctl gpu list` before spending a create call.** Availability is reported per datacenter;
  `datacenter list` answers nothing. A **network volume pins the datacenter**, and SPEC §3.11 (1) makes
  the CLASS the contract: A6000 anywhere, A40 in-class with the card in provenance, **never A100**.
- **`parent_msg_id` and `reply_to_msg_id` are different id spaces, and comparing them looks fine.** One
  is the channel post, the other a message in the discussion group, so `reply_to != parent` is true for
  essentially every row. The thread head is the **smallest** reply target in the thread. Sanity gate: a
  reply family near the corpus size means the discriminator is wrong, not the corpus.
- **Never `git add -A` here.** Team-lead files land in the tree mid-session and the next queued
  `docs/PROMPT-*.md` arrives untracked without warning. Stage by path. The trap has fired with every
  queued prompt since `docs/PROMPT-4.5g4.md`.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. If the pod exists only for one session, **delete** it
  (`runpodctl pod delete` — there is no `pod terminate`), do not stop it. A stopped pod is not a stopped
  bill, and `runpodctl pod list` shows running pods only — use `pod list -a`.
- **Network volumes live in a different datacenter set than the A6000 does** (`EU-SE-1` had the best
  A6000 stock and takes no volumes); pick on the intersection or pay for a second volume. And
  `RUNPOD_POD_ID` is not inherited over ssh — export it or the record cannot name its machine.
- **The RunPod PyTorch image's python is PEP 668 managed.** Use `python3 -m venv --system-site-packages`
  so the image's CUDA-matched torch is reused rather than re-downloaded.
- **Python buffers stdout when it is redirected to a file.** `loss.jsonl` is the live view; `python3 -u`
  fixes the log itself.
- **`results/spend_phase4.json` is the $25 cap's anchor and must not be regenerated.** Delete it and the
  counter silently restarts at today's balance. The guard also refuses when the balance is *above* the
  anchor — a mid-phase top-up is an operator decision.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through the
  scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the `dirty`
  paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor. Do not
  re-run with a bigger `--max-run-usd` to get the record.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py` refuses
  to train above `--time-budget-min` and exits **3**, which reads exactly like a crash. Grep your own
  guards before any unattended launch.
- **Batch 1 is PERMANENT, and "re-measure it" is no longer the answer.** The authorised re-measurement
  ran 2026-08-06 and failed; SPEC §3.11 (2) fixes serving at batch 1. Only a NEW pre-registration may
  re-open it. [[5b2-batch-measurement]]
- **`add_special_tokens=False` is load-bearing and now asserted** (Gemma 4's chat template emits `<bos>`
  itself), and **Gemma 4 has a thinking channel** — `enable_thinking=False` + `add_generation_prompt=True`,
  passed explicitly, or `parse_reply` reads the first brace inside the reasoning text.
- **A `--probe` is not a smoke test unless it prints rows.** Aggregate counts are identical whenever two
  configurations merely parse. Diff the per-row prediction lines and guard with `test -s` — `diff` on two
  empty files is silent success.
- **A print statement can crash a run after the record is written.** Drive `main` through `--record-out`
  with a stub: `--smoke` returns before the record is built and `--probe` before it is written.
- **`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`, `docs/PROMPT-*.md` are team-lead files.** Read
  and commit, never edit. Phase-end facts go to the daily log or `implementation-notes.md`. The refusal
  reads "File is in a directory that is denied", but the rules are file-scoped: the rest of `docs/` is
  writable.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import either, or
  `make check` stops being runnable on a bare checkout. And `RAW_STORE_SALT` in `.env` must never be
  rotated: a new salt orphans every `sender_anon_id`.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair honest.
