# Take-Home: Service Parts Inventory Health Check

## Scenario
You've joined a service parts planning team. The network has **one Global Distribution Center (GDC)** and **three Parts Distribution Centers (PDC1, PDC2, PDC3)**. Each location serves its own direct demand, and the GDC also replenishes the PDCs.

The planning manager wants to know, for every SKU at every location:
- How many **weeks of supply** do we have today?
- What happens once the **incoming supply** lands?
- Which SKUs are short, healthy, in excess, or sitting with no demand at all?

## Data (`data/`)
| File | Description |
|---|---|
| `parts.csv` | Part master: `part_number`, `part_description`, `part_type`, `planner`, `qpc` (quantity per container; assume every container is a **standard pallet**) |
| `demand_forecast_monthly.csv` | Monthly demand forecast per part and location for the **next 24 months** (Nov 2026 to Oct 2028), one column per month. `demand_type` is **Direct** (customer demand served from that location) or **Replenishment** (the GDC's planned shipments to restock a PDC; `ship_to` shows which PDC) |
| `inventory_on_hand.csv` | Current on-hand quantity per part and location (snapshot 2026-10-22) |
| `incoming_supply.csv` | Open incoming supply per part and destination, with ETA. `source` is a supplier PO or a GDC Transfer (already shipped from the GDC, in transit) |

All quantities are in **pieces** (eaches).

## Tasks
1. **Calculate Weeks of Supply (WOS)** for the **current on-hand** inventory of every part and location. Explain your method.
2. **Define an inventory status metric** (for example Stockout / Short / Healthy / Excess / No Demand; your call). Set the thresholds, justify them, and classify every part and location.
3. **Summarize WOS at the DC level.** How would you report one view per location (GDC, PDC1, PDC2, PDC3) to the planning manager? Explain why you chose that roll-up.
4. **Review the incoming supply** against your findings, and **recommend** what the planner should do about the top issues. Keep it short.

## Bonus: Planning assistant (optional)
Build a simple assistant (CLI, notebook widget, Streamlit, or similar) that lets a planner ask questions in plain English and **quickly get answers, charts and breakdowns**. For example:
- "Show me all Excess parts for *&lt;planner&gt;* at PDC2"
- "Break down status by part type at the GDC"
- "Chart the 24-month demand for part *&lt;part_number&gt;* across locations"
- "How many pallets of no-demand inventory sit at each location?"

You can use an LLM (with tool or function calling) or a rule-based approach. The numbers must come from your data and code, not from the model. Include a short demo (screenshots or a 2-minute recording) and **do not commit API keys**.

## Deliverables
- Code (notebook or scripts) with a short `README` explaining how to run it
- Output file (Excel or CSV) with WOS and status per part and location
- A 1-page summary or 3–5 slides for the planning manager
- `ASSUMPTIONS.md`: your definitions, any assumptions you made, and what you'd do with more time

## Guidelines
- **Time:** about 3–4 hours for the core tasks, plus 1–2 hours if you attempt the bonus. Please don't go far beyond that.
- **Tools:** use any language and tools you like, including AI coding assistants.
- **Reasoning counts:** clear reasoning and stated assumptions matter more than polish. An incomplete solution with sound reasoning is better than a complete one without it.
- **Next step:** a 30-minute follow-up call to walk through your work.
