/**
 * The red panel of DESIGN-ship-1 §5: the file, the field, and the make target that writes it.
 *
 * The rest of the tab still renders around it. A blank in the place of a figure would read as
 * «none in the market» — a claim about the market that no file made.
 */

import type { Translate } from '../i18n/t.ts'

export interface SourceMissingPanelProps {
  t: Translate
  file: string
  field?: string
  /** the command that writes the file — `make front`, `make tick` */
  target: string
}

export function SourceMissingPanel({
  t,
  file,
  field,
  target,
}: SourceMissingPanelProps): React.JSX.Element {
  return (
    <section className="missing" role="alert">
      <h3>{t('error.source_missing', { file: field === undefined ? file : `${file} :: ${field}` })}</h3>
      <p>{t('error.source_missing.hint', { target })}</p>
    </section>
  )
}
