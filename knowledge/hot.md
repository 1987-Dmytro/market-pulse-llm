<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 07:19:03 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
0b4211c docs(progress): back under the file's own 60-line cap
0aa3dd8 docs(progress): the gate's reason is exact — ten files NAME docs/STATUS.md, four READ it
01a6916 knowledge: s19's boot state — iteration 3 is BOUGHT, the open stop is the holdout notice
ca0dfdb docs(progress): iteration 3 is bought and BOTH bars hold — the open stop is the holdout notice
b93c997 s19(promo-dev): iteration 3 bought and scored — subject 0.7500 RED -> 0.8714 HOLDS, signal 0.9104
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
**Last update:** 2026-09-05 (s20). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл `PROCESS.md` v3, фаза **v7**. Руками, ≤40 строк.

## 🔥 What's Hot
**⛔ ИТЕРАЦИЯ 3 КУПЛЕНА И ПРИНЯТА (q) — DEV-ПЕТЛЯ ЗАКРЫТА, не покупать её снова.** Субъект **0.8714**,
сигнал **0.9104**, полное чтение (40/40, 0 parse failures). Эталон холдаута ПРИШЁЛ 05.09:
`docs/labels-promo-holdout.jsonl`, 188 строк, sha `6fa804880d5d14db…`.
**s20 сделал holdout-prep за $0** (`f879bf9`, `31f9461`): эмиттер и грейдер берут холдаут
ПАРАМЕТРАМИ (`--part {dev,holdout} --gold --step --cap`), `use_part()` перецеливает файловые
константы на входе, `own_rate()` СНЯЛ борроу на свои **88.772 / 201.967 s** (самый медленный под),
`--register` ОТКАЗЫВАЕТ без пина эталона; dev-нога побайтно та же (`5510dd2b3098cdd3…`).

## ⏭️ Next — ДВА ОТКРЫТЫХ СТОПА, платный выстрел ЗАБЛОКИРОВАН, ничего не писать вперёд
**(a) НЕ ЗВАТЬ `--project` на холдауте.** Полосы — dev-петли (край $1.20 ВЫШЕ капа $0.90), KILL —
«max-угол над капом», который у холдаута ПО ПОСТРОЕНИЮ ($1.8999 против $0.90) и который (q)3 уже
принял на рунге 0: `--register` скажет FITS, `--project` через минуту KILL. Полосы называет ТИМЛИД.
**(b) `--close` на `promo-dev-loop` ОТКАЗАЛ, не форсирован:** settles $1.159076 против записанного
$0.866700 — **33.7%**, вне 5%; правая часть `recorded_reading()` — последний `--note`, ВСЕГДА снятый
ДО последнего пода, так что многоподовый шаг не закроется в 5% никогда. Леджер ОТКРЫТ и назван.
**💰 05.09 РУКАМИ:** цикл 3 REMAINING **$1.8312**/$7.00 · `promo-holdout` — НОВЫЙ шаг, кап **$0.90**
((q)3), потрачено $0.00, свой леджер · c3 ≤$0.50 · том удаляется ПОСЛЕ c3. Рунг 0 холдаута: cheap
**$0.8420 (−6.4%)** · priced **$0.8993 (−0.1%!)** · dear **$1.8999 (+111%)**.

## 🚧 Blockers / долги (названы, не построены)
**Ожидание (q)3 в $0.37–0.58 НИЖЕ собственного темпа:** средний угол $0.8420, а реальные $0.493744
итерации 3 по текстовым строкам (140 → 188) ≈$0.64. Не KILL (кап — жёсткий стоп), но **угол `priced`
(ОДНО пересоздание после dead-man) оставляет $0.0007**: второй под не бесплатен. · **Ветки холдаута в
`rung_0`/`register`/`use_part` без теста** (§4 запрещает), проверка одна — сухой контакт за $0. ·
`prep()` зовёт свой счёт `draw.dev_threads` и на холдауте (ключ пиннит `test_promo_dev_pass.py:61`) ·
остальные долги — списком в `docs/plans/promo-pulse-1.PROGRESS.md` («named, not built»), этот файл —
кэш, а не журнал.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
