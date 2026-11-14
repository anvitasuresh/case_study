# Service Parts Inventory Health Check

Weeks of supply, inventory status and an incoming supply review for one GDC and three PDCs.

## Setup

Python 3.9+ with pandas and openpyxl:

```bash
pip install pandas openpyxl
```

Put the four input files in `data/`:
`parts.csv`, `demand_forecast_monthly.csv`, `inventory_on_hand.csv`, `incoming_supply.csv`

## How to run

Each script builds on the one before it (it imports the previous step), so any of them can be run on its own:

| Step | Command | What it does | Output |
|---|---|---|---|
| 0 | `python clean.py` | Cleans all 4 files and prints a short data-quality check | (printed) |
| 1 | `python task1_wos.py` | Weeks of supply per part + location | `output/task1_wos.csv` |
| 2 | `python task2_status.py` | Inventory status per part + location | `output/task2_inventory_status.csv` |
| 3 | `python task3_summary.py` | One summary row per DC | `output/task3_dc_summary.csv` |
| 4 | `python task4_supply.py` | Projected status after incoming supply + top issues | `output/task4_supply_review.csv` |
| – | `python export_excel.py` | Runs everything and saves all results in one workbook | `output/inventory_health_check.xlsx` |

`python export_excel.py` runs every step and saves the final workbook. The per-step CSVs are only written when you run those scripts directly.


## Bonus: planning assistant

A Streamlit chat app where a planner asks questions in plain English (e.g. "Show me all Excess parts for Sofia Novak at PDC2"). Gemini only picks one of four pandas functions in assistant_tools.py and fills in its inputs; the app runs that function on the data and shows the table and chart, so every number comes from the code, not the model.

```bash
pip install google-genai streamlit python-dotenv
echo "GEMINI_API_KEY=your-key-here" > .env     # free key from Google AI Studio; .env is git-ignored
streamlit run assistant.py
```

- see `screenshots/` to see the assistant UI and 3 questions it responded to

## Other files

- `task1_wos.md` – `task4_supply.md`: method and results for each task
- `ASSUMPTIONS.md`: definitions, data cleaning, assumptions, and what I'd do with more time
- `Service Parts Inventory Health Check.pdf`: 5-slide summary for the planning manager