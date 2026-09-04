<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 06:37:14 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
126555c docs(progress): iteration 1 is read — the open stop is «iteration 1 read», with its three questions
b0c90cc s9(paid): iteration 1 ran WHOLE — signal 0.8792 HOLDS, subject 0.7929 against 0.80, one comment short
36ef74f s9(parse): gemma-4 fences its answer, and the fence is not the answer
77bfed7 s9(project): the summary line read a key `corner()` does not return
d562d34 s9(ledger): the promo-dev-loop step ledger anchored BEFORE the first pod of this session
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `terminate-after-is-the-cap-less-what-the-step-spent.md` — `--terminate-after` is derived from the cap LESS what the step already spent
- `the-fence-is-not-the-answer.md` — The ```json fence is read off, and nothing inside it is repaired — iteration 1's one deviation

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-03 (сессия 9 — ИТЕРАЦИЯ 1 КУПЛЕНА И ПРОШЛА ЦЕЛИКОМ). Этап 1
`SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v3 (без `/goal`). Руками, ≤40 строк.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — стоп «iteration 1 read».** Состояние живёт в
`docs/plans/promo-pulse-1.PROGRESS.md` (done / next / open stop) — он заменил STOP-файлы и отчёты.
Итерация 1: под `0z95ve2n570f0t`, 2 120 с, **$0.435778**; 56/56 юнитов, все balanced, 0 ошибок
разбора. **signal-type 0.8792 ДЕРЖИТ 0.75 · subject 111/140 = 0.7929 против 0.80 — красный на ОДИН
коммент.** Страты: currency 0.7377/0.8583, decimal_only 0.8354/0.9000. Нога B — 16 пустых массивов,
и они ВЕРНЫЕ (рыба, свинина, шланги, люстры — молочки там нет).

**🎯 Три вопроса тимлиду** (все в PROGRESS): (1) 29 промахов subject одной формы — модель отвечает
СЕТЬЮ там, где кодбук хочет товар; это вопрос КОДБУКА, файла тимлида. (2) Забор ```json вокруг всех
40 ответов: `promo_prompts.parse` теперь снимает его и больше ничего — [[the-fence-is-not-the-answer]];
сырые ответы на диске, пересчитывается в любую сторону за $0. (3) Леджер шага ОТКРЫТ: `--close`
отказался на неприземлившемся billing walk (0 мс против 2 120 000) вместо ~$0.00 навсегда.

**✅ Что построено за $0 до денег.** `--project` (гейт таблицы решений; GO $0.7844 против $0.80),
`--score` (соединение ответов с K8 + таблица ошибок), закрытие МАССИВА для ноги B, и восемь
дефектов, подтверждённых состязательным аудитом (`git show 4e75e04`). Дед-ман 500 с оправдался —
порт на 37-й секунде. `--terminate-after` = кап МИНУС уже потраченное
([[terminate-after-is-the-cap-less-what-the-step-spent]]).

## ⏭️ Next / 🚧 Blockers
Ждём рулинг по «iteration 1 read» → итерация 2. Параллельно и за $0: разметка позиций тимлидом ПО
СТРАНИЦАМ (46 страниц) — критический путь S1.
Деньги: шаг `promo-dev-loop` **$0.5254 из $2.50** ($1.9746 осталось) · `CYCLE 3 SPENT $4.0631 of
$7.00 · REMAINING $2.9369`; холдаут $0.30 не тронут. Леджер шага заякорен 20:17:16Z и не закрыт.
**⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`). **⛔ `1925810730` и инвайт-хэш неадресуемы.**
**⚠️ Платный ран — отцеплённым (`setsid`), Dv904** — сегодня хостовые вотчеры убили, под выжил.
**⚠️ Фикстура, пишущая в стор, ДОЛЖНА патчить ВСЕ derived-корни.**
**⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ просто так.**

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
