/**
 * The shell: the header banner, the two tab groups, and the route (DESIGN-ship-1 §4).
 *
 * One load at boot decides the mode and hands every tab the same two exports. A file that would
 * not load is the red panel of §5 with the file's name on it — the app refuses rather than
 * rendering a screen whose blanks a reader would take for readings.
 */

import { useEffect, useState } from 'react'

import { AppContext, applyLang, applyTheme, rememberLang, rememberTheme, rememberedLang, rememberedTheme } from './app-state.ts'
import type { App as AppData, ThemeChoice } from './app-state.ts'
import { chainTable } from './data/chains.ts'
import { SourceMissing, loadAll } from './data/load.ts'
import type { Mode } from './data/load.ts'
import { dataUntil } from './data/front.ts'
import { asDayMonth, positions } from './data/promo.ts'
import { count } from './format.ts'
import type { Lang } from './i18n/t.ts'
import { translator } from './i18n/t.ts'
import type { Translate } from './i18n/t.ts'
import { CC_TABS, hrefFor, paramOf, promoTabs, servedOnly, useRoute } from './router.ts'
import { SourceMissingPanel } from './components/SourceMissingPanel.tsx'
import { CommandCentreTab } from './tabs/CommandCentre.tsx'
import { LoopTab } from './tabs/Loop.tsx'
import { PositionsTab } from './tabs/Positions.tsx'
import { QualityTab } from './tabs/Quality.tsx'
import { ReactionsTab } from './tabs/Reactions.tsx'
import { RegionTab } from './tabs/Region.tsx'
import { TrendsTab } from './tabs/Trends.tsx'

type Boot =
  | { state: 'loading' }
  | { state: 'ready'; data: Omit<AppData, 'lang' | 't' | 'chains'> }
  | { state: 'failed'; error: SourceMissing | Error }

export function App(): React.JSX.Element {
  const route = useRoute()
  const [boot, setBoot] = useState<Boot>({ state: 'loading' })
  const [lang, setLang] = useState<Lang>(() => rememberedLang() ?? 'uk')
  const [theme, setTheme] = useState<ThemeChoice>(() => rememberedTheme())

  useEffect(() => {
    loadAll()
      .then((data) => setBoot({ state: 'ready', data }))
      .catch((error: unknown) =>
        setBoot({ state: 'failed', error: error instanceof Error ? error : new Error(String(error)) }),
      )
  }, [])

  useEffect(() => applyTheme(theme), [theme])
  useEffect(() => applyLang(lang), [lang])

  // a link may carry the language and the theme: `?lang=en&theme=dark` wins over what this browser
  // remembers, which is what makes a view — including the one a screenshot is taken of — a link
  const linkLang = paramOf(route, 'lang')
  const linkTheme = paramOf(route, 'theme')
  useEffect(() => {
    if (linkLang === 'uk' || linkLang === 'en') setLang(linkLang)
  }, [linkLang])
  useEffect(() => {
    if (linkTheme === 'light' || linkTheme === 'dark' || linkTheme === 'system') setTheme(linkTheme)
  }, [linkTheme])

  const t = translator(lang)

  if (boot.state === 'loading') return <main className="shell">…</main>
  if (boot.state === 'failed') {
    const file = boot.error instanceof SourceMissing ? boot.error.file : t('error.boot')
    const field = boot.error instanceof SourceMissing ? boot.error.field : undefined
    return (
      <main className="shell">
        <SourceMissingPanel t={t} file={file} {...(field === undefined ? {} : { field })} target="make front" />
      </main>
    )
  }

  const app: AppData = { ...boot.data, lang, t, chains: chainTable(boot.data.front) }
  const chooseLang = (next: Lang): void => {
    setLang(next)
    rememberLang(next)
  }
  const chooseTheme = (next: ThemeChoice): void => {
    setTheme(next)
    rememberTheme(next)
  }

  const windows = app.status.windows
  const banner = windows
    .map((one) => `${one.id} ${asDayMonth(one.since)}–${asDayMonth(one.until)}`)
    .join(' · ')
  const tick = app.status.tick.at

  return (
    <AppContext.Provider value={app}>
      <header className="top">
        <div className="shell">
          <h1>{t('app.name')}</h1>
          <p className="banner">
            {t('header.windows')}: <b>{banner}</b> — <b>{count(lang, positions(app.promo).length)}</b>{' '}
            {t('header.positions')}, <b>{count(lang, app.status.threads.read)}</b>{' '}
            {t('header.threads')}
            <br />
            {tick === null
              ? t('header.data_until', { date: dataUntil(app.front).date })
              : t('header.updated', { at: tick.slice(0, 16).replace('T', ' ') })}
          </p>
          <div className="top-controls">
            <span
              className="chip"
              title={t(app.mode === 'served' ? 'header.mode.served.title' : 'header.mode.static.title')}
            >
              {t(app.mode === 'served' ? 'header.mode.served' : 'header.mode.static')}
            </span>
            <span className="chip" role="group" aria-label={t('header.lang')}>
              <button type="button" aria-pressed={lang === 'uk'} onClick={() => chooseLang('uk')}>
                UA
              </button>
              <button type="button" aria-pressed={lang === 'en'} onClick={() => chooseLang('en')}>
                EN
              </button>
            </span>
            <button
              type="button"
              aria-label={t('header.theme')}
              onClick={() => chooseTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? t('header.theme.light') : t('header.theme.dark')}
            </button>
          </div>
        </div>
      </header>

      <nav className="tabs">
        <div className="shell">
          <div className="group" role="tablist" aria-label={t('nav.group.promo')}>
            <span>{t('nav.group.promo')}</span>
            {promoTabs(app.mode).map((tab) => (
              <a
                key={tab}
                role="tab"
                href={hrefFor(`/promo/${tab}`)}
                aria-current={route.path === `/promo/${tab}` ? 'page' : undefined}
              >
                {t(`nav.promo.${tab}`)}
              </a>
            ))}
          </div>
          <div className="group" role="tablist" aria-label={t('nav.group.cc')}>
            <span>{t('nav.group.cc')}</span>
            {CC_TABS.map((tab) => (
              <a
                key={tab}
                role="tab"
                href={hrefFor(`/cc/${tab}`)}
                aria-current={route.path === `/cc/${tab}` ? 'page' : undefined}
              >
                {t(`nav.cc.${tab}`)}
              </a>
            ))}
          </div>
        </div>
      </nav>

      <main className="shell">
        <Tab path={route.path} mode={app.mode} t={t} />
      </main>
    </AppContext.Provider>
  )
}

function Tab({ path, mode, t }: { path: string; mode: Mode; t: Translate }): React.JSX.Element {
  // the STATIC build does not ship Якість, and a link to it is answered by the sentence that says
  // where the tab is — not by the tab, and not by a blank (DESIGN-ship-1 §11, §10)
  if (servedOnly(path, mode)) {
    return (
      <>
        <h2 className="question">{t('quality.served_only')}</h2>
        <p className="population">{t('quality.served_only.hint')}</p>
      </>
    )
  }
  switch (path) {
    case '/promo/positions':
      return <PositionsTab />
    case '/promo/trends':
      return <TrendsTab />
    case '/promo/reactions':
      return <ReactionsTab />
    case '/promo/region':
      return <RegionTab />
    case '/promo/quality':
      return <QualityTab />
    case '/promo/loop':
      return <LoopTab />
    default:
      return <CommandCentreTab path={path} />
  }
}
