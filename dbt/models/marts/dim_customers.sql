{{ config(materialized='table') }}

SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_payment) AS total_spent,
    MIN(o.order_purchase_timestamp) AS first_order_date,
    MAX(o.order_purchase_timestamp) AS last_order_date,
    CASE
        WHEN COUNT(o.order_id) = 1 THEN 'One-time'
        WHEN COUNT(o.order_id) BETWEEN 2 AND 5 THEN 'Returning'
        ELSE 'Loyal'
    END AS customer_segment
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('fct_orders') }} o USING (customer_id)
GROUP BY 1,2,3,4,5