# sku-b bar 1 — the 29 missed gold pairs, packed for the team lead's read

Bar 1 read 0.3603 vs 0.75 — FAIL — over 15 posts with a non-empty gold set: 26 of 55 gold keys found, 29 missed. This file decomposes the misses and rules on nothing — the verdicts are the team lead's, from the page images.

**The gold is per POST, not per page**: one reviewer named the brands visible across the pages sent for a post, so a missed key is missed by the post's whole union of page answers. **The pages are a slice** — `pages_available` names how many the post really has, and no brand on an unsent page is in this gold.

Each page below is in one of three states: the `brand_raw` list the instrument extracted, `[]` (it answered and named nothing), or `UNREADABLE` with the reason the extractor refused the reply.

## The three classes

- **a** — the brand is PRINTED on a sent page WITH a price box — a real under-read
- **b** — the brand is VISIBLE on a sent page WITHOUT a price box — bar-vs-instrument mismatch
- **c** — the brand is NOT VISIBLE on the sent pages at all — gold noise

## The posts

### @atb_market_official:4340 — gold 3 · found 1 · missed 2 · recall 0.3333

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4340.jpg | `7ae55c29dc8d…` | `[]` |
| 2 | atb_market_official_4341.jpg | `39862ec33b1a…` | «Three Bears» · «Three Bears» |
| 3 | atb_market_official_4342.jpg | `3e9d93e56bf6…` | **UNREADABLE** — printed discount '-50%*' is not a percentage |
| 4 | atb_market_official_4343.jpg | `5b99c3dcc141…` | «Своя Лінія» |
| 5 | atb_market_official_4344.jpg | `189ce416a8da…` | «Своя Лінія» |
| 6 | atb_market_official_4345.jpg | `fd8d243b9791…` | `[]` |

**MISSED — to be ruled on**

- **1.** `raw:rud` — the reviewer wrote `rud` (watchlist_hits) · registry: «Рудь»
  - ⚠ this post has an unreadable page — page 3 (printed discount '-50%*' is not a percentage). A page the extractor refused contributes no brand to the post's union
  - ⚠ the instrument extracted `raw:three bears` on this post and no gold key matches it. Stated as a fact about the post; nothing here claims it is this brand
- **2.** `raw:try-vedmedi` — the reviewer wrote `try-vedmedi` (watchlist_hits) · registry: «Три Ведмеді» / «Три Медведя»
  - ⚠ this post has an unreadable page — page 3 (printed discount '-50%*' is not a percentage). A page the extractor refused contributes no brand to the post's union
  - ⚠ the instrument extracted `raw:three bears` on this post and no gold key matches it. Stated as a fact about the post; nothing here claims it is this brand

**FOUND — the control half**

- `raw:svoia-liniia` — p4 «Своя Лінія» · p5 «Своя Лінія»

> Reviewer's note: Page 4341 headline reads ТМ «Три Ведмеді» while the caption renders it as «Three Bears» -- a Latin form the canon table has no alias for, so a matcher reading the caption sees no watchlist brand there; Своя Лінія carries three of the six pages (4343 Золотий Каштан, 4344 Факел, 4345 ковбаса «Баликова» ТМ «М'ясна лавка»/«Своя Лінія»). Verdict partial, not faithful: everything stated is true, but six product pages are compressed into one clause and all SKU names, weights and prices («Фісташка» 500 г, «100% морозиво», «Чорниця-ожина») are dropped, unlike the other ATB captions in this pack. Milka is chocolate, excluded from other_dairy_brands by the dairy/ice-cream-only rule.

### @atb_market_official:4350 — gold 3 · found 2 · missed 1 · recall 0.6667

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4350.jpg | `3147747cc649…` | «Своя Лінія» · «Своя Лінія» |
| 2 | atb_market_official_4351.jpg | `08db5ad39959…` | `[]` |
| 3 | atb_market_official_4352.jpg | `1287d91aaf74…` | «Дольче» · «Дольче» |
| 4 | atb_market_official_4353.jpg | `4ea2a6918bfc…` | `[]` |
| 5 | atb_market_official_4354.jpg | `2d3c859e3e6f…` | `[]` |
| 6 | atb_market_official_4355.jpg | `022c64a0f006…` | `[]` |

**MISSED — to be ruled on**

- **3.** `raw:lactel` — the reviewer wrote `lactel` (other_dairy_brands)

**FOUND — the control half**

- `raw:svoia-liniia` — p1 «Своя Лінія» ×2
- `raw:дольче` — p3 «Дольче» ×2

> Reviewer's note: Caption carries Своя Лінія and Дольче, but drops the `lactel` maker logo printed on every Дольче pot (a dairy brand only ever readable in the image), and it under-attributes: the chips (4351) and the Roar! bars (4353) are also ТМ Своя Лінія, which the caption gives only to the cheese.

### @atb_market_official:4360 — gold 4 · found 3 · missed 1 · recall 0.7500

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4360.jpg | `3b417da3cb1f…` | «Київський Пломбір» · «Каштан» · «Каштан» · «Київський Пломбір» · «Limo» · «Limo» |
| 2 | atb_market_official_4361.jpg | `1ef0c6a1847d…` | `[]` |
| 3 | atb_market_official_4362.jpg | `23f2914eb381…` | `[]` |
| 4 | atb_market_official_4363.jpg | `120d01e56cd4…` | `[]` |
| 5 | atb_market_official_4364.jpg | `30203fbdffe4…` | `[]` |
| 6 | atb_market_official_4365.jpg | `8d9fe4cabdcc…` | `[]` |

**MISSED — to be ruled on**

- **4.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- `raw:limo` — p1 «Limo» ×2
- `raw:каштан` — p1 «Каштан» ×2
- `raw:київський пломбір` — p1 «Київський Пломбір» ×2

> Reviewer's note: Page 1 is an all-ice-cream page naming «Київський Пломбір», «Каштан» and watchlist «Лімо», and «Своя Лінія» carries eight items across pages 2-6, yet the caption lists categories only and names no brand at all -- every brand in this post is image-only, so a text matcher scores zero here by construction; «Сирні палички ТМ «ЇЗІ»» (Глобино) is left out of open extraction under the rule that a non-dairy brand selling one cheese SKU is not a dairy brand.

### @atb_market_official:4377 — gold 1 · found 0 · missed 1 · recall 0.0000

4 pages sent of 4 available (0 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4377.jpg | `1093fd99ffc4…` | `[]` |
| 2 | atb_market_official_4378.jpg | `c9d234543178…` | `[]` |
| 3 | atb_market_official_4379.jpg | `51043b5cfe17…` | `[]` |
| 4 | atb_market_official_4380.jpg | `5cf4ed8c0c68…` | `[]` |

**MISSED — to be ruled on**

- **5.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- — none


> Reviewer's note: Four own-label posters, four ТМ lines, all four transcribed verbatim including the compound «М'ЯСНА ЛАВКА/ СВОЯ ЛІНІЯ» — same one-product-per-page layout as @atb_aktsiyi:2999 and the same clean result; no dairy on any page (salami, ketchup, cereal, foil), the milk in the cereal-bowl photo is styling.

### @atb_market_official:4381 — gold 7 · found 4 · missed 3 · recall 0.5714

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4381.jpg | `6d02a184e8f4…` | «Laska» · «Laska» |
| 2 | atb_market_official_4382.jpg | `1449961dd364…` | «Ласунка» · «Ласунка» · «Ласунка» · «Ласунка» |
| 3 | atb_market_official_4383.jpg | `4418a4a0129e…` | «Розумний вибір» · «Розумний вибір» · «Розумний вибір» |
| 4 | atb_market_official_4384.jpg | `e4457f9a4525…` | «President» · «President» |
| 5 | atb_market_official_4385.jpg | `0f8ae2f9c759…` | «Komo» · «Komo» · «Komo» · «Komo» |
| 6 | atb_market_official_4386.jpg | `47954a207fc9…` | `[]` |

**MISSED — to be ruled on**

- **6.** `raw:maximuse` — the reviewer wrote `Maximuse` (other_dairy_brands)
  - ⚠ the instrument extracted `raw:komo` on this post and no gold key matches it. Stated as a fact about the post; nothing here claims it is this brand
- **7.** `raw:каштан` — the reviewer wrote `Каштан` (other_dairy_brands)
  - ⚠ the instrument extracted `raw:komo` on this post and no gold key matches it. Stated as a fact about the post; nothing here claims it is this brand
- **8.** `raw:комо / komo` — the reviewer wrote `Комо / Komo` (other_dairy_brands)
  - ⚠ the instrument extracted `raw:komo` on this post and no gold key matches it. Stated as a fact about the post; nothing here claims it is this brand

**FOUND — the control half**

- `president` — p4 «President» ×2
- `raw:laska` — p1 «Laska» ×2
- `raw:lasunka` — p2 «Ласунка» ×4
- `raw:розумний вибір` — p3 «Розумний вибір» ×3

> Reviewer's note: Systematic pattern: the caption lists SKU names and drops the TM line. p.4382 reads 'ТМ «Ласунка»' over «Стакан Великан»/«Гран-Прі» - the caption names both SKUs and never the watchlist brand; same for 'ТМ «Laska»' behind Maximuse and 'ТМ «Розумний вибір»' behind Каштан. Only President and Komo survive because there the SKU name IS the TM.

### @atb_market_official:4391 — gold 1 · found 0 · missed 1 · recall 0.0000

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4391.jpg | `b310158e7a59…` | `[]` |
| 2 | atb_market_official_4392.jpg | `f566591d20b6…` | `[]` |
| 3 | atb_market_official_4393.jpg | `ddf11445fe8f…` | `[]` |
| 4 | atb_market_official_4394.jpg | `9ed5e1c9c49a…` | `[]` |
| 5 | atb_market_official_4395.jpg | `179abdd1eccc…` | `[]` |
| 6 | atb_market_official_4396.jpg | `b8923ddb55e2…` | `[]` |

**MISSED — to be ruled on**

- **9.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- — none


> Reviewer's note: Caption stops mid-word at «з арома», so image 4395's second «ТМ Своя Лінія» attribution is cut and image 4396 (Norven salmon/trout) is absent entirely — a 6-image flyer captioned to a length limit; the brand_id is still carried once from 4391, so nothing is missed at brand level, but per-occurrence coverage is 4 of 6 images.

### @atb_market_official:4401 — gold 12 · found 5 · missed 7 · recall 0.4167

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4401.jpg | `c4f4b3c9e804…` | `[]` |
| 2 | atb_market_official_4402.jpg | `8859763a6f1e…` | «Premialle» |
| 3 | atb_market_official_4403.jpg | `eafb197478ef…` | «Молокія» |
| 4 | atb_market_official_4404.jpg | `6a90291ce4ce…` | «Ферма» · «Злагода» · «Галичина» · «Галичина» · «Злагода» · «Premialle» |
| 5 | atb_market_official_4405.jpg | `dbd22e75e69b…` | **UNREADABLE** — malformed JSON |
| 6 | atb_market_official_4406.jpg | `48bcd38bb044…` | `[]` |

**MISSED — to be ruled on**

- **10.** `raw:frenzy (рудь)` — the reviewer wrote `Frenzy (Рудь)` (other_dairy_brands)
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **11.** `raw:imperium (рудь)` — the reviewer wrote `Imperium (Рудь)` (other_dairy_brands)
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **12.** `raw:rud` — the reviewer wrote `rud` (watchlist_hits) · registry: «Рудь»
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **13.** `raw:selianske` — the reviewer wrote `selianske` (watchlist_hits) · registry: «Селянське» / «Селянское»
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **14.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **15.** `raw:try-vedmedi` — the reviewer wrote `try-vedmedi` (watchlist_hits) · registry: «Три Ведмеді» / «Три Медведя»
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union
- **16.** `raw:київський пломбір` — the reviewer wrote `Київський Пломбір` (other_dairy_brands)
  - ⚠ this post has an unreadable page — page 5 (malformed JSON). A page the extractor refused contributes no brand to the post's union

**FOUND — the control half**

- `raw:ferma` — p4 «Ферма»
- `raw:halychyna` — p4 «Галичина» ×2
- `raw:molokija` — p3 «Молокія»
- `raw:premialle` — p2 «Premialle» · p4 «Premialle»
- `raw:zlahoda` — p4 «Злагода» ×2

> Reviewer's note: Six-page leaflet, every offer headed «ТМ «...»» in large print: the caption lists categories («сир, масло, сирок, йогурти, вершки, морозиво») and carries exactly ONE brand, Mini Bee -- a nappy TM -- while 8 watchlist brands are legible; «Масло солодковершкове «Селянське» ТМ «Молокія»» is two watchlist brands in one line, and p.2/p.4 print ТМ «Premialle» and «Салямі Преміум» -- two near-misses for canon `premia` (Премія).

### @atb_market_official:4411 — gold 1 · found 0 · missed 1 · recall 0.0000

4 pages sent of 4 available (0 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4411.jpg | `edb0901b78bd…` | `[]` |
| 2 | atb_market_official_4412.jpg | `042793ac6b2a…` | `[]` |
| 3 | atb_market_official_4413.jpg | `127a75b9c213…` | `[]` |
| 4 | atb_market_official_4414.jpg | `220ee6af67f3…` | `[]` |

**MISSED — to be ruled on**

- **17.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- — none


> Reviewer's note: Four catalogue pages carry ТМ «Своя Лінія» on eight distinct products (желатин, агар-агар, часник, соломка, шпроти, мило, вологий папір, серветки, рушник) plus a dozen third-party TMs, and the caption names not one brand — it summarises by product class only; 'соломка зі смаком сиру/сметани' is a flavour claim on crisps, not a dairy item. Verdict basis stated explicitly: there is NO dairy or ice cream on these four pages, so I am counting the presence of a watchlist brand as category-relevant — that is why this row is `partial` while 4415, also zero-dairy but with no watchlist brand on it, is `faithful`.

### @atb_market_official:4421 — gold 1 · found 0 · missed 1 · recall 0.0000

4 pages sent of 4 available (0 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4421.jpg | `ee4417bbd077…` | `[]` |
| 2 | atb_market_official_4422.jpg | `dcdfa1d16c2d…` | `[]` |
| 3 | atb_market_official_4423.jpg | `149068940c26…` | `[]` |
| 4 | atb_market_official_4424.jpg | `852f1442cadc…` | `[]` |

**MISSED — to be ruled on**

- **18.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- — none


> Reviewer's note: Private-label post: `svoia-liniia` on 3 of 4 pages (sausage, chips x2), again zero dairy. The chips are dairy-FLAVOURED («SOUR CREAM & GREENS», «CHEESE зі смаком сиру») — a category-keyword matcher would read these as dairy. Caption carries every ТМ on the pages.

### @atb_market_official:4426 — gold 4 · found 4 · missed 0 · recall 1.0000

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4426.jpg | `01bb05510052…` | «Magnat» · «Magnat» · «Magnat» |
| 2 | atb_market_official_4427.jpg | `e6d1c59507b5…` | «Хрещатик» · «Хрещатик» |
| 3 | atb_market_official_4428.jpg | `ccb5034ab870…` | «Своя Лінія» · «Своя Лінія» · «Розумний вибір» · «Розумний вибір» |
| 4 | atb_market_official_4429.jpg | `c03b710fa8cb…` | `[]` |
| 5 | atb_market_official_4430.jpg | `41a98b825eea…` | `[]` |
| 6 | atb_market_official_4431.jpg | `dcca9698d2b6…` | `[]` |

**MISSED — to be ruled on**

- — none


**FOUND — the control half**

- `raw:magnat` — p1 «Magnat» ×3
- `raw:svoia-liniia` — p3 «Своя Лінія» ×2
- `raw:розумний вибір` — p3 «Розумний вибір» ×2
- `raw:хрещатик` — p2 «Хрещатик» ×2

> Reviewer's note: Four ice-cream TMs on three pages, all four carried by the caption, «Своя Лінія» named twice (морозиво «Великий Стакан» and чипси). Direct contrast with @atb_aktsiyi:3036 above: the same captioner carries the private label when it sits on a food/category SKU and drops it when it sits on wine, soap or paper -- so caption-mediated svoia-liniia recall is biased toward, not away from, the tracked category. Three ATB private labels here (Своя Лінія, Розумний вибір, М'ясна лавка) against one national ice-cream brand.

### @atb_market_official:4436 — gold 2 · found 1 · missed 1 · recall 0.5000

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4436.jpg | `05bf37c88509…` | `[]` |
| 2 | atb_market_official_4437.jpg | `de6eedd7b00c…` | `[]` |
| 3 | atb_market_official_4438.jpg | `37da97d26681…` | `[]` |
| 4 | atb_market_official_4439.jpg | `0deb6c3f3517…` | `[]` |
| 5 | atb_market_official_4440.jpg | `0eb66b03ac36…` | «SOT» · «SOT» · «SOT» |
| 6 | atb_market_official_4441.jpg | `3380d7d0559e…` | `[]` |

**MISSED — to be ruled on**

- **19.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- `raw:sot` — p5 «SOT» ×3

> Reviewer's note: The caption lists every product line but drops every single TM printed on the pages -- «Торчин», «День у День», «SOT», «Своя Лінія» -- and closes with 'різних брендів'; the watchlist brand svoia-liniia is legible on the jar labels of p.4441 and exists nowhere but in the images.

### @atb_market_official:4446 — gold 5 · found 0 · missed 5 · recall 0.0000

6 pages sent of 9 available (3 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4446.jpg | `2da2cef4f7a6…` | **UNREADABLE** — size '6х100 г' is a multipack — a pack count is not a size |
| 2 | atb_market_official_4447.jpg | `09dfaf145ec2…` | `[]` |
| 3 | atb_market_official_4448.jpg | `a4141a2accd9…` | `[]` |
| 4 | atb_market_official_4449.jpg | `27f774ded269…` | `[]` |
| 5 | atb_market_official_4450.jpg | `45f965d35bb6…` | `[]` |
| 6 | atb_market_official_4451.jpg | `7ebea081687c…` | `[]` |

**MISSED — to be ruled on**

- **20.** `raw:limo` — the reviewer wrote `limo` (watchlist_hits) · registry: «Лімо» / «Лимо»
  - ⚠ this post has an unreadable page — page 1 (size '6х100 г' is a multipack — a pack count is not a size). A page the extractor refused contributes no brand to the post's union
- **21.** `raw:nesquik (какао-напій шоколадно-молочний коктейль, 200 г)` — the reviewer wrote `Nesquik (Какао-напій шоколадно-молочний коктейль, 200 г)` (other_dairy_brands)
  - ⚠ this post has an unreadable page — page 1 (size '6х100 г' is a multipack — a pack count is not a size). A page the extractor refused contributes no brand to the post's union
- **22.** `raw:rud` — the reviewer wrote `rud` (watchlist_hits) · registry: «Рудь»
  - ⚠ this post has an unreadable page — page 1 (size '6х100 г' is a multipack — a pack count is not a size). A page the extractor refused contributes no brand to the post's union
- **23.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»
  - ⚠ this post has an unreadable page — page 1 (size '6х100 г' is a multipack — a pack count is not a size). A page the extractor refused contributes no brand to the post's union
- **24.** `raw:try-vedmedi` — the reviewer wrote `try-vedmedi` (watchlist_hits) · registry: «Три Ведмеді» / «Три Медведя»
  - ⚠ this post has an unreadable page — page 1 (size '6х100 г' is a multipack — a pack count is not a size). A page the extractor refused contributes no brand to the post's union

**FOUND — the control half**

- — none


> Reviewer's note: Nesquik is listed as dairy-adjacent — a milk-drink mix, not milk; drop it if the category is read strictly. The most expensive caption in the pack: page 1 is a pure ice-cream page carrying FOUR watchlist marks — «Monaco» ТМ «Три Ведмеді», «Сиркове 1965» and «Пломбір 1965»/«LIMO ICE CREAM» ТМ «Лімо», «Соковита трилогія» and «Black-кава» ТМ «Рудь» — plus ТМ «Своя Лінія» on p2 (Wild Dog) and p5 (Crackly Crush/«Червоний Мак»), and the caption reduces all six pages to the single word 'морозиво' inside a category list with no brand at all; every category it names is correct, so the loss is entirely brand-level and this is the 3-tile grid layout again, not the single-product poster.

### @atb_market_official:4467 — gold 4 · found 2 · missed 2 · recall 0.5000

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4467.jpg | `adae9a803f2d…` | **UNREADABLE** — printed discount '-50%*' is not a percentage |
| 2 | atb_market_official_4468.jpg | `5c9b6e24e661…` | «Київський Пломбір» · «Київський Пломбір» · «Київський Пломбір» |
| 3 | atb_market_official_4469.jpg | `273181ece70a…` | `[]` |
| 4 | atb_market_official_4470.jpg | `135aa9ae4989…` | «Своя Лінія» |
| 5 | atb_market_official_4471.jpg | `4a259e35e6de…` | «Своя Лінія» · «Своя Лінія» |
| 6 | atb_market_official_4472.jpg | `3083dd0ce5cc…` | `[]` |

**MISSED — to be ruled on**

- **25.** `raw:rud` — the reviewer wrote `rud` (watchlist_hits) · registry: «Рудь»
  - ⚠ this post has an unreadable page — page 1 (printed discount '-50%*' is not a percentage). A page the extractor refused contributes no brand to the post's union
- **26.** `raw:максхолод` — the reviewer wrote `Максхолод` (other_dairy_brands)
  - ⚠ this post has an unreadable page — page 1 (printed discount '-50%*' is not a percentage). A page the extractor refused contributes no brand to the post's union

**FOUND — the control half**

- `raw:svoia-liniia` — p4 «Своя Лінія» · p5 «Своя Лінія» ×2
- `raw:київський пломбір` — p2 «Київський Пломбір» ×3

> Reviewer's note: All three ice-cream TMs across six pages are named; the same channel's 4508 caption names none, so brand-carrying varies post to post rather than being a fixed capability of the captioner.

### @atb_market_official:4498 — gold 1 · found 0 · missed 1 · recall 0.0000

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4498.jpg | `4d22c6e04921…` | `[]` |
| 2 | atb_market_official_4499.jpg | `f22d3efff2ca…` | `[]` |
| 3 | atb_market_official_4500.jpg | `f1013a170064…` | `[]` |
| 4 | atb_market_official_4501.jpg | `96c6511e81c3…` | `[]` |
| 5 | atb_market_official_4502.jpg | `e8193cdad9ec…` | `[]` |
| 6 | atb_market_official_4503.jpg | `122da62247c2…` | `[]` |

**MISSED — to be ruled on**

- **27.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»

**FOUND — the control half**

- — none


> Reviewer's note: Six leaflet pages transcribed accurately, dates included; svoia-liniia is readable on four of them but sits on fish, herring and barbecue charcoal -- a watchlist hit that carries no dairy signal at all.

### @atb_market_official:4508 — gold 6 · found 4 · missed 2 · recall 0.6667

6 pages sent of 10 available (4 not sent, and no brand on them is in this gold).

| page | file | sha256 | the instrument answered |
| --- | --- | --- | --- |
| 1 | atb_market_official_4508.jpg | `713ceb7fa40f…` | «Ласунка» · «Рудь» · «Рудь» · «Лімо» · «Лімо» · «Каштан» · «Каштан» |
| 2 | atb_market_official_4509.jpg | `9547ccd8e03b…` | `[]` |
| 3 | atb_market_official_4510.jpg | `2fbdf44b48d0…` | `[]` |
| 4 | atb_market_official_4511.jpg | `e942a20653f8…` | `[]` |
| 5 | atb_market_official_4512.jpg | `50bd1532ed77…` | `[]` |
| 6 | atb_market_official_4513.jpg | `4c715e2c17a7…` | `[]` |

**MISSED — to be ruled on**

- **28.** `raw:svoia-liniia` — the reviewer wrote `svoia-liniia` (watchlist_hits) · registry: «Своя Лінія» / «Своя Линия»
- **29.** `raw:try-vedmedi` — the reviewer wrote `try-vedmedi` (watchlist_hits) · registry: «Три Ведмеді» / «Три Медведя»

**FOUND — the control half**

- `raw:lasunka` — p1 «Ласунка»
- `raw:limo` — p1 «Лімо» ×2
- `raw:rud` — p1 «Рудь» ×2
- `raw:каштан` — p1 «Каштан» ×2

> Reviewer's note: Six pages, more than a dozen readable TM names, and the caption names none — it summarises by category only («морозиво, заморожені продукти, напої, чай, каву…»); the same channel's 4467 caption does name brands, so this is a per-post collapse, not a channel-wide limit. Page 4510 also carries juice ТМ «Galicia» (Latin, and a juice) — the mirror of the Latin «Rud» case in @ekomarket_shop:1450: one transliteration shape costs a miss, the other invites a false hit on `halychyna`.

## The verdict template

One line per missed pair. Write `a`, `b` or `c` in the last column; the classes are above. The flag columns are facts about the post, carried onto every one of its rows so that a line can be ruled on without scrolling back — they are not a verdict and they pair with nothing.

| # | post | gold key | reading as | unreadable pages | extracted here, in no gold key | verdict (a\|b\|c) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 4340 | `raw:rud` | «Рудь» | p3 | `raw:three bears` |  |
| 2 | 4340 | `raw:try-vedmedi` | «Три Ведмеді» / «Три Медведя» | p3 | `raw:three bears` |  |
| 3 | 4350 | `raw:lactel` | «lactel» | — | — |  |
| 4 | 4360 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 5 | 4377 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 6 | 4381 | `raw:maximuse` | «Maximuse» | — | `raw:komo` |  |
| 7 | 4381 | `raw:каштан` | «Каштан» | — | `raw:komo` |  |
| 8 | 4381 | `raw:комо / komo` | «Комо / Komo» | — | `raw:komo` |  |
| 9 | 4391 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 10 | 4401 | `raw:frenzy (рудь)` | «Frenzy (Рудь)» | p5 | — |  |
| 11 | 4401 | `raw:imperium (рудь)` | «Imperium (Рудь)» | p5 | — |  |
| 12 | 4401 | `raw:rud` | «Рудь» | p5 | — |  |
| 13 | 4401 | `raw:selianske` | «Селянське» / «Селянское» | p5 | — |  |
| 14 | 4401 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | p5 | — |  |
| 15 | 4401 | `raw:try-vedmedi` | «Три Ведмеді» / «Три Медведя» | p5 | — |  |
| 16 | 4401 | `raw:київський пломбір` | «Київський Пломбір» | p5 | — |  |
| 17 | 4411 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 18 | 4421 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 19 | 4436 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 20 | 4446 | `raw:limo` | «Лімо» / «Лимо» | p1 | — |  |
| 21 | 4446 | `raw:nesquik (какао-напій шоколадно-молочний коктейль, 200 г)` | «Nesquik (Какао-напій шоколадно-молочний коктейль, 200 г)» | p1 | — |  |
| 22 | 4446 | `raw:rud` | «Рудь» | p1 | — |  |
| 23 | 4446 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | p1 | — |  |
| 24 | 4446 | `raw:try-vedmedi` | «Три Ведмеді» / «Три Медведя» | p1 | — |  |
| 25 | 4467 | `raw:rud` | «Рудь» | p1 | — |  |
| 26 | 4467 | `raw:максхолод` | «Максхолод» | p1 | — |  |
| 27 | 4498 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 28 | 4508 | `raw:svoia-liniia` | «Своя Лінія» / «Своя Линия» | — | — |  |
| 29 | 4508 | `raw:try-vedmedi` | «Три Ведмеді» / «Три Медведя» | — | — |  |

Pack: `results/sku_miss_pack.json` · contract: `docs/PROMPT-sku-miss-pack.md`
