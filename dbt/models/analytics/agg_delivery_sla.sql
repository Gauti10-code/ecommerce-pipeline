{{ config(materialized='table') }}

SELECT
    customer_state,
    COUNT(order_id) AS total_orders,
    AVG(delivery_hours) AS avg_delivery_hours,
    SUM(CASE WHEN delivered_on_time THEN 1 ELSE 0 END) AS on_time_count,
    ROUND(
        CAST(SUM(CASE WHEN delivered_on_time THEN 1 ELSE 0 END) AS NUMERIC) / 
        NULLIF(COUNT(CASE WHEN order_status = 'delivered' THEN 1 END), 0) * 100
    , 2) AS on_time_pct
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('stg_customers') }} c USING (customer_id)
WHERE order_status = 'delivered'
GROUP BY 1
ORDER BY on_time_pct DESC