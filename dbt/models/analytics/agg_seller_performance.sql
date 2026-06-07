{{ config(materialized='table') }}

SELECT
    seller_id,
    seller_tier,
    total_orders,
    total_revenue,
    avg_order_value,
    total_freight,
    ROUND(CAST(total_freight AS NUMERIC) / NULLIF(CAST(total_revenue AS NUMERIC), 0) * 100, 2) AS freight_pct
FROM {{ ref('dim_sellers') }}
ORDER BY total_revenue DESC