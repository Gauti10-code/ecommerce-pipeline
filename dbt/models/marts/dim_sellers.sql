{{ config(materialized='table') }}

WITH seller_metrics AS (
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(price) AS total_revenue,
        AVG(price) AS avg_order_value,
        SUM(freight_value) AS total_freight
    FROM {{ ref('stg_order_items') }}
    GROUP BY seller_id
)

SELECT
    s.seller_id,
    sm.total_orders,
    sm.total_revenue,
    sm.avg_order_value,
    sm.total_freight,
    CASE
        WHEN sm.total_revenue >= 10000 THEN 'High Value'
        WHEN sm.total_revenue >= 1000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS seller_tier
FROM seller_metrics sm
LEFT JOIN (
    SELECT DISTINCT seller_id 
    FROM {{ ref('stg_order_items') }}
) s USING (seller_id)