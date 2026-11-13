# Bonus: planning assistant. Ask a question in plain English, get a table/chart back.
# Run: streamlit run assistant.py
#
# How it works:
#   1. Gemini reads the question and picks ONE tool from assistant_tools.py + its inputs
#   2. Python runs that tool on our data (so every number comes from pandas, not the model)
#   3. The app shows the table and a chart

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from assistant_tools import TOOLS

load_dotenv()  # reads GEMINI_API_KEY from the .env file
client = genai.Client()  # picks up GEMINI_API_KEY automatically
MODELS = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-3.8-flash"]

INSTRUCTIONS = """You help a service parts planner explore inventory data.
Always answer by calling exactly ONE of the tools. Never make up numbers.
Locations are GDC, PDC1, PDC2, PDC3. Statuses are Stockout, Short, Healthy, Excess, No Demand.
If the question can't be answered with the tools, say so briefly."""

config = types.GenerateContentConfig(
    system_instruction=INSTRUCTIONS,
    tools=list(TOOLS.values()),  # the SDK reads each function's inputs + docstring
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    ),  # I run the tool myself
)

# charts to draw for each tool (filter_parts is just a table)
CHARTS = {
    "status_breakdown": st.bar_chart,
    "demand_chart": st.line_chart,
    "pallets_by_status": st.bar_chart,
}


def answer(question):
    # ask Gemini which tool to use; if a model is busy (503), try the next one
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model, contents=question, config=config
            )
            break
        except Exception as e:
            if model == MODELS[-1]:
                raise e  # every model failed -> show the error
    if not response.function_calls:
        return {"text": response.text}  # no tool fits -> show the model's reply

    call = response.function_calls[0]
    args = dict(call.args or {})
    result = TOOLS[call.name](**args)  # run the real pandas function
    label = ", ".join(f"{k}={v}" for k, v in args.items())
    return {
        "text": f"Ran `{call.name}({label})` — {len(result)} rows",
        "table": result,
        "tool": call.name,
    }


def show(msg):
    # draw one answer: text, then chart (if any), then the table
    st.markdown(msg["text"])
    if "table" in msg:
        if msg["tool"] in CHARTS and len(msg["table"]) > 0:
            CHARTS[msg["tool"]](msg["table"])
        st.dataframe(msg["table"])


st.title("Service Parts Planning Assistant")
st.caption(
    "Try: “Show me all Excess parts for Sofia Novak at PDC2” · “Break down status by part type at the GDC” · "
    "“Chart the 24-month demand for SKU98” · “How many pallets of no-demand inventory sit at each location?”"
)

# keep the chat history between questions
if "history" not in st.session_state:
    st.session_state.history = []

for role, msg in st.session_state.history:
    with st.chat_message(role):
        show(msg)

question = st.chat_input("Ask about inventory, status, demand or pallets")
if question:
    st.session_state.history.append(("user", {"text": question}))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            msg = answer(question)
        except Exception as e:
            msg = {"text": f"Something went wrong: {e}"}
        show(msg)
    st.session_state.history.append(("assistant", msg))
