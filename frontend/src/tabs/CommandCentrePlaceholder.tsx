/**
 * Командний центр — the honest stand-in every `#/cc/*` route renders until front-2 builds the
 * nine tabs (DESIGN-ship-1 §7 T0–T8, §10: never an empty state without a sentence).
 *
 * It reads ONE block, `front_data.json :: command_center.conclusions` — the three readings
 * `build_dashboard.py`'s own rule generated over the window — and renders each in the reader's
 * language with the metric paths it stands on beneath it.
 *
 * What it refuses: it computes nothing and fetches nothing; it shows no figure of its own, so no
 * KPI card here claims a reading front-2 has not built; it invents no content for the tab the
 * reader asked for beyond that tab's NAME; and a hash outside {@link CC_TABS} gets the placeholder's
 * own title instead of a blank screen — a blank where a tab belongs reads as «this tab is empty».
 */

import { useApp } from '../app-state.ts'
import { conclusions } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { CC_TABS } from '../router.ts'

/** `front.ts` inlines this path in its own `must()` call and exports no constant for it. */
const CONCLUSIONS_FIELD = 'command_center.conclusions'

const CC_PREFIX = '/cc/'

/**
 * The command-centre tab a path asks for, or undefined. App.tsx routes EVERY unmatched path here,
 * so a hand-typed `#/cc/t9` and a `#/nonsense` both arrive and neither names a tab.
 */
function ccTabOf(path: string): (typeof CC_TABS)[number] | undefined {
  if (!path.startsWith(CC_PREFIX)) return undefined
  const id = path.slice(CC_PREFIX.length)
  return CC_TABS.find((tab) => tab === id)
}

export function CommandCentrePlaceholder({ path }: { path: string }): React.JSX.Element {
  const { front, lang, t } = useApp()
  const tab = ccTabOf(path)
  const rows = conclusions(front)

  return (
    <>
      <h2 className="question">{t('cc.placeholder.title')}</h2>
      <p className="population">{tab === undefined ? t('cc.placeholder.title') : t(`nav.cc.${tab}`)}</p>
      <p>{t('cc.placeholder.body')}</p>

      <section className="block">
        <h2>{t('cc.placeholder.conclusions')}</h2>
        {rows.length === 0 ? (
          <p className="muted">{t('common.absent')}</p>
        ) : (
          <ol className="rows">
            {rows.map((row) => (
              <li key={row.id}>
                {lang === 'uk' ? row.ua : row.en}
                <p className="pair">
                  {row.stands_on.map((field) => (
                    <code key={field}>{field}</code>
                  ))}
                </p>
              </li>
            ))}
          </ol>
        )}
      </section>

      <p className="sources">
        {t('common.sources')}: <code>{FRONT_FILE} :: {CONCLUSIONS_FIELD}</code>
      </p>
    </>
  )
}
