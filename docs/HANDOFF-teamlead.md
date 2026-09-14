# HANDOFF-teamlead — вход новой тимлид-сессии (team-lead file; ПЕРЕЗАПИСЫВАЕТСЯ тимлидом при закрытии каждой его сессии)

Механика (стандарт с 14.09, слово оператора): тимлид-сессия в Cowork при закрытии сама переписывает
ЭТОТ файл через Desktop Commander; новая тимлид-сессия начинается с константного промта оператора и
читает этот файл ПЕРВЫМ, затем docs/STATUS.md и новейшую секцию лога решений. Ничего искать не надо.

## Состояние на 14.09 (вечер) — всё принято моими прогонами, $0 весь день
- Фаза `ship-1`, PHASE v20; рулинги дня: (fff) weekly-home · (ggg) стоп s61 → форма (c), реестр не
  двигается · (hhh) region-collect · (iii) reactions-region. Вся объединённая задача (eee) —
  редизайн Реакцій + регион — закрыта за ОДИН день, четыре приёмки подряд.
- Сеалы целы: `promo_screen_data.json` e45860c6… · `config/registry.yaml` eff8ba5b…; экран 1301.
- Suite 4348/2 (`/tmp/tl_make_check_s63.log`), vitest 37/37 — прогоны тимлида.
- Регион: 18 каналов вне реестра (`config/region_channels.yaml`), корень `data/raw_region/`
  (15 889 постов · 8 232 коммента), baseline 0/0/0, выборка комментов честно на экране.
- Деньги: REMAINING $1.1602; облако пусто; впереди только $0.

## Осталось до гейта
s64 «e2e-ship» (исполнитель) → «linkedin-pack» (ТИМЛИД, после README) →
ГЕЙТ (оператор): ср 16.09 вечером (резерв чт 17.09 12:00). Запас ~сутки.

## Следующая тимлид-сессия делает
1. Принимает отчёт s64 «e2e-ship» СВОИМИ прогонами: чистый клон в /tmp (make check + front + tick +
   promo-screen), проба удалённого источника — ПРЯМО-требуемый файл ((iii) 3, не glob), README-витрина,
   `docs/reports/ship-1.md` ≤30 строк, make check ≥ 4348, порцелан §8 пуст. Рулинг ≤12 строк,
   тик в PHASE (→v21), STATUS, и ПЕРЕЗАПИСЬ этого файла.
2. Затем свой айтем «linkedin-pack»: пост + скриншоты + легенда — только из README и файлов
   результатов, ничего от руки.
3. STATUS всегда отвечает КОГДА: гейт ср 16.09 вечером.

## Долги пост-гейта (до гейта не трогать)
glob-асимметрия `required()` · emptiness-guard `report()` · «—» chip · error boundary вкладок ·
s1-bakeoff · добор 2 692 региональных тредов бесплатными перегонами · платное чтение очереди (548)
только после dry-run · перенос запечатанных цитат STATUS в архивный файл.

## Решённое, что легко забыть
- Скилл-строка v3.23 ОДОБРЕНА оператором 14.09 (замер радиуса перед касанием запечатанного файла +
  grep прецедентов; хендофф-в-репо + константный старт). Обновление скилла — на стороне оператора в
  Cowork; патч выдан в чате 14.09.
- `config/region_brands.yaml` оператор правит сам, без рулинга (ggg 5).

## Запуск s64 (свежий процесс `claude` в репо, вставить дословно)
```
Phase ship-1. Every docs/ file below is read with the Read tool — never cat, sed, awk or cp on a team-lead path. Read, in this order and nothing else first: git log -15 --oneline; docs/plans/ship-1.PROGRESS.md; the NEWEST dated section of docs/reviews/2026-08-30-plan-promo-pulse-1.md; docs/PHASE-ship-1.md §2 as the feature list and §4 as the fork defaults; docs/DESIGN-ship-1.md before any front item. Commit any modified or new team-lead file by path first (docs/STATUS.md, docs/PHASE-*.md, docs/PROMPT-*.md, docs/DESIGN-*.md, docs/PROCESS.md, docs/reviews/*, docs/labels-*.jsonl, docs/HANDOFF-teamlead.md). Then do exactly ONE item: the "next" line of PROGRESS. Verify it with its own check and show the output. Commit by path. Update PROGRESS (done / next / open stop, ≤60 lines). If you reach a stop-point of §4 — a paid or irreversible step, a sealed file that would move, a test that would have to be weakened — write it into PROGRESS as the open stop (≤15 lines: stop-point, question, tree state) and END YOUR TURN; a UI or library fork is NOT a stop (§4: decide, name it in PROGRESS, continue). Never add a test, pin, guard or ledger the phase file did not ask for; name the need in PROGRESS instead. Money: $0 on every item; nothing is created in the cloud.
```
