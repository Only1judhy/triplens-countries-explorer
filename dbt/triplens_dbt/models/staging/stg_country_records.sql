with latest_batch as (

    select
        ingestion_id,
        loaded_at,
        raw_payload

    from {{ source('raw', 'country_api_raw') }}

    qualify row_number() over (
        order by loaded_at desc
    ) = 1

)

select
    country.value as country_json,
    latest_batch.ingestion_id,
    latest_batch.loaded_at

from latest_batch,
lateral flatten(
    input => latest_batch.raw_payload:countries
) as country