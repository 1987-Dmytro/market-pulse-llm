/**
 * Colour follows the ENTITY: a chain keeps its slot across every tab (DESIGN-ship-1 §3, §6).
 *
 * The slots are the brief's own eight, by chain id, assigned ONCE here. Everything else is data:
 * the display NAME of a chain comes from `front_data.json :: chains` — the registry's own rows,
 * folded exactly as the screen folded them — so a chain the registry renames is renamed on the
 * app too, and no label is typed twice.
 */

import type { FrontExport } from '../types.ts'

/** The brief's fixed order. A chain outside it folds into «інші» in charts and stays named in
 *  tables — a ninth colour would break the validated all-pairs palette. */
export const SLOTS: readonly string[] = [
  'atb',
  'varus',
  'silpo',
  'marketopt_promo',
  'forainfo',
  'blyzenko',
  'ekomarket_shop',
  'epicentrk_sale',
]


/** 1-based series slot, or 0 for «інші» — the CSS variable is `--s<slot>`. */
export function slotOf(chainId: string): number {
  const index = SLOTS.indexOf(chainId)
  return index === -1 ? 0 : index + 1
}

export function seriesColour(chainId: string): string {
  const slot = slotOf(chainId)
  return slot === 0 ? 'var(--text-3)' : `var(--s${slot})`
}


export interface ChainName {
  id: string
  name: string
  source_type: string
}

export function chainTable(front: FrontExport): Map<string, ChainName> {
  const rows = front.chains?.rows ?? []
  return new Map(rows.map((row) => [row.id, row]))
}

/**
 * The name to print for a chain id. A chain the table does not carry keeps the EXPORT's own id:
 * an invented display name would be a label no file holds.
 */
export function chainName(table: Map<string, ChainName>, chainId: string): string {
  return table.get(chainId)?.name ?? chainId
}

/** Chain ids in the brief's slot order first, then the rest alphabetically — one stable order. */
export function orderChains(ids: Iterable<string>): string[] {
  return [...new Set(ids)].sort((left, right) => {
    const [a, b] = [slotOf(left), slotOf(right)]
    if (a !== b) return (a === 0 ? Number.MAX_SAFE_INTEGER : a) - (b === 0 ? Number.MAX_SAFE_INTEGER : b)
    return left.localeCompare(right, 'uk')
  })
}

/**
 * A colour for a series the slot table cannot name — the rollup's rows key on the CHANNEL handle
 * (`@atb_market_official`), not on a folded chain id, so those charts colour by position in their
 * own ordered list. Past the eighth series the palette is exhausted and the mark goes recessive.
 */
export function colourByIndex(index: number): string {
  return index < 8 ? `var(--s${index + 1})` : 'var(--text-3)'
}
