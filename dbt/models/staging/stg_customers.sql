{{ config(materialized='view') }}

SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    ingested_at
FROM ecommerce_raw.customers
WHERE customer_id IS NOT NULL