# Task 1: Weeks of Supply (WOS)

**Code:** `clean.py` (data cleaning) → `task1_wos.py` (WOS calculation)
**Output:** `output/task1_wos.csv` (one row per part + location, 345 rows)

## What WOS means

WOS answers: *if we stopped receiving stock today, how many weeks would the current inventory last?*

```
WOS = on-hand quantity / average weekly demand
```

Example: SKU10 at the GDC has 14 pieces on hand and uses about 8 per week, so it has 14 / 8 ≈ **1.7 weeks** of supply.

## Step 0: Cleaning the data first

Before calculating anything, I cleaned the inputs. WOS depends on matching each part's inventory to its demand by part number and location, and the raw formats broke that match. On the raw data, **99 of 309** inventory rows couldn't find their demand forecast. After cleaning, only 33 couldn't, and those genuinely have no demand.

Main fixes:
- Standardized part numbers (`sku16`, `SKU-6`, `SKU0022` → `SKU16`, `SKU6`, `SKU22`) and locations (`gdc`, `Global DC`, `PDC-1` → `GDC`, `PDC1`)
- Converted text numbers like `"1,103"` to numbers
- Removed exact duplicate rows in inventory, demand, and supply (same PO + line = entered twice)
- Set negative on-hand and negative forecasts to 0 (negative on-hand is flagged for the planner)
- Filled blank forecast months with that row's average month (blank = missing data, not zero demand)

## Method

### 1. Which demand counts at each location
- **PDCs:** only their **Direct** demand (customers they serve).
- **GDC:** **Direct + Replenishment**. The GDC also has to ship stock to restock the PDCs, so leaving that out would make the GDC look like it has more supply than it really does.

The Replenishment rows are already stored under `location = GDC`, so grouping demand by part + location adds them to the GDC automatically. Each piece of demand is counted once, at the location that has to supply it.

### 2. Weekly demand = next 6 months of forecast / 26 weeks

I used the **next 6 months** of the forecast (Nov 2026 – Apr 2027), not the full 24 months, so WOS reflects near-term demand.

**Why 6 months and not 3:** I tested both.
- For most parts the difference is small (median change in WOS of about 10%).
- But replenishment demand is lumpy: **46%** of replenishment months are 0, with big shipments in between.
- Example: **SKU98 at the GDC** has 1,540 on hand. A 3-month window gives **65 weeks** of supply (looks like excess), because it misses the ~720/month restocking shipments to PDC2 that start in February. The 6-month window gives **14 weeks**, which is much closer to reality (the stock would actually run out around March).

A 3-month window can miss these waves entirely, so 6 months is safer while still focusing on the near term.

### 3. Edge cases
- **Demand = 0:** WOS can't be calculated (divide by zero), so it's left blank and labeled **No Demand** in Task 2.
- **On hand = 0 but demand > 0:** WOS = 0 (a stockout).
- I used an **outer join** of inventory and demand, so part-locations that have demand but no inventory record are kept (they're stockouts, not missing data).

## Results

| Location | Part-locations | Median WOS (weeks) |
|---|---|---|
| GDC | 97 | 8.8 |
| PDC1 | 84 | 2.8 |
| PDC2 | 91 | 6.6 |
| PDC3 | 73 | 5.0 |

- **345** part-locations in total
- **47** have demand but zero stock (already stocked out)
- **45** have no demand in the next 6 months (in fact, none for the full 24 months)

## Limitations / what I'd do with more time
- **Time-phased WOS:** instead of an average rate, walk forward month by month and subtract each month's forecast until the stock runs out. This handles lumpy demand like SKU98 exactly.
- The forecast is taken as given. With history, I'd check forecast accuracy and how variable demand is.