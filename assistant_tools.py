# The 4 tools the planning assistant can call.
# The LLM only picks a tool + fills in the inputs. All numbers come from these
# pandas functions, never from the model.
# (Gemini reads each function's name, inputs and docstring to decide which to use.)

import pandas as pd
from clean import dem, months
from task4_supply import (
    df,
)  # one row per part + location with WOS, status, planner, part type...

df = df.copy()
df["pallets"] = (
    df["on_hand_qty"] / df["qpc"]
)  # pieces -> pallets (blank if qpc is missing)


def match(col, value):
    # case-insensitive filter that is skipped when the value is empty
    if not value:
        return pd.Series(True, index=df.index)
    return df[col].fillna("").str.lower() == value.lower()


def filter_parts(
    status: str = "", location: str = "", planner: str = "", part_type: str = ""
):
    """List part-locations that match the filters. Leave a filter empty to skip it.
    status: Stockout, Short, Healthy, Excess or No Demand.
    location: GDC, PDC1, PDC2 or PDC3.
    planner: planner's full name, e.g. Sofia Novak.
    part_type: e.g. Brake, Glass, HVAC, Fastener."""
    rows = df[
        match("status", status)
        & match("location", location)
        & match("planner", planner)
        & match("part_type", part_type)
    ]
    cols = [
        "part_number",
        "location",
        "planner",
        "part_type",
        "on_hand_qty",
        "weekly_demand",
        "wos",
        "status",
        "incoming_qty",
        "status_after",
    ]
    return (
        rows[cols]
        .sort_values(["location", "part_number"])
        .round(1)
        .reset_index(drop=True)
    )


def status_breakdown(location: str = "", by: str = "part_type"):
    """Count part-locations in each status, grouped by part_type, planner or location.
    location: GDC, PDC1, PDC2 or PDC3 (empty = all locations)."""
    rows = df[match("location", location)]
    order = ["Stockout", "Short", "Healthy", "Excess", "No Demand"]
    table = pd.crosstab(rows[by], rows["status"])
    return table.reindex(columns=[s for s in order if s in table.columns])


def demand_chart(part_number: str):
    """24-month demand forecast for one part (e.g. SKU98), one column per location.
    GDC demand includes its replenishment shipments to the PDCs."""
    rows = dem[
        dem["part_number"].str.lower()
        == part_number.lower().replace("-", "").replace(" ", "")
    ]
    return (
        rows.groupby("location")[months].sum().T.round(0)
    )  # months as rows so it charts as lines


def pallets_by_status(status: str = "No Demand"):
    """Total pallets of on-hand stock at each location for parts in one status
    (Stockout, Short, Healthy, Excess or No Demand)."""
    rows = df[match("status", status)]
    return rows.groupby("location")[["pallets"]].sum().round(0)


# name -> function, so the app can run whichever tool the model picks
TOOLS = {
    f.__name__: f
    for f in [filter_parts, status_breakdown, demand_chart, pallets_by_status]
}
