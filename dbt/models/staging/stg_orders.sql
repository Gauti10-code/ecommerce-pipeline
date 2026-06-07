{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    order_status,
    CAST(NULLIF(order_purchase_timestamp, 'nan') AS TIMESTAMP) AS order_purchase_timestamp,
    CAST(NULLIF(order_approved_at, 'nan') AS TIMESTAMP) AS order_approved_at,
    CAST(NULLIF(order_delivered_carrier_date, 'nan') AS TIMESTAMP) AS order_delivered_carrier_date,
    CAST(NULLIF(order_delivered_customer_date, 'nan') AS TIMESTAMP) AS order_delivered_customer_date,
    CAST(NULLIF(order_estimated_delivery_date, 'nan') AS TIMESTAMP) AS order_estimated_delivery_date,
    ingested_at
FROM ecommerce_raw.orders
WHERE order_id IS NOT NULL