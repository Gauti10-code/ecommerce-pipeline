{{config(materialized='view')}}

SELECT  order_id,
        CAST(order_item_id as INTEGER) as order_item_id,
        product_id,
        seller_id,
        CAST(shipping_limit_date as TIMESTAMP) as shipping_limit_date,
        CAST(NULLIF(price,'nan') AS FLOAT) as price,
        CAST(NULLIF(freight_value,'nan') AS FLOAT)as freight_value,
        ingested_at
FROM    ecommerce_raw.order_items
Where   order_id is NOT NULL