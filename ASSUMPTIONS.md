# Assumptions

## Definitions

| Term | Definition |
|---|---|
| **Weekly demand** | Next 6 months of forecast (Nov 2026 – Apr 2027) ÷ 26 weeks |
| **Demand by location** | PDCs: Direct demand only. GDC: Direct + Replenishment (its shipments to restock the PDCs) |
| **WOS** | On-hand qty ÷ weekly demand (blank when weekly demand = 0) |
| **Stockout** | On hand = 0 and weekly demand > 0 |
| **Short / Healthy / Excess** | PDCs: < 4 / 4–13 / > 13 weeks. GDC: < 8 / 8–26 / > 26 weeks |
| **No Demand** | Weekly demand = 0 (all 45 have zero demand for the full 24 months) |
| **Extra pallets** | Excess parts: stock above the excess threshold ÷ qpc. No Demand parts: all stock ÷ qpc |
| **Projected stock** | On hand + all open incoming supply for that part + location |
| **Arrives too late** | A Short/Stockout part whose WOS is less than the weeks until its first order arrives |
| **Possible double order** | Same part, destination, source and qty on different POs, arriving within 14 days of each other |

## Data cleaning

| Issue found | What I did | Why |
|---|---|---|
| Part numbers in many formats (`sku16`, `SKU-6`, `SKU0022`, leading spaces) | Standardized to `SKU` + number | Otherwise the files don't join. On the raw data, 99 of 309 inventory rows couldn't find their forecast |
| Location names in many formats (`gdc`, `Global DC`, `PDC-1`, `PDC 3`) | Standardized to GDC / PDC1 / PDC2 / PDC3 | Same reason |
| Numbers stored as text (`"1,103"`, `"277.0"`) | Converted to numbers | Needed for any math |
| Inconsistent demand types (`Replen`, `DIRECT`) and casing in part types / planners | Standardized | So Replenishment rows aren't missed and groupings are clean |
| 5 exact duplicate inventory rows, 2 exact duplicate demand rows | Removed | Identical in every field, so treated as export errors, not real extra stock or demand |
| 4 repeated PO lines (same PO + line number) | Removed | A PO + line uniquely identifies an order line |
| 4 negative on-hand quantities (SKU46 GDC, SKU52 PDC1, SKU75 PDC1, SKU92 PDC2) | Set to 0, flagged | Negative stock isn't possible; likely a late transaction the planner should check |
| 6 negative forecast values | Set to 0 | Negative demand isn't meaningful here |
| 42 blank forecast months | Filled with that row's average month | Blank is more likely missing data than zero demand; filling with 0 would overstate WOS |
| ETA dates in 4 formats | Parsed all of them | |
| 3 parts with missing or zero qpc (SKU5, SKU34, SKU57) | Left blank | WOS still works; they're left out of pallet totals |
| SKU901, SKU902 (inventory) and SKU903 (supply) not in the parts master | Kept and flagged | They're real stock/orders; the parts master should be updated |
| SKU6 listed twice in the parts master | Kept one | |

## Key assumptions

- **The forecast is correct as given.** I didn't adjust it or check its accuracy.
- **6-month demand window.** I tested 3 vs 6 months. Most parts change little (median ~10%), but replenishment demand is lumpy (46% of its months are zero), and a 3-month window missed big restocking waves. Example: SKU98 at the GDC shows 65 weeks with 3 months vs. 14 weeks with 6 months, and it would actually run out around March.
- **Thresholds.** There is no lead-time data (ETAs exist but no order dates), so the thresholds are informed assumptions: the GDC buys from suppliers (open orders arrive up to ~12 weeks out), so it needs more cover than PDCs restocked from the GDC. They're one setting at the top of `task2_status.py`.
- **All incoming supply counts.** Every open order arrives by Jan 12, 2027, inside the 6-month window. GDC Transfers have already left the GDC, so counting them at the receiving PDC doesn't double count.
- **Pallets.** Every container is a standard pallet (per the README); partially filled pallets aren't modeled.
- **No cost data,** so extra stock is measured in pallets, not dollars.

## What I'd do with more time

- **Time-phased projection:** walk forward month by month (stock − demand + arrivals) instead of using an average rate, so lumpy demand and arrival timing are exact.
- **Per-part thresholds** based on real lead times and demand variability (safety stock), instead of one rule per location type.
- **Add part costs** to size excess and no-demand inventory in dollars.
- **A rebalancing plan:** match each short location to the location with the most extra stock of that part and suggest transfer quantities.
- **Check forecast accuracy** against actual history.