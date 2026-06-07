{{ config(materialized='table') }}

SELECT
    DATE(order_purchase_timestamp) AS order_date,
    COUNT(order_id) AS total_orders,
    SUM(total_payment) AS total_revenue,
    AVG(total_payment) AS avg_order_value,
    SUM(CASE WHEN delivered_on_time THEN 1 ELSE 0 END) AS on_time_deliveries,
    COUNT(CASE WHEN order_status = 'delivered' THEN 1 END) AS delivered_orders,
    COUNT(CASE WHEN order_status = 'cancelled' THEN 1 END) AS cancelled_orders
FROM {{ ref('fct_orders') }}
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY 1
ORDER BY 1