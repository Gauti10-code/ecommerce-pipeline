import json
import time
import pandas as pd
from kafka import KafkaProducer
from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

producer=KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v:json.dumps(v,default=str).encode('utf-8'))

orders = pd.read_csv(f'{BASE_DIR}/data/olist_orders_dataset.csv')
order_items = pd.read_csv(f'{BASE_DIR}/data/olist_order_items_dataset.csv')
customers = pd.read_csv(f'{BASE_DIR}/data/olist_customers_dataset.csv')
payments = pd.read_csv(f'{BASE_DIR}/data/olist_order_payments_dataset.csv')

print(f"Loaded {len(orders)} orders")
print(f"Publishing to Kafka topics...")

for _,row in orders.iterrows():
  producer.send('raw_orders',value=row.to_dict())

producer.flush()
print(f"Published {len(orders)} orders to raw_orders topic")

for _, row in order_items.iterrows():
    producer.send('raw_order_items', value=row.to_dict())

producer.flush()
print(f"Published {len(order_items)} order items to raw_order_items topic")

# Publish customers
for _, row in customers.iterrows():
    producer.send('raw_customers', value=row.to_dict())

producer.flush()
print(f"Published {len(customers)} customers to raw_customers topic")

# Publish payments
for _, row in payments.iterrows():
    producer.send('raw_payments', value=row.to_dict())

producer.flush()
print(f"Published {len(payments)} payments to raw_payments topic")

print("All data published to Kafka!")
producer.close()