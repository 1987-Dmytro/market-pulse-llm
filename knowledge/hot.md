<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 08:57:25 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
96be763 knowledge: the Stop hook's own regeneration of the index and the day's log
9d82b48 docs(progress): back under the file's own 60-line cap
2bf1f86 docs(progress): holdout-prep is done at $0 and TWO stops are open — the shot is blocked
858ead0 s20(holdout-prep): `use_part` binds BOTH halves — `use_part("dev")` was a silent no-op
032b69d knowledge: s20's boot state — the dev loop is CLOSED and TWO stops are open
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-fence-defeats-the-dispatch-that-fixes-the-array.md` — The fence defeats the dispatch that fixes the array
- `the-invite-hash-is-resolved-at-the-call-site.md` — The invite hash is resolved at the call site, not in the registry

## 📅 Recent daily logs

- `2026-09-05.md`
- `2026-09-04.md`
- `2026-09-03.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-05 08:53 (s20, чекпойнт). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл `PROCESS.md` v3, фаза **v7**. Руками, ≤40 строк.

## 🔥 What's Hot
**⛔ ИТЕРАЦИЯ 3 КУПЛЕНА И ПРИНЯТА (q) — DEV-ПЕТЛЯ ЗАКРЫТА, не покупать её снова.** Субъект **0.8714**,
сигнал **0.9104**, полное чтение (40/40, 0 parse failures). Эталон холдаута ПРИШЁЛ 05.09:
`docs/labels-promo-holdout.jsonl`, 188 строк, sha `6fa804880d5d14db…`.
**s20 сделал holdout-prep за $0** (`f879bf9` `31f9461` `7a7d90c` `858ead0` `9d82b48`): эмиттер и
грейдер берут холдаут ПАРАМЕТРАМИ (`--part {dev,holdout} --gold --step --cap`), `use_part()` вяжет
ОБЕ половины на входе, `own_rate()` СНЯЛ борроу на свои **88.772 / 201.967 s** (самый медленный под),
`--register` ОТКАЗЫВАЕТ без пина эталона; dev-нога побайтно та же (`5510dd2b3098cdd3…`).
**`make check` 4320 passed, 2 skipped, exit 0 на `858ead0`** — счёт s19 (тестов не добавлено и не изменено, пол 4266); дерево чистое.

## ⏭️ Next — ДВА ОТКРЫТЫХ СТОПА, платный выстрел ЗАБЛОКИРОВАН, ничего не писать вперёд
**(a) БЛОК НАЧИНАЕТСЯ НА `--register`, а не на `--project` (s21).** `register()` пишет
`decision_table` БЕЗ ветки по `PART` (`promo_dev_pass.py:860`) — первая же команда §0a вкоммитит
полосы dev-петли в предрегистрацию холдаута. И `project()` их НЕ ЧИТАЕТ: вердикт — литералы
`0.80`/`1.20` (`:1275`), KILL при `not worst["fits"]` → KILL, как только медленнейший из трёх
смоука перевалит **95.340 s/thread** (а это самый длинный тред популяции). Полосы называет ТИМЛИД,
и ответу нужна ФОРМА: (i) полосы + право править `project()`, либо (ii) гейт §5 не запускать.
**(b) `--close` на `promo-dev-loop` ОТКАЗАЛ, не форсирован:** settles $1.159076 против записанного
$0.866700 — **33.7%**, вне 5%; правая часть `recorded_reading()` — последний `--note`, ВСЕГДА снятый
ДО последнего пода, так что многоподовый шаг не закроется в 5% никогда. Леджер ОТКРЫТ и назван.
**💰 05.09 РУКАМИ:** цикл 3 REMAINING **$1.8312**/$7.00 · `promo-holdout` — НОВЫЙ шаг, кап **$0.90**
((q)3), потрачено $0.00, свой леджер · c3 ≤$0.50 · том удаляется ПОСЛЕ c3. Рунг 0 холдаута: cheap
**$0.8420 (−6.4%)** · priced **$0.8993 (−0.1%!)** · dear **$1.8999 (+111%)**.

## 🚧 Blockers / долги (названы, не построены)
**Ожидание (q)3 в $0.37–0.58 НИЖЕ собственного темпа:** средний угол $0.8420, реальные $0.493744
итерации 3 по текстовым строкам (140 → 188) ≈$0.64. Не KILL (кап — жёсткий стоп), но **угол `priced`
(ОДНО пересоздание после dead-man) оставляет $0.0007**. · **Ветки холдаута без теста** (§4 запрещает),
проверка одна — сухой контакт за $0 ·
`prep()` зовёт свой счёт `draw.dev_threads` и на холдауте (ключ пиннит `test_promo_dev_pass.py:61`) ·
остальные — списком в `docs/plans/promo-pulse-1.PROGRESS.md` («named, not built»), этот файл кэш, не журнал.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
