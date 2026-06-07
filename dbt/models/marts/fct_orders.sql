{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    CASE 
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
        THEN true 
        ELSE false 
    END AS delivered_on_time,
    CASE
        WHEN o.order_delivered_customer_date IS NOT NULL
        THEN EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))/3600
        ELSE NULL
    END AS delivery_hours,
    p.total_payment,
    p.payment_type,
    i.total_items,
    i.total_freight
FROM {{ ref('stg_orders') }} o
LEFT JOIN (
    SELECT 
        order_id,
        SUM(payment_value) AS total_payment,
        MAX(payment_type) AS payment_type
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id
) p ON o.order_id = p.order_id
LEFT JOIN (
    SELECT 
        order_id,
        COUNT(*) AS total_items,
        SUM(freight_value) AS total_freight
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
) i ON o.order_id = i.order_id