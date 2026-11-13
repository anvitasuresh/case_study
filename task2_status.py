# Task 2: give every part + location an inventory status based on WOS
# see task2_status.md for justification/explanation

import os
from task1_wos import wos

# thresholds in weeks of supply -> (short if below, excess if above)
# PDCs get restocked from the GDC (fast), so they need less cover.
# The GDC buys from suppliers (slow), so it needs more cover.
THRESHOLDS = {
    "PDC": (4, 13),
    "GDC": (8, 26),
}


def get_status(row):
    # GDC uses the GDC thresholds, PDC1/2/3 all use the PDC ones
    short, excess = THRESHOLDS["GDC"] if row["location"] == "GDC" else THRESHOLDS["PDC"]

    if row["weekly_demand"] == 0:
        return "No Demand"  # nobody needs it -> can't calculate WOS
    if row["on_hand_qty"] == 0:
        return "Stockout"  # demand but nothing on the shelf
    if row["wos"] < short:
        return "Short"
    if row["wos"] > excess:
        return "Excess"
    return "Healthy"


wos["status"] = wos.apply(get_status, axis=1)


if __name__ == "__main__":
    # save the final file (WOS + status for every part + location)
    os.makedirs("output", exist_ok=True)
    wos.to_csv("output/task2_inventory_status.csv", index=False)
    print("saved", len(wos), "rows to output/task2_inventory_status.csv\n")

    # count of each status at each location
    order = ["Stockout", "Short", "Healthy", "Excess", "No Demand"]
    counts = wos.pivot_table(
        index="location",
        columns="status",
        values="part_number",
        aggfunc="count",
        fill_value=0,
    )[order]
    counts["Total"] = counts.sum(axis=1)
    print(counts)
