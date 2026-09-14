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
  /** present only on the rows a human corrected against the leaflet page — the sealed screen
   *  export carries none of these; they arrive on `front_data.json :: positions.rows` */
  correction?: Correction
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

/** The population a reading was taken over, and the file's own sentence about what it is. Every
 *  figure of the command centre carries one: «5075» means nothing until it says «of what». */
export interface Sample {
  name: string
  reading: string
  rows?: number
  of?: number
  share?: number
  watchlist_rules?: string
}

/** Readings by population, with the file naming which one is the headline. The app never picks:
 *  `headline_sample` is the producer's ruling and the other reading stays visible. */
export interface SampledOf<T> {
  by_sample: Record<string, T>
  headline_sample: string
}

/** A METRIC read that way — the same shape plus the population's own sentence. */
export interface Sampled<T> extends SampledOf<T> {
  sample: Sample
}

export interface Volume {
  comments: { bought: number; payable: number; text_less: number }
  leaflet_pages: number
  position_rows: number
  post_texts: number
  sample: Sample
}

export interface NsrReading {
  negative: number
  neutral: number
  positive: number
  nsr: number
  scored: number
  sample: Sample
}

export interface NegativeShareReading {
  negative: number
  negative_share: number
  negative_share_sarcasm_adjusted: number
  reclassified_from_sarcasm: number
  scored: number
  sample: Sample
}

export interface SovReading {
  mentions: Record<string, number>
  share: Record<string, number>
  own_brands: string[]
  total_mentions: number
  watchlist_rules: string
  sample: Sample
}

export interface AspectReading {
  labels: Record<string, number>
  share: Record<string, number>
  rows_with_no_aspect: number
  total_labels: number
  scored: number
  sample: Sample
}

/** n + the five points of `aggregates.spread`/`quartiles` — null where the population is empty. */
export interface Spread {
  n: number
  min: number | null
  q1: number | null
  median: number | null
  q3: number | null
  max: number | null
}

export interface DepthCarrier {
  from_price_pair: Spread
  from_printed_badge: Spread
  position_rows: number
  printed_disagrees_with_computed: number
}

export interface PromoDepth {
  by_carrier: Record<string, DepthCarrier>
  law: string
  printed_disagrees_with_computed: number
  readings: { from_price_pair: Spread; from_printed_badge: Spread }
  sample: Sample
}

export interface Coverage {
  channels: { in_registry: number; with_a_row: number; share: number }
  segments: { in_registry: number; with_a_row: number; share: number }
  sample: Sample
}

export interface PromoPressure {
  by_brand: Record<string, number>
  by_chain: Record<
    string,
    { by_carrier: Record<string, number>; named_by_amendment_3_20: boolean; position_rows: number }
  >
  share: Record<string, number>
  position_rows: number
  rows_with_no_resolved_brand: number
  sample: Sample
}

export interface CcMetrics {
  volume: Volume
  nsr: Sampled<NsrReading>
  negative_share_sarcasm_adjusted: Sampled<NegativeShareReading>
  sov: Sampled<SovReading> & { watchlist_rules: string }
  aspect_share: Sampled<AspectReading>
  promo_depth: PromoDepth
  promo_pressure: PromoPressure
  coverage: Coverage
}

/** One population's own reading inside a segment or a channel cut. */
export interface CommentCut {
  rows: number
  scored: number
  sentiment: Record<string, number>
  intents: {
    frequency: Record<string, number>
    labels_per_scored_row: number
    rows_with_no_intent: number
  }
  language: { rows: Record<string, number>; sentiment: Record<string, Record<string, number>> }
  brand_attribution: { mentions: Record<string, number>; rows_with_a_brand: number }
  empty_text: { rows: number; with_no_intent: number }
  sarcasm: { denominator: string; rate: number; true: number; false: number }
  unreadable: { rows: number; reasons: Record<string, number> }
}

export interface SegmentCut {
  bought: CommentCut
  payable: CommentCut
  channels_with_a_row: string[]
  registry_channels: number
}

export interface ChannelCut {
  bought: CommentCut
  payable: CommentCut
  segment: string
  source_id: string
  source_type: string
}

export interface CcCuts {
  brand_by_sentiment: { rows: Record<string, Record<string, number>>; sample: Sample; watchlist_rules: string }
  brand_attribution_in_the_comment_cuts: { reading: string; watchlist_rules: string }
  comment_by_segment: Record<string, SegmentCut>
  comment_by_channel: Record<string, ChannelCut>
  positions_by_carrier: Record<string, number>
  positions_by_category: Record<string, number>
  legs: Record<string, unknown>
}

/** A reading this window CANNOT carry, in the file's own words — the sentence a tab prints instead
 *  of a figure (DESIGN-ship-1 §10: never an empty state without a sentence). */
export interface NotComputable {
  reason: string
  surface: string
  unlock: string
}

export interface CommandCentre {
  contract: string
  phase: string
  conclusions: Conclusion[]
  window: Window & { populations: Record<string, number>; reading: string; rule: string }
  metrics: CcMetrics
  cuts: CcCuts
  not_computable: Record<string, NotComputable>
  promo: { positions_table: { law: string; rows: Position[]; sample: Sample; window: string } }
  provenance: Record<string, unknown>
  convergence: Record<string, unknown>
  dictionary: { metrics: string[]; path: string; sha256: string }
}

/** One sample's Δ column: each watchlist brand's SoV share minus the reference own brand's, the
 *  subtraction the producer does so that T4 does not (ruling (ddd) 2). `reference` is named on the
 *  reading because the record lists its own brands alphabetically — `null` is a brand the sample
 *  has no share for at all, and it prints as a sentence, never as a tie. */
export interface DeltaVsOwn {
  reference: string
  own_brands: string[]
  delta: Record<string, number | null>
}

/** `front_data.json :: command_center_derived` — what the producer computes FROM the sealed
 *  command centre, for screens the brief orders a figure the sealed file does not carry. */
export interface CommandCentreDerived {
  from: string
  reading: string
  sov_delta_vs_own: SampledOf<DeltaVsOwn>
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

/** The rows whose own page prints no price: dropped where they cannot be priced and counted there,
 *  with the reason each was dropped for. The same block sits on the price cards and on the
 *  positions table — two populations, one sentence (`export_front_data.excluded_rows`). */
export interface ExcludedRows {
  n: number
  from: string
  reading: string
  rows: { row_id: string; carrier: string; category: string; why: string }[]
}

/** The Позиції table's own rows — the sealed screen export's positions with the human-verified
 *  record of `config/price_corrections.yaml` applied ONCE by the producer (ruling (aaa) 13.09).
 *  The sealed file keeps its bytes; the table reads these. */
export interface PositionsBlock {
  from: string
  reading: string
  rows: Position[]
  /** how many of `rows` carry a `correction` — the record's own count, not a filter run here */
  corrected: number
  excluded: ExcludedRows
}

/** The week the whole screen reports on: the newest ISO week ANY chain has leaflet pages in, and
 *  the dates those pages carry. Not every chain has a set in it — `chains` names the ones that do,
 *  and each chain's card keeps its own newest week (operator's rule (б), 13.09). */
export interface ReportingWeek {
  from: string
  reading: string
  week: string
  since: string
  until: string
  chains: string[]
  chains_with_a_set: number
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
  /** each chain's own median INSIDE this basis, cheapest first — the ranking exhibit's rows */
  chains: CategoryChain[]
}

/** One chain inside one (category × unit) basis. `n` rides beside the median because one row is
 *  also a median: no floor drops a thin chain, so the reader is shown the count and decides. */
export interface CategoryChain {
  chain: string
  name: string
  n: number
  min: number
  median: number
  max: number
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
  excluded: ExcludedRows
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

/** A sentence the producer wrote in both languages. `Finding` is this plus an id and its figures'
 *  paths; the readings of §13 carry no id, because each one titles exactly one exhibit. */
export interface Said {
  ua: string
  en: string
}

/** One finding the paid reader kept, inside its thread's card (DESIGN-ship-1 §13 (3)). */
export interface SignalRow {
  type: string
  subject: string | null
  subject_type: string
  quote: string | null
  confidence: number | null
  /** the producer's own rule, so the app never re-spells «what counts as unsure» */
  low_confidence: boolean
}

/** A thread the reader found something in: the ROOT promo post and the signals under it.
 *  `date` and `text` are `null` when the committed draw and pack files do not carry the thread —
 *  «rows not exported» is a legal answer and an invented post is not. */
export interface ThreadCard {
  channel: string
  thread_root: string
  date: string | null
  text: string | null
  signals: number
  rows: SignalRow[]
}

export interface VoiceGroup {
  type: string
  title: Said
  n: number
  rows: {
    subject: string | null
    quote: string | null
    channel: string
    thread_root: string
    confidence: number | null
    low_confidence: boolean
  }[]
}

/** Промо · Реакції in §13's grammar. Every figure is counted by the producer over
 *  `results/promo_signals/`: one row per FINDING, never per comment. */
export interface ReactionsBlock {
  from: string
  reading: string
  rows: number
  /** the same population `promo_screen_data.json :: screen.feed` carries, with the subject fields
   *  that export does not hold — the tab reads this list and never both */
  feed: (SignalRow & { channel: string; msg_id: number; thread_root: string })[]
  coverage: {
    read: number
    queue: number
    not_collected: number
    population: number
    product_population: number
    channels: number
    threads_with_a_signal: number
    low_confidence: number
    from: string
  }
  matrix: {
    types: string[]
    subject_types: string[]
    subject_words: Record<string, Said>
    cells: { type: string; subject_type: string; n: number }[]
    by_type: Record<string, number>
    by_subject_type: Record<string, number>
  }
  complaints: {
    type: string
    of_type: number
    bars: { subject_type: string; n: number }[]
    other: number
    title: Said
  }
  mix_by_channel: {
    channels: {
      channel: string
      signals: number
      parts: { type: string; n: number; share: number }[]
      complaints: number
    }[]
    title: Said | null
  }
  monthly: {
    type: string
    months: {
      month: string
      signals: number
      complaints: number
      share: number
      /** the month's size AS A SHARE, so §12's greyed context rides the one axis */
      weight: number
    }[]
    /** signals whose thread carries no post date at all — printed, never dropped in silence */
    without_a_date: number
    title: Said | null
  }
  threads: { cards: ThreadCard[]; shown: number; of: number; title: Said | null }
  sku_voice: { groups: VoiceGroup[]; rows: number; title: Said }
}

/** One mention the keyword sentinel found. Empty is the honest answer and the file is empty today. */
export interface MentionRow {
  channel: string
  msg_id: number
  kind: string
  date: string
  brand: string
  /** WHICH spelling hit — what lets a human judge «Гармонія» the brand from «гармонія» the noun */
  matched: string
  quote: string
}

/** One regional channel: the sentinel's own counts, joined to the collector's thread coverage.
 *  The three thread figures are `null` for a channel the report does not carry. */
export interface RegionChannel {
  channel: string
  posts: number
  comments: number
  mentions: number
  first_date: string | null
  last_date: string | null
  threads_total: number | null
  threads_read: number | null
  outstanding: number | null
}

/**
 * Промо · Регіон — the stage-2 keyword sentinel's baseline (DESIGN-ship-1 §13).
 *
 * NOT `RegionsBlock` one letter over: that is the operator's cut across retail CHAINS
 * (`config/chain_regions.yaml`) rendered at the foot of Позиції, and this is the Poltava-oblast
 * CHANNELS the sentinel reads. Two populations, two files, and nothing joins them.
 */
export interface RegionPulseBlock {
  from: string
  reading: string
  window: { first_date: string | null; last_date: string | null }
  totals: { channels: number; posts: number; comments: number; mentions: number }
  sources: { brands: string; channels: string; roots: string[] }
  brands: {
    brand_id: string
    name: string
    own: boolean | null
    spellings: string[]
    mentions: number
  }[]
  channels: RegionChannel[]
  mentions: MentionRow[]
  sample: {
    channels: number
    threads_total: number
    threads_read: number
    outstanding: number
    sentence: Said
    from: string
  }
  instrument: Said
  baseline_says: Said
  promo_link: { chain: string; name: string }
}

/** One code rule's finding, worded by the producer in both languages (DESIGN-ship-1 §12).
 *
 * The app renders the sentence and words none of it: `stands_on` is the path of every figure the
 * sentence states, inside this same export, so a reader (and the suite) can hold the words against
 * the block they were computed from. */
export interface Finding {
  id: string
  ua: string
  en: string
  stands_on: Record<string, number>
}

/** Which basis the chain ranking is drawn over — the one with the most priced rows. The rows
 *  themselves live on that basis (`category_prices.categories[].bases[].chains`), read by lookup:
 *  a second copy of them in this block could disagree with the cards beside it. */
export interface ChainRanking {
  category: string
  unit: string
  name: string
  ranked: number
  reading: string
}

export interface TrendsBlock {
  from: string
  reading: string
  /** «Три висновки тижня» — a week where a rule found nothing carries fewer, never an invented one */
  conclusions: Finding[]
  /** one action title per exhibit, keyed by the exhibit's id */
  exhibits: Finding[]
  chain_ranking: ChainRanking | null
  /** the (category × unit) basis the spread exhibit's own title is about — the strip accents that
   *  row instead of finding it again, because a rule run twice is a rule with two answers */
  widest: { category: string; unit: string } | null
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
  command_center_derived: CommandCentreDerived
  model: { from: string; verdict: Record<string, unknown> }
  s2_readings: S2Row[]
  /** `build_promo_screen.S2_BOUNDARY` — the one sentence that separates the shipped row from
   *  the readings under it, defined once in Python and rendered wherever the table is */
  s2_boundary: string
  media: MediaBlock
  reporting_week: ReportingWeek
  positions: PositionsBlock
  category_prices: CategoryPricesBlock
  trends: TrendsBlock
  /** the CHAIN cut at the foot of Позиції — `region` below is the sentinel's channels, and the two
   *  are one letter apart on purpose only in the spec: nothing joins them */
  regions: RegionsBlock
  reactions_v2: ReactionsBlock
  region: RegionPulseBlock
  s1_reading: S1Reading
  status: Status
  dictionary: { from: string; sha256: string; metrics: MetricEntry[] }
  sources: Record<string, { sha256: string; bytes: number }>
}
