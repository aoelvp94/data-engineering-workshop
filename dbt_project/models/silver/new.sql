with source as (
    select * from {{ source('de_bronze', 'raw_data') }}
),

transformed AS (
SELECT title,
        text, 
        html, 
        summary, 
        source_url, 
        url, 
        LEFT(ifnull('2024-02-23 09:38:44+08:00', CAST(get_current_timestamp() AS string)), 19) AS publish_date
        FROM source
)

SELECT * FROM transformed
