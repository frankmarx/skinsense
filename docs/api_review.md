# API Review: CSFloat, Skinport, market.csgo.com

A catalog of the **data available** from each marketplace API: endpoints, auth, rate limits, money units, response shapes, and sample responses. This document deliberately says nothing about how we store or pipeline the data.

All endpoints below were verified live on **2026-10-23** unless noted. Samples marked *(live)* were captured from real responses during probing; samples marked *(docs)* come from the provider's documentation.

Sources:

- CSFloat: unofficial reference https://csfloatapi.com (46 operations; OpenAPI at `/openapi.yaml`) — the official docs were removed; last archived copy at https://web.archive.org/web/20260320124433/https://docs.csfloat.com/
- Skinport: official docs https://docs.skinport.com
- market.csgo.com: docs are a JS app (https://market.csgo.com/en/api/content/start); content was read via a rendering proxy and verified by probing

---

## 1. At a glance

| Capability (grain) | CSFloat | Skinport | market.csgo.com |
|---|---|---|---|
| **Item catalog data** (per item) | `/schema` (public) — weapons, collections, rarities | — | `/v2/dictionary/names.json` (public) |
| **Item-level pricing data** (per item; per-day only via snapshot cadence) | `price-list` (public) — min_price + quantity | `/v1/items` (public) — min/max/mean/median + suggested_price + quantity | `/v2/prices` (public) — price + volume |
| **Listing-level pricing data** — float/seed/stickers* (per listing) | `/listings` (key) | — | `full-export` (public), ~1.1M listings |
| **Sale records** (per sale; filterable by item only — returns most-recent window, no day filter) | `/history/{mhn}/sales` (public) — 40 most recent | — | `/v2/history` (key; sparse in testing) |
| **Trailing sale aggregates** (per item; fixed 24h/7d/30d/90d windows, not per-day) | — | `/v1/sales/history` (public) | `/v2/history` (key; sparse in testing) |
| **Daily price history** (per item × per day; filterable by item — one item per call; no day filter, full range returned) | `/history/{mhn}/graph` (public) — ~5.5y depth | — (derivable from trailing windows) | — |
| **Scarcity / out-of-stock** (per item) | — | `/v1/sales/out-of-stock` (public) | — |
| **Reference / model prices** (per item or per listing) | `reference.predicted_price` on listings/sales | `suggested_price` | — |
| Auth | API key, raw `Authorization` header | none (all public) | API key, `key` query param |
| Money units | integer USD **cents** | decimal USD (major units) | integer USD **mills** (1/1000) |
| Rate limits | per-route, `X-RateLimit-*` headers | 8 req / 5 min, 5-min cache | 5 req/sec **or the key is deleted** |

\* **Open question for listing-level data:** listings churn constantly (created, sold, delisted) — we need to figure out how to manage them: identity keys, refresh cadence, and dedupe/churn handling.

Canonical item key across all three: `market_hash_name` (Steam market hash name).

---

## 2. CSFloat

Base: `https://csfloat.com/api/v1`

**Conventions**
- Auth (where required): API key sent raw in the `Authorization` header — **no `Bearer` prefix**. A `Bearer` prefix is rejected with a misleading `403 "You need to be logged in to search listings"`. An invalid/empty key produces the same message.
- Money: integer USD **cents** (`500` = $5.00).
- IDs (listing, asset, Steam): JSON strings exceeding JS safe-integer range — treat as strings.
- Rate limits: **per route**, differing by orders of magnitude, no published table. Every response carries `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset`. Errors carry a stable numeric `code` and a volatile `message`; `429` means wait for `X-RateLimit-Reset`.

### 2.1 `GET /listings/price-list` — public
All items as one summary list.

```json
[
  {"market_hash_name": "10 Year Birthday Sticker Capsule", "quantity": 272, "min_price": 57},
  {"market_hash_name": "1st Lieutenant Farlow | SWAT",     "quantity": 194, "min_price": 681},
  {"market_hash_name": "2020 RMR Challengers",             "quantity": 861, "min_price": 15}
]
```
*(live; `min_price` in cents; full response covers the entire catalog)*

### 2.2 `GET /listings` — key required
Cursor-paginated listing search (`?limit=50&cursor=…`, max 50/page). Filters: `market_hash_name`, `min_price`/`max_price` (cents), `min_float`/`max_float`, `category` (0 any / 1 normal / 2 StatTrak / 3 souvenir), `def_index`, `paint_index`, `paint_seed`, `collection`, `type` (`buy_now`/`auction`), `stickers`, `sort_by` (`lowest_price`, `most_recent`, `lowest_float`, `best_deal`, `highest_discount`, `float_rank`, …). Envelope `{data: [...], cursor}`.

```json
{
  "data": [{
    "id": "1033351332083403463",
    "created_at": "2026-10-22T12:09:16.308885Z",
    "type": "auction",
    "price": 858,
    "state": "listed",
    "seller": {"steam_id": "…", "username": "…", "online": true,
               "statistics": {"median_trade_time": 305, "total_trades": 13, "…": "…"}},
    "item": {
      "asset_id": "22547095285", "market_hash_name": "M4A4 | Poseidon (Factory New)",
      "def_index": 16, "paint_index": 449, "paint_seed": 700,
      "float_value": 0.02796577662229538,
      "is_stattrak": false, "is_souvenir": false,
      "rarity": 5, "rarity_name": "Covert", "quality": 4,
      "item_name": "M4A4 | Poseidon", "wear_name": "Factory New",
      "collection": "The Gods and Monsters Collection",
      "stickers": [{"stickerId": 1060, "slot": 3, "wear": null,
                    "name": "Sticker | Team EnVyUs (Holo) | MLG Columbus 2016",
                    "reference": {"price": 736, "quantity": 1}}],
      "phase": null, "low_rank": null, "high_rank": null,
      "tradable": 0, "inspect_link": "steam://…", "icon_url": "…"
    },
    "reference": {"base_price": 2412, "predicted_price": 2673, "float_factor": 1.108,
                  "keychain_price": 0, "quantity": 13387,
                  "buy_order": {"max_price": 2100, "quantity": 4},
                  "last_updated": "2026-10-23T20:42:14Z"},
    "is_watchlisted": false, "watchers": 0,
    "min_offer_price": 221000, "max_offer_discount": 1500,
    "auction_details": {"expires_at": "…", "reserve_price": 800,
                        "top_bid": {"price": 858, "state": "…"}}
  }],
  "cursor": "…"
}
```
*(shape from live response + csfloatapi.com schema; fields condensed — `item.stickers[]`, `item.keychains[]`, `item.fade`, `item.blue_gem` exist on relevant items)*

Notable data: per-listing `float_value`/`paint_seed`/stickers, CSFloat's own model prices (`reference.predicted_price`, `float_factor`), buy-order depth (`reference.buy_order`), watcher counts, auction bids, sticker reference prices with per-sticker SCM valuation.

### 2.3 `GET /listings/{id}` — key required
Single listing by id, same shape as above, works for inactive listings too (`state != listed`).

### 2.4 `GET /history/{market_hash_name}/graph` — public
Daily average sale price and sale count for one item. Optional `paint_index` query param restricts Doppler-phase/finish variants. Verified depth: **~5.5 years** (1,977 daily points for AK-47 | Redline (Field-Tested), back to 2020-04). Newest first.

```json
[
  {"day": "2026-10-23T00:00:00Z", "avg_price": 10598.62, "count": 69},
  {"day": "2026-10-22T00:00:00Z", "avg_price": 8556.40,  "count": 75},
  {"day": "2026-10-21T00:00:00Z", "avg_price": 10714.22, "count": 96}
]
```
*(live; `avg_price` in cents)*

### 2.5 `GET /history/{market_hash_name}/sales` — public
The **40 most recent completed sales** for one item (optional `paint_index`). Same listing shape as `/listings` plus `sold_at`, with `state: "sold"`.

```json
[{
  "id": "1033843178542860920",
  "created_at": "2026-10-23T20:43:41.642346Z",
  "sold_at": "2026-10-23T23:44:45.885892Z",
  "type": "buy_now",
  "price": 2389,
  "state": "sold",
  "reference": {"base_price": 2412, "predicted_price": 2673, "float_factor": 1.1083714,
                "quantity": 13387, "sticker_overpay": {"total_price": 9},
                "last_updated": "2026-10-23T20:42:14.735453Z"},
  "item": {"market_hash_name": "AK-47 | Redline (Field-Tested)",
           "float_value": 0.24, "paint_seed": 391, "paint_index": 610,
           "is_stattrak": false, "is_souvenir": false, "stickers": [],
           "collection": "…", "rarity_name": "Classified", "wear_name": "Field-Tested"},
  "watchers": 0
}]
```
*(live; `item` keys condensed — full set matches `/listings`)*

Notable data: real transaction prices with per-item attributes (float/pattern at sale time) and CSFloat's model residual (`price` vs `reference.predicted_price`), plus `sticker_overpay`.

### 2.6 `GET /schema` — public
Full game catalog: weapons, paints, stickers, keychains, collections, containers, agents, collectibles, music kits, rarities, custom stickers, highlight reels. Large (~MBs); changes rarely.

```json
{
  "collections": [
    {"key": "set_community_13", "name": "The Gamma Collection", "has_crate": true},
    {"key": "set_community_15", "name": "The Glove Collection", "has_crate": true},
    {"key": "set_canals",       "name": "The Canals Collection"}
  ],
  "weapons": {}, "stickers": {}, "keychains": {}, "containers": {},
  "agents": {}, "collectibles": {}, "music_kits": {}, "rarities": {},
  "custom_stickers": {}, "highlight_reels": {}
}
```
*(live; non-collection maps condensed — e.g. `weapons` maps def_index → weapon data)*

### 2.7 `GET /meta/exchange-rates` — public
Currency multipliers relative to USD, keyed by lowercase code (32 site currencies plus others).

```json
{"data": {"usd": 1, "eur": 0.92, "gbp": 0.79, "aed": 3.67255, "afn": 64.83}}
```
*(live; trimmed)*

### 2.8 `GET /me` — key required
Account-scoped profile. No market data, but the cheapest definitive key-validity check (returns `200` with a valid key; `401 code 82 "invalid api key"` otherwise).

### 2.9 Other documented operations (csfloatapi.com)
Buying/selling/offers/trades/account routes exist (46 total). Read routes are rate-limit-generous; mutation routes are reportedly ~two orders of magnitude tighter. Out of scope for a data review.

---

## 3. Skinport

Base: `https://api.skinport.com/v1`

**Conventions**
- All documented data endpoints are **public** (no auth). Account/websocket categories need OAuth and are out of scope.
- Money: **decimal major units** in the requested currency. Docs default to `EUR`; request `currency=USD` explicitly.
- `Accept-Encoding: br` header is **required** (Brotli).
- Rate limit: **8 requests / 5 minutes**; responses cached server-side for 5 minutes (`out-of-stock`: 1 hour). One call per endpoint per cache window is effectively the ceiling.

### 3.1 `GET /v1/items?app_id=730&currency=USD&tradable=true` — public
Supply snapshot per item: listing count + price spread + Steam-reference `suggested_price`.

```json
[
  {
    "market_hash_name": "AK-47 | Aquamarine Revenge (Battle-Scarred)",
    "version": null,
    "currency": "USD",
    "suggested_price": 13.18,
    "item_page": "https://skinport.com/item/csgo/ak-47-aquamarine-revenge-battle-scarred",
    "market_page": "https://skinport.com/market/730?cat=Rifle&item=Aquamarine+Revenge",
    "min_price": 11.33, "max_price": 18.22,
    "mean_price": 12.58, "median_price": 13.37,
    "quantity": 25,
    "created_at": 1535988253, "updated_at": 1568073728
  },
  {
    "market_hash_name": "★ M9 Bayonet | Fade (Factory New)",
    "currency": "USD", "suggested_price": 319.11,
    "min_price": null, "max_price": null, "mean_price": null, "median_price": null,
    "quantity": 0, "created_at": 1535988302, "updated_at": 1568073725
  }
]
```
*(docs; `created_at`/`updated_at` are Unix seconds; zero-supply items return null prices)*

`version` disambiguates pattern variants (e.g. `"Emerald"` for Gamma Doppler).

### 3.2 `GET /v1/sales/history?app_id=730&currency=USD[&market_hash_name=…]` — public
Trailing sale aggregates per item over four overlapping windows. Without `market_hash_name`, returns every item.

```json
[
  {
    "market_hash_name": "Glove Case",
    "version": null, "currency": "USD",
    "item_page": "https://skinport.com/item/glove-case",
    "market_page": "https://skinport.com/market?item=Glove%20Case&cat=Container",
    "last_24_hours": {"min": 5.00, "max": 6.38, "avg": 5.90,  "median": 5.96, "volume": 118},
    "last_7_days":   {"min": 5.00, "max": 6.43, "avg": 5.83,  "median": 5.96, "volume": 730},
    "last_30_days":  {"min": 4.19, "max": 6.45, "avg": 5.61,  "median": 5.58, "volume": 5282},
    "last_90_days":  {"min": 2.82, "max": 6.45, "avg": 5.36,  "median": 5.41, "volume": 14521}
  }
]
```
*(docs; nulls and `volume: 0` for items with no sales in a window)*

Note: windows overlap; day-over-day deltas of the cumulative volumes approximate daily sales counts.

### 3.3 `GET /v1/sales/out-of-stock?app_id=730&currency=USD` — public
Items with recent sales history but **zero current supply** — a direct scarcity list. Cached 1 hour.

```json
[
  {"market_hash_name": "Souvenir AWP | Desert Hydra (Factory New)",
   "version": null, "currency": "USD",
   "suggested_price": 9995.66, "avg_sale_price": 6287.45, "sales_last_90d": 6},
  {"market_hash_name": "★ Butterfly Knife | Gamma Doppler (Factory New)",
   "version": "Emerald", "currency": "USD",
   "suggested_price": 15110.53, "avg_sale_price": 11786.21, "sales_last_90d": 2}
]
```
*(docs)*

---

## 4. market.csgo.com

Base: `https://market.csgo.com/api/v2/` (v2 endpoints) and `https://market.csgo.com/api/` (bulk files)

**Conventions**
- Auth: API key from the user cabinet, passed as a **`key` query parameter** (never a header). The key grants access to trading and some data routes; bulk files below are keyless.
- Money: integer USD **mills** (thousandths) in keyed listing endpoints — `26935` = $26.935 (verified against the decimal price file). The public `prices/USD.json` returns decimal USD with three decimals.
- **Hard rate limit: more than 5 requests/second and the key is deleted** (per docs). An API activity log exists at `market.csgo.com/en/api/log`.
- Docs are a JS app; the sample `full-export` filename in them is stale and 404s — always resolve current filenames from the index.

### 4.1 `GET /api/full-export/USD.json` → `/api/full-export/{chunk}.json` — ALL listings, keyless
The index returns the current chunk list plus the column order; each chunk holds 10,000 listings. Verified live: **112 chunks ≈ 1.12M individual listings**, regenerated continuously (index `time` field).

Index *(live, trimmed)*:

```json
{
  "success": true,
  "time": 1792807546,
  "currency": "USD",
  "format": ["price", "id", "market_hash_name", "classid", "instanceid",
             "real_instance", "asset", "old_price", "stamp", "base_id",
             "float", "phase", "paintseed", "paintindex", "stickers",
             "type", "chance_to_transfer", "source", "inspect_certificate"],
  "items": ["17928075706907.json", "17928075708130.json", "…112 files total…"]
}
```

Chunk rows are **positional arrays** in `format` order *(live, first row, labeled)*:

```json
{
  "price": 61,                    // USD mills
  "id": 485802264,                // market.csgo listing id
  "market_hash_name": "Sealed Graffiti | Tilt (Wire Blue)",
  "classid": 1989284963,          // Steam classid — listing key component
  "instanceid": 302028390,        // Steam instanceid
  "real_instance": 302028390,
  "asset": 0,
  "old_price": 0,
  "stamp": "2026-10-24 04:08:56", // when this offer was listed
  "base_id": 0,
  "float": null,                  // float value where applicable
  "phase": "",                    // Doppler/finish phase where applicable
  "paintseed": null,
  "paintindex": null,
  "stickers": "11289205989|11289205989|…" , // sticker ids by slot, or null
  "type": "Graffiti",
  "chance_to_transfer": 80,
  "source": "STEAM",
  "inspect_certificate": "1809A0C3…"        // or null
}
```

In a 500-row sample, 280 rows had floats populated (the rest were non-float item types). `classid_instanceid` is the natural per-listing identity.

### 4.2 `GET /v2/search-item-by-hash-name?key=…&hash_name=…` — key required
Up to 100 current offers for one exact name. Price-per-listing but **no float attributes** — join to full-export rows on `classid`/`instanceid` for depth.

```json
{
  "success": true,
  "currency": "USD",
  "data": [
    {"market_hash_name": "AK-47 | Redline (Field-Tested)", "price": 26935,
     "class": 7993036958, "instance": 9104376351, "count": 1, "source": "STEAM"},
    {"market_hash_name": "AK-47 | Redline (Field-Tested)", "price": 26974,
     "class": 7993036958, "instance": 9126114966, "count": 1, "source": "STEAM"}
  ]
}
```
*(live; `price` in mills; cheapest-first)*

### 4.3 `GET /v2/prices/USD.json` — public
One aggregate price + volume per item, every item, ~2.5MB.

```json
{
  "success": true, "time": 1792806184, "currency": "USD",
  "items": [
    {"market_hash_name": "'Blueberries' Buckshot | NSWC SEAL", "volume": "34",  "price": "10.856"},
    {"market_hash_name": "AK-47 | Redline (Field-Tested)",     "volume": "385", "price": "26.935"}
  ]
}
```
*(live; `price` decimal USD — 26.935 == 26935 mills in §4.2, confirming the unit; `volume` semantics not yet confirmed: sales-count vs listings-count)*

### 4.4 Sales history — key partially verified
- `GET /api/v2/full-history/all.json` — public, ~1.5MB: dictionary mapping every `market_hash_name` to its history `item_id`.

```json
{"history": {"AK-47 | Redline (Field-Tested)": 7929, "Clutch Case": 406261, "…": 0}}
```
*(live, trimmed)*

- `GET /api/v2/history?key=…&item_id=…` — key required. Documented shape *(docs)*:

```json
{
  "time": 1751980096,
  "data": [{
    "id": 406245,
    "max":      {"RUB": 1, "USD": 0.849, "EUR": 0.952},
    "min":      {"RUB": 1, "USD": 0.849, "EUR": 0.952},
    "average":  {"RUB": 1, "USD": 0.850, "EUR": 0.950},
    "average7d":  {"USD": 0, "EUR": 0},
    "average30d": {"USD": 0, "EUR": 0},
    "sales7d":    {"USD": 0, "EUR": 0},
    "sales30d":   {"USD": 0, "EUR": 0},
    "history": [[1715859461, 1, 0.849, 0.952]]
  }]
}
```
`history` rows are `[timestamp, price_rub, price_usd, price_eur]`. **Caveat:** verified 200 with a valid key but returned `data: []` for a live id (AK Redline FT) — id semantics or data availability needs investigation before relying on this endpoint.

### 4.5 `GET /v2/dictionary/names.json` — public
`name_id ↔ market_hash_name` dictionary (~2.9MB), used by their websocket stream.

```json
{"success": true, "time": 1792806184,
 "items": [{"id": "628235", "hash_name": "#CSGO_crate_musickit_masterminds2_capsule"},
           {"id": "63339",  "hash_name": "'Blueberries' Buckshot | NSWC SEAL"}]}
```
*(live, trimmed)*

### 4.6 Dead or gated (verified 2026-10-23)
- `GET /v2/items` — key accepted (`success: true`) but `items: null` across param variants; appears disabled.
- `GET /v2/item` — `404` for every `classid_instanceid` format on fresh listings.
- `GET /v2/prices-classic/USD.json` — `404` with and without key (documented, but gone).
- Websocket (Centrifugo): `/v2/get-ws-token` then subscribe to `public:items:730:usd` for a real-time price/listing firehose; token expires after 10 minutes. Traffic-heavy; noted for completeness.

---

## 5. Cross-source data notes

1. **Join key:** `market_hash_name` is present in every data endpoint of all three sources. Skinport additionally disambiguates pattern variants via `version`; CSFloat and market.csgo encode variants in `paint_index`/`phase`.
2. **Units:** CSFloat cents (÷100), Skinport decimal dollars (as-is), market.csgo mills (÷1000). All verified.
3. **Listing identity:** CSFloat `id` (string) and market.csgo `classid_instanceid` (and `id`) both identify a single offer; Skinport exposes no listing-level data.
4. **Float/pattern attributes:** CSFloat (listings + sales: `float_value`, `paint_seed`, `stickers[]` with per-sticker reference prices) and market.csgo (full-export: `float`, `paintseed`, `paintindex`, `stickers`, `phase`). Skinport: none.
5. **Sales data:** CSFloat offers per-sale records (public, 40/item) and daily aggregates (public, ~5.5y); Skinport offers trailing-window aggregates only; market.csgo's per-item history endpoint is promising but currently returns empty data.
6. **Model/reference prices:** CSFloat `reference.predicted_price` (their own valuation model, on every listing/sale) and Skinport `suggested_price` (Steam reference).

## 6. References

- CSFloat unofficial reference: https://csfloatapi.com — OpenAPI: https://csfloatapi.com/openapi.yaml
- CSFloat archived official docs (stale re: `/listings` auth): https://web.archive.org/web/20260320124433/https://docs.csfloat.com/
- Skinport docs: https://docs.skinport.com — items: /items, sales history: /sales/history, out-of-stock: /sales/out-of-stock
- market.csgo.com docs (JS app): https://market.csgo.com/en/api/content/start — API activity log: https://market.csgo.com/en/api/log
