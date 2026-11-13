# Task 1: Weeks of Supply (WOS) for current on-hand inventory.
# WOS = on-hand qty / average weekly demand (next 6 months)

import os
import pandas as pd
from clean import parts, inv, dem, months

next_6 = months[:6]  # Nov 2026 - Apr 2027

# 1) total demand per part + location
# Replenishment rows are stored under location = GDC, so grouping by location
# automatically adds them to the GDC's Direct demand (PDCs just get Direct)
demand = dem.groupby(["part_number", "location"], as_index=False)[next_6].sum()

# 2) turn 6 months of demand into a weekly rate (6 months = 26 weeks)
demand["weekly_demand"] = demand[next_6].sum(axis=1) / 26
demand = demand[["part_number", "location", "weekly_demand"]]

# 3) put inventory and demand side by side
# outer join keeps parts that have stock but no demand, AND parts that have
wos = inv.merge(demand, on=["part_number", "location"], how="outer")
wos["on_hand_qty"] = wos["on_hand_qty"].fillna(0)
wos["weekly_demand"] = wos["weekly_demand"].fillna(0)
wos["negative_flag"] = (
    wos["negative_flag"] == True
)  # blanks (no inventory row) -> False

# 4) WOS = on hand / weekly demand
# if weekly demand is 0 I can't divide, so WOS stays blank (-> "No Demand" in task 2)
has_demand = wos["weekly_demand"] > 0
wos.loc[has_demand, "wos"] = wos["on_hand_qty"] / wos["weekly_demand"]

# 5) add part details (type, planner, qpc) so we can filter/group later
wos = wos.merge(
    parts[["part_number", "part_type", "planner", "qpc"]], on="part_number", how="left"
)

wos = wos.sort_values(["location", "part_number"]).round({"weekly_demand": 1, "wos": 1})


if __name__ == "__main__":
    # save the full table
    os.makedirs("output", exist_ok=True)
    wos.to_csv("output/task1_wos.csv", index=False)
    print("saved all", len(wos), "rows to output/task1_wos.csv\n")

    print(wos.head(10).to_string(index=False))
    print("\ntotal part-locations:", len(wos))
    print("no demand (WOS blank):", wos["wos"].isna().sum())
    print(
        "zero on hand but has demand:", ((wos["on_hand_qty"] == 0) & has_demand).sum()
    )
