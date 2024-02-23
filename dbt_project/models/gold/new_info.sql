with source as (
    select * from "data"."main"."new"
),

transformed AS (
SELECT COUNT(*),
        publish_date
        FROM source
        GROUP BY publish_date
)

SELECT * FROM transformed