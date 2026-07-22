select
    country.country_json:uuid::string as country_id,
    nullif(country.country_json:codes:alpha_3::string, '')
        as country_code_alpha_3,
    currency.value:code::string as currency_code,
    currency.value:name::string as currency_name,
    currency.value:symbol::string as currency_symbol,
    country.ingestion_id,
    country.loaded_at

from {{ ref('stg_country_records') }} as country,
lateral flatten(
    input => country.country_json:currencies
) as currency

where currency.value:code is not null