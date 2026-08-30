#!/usr/bin/env python3
"""C1 r2 step 1 — the chains' OWN sites are the instrument, not Telegram's name search.

r1 asked Telegram "who is called METRO?" and got METRO Russia, an ISP «Копійка» and an ОСББ
«Барвінок» (Dv871): the instrument was wrong for the question. A chain's official channel is
linked from the chain's own footer, so this pass reads the footer and extracts every `t.me/` link.

Two failure modes are kept apart, because collapsing them would read as an answer:
  `no-link`  — the page was READ and carries no `t.me/` link. A fact about the chain.
  `blocked` / `dns` / `error` — the page was never read. A fact about the fetch.
`method` (`curl` | `browser`) is a column for the same reason r1 kept `api` vs `store`: a page
rendered by JavaScript has no footer in its HTML, and a row fetched the cheap way is not the
same reading as a row a browser rendered.

$0, read-only, HTTP only — CLAUDE.md allows HTTP for DISCOVERY of official handles.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from discover_channels import RETAIL_CHAINS  # noqa: E402  the 35 names of SPEC v2 §3 category A

RECORD = REPO_ROOT / "results" / "retail_chains.json"

# The candidate domains named in docs/PROMPT-retail-census-r2.md, mapped onto the SPEC §3 names.
# `epicentrk.ua` is in the contract's list and matches NO name in RETAIL_CHAINS — it is carried as
# its own row, flagged, rather than dropped or silently counted as one of the 35 (Dv880).
DOMAINS = {
    "АТБ": "atbmarket.com",
    "Сільпо": "silpo.ua",
    "Novus": "novus.ua",
    "METRO": "metro.ua",
    "Auchan": "auchan.ua",
    "Фора": "fora.ua",
    "Varus": "varus.ua",
    "Thrash!": "thrash.ua",
    "Fozzy": "fozzyshop.ua",
    "ЕКО маркет": "eko.com.ua",
    "Велмарт": "velmart.ua",
    "Близенько": "blyzenko.ua",
    "Наш Край": "nashkraj.ua",
    "Рукавичка": "rukavychka.ua",
    "Коло": "kolo.ua",
    "Delikat": "delikat.ua",
    "Сім23": "sim23.ua",
    "Копійка": "kopiyka.ua",
    "Таврія В": "tavriav.ua",
    "Ультрамаркет": "ultramarket.ua",
    "MegaMarket": "megamarket.ua",
    "Zakaz.ua": "zakaz.ua",
    "Маркетопт": "marketopt.ua",
    "Грош": "grosh.ua",
}
EXTRA_DOMAINS = {"Епіцентр [not in SPEC §3 A]": "epicentrk.ua"}

# Names with no domain in the contract. Aggregators are answered from r1's Telegram measurement
# (the contract says so); the five chains below have no verified site yet — `--probe` tries the
# obvious spellings and only a resolving page that names the chain is ever written down.
AGGREGATORS = {"MSUa", "Копійочка", "Знижком", "Хочу дешевше", "Акції та знижки", "Skidka"}

PROBE_GUESSES = {
    "Rozetka продукти": ["rozetka.com.ua"],
    "Толока": ["toloka.ua", "toloka.com.ua"],
    "Гурман": ["gurman.ua", "gurman.poltava.ua"],
    "Файно маркет": ["fayno-market.ua", "faynomarket.ua", "fayno.market"],
    "Барвінок": ["barvinok.ua", "barvinok-market.com.ua"],
    # Found by web discovery after the contract's own candidates failed DNS (CLAUDE.md allows HTTP
    # for DISCOVERY of official handles). A candidate still has to answer AND name the chain.
    "Delikat": ["delikat.site", "delikat.online"],
    "Маркетопт": ["marketopt.com.ua", "marketopt.ua"],
}

# What the discovery established for a name that ends with no site. Written into the row so the
# record carries the reason, not just the report: «no site verified» is one word for several very
# different states, and one of these names is not a live chain at all.
DISCOVERY_NOTES = {
    "Барвінок": (
        "the retail brand no longer exists: the chain was sold in December 2015 and bought by"
        " ATB-Market in 2016, and every «Барвінок» store was rebranded to «АТБ». This is why r1's"
        " name search returned an ОСББ «Барвінок» — there is no retail channel to find."
    ),
    "Толока": (
        "web discovery finds no retail chain of this name; «толока» is the Ukrainian word for a"
        " community work-day, which is what the searches return. SPEC v2 §3 pairs it with"
        " «Маркетопт»; the pairing is not visible in any source found."
    ),
    "Гурман": (
        "no Poltava-region chain with a site: the name belongs to a shop in Південне (Instagram"
        " only) and to gurman-dnepr.com.ua in Dnipro. `gurman.ua` is a domain-for-sale page."
    ),
    "Маркетопт": (
        "a real Poltava chain with NO website — its official presence is Instagram @marketopt and"
        " Facebook @marketopt.official. `marketopt.ua` does not resolve. Absence of a site is not"
        " absence of the chain, and this row cannot be answered by reading a footer."
    ),
}

# Footer and social blocks live on the home page on most of these sites; contacts pages carry
# them when the home page is a rendered shell. Kept short: every extra path is another request.
PATHS = ("/", "/contacts", "/about")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = [
    "-H",
    f"User-Agent: {UA}",
    "-H",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "-H",
    "Accept-Language: uk-UA,uk;q=0.9,en;q=0.8",
    "-H",
    "Sec-Fetch-Mode: navigate",
    "-H",
    "Upgrade-Insecure-Requests: 1",
]

LINK_RE = re.compile(r"(?:https?://)?t\.me/(\+[A-Za-z0-9_-]+|[A-Za-z0-9_][A-Za-z0-9_]{3,31})", re.I)
# `t.me/share/url?...` is a share widget, never a channel; `t.me/iv` is instant view.
NOT_A_CHANNEL = {"share", "iv", "joinchat", "addstickers", "proxy", "socks", "s"}


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def kind_of(token: str) -> str:
    """What a `t.me/` target actually is. Step 2 can only resolve `channel` and `invite`.

    `t.me/+380675178085` is a phone deep link ("write to us on Telegram"), NOT a group invite —
    it has no username to resolve and no history to measure. Counting it as an invite would put a
    support phone number in the census's resolve budget and score it as a chain's channel.

    Telegram reserves every username ending in `bot` for bots, with or without the underscore:
    `@VelmartUaBot` and `@sim23_chatbot` are bots that an `_bot` suffix test calls channels. The
    resolve in step 2 is the judge either way — a bot comes back a User, not a Channel — so this
    only decides who is worth spending a request on.
    """
    if token.startswith("+"):
        return "contact" if token[1:].isdigit() else "invite"
    return "bot" if token.lower().endswith("bot") else "channel"


def extract(html: str) -> list[str]:
    """Every `t.me/` target on the page, deduped, share widgets and instant-view dropped."""
    out: list[str] = []
    for hit in LINK_RE.findall(html):
        if hit.lower() in NOT_A_CHANNEL:
            continue
        token = hit if hit.startswith("+") else f"@{hit}"
        if token not in out:
            out.append(token)
    return out


def set_handles(row: dict, links: list[str]) -> None:
    """Handles and what each one IS — a chain whose only link is a `_bot` has no channel to collect."""
    row["handles"] = links
    row["kinds"] = {token: kind_of(token) for token in links}
    row["resolvable"] = [t for t in links if kind_of(t) in ("channel", "invite")]


def fetch(url: str, timeout: int = 25) -> tuple[int, str]:
    """(http status, body). Status 0 means the request never produced a response at all."""
    proc = subprocess.run(
        [
            "curl",
            "-sL",
            "--compressed",
            "--max-time",
            str(timeout),
            *HEADERS,
            "-w",
            "\n%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
        errors="replace",
    )
    if proc.returncode != 0:
        return 0, proc.stderr.strip()[:200]
    body, _, code = proc.stdout.rpartition("\n")
    return int(code or 0), body


def read_site(domain: str, *, pause: float = 1.0) -> dict:
    """Read a domain's home page and its contact pages; classify what came back."""
    pages, links, statuses = [], [], []
    for path in PATHS:
        url = f"https://{domain}{path}"
        code, body = fetch(url)
        found = extract(body) if code == 200 else []
        pages.append({"url": url, "http": code, "bytes": len(body), "links": found})
        statuses.append(code)
        for token in found:
            if token not in links:
                links.append(token)
        time.sleep(pause)  # polite: these are somebody's production sites
    sizes = {p["bytes"] for p in pages if p["http"] == 200}
    if links:
        status = "ok"
    elif 200 in statuses and len(sizes) == 1 and len([p for p in pages if p["http"] == 200]) > 1:
        # Every path returned the same bytes: one client-rendered shell, not three pages. The
        # footer is built by JavaScript, so curl never saw it — this is NOT "the chain has no
        # channel", it is "this instrument cannot read this site". Dv871 recurring in a new tool.
        status = "shell"
    elif 200 in statuses:
        status = "no-link"  # a page WAS read and carries no t.me link — a fact about the chain
    elif 403 in statuses or 503 in statuses:
        status = "blocked"  # never read: bot protection. A fact about the fetch, not the chain
    elif set(statuses) == {0}:
        status = "dns"
    else:
        status = "error"
    return {"domain": domain, "status": status, "method": "curl", "links": links, "pages": pages}


ASSET_RE = re.compile(r"""<(?:script[^>]+src|link[^>]+href)=["']([^"']+\.js[^"']*)["']""", re.I)


def read_assets(domain: str, *, cap: int = 20) -> dict:
    """The footer a `shell` or `no-link` page never rendered is still IN the bundle that renders it.

    A client-rendered site serves an empty shell to curl, so `no t.me link` from the HTML is a
    statement about the fetch, not about the chain. The links themselves are compiled into the
    JavaScript, which is plain HTTP and needs no browser permission. This reads the shell, follows
    its own `<script src>` tags, and greps those — an instrument for the sites the cheap one cannot
    read, kept apart from it by `method: curl+bundle`.
    """
    code, body = fetch(f"https://{domain}/")
    if code != 200:
        return {"status": "blocked", "links": [], "assets": []}
    urls, seen = [], set()
    for src in ASSET_RE.findall(body):
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = f"https://{domain}{src}"
        elif not src.startswith("http"):
            continue
        if src not in seen:
            seen.add(src)
            urls.append(src)
    links, assets = [], []
    for url in urls[:cap]:
        acode, abody = fetch(url, timeout=30)
        found = extract(abody) if acode == 200 else []
        assets.append({"url": url, "http": acode, "bytes": len(abody), "links": found})
        for token in found:
            if token not in links:
                links.append(token)
        time.sleep(0.3)
    return {
        "status": "ok" if links else "no-link-in-bundle",
        "links": links,
        "assets": assets,
        "n_scripts_seen": len(urls),
    }


def run_deep(names: list[str] | None) -> int:
    """Second instrument over the rows the first one could not read."""
    state = load()
    by_name = {row["name"]: row for row in state["rows"]}
    targets = names or [
        r["name"] for r in state["rows"] if r.get("site_status") in ("shell", "no-link", "blocked")
    ]
    for name in targets:
        row = by_name[name]
        if not row.get("site"):
            continue
        read = read_assets(row["site"])
        row["bundle"] = {
            "status": read["status"],
            "n_scripts": read.get("n_scripts_seen", 0),
            "assets": read["assets"],
        }
        if read["links"]:
            row["site_status"] = "ok"
            row["method"] = "curl+bundle"
            set_handles(row, read["links"])
        print(
            f"{name:24} {row['site']:18} {read['status']:18} "
            f"{len(read['assets'])} assets  {' '.join(read['links']) or '—'}"
        )
    state["rows"] = [by_name[r["name"]] for r in state["rows"]]
    state["step_1"]["bundle_pass_at"] = stamp()
    save(state)
    return 0


def blank_row(name: str) -> dict:
    return {
        "name": name,
        "site": None,
        "site_status": "no-site-in-contract",
        "method": None,
        "handles": [],
        "kinds": {},
        "resolvable": [],
        "pages": [],
        "in_spec_a": name in RETAIL_CHAINS,
        "is_aggregator": name in AGGREGATORS,
    }


def load() -> dict:
    if RECORD.exists():
        return json.loads(RECORD.read_text(encoding="utf-8"))
    return {"rows": [], "step_1": {}, "step_2": {}}


def save(state: dict) -> None:
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_fetch(only: list[str] | None) -> int:
    state = load()
    by_name = {row["name"]: row for row in state.get("rows", [])}
    names = list(RETAIL_CHAINS) + list(EXTRA_DOMAINS)
    domains = {**DOMAINS, **EXTRA_DOMAINS}
    for name in names:
        # The row is built for every name even when --only narrows the fetch: a name without a row
        # would drop out of the record silently, and 35 rows is the deliverable's shape.
        row = by_name.get(name) or blank_row(name)
        by_name[name] = row
        if only and name not in only:
            continue
        domain = domains.get(name)
        if not domain:
            if name in AGGREGATORS:
                row["site_status"] = "aggregator — answered from r1's Telegram measurement"
            continue
        read = read_site(domain)
        row.update(
            site=domain,
            site_status=read["status"],
            method=read["method"],
            pages=read["pages"],
        )
        set_handles(row, read["links"])
        print(f"{name:24} {domain:20} {read['status']:9} {' '.join(read['links']) or '—'}")
    state["rows"] = [by_name[n] for n in names]
    state["step_1"] = {
        "at": stamp(),
        "paths": list(PATHS),
        "names_source": "scripts/discover_channels.py :: RETAIL_CHAINS (SPEC v2 §3 category A)",
        "n_names": len(RETAIL_CHAINS),
        "extra_domains": EXTRA_DOMAINS,
    }
    save(state)
    print(f"\nwrote {RECORD.relative_to(REPO_ROOT)} — {len(state['rows'])} rows")
    return 0


def names_the_chain(body: str, name: str) -> bool:
    """Does this page belong to the chain, or merely answer on the guessed domain?

    `gurman.ua` returns HTTP 200 with «Это доменное имя продается» — a parking page. A probe that
    accepts any 200 writes that into the census as «Гурман's site carries no Telegram link», which
    is a fact about a domain squatter dressed as a fact about a chain. The contract says: verify
    the domain is the chain's, never invent one.
    """
    low = body.lower()
    tokens = [w for w in re.split(r"[^\w']+", name) if len(w) >= 4 and w.lower() != "маркет"]
    return any(token.lower() in low for token in tokens)


def run_probe() -> int:
    """The five names with no contract domain: try the obvious spellings, write only what answers."""
    state = load()
    by_name = {row["name"]: row for row in state.get("rows", [])}
    for name, guesses in PROBE_GUESSES.items():
        row = by_name.get(name) or blank_row(name)
        by_name[name] = row
        if row.get("handles") or row.get("site_status") in ("ok", "no-link"):
            # This row already has a reading — from curl, from the bundle, or from the browser.
            # The probe's job is to FIND a site for a name that has none; letting its else-branch
            # run here rewrites `@rrozetka` (read in Chrome) as «no site verified», which is a
            # downgrade dressed as a measurement.
            print(f"{name:20} already read ({row.get('site_status')}) — probe skipped")
            continue
        tried = []
        for domain in guesses:
            code, body = fetch(f"https://{domain}/")
            mine = code == 200 and names_the_chain(body, name)
            tried.append(
                {"domain": domain, "http": code, "bytes": len(body), "names_the_chain": mine}
            )
            print(f"{name:20} {domain:24} http={code} bytes={len(body)} is-the-chain={mine}")
            if code == 200 and mine:
                read = read_site(domain)
                row.update(
                    site=domain,
                    site_status=read["status"],
                    method="curl",
                    pages=read["pages"],
                )
                set_handles(row, read["links"])
                break
            time.sleep(1.0)
        else:
            row["site_status"] = "no-site-verified"
        if row["site_status"] == "no-site-verified" and name in DISCOVERY_NOTES:
            row["no_site_reason"] = DISCOVERY_NOTES[name]
        row["probed"] = tried
    state["rows"] = [by_name[r["name"]] for r in state["rows"]]
    save(state)
    return 0


def run_merge(path: Path) -> int:
    """Merge a browser pass: {name: {url, links, note}}. Browser rows overwrite curl rows and say so."""
    incoming = json.loads(path.read_text(encoding="utf-8"))
    state = load()
    by_name = {row["name"]: row for row in state["rows"]}
    for name, found in incoming.items():
        row = by_name[name]  # KeyError is the right failure: a name the census does not carry
        links = found.get("links", [])
        set_handles(row, links)
        row["site_status"] = "ok" if links else "no-link"
        row["method"] = "browser"
        row["pages"] = row.get("pages", []) + [
            {
                "url": found["url"],
                "http": 200,
                "rendered": True,
                "links": links,
                "note": found.get("note", ""),
            }
        ]
        print(f"{name:24} browser  {' '.join(links) or '—'}")
    state["rows"] = [by_name[r["name"]] for r in state["rows"]]
    state["step_1"]["browser_pass_at"] = stamp()
    save(state)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="C1 r2 step 1 — t.me links from the chains' own sites.")
    p.add_argument("--fetch", action="store_true", help="curl pass over the contract's domains")
    p.add_argument("--only", nargs="*", help="restrict --fetch to these names (the control run)")
    p.add_argument(
        "--deep",
        nargs="*",
        help="follow the page's own JS bundles — the shell/no-link/blocked rows",
    )
    p.add_argument(
        "--probe", action="store_true", help="try domains for the names the contract omits"
    )
    p.add_argument("--merge-browser", type=Path, help="merge a rendered-page pass from Chrome")
    args = p.parse_args(argv)
    if args.merge_browser:
        return run_merge(args.merge_browser)
    if args.deep is not None:
        return run_deep(args.deep or None)
    if args.probe:
        return run_probe()
    if args.fetch:
        return run_fetch(args.only)
    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
