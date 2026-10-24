# API Review: CSFloat & Skinport

Purpose: a structured review of every endpoint we can draw from, verified live where possible, so that pulls from each source land in bronze/silver in shapes that compose across sources. Research date: 2026-10-23. Live probes were run against `csfloat.com/api/v1` and `api.skinport.com/v1` from this repo's client conventions.

Sources reviewed:

- Unofficial CSFloat API reference: https://csfloatapi.com (46 documented operations; includes OpenAPI spec at `/openapi.yaml`)
- Archived official CSFloat docs (removed by CSFloat): https://web.archive.org/web/20260320124433/https://docs.csfloat.com/
- Skinport official docs: https://docs.skinport.com

---

## 1. Executive summary

| # | Finding | Impact |
|---|---------|--------|
| 1 | **`GET /history/{mhn}/graph` is live, unauthenticated, and returns ~5.5 years of daily avg price + sale count** (verified: 1,977 daily points for AK-47 Redline FT back to 2020-04) | Single biggest win available. Backfills `item_day_sale` with years of real sale data on day one |
| 2 | **`GET /history/{mhn}/sales` is live, unauthenticated.** Returns the 40 most recent completed sales with full item detail (float, seed, stickers, CSFloat's own `predicted_price`) | Per-sale fact data CSFloat-side; feeds float/pattern premium analysis |
| 3 | **`GET /schema` and `GET /meta/exchange-rates` are live, unauthenticated** | `item_master` enrichment (collections, weapon types, rarities) without name-parsing heuristics |
| 4 | **`GET /listings` works with the raw API key** (verified 200). The auth style is the gotcha: raw key in the `Authorization` header — a `Bearer` prefix is rejected with a misleading `"You need to be logged in to search listings"` 403 | The existing `cs_float_item_listing_details` event **works as designed**; keep the client's raw-key header exactly as is |
| 5 | **The local `backend/.env` has an empty `CSFLOAT_API_KEY`** while the Secrets Manager copy is valid (verified via `/me` → 200). Unnoticed locally because `price-list` is public — `test_connection` passes even with a garbage/empty key | Sync the key from Secrets Manager into local `.env`; repoint `test_connection` at `/me` so it actually validates the key |
| 6 | **Skinport has an untouched `GET /v1/sales/out-of-stock` endpoint** (1-hour cache): suggested price, avg sale price, sales in last 90d for items with zero supply | Direct scarcity/demand-exceeds-supply signal; cheap to add |
| 7 | CSFloat rate limits are **per-route with no published table**; every response carries `X-RateLimit-*` headers | Client should be header-driven, not fixed-interval |

Recommendation in one line: pull daily snapshots from the two bulk Skinport endpoints plus CSFloat `price-list`, backfill `item_day_sale` from CSFloat `graph`, treat `sales`/`schema` as targeted enrichment, and keep `GET /listings` in the mix for per-listing detail (raw-key auth required).

---

## 2. CSFloat — endpoint-by-endpoint

Base URL: `https://csfloat.com/api/v1`. Money is **integer USD cents** everywhere (`500` = $5.00). Auth (when required) is the raw key in the `Authorization` header — no `Bearer` prefix. IDs are JSON strings exceeding JS safe-integer range — keep them strings.

### 2.1 Verified live & public (no auth)

#### `GET /listings/price-list` — already wired (`csfloat_listing`)
- Shape: `{ market_hash_name, quantity, min_price }[]`, prices in cents.
- Role: the current **supply snapshot** (listing count + floor price per item). This is CSFloat's answer to Skinport `/items`.
- Rate limit: unknown but generous; it's the same route our twice-daily event already hits.

#### `GET /history/{market_hash_name}/graph` — NEW, the price history
- Path param: complete URL-encoded market hash name. Optional `paint_index` query param restricts variants (Doppler phases, knife finishes).
- Shape: `{ day: ISO date, avg_price: cents (float), count: int }[]`, newest first. Verified depth: back to 2020-04 (~5.5 years) for a liquid item.
- What to store:
  - Bronze: `csfloat_price_history` — `job_id`, `market_hash_name`, `paint_index (nullable)`, `day (date)`, `avg_price (integer cents, as returned)`, `count`.
  - Silver: feeds `item_day_sale` (`datasource_id = csfloat`) with `sell_count = count`, plus avg price. **Model gap:** `item_day_sale` currently has `min_price` only — avg price is the actual signal here. Options: add `avg_price` column (recommended, single clean migration) or overload `min_price` (misleading; avoid).
  - Idempotency: repeated pulls overlap history. Upsert on `(item_id, datasource_id, day)` and prefer the freshly pulled row (revisions happen; later pulls win).
- Backfill note: one request per item. Full catalog ≈ price-list size (~10k+ names). Pace off `X-RateLimit-Remaining`; chunk via the existing `params` mechanism in the SQS message (same pattern as `cs_float_item_listing_details`).

#### `GET /history/{market_hash_name}/sales` — NEW, per-sale facts
- Shape: array of the 40 most recent completed listings for the item: `{ id, created_at, sold_at, price, state, item {...}, reference { base_price, predicted_price, float_factor, sticker_overpay, ... } }`. `item` includes `float_value`, `paint_seed`, `paint_index`, `is_stattrak`, `is_souvenir`, `stickers[]`, `collection`, `rarity_name`.
- What to store:
  - Bronze: `csfloat_sale` mirroring the listing-detail bronze pattern (typed scalars + JSON blobs for `item`/`reference`).
  - Silver: an `item_sale_detail` fact keyed by CSFloat `sale id` — this is genuinely new analytical surface: **list price vs `predicted_price`** (mispricing screen), **`sticker_overpay`** quantified, float-vs-sale-price curves from real transactions.
  - Caveat: fixed window of 40; pull cadence must exceed sell-rate for continuous coverage, or accept gaps on fast items. Dedupe by sale `id` makes reruns safe.
- Relationship to `item_listing_detail`: same listing shape, but with `sold_at` set and `state != listed`. If `GET /listings` stays login-gated, this endpoint is the *only* way listing-detail-level item attributes (float/seed) flow in — via sold items instead of active ones.

#### `GET /schema` — NEW, catalog/enrichment
- Shape: `{ collections[], weapons, stickers, keychains, containers, agents, collectibles, music_kits, rarities, ... }`.
- Role: replaces name-parsing heuristics. `item_master` today derives `item_type`/`wear`/`stat_track` from `parse_market_hash_name`; the schema gives authoritative mappings (`collection` keys appear on items in `sales`/`listings` responses too, e.g. `set_community_13`).
- What to store: bronze `csfloat_schema` (one row per pull, JSON), silver: enrich `item_master` with `collection`, `rarity`, `def_index`/`paint_index` → canonical weapon name. Low frequency (weekly is plenty; the schema changes rarely).

#### `GET /meta/exchange-rates` — NEW, utility
- Shape: `{ data: { <lowercase ccy>: multiplier-vs-USD } }`.
- Role: only needed if we ever store non-USD. Given both our sources natively quote USD (CSFloat cents are USD; Skinport client requests USD), the simple rule is: **store USD only** and skip this endpoint. Documented for completeness.

### 2.2 Verified live & key-authed

#### `GET /listings` (search) — WORKS with raw key; auth style matters
- Verified 200 with `Authorization: <API-KEY>` (raw, no prefix). Rejected 403 `code 1: "You need to be logged in to search listings"` with a `Bearer` prefix or with an empty/invalid key — the error message is misleading; it means *auth was not accepted*, not that a browser session is required.
- The existing `get_item_listing_details()` / `CSFloatListingDetailLoader` / `cs_float_item_listing_details` event work as designed. Cost caveat: paginated per item (50/page), so scope pulls to a curated item list via the event's `market_hash_names` param and pace off `X-RateLimit-*`.
- Item-level attributes (`float_value`, `paint_seed`, stickers, `reference.predicted_price` on each listing) land in `item_listing_detail` — the float/pattern premium surface. `/history/{mhn}/sales` (§2.1) remains a complementary source of the same attributes via sold items, with `sold_at` and real transaction prices.

#### `GET /me` — protected; validates the key
- Verified 200 with a valid raw key. No market data, but the cheapest definitive key check — the right target for `test_connection` (the current target, `price-list`, is public and passes regardless of key validity).

### 2.3 Rate limits (CSFloat-wide conventions)
- Limits are **per route**, differing by orders of magnitude; no published table.
- Every response carries `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset`.
- Client guidance: raise on 429 after waiting to `X-RateLimit-Reset` (connector convention already raises on failure — good); drive pacing from headers rather than fixed sleeps. For the SQS consumer (batch_size=1), a simple "read remaining, sleep if low" inside the connector is enough.
- Errors are numeric `code` + message; codes are stable, messages are not — branch on `code`.

---

## 3. Skinport — endpoint-by-endpoint

Base URL: `https://api.skinport.com/v1`. All routes public. Prices are **decimal major units** (not cents). The `Accept-Encoding: br` header is **required** (Brotli). Docs default currency is EUR — our client explicitly requests USD; keep that.

Shared limits: **8 requests / 5 minutes**, responses cached server-side 5 minutes. With one request per endpoint per sync, we use a fraction of budget. The binding constraint is never raw QPS — it's that there is no reason to call more than once per cache window.

#### `GET /v1/items` — bronze table exists (`skinport_item`), loader missing
- Shape: `{ market_hash_name, version, currency, suggested_price, min/max/mean/median_price, quantity, created_at, updated_at, item_page, market_page }[]`.
- Role: Skinport **supply snapshot** — the direct comparable to CSFloat `price-list`. Also the source of `suggested_price` (Steam-reference price) — key for discount metrics.
- Silver: feeds `item_day_listing` (`datasource_id = skinport`): `listings_count = quantity`, `min_price = min_price` (currency conversion: Skinport dollars vs CSFloat cents — normalize to **dollars in silver** everywhere).
- Gap: `version` (e.g. "Emerald" for Gamma Doppler) is stored in bronze but has no silver home; matters for pattern-variant items. Park until variant handling is designed (see §5.3).

#### `GET /v1/sales/history` — bronze table exists (`skinport_sales_history`), loader missing
- Shape: trailing aggregates `{ last_24_hours, last_7_days, last_30_days, last_90_days }`, each `{ min, max, avg, median, volume }`, per item.
- Role: demand side. Overlapping trailing windows — but **daily snapshots convert them into daily increments**: e.g., daily sale count ≈ `vol(30d, today) - vol(30d, yesterday)` for the trailing 29 of 30 days. Store the raw windows in bronze (mirror exactly); derive increments in silver.
- Silver: feeds `item_day_sale` (`datasource_id = skinport`). Note: after the CSFloat graph backfill lands, this becomes corroboration rather than the primary sale series — two independent marketplaces measuring the same demand.

#### `GET /v1/sales/out-of-stock` — NEW, untouched
- Shape: `{ market_hash_name, version, suggested_price, avg_sale_price, sales_last_90d }[]` — items with demand history but **zero current supply**.
- Role: the cleanest scarcity screen available from either source: things that sold recently at X and currently cannot be bought. Complements `price-list`/`items` (which only show items *with* supply).
- Cache: 1 hour. One call per sync.
- What to store: bronze `skinport_out_of_stock_item`; silver: either flag rows in `item_day_listing` (`listings_count = 0`) or a small dedicated table. Flagging `item_day_listing` keeps one supply grain; recommended.

#### Account & Websocket categories
- OAuth client-credential flows for account-scoped data (own sales/orders); a websocket exists for real-time sales. Out of scope for a batch aggregator; revisit only if intraday data ever matters.

---

## 4. Cross-source data contract (the point of doing this review first)

1. **Canonical key:** `market_hash_name` → `item_master`. Every verified endpoint from both sources carries it. `bulk_get_or_create_items` is the single choke point for item identity — all loaders must route through it.
2. **Currency:** USD everywhere. CSFloat bronze keeps cents (as delivered); Skinport bronze keeps decimal dollars (as delivered). **Silver normalizes to dollars** (`cents / 100.0`). No FX storage; if this ever changes, `meta/exchange-rates` exists.
3. **Grain:**
   - `item_day_listing(item, datasource, day)` — supply snapshots: CSFloat `price-list`, Skinport `items`, Skinport `out-of-stock` (as zero-quantity).
   - `item_day_sale(item, datasource, day)` — sales: CSFloat `graph` (backfill + daily), Skinport `sales/history` (derived increments).
   - `item_listing_detail` / new `item_sale_detail` — per-listing facts: CSFloat `/listings` (active listings, raw-key auth) and `/history/{mhn}/sales` (completed sales).
4. **Identity of a datasource:** the `datasource` table must be seeded (currently empty; every silver table FKs to it and CSFloat events hardcode `datasource_id="1"`). Suggested rows: `1 = csfloat`, `2 = skinport`. Skinport loaders currently reference no datasource — they will need IDs at silver time.
5. **Timestamps:** CSFloat ISO-8601 UTC strings; Skinport epoch seconds on items. Normalize to `TIMESTAMP` in silver; bronze mirrors raw.
6. **Rerun safety:** every silver write upserts on its natural key; bronze accumulates per `job_id`. New endpoints must follow the same rule (CSFloat graph upserts per `(item, day)`; sales dedupe on sale id).

---

## 5. What to pull, in priority order

### P0 — make existing pipelines real (no new endpoints)
1. Seed `datasource` (`csfloat`, `skinport`).
2. Write the Skinport loaders (`items`, `sales_history`) following `docs/adding_datasource.md` — bronze tables already exist and are empty.
3. Re-enable the twice-daily scheduler group (currently commented out in `event_registry.py`); fold Skinport pulls into the same cadence (they share one budget group of 8/5min; two calls per cycle is trivial).
4. Repoint `test_connection` at `GET /me` (key-authed, cheap) — today it hits public `price-list` and validates nothing about the key.
5. Sync the valid `CSFLOAT_API_KEY` from Secrets Manager into local `backend/.env` (currently empty — local runs of key-authed events will 403).
6. Re-enable `cs_float_item_listing_details` runs over a curated item list — it works with the raw key; it was never broken, only untested with a real key.

### P1 — the backfill win
6. `GET /history/{mhn}/graph` → bronze `csfloat_price_history` → silver `item_day_sale` (+`avg_price` column). Chunked, header-paced backfill over the full catalog; then a daily top-up for the newest day.

### P2 — enrichment & new signals
7. `GET /v1/sales/out-of-stock` → zero-supply flags.
8. `GET /schema` → `item_master` enrichment (collection, rarity, canonical weapon/type), replacing fragile name parsing over time.
9. `GET /history/{mhn}/sales` → `item_sale_detail` facts (mispricing vs `predicted_price`, sticker overpay, float curves).

### Parked
- Skinport account/websocket (OAuth), any CSFloat buy/sell/offer/trade routes (out of scope for an aggregator; rate-limited 2 orders of magnitude tighter).

---

## 6. Insights the combined data supports

Once P0–P1 land, per item per day, across two marketplaces:

- **Cross-market spreads:** CSFloat floor (cents→$) vs Skinport min/median → buy-low/sell-high screening with transaction-cost caveats.
- **Real price history:** years of daily avg + volume per item (CSFloat graph), corroborated by Skinport trailing windows → trend, volatility, liquidity.
- **Supply vs demand:** `quantity` (both sources) vs sale counts → days-of-supply, oversupply/shortage detection; out-of-stock screen for extreme scarcity.
- **Discount to reference:** Skinport `min_price` vs `suggested_price` → mispricing vs Steam reference.
- (P2) **Float/pattern premiums** and **CSFloat model trust**: sale price vs CSFloat `predicted_price` residuals.

## 7. Known pipeline defects found during this review

- `datasource` table empty while silver FKs reference it (first silver write from a fresh DB fails FK).
- `run_sales_history` fetches but stores nothing; no Skinport loaders exist.
- Twice-daily schedule group commented out; `SCHEDULE_GROUPS['twice_daily']` never triggered.
- Local `backend/.env` `CSFLOAT_API_KEY` is empty (Secrets Manager copy is valid); local runs of key-authed events will 403 with a misleading "log in" message. Masked by the public `price-list` connection test.
- Two `job_log_details` rows stuck `Running` since 2026-06-19 (orphaned lambda timeouts) — consider a sweeper that marks jobs failed if `end_time` is null and older than X.

## 8. References

- Unofficial CSFloat API (primary CSFloat reference going forward): https://csfloatapi.com — spec: https://csfloatapi.com/openapi.yaml
- Archived official CSFloat docs (stale re: `/listings` auth): https://web.archive.org/web/20260320124433/https://docs.csfloat.com/
- Skinport docs: https://docs.skinport.com — items: /items, sales history: /sales/history, out-of-stock: /sales/out-of-stock
- Repo process for turning any endpoint above into a pipeline: `docs/adding_datasource.md`
