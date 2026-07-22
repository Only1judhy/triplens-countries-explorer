select
    md5(language_natural_key) as language_key,
    language_natural_key,
    max(language_code) as language_code,
    max(language_name) as language_name,
    max(native_language_name) as native_language_name

from {{ ref('int_country_languages') }}

group by language_natural_key