# Task 3: WOS Summary by DC

**Code:** `task3_summary.py` (uses the statuses from `task2_status.py`)
**Output:** `output/task3_dc_summary.csv` (one row per location)

## The question

The planning manager wants one view per location (GDC, PDC1, PDC2, PDC3). Each location has 73–97 part-level WOS numbers, so I need to combine them up into a summary that isn't misleading.

## Roll-ups I considered (and why I didn't use them)

**Total on-hand pieces / total weekly demand.** This adds up pieces across different parts, but a bolt and a windshield aren't comparable units. High-volume fasteners (some with 10,000+ pieces) would dominate the number, so a DC could show "20 weeks of supply" while a big share of its parts are stocked out.

**Average WOS across parts.** Averages get pulled around by extremes. One part with 100 weeks of supply drags the number up and hides many parts sitting at 0. It also can't cleanly include No Demand parts, which have no WOS.

## What I report instead

For each DC:

1. **Status mix (% of parts in each status).** This is the main view. It tells the manager directly *where the problems are* (ex: "20% of PDC1's parts are stocked out").
2. **Median WOS.** How many weeks of cover a *typical* part has. The median isn't skewed by a few extreme parts. Stockouts count as 0 weeks; No Demand parts are left out since they have no WOS.
3. **Extra pallets.** How much warehouse space is taken up by stock nobody needs right now:
   - For **Excess** parts, only the stock *above* the excess threshold counts as extra.
   - For **No Demand** parts, all of the stock is extra.
   - Pieces are converted to pallets using `qpc` (pieces per pallet) from the parts list.

This turns "too much stock" into something physical the team can act on (space to free up), and it's the closest thing to a cost measure since the data doesn't include part prices.

## Results

| Location | Parts | Stockout | Short | Healthy | Excess | No Demand | Median WOS | Extra pallets |
|---|---|---|---|---|---|---|---|---|
| GDC | 97 | 5% | 37% | 30% | 19% | 9% | 8.8 wks | 728 |
| PDC1 | 84 | **20%** | 25% | **18%** | 20% | 17% | **2.8 wks** | 267 |
| PDC2 | 91 | 13% | 26% | 22% | 24% | 14% | 6.6 wks | 568 |
| PDC3 | 73 | 18% | 22% | **38%** | 10% | 12% | 5.0 wks | 243 |

## Takeaways for the planning manager

- **PDC1 needs the most attention.** It has the highest stockout rate (20%), the fewest Healthy parts (18%), and a typical part has under 3 weeks of cover.
- **The GDC has few stockouts (5%) but 37% of its parts are Short.** Since the GDC restocks the PDCs, shortages here will spread to the PDCs if they aren't fixed.
- **The GDC and PDC2 hold the most extra stock** (728 and 568 pallets). The GDC's comes mostly from Excess parts ( around 590 pallets), so there's room to slow down or redirect orders.
- **PDC3 is the healthiest PDC** (38% Healthy, only 10% Excess), but most of its extra pallets ( around 209 of 243) are No Demand stock that could be cleared out.

## Limitations / what I'd do with more time

- **No cost data.** With unit costs, I'd add the **dollar value** of Excess and No Demand inventory, which is usually what leadership cares about most.
- **5 part-locations are missing a pallet quantity** (SKU5, SKU34, and the unknown SKU901/902), so they're left out of the pallet totals.
- Pallet counts assume every container is a standard pallet (as the README says) and don't account for partially filled pallets.
- I'd also break the summary down by **part type** and **planner** so each planner can see their own problem parts.