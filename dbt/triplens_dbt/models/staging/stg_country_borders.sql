select
    country.country_json:uuid::string as country_id,
    nullif(country.country_json:codes:alpha_3::string, '')
        as country_code_alpha_3,
    border.value::string as border_country_code_alpha_3,
    country.ingestion_id,
    country.loaded_at

from {{ ref('stg_country_records') }} as country,
lateral flatten(
    input => country.country_json:borders
) as border

where border.value is not null