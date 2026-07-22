select distinct
    source_country.country_key,
    border_country.country_key as border_country_key,
    relationships.country_code_alpha_3,
    relationships.border_country_code_alpha_3

from {{ ref('int_country_borders') }} as relationships

inner join {{ ref('dim_country') }} as source_country
    on relationships.country_id = source_country.country_id

left join {{ ref('dim_country') }} as border_country
    on relationships.border_country_code_alpha_3
       = border_country.country_code_alpha_3