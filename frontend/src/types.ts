/**
 * The shapes of the two exports the app reads — written FROM the files, not from memory
 * (DESIGN-ship-1 §2). A field the producers omit when a row does not carry it is optional here and
 * never `| null`: `src/market_pulse/aggregates.py :: promo_positions` says an absent field is
 * ABSENT, because `0` would claim the badge was printed as zero.
 *
 * `command_center` is typed only as deeply as the promo half reads it — front-2 puts the command
 * centre on the app and types the rest of that record then.
 */

export interface Window {
  id: string
  anchor: string
  days: number
  since: string
  until: string
}

export interface Brand {
  display: string
  id?: string
  own?: boolean
}

export interface PositionItem {
  category: string
  line?: string
  size_value?: number
  size_unit?: string
  pack_count?: number
  attribute_pct?: number
}

export interface Position {
  row_id: string
  tier: string
  carrier: string
  brand: Brand
  chain: { id: string; named_by_amendment_3_20: boolean }
  item: PositionItem
  evidence: { channel: string; msg_id: number }
  /** the PRINTED badge's own reading, absent when no badge was printed */
  depth?: number
  printed_pct?: number
  promo_price?: number
}

export interface RollupRow {
  brand: string
  chain: string
  metric: string
  value: number
  week: string
}

export interface DepthRow {
  brand: string
  chain: string
  depth_mean: number
  week: string
}

export interface FeedRow {
  channel: string
  msg_id: number
  quote: string
  thread_root: number
  type: string
}

export interface Threads {
  from: string
  population: number
  product_population: number
  queue: number
  read: number
  not_collected: number
  read_threads: string[]
}

export type TableRows = Record<string, number>

export interface PromoExport {
  contract: string
  window_id: string
  windows: Window[]
  not_collected: { channels: string[]; position_rows: number }
  screen: {
    positions: Position[]
    rollup: RollupRow[]
    weeks: string[]
    depth_by_chain_and_brand: DepthRow[]
    feed: FeedRow[]
    threads: Threads
    table_rows: TableRows
  }
}

export interface Bar {
  bar: number
  held: boolean
  value: number
}

export interface S2Row {
  label: string
  file: string
  block: string
  bars: { subject_agreement: Bar; signal_type_agreement: Bar }
  agreed: number
  comments: number
  misses: { total: number; gold_unsure: number; rule: string } | null
}

export interface GradeRecord {
  contract: string
  gold: string
  predicted: string
  match_rule: string
  bars: {
    completeness: { bar: number; gold: number; held: boolean; matched: number; value: number }
    price_accuracy: {
      bar: number
      denominator: string
      held: boolean
      right: number
      scored: number
      value: number
    }
  }
  readings: {
    gold_rows_no_prediction_reached: number
    predicted_rows_no_gold_row_claims: number
    price_old: { agree: number; n: number; note: string }
    printed_badge: { agree: number; n: number; note: string }
  }
}

export interface S1Reading {
  from: string
  /** null when the grade file is not in this checkout — `why` says which file would carry it */
  reading: GradeRecord | null
  why?: string
  draw?: { from: string; pages: number; population: number; rows_drawn: number; seed: number }
}

export interface MoneyReading {
  from: string
  remaining_usd: number
  spent_usd: number
  cap_usd: number
  at: string
  note: string
}

/**
 * The tick, as the two modes answer it: the state file's own counters when a tick has run, or
 * `at: null` beside the sentence that says which file would carry one.
 */
export interface TickReading {
  at: string | null
  why?: string
  new_rows?: TableRows
  table_rows?: TableRows
  schedule?: string
}

export interface Status {
  tick: TickReading
  threads: Threads
  table_rows: TableRows
  money: MoneyReading
  window_id: string
  from: string
  windows: Window[]
}

export interface Schedule {
  min_interval_hours: number
  default_interval_hours: number
  note?: string
}

export interface Conclusion {
  id: string
  ua: string
  en: string
  stands_on: string[]
}

export interface MetricEntry {
  id: string
  name: { ua: string; en: string }
  definition: { ua: string; en: string }
  formula: string
  how_to_read: { ua: string; en: string }
  pitfalls: { ua: string[]; en: string[] }
}

export interface CommandCentre {
  contract: string
  phase: string
  conclusions: Conclusion[]
  window: Window & { populations: Record<string, number>; reading: string; rule: string }
  metrics: Record<string, unknown>
  cuts: Record<string, unknown>
  not_computable: Record<string, unknown>
  promo: Record<string, unknown>
  provenance: Record<string, unknown>
  convergence: Record<string, unknown>
  dictionary: { metrics: string[]; path: string; sha256: string }
}

export interface ChainRow {
  id: string
  name: string
  source_type: string
}

/** One chain's newest flyer set: the staged page names, the dates those pages carry, and how many
 *  positions were read off them (`export_front_data.media`, DESIGN-ship-1 §11). */
export interface FlyerSet {
  chain: string
  week: string
  since: string
  until: string
  pages: string[]
  positions: number
  cover: string
}

export interface MediaFile {
  name: string
  file: string
  bytes: number
}

export interface MediaBlock {
  from: string
  reading: string
  /** the directory `make front` stages the photos into, under the app's own root */
  dir: string
  /** `"<channel>:<msg_id>"` → the staged name of the page that position was read off */
  pages: Record<string, string>
  flyers: FlyerSet[]
  /** the staging list — what the build copies, and the only names the app may reference */
  files: MediaFile[]
  rows_without_a_page: number
  pages_without_a_date: number
}

/** What a human changed on this row and against which page — the record of
 *  `config/price_corrections.yaml`, applied by `export_front_data.page_true` (ruling (yy) 13.09).
 *  `was` carries the figures it replaced, so the card can say WHAT moved and not only that
 *  something did; `exclude` marks a row whose page prints no price at all. */
export interface Correction {
  from: string
  page: string
  verified_by: string[]
  was: { promo_price?: number; size_value?: number }
  exclude?: string
}

/** One position as a card: what it is, what it costs, and the page it was read off. The optional
 *  fields are the row's own absences — a pack with no printed badge has no `printed_pct`, and a row
 *  whose photo never arrived has no `page`, which is a sentence the card says rather than a hole. */
export interface PriceCard {
  row_id: string
  brand: string
  category: string
  chain: string
  chain_name: string
  channel: string
  msg_id: number
  line?: string
  size_value?: number
  size_unit?: string
  pack_count?: number
  promo_price?: number
  printed_pct?: number
  /** `uah_per_kg` or `uah_per_l` — absent together with `unit_price` when the row carries no size */
  unit?: string
  unit_price?: number
  page?: string
  /** present only on the rows a human corrected against the leaflet page */
  correction?: Correction
}

/** One category read in ONE unit. Never pooled across units: a category holding both grams and
 *  millilitres has no single median, so the producer cuts it in two and the app shows both. */
export interface CategoryBasis {
  unit: string
  n: number
  min: number | null
  median: number | null
  max: number | null
  q1: number | null
  q3: number | null
  cheapest: PriceCard
  dearest: PriceCard
}

/** A category of `config/registry.yaml :: taxonomy.tracked_groups`, present whether or not the
 *  market promoted it this window — `bases: []` is «немає в даних», never a zero. */
export interface CategoryPrices {
  category: string
  name: string
  group: string
  /** set on the two keys that are also parents — `dairy` labels the rows whose subcategory was
   *  not printed, so the app must not let it read as the dairy total */
  is_group_key?: boolean
  /** every row of the category, priced or not: the gap to `bases[].n` is the unpriced remainder */
  positions: number
  bases: CategoryBasis[]
}

export interface CategoryPricesBlock {
  from: string
  reading: string
  /** the rows of the window the block reads — every chain's current leaflet week */
  positions: number
  rows_without_a_unit_price: number
  /** the rows of that window whose own page prints NO price: they stay in `positions` and are
   *  counted here instead of being priced, because a row quietly dropped is a population that
   *  moved without a sentence */
  excluded: {
    n: number
    from: string
    reading: string
    rows: { row_id: string; carrier: string; category: string; why: string }[]
  }
  categories: CategoryPrices[]
}

/** One chain of a regional cut, on its own current week — or `absent`, naming why it carries no
 *  week at all. A chain with no flyer set is a different state from a chain with an empty one. */
export interface RegionChain {
  chain: string
  name: string
  absent?: string
  week?: string
  since?: string
  until?: string
  positions?: PriceCard[]
}

export interface RegionCut {
  region: string
  name: string
  chains: RegionChain[]
}

/** The operator's regional cuts. A selection of CHAINS, not a geography of rows: the registry
 *  carries no region, and `reading` is the sentence that says so on the screen. */
export interface RegionsBlock {
  from: string
  reading: string
  cuts: RegionCut[]
}

export interface FrontExport {
  contract: string
  chains: {
    from: string
    reading: string
    rows: ChainRow[]
    /** a telegram handle → the chain id `rows` names, so a block keyed on handles (the rollup)
     *  can be labelled with the same name a block keyed on chain ids (the positions) shows */
    by_channel: Record<string, string>
  }
  data_until: { date: string; from: string }
  command_center: CommandCentre
  model: { from: string; verdict: Record<string, unknown> }
  s2_readings: S2Row[]
  /** `build_promo_screen.S2_BOUNDARY` — the one sentence that separates the shipped row from
   *  the readings under it, defined once in Python and rendered wherever the table is */
  s2_boundary: string
  media: MediaBlock
  category_prices: CategoryPricesBlock
  regions: RegionsBlock
  s1_reading: S1Reading
  status: Status
  dictionary: { from: string; sha256: string; metrics: MetricEntry[] }
  sources: Record<string, { sha256: string; bytes: number }>
}
