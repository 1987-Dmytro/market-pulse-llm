# Ревизия инструментария 08.09 (вечер) — оба яруса, сверка с официальными доками Claude Code (у нас 2.1.263); решения оператора

Team-lead file. Запрос оператора: «используй все существующие плагины, поставь исполнителю нужные инструменты, пересмотри
инструментарий твой и исполнителя для оптимального результата; из Telegram проектом не управляю». Прочитано: репо (`CLAUDE.md`,
`.claude/**`, `.mcp.json`, `knowledge/runbooks/tooling.md`, PROCESS, PHASE, STATUS, PROGRESS, git log), `~/.claude/settings.json`,
`~/.claude/plugins/installed_plugins.json`, `~/.claude/skills/*`, `claude plugin list`, `claude mcp list`, `claude auto-mode config`,
процессы Мака. Доки: permission-modes · auto-mode-config · permissions · hooks · model-config · commands · workflows · memory
(code.claude.com/docs/en/…, прочитаны 08.09; цитаты ниже — дословно). Рулинг: `2026-08-30-plan-promo-pulse-1.md` (ee).

## 1. Инвентарь — исполнитель (Claude Code 2.1.263, модель `opus[1m]`)
- Плагины (user scope): code-review · commit-commands · context7 · ponytail 4.7 · pyright-lsp · security-guidance 2.0.7 — включены;
  rust-analyzer-lsp — включён, здесь не нужен; serena — выключен (решение 27.08). MCP user: `ref`, `blockscout` (не нужен);
  + 4 коннектора claude.ai (Gmail, Drive, Calendar, Canva) грузятся в каждую сессию. `.mcp.json` пуст — по замыслу.
- Скиллы `~/.claude/skills`: brain-init (M6) · graphify · memory-protocol · ccc-send. Команды репо: /plan-phase /report /save /close.
  Rules: 6 файлов с `paths:`. Хуки репо: SessionStart ×4, Stop ×1, PreToolUse(Bash) ×2 (sweep-guard, graphify-hint).
- Глобально (`~/.claude/settings.json`): `defaultMode: auto`, `allow: Bash(*)…`, `additionalDirectories: [/Users/hdv_1987]`,
  `effortLevel: high`, `model: opus[1m]`, хуки `ccc hook-permission` (PreToolUse, ВСЕ инструменты, timeout 300000) и `ccc hook-stop`;
  сервис launchd `com.ccc` (`ccc listen`, Telegram-бот с `/c <cmd>`) — 19 дней в фоне; в `env` — живой токен другого проекта.
- Факт запуска: s36 шла как `claude --dangerously-skip-permissions`; s33 (отказ на `pod create`) шла в auto-режиме. Режим
  запуска менялся от сессии к сессии и нигде не был записан. Мак: 8 ГБ RAM; `make check` s36 трижды убит по памяти во время
  её же 20-агентного ревью-workflow — прошёл пятью слайсами (девиация `env-memory`).

## 2. Инвентарь — тимлид (Cowork)
Работает на протоколе: Desktop Commander (репо: чтение, `make check` в фоне, мои файлы; нативно на Маке, не VM) · Agent —
свежий верификатор до покупки · claude-code-guide — проверка механики харнеса по докам · Projects — handoff · память.
Плагины Cowork (16): к проекту — engineering (чек-лист верификатора), data (валидация эталонов, чтение result-файлов); позже —
marketing + design + Canva (упаковка для LinkedIn после гейта); sales/legal/HR/finance/support/enterprise-search/pdf — не про
этот проект; Google Calendar — даты гейта и моих сессий эталона; Gmail/Drive/Chrome — нет применения (источники — только Telegram).

## 3. Находки (по весу; цитата → следствие)
1. **Деньги: отказ классификатора на s33 объяснён.** auto-mode-config: «Claude Code suspends only the broad rules that grant
   arbitrary code execution, such as `Bash(*)`»; «narrow Bash … allow rules such as `Bash(npm test)` stay in effect in auto mode,
   and Claude Code resolves them before the classifier runs». Глобальный `Bash(*)` в auto-режиме не работает — классификатор
   видел `pod create`. permission-modes: «Deny rules block in every mode, including bypassPermissions. Allow rules have no effect
   in bypassPermissions». Значит: (а) с флагом `--dangerously-skip-permissions` классификатора нет, а deny/хуки/гард денег
   остаются; (б) узкие правила `Bash(runpodctl pod create:*)`, `Bash(runpodctl pod delete:*)` страхуют сессию без флага.
   Доказательство PROCESS v2.3 («`--help` прошёл харнес») ничего не доказывало: безобидную команду классификатор пропускает
   и без правила. Правила пишутся из доков, проверка — детерминированная (поле в файле), не «безобидный вызов прошёл».
2. **Таймауты хуков — секунды.** hooks: «`timeout` | Seconds before canceling … Defaults: 600 for `command`». В репо 5000/3000/
   15000 (= 83/50/250 мин), глобальный ccc 300000 (= 83 ч); те же числа в шаблоне brain-init (`templates/settings-hooks.json.tmpl`,
   `scripts/scaffold.py`) и в `two-tier-dev/executor-kit/claude-config/settings.json` — уезжали бы в каждый новый проект. И обратное:
   «A timed-out `command` … hook doesn't block the tool call» — у sweep-guard таймаут должен быть щедрым (30 с), короткий = дыра.
3. **SessionStart-хуки параллельны.** hooks: «All matching hooks run in parallel». `refresh-hot-cache.py` и `cat hot.md` гонялись —
   в контекст мог попадать несвежий AUTO-блок. Один последовательный хук `refresh; cat; stale; census`.
4. **Effort — ритуал вместо поля.** model-config: `effortLevel` в любом файле настроек; `CLAUDE_CODE_EFFORT_LEVEL` — высший
   приоритет; commands: «`max` and `ultracode` are session-only; the `ultracode` key persists». Глобальный дефолт `high`, записи
   для opus в `modelSettings` нет → забытый `/effort xhigh` = сессия на `high`. Поле: `env.CLAUDE_CODE_EFFORT_LEVEL=xhigh`,
   `ultracode: false`.
5. **Цена авто-оркестрации.** s35 (ultracode ON, слово оператора): workflow 57 агентов, 40 умерли на лимите модели, 22 из 26
   находок не проверены; `~/.claude.json`: 48,7 млн cache-read + 2,35 млн cache-write + 0,51 млн output токенов, `lastCost` ≈ $73
   (API-эквивалент) — самая дорогая сессия фазы. s36: 20-агентное ревью параллельно с `make check` → память 8-ГБ Мака кончилась,
   верификатор прошёл только слайсами. workflows: «Up to 16 concurrent agents». PROCESS уже говорил «ultracode OFF» — теперь поле.
6. **Гигиена Мака (файлы оператора).** ccc: хук на каждом вызове инструмента + бот с shell-доступом, которым не пользуются →
   снять целиком. `additionalDirectories` = весь home → сузить до `~/Desktop/Projects` и `~/.claude` (brain-init читает
   `~/.claude.json`, `~/.claude/settings.json`). Токен из `env` глобального файла → в `.claude/settings.local.json` того проекта
   (оператор сам; значение нигде не печатается).
7. **Устаревшее.** `knowledge/runbooks/tooling.md`: «code-review не включён» — включён (`claude plugin list` 08.09); PROCESS
   «Hooks and guards» называл `refuse-sweeping-commands.sh` — файл `scripts/hooks/refuse_sweeping_commands.py`. `/skill-doctor`
   в списке команд доков ОТСУТСТВУЕТ — отчёт о стоимости контекста даёт `/context all` (оператор, один раз, на старте s37).

## 4. Решения оператора 08.09 (вечер) и куда что вошло
- Исполнитель: **s37 «harness-fields» ($0) ПЕРЕД «c3-prep»** — файл `docs/reviews/2026-09-08-harness-fields/settings.json`
  копируется по пути в `.claude/settings.json`; проверка — однострочник PROCESS «Harness fields» → `HARNESS FIELDS OK`
  (прогнан мной на этом файле: OK; на старом файле — MISSING, обе стороны); хуки проверяет старт следующей сессии. Рулинг (ee);
  PHASE v21 §6.1/§8; PROCESS v2.4 «Harness fields» + правки «Models and effort», «Hooks and guards», «Executor conventions».
- Строка запуска всех сессий исполнителя: **`claude --dangerously-skip-permissions`** — поле PROCESS и §0 каждого платного ранбука
  (c3-prep пишет его в ранбук c3; гейт ранбука grep-ает оба allow-правила и первую лексему строки create, exit ≠ 0 иначе).
- Оператор больше не печатает `/effort xhigh`; стандартный промт — байт в байт прежний.
- Мак (тимлид, после конца s36, с бэкапом): оба ccc-хука удалены из `~/.claude/settings.json`, сервис `com.ccc` остановлен,
  plist переименован в `.disabled-20260908`; `additionalDirectories` сужен. Токен переносит оператор.
- Шаблоны: `two-tier-dev` (`250265f`: executor-kit settings, templates PROCESS / standing-prompt / runbook-paid-run, CHANGELOG,
  скилл v3.16) и `~/.claude/skills/brain-init` (`templates/settings-hooks.json.tmpl`, `scripts/scaffold.py`) — секунды, один
  SessionStart, поля effort/ultracode.
- Календарь оператора: эталон позиций 09.09 и 10.09 (10:00–12:00), гейт этапа 1 — 12.09 10:00 (30 мин).
- Скилл v3.16 (паттерны): правило харнеса пишется из доков платформы, а не из симптома, доказательство детерминированное; режим
  сессии, усилие, оркестрация, таймауты гардов — поля харнеса и записи рана; дефект шаблона правится в шаблоне в тот же день;
  авто-оркестрация в сессии исполнителя — строка расходов ретро.

## 5. Сознательно не сделано (и когда пересмотр)
- Модель исполнителя: Opus 5 до гейта; **Fable 5.1 — с фазы C6** вместе с переизданием стандартного промта (PROCESS: смена модели
  переиздаёт промты; посреди денежного шага — нет).
- Плагины исполнителю не ставились — всё нужное фазе есть (pyright, context7/ref, commit-commands, code-review, security-guidance,
  ponytail, graphify). Диета (`blockscout`, rust-lsp, 4 коннектора, ponytail/security-guidance на каждом Stop) — по `/context all`
  на ретро фазы, не наугад. `.mcp.json` остаётся пустым. Workflow-ы в Cowork — только по слову оператора («use a workflow»).
- Второй мозг исполнителя (hot.md + daily logs + native memory) рядом с PROGRESS — три памяти; кандидат диеты на ретро, не сейчас.

## 6. Карта: инструмент тимлида → шаг протокола
Брифинг/промт — текст; приёмка — Desktop Commander (diff, артефакт, свой прогон; `git --no-optional-locks`, без записи в репо,
пока идёт сессия исполнителя — её porcelain-штамп; python — `~/.pyenv/shims/python3.11`, не homebrew); деньги до покупки — Agent
(свежий верификатор) + чтение dry-run и HEAD; правило харнеса — claude-code-guide/WebFetch по докам ДО рулинга; эталоны — Desktop
Commander (картинки страниц читаются им же), валидатор — свой скрипт в `data/annotation/`; гейт оператора 12–13.09 — 20 строк из
`draw_truth_20.py` рядом с эталоном (при нужде — страница-артефакт); даты — Google Calendar; handoff — Projects; упаковка для
LinkedIn (после гейта) — marketing/design/Canva.
