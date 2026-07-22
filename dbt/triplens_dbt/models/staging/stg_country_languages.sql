select
    country.country_json:uuid::string as country_id,
    nullif(country.country_json:codes:alpha_3::string, '')
        as country_code_alpha_3,
    language.value:iso639_3::string as language_code,
    language.value:name::string as language_name,
    language.value:native_name::string as native_language_name,
    country.ingestion_id,
    country.loaded_at

from {{ ref('stg_country_records') }} as country,
lateral flatten(
    input => country.country_json:languages
) as language

where language.value:name is not null
