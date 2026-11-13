# Task 4: check if incoming supply fixes the problems from Task 2 (or makes them worse).

import os
import pandas as pd
from clean import sup
from task2_status import wos, get_status

SNAPSHOT = pd.Timestamp("2026-10-22")
BAD = ["Stockout", "Short"]

# 1) total incoming qty + earliest arrival date per part + destination
incoming = sup.groupby(["part_number", "destination"], as_index=False).agg(
    incoming_qty=("qty", "sum"), first_eta=("eta_date", "min")
)
incoming = incoming.rename(columns={"destination": "location"})

# outer join so supply going to a part-location with no stock/demand isn't dropped
df = wos.merge(incoming, on=["part_number", "location"], how="outer")
df[["on_hand_qty", "weekly_demand", "incoming_qty"]] = df[
    ["on_hand_qty", "weekly_demand", "incoming_qty"]
].fillna(0)
df["status"] = df["status"].fillna(
    "No Demand"
)  # supply-only rows (like SKU903) have no demand

# 2) projected stock + WOS once everything lands, then re-run the same status rules
after = df.copy()
after["on_hand_qty"] = df["on_hand_qty"] + df["incoming_qty"]
after["wos"] = after["on_hand_qty"] / after["weekly_demand"].where(
    after["weekly_demand"] > 0
)
df["projected_wos"] = after["wos"].round(1)
df["status_after"] = after.apply(get_status, axis=1)

# 3) timing: does the supply land before the part runs out?
df["weeks_to_arrival"] = ((df["first_eta"] - SNAPSHOT).dt.days / 7).round(1)
df["arrives_too_late"] = (
    df["status"].isin(BAD)
    & (df["incoming_qty"] > 0)
    & (df["wos"].fillna(0) < df["weeks_to_arrival"])
)

# 4) flag the issues
no_help = df[df["status"].isin(BAD) & (df["incoming_qty"] == 0)]
too_late = df[df["arrives_too_late"]]
adds_excess = df[
    (df["incoming_qty"] > 0) & df["status_after"].isin(["Excess", "No Demand"])
]

# possible double orders: same part, place, source + qty arriving within 2 weeks of each other
# (regular repeat orders are usually spaced a month+ apart, so 2 weeks looks like a duplicate)
s = sup.sort_values("eta_date")
s["days_since_prev"] = (
    s.groupby(["part_number", "destination", "source", "qty"])["eta_date"]
    .diff()
    .dt.days
)
double_orders = s[s["days_since_prev"] <= 14][
    [
        "po_number",
        "part_number",
        "destination",
        "source",
        "qty",
        "eta_date",
        "days_since_prev",
    ]
]

# rebalance: still short at one DC after supply, but excess at another
short_parts = set(df.loc[df["status_after"].isin(BAD), "part_number"])
excess_parts = set(df.loc[df["status_after"] == "Excess", "part_number"])
rebalance = df[
    df["part_number"].isin(short_parts & excess_parts)
    & df["status_after"].isin(BAD + ["Excess"])
]


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/task4_supply_review.csv", index=False)
    print("saved output/task4_supply_review.csv\n")

    print("status BEFORE vs AFTER incoming supply:")
    print(pd.crosstab(df["status"], df["status_after"], margins=True), "\n")

    cols = [
        "part_number",
        "location",
        "status",
        "wos",
        "weekly_demand",
        "incoming_qty",
        "weeks_to_arrival",
        "status_after",
    ]
    print(f"1) Short/Stockout with NO supply coming: {len(no_help)}")
    print(
        no_help.sort_values("weekly_demand", ascending=False)[cols]
        .head(5)
        .to_string(index=False),
        "\n",
    )
    print(f"2) Supply arrives AFTER the part runs out: {len(too_late)}")
    print(
        too_late.sort_values("weekly_demand", ascending=False)[cols]
        .head(5)
        .to_string(index=False),
        "\n",
    )
    print(
        f"3) Supply landing where stock is already Excess/No Demand: {len(adds_excess)}"
    )
    print(
        adds_excess.sort_values("incoming_qty", ascending=False)[cols]
        .head(5)
        .to_string(index=False),
        "\n",
    )
    print(f"4) Possible double orders: {len(double_orders)}")
    print(double_orders.to_string(index=False), "\n")
    print(
        f"5) Parts short at one DC but excess at another (after supply): {len(short_parts & excess_parts)}"
    )
    print(
        rebalance.sort_values(["part_number", "status_after"])[
            ["part_number", "location", "status_after", "projected_wos"]
        ]
        .head(10)
        .to_string(index=False)
    )
