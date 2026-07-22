select distinct
    country.country_key,
    language.language_key,
    relationships.country_id,
    relationships.language_natural_key

from {{ ref('int_country_languages') }} as relationships

inner join {{ ref('dim_country') }} as country
    on relationships.country_id = country.country_id

inner join {{ ref('dim_language') }} as language
    on relationships.language_natural_key = language.language_natural_key