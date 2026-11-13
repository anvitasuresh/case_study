# Puts all the results into one Excel file for the planning manager.
# Run this last: python export_excel.py

import pandas as pd
from task3_summary import (
    summary,
)  # importing task3 first also adds extra_pallets to each row
from task4_supply import df, double_orders

# main sheet: one row per part + location with WOS, status, and the supply review
cols = [
    "part_number",
    "location",
    "part_type",
    "planner",
    "qpc",
    "on_hand_qty",
    "negative_flag",
    "weekly_demand",
    "wos",
    "status",
    "incoming_qty",
    "first_eta",
    "weeks_to_arrival",
    "projected_wos",
    "status_after",
    "arrives_too_late",
    "extra_pallets",
]
main = df[cols].sort_values(["location", "part_number"])
main["first_eta"] = main[
    "first_eta"
].dt.date  # drop the time so Excel shows a clean date
main["negative_flag"] = (
    main["negative_flag"] == True
)  # supply-only rows have no flag -> False
main = main.round(
    {"weekly_demand": 1, "wos": 1, "extra_pallets": 1}
)  # round only for display

# one file, three sheets
with pd.ExcelWriter("output/inventory_health_check.xlsx") as writer:
    main.to_excel(writer, sheet_name="WOS and Status", index=False)
    summary.to_excel(writer, sheet_name="DC Summary")
    double_orders.to_excel(writer, sheet_name="Possible Double Orders", index=False)
