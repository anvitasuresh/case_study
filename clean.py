# Step 0: clean the 4 input files so they can be joined correctly.

import re
import pandas as pd

# ---------- helper functions ----------


def clean_part(p):
    # standardize: 'sku16', ' SKU-6', 'SKU0022' -> 'SKU16', 'SKU6', 'SKU22'
    num = re.search(r"\d+", str(p)).group()
    return "SKU" + str(int(num))


def clean_loc(x):
    # standardize:'gdc', 'Global DC', 'PDC-1', 'pdc 3' -> 'GDC', 'PDC1', 'PDC3'
    if pd.isna(x):
        return x
    x = str(x).upper().replace(" ", "").replace("-", "")
    return "GDC" if x in ("GDC", "GLOBALDC") else x


def to_num(x):
    # standardize: '1,103' -> 1103.0   (blanks stay blank)
    if pd.isna(x):
        return None
    return float(str(x).replace(",", ""))


# now clean each csv file
# ---------- parts master ----------
parts = pd.read_csv("data/parts.csv", dtype=str)
parts["part_number"] = parts["part_number"].apply(clean_part)
parts["part_type"] = parts["part_type"].str.strip().str.title()
parts["planner"] = parts["planner"].str.strip().str.title()
parts["qpc"] = parts["qpc"].apply(to_num)
parts.loc[parts["qpc"] == 0, "qpc"] = None  # qpc of 0 is invalid -> treat as missing
parts = parts.drop_duplicates("part_number")  # SKU6 was listed twice


# ---------- inventory on hand ----------
inv = pd.read_csv("data/inventory_on_hand.csv", dtype=str)
inv["part_number"] = inv["part_number"].apply(clean_part)
inv["location"] = inv["location"].apply(clean_loc)
inv["on_hand_qty"] = inv["on_hand_qty"].apply(to_num)
inv = inv.drop_duplicates()  # exact copies = export error, don't double count
inv = inv.groupby(["part_number", "location"], as_index=False)["on_hand_qty"].sum()

# negative stock isn't possible -> flag it for the planner, use 0 in the math
inv["negative_flag"] = inv["on_hand_qty"] < 0
inv["on_hand_qty"] = inv["on_hand_qty"].clip(lower=0)


# ---------- demand forecast ----------
dem = pd.read_csv("data/demand_forecast_monthly.csv", dtype=str)
months = list(dem.columns[4:])  # the 24 month columns
dem["part_number"] = dem["part_number"].apply(clean_part)
dem["location"] = dem["location"].apply(clean_loc)
dem["ship_to"] = dem["ship_to"].apply(clean_loc)
dem["demand_type"] = (
    dem["demand_type"].str.strip().str.title().replace({"Replen": "Replenishment"})
)

for m in months:
    dem[m] = dem[m].apply(to_num)

dem = dem.drop_duplicates()  # don't count the same forecast twice
dem[months] = dem[months].clip(lower=0)  # negative demand -> 0

# blank month = missing data, not zero demand -> fill with that row's average month
row_avg = dem[months].mean(axis=1)
for m in months:
    dem[m] = dem[m].fillna(row_avg)


# ---------- incoming supply ----------
sup = pd.read_csv("data/incoming_supply.csv", dtype=str)
sup["part_number"] = sup["part_number"].apply(clean_part)
sup["destination"] = sup["destination"].apply(clean_loc)
sup["qty"] = sup["qty"].apply(to_num)
sup["eta_date"] = pd.to_datetime(
    sup["eta_date"], format="mixed"
)  # handles all 4 date formats
sup = sup.drop_duplicates(
    ["po_number", "po_line"]
)  # same PO + line = entered twice --> drop


# ---------- quick checks (run: python clean.py) ----------
if __name__ == "__main__":
    print("locations:", sorted(inv["location"].unique()))
    print("demand types:", sorted(dem["demand_type"].unique()))
    print(
        "negative on-hand (set to 0):",
        inv[inv["negative_flag"]][["part_number", "location"]].values.tolist(),
    )
    print("missing qpc:", parts[parts["qpc"].isna()]["part_number"].tolist())

    known = set(parts["part_number"])
    print(
        "in inventory but not in parts list:", sorted(set(inv["part_number"]) - known)
    )
    print("in supply but not in parts list:", sorted(set(sup["part_number"]) - known))
