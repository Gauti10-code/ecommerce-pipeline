import os
import openai
import streamlit as st
from dotenv import load_dotenv
from agent import ask, DB_CONFIG
import psycopg2

load_dotenv()


def get_metric(query: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else "N/A"
    except Exception:
        return "N/A"


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="E-Commerce Agent", page_icon="🛒", layout="wide")
st.title("🛒 E-Commerce Data Agent")
st.caption("Ask anything about your pipeline data — powered by GPT-4o + PostgreSQL")

# ── Top KPI metrics ───────────────────────────────────────────────────────────
st.subheader("Pipeline Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = get_metric("SELECT COUNT(*) FROM public_marts.fct_orders")
    st.metric("Total Orders", f"{total_orders:,}" if isinstance(total_orders, int) else total_orders)

with col2:
    total_revenue = get_metric("SELECT ROUND(SUM(total_payment)::numeric, 2) FROM public_marts.fct_orders")
    st.metric("Total Revenue", f"R$ {total_revenue:,}" if isinstance(total_revenue, (int, float)) else total_revenue)

with col3:
    on_time_pct = get_metric("""
        SELECT ROUND(100.0 * SUM(CASE WHEN delivered_on_time THEN 1 ELSE 0 END) / COUNT(*), 1)
        FROM public_marts.fct_orders WHERE delivered_on_time IS NOT NULL
    """)
    st.metric("On-Time Delivery", f"{on_time_pct}%" if on_time_pct != "N/A" else "N/A")

with col4:
    loyal_customers = get_metric("SELECT COUNT(*) FROM public_marts.dim_customers WHERE customer_segment = 'Loyal'")
    st.metric("Loyal Customers", f"{loyal_customers:,}" if isinstance(loyal_customers, int) else loyal_customers)

st.divider()

# ── Chat interface ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            for sql in msg["sql"]:
                with st.expander("SQL Query"):
                    st.code(sql, language="sql")
        if "dataframes" in msg:
            for df in msg["dataframes"]:
                st.dataframe(df, use_container_width=True)

if prompt := st.chat_input("Ask about your data... e.g. Which state has the worst delivery time?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            answer, sql_queries, dataframes = ask(client, prompt)

        st.markdown(answer)
        for sql in sql_queries:
            with st.expander("SQL Query"):
                st.code(sql, language="sql")
        for df in dataframes:
            st.dataframe(df, use_container_width=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sql": sql_queries,
        "dataframes": dataframes,
    })
