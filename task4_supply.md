# Task 4: Incoming Supply Review

**Code:** `task4_supply.py` · **Output:** `output/task4_supply_review.csv`

## Method
1. **Projected stock** = current on hand + all incoming supply (summed per part + location). All open orders land by Jan 12, inside the 6-month demand window, so I count all of them. GDC Transfers have already left the GDC, so adding them to the receiving PDC doesn't double count.
2. **Projected WOS + status** using the same rules as Task 2.
3. **Timing check:** weeks until the first order arrives = (ETA − snapshot) / 7. If a Short/Stockout part's WOS is less than that, the supply **arrives too late** and there's a gap.
4. **Possible double orders:** same part, destination, source and qty arriving **within 2 weeks** of each other on different POs. Regular repeat orders are usually spaced a month or more apart, so this looks like a duplicate.

## Before vs. after supply lands

| Status | Today | After supply |
|---|---|---|
| Stockout | 47 | 31 |
| Short | 97 | 71 |
| Healthy | 92 | 106 |
| Excess | 64 | **92** |

Supply fixes 42 shortages, but it also pushes **28 Healthy/Short part-locations into Excess**. It's going to the wrong places in many cases.

## Top issues + recommendations

**1. Big orders are going to PDC3 while other DCs are stocked out → redirect them.**
- **SKU75:** 5,843 incoming to PDC3 (already healthy), while PDC1 and PDC2 are stocked out and the GDC is short (955/week demand, no supply coming).
- **SKU26:** 1,007 to PDC3, while PDC2 is stocked out and the GDC has only 1.6 weeks left.
- **SKU43:** 4,432 transfer to PDC3 + 2,272 to the GDC, while PDC1 and PDC2 are stocked out.
→ Split or redirect these orders (or transfer onward once they land) to the DCs that need them.

**2. 99 Short/Stockout part-locations have no supply coming → order or expedite.**
Highest-volume: **SKU75, SKU2, SKU26 at the GDC** (500–950 pieces/week). Because the GDC restocks the PDCs, these will spread.

**3. 40 orders arrive after the part runs out → expedite or bridge with a transfer.**
e.g. **SKU98 at PDC2** is stocked out (165/week) and its 1,505 pieces don't arrive for ~12 weeks.

**4. 4 possible double orders → check with purchasing before they land.**
**SKU50 at the GDC** (2 × 1,103 pieces, 5 days apart) is the biggest, and together they push the GDC into Excess. Also SKU4 (PDC3), SKU96 (PDC2), SKU51 (GDC).

**5. 47 parts will still be short at one DC but excess at another → rebalance before buying.**
Transferring between DCs is usually faster and cheaper than a new supplier order.

## Limitations
- Projection adds all supply at once; it doesn't model *when* stock runs out between arrivals (a month-by-month projection would).
- No lead times or costs, so I can't say whether expediting or transferring is cheaper for a given part.
- The 2-week duplicate rule is a heuristic; purchasing would need to confirm.