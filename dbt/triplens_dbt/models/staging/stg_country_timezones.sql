select
    country.country_json:uuid::string as country_id,
    nullif(country.country_json:codes:alpha_3::string, '')
        as country_code_alpha_3,
    timezone.value::string as timezone,
    country.ingestion_id,
    country.loaded_at

from {{ ref('stg_country_records') }} as country,
lateral flatten(
    input => country.country_json:timezones
) as timezone

where timezone.value is not null