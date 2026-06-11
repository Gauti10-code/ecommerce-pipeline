markdown# Real-time E-commerce Analytics Pipeline

A production-grade data engineering pipeline that processes 100k+ orders from the Brazilian E-commerce (Olist) dataset using Kafka, Airflow, dbt, and PostgreSQL.

## Architecture
CSV Data (Olist Dataset)
↓
Kafka Producer → Kafka Topics (raw_orders, raw_order_items, raw_customers, raw_payments)
↓
Kafka Consumer → PostgreSQL (ecommerce_raw)
↓
Apache Airflow (Orchestration)
↓
dbt Models → PostgreSQL (ecommerce_staging → ecommerce_marts → ecommerce_analytics)

## Tech Stack

| Tool | Purpose |
|------|---------|
| Apache Kafka | Real-time event streaming |
| Apache Airflow | Pipeline orchestration |
| dbt | Data transformation & testing |
| PostgreSQL | Data warehouse |
| Docker | Kafka & Zookeeper containerization |
| Python | Producer, consumer, DAGs |

## Data Flow

### Layer 1 — Raw (ecommerce_raw)
Exact copy of Kafka messages. Never modified.

### Layer 2 — Staging (ecommerce_staging)
Cleaned and typed data via dbt views:
- `stg_orders` — cleaned order data with proper timestamps
- `stg_order_items` — items per order with float prices
- `stg_customers` — customer profiles
- `stg_payments` — payment records

### Layer 3 — Marts (ecommerce_marts)
Business logic via dbt tables:
- `fct_orders` — one row per order with delivery metrics, payment totals
- `dim_customers` — customer segments (One-time, Returning, Loyal)
- `dim_sellers` — seller tiers (High/Mid/Low Value)

### Layer 4 — Analytics (ecommerce_analytics)
Aggregated reporting tables:
- `agg_daily_revenue` — daily order counts and revenue
- `agg_seller_performance` — seller rankings
- `agg_delivery_sla` — on-time delivery % by state

## Key Metrics
- 99,441 orders processed
- 112,650 order items
- 3,095 unique sellers
- 4 Kafka topics
- 10 dbt models
- 11 data quality tests (all passing)

## Project Structure
ecommerce_pipeline/
├── dags/                    # Airflow DAGs
├── kafka/                   # Producer & Consumer
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── staging/
│   │   ├── marts/
│   │   └── analytics/
│   └── dbt_project.yml
├── docker/                  # Docker compose for Kafka
├── data/                    # Raw CSV files (not committed)
└── requirements.txt

## How to Run

### Prerequisites
- Ubuntu/WSL2
- Docker Desktop
- PostgreSQL
- Python 3.11

### Setup
```bash
# 1. Start Kafka
cd docker && docker compose up -d

# 2. Start PostgreSQL
sudo service postgresql start

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Initialize Airflow
airflow db init
airflow users create --username admin --password admin123 \
  --firstname Eden --lastname Singh --role Admin --email admin@example.com

# 5. Run pipeline manually
python kafka/producer.py
python kafka/consumer.py
cd dbt && dbt run && dbt test

# 6. Or via Airflow
airflow scheduler &
airflow webserver -p 8080
# Trigger kafka_to_postgres DAG then dbt_transformation DAG
```

