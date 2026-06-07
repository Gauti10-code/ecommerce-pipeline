import json
import psycopg2
import os
from kafka import KafkaConsumer

# PostgreSQL connection
def get_pg_conn():
    return psycopg2.connect(
        host='localhost',
        dbname='ecommerce',
        user='postgres',
        password='admin123',
        port=5432
    )

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ecommerce_raw.orders (
            order_id TEXT,
            customer_id TEXT,
            order_status TEXT,
            order_purchase_timestamp TEXT,
            order_approved_at TEXT,
            order_delivered_carrier_date TEXT,
            order_delivered_customer_date TEXT,
            order_estimated_delivery_date TEXT,
            ingested_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ecommerce_raw.order_items (
            order_id TEXT,
            order_item_id TEXT,
            product_id TEXT,
            seller_id TEXT,
            shipping_limit_date TEXT,
            price TEXT,
            freight_value TEXT,
            ingested_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ecommerce_raw.customers (
            customer_id TEXT,
            customer_unique_id TEXT,
            customer_zip_code_prefix TEXT,
            customer_city TEXT,
            customer_state TEXT,
            ingested_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ecommerce_raw.payments (
            order_id TEXT,
            payment_sequential TEXT,
            payment_type TEXT,
            payment_installments TEXT,
            payment_value TEXT,
            ingested_at TIMESTAMP DEFAULT NOW()
        )
    """)

def consume_topic(topic, insert_sql, fields):
    pg_conn = get_pg_conn()
    cursor = pg_conn.cursor()
    create_tables(cursor)
    
    # Truncate table before inserting to avoid duplicates
    table_name = topic.replace('raw_', '')
    cursor.execute(f'TRUNCATE TABLE ecommerce_raw.{table_name}')
    pg_conn.commit()

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=10000
    )

    count = 0
    for message in consumer:
        data = message.value
        vals = tuple([str(data.get(f, '')) for f in fields])
        cursor.execute(insert_sql, vals)
        count += 1
        if count % 1000 == 0:
            pg_conn.commit()
            print(f'  {count} rows inserted into {topic}')

    pg_conn.commit()
    cursor.close()
    pg_conn.close()
    consumer.close()
    print(f'Done: {count} rows inserted into {topic}')

# Orders
print("Consuming raw_orders...")
consume_topic(
    'raw_orders',
    "INSERT INTO ecommerce_raw.orders (order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    ['order_id','customer_id','order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date']
)

# Order Items
print("Consuming raw_order_items...")
consume_topic(
    'raw_order_items',
    "INSERT INTO ecommerce_raw.order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    ['order_id','order_item_id','product_id','seller_id','shipping_limit_date','price','freight_value']
)

# Customers
print("Consuming raw_customers...")
consume_topic(
    'raw_customers',
    "INSERT INTO ecommerce_raw.customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state) VALUES (%s,%s,%s,%s,%s)",
    ['customer_id','customer_unique_id','customer_zip_code_prefix','customer_city','customer_state']
)

# Payments
print("Consuming raw_payments...")
consume_topic(
    'raw_payments',
    "INSERT INTO ecommerce_raw.payments (order_id, payment_sequential, payment_type, payment_installments, payment_value) VALUES (%s,%s,%s,%s,%s)",
    ['order_id','payment_sequential','payment_type','payment_installments','payment_value']
)

print("All data consumed from Kafka and loaded into PostgreSQL!")