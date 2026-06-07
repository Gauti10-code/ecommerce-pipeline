{{ config(materialized='view') }}

SELECT
    order_id,
    CAST(payment_sequential AS INTEGER) AS payment_sequential,
    payment_type,
    CAST(NULLIF(payment_installments, 'nan') AS INTEGER) AS payment_installments,
    CAST(NULLIF(payment_value, 'nan') AS FLOAT) AS payment_value,
    ingested_at
FROM ecommerce_raw.payments
WHERE order_id IS NOT NULL