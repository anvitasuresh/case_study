# Task 3: one summary row per DC (GDC, PDC1, PDC2, PDC3).

# Instead of adding up pieces, report the status mix + median WOS + pallets of extra stock

import os
from task2_status import wos, THRESHOLDS

STATUSES = ["Stockout", "Short", "Healthy", "Excess", "No Demand"]

# --- pallets of extra stock ---
# Excess parts: only the stock ABOVE the excess threshold is extra
# No Demand parts: all of this stock is extra
max_weeks = wos["location"].map(
    lambda loc: THRESHOLDS["GDC"][1] if loc == "GDC" else THRESHOLDS["PDC"][1]
)
wos["extra_qty"] = 0.0
is_excess = wos["status"] == "Excess"
is_no_demand = wos["status"] == "No Demand"

# extra stock = what we have − the most we should have
wos.loc[is_excess, "extra_qty"] = wos["on_hand_qty"] - max_weeks * wos["weekly_demand"]
wos.loc[is_no_demand, "extra_qty"] = wos["on_hand_qty"]
wos["extra_pallets"] = (
    wos["extra_qty"] / wos["qpc"]
)  # qpc = pieces per pallet (blank qpc -> skipped)

# --- build the summary table, one row per location ---
summary = wos.pivot_table(
    index="location",
    columns="status",
    values="part_number",
    aggfunc="count",
    fill_value=0,
)[STATUSES]
summary["Total parts"] = summary.sum(axis=1)

# turn counts into % of parts at that location
for s in STATUSES:
    summary[s + " %"] = (summary[s] / summary["Total parts"] * 100).round(0)

# median WOS of parts that have demand (stockouts count as 0 weeks)
summary["Median WOS (wks)"] = wos.groupby("location")["wos"].median().round(1)

# pallets of extra stock (excess + no demand)
summary["Extra pallets"] = wos.groupby("location")["extra_pallets"].sum().round(0)

summary = summary[
    ["Total parts"]
    + [s + " %" for s in STATUSES]
    + ["Median WOS (wks)", "Extra pallets"]
]


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    summary.to_csv("output/task_3_dc_summary.csv")
    print("saved output/task_3_dc_summary.csv\n")
    print(summary.to_string())
