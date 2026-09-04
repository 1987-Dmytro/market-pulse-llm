"""The promo-signal extractor's prompt — a NEW module, because `prompts.py` is pinned.

`src/market_pulse/prompts.py` is pinned by five sealed records (`docs/PROMPT-pass1-fewshot.md` D0.2
and the reader registrations), and `docs/PHASE-promo-pulse-1.md` §4 says new prompt text goes in a
new module. This is that module, and it holds exactly one contract: given a promo post and the
comments under it, name what each comment is ABOUT and what the thread SAYS.

Two things this file is deliberately built around.

**The prompt carries the annotator's law.** The codebook the team lead labels dev-40 by is rendered
INTO the prompt, not summarised beside it: where a guideline and a prompt disagree, the model obeys
the prompt and the grader scores the guideline, and the disagreement shows up as an unexplainable
error table ([[prompt_must_carry_the_annotators_law]]). :data:`CODEBOOK` is that law, and
:func:`render` puts it in front of every call.

**The version is the RENDER, not the file.** `signal.extractor_version` is
:func:`extractor_version`, the sha256 of the rendered text — a row has to say which instrument
produced it, and the module's own sha would move for a comment change that the model never saw,
while a template edit that changes what the model reads would move both. The render is what the
model read ([[the_identity_field_stops_covering_the_change]]).

Serving is unchanged and needs no flag: `local_llm.CHAT_TEMPLATE` carries
`"enable_thinking": False` as every client's default, and batch 1 is structural — the positions,
caption and reader legs each loop one item per forward (plan §5.11).
"""

from __future__ import annotations

import functools
import hashlib
import json
from pathlib import Path

import yaml

ADMINS = Path(__file__).resolve().parents[2] / "config" / "channel_admins.yaml"
"""The channel's own account per handle. A file of its own by ruling 04.09 (g) item 1 — the
registry 21 sealed records pin may not grow — and this module is its ONE reader."""

SUBJECT_TYPES = ("chain", "brand", "sku", "post")
"""What a comment can be about. Mirrors `aggregates.SUBJECT_TYPES`; asserted equal in the tests, so
the prompt and the table cannot drift into two vocabularies."""

SIGNAL_TYPES = ("жалоба", "похвала", "спрос", "привычка", "цена")
"""The five of `docs/PHASE-promo-pulse-1.md` §2 S2, in the codebook's own words."""

ATTRIBUTION_SOURCES = ("explicit", "reply_context", "post_context")
"""How the subject was established, weakest last."""

CODEBOOK = """Ти розмічаєш коментарі під ПРОМО-постом торгової мережі.

ПРО ЩО коментар (about) — РІВНО ОДИН субʼєкт на КОЖЕН коментар з текстом:
  chain  — мережа і все, що їй належить: магазини, персонал, каси, наявність на полиці,
           доставка, додаток, сайт, картка лояльності, підтримка, гаряча лінія, чесність
           акції та МЕХАНІКА акції (промокод, купон, ваучер, кешбек). У каналі САМОЇ
           мережі (@VARUS_channel) канал, його пости й тексти — це теж мережа.
  brand  — торгова марка без конкретного товару (Яготинське, Галичина, Рудь, Молокія…)
  sku    — конкретний товар: бренд + тип товару, як написано в тексті
  post   — сам пост або КАНАЛ як обʼєкт, і сюди ж іде ШУМ (правило 2)

ЗВІДКИ ти це знаєш (source):
  explicit       — субʼєкт названий у САМОМУ коментарі
  reply_context  — субʼєкт названий у коментарі, на який цей відповідає
  post_context   — субʼєкт названий тільки в пості

СИГНАЛ треду (signal), нуль або більше:
  жалоба    — скарга чи негативна оцінка: якість, сервіс, немає в наявності, обман,
              відмова купувати; сарказм читається ЗА ЗМІСТОМ («Торгують порожнечею»,
              «Могутньо і незламно», «Шикарно. Цілий день тиша, а потім скидка»)
  похвала   — позитивна оцінка: смак, якість, сервіс, вигідна акція; подяка З ПРЕДМЕТОМ
              («дякую за вашу працю»). Голе «дякую» — шум (2)
  спрос     — інтерес до пропозиції: наявність, де, до коли, що всередині, намір купити,
              як скористатися акцією
  привычка  — заявлена РЕГУЛЯРНІСТЬ, і потрібне слово регулярності: постійно, завжди,
              щотижня, регулярно, роками. Лічба покупок («перший раз… вчора»,
              «декілька разів купувала») регулярністю НЕ є
  цена      — судження або питання про ЦІНУ: рівень, динаміка, порівняння, умови, а
              також правильність чи одиниця надрукованої ціни («на світлині ціна правильна»,
              «це за 100 г ціна?»)

ПРАВИЛА
1. Один субʼєкт на коментар, і КОЖЕН коментар з текстом його має. Два явних субʼєкти —
   бери той, З ЯКОГО коментар ПОЧИНАЄТЬСЯ; другий може зʼявитися в рядку signals.
2. ШУМ і службові → subject_type "post", subject «<msg_id кореня>», БЕЗ сигналів: самі
   емодзі чи реакція, привітання, голе «дякую/спасибо», пунктуація, теги, оффтоп
   («Слава ЗСУ»), балачки між коментаторами і ВЛАСНІ відповіді каналу («Дякуємо за звернення»,
   «переказали колегам», «Світлину вже замінили», «напишіть у чат @varusua_bot»). Рядок post — це
   ВІДПОВІДЬ, а не unsure.
3. Коментар про сам пост чи канал несе сигнали ТІЛЬКИ в каналі-агрегаторі акцій різних
   мереж: «на фото неправильна ціна» → post, жалоба + цена; «канал не про знижки, а про
   треш» → post, жалоба. У каналі мережі те саме — це chain.
4. Форма субʼєкта — НАЗИВНИЙ відмінок. Якщо сутність є в пості — у написанні ПОСТА
   (VARUS, навіть коли коментар пише «варусу»; McDonald’s з апострофом поста; Сільпо,
   KFC, Roshen). Якщо в пості її немає — у написанні коментаря в називному («масло»,
   «атб», «рошен»). sku = бренд + тип товару як у тексті (чипси Люкс, ПИВО BAVARIA,
   Щастябокс, МакМеню, курячі чіпси) — БЕЗ обʼєму, ваги і жирності, якщо в пості не
   перелічено кількох варіантів одного товару. Якщо мережа НІДЕ в треді не названа —
   хендл каналу без «@».
5. Кожен сигнал МУСИТЬ мати цитату — підрядок коментаря, слово в слово.
6. Субʼєкт сигналу спрос: наявність / де / до коли / що всередині → ТОВАР (sku або
   brand); механіка акції, доставка, магазин у місті («У Житомирі є ваша крамниця?») →
   МЕРЕЖА (chain); строки чи умови акції В ЦІЛОМУ, без товару («акція діє 17.03?»,
   «4 січня акції одного дня немає?») → МЕРЕЖА (chain); прохання до каналу-агрегатора
   про акції ІНШОЇ мережі («Свіжих акцій сільпо ще не було?») → та мережа, explicit.
   Питання-претензія («Що з бонусами, у мене нуль») → жалоба, не спрос. Пари несуть
   ОБИДВА типи: «дорого» і «500 грн за картонку» → цена + жалоба; «класна ціна» →
   цена + похвала.
7. НЕЙТРАЛЬНИЙ коментар зберігає свій субʼєкт і НЕ несе сигналу — пояснення, відповідь
   по факту, уточнення, жарт без оцінки («такі в них правила», «Чи з 12 числа»,
   «Діє знижка 3%»). Не вигадуй сигнал, щоб заповнити рядок.
8. unsure — тільки коли субʼєкт НЕ встановлюється з поста і треду. Шум не unsure (2).
   Якщо клас не з переліку — не вигадуй новий: unsure з причиною.
9. Коментар без тексту (тільки стікер чи фото) не розмічається взагалі.
10. Один тред може нести кілька сигналів про РІЗНІ субʼєкти — це різні рядки signals."""

EXAMPLES = """ПРИКЛАДИ (синтетичні, за кодбуком §3–§6; жодного рядка з даних):
1. «у додатку не спрацював купон» → chain / VARUS: субʼєкт chain — це ІМʼЯ мережі, а не її
   функція (додаток, картка лояльності, гаряча лінія, сертифікати) [§3]
2. «а в якому місті його ще можна взяти?» → sku (товар з поста) / спрос: наявність і місце
   питають про ТОВАР; мережу чи місто пиши в note [§5]
3. «[admin] Дякуємо за звернення» → post / <msg_id кореня> / без сигналів: коментар самого
   каналу, і мітку [admin] ставить рендер, а не ти [§6]
4. «навіщо це взагалі публікувати» під постом каналу-агрегатора → post / <msg_id кореня>,
   жалоба: сам пост чи канал як обʼєкт [§3]
5. «Ок, зрозуміло» · «І що?» · «Ага, ясно» · «Плюсую» → post / <msg_id кореня> / без
   сигналів: репліка іншому коментатору, яка нічого не називає і не оцінює [§6]"""
"""The worked examples the TEMPLATE carries — ruling 03.09 (f) item 3's five categories, in the
codebook's own shape and cited by its sections, and SYNTHETIC by ruling 04.09 (j) item 3: not one
line of them is a dev-40 or holdout-40 thread. `promo_dev_pass.py --leak-check` is the proof, and
it reads these strings out of this module rather than a list retyped beside it
([[a_number_typed_into_its_own_checker]], [[the_instruments_examples_came_from_the_exam]])."""

TEMPLATE = """{codebook}

""" + EXAMPLES + """

ПОСТ ({channel}, msg_id={thread_root}):
{post}

КОМЕНТАРІ:
{comments}

Поверни JSON: {{"about": [...], "signals": [...], "unsure": [...]}}
  about  : {{"msg_id": int, "subject_type": str, "subject": str, "source": str, "confidence": float}}
  signals: {{"type": str, "subject_type": str, "subject": str, "msg_id": int, "quote": str,
             "confidence": float}}
  unsure : {{"msg_id": int, "reason": str, "candidates": [str]}}"""


@functools.lru_cache(maxsize=1)
def _admins() -> dict[str, frozenset[str]]:
    return {
        handle: frozenset(ids or ())
        for handle, ids in (yaml.safe_load(ADMINS.read_text(encoding="utf-8")) or {}).items()
    }


def admin_ids(channel: str) -> frozenset[str]:
    """The `sender_anon_id`s of `channel`'s own account, empty for a channel with none named."""
    return _admins().get(channel, frozenset())


def render(channel: str, thread_root, post: str, comments: list[dict]) -> str:
    """The text the model reads, for one cooled thread. Deterministic — no clock, no ordering luck.

    Comments are rendered in msg_id order rather than store order: the store is append-only and a
    resumed collection can interleave, and a prompt whose lines move between runs would move
    `extractor_version` with them.

    Two rules of ruling 04.09 (g), both mechanical so the model never guesses at them. A comment the
    channel's OWN account wrote is prefixed `[admin] ` — iteration 1 missed four of them because the
    text alone cannot say who wrote it (codebook §6, rule 2). A comment with no text is DROPPED: it
    is outside the queue, outside the gold, and a blank `[admin] ` line would be content nobody
    labelled ([[an_exclusion_by_id_is_not_an_exclusion_by_text]] — the id decides, the text does
    not, and a `null` sender matches no admin).
    """
    admins = admin_ids(channel)
    lines = []
    for row in sorted(comments, key=lambda row: int(row["msg_id"])):
        text = (row.get("text") or "").strip()
        if not text:
            continue
        mark = "[admin] " if row.get("sender_anon_id") in admins else ""
        lines.append(f"[{row['msg_id']}] {mark}{text}")
    return TEMPLATE.format(
        codebook=CODEBOOK,
        channel=channel,
        thread_root=thread_root,
        post=(post or "").strip() or "(без тексту — ціна в зображенні)",
        comments="\n".join(lines),
    )


def extractor_version(rendered: str) -> str:
    """sha256 of the rendered prompt — what `signal.extractor_version` carries."""
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def codebook_version() -> str:
    """sha256 of the LAW alone, so a codebook change is visible without a thread to render.

    Separate from :func:`extractor_version` on purpose: every thread renders a different prompt and
    therefore a different version, so a per-row version cannot answer "did the law move?".
    """
    return hashlib.sha256(CODEBOOK.encode("utf-8")).hexdigest()


def template_version() -> str:
    """sha256 of the TEMPLATE — the examples block included, because it is part of that string.

    Ruling 04.09 (g) item 3: `codebook_version` alone cannot separate two instruments that share a
    law and differ in what is rendered around it, and `extractor_version` is per THREAD, so neither
    answers «did the render move?» in a record. This does, and the registration carries it.
    """
    return hashlib.sha256(TEMPLATE.encode("utf-8")).hexdigest()


def vocabulary() -> dict:
    """The three closed lists, as the record writes them down beside a reading."""
    return {
        "subject_types": list(SUBJECT_TYPES),
        "signal_types": list(SIGNAL_TYPES),
        "attribution_sources": list(ATTRIBUTION_SOURCES),
        "codebook_sha256": codebook_version(),
    }


def unfence(answer: str) -> tuple[str, bool]:
    """The JSON inside a markdown fence, and whether there was one.

    The CODEBOOK asks for JSON and nowhere forbids a fence — `prompts.positions_messages_text_gm4`
    is the registration that does — and gemma-4 fenced every reply of iteration 1: ```` ```json ````
    then a complete object. Reading the fence off is not answer repair, which ruling 03.09 (c) item
    3 reserves for iterations 2–5: nothing inside the object is changed, added or closed, and an
    object that is malformed or was cut by the ceiling is still a parse failure counted by cause
    ([[empty_class_eats_the_parse_failures]]). The closing fence is usually absent — the balanced
    stop ends generation at the object's own last brace, so the trailing ```` ``` ```` is the four
    characters it cut.
    """
    text = answer.strip()
    if not text.startswith("```"):
        return answer, False
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return (body.rsplit("```", 1)[0] if body.rstrip().endswith("```") else body), True


def fold(rows: list) -> dict | None:
    """An ARRAY answer read as the rows it is — one element per comment — or `None`.

    The other half of ruling 04.09 (m). The codebook asks for JSON and fixes the KEYS, never the
    outer container, and iteration 2's `@VARUS_channel:6216` answered a list of `{"about": …,
    "signals": …, "unsure": …}` — one element per comment, `about` singular where the object shape
    carries a list. Reading it is not answer repair: no row is changed, added or closed, only the
    wrapper is dropped. `promo_dev_pod_runner.balanced_prefix` is the half that lets such an answer
    finish generating; this is the half that counts its rows.

    `None` — an element that is not an object — leaves the caller to count the answer as what it is
    ([[empty_class_eats_the_parse_failures]]): a list of strings is not three rows, it is a refusal
    of the shape, and folding it to an empty class would spend a paid reply on silence.
    """
    folded: dict[str, list] = {"about": [], "signals": [], "unsure": []}
    for row in rows:
        if not isinstance(row, dict):
            return None
        for key, out in folded.items():
            value = row.get(key)
            if value is not None:
                out.extend(value if isinstance(value, list) else [value])
    return folded


def parse(answer: str) -> dict:
    """The model's answer as a dict, or a counted parse failure — never an exception.

    An empty class eats parse failures when a refusal is silently read as "nothing found"
    ([[empty_class_eats_the_parse_failures]]), so an unparseable answer returns its own marked
    shape and the caller counts it as what it is.
    """
    body_text, fenced = unfence(answer)
    try:
        body = json.loads(body_text)
    except json.JSONDecodeError as bad:
        return {"about": [], "signals": [], "unsure": [], "fenced": fenced, "parse_failure": str(bad)}
    if isinstance(body, list):
        body = fold(body)
    if not isinstance(body, dict):
        return {
            "about": [], "signals": [], "unsure": [], "fenced": fenced,
            "parse_failure": "not an object",
        }
    return {
        "about": body.get("about") or [],
        "signals": body.get("signals") or [],
        "unsure": body.get("unsure") or [],
        "fenced": fenced,
        "parse_failure": None,
    }
