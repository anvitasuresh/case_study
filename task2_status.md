# Task 2: Inventory Status

**Code:** `task2_status.py` (uses the WOS table from `wos.py`)
**Output:** `output/task2_inventory_status.csv` (WOS + status for all 345 part-locations)

## Why a status metric

WOS is just a number. The planner needs a label that says what to do with each part, so every part-location gets one of five statuses you see bwlow. 

## Status definitions

| Status | Rule | What it means for the planner |
|---|---|---|
| **Stockout** | On hand = 0 and demand > 0 | Already can't fill orders. Act now. |
| **Short** | WOS below the short threshold | Will likely run out before new stock can arrive |
| **Healthy** | WOS between the thresholds | Enough stock, not too much |
| **Excess** | WOS above the excess threshold | Too much stock: money and warehouse space tied up |
| **No Demand** | Weekly demand = 0 | Nobody needs it. Candidate to move or scrap. |

The rules are checked in that order (No Demand first, then Stockout, Short, Excess, otherwise Healthy), so every part-location gets exactly one status.

## Thresholds

| Location | Short if WOS below | Healthy | Excess if WOS above |
|---|---|---|---|
| **PDC1 / PDC2 / PDC3** | 4 weeks | 4–13 weeks | 13 weeks |
| **GDC** | 8 weeks | 8–26 weeks | 26 weeks |

### Why different thresholds for the GDC and PDCs
They get restocked differently, so they need different amounts of cover:
- **Short threshold ≈ how long it takes to get more stock.** PDCs are restocked from the GDC, which is relatively fast, so about **1 month** of cover is enough. The GDC buys from suppliers, which is slower. The open supplier orders arrive up to ~12 weeks out, so the GDC needs about **2 months** of cover.
- **Excess threshold = a reasonable planning horizon.** More than a quarter (13 weeks) at a PDC, or more than half a year (26 weeks) at the GDC, ties up cash and space. 26 weeks also matches the 6-month demand window used for WOS.
- Using one set of thresholds everywhere would either flag the GDC as short all the time or let the PDCs hold far too much.

The thresholds are one setting at the top of `status.py`, so they're easy to change if the team uses different targets.

## Results

| Location | Stockout | Short | Healthy | Excess | No Demand | Total |
|---|---|---|---|---|---|---|
| GDC | 5 | 36 | 29 | 18 | 9 | 97 |
| PDC1 | 17 | 21 | 15 | 17 | 14 | 84 |
| PDC2 | 12 | 24 | 20 | 22 | 13 | 91 |
| PDC3 | 13 | 16 | 28 | 7 | 9 | 73 |
| **Total** | **47** | **97** | **92** | **64** | **45** | **345** |

**Takeaways:**
- **Only 92 of 345 (27%) are Healthy.** 144 (42%) are Stockout or Short, so the network is more at risk of running out than of overstocking.
- **PDC1 is in the worst shape:** 17 stockouts and only 15 Healthy parts out of 84.
- **45 part-locations have no demand for the full 24-month forecast.** 39 of them still have stock sitting in a warehouse (dead stock).
- **43 of 102 parts are Short or Stocked out at one location but Excess at another.** That points to rebalancing stock between DCs instead of buying more (covered in Task 4).

## Limitations / what I'd do with more time
- **No lead-time data:** the file has ETAs but not order dates, so I couldn't measure actual lead times. The thresholds are informed assumptions.
- With more data, I'd set thresholds **per part** based on its real lead time and how much its demand varies (safety stock), instead of one rule per location type.
- This status uses **current on-hand only**. Task 4 looks at how incoming supply changes the picture.
