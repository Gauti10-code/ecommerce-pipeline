import os
import json
import openai
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

SCHEMA = """
E-Commerce PostgreSQL Database

ANALYTICS LAYER (use for summary/aggregate questions):
- public_analytics.agg_daily_revenue
    order_date DATE, total_orders BIGINT, total_revenue FLOAT,
    avg_order_value FLOAT, on_time_deliveries BIGINT,
    delivered_orders BIGINT, cancelled_orders BIGINT

- public_analytics.agg_delivery_sla
    customer_state TEXT, total_orders BIGINT,
    avg_delivery_hours FLOAT, on_time_count BIGINT, on_time_pct FLOAT

- public_analytics.agg_seller_performance
    seller_id TEXT, seller_tier TEXT, total_orders BIGINT,
    total_revenue FLOAT, avg_order_value FLOAT,
    total_freight FLOAT, freight_pct FLOAT

MARTS LAYER (use for detailed/entity-level questions):
- public_marts.fct_orders
    order_id TEXT, customer_id TEXT, order_status TEXT,
    order_purchase_timestamp TIMESTAMP, delivered_on_time BOOLEAN,
    delivery_hours FLOAT, total_payment FLOAT, payment_type TEXT,
    total_items BIGINT, total_freight FLOAT

- public_marts.dim_customers
    customer_id TEXT, customer_unique_id TEXT,
    customer_city TEXT, customer_state TEXT,
    total_orders BIGINT, total_spent FLOAT,
    customer_segment TEXT

- public_marts.dim_sellers
    seller_id TEXT, total_orders BIGINT,
    total_revenue FLOAT, avg_order_value FLOAT,
    seller_tier TEXT
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Execute a SQL query on the ecommerce PostgreSQL database and return results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL SELECT query to execute. Always add LIMIT 50 unless asked for all rows.",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


def run_sql(query: str) -> str:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            return "Query returned no results."
        return json.dumps([dict(r) for r in rows], indent=2, default=str)
    except Exception as e:
        return f"SQL Error: {e}"


def ask(client: openai.OpenAI, question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a data analyst for an e-commerce company. "
                "When the user asks a question, write SQL to fetch the data, run it, then explain the results in plain English. "
                "Always prefer the analytics layer for summary questions and marts layer for detail questions. "
                f"\n\nDatabase schema:\n{SCHEMA}"
            ),
        },
        {"role": "user", "content": question},
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                query = json.loads(tool_call.function.arguments)["query"]
                result = run_sql(query)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            return msg.content


