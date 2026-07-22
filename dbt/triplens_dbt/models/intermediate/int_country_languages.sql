select distinct
    country_id,
    country_code_alpha_3,
    coalesce(
        nullif(language_code, ''),
        language_name
    ) as language_natural_key,
    language_code,
    language_name,
    native_language_name

from {{ ref('stg_country_languages') }}

where country_id is not null
  and language_name is not null